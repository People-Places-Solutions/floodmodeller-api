"""
Flood Modeller Python API
Copyright (C) 2025 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from __future__ import annotations

import io
import logging
import time
from copy import deepcopy
from pathlib import Path
from subprocess import DEVNULL, Popen
from typing import Callable

import requests
from lxml import etree
from tqdm import trange

from floodmodeller_api._base import FMFile

from .logs import LF2, create_lf, error_2d_dict
from .util import handle_exception
from .xml2d_template import xml2d_template


def value_from_string(value: str | list[str]):
    try:
        if isinstance(value, list):
            return value
        return float(value) if "." in value else int(value)
    except ValueError:
        return value


def categorical_sort(itm, order, ns):
    try:
        return order[itm.tag.replace(ns, "")]
    except Exception:
        return 0


class XML2D(FMFile):
    """Reads and write Flood Modeller 2D XML format '.xml'

    Args:
        xml_filepath (str, optional): Full filepath to xml file.

    Output:
        Initiates 'XML2D' class object

    Raises:
        TypeError: Raised if xml_filepath does not point to a .xml file
        FileNotFoundError: Raised if xml_filepath points to a file which does not exist
    """

    _filetype: str = "XML2D"
    _suffix: str = ".xml"
    _xsd_loc: str = "https://schema.floodmodeller.com/7.1/2d.xsd"
    _w3_schema: str = "{http://www.w3.org/2001/XMLSchema}"
    OLD_FILE = 5
    GOOD_EXIT_CODE = 100

    @handle_exception(when="read")
    def __init__(self, xml_filepath: str | Path | None = None, from_json: bool = False):
        if from_json:
            return
        if xml_filepath is not None:
            FMFile.__init__(self, xml_filepath)
            self._read()
            self._log_path = self._filepath.with_suffix(".lf2")
        else:
            self._read(from_blank=True)

    def _read(self, from_blank=False):
        # Read xml data
        self._ns = "{https://www.floodmodeller.com}"
        if from_blank:
            self._xmltree = etree.parse(io.StringIO(xml2d_template))
        else:
            self._xmltree = etree.parse(self._filepath)
        try:
            xsd_bin = requests.get(self._xsd_loc).content
            self._xsd = etree.parse(io.BytesIO(xsd_bin))
            self._xsdschema = etree.XMLSchema(self._xsd)
        except Exception:
            self._xsd = etree.parse(Path(__file__).parent / "xsd_backup.xml")
            self._xsdschema = etree.XMLSchema(self._xsd)
        self._get_multi_value_keys()

        self._create_dict()
        for key, data in self._data.items():
            if key == "domain":
                self.domains = {domain["domain_id"]: domain for domain in data}
            else:
                setattr(self, key, data)
        for attr in [
            "name",
            "link1d",
            "logfile",
            "domains",
            "restart_options",
            "advanced_options",
            "processor",
            "unit_system",
            "description",
        ]:
            if attr not in self.__dict__:
                setattr(self, attr, None)

    def _create_dict(self):
        """Iterate through XML Tree to add all elements as class attributes"""
        xml_dict = {}
        root = self._xmltree.getroot()

        xml_dict.update({"name": root.attrib["name"]})

        xml_dict = self._recursive_elements_to_dict(xml_dict, root)
        self._raw_data = xml_dict
        self._data = deepcopy(self._raw_data)

    def _recursive_elements_to_dict(self, xml_dict, tree):
        # Some elements can have multiple instances e.g. domains.
        # In these cases we need to have the id of that instance as a new key on the domain
        # e.g. xml.domains[domain_id]["computational_area"]... etc

        for child in tree:
            if isinstance(child, etree._Comment):
                continue  # Skips comments in xml
            child_key = child.tag.replace(self._ns, "")
            if child_key in self._multi_value_keys:
                if child_key in xml_dict:
                    xml_dict[child_key].append({})
                else:
                    xml_dict[child_key] = [{}]
                child_dict = xml_dict[child_key][-1]
            else:
                xml_dict[child_key] = {}  # Create new key for element
                child_dict = xml_dict[child_key]
            value = "" if child.text is None else child.text.strip()
            if "\n" in value:
                value = value.split("\n")  # Only used for output variables
            if len(child.attrib) != 0:
                child_dict.update(child.attrib)
                if value != "":
                    child_dict.update({"value": value_from_string(value)})

                self._recursive_elements_to_dict(child_dict, child)

            elif value == "":
                self._recursive_elements_to_dict(child_dict, child)

            elif child_key in self._multi_value_keys:
                xml_dict[child_key] = xml_dict[child_key][:-1]  # remove unused dict
                xml_dict[child_key].append(value_from_string(value))
            else:
                xml_dict[child_key] = value_from_string(value)

        return xml_dict

    def _recursive_reorder_xml(self, parent="ROOT"):
        if parent == "ROOT":
            parent = self._xmltree.getroot()
        parent[:] = self._sort_from_schema(parent)

        for child in parent:
            if not isinstance(child, etree._Comment):
                self._recursive_reorder_xml(child)

    def _sort_from_schema(self, parent):
        # find element in schema
        parent_name = parent.tag.replace(self._ns, "")
        schema_elem = self._xsd.find(
            f".//{self._w3_schema}*[@name='{parent_name}']",
        )
        if "type" in schema_elem.attrib:
            schema_elem = self._xsd.find(
                f".//{self._w3_schema}*[@name='{schema_elem.attrib['type']}']",
            )
        else:
            schema_elem = schema_elem.find(f"{self._w3_schema}complexType")
        if schema_elem is None:
            return parent.getchildren()

        seq = schema_elem.find(f"{self._w3_schema}sequence")
        if seq is None:
            return parent.getchildren()

        categorical_order = {sub_element.attrib["name"]: idx for idx, sub_element in enumerate(seq)}
        return sorted(
            parent.getchildren(),
            key=lambda x: categorical_sort(x, categorical_order, self._ns),
        )

    def _validate(self):
        try:
            self._xsdschema.assert_(self._xmltree)  # noqa: PT009
        except AssertionError as err:
            msg = f"XML Validation Error for {self!r}:\n     {err.args[0].replace(self._ns, '')}"
            raise ValueError(msg) from err

    def _recursive_update_xml(  # noqa: C901, PLR0912
        self,
        new_dict,
        orig_dict,
        parent_key,
        list_idx=None,
    ):
        for key, item in new_dict.items():
            if key in self._multi_value_keys and not isinstance(item, list):
                msg = f"Element: '{key}' must be added as list"
                raise Exception(msg)
            if parent_key == "ROOT":
                parent = self._xmltree.getroot()
            else:
                parent = self._xmltree.findall(f".//{self._ns}{parent_key}")[list_idx or 0]

            if key not in orig_dict:
                # New key added, add recursively
                self._recursive_add_element(parent=parent, add_item=item, add_key=key)

            elif isinstance(item, dict):
                self._recursive_update_xml(item, orig_dict[key], key, list_idx)
            elif isinstance(item, list) and isinstance(item[0], dict):
                for i, _item in enumerate(item):
                    if isinstance(_item, dict):
                        try:
                            self._recursive_update_xml(_item, orig_dict[key][i], key, list_idx=i)
                        except IndexError:
                            # New thing added, Add it all recursively
                            self._recursive_add_element(
                                parent=parent,
                                add_item=_item,
                                add_key=key,
                                from_list=True,
                            )

            else:
                if parent_key == "ROOT":
                    item = getattr(self, key)
                try:
                    if item != orig_dict[key]:
                        if key == "value":
                            # Value has been updated
                            parent.text = str(item)
                        else:
                            # Attribute has been updated
                            elems = parent.findall(f"{self._ns}{key}")
                            if isinstance(item, list) and key != "variables":
                                # Handle multiple similar elements
                                if len(elems) < len(item):
                                    while len(elems) < len(item):
                                        elems.append(etree.SubElement(parent, f"{self._ns}{key}"))
                                elif len(elems) > len(item):
                                    while len(elems) > len(item):
                                        parent.remove(elems.pop())

                                for i in range(len(elems)):
                                    elems[i].text = item[i]

                            elif len(elems) == 1:
                                elem = elems[0]
                                if isinstance(item, list):
                                    elem.text = "\n".join(item)
                                else:
                                    elem.text = str(item)

                            else:
                                parent.set(key, str(item))
                except KeyError:
                    # New value/attribute added
                    self._recursive_add_element(parent=parent, add_item=item, add_key=key)

    def _recursive_add_element(  # noqa: C901, PLR0912
        self,
        parent,
        add_item,
        add_key,
        from_list=False,
    ):
        if add_key in self._multi_value_keys and not isinstance(add_item, list) and not from_list:
            msg = f"Element: '{add_key}' must be added as list"
            raise Exception(msg)
        if isinstance(add_item, dict):
            new_element = etree.SubElement(parent, f"{self._ns}{add_key}")
            for key, item in add_item.items():
                self._recursive_add_element(parent=new_element, add_item=item, add_key=key)
        elif isinstance(add_item, list):
            if add_key == "variables":
                # Variables is special case where we have list but add to one element
                new_element = etree.SubElement(parent, f"{self._ns}{add_key}")
                new_element.text = "\n".join(add_item)
            else:
                for item in add_item:
                    self._recursive_add_element(
                        parent=parent,
                        add_item=item,
                        add_key=add_key,
                        from_list=True,
                    )
        elif add_key == "value":  # Value has been added
            parent.text = str(add_item)
        else:  # Attribute or element added
            # Check schema to see if we should use parent.set for attribute
            # or etree.subelement() and set text
            schema_elem = self._xsd.findall(
                f".//{self._w3_schema}*[@name='{add_key}']",
            )
            if len(schema_elem) == 1:
                schema_elem = schema_elem[0]
            else:
                # This is just here for when there's multiple schema elements with same
                # name, e.g. 'frequency'
                parent_schema_elem = self._xsd.find(
                    f".//{self._w3_schema}*[@name='{parent.tag.replace(self._ns, '')}']",
                )
                if "type" in parent_schema_elem.attrib:
                    parent_schema_elem = self._xsd.find(
                        f".//{self._w3_schema}*[@name='{parent_schema_elem.attrib['type']}']",
                    )
                schema_elem = parent_schema_elem.find(
                    f".//{self._w3_schema}*[@name='{add_key}']",
                )

            if schema_elem is None:
                msg = f"Schema element for key '{add_key}' not found in XSD."
                raise ValueError(msg)

            if schema_elem.tag.endswith("attribute"):
                parent.set(add_key, str(add_item))

            else:
                new_element = etree.SubElement(parent, f"{self._ns}{add_key}")
                new_element.text = str(add_item)

    def _recursive_remove_data_xml(self, new_dict, parent, list_idx=None):
        # This method will recursively work through the original dictionary and remove any
        # items that are not in the new_dictionary and need to be removed.
        list_idx = 0
        list_idx_key = ""
        for elem in parent:
            if isinstance(elem, etree._Comment):
                continue  # Skips comments in xml
            # Check each element is in the new_dict somewhere, delete if not
            elem_key = elem.tag.replace(self._ns, "")
            if elem_key in self._multi_value_keys:
                if list_idx_key != elem_key:
                    list_idx_key = elem_key
                    list_idx = 0
                try:
                    self._recursive_remove_data_xml(new_dict[elem_key][list_idx], elem)
                    list_idx += 1
                except (IndexError, KeyError):
                    parent.remove(elem)

            elif elem_key in new_dict:
                self._recursive_remove_data_xml(new_dict[elem_key], elem)

            else:
                parent.remove(elem)

    def _update_dict(self):
        self._data = {}
        for attr in [
            "name",
            "link1d",
            "logfile",
            "domains",
            "restart_options",
            "advanced_options",
            "processor",
            "unit_system",
            "description",
        ]:
            if getattr(self, attr) is not None:
                if attr == "domains":
                    self._data["domain"] = [domain for _, domain in self.domains.items()]
                else:
                    try:
                        self._data[attr] = getattr(self, attr)
                    except AttributeError:
                        self._data[attr] = None

    @handle_exception(when="write")
    def _write(self) -> str:
        self._update_dict()
        self._recursive_update_xml(self._data, self._raw_data, "ROOT")
        self._recursive_remove_data_xml(self._data, self._xmltree.getroot())
        etree.indent(self._xmltree, space="    ")
        try:
            self._validate()
        except Exception:
            self._recursive_reorder_xml()
            self._validate()

        self._raw_data = deepcopy(self._data)  # reset raw data to equal data

        return f'<?xml version="1.0" standalone="yes"?>\n{etree.tostring(self._xmltree.getroot()).decode()}'

    def _get_multi_value_keys(self):
        self._multi_value_keys = []
        root = self._xsd.getroot()
        for elem in root.findall(f".//{self._w3_schema}element"):
            if elem.attrib.get("maxOccurs") not in (None, "0", "1"):
                self._multi_value_keys.append(elem.attrib["name"])
        self._multi_value_keys = set(self._multi_value_keys)

    def diff(self, other: XML2D, force_print: bool = False) -> None:
        """Compares the XML2D class against another XML2D class to check whether they are
        equivalent, or if not, what the differences are. Two instances of a XML2D class are
        deemed equivalent if all of their attributes are equal except for the filepath and
        raw data. For example, two XML2D files from different filepaths that had the same
        data except maybe some differences in decimal places and some default parameters
        ommitted, would be classed as equaivalent as they would produce the same XML2D instance
        and write the exact same data.

        The result is printed to the console. If you need to access the returned data, use
        the method ``XML2D._get_diff()``

        Args:
            other (floodmodeller_api.XML2D): Other instance of a XML2D class
            force_print (bool): Forces the API to print every difference found, rather than
                just the first 25 differences. Defaults to False.
        """
        self._diff(other, force_print=force_print)

    def update(self) -> None:
        """Updates the existing XML based on any altered attributes"""
        self._update()

        # Update XML dict and tree
        self._read()

    def save(self, filepath: str | Path) -> None:
        """Saves the XML to the given location, if pointing to an existing file it will be overwritten.
        Once saved, the XML() class will continue working from the saved location, therefore any further calls to XML.update() will
        update in the latest saved location rather than the original source XML used to construct the class

        Args:
            filepath (str): Filepath to new save location including the name and '.xml' extension

        Raises:
            TypeError: Raised if given filepath doesn't point to a file suffixed '.xml'
        """

        self._save(filepath)

        # Update XML dict and tree
        self._read()
        self._log_path = self._filepath.with_suffix(".lf2")

    @handle_exception(when="simulate")
    def simulate(  # noqa: C901, PLR0912, PLR0913
        self,
        method: str = "WAIT",
        raise_on_failure: bool = True,
        precision: str = "DEFAULT",
        enginespath: str = "",
        console_output: str = "simple",
        range_function: Callable = trange,
        range_settings: dict | None = None,
    ) -> Popen | None:
        """Simulate the XML2D file directly as a subprocess.

        Args:
            method (str, optional): {'WAIT'} | 'RETURN_PROCESS'
                'WAIT' - The function waits for the simulation to complete before continuing (This is default)
                'RETURN_PROCESS' - The function sets the simulation running in background and immediately continues, whilst returning the process object.
                Defaults to 'WAIT'.
            raise_on_failure (bool, optional): If True, an exception will be raised if the simulation fails to complete without errors.
                If set to False, then the script will continue to run even if the simulation fails. If 'method' is set to 'RETURN_PROCESS'
                then this argument is ignored. Defaults to True.
            precision (str, optional): {'DEFAULT'} | 'SINGLE' | 'DOUBLE'
                Define which engine to use for simulation, if set to 'DEFAULT' it will use the precision specified in the IEF. Alternatively,
                this can be overwritten using 'SINGLE' or 'DOUBLE'.
            enginespath (str, optional): {''} | '/absolute/path/to/engine/executables'
                Define where the engine executables are located. This replaces the default location (usual installation folder) if set to
                anything other than ''.
            console_output (str, optional): {'simple'} | 'standard' | 'detailed'
                'simple' - A simple progress bar for the simulation is presented in the console
                'standard' - The standard Flood Modeller 2D output is presented in the console
                'detailed' - The most detailed Flood Modeller 2D output is presented in the console
                Defaults to 'WAIT'.


        Raises:
            UserWarning: Raised if ief filepath not already specified

        Returns:
            subprocess.Popen(): If method == 'RETURN_PROCESS', the Popen() instance of the process is returned.

        """

        self.range_function = range_function
        self.range_settings = range_settings if range_settings else {}

        if self._filepath is None:
            msg = "xml2D must be saved to a specific filepath before simulate() can be called."
            raise UserWarning(msg)
        if precision.upper() == "DEFAULT":
            precision = "SINGLE"  # defaults to single precision
            for domain in self.domains.values():
                if domain["run_data"].get("double_precision") == "required":
                    precision = "DOUBLE"
                    break

        if enginespath == "":
            # Default location
            _enginespath = r"C:\Program Files\Flood Modeller\bin"
        else:
            _enginespath = enginespath
            if not Path(_enginespath).exists():
                msg = f"Flood Modeller non-default engine path not found! {_enginespath!s}"
                raise Exception(msg)

        # checking if all schemes used are fast, if so will use FAST.exe
        is_fast = True
        for domain in self.domains.values():
            if domain["run_data"]["scheme"] != "FAST":
                is_fast = False
                break

        if is_fast is True:
            isis2d_fp = str(Path(_enginespath, "FAST.exe"))
        elif precision.upper() == "SINGLE":
            isis2d_fp = str(Path(_enginespath, "ISIS2d.exe"))
        else:
            isis2d_fp = str(Path(_enginespath, "ISIS2d_DP.exe"))

        if not Path(isis2d_fp).exists():
            msg = f"Flood Modeller engine not found! Expected location: {isis2d_fp}"
            raise Exception(msg)

        console_output = console_output.lower()
        run_command = (
            f'"{isis2d_fp}" {"-q" if console_output != "detailed" else ""} "{self._filepath}"'
        )
        stdout = DEVNULL if console_output == "simple" else None

        if method.upper() == "WAIT":
            logging.info("Executing simulation ... ")
            # execute simulation
            process = Popen(run_command, cwd=Path(self._filepath).parent, stdout=stdout)

            # progress bar based on log files:
            if console_output == "simple":
                self._lf = create_lf(self._log_path, "lf2")
                self._update_progress_bar(process)

            while process.poll() is None:
                # process is still running
                time.sleep(1)

            exitcode = process.returncode
            self._interpret_exit_code(exitcode, raise_on_failure)

        elif method.upper() == "RETURN_PROCESS":
            logging.info("Executing simulation ...")
            # execute simulation
            return Popen(run_command, cwd=Path(self._filepath).parent, stdout=stdout)

        return None

    def get_log(self):
        """If log files for the simulation exist, this function returns them as a LF2 class object

        Returns:
            floodmodeller_api.LF2 class object
        """
        if not self._log_path.exists():
            msg = "Log file (LF2) not found"
            raise FileNotFoundError(msg)

        return LF2(self._log_path)

    def _update_progress_bar(self, process: Popen):
        """Updates progress bar based on log file"""

        # only if there is a log file
        if self._lf is None:
            return

        # tqdm progress bar
        for i in self.range_function(100, **self.range_settings):
            # Process still running
            while process.poll() is None:
                time.sleep(0.1)

                # Find progress
                self._lf.read(suppress_final_step=True)
                progress = self._lf.report_progress()

                # Reached i% progress => move onto waiting for (i+1)%
                if progress > i:
                    break

            # Process stopped
            if process.poll() is not None:
                # Find final progress
                self._lf.read(suppress_final_step=True)
                progress = self._lf.report_progress()

                if progress > i:
                    pass  # stopped because it completed
                else:
                    break  # stopped for another reason

    def _interpret_exit_code(self, exitcode: int, raise_on_failure: bool):
        """This function will interpret the exit code and tell us if this is good or bad

        Args:
            exitcode - this is the exitcode from the simulation

        Return:
            String that explains the exitcode - this might be too much!
        """
        try:
            msg = f"Exit with {exitcode}: {error_2d_dict[exitcode]}"
        except Exception:
            msg = f"Exit with {exitcode}: Unknown error occurred!"

        if raise_on_failure and exitcode != self.GOOD_EXIT_CODE:
            raise Exception(msg)
        logging.info(msg)
