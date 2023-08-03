"""
Flood Modeller Python API
Copyright (C) 2023 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

import pandas as pd
import math 

from ._base import Unit



class COMMENT(Unit):
    """Class to hold and process Comments within dat file 

    Args:
        text (str, optional): comment text.

    Returns:
        COMMENT: Flood Modeller COMMENT within dat file object"""

    _unit = "COMMENT"

    def _read(self, block):
        """Function to read a given COMMENT block and store data as class attributes"""
        self.text = block[2:] # join into text 


    def _write(self):
        """Function to write a valid comments block"""
        block = [self._unit]
    
        # Number of comment lines
        num_lines = math.ceil(len(self.text)/80)
        num_lines_line = "{:>10}".format(str(num_lines))
        block.append(num_lines_line)
    
        # Comment text lines
        text = self.text
        block.append(text)
    
        return block

    #def _create_from_blank(self, text = []):
        #for param, val in {"text": text,}.items():setattr(self, param, val)
        
    def _create_from_blank(self, text=None):
        '''Function to create an empty comment unit. '''
        if text is None:
            text = []
        setattr(self, 
                "text", 
                text)
