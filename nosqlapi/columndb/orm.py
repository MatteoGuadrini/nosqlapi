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

# region Imports
from nosqlapi.kvdb.orm import Keyspace

# endregion

# region Classes
Keyspace = Keyspace


class Table:

    def __init__(self, name, *columns, **options):
        self._name = name
        self._columns = [column for column in columns]
        self._options = options

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def columns(self):
        return self._columns

    @property
    def options(self):
        return self._options

    def add_column(self, column):
        self._columns.append(column)

    def delete_column(self, index=-1):
        del self[index]

    def set_option(self, option):
        self._options.update(option)

    def __getitem__(self, item):
        return self._columns[item]

    def __setitem__(self, key, value):
        self._columns[key] = value

    def __delitem__(self, key=-1):
        self._columns.pop(key)

    def __repr__(self):
        return f'{self.__class__.__name__} object, name={self.name}>'

    def __str__(self):
        return f'{self.columns}'


class Column:

    def __init__(self, name, of_type=None, max_len=None):
        self.name = name
        self._of_type = of_type
        self.max_len = max_len
        self._data = []
        self._auto_increment = False

    @property
    def of_type(self):
        return self._of_type

    @property
    def data(self):
        return self._data

    @property
    def auto_increment(self):
        return self._auto_increment

    @auto_increment.setter
    def auto_increment(self, value: bool):
        if value is not bool:
            raise TypeError('auto_increment must be a bool value')
        self._auto_increment = value

    def append(self, data):
        if self.max_len and len(self._data) >= self.max_len:
            raise IndexError(f'maximum number of satisfied data: {self.max_len}')
        if data is not self._of_type:
            raise TypeError(f'the data must be of the type {self.of_type}')
        self._data.append(data)

    def pop(self, index=-1):
        self._data.pop(index)

# endregion
