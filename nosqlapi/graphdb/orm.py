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

"""ORM module for graph NOSQL database."""

# region Imports
from collections import namedtuple

from nosqlapi.kvdb.orm import Keyspace
from ..common.orm import Text

# endregion

# region global variable
__all__ = ['Label', 'Property', 'RelationshipType', 'Database', 'Node', 'Relationship', 'Index']


# endregion


# region Classes
class Label(Text):

    """Label of node"""

    pass


class Property(dict):

    """Property of node"""

    def __repr__(self):
        out = []
        for key, value in self.items():
            pair = f'{key}: '
            if isinstance(value, str):
                pair += f"'{value}'"
            else:
                pair += f'{value}'
            out.append(pair)
        return '{{{pairs}}}'.format(pairs=', '.join(out))


class RelationshipType(Label):

    """Type of relationship like a label"""

    pass


class Database(Keyspace):

    """Represents database"""

    def __init__(self, name, address=None, role=None, status=None, default=False):
        super().__init__(name=name)
        self.address = address
        self.role = role
        self.status = status
        self.default = default

    @property
    def online(self):
        """Status of database"""
        if self.status == 'online':
            return True
        else:
            return False


class Node:

    """Represents node"""

    def __init__(self, labels, properties=None, var=''):
        self.labels = []
        self.labels.extend(labels)
        self.properties = Property()
        self.var = var
        if properties:
            self.properties.update(properties)

    def add_label(self, label):
        """Add label to node

        :param label: label string or object
        :return: None
        """
        self.labels.append(label)

    def delete_label(self, index=-1):
        """Delete label

        :param index: number of index
        :return: None
        """
        self.labels.pop(index)

    def __getitem__(self, item):
        return self.properties[item]

    def __setitem__(self, key, value):
        self.properties[key] = value

    def __delitem__(self, key):
        del self.properties[key]

    def __str__(self):
        return f'({self.var}:{":".join(self.labels)} {self.properties})'

    def __repr__(self):
        return f'{self.__class__.__name__} object, labels={self.labels}>'


class Relationship(Node):

    """Represents relationship among nodes"""

    def __str__(self):
        return f'[{self.var}:{":".join(self.labels)} {self.properties}]'

    def __repr__(self):
        return f'{self.__class__.__name__} object, type={self.labels}>'


# endregion

# region Other objects
Index = namedtuple('Index', ['name', 'node', 'properties', 'options'], defaults=(None,))

# endregion
