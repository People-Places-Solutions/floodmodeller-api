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

''' Holds the base unit class for all FM 1D units Units '''

# REVIEW: Is this need, or can i make use of the units._base? Really not sure what's going on here

class Urban1D:
    _unit = None
    _subtype = None
    _name = None

    def __init__(self, unit_block=None, n=12, **kwargs):
        self._label_len = n
        if unit_block != None:
            self._read(unit_block)
        else:
            self._create_from_blank(**kwargs)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def subtype(self):
        return self._subtype

    @subtype.setter
    def subtype(self, new_value):
        raise ValueError ("You cannot changed the subtype of a unit once it has been instantiated")


    def __repr__(self):
        if self._subtype is None:
            return f'<floodmodeller_api Unit Class: {self._unit}(name={self._name})>'
        else:
            return f'<floodmodeller_api Unit Class: {self._unit}(name={self._name}, type={self._subtype})>'

    def _create_from_blank(self):
        raise NotImplementedError(
                f'Creating new {self._unit} units is not yet supported by floodmodeller_api, only existing units can be read')
           
    def __str__(self):
        return '\n'.join(self._write())

    def _read(self):
        raise NotImplementedError

    def _write(self):
        raise NotImplementedError