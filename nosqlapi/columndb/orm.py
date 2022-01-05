#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# orm -- nosqlapi
#
#     Copyright (C) 2021 Matteo Guadrini <matteo.guadrini@hotmail.it>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""ORM module for column NOSQL database."""

# region Imports
from collections import namedtuple

from nosqlapi.common import Counter
from nosqlapi.kvdb.orm import Keyspace as Ks

# endregion

# region global variable
__all__ = ['Keyspace', 'Table', 'Column', 'Index']


# endregion

# region Classes
class Keyspace(Ks):
    """Represents keyspace like database"""
    pass


class Table:
    """Represents table as container of columns"""

    def __init__(self, name, *columns, **options):
        self._name = name
        self._columns = [column for column in columns]
        self._options = options
        self._index = []

    @property
    def name(self):
        """Name of table"""
        return self._name

    @name.setter
    def name(self, value):
        """Name of table"""
        self._name = value

    @property
    def columns(self):
        """List of columns"""
        return self._columns

    @property
    def options(self):
        """Options"""
        return self._options

    @property
    def index(self):
        """List of indexes"""
        return self._index

    def add_column(self, column):
        """Adding one column to table

        :param column: column name or object
        :return: None
        """
        self._columns.append(column)

    def delete_column(self, index=-1):
        """Deleting one column to table

        :param index: number of index
        :return: None
        """
        self._columns.pop(index)

    def set_option(self, option):
        """Update options

        :param option: dict options
        :return: None
        """
        self._options.update(option)

    def get_rows(self):
        """Getting all rows

        :return: List[tuple]
        """
        return [tuple([col[i] for col in self.columns])
                for i in range(len(self.columns))]

    def add_index(self, index):
        """Adding index to index property

        :param index: name or Index object
        :return: None
        """
        self._index.append(index)

    def delete_index(self, index=-1):
        """Deleting index to index property

        :param index: name or Index object
        :return: None
        """
        self._index.pop(index)

    def __getitem__(self, item):
        return self._columns[item]

    def __setitem__(self, key, value):
        self._columns[key] = value

    def __delitem__(self, key=-1):
        self._columns.pop(key)

    def __iter__(self):
        return (column for column in self.columns)

    def __repr__(self):
        return f'{self.__class__.__name__} object, name={self.name}>'

    def __str__(self):
        return f'{self.columns}'


class Column:
    """Represents column as container of values"""

    def __init__(self, name, of_type=None, max_len=None):
        self.name = name
        self._of_type = of_type
        self.max_len = max_len
        self._data = []
        self._auto_increment = False

    @property
    def of_type(self):
        """Type of column"""
        return self._of_type

    @property
    def data(self):
        """List of values"""
        return self._data

    @property
    def auto_increment(self):
        """Auto-increment value"""
        return self._auto_increment

    @auto_increment.setter
    def auto_increment(self, value: bool):
        """Auto-increment value"""
        if value is not bool:
            raise TypeError('auto_increment must be a bool value')
        self._auto_increment = value

    def append(self, data=None):
        """Appending data to column.
        If auto_increment is True, the value is incremented automatically.

        :param data: any type of data
        :return: None
        """
        if self.max_len and len(self._data) >= self.max_len:
            raise IndexError(f'maximum number of satisfied data: {self.max_len}')
        if not isinstance(data, self.of_type) and self.of_type is not None:
            raise TypeError(f'the data must be of the type {self.of_type} or NoneType')
        if self.auto_increment:
            if isinstance(self.of_type, (int, float, Counter)):
                try:
                    last = self.data[-1]
                    self._data.append(last + 1)
                except IndexError:
                    self._data.append(1)
        else:
            self._data.append(data)

    def pop(self, index=-1):
        """Deleting value

        :param index: number of index
        :return: None
        """
        self._data.pop(index)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key=-1):
        self.pop(key)

    def __iter__(self):
        return (item for item in self.data)

    def __repr__(self):
        return f'{self.__class__.__name__} object, name={self.name} type={self.of_type.__class__.__name__}>'

    def __str__(self):
        return f'{self.data}'


# endregion

# region Other objects
Index = namedtuple('Index', ['name', 'table', 'column'])

# endregion
