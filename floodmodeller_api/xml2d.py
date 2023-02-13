"""
Flood Modeller Python API
Copyright (C) 2022 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

import os
import time

from pathlib import Path
from subprocess import Popen
from copy import deepcopy
from typing import Union, Optional
from lxml import etree
from floodmodeller_api._base import FMFile
from tqdm import trange

# import xml as xml

import datetime as dt


from .zzn import ZZN
from .logs import lf_factory, error_2D_dict


def value_from_string(value: Union[str, list[str]]):
    try:
        val = float(value)
        if not "." in value:
            val = int(val)
        return val
    except ValueError:
        return value
    except TypeError:
        return value


def categorical_sort(itm, order, ns):
    try:
        return order[itm.tag.replace(ns, "")]
    except:
        return 0


class XML2D(FMFile):
    """Reads and write Flood Modeller 2D XML format '.xml'

    Args:
        xml_filepath (str, optional): Full filepath to xml file.

    Output:
        Initiates 'XML' class object

    Raises:
        TypeError: Raised if xml_filepath does not point to a .xml file
        FileNotFoundError: Raised if xml_filepath points to a file which does not exist
    """

    _filetype: str = "XML2D"
    _suffix: str = ".xml"
    _xsd_loc: str = "http://schema.floodmodeller.com/5.1/2d.xsd"
    # _xsd_loc : str = r"C:\Program Files\Flood Modeller\bin\2d_test.xsd"

    def __init__(self, xml_filepath: Union[str, Path] = None):
        try:
            self._filepath = xml_filepath
            if self._filepath != None:
                FMFile.__init__(self)
                self._read()

            else:
                raise NotImplementedError(
                    "Creating new XML2D files is currently not supported. "
                    "Please point to an existing xml 2d file"
                )
        except Exception as e:
            self._handle_exception(e, when="read")

    def _read(self):
        # Read xml data
        self._ns = "{https://www.floodmodeller.com}"
        # etree.register_namespace('', 'https://www.floodmodeller.com')
        self._xmltree = etree.parse(self._filepath)
        self._xsd = etree.parse(self._xsd_loc)
        self._xsdschema = etree.XMLSchema(self._xsd)
        self._get_multi_value_keys()

        self._create_dict()
        # self._create_schema_dict()
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

            else:
                xml_dict[child_key] = value_from_string(value)

        return xml_dict

    def _recursive_reorder_xml(self, parent="ROOT"):
        if parent == "ROOT":
            parent = self._xmltree.getroot()
        parent[:] = self._sort_from_schema(
            parent
        ) 

        for child in parent:
            if not type(child) == etree._Comment:
                self._recursive_reorder_xml(child)

    def _sort_from_schema(self, parent):
        # find element in schema
        parent_name = parent.tag.replace(self._ns, "")
        schema_elem = self._xsd.find(
            f".//{{http://www.w3.org/2001/XMLSchema}}*[@name='{parent_name}']"
        )
        if "type" in schema_elem.attrib:
            schema_elem = self._xsd.find(
                f".//{{http://www.w3.org/2001/XMLSchema}}*[@name='{schema_elem.attrib['type']}']"
            )
        else:
            schema_elem = schema_elem.find(
                "{http://www.w3.org/2001/XMLSchema}complexType"
            )
        if schema_elem is None:
            return parent.getchildren()

        seq = schema_elem.find("{http://www.w3.org/2001/XMLSchema}sequence")
        if seq is None:
            return parent.getchildren()

        else:
            categorical_order = {
                sub_element.attrib["name"]: idx for idx, sub_element in enumerate(seq)
            }
            return sorted(
                parent.getchildren(),
                key=lambda x: categorical_sort(x, categorical_order, self._ns),
            )

    def _validate(self):
        try:
            self._xsdschema.assert_(self._xmltree)
        except AssertionError as err:
            msg = (
                f"XML Validation Error for {self.__repr__()}:\n"
                f"     {err.args[0].replace(self._ns, '')}"
            )
            raise ValueError(msg)

    def _recursive_update_xml(self, new_dict, orig_dict, parent_key, list_idx=None):
        # TODO: Handle removing params

        for key, item in new_dict.items():
            if parent_key == "ROOT":
                parent = self._xmltree.getroot()
            else:
                parent = self._xmltree.findall(f".//{self._ns}{parent_key}")[
                    list_idx or 0
                ]

            if key not in orig_dict:
                # New key added, add recursively
                self._recursive_add_element(parent=parent, add_item=item, add_key=key)

            elif type(item) == dict:
                self._recursive_update_xml(item, orig_dict[key], key, list_idx)
            elif type(item) == list and key != "variables":
                for i, _item in enumerate(item):
                    if type(_item) == dict:
                        try:
                            self._recursive_update_xml(
                                _item, orig_dict[key][i], key, list_idx=i
                            )
                        except IndexError:
                            # New thing added, Add it all recursively
                            self._recursive_add_element(
                                parent=parent, add_item=_item, add_key=key
                            )

            else:
                if parent_key == "ROOT":
                    item = getattr(self, key)
                try:
                    if not item == orig_dict[key]:
                        if key == "value":
                            # Value has been updated
                            parent.text = str(item)
                        else:
                            # Attribute has been updated
                            elem = parent.find(f"{self._ns}{key}")
                            if elem is not None:
                                if type(item) == list:
                                    elem.text = "\n".join(item)
                                else:
                                    elem.text = str(item)
                            else:
                                parent.set(key, str(item))
                except KeyError:
                    # New value/attribute added
                    self._recursive_add_element(
                        parent=parent, add_item=item, add_key=key
                    )
 


    def _recursive_add_element(self, parent, add_item, add_key):
        if type(add_item) == dict:
            new_element = etree.SubElement(parent, f"{self._ns}{add_key}")
            for key, item in add_item.items():
                self._recursive_add_element(
                    parent=new_element, add_item=item, add_key=key
                )
        elif type(add_item) == list:
            # new_element = etree.SubElement(parent, f"{self._ns}{add_key}")
            if add_key == "variables":
                # Variables is special case where we have list but add to one element
                new_element = etree.SubElement(parent, f"{self._ns}{add_key}")
                new_element.text = "\n".join(add_item)
            else:
                for item in add_item:
                    self._recursive_add_element(
                        parent=parent, add_item=item, add_key=add_key
                    )
        else:
            if add_key == "value":  # Value has been added
                parent.text = str(add_item)
            else:  # Attribute or element added
                # Check schema to see if we should use parent.set for attribute
                # or etree.subelement() and set text
                schema_elem = self._xsd.findall(
                    f".//{{http://www.w3.org/2001/XMLSchema}}*[@name='{add_key}']"
                )
                if len(schema_elem) == 1:
                    schema_elem = schema_elem[0]
                else:
                    # This is just here for when there's multiple schema elements with same
                    # name, e.g. 'frequency'
                    parent_schema_elem = self._xsd.find(
                        f".//{{http://www.w3.org/2001/XMLSchema}}*[@name='{parent.tag.replace(self._ns, '')}']"
                    )
                    if "type" in parent_schema_elem.attrib:
                        parent_schema_elem = self._xsd.find(
                            f".//{{http://www.w3.org/2001/XMLSchema}}*[@name='{parent_schema_elem.attrib['type']}']"
                        )
                    schema_elem = parent_schema_elem.find(
                        f".//{{http://www.w3.org/2001/XMLSchema}}*[@name='{add_key}']"
                    )

                if schema_elem.tag.endswith("attribute"):
                    parent.set(add_key, str(add_item))

                else:
                    new_element = etree.SubElement(parent, f"{self._ns}{add_key}")
                    new_element.text = str(add_item)

    def _recursive_remove_data_xml(self, orig_dict, new_dict, parent_key, list_idx=None):
        # This method will recursively work through the original dictionary and remove any
        # items that are not in the new_dictionary and need to be removed.

        
        for key, item in orig_dict.items():
            if parent_key == "ROOT":
                parent = self._xmltree.getroot()
            else:
                parent = self._xmltree.findall(f".//{self._ns}{parent_key}")[
                    list_idx or 0
                ]

            if key not in new_dict:
            # New key added, add recursively
                self._remove_element(parent=parent, remove_item=item, remove_key=key)

            elif type(item) == dict:
                self._recursive_remove_data_xml(item, new_dict[key], key, list_idx)
            elif type(item) == list and key != "variables":  # needs handling, need to iterate through list of things.
                for i, _item in enumerate(item):
                    if _item in new_dict[key]:
                        self._recursive_remove_data_xml(_item, new_dict[key][i], key, list_idx)  # double check item or _item
                    else:
                        self._remove_element(parent=parent, remove_item=_item, remove_key=key)  # double check item or _item
                    if type(_item) == dict:
                        if _item in new_dict[key]:
                            self._recursive_remove_data_xml(
                                _item, new_dict[key][i], key, list_idx=i
                            )
                        else:
                            self._remove_element(parent=parent, remove_item=_item, remove_key=key)
                       
            # else:
            #     if parent_key == "ROOT":
            #         item = getattr(self, key)
            #     try:
            #         if not item == new_dict[key]:  #problem with this part
            #             if key == "value":
            #                 # Value found to be removed
            #                 self._remove_element(parent=parent, remove_item=item, remove_key=key)
            #             else:
            #                 # Attribute has been found to be removed
            #                 elem = parent.find(f"{self._ns}{key}")
            #                 if elem is not None:
            #                     if type(item) == list:
            #                         self._remove_element(parent=parent, remove_item=item, remove_key=key)
            #                     else:
            #                         self._remove_element(parent=parent, remove_item=item, remove_key=key)
            #                 else:
            #                     self._remove_element(parent=parent, remove_item=item, remove_key=key)
            #     except KeyError:
            #         # New value/attribute added
            #         self._remove_element(
            #             parent=parent, remove_item=item, remove_key=key
            #         )

    def _remove_element(self, parent, remove_item, remove_key):
        # This function will remove the element from the xml file at the highest
        # level possible.
        #
        # Inputs:
            # parent - this is the path of the item to be removed
            # remove_item - the item to be removed
            # remove_key - the corresponding key
        #
        # Outputs:
            # self - with features removed

        # need to detail path to specific parent
        # Step 1: Find right path, locally with the problem you want to solve
        # Step 2: Now loop through to find the branch that we want to cut off
        #
        # WORRY - how do we know we are in the right path, could be trying to cut BC1 from domain 2 and how
        # does it know to cut it from domain 2 and not domain 1? We are going to have to be careful of how 
        # the branch is passed in.
        #
        # Potential solution? xpath() can 
        
        # Pseudocode idea - similar to stack overflow
        for r in somepath:# could this be useful? f".//{{http://www.w3.org/2001/XMLSchema}}*[@name='{add_key}']"
            r.getparent().remove(r)
        etree._Element.parent.remove(remove_key)

            


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
                    self._data["domain"] = [
                        domain for _, domain in self.domains.items()
                    ]
                else:
                    self._data[attr] = getattr(self, attr)

    def _write(self) -> str:
        try:
            self._update_dict()
            self._recursive_update_xml(self._data, self._raw_data, "ROOT")
            self._recursive_remove_data_xml(self._data, self._raw_data, "ROOT")
            etree.indent(self._xmltree, space="    ")
            try:
                self._validate()
            except:
                self._recursive_reorder_xml()
                self._recursive_remove_data_xml()
                self._validate()

            self._raw_data = deepcopy(self._data)  # reset raw data to equal data

            return f'<?xml version="1.0" standalone="yes"?>\n{etree.tostring(self._xmltree.getroot()).decode()}'

        except Exception as e:
            self._handle_exception(e, when="write")

    def _get_multi_value_keys(self):
        self._multi_value_keys = []
        root = self._xsd.getroot()
        for elem in root.findall(".//{http://www.w3.org/2001/XMLSchema}element"):
            if elem.attrib.get("maxOccurs") not in (None, "0", "1"):
                self._multi_value_keys.append(elem.attrib["name"])
        self._multi_value_keys = set(self._multi_value_keys)

    def diff(self, other: "XML2D", force_print: bool = False) -> None:
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

    def save(self, filepath: Optional[Union[str, Path]]):
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

    def simulate(
        self,
        method: Optional[str] = "WAIT",
        raise_on_failure: Optional[bool] = True,
        precision: Optional[str] = "DEFAULT",
        enginespath: Optional[str] = "",
    ) -> Optional[Popen]:

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



        Raises:
            UserWarning: Raised if ief filepath not already specified

        Returns:
            subprocess.Popen(): If method == 'RETURN_PROCESS', the Popen() instance of the process is returned.

        """

        try:
            if self._filepath == None:
                raise UserWarning(
                    "xml2D must be saved to a specific filepath before simulate() can be called."
                )
            if precision.upper() == "DEFAULT":
                precision = "SINGLE"  # defaults to single precision
                for attr in dir(self):
                    if (
                        attr.upper() == "LAUNCHDOUBLEPRECISIONVERSION"
                    ):  # Unless DP specified
                        if getattr(self, attr) == "1":
                            precision = "DOUBLE"
                            break

            if enginespath == "":
                _enginespath = (
                    r"C:\Program Files\Flood Modeller\bin"  # Default location
                )
            else:
                _enginespath = enginespath
                if not Path(_enginespath).exists:
                    raise Exception(
                        f"Flood Modeller non-default engine path not found! {str(_enginespath)}"
                    )

            # checking if all schemes used are fast, if so will use FAST.exe
            # TODO: Add in option to choose to use or not to use if you can
            is_fast = True
            for dom in xml2d._raw_data["domain"]:
                if dom["run_data"]["scheme"] != "FAST":
                    is_fast = False
                    break

            if is_fast == True:
                isis2d_fp = str(Path(_enginespath, "FAST.exe"))
            elif precision.upper() == "SINGLE":
                isis2d_fp = str(Path(_enginespath, "ISIS2d.exe"))
            else:
                isis2d_fp = str(Path(_enginespath, "ISIS2d_DP.exe"))

            if not Path(isis2d_fp).exists:
                raise Exception(
                    f"Flood Modeller engine not found! Expected location: {isis2d_fp}"
                )

            run_command = f'"{isis2d_fp}" -q "{self._filepath}"'

            if method.upper() == "WAIT":
                # executing simulation
                print("Executing simulation ... ")
                process = Popen(
                    run_command, cwd=os.path.dirname(self._filepath)
                )  # execute

                # No log file in 2D solver therefore no reference to log file
                # or progress bar, instead we check the exit code, 100 is everything
                # is fine, anything else is a code that means something has gone wrong!

                # progress bar based on log files:
                self._init_log_file()
                self._update_progress_bar(process)

                while process.poll() is None:
                    # process is still running
                    time.sleep(1)

                exitcode = process.returncode
                self._interpret_exit_code(exitcode)

                ### Here we need something that will print/store the
                ### exit code value so we know if it is working well or not.

            elif method.upper() == "RETURN_PROCESS":
                # executing simulation
                print("Executing simulation ...")
                process = Popen(
                    run_command, cwd=os.path.dirname(self._filepath)
                )  # execute simulation
                return process

        except Exception as e:
            self._handle_exception(e, when="simulate")

    def _get_result_filepath(self, suffix):

        if hasattr(self, "Results"):
            path = Path(self.Results).with_suffix("." + suffix)
            if not path.is_absolute():
                # set cwd to xml2d location and resolve path
                path = Path(self._filepath.parent, path).resolve()

        else:
            path = self._filepath.with_suffix("." + suffix)

        return path

    def get_results(self) -> ZZN:
        """If results for the simulation exist, this function returns them as a ZZN class object.

        Returns:
            floodmodeller_api.ZZN class object
        """

        # Get zzn location
        result_path = self._get_results_filepath(suffix="zzn")

        if result_path.exists():
            return ZZN(result_path)

        else:
            raise FileNotFoundError("Simulation results file (zzn) not found")

    def get_log(self):
        """If log files for the simulation exist, this function returns them as a LF1 class object

        Returns:
            floodmodeller_api.LF2 class object
        """
        suffix = "lf2"
        # Get lf location
        lf_path = self._get_result_filepath(suffix)

        if not lf_path.exists():
            raise FileNotFoundError("Log file (" + suffix + ") not found")

        return lf_factory(lf_path, suffix, False)

    def _init_log_file(self):
        """Checks for a new log file, waiting for its creation if necessary"""
        suffix = "lf2"
        # not needed in this case
        # # ensure progress bar is supported for that type
        # if not ( suffix == 'lf2' and (not steady)): #again does this need changing?? FLAG
        #     #need a comment inserting here FLAG
        #     self._lf = None
        #     return

        # find what log filepath should be
        lf_filepath = self._get_result_filepath(suffix)

        # wait for log file to exist
        log_file_exists = False
        max_time = time.time() + 10

        while not log_file_exists:

            time.sleep(0.1)

            log_file_exists = lf_filepath.is_file()

            # timeout
            if time.time() > max_time:
                self._no_log_file("log file is expected but not detected")
                self._lf = None
                return

        # wait for new log file
        old_log_file = True
        max_time = time.time() + 10

        while old_log_file:

            time.sleep(0.1)

            # difference between now and when log file was last modified
            last_modified_timestamp = lf_filepath.stat().st_mtime
            last_modified = dt.datetime.fromtimestamp(last_modified_timestamp)
            time_diff_sec = (dt.datetime.now() - last_modified).total_seconds()

            # it's old if it's over 5 seconds old (TODO: is this robust?)
            old_log_file = time_diff_sec > 5

            # timeout
            if time.time() > max_time:
                self._no_log_file("log file is from previous run")
                self._lf = None
                return

        # create LF instance
        self._lf = lf_factory(lf_filepath, suffix, False)

    def _no_log_file(self, reason):
        """Warning that there will be no progress bar"""

        print("No progress bar as " + reason + ". Simulation will continue as usual.")

    def _update_progress_bar(self, process: Popen):
        """Updates progress bar based on log file"""

        # only if there is a log file
        if self._lf is None:
            return

        # tqdm progress bar
        for i in trange(100):

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

    def _interpret_exit_code(self, exitcode):
        """This function will interpret the exit code and tell us if this is good or bad

        Args:
            exitcode - this is the exitcode from the simulation

        Return:
            String that explains the exitcode - this might be too much!
        """

        # TODO: Expand this to a dict that will tell us what the code means.
        # Description = error_2D_dict.get(exitcode, None)

        if exitcode is None:
            print(f"Exit code not in dictionary, Error code: {exitcode}")

        else:
            print(f"Exit with {exitcode}: {error_2D_dict[exitcode]}")
