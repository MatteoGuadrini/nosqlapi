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
from nosqlapi.common.orm import Uuid
from json import dumps


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

    def __iter__(self):
        return (doc for doc in self.docs)


class Document:

    def __init__(self, value=None, oid=None, **values):
        self._body = {}
        if not oid:
            self._id = Uuid()
            self['_id'] = self.id.__str__()
        else:
            self._id = self['_id'] = oid
        if value is not None or isinstance(value, dict):
            self._body.update(value)
        if values:
            self._body.update(values)

    @property
    def id(self):
        return self._id

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        if isinstance(value, dict):
            self._body = value
        else:
            raise ValueError('value must be a dict')

    def to_json(self, indent=2):
        return dumps(self.body, indent=indent)

    def __getitem__(self, item):
        return self.body[item]

    def __setitem__(self, key, value):
        self._body[key] = value

    def __delitem__(self, key):
        del self._body[key]

    def __repr__(self):
        return f'<{self.__class__.__name__} object, id={self.id}>'

    def __str__(self):
        return f'{self.body}'

    def __len__(self):
        return len(self.body)

    def __iter__(self):
        return (key for key in self.body)


class Index:

    def __init__(self, name, data):
        self.name = name
        self.data = {}
        self.data.update(data)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]


# endregion
