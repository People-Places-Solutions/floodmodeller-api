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
from pathlib import Path
from copy import deepcopy
from typing import Union, Optional
from lxml import etree
from floodmodeller_api._base import FMFile

def value_from_string(value: str):
    try:
        val = float(value)
        if not '.' in value:
            val = int(val)
        return val
    except ValueError:
        return value


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
        for key, data in self.data.items():
            #TODO: This only works for single domain atm
            # Need to have an attr called domains: list of each domain
            if key == 'domain':
                self.domains = {domain['domain_id']: domain for domain in data}
            else:
                setattr(self, key, data)

    def _create_dict(self):
        """Iterate through XML Tree to add all elements as class attributes"""
        xml_dict = {}
        root = self._xmltree.getroot()

        xml_dict.update(
            {"name": root.attrib["name"]}
        )

        xml_dict = self._recursive_elements_to_dict(xml_dict, root)
        self._raw_data = xml_dict
        self.data = deepcopy(self._raw_data)

    def _recursive_elements_to_dict(self, xml_dict, tree):
        # Some elements can have multiple instances e.g. domains. 
        # In these cases we need to have the id of that instance as a new key on the domain
        # e.g. xml.domains[domain_id]["computational_area"]... etc

        for child in tree:
            if isinstance(child, etree._Comment):
                continue # Skips comments in xml
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
            value = "" if child.text is None else child.text.replace("\n", "").strip()
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
        #TODO: Handle adding/removing params
        # For adding, need to use schema to check where it should be added. (or just 
        # assume user puts in right place and validate?)

        for key, item in new_dict.items():
            if parent_key == "ROOT":
                parent = self._xmltree.getroot()
            else:
                parent = self._xmltree.findall(f".//{self._ns}{parent_key}")[list_idx or 0]

            if type(item) == dict:
                self._recursive_update_xml(item, orig_dict[key], key, list_idx)
            elif type(item) == list:
                for i, _item in enumerate(item):
                    if type(_item) == dict:
                        self._recursive_update_xml(
                            _item, orig_dict[key][i], key, list_idx=i
                        )
                    
            else:
                if parent_key == "ROOT":
                    item = getattr(self, key)
                if not item == orig_dict[key]:
                    if key == "value":
                        # Value has been updated
                        parent.text = str(item)
                    else:
                        # Attribute has been updated
                        elem = parent.find(f"{self._ns}{key}")
                        if elem is not None:
                            elem.text = str(item)
                        else:
                            parent.set(key, str(item))

    def _write(self) -> str:
        try:
            self._recursive_update_xml(self.data, self._raw_data, "ROOT")
            self._validate()

            return f'<?xml version="1.0" standalone="yes"?>\n{etree.tostring(self._xmltree.getroot()).decode()}'

        except Exception as e:
            self._handle_exception(e, when="write")
    
    def _get_multi_value_keys(self):
        self._multi_value_keys = []
        root = self._xsd.getroot()
        for elem in root.findall('.//{http://www.w3.org/2001/XMLSchema}element'):
            if elem.attrib.get('maxOccurs') not in (None, '0', '1'):
                self._multi_value_keys.append(elem.attrib['name'])
        self._multi_value_keys = set(self._multi_value_keys)
        
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

    def simulate(self):
        raise NotImplementedError
