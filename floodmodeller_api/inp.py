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

        # Generate DAT structure
        self._update_dat_struct()
        

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
        # Get general paramers from INP file. 
        
        #Sample code below:
        '''self.title = self._raw_data[0]
        self.general_parameters = {}
        params = units.helpers.split_10_char(self._raw_data[2])
        if len(params) == 6:
            # Adds the measurements unit if not specified
            params.append('DEFAULT')
        params.extend(units.helpers.split_10_char(self._raw_data[3]))
        self.general_parameters['Node Count'] = int(params[0])
        self.general_parameters['Lower Froude'] = float(params[1])
        self.general_parameters['Upper Froude'] = float(params[2])
        self.general_parameters['Min Depth'] = float(params[3])
        self.general_parameters['Convergence Direct'] = float(params[4])
        self._label_len = int(params[5])  # label length
        self.general_parameters['Units'] = params[6]
        self.general_parameters['Water Temperature'] = float(params[7])
        self.general_parameters['Convergence Flow'] = float(params[8])
        self.general_parameters['Convergence Head'] = float(params[9])
        self.general_parameters['Mathematical Damping'] = float(params[10])
        self.general_parameters['Pivotal Choice'] = float(params[11])
        self.general_parameters['Under-relaxation'] = float(params[12])
        self.general_parameters['Matrix Dummy'] = float(params[13])
        self.general_parameters['RAD File'] = self._raw_data[5]
        '''
        pass
    
    def _get_unit_definitions(self):
        pass

    def _update_dat_struct(self):
        """Internal method used to update self._inp_struct which details the overall structure of the inp file as a list of blocks, each of which
            are a dictionary containing the 'start', 'end' and 'type' of the block.

        """

       # Generate DAT structure
        inp_struct = []
        in_block = False
        in_general = False
        in_title = False
        title_n = None  # Used as counter for number of lines in a comment block #TODO: Review what is no longer needed
        general_block = {'start': 0, 'Type': 'GENERAL'}
        unit_block = {}
        for idx, line in enumerate(self._raw_data):
            
            if line == '[TITLE]':
                in_title = True

                #TODO is this needed?
                if in_block == True: 
                    unit_block['end'] = idx - 1  # add ending index
                    # append existing block to the inp_struct
                    inp_struct.append(unit_block)
                    unit_block = {}  # reset bdy block '''

                # start new block for COMMENT
                unit_block['Type'] = line.split(' ')[0]
                unit_block['start'] = idx  # add starting index
                continue


            '''# Deal with comment blocks explicitly as they could contain unit keywords
            if in_title and title_n is None: #TODO: what does this sction do?
                title_n = int(line.strip())
                continue
            elif in_title:
                title_n -= 1
                if title_n == 0:
                    unit_block['end'] = idx  # add ending index
                    # append existing bdy block to the dat_struct
                    dat_struct.append(unit_block)
                    unit_block = {}  # reset bdy block
                    in_comment = False
                    in_block = False
                    comment_n = None
                    continue
                else:
                    continue  # move onto next line as still in comment block'''
            

        if len(unit_block) != 0:
            # Only adds end block if there is a block present (i.e. an empty DAT stays empty)
            # add ending index for final block
            unit_block['end'] = len(self._raw_data) - 1
            inp_struct.append(unit_block)  # add final block

        self._inp_struct = inp_struct

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


