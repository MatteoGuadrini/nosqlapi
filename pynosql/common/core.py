#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# core -- pynosql
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

# region imports
from abc import ABC, abstractmethod
from .exception import *


# endregion

# region Classes
class Connection(ABC):
    """Server connection abstract class"""

    @abstractmethod
    def close(self):
        """Delete this object

        :return: None
        """
        pass

    @abstractmethod
    def connect(self):
        """Connect database server

        :return: Session object
        """
        pass

    @abstractmethod
    def create_database(self, *args, **kwargs):
        """Create new database on server

        :return: None
        """
        pass

    @abstractmethod
    def has_database(self, *args, **kwargs):
        """Check if database exists on server

        :return: bool
        """
        pass

    @abstractmethod
    def delete_database(self, *args, **kwargs):
        """Delete database on server

        :return: None
        """
        pass

    @abstractmethod
    def databases(self):
        """Get all databases

        :return: Response
        """
        pass


class Selector(ABC):
    """Selector abstract class"""

    def __init__(self):
        self._selector = dict()
        self._fields = None
        self._partition = None
        self._condition = None
        self._order = None
        self._limit = None

    @property
    def selector(self):
        return self._selector

    @selector.setter
    def selector(self, value):
        self._selector = value

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value: list):
        if isinstance(value, list):
            self._fields = value
        else:
            raise SelectorAttributeError('fields must be a list object')

    @property
    def partition(self):
        return self._partition

    @partition.setter
    def partition(self, value):
        self._partition = value

    @property
    def condition(self):
        return self._condition

    @condition.setter
    def condition(self, value):
        self._condition = value

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, value):
        self._order = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value

    @abstractmethod
    def build(self):
        """Build string query selector

        :return: string
        """
        pass


class Session(ABC):
    """Server session abstract class"""

    def __init__(self):
        self._item_count = 0
        self._description = ()

    @property
    @abstractmethod
    def item_count(self):
        return self._item_count

    @property
    @abstractmethod
    def description(self):
        return self._description

    @property
    @abstractmethod
    def acl(self):
        pass

    @abstractmethod
    def get(self, *args, **kwargs):
        """Get one or more value

        :return: Response
        """
        pass

    @abstractmethod
    def insert(self, *args, **kwargs):
        """Insert one value

        :return: None
        """
        pass

    @abstractmethod
    def insert_many(self, *args, **kwargs):
        """Insert one or more value

        :return: None
        """
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        """Update one value

        :return: None
        """
        pass

    @abstractmethod
    def update_many(self, *args, **kwargs):
        """Update one or more value

        :return: None
        """
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        """Delete one value

        :return: None
        """
        pass

    @abstractmethod
    def close(self):
        """Delete session

        :return: None
        """
        pass

    @abstractmethod
    def find(self, *args, **kwargs):
        """Find data

        :return: Response
        """
        pass

    @abstractmethod
    def grant(self, *args, **kwargs):
        """Grant users ACLs

        :return: Response
        """
        pass

    @abstractmethod
    def revoke(self, *args, **kwargs):
        """Revoke users ACLs

        :return: Response
        """
        pass


class Response(ABC):
    """Server response abstract class"""

    def __init__(self, data, code=None, header=None, error=None):
        self._data = data
        self._code = code
        self._header = header
        self._error = error

    @property
    def data(self):
        return self._data

    @property
    def code(self):
        return self._code

    @property
    def header(self):
        return self._header

    @property
    def error(self):
        return self._error

    def __bool__(self):
        if self.error:
            return False
        if self.data:
            return True

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f'<class {self.__class__.__name__}: data={type(self.data)}, code={self.code}, error={self.error}>'

    def __contains__(self, item):
        return True if item in self.data else False


class Batch(ABC):
    """Batch abstract class"""

    def __init__(self, session: Session, query):
        self.session = session
        self._query = query

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        if not isinstance(value, Session):
            raise SessionError(f'{value} not contains a valid session')
        self._session = value

# endregion
