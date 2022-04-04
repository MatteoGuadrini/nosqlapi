#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# odm -- nosqlapi
#
#     Copyright (C) 2022 Matteo Guadrini <matteo.guadrini@hotmail.it>
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

"""ODM module for column NOSQL database."""

# region Imports
from collections import namedtuple
from functools import wraps

from nosqlapi.common import Counter
from nosqlapi.kvdb.odm import Keyspace as Ks

# endregion

# region global variable
__all__ = ['Keyspace', 'Table', 'Column', 'Index', 'column']


# endregion

# region Classes
class Keyspace(Ks):

    """Represents keyspace like database"""

    pass


class Table:

    """Represents table as container of columns"""

    def __init__(self, name, *columns, **options):
        """Table object

        :param name: Name of table
        :param columns: Columns
        :param options: Options
        """
        self._name = name
        self._columns = [col for col in columns]
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

    @property
    def header(self):
        return tuple([col.name for col in self.columns])

    @property
    def primary_key(self):
        pk = [col.name for col in self.columns if col.primary_key]
        return pk[0]

    @primary_key.setter
    def primary_key(self, value: str):
        for col in self.columns:
            if col.name == value:
                col.primary_key = True

    def add_column(self, *columns):
        """Adding one or more column object to table

        :param columns: Column objects
        :return: None
        """
        self._columns.extend(columns)

    def delete_column(self, index=-1):
        """Deleting one column to table

        :param index: Number of index
        :return: None
        """
        self._columns.pop(index)

    def set_option(self, option):
        """Update options

        :param option: Dict options
        :return: None
        """
        self._options.update(option)

    def add_row(self, *rows):
        """Add one or more row into columns

        :param rows: Tuple of objects
        :return: None
        """
        for row in rows:
            # Check length of columns and row
            if len(row) != len(self.columns):
                raise ValueError(f"length of row {row} is different of length of columns {len(self.columns)}")
            for element, col in zip(row, self.columns):
                col.append(element)

    def delete_row(self, row=-1):
        """Delete one row into columns

        :param row: Index of row
        :return: None
        """
        for col in self.columns:
            col.pop(row)

    def get_rows(self):
        """Getting all rows

        :return: List[tuple]
        """
        return [dataset for dataset in self]

    def add_index(self, index):
        """Adding index to index property

        :param index: Name or Index object
        :return: None
        """
        self._index.append(index)

    def delete_index(self, index=-1):
        """Deleting index to index property

        :param index: Name or Index object
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
        return (tuple([col[index] for col in self.columns])
                for index in range(len(self.columns[0])))

    def __repr__(self):
        return f'<{self.__class__.__name__} object, name={self.name}>'

    def __str__(self):
        return f'{self.columns}'


class Column:

    """Represents column as container of values"""

    def __init__(self, name,
                 data=None,
                 of_type=None,
                 max_len=None,
                 auto_increment=False,
                 primary_key=False,
                 default=None):
        """Column object

        :param name: Name of column
        :param data. Data list or tuple
        :param of_type: Type of column
        :param max_len: Max length of column
        :param auto_increment: Boolean value (default False)
        :param primary_key: Set this column like a primary key
        :param default: Default function for generate data
        """
        self.name = name
        self._of_type = of_type if of_type is not None else object
        self.max_len = max_len
        self._data = [] if not data else list(data)
        self._default = default
        self._primary_key = primary_key
        self._auto_increment = auto_increment

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

    @property
    def default(self):
        return self._default

    @property
    def primary_key(self):
        return bool(self._primary_key)

    @primary_key.setter
    def primary_key(self, value):
        self._primary_key = bool(value)

    def append(self, data=None):
        """Appending data to column.
        If auto_increment is True, the value is incremented automatically.

        :param data: Any type of data
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
        elif self.default:
            if not callable(self.default):
                raise ValueError('default value must be callable without args')
            self._data.append(self.default())
        else:
            self._data.append(data)

    def pop(self, index=-1):
        """Deleting value

        :param index: Number of index
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

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f'<{self.__class__.__name__} object, name={self.name} type={self.of_type.__class__.__name__}>'

    def __str__(self):
        return f'{self.data}'


# endregion

# region Other objects
Index = namedtuple('Index', ['name', 'table', 'column'])


# endregion


# region Functions
def column(func):
    """Decorator function to transform list or tuple object to Column object

    :param func: function to decorate
    :return: Column object
    """
    @wraps(func)
    def inner(*args, **kwargs):
        data = func(*args, **kwargs)
        if not isinstance(data, (list, tuple)):
            raise ValueError(f"function {func.__name__} doesn't return a list or a tuple")
        return Column(name=func.__name__, data=data)

    return inner

# endregion
