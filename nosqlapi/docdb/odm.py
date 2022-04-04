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

"""ODM module for document NOSQL database."""

# region Imports
from functools import wraps
from json import dumps

from nosqlapi.common.odm import Uuid

from nosqlapi.kvdb.odm import Keyspace

# endregion

# region global variable
__all__ = ['Database', 'Collection', 'Document', 'Index', 'document']


# endregion

# region Classes
class Database(Keyspace):

    """Represents database"""

    pass


class Collection:

    """Represents collection of documents"""

    def __init__(self, name, *docs):
        """Collection object

        :param name: Name of collection
        :param docs: Documents like dict
        """
        self.name = name
        self._docs = []
        if docs:
            self._docs.extend(list(docs))

    @property
    def docs(self):
        """Documents of collection"""
        return self._docs

    def append(self, doc):
        """Append document to collection

        :param doc: Documents like dict
        :return: None
        """
        self._docs.append(doc)

    def pop(self, doc=-1):
        """Delete document from collection

        :param doc: Number of document to remove
        :return: None
        """
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

    """Represents document"""

    def __init__(self, value=None, oid=None, **values):
        """Document object

        :param value: Body of document like dict
        :param oid: String id (default uuid1 string)
        :param values: Additional values of body
        """
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
        """Document unique id"""
        return self._id

    @property
    def body(self):
        """Elements of document"""
        return self._body

    @body.setter
    def body(self, value):
        """Elements of document"""
        if isinstance(value, dict):
            self._body = value
        else:
            raise ValueError('value must be a dict')

    def to_json(self, indent=2):
        """Transform document into json

        :param indent: Number of indentation
        :return: str
        """
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

    """Represents document index"""

    def __init__(self, name, data):
        """Index object

        :param name: Name of index
        :param data: Data of index like dict
        """
        self.name = name
        self.data = {}
        self.data.update(data)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return f"Index({', '.join(f'{key}={value}' for key, value in self.data.items())})"

# endregion


# region Functions
def document(func):
    """Decorator function to transform dictionary object to Document object

    :param func: function to decorate
    :return: Document object
    """
    @wraps(func)
    def inner(*args, **kwargs):
        data = func(*args, **kwargs)
        if not isinstance(data, dict):
            raise ValueError(f"function {func.__name__} doesn't return a dict")
        return Document(value=data)

    return inner

# endregion
