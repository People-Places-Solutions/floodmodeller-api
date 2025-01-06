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
        self.text = "\n".join(block[2:])  # join into text

    def _write(self):
        """Function to write a valid comments block"""
        block = [self._unit]

        # Number of comment lines
        num_lines = len(self.text.split("\n"))
        block.append(f"{num_lines:>10}")

        # Comment text lines
        block.extend(self.text.split("\n"))

        return block

    def _create_from_blank(self, text=None):
        """Function to create an empty comment unit."""
        if text is None:
            text = ""
        self.text = text
