#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# utils -- nosqlapi
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

"""Utils function and classes for any type of NOSQL database"""

# region imports
from nosqlapi import ConnectError

# endregion

# region globals

API_COMPLIANT_METHODS = ('close', 'connect', 'create_database', 'has_database', 'delete_database', 'databases',
                         'show_database', 'get', 'insert', 'insert_many', 'update', 'update_many', 'delete', 'find',
                         'grant', 'revoke', 'new_user', 'set_user', 'delete_user', 'add_index', 'add_index',
                         'call', 'build', 'execute', 'link', 'detach')


# endregion


# region functions
def api(**methods):
    """Decorator function to transform standard classes into API compliant classes

    :param methods: method names that you want to bind to the methods of API compliant classes
    :return: class
    """

    def wrapped(cls):
        """Wrap function to decorate standard class

        :param cls: standard class you want to decorate
        :return: class
        """
        for name, api_name in methods.items():
            # Check if name is a compliant methods
            if api_name not in API_COMPLIANT_METHODS:
                raise ValueError(f'{api_name} methods is not in API compliant methods')
            if name in dir(cls):
                setattr(cls, api_name, getattr(cls, name))
        return cls

    return wrapped


# endregion


# region classes
class Manager:

    def __init__(self, connection, *args, **kwargs):
        # Check if connection is a compliant API connection object
        if not hasattr(connection, 'connect'):
            raise ConnectError('connection is not a valid connection object')
        self.connection = connection
        self.session = self.connection.connect(*args, **kwargs)
        # Set session properties
        self._database = self.session.database
        self._acl = self.session.acl
        self._item_count = self.session.item_count
        self._description = self.session.description
        self._indexes = self.session.indexes

    @property
    def item_count(self):
        return self._item_count

    @property
    def database(self):
        return self._database

    @property
    def acl(self):
        return self._acl

    @property
    def description(self):
        return self._description

    @property
    def indexes(self):
        return self._indexes

# endregion
