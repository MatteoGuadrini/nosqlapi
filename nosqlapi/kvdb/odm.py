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

"""ODM module for key-value NOSQL database."""

# region Imports
from collections import namedtuple

# endregion

# region global variable
__all__ = ['Keyspace', 'Subspace', 'Transaction', 'Item', 'ExpiredItem', 'Index']


# endregion

# region Classes
class Transaction:

    """Represents group of commands in a single step"""

    def __init__(self, commands=None):
        """Transaction object

        :param commands: List of commands
        """
        if commands is None:
            commands = []
        self._commands = commands

    @property
    def commands(self):
        """Command list"""
        return list(enumerate(self._commands))

    def add(self, command, index=-1):
        """Add command to commands list

        :param command: Command string
        :param index: Index to append command
        :return: None
        """
        if index == -1:
            self._commands.append(command)
        else:
            self._commands.insert(index, command)

    def delete(self, index=-1):
        """Remove command to command list

        :param index: Index to remove command
        :return: None
        """
        self._commands.pop(index)

    def __getitem__(self, item):
        return self._commands[item]

    def __setitem__(self, key, value):
        self._commands[key] = value

    def __delitem__(self, key):
        del self._commands[key]

    def __repr__(self):
        return f'<{self.__class__.__name__} object, commands={len(self.commands)}>'

    def __str__(self):
        return '\n'.join(command for command in self._commands)

    def __iter__(self):
        return (command for command in self._commands)


class Keyspace:

    """Represents keyspace like database"""

    def __init__(self, name, exists=False):
        """Keyspace object

        :param name: Name of keyspace
        :param exists: Existing keyspace (default False)
        """
        self._name = name
        self._exists = exists
        self._store = []

    @property
    def name(self):
        """Name of keyspace"""
        return self._name

    @name.setter
    def name(self, value):
        """Name of keyspace"""
        self._name = value

    @property
    def exists(self):
        """Existence of keyspace"""
        return self._exists

    @property
    def store(self):
        """List of object into keyspace"""
        return self._store

    def append(self, item):
        """Append item into store

        :param item: Key/value item
        :return: None
        """
        self._store.append(item)

    def pop(self, item=-1):
        """Remove item from the store

        :param item: Index of item to remove
        :return: None
        """
        self._store.pop(item)

    def __getitem__(self, item):
        return self.store[item]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __repr__(self):
        return f'<{self.__class__.__name__} object, name={self.name}>'

    def __str__(self):
        return f'{self.store}'

    def __len__(self):
        return len(self.store)

    def __iter__(self):
        return (obj for obj in self._store)


class Subspace(Keyspace):

    """Represents subspace of the keyspace"""

    def __init__(self, name, sub=None, sep='.'):
        """Subspace object

        :param name: Name of keyspace
        :param sub: Subname of keyspace
        :param sep: Separation character
        """
        super().__init__(name)
        if sub:
            self.name += sep + sub


class Item:

    """Represents key/value like a dictionary"""

    def __init__(self, key, value=None):
        """Item object

        :param key: Key of item
        :param value: Value of item
        """
        self._key = key
        self._value = value
        self.__dict = {}
        self.set(key, value)

    @property
    def key(self):
        """Key of item"""
        return self._key

    @property
    def value(self):
        """Value of the key"""
        return self._value

    def get(self):
        """Get item

        :return: dict
        """
        return self.__dict

    def set(self, key, value=None):
        """Set item

        :param key: Key of item
        :param value: Value of the key
        :return: None
        """
        self[key] = value

    def __getitem__(self, item):
        return self.__dict.get(item)

    def __setitem__(self, key, value):
        if not self.__dict.get(key):
            self.__dict.clear()
        self.__dict[key] = value
        self._key = key
        self._value = value

    def __delitem__(self, key):
        del self.__dict[key]

    def __repr__(self):
        return f'<{self.__class__.__name__} object, key={self.key} value={self.value}>'

    def __str__(self):
        return f'{self.__dict}'


class ExpiredItem(Item):

    """Represents Item object with ttl expired time"""

    def __init__(self, key, value=None, ttl=None):
        """ExpiredItem object

        :param key: Key of item
        :param value: Value of item
        :param ttl: Time to live of item
        """
        super().__init__(key, value)
        self._ttl = ttl
        self['ttl'] = self._ttl

    @property
    def ttl(self):
        """Time to live of item"""
        return self._ttl

    def __setitem__(self, key, value):
        if key == 'ttl':
            self._ttl = value
            self['ttl'] = self._ttl
        else:
            if not self.__dict.get(key):
                self.__dict.clear()
            self.__dict[key] = value
            self._key = key
            self._value = value
            self.__dict['ttl'] = self._ttl

    def __repr__(self):
        return f'<{self.__class__.__name__} object, key={self.key} value={self.value} ttl={self.ttl}>'


# endregion

# region Other objects
Index = namedtuple('Index', ['name', 'key'])

# endregion
