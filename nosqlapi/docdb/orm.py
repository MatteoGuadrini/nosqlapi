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
class Database(Keyspace):
    pass


class Collection:

    def __init__(self, name, *docs):
        self.name = name
        self._docs = []
        if docs:
            self._docs.extend(list(docs))

    @property
    def docs(self):
        return self._docs

    def append(self, doc):
        self._docs.append(doc)

    def pop(self, doc=-1):
        self._docs.pop(doc)

    def __getitem__(self, item):
        return self.docs[item]

    def __setitem__(self, key, value):
        self._docs[key] = value

    def __delitem__(self, key):
        del self._docs[key]

    def __repr__(self):
        return f'<{self.__class__.__name__} object, name={self.name}>'

    def __str__(self):
        return f'{self.docs}'

    def __len__(self):
        return len(self.docs)


# endregion
