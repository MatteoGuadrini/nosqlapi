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
        self._options = {k: v for k, v in options.items()}

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

    def set_option(self, option):
        self._options.update(option)

    def __getitem__(self, item):
        return self._columns[item]

    def __repr__(self):
        return f'{self.__class__.__name__} object, name={self.name}>'

    def __str__(self):
        return f'{self.columns}'

# endregion
