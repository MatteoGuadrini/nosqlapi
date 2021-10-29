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
from nosqlapi.common.exception import ConnectError

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
        self._item_count = self.session.item_count
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

    def get(self, *args, **kwargs):
        """Get one or more value

        :return: Union[tuple, Response]
        """
        return self.session.get(*args, **kwargs)

    def insert(self, *args, **kwargs):
        """Insert one value

        :return: Union[bool, Response]
        """
        return self.session.insert(*args, **kwargs)

    def insert_many(self, *args, **kwargs):
        """Insert one or more value

        :return: Union[bool, Response]
        """
        return self.session.insert_many(*args, **kwargs)

    def update(self, *args, **kwargs):
        """Update one value

        :return: Union[bool, Response]
        """
        return self.session.update(*args, **kwargs)

    def update_many(self, *args, **kwargs):
        """Update one or more value

        :return: Union[bool, Response]
        """
        return self.session.update_many(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete one value

        :return: Union[bool, Response]
        """
        return self.session.delete(*args, **kwargs)

    def close(self, *args, **kwargs):
        """Close session

        :return: None
        """
        self.session.close(*args, **kwargs)

    def find(self, *args, **kwargs):
        """Find data

        :return: Union[tuple, Response]
        """
        return self.session.find(*args, **kwargs)

    def grant(self, *args, **kwargs):
        """Grant users ACLs

        :return: Union[Any, Response]
        """
        return self.session.grant(*args, **kwargs)

    def revoke(self, *args, **kwargs):
        """Revoke users ACLs

        :return: Union[Any, Response]
        """
        return self.session.revoke(*args, **kwargs)

    def new_user(self, *args, **kwargs):
        """Create new user

        :return: Union[bool, Response]
        """
        return self.session.new_user(*args, **kwargs)

    def set_user(self, *args, **kwargs):
        """Modify exist user

        :return: Union[bool, Response]
        """
        return self.session.set_user(*args, **kwargs)

    def delete_user(self, *args, **kwargs):
        """Delete exist user

        :return: Union[bool, Response]
        """
        return self.session.delete_user(*args, **kwargs)

    def add_index(self, *args, **kwargs):
        """Add index to database

        :return: Union[bool, Response]
        """
        return self.session.add_index(*args, **kwargs)

    def delete_index(self, *args, **kwargs):
        """Delete index to database

        :return: Union[bool, Response]
        """
        return self.session.delete_index(*args, **kwargs)

    def call(self, *args, **kwargs):
        """Call a batch

        :return: Union[Any, Response]
        """
        return self.session.call(self.session, *args, **kwargs)

    def change(self, connection, *args, **kwargs):
        """Change connection type

        :param connection: Connection object
        :param args: positional args of Connection object
        :param kwargs: keywords args of Connection object
        :return: None
        """
        if not hasattr(connection, 'connect'):
            raise ConnectError(f'{connection} is not a valid Connection object')
        self.connection = connection
        self.session = self.connection.connect(*args, **kwargs)

    def __repr__(self):
        return f'<{self.__class__.__name__} object, connection={self.connection}>'

    def __str__(self):
        return str(self.session)

    def __bool__(self):
        if self.session:
            return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# endregion
