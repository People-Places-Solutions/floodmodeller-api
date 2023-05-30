import pandas as pd

from ._base import Unit
from .helpers import (
    join_10_char,
    join_12_char_ljust,
    join_n_char_ljust,
    split_10_char,
    split_12_char,
    split_n_char,
    _to_float,
    _to_int,
)
from floodmodeller_api.validation import _validate_unit



class COMMENT(Unit):
    """Class to hold and process Comments within dat file 

    Args:
        text (str, optional): comment text.

    Returns:
        COMMENT: Flood Modeller COMMENT within dat file object"""

    _unit = "COMMENT"

    def _read(self, block):
        """Function to read a given COMMENT block and store data as class attributes"""
        self.text = block[0].strip()


    def _write(self):
        """Function to write a valid INTERPOLATE block"""
        block = [self._unit]
    
        # Number of comment lines
        num_lines = len(self.comment.strip().split("\n"))
        num_lines_line = "{:>10}".format(str(num_lines))
        block.append(num_lines_line)
    
        # Comment text lines
        comment_text = self.comment.strip().split("\n")
        block.extend(comment_text)
    
        return block

    def _create_from_blank(self, text = ''):

        for param, val in {
            "comment text": text,
        }.items():
            setattr(self, param, val)
        
        
