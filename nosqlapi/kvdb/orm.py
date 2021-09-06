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

# region Classes
class Item:

    def __init__(self, key, value=None):
        self._key = key
        self._value = value
        self.__dict = {}

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    def __getitem__(self, item):
        return self.__dict.get(item)

    def __setitem__(self, key, value):
        if not self.__dict.get(key):
            self.__dict.clear()
        self[key] = value
        self._key = value
        self._value = value

    def __delitem__(self, key):
        del self.__dict[key]

    def __repr__(self):
        return f'<{self.__class__.__name__} object, key={self.key} value={self.value}>'

    def __str__(self):
        return f'{self.__dict}'


# endregion
