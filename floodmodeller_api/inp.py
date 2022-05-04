'''
Flood Modeller Python API
Copyright (C) 2022 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
'''

from pathlib import Path
from typing import Optional, Union

from ._base import FMFile

class INP(FMFile):
    """Reads and writes Flood Modeller 1DUrban file format '.inp'

    Args:
        inp_filepath (str, optional): Full filepath to inp file. If not specified, a new INP class will be created. Defaults to None. 

    Output:
        Initiates 'INP' class object

    Raises:
        TypeError: Raised if inp_filepath does not point to a .inp file
        FileNotFoundError: Raised if inp_filepath points to a file which does not exist
    """

    _filetype: str = 'INP'
    _suffix:str = '.inp'

    
    def __init__(self, inp_filepath: Optional[Union[str, Path]] = None):
        self._filepath = inp_filepath  
        if self._filepath != None:
            FMFile.__init__(self)
            self._read()
        else:
            self._create_from_blank()
            
        self._get_general_parameters()
        self._get_unit_definitions()

    def _read(self):
        # Read INP data
        with open(self._filepath, 'r') as inp_file:
            self._raw_data = [line.rstrip('\n')
                              for line in inp_file.readlines()]
        pass
        # Generate DAT structure
        #self._update_inp_struct()
        

    def _write(self) -> str:
        """Returns string representation of the current INP data

        Returns:
            str: Full string representation of INP in its most recent state (including changes not yet saved to disk)
        """
        
        inp_string = ''
        for line in self._raw_data:
            inp_string += line + '\n'

        return inp_string

    def _create_from_blank(self):
        pass
    
    def _get_general_parameters(self):
        pass
    
    def _get_unit_definitions(self):
        pass

    def update(self) -> None:
        """ Updates the existing INP based on any altered attributes """
        self._update()

    def save(self, filepath: Union[str, Path]) -> None:
        """Saves the INP to the given location, if pointing to an existing file it will be overwritten. 
        Once saved, the INP() class will continue working from the saved location, therefore any further calls to INP.update() will 
        update in the latest saved location rather than the original source INP used to construct the class

        Args:
            filepath (str): Filepath to new save location including the name and '.inp' extension

        Raises:
            TypeError: Raised if given filepath doesn't point to a file suffixed '.inp'
        """
        filepath = Path(filepath).absolute()
        self._save(filepath)


