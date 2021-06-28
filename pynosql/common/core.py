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
    def create_database(self):
        """Create new database on server

        :return: None
        """
        pass

    @abstractmethod
    def has_database(self):
        """Check if database exists on server

        :return: bool
        """
        pass

    @abstractmethod
    def delete_database(self):
        """Delete database on server

        :return: None
        """
        pass

    @abstractmethod
    def databases(self):
        """Get all databases

        :return: list
        """
        pass


class Selector(ABC):
    """Selector class"""

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
    def item_count(self):
        return self._item_count

    @property
    def description(self):
        return self._description

    @abstractmethod
    def get(self):
        """Get one or more value

        :return: dict
        """
        pass

    @abstractmethod
    def insert(self):
        """Insert one value

        :return: None
        """
        pass

    @abstractmethod
    def insert_many(self):
        """Insert one or more value

        :return: None
        """
        pass

    @abstractmethod
    def update(self):
        """Update one value

        :return: None
        """
        pass

    @abstractmethod
    def update_many(self):
        """Update one or more value

        :return: None
        """
        pass

    @abstractmethod
    def delete(self):
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
    def find(self, selector: Selector):
        """Find data

        :return: Any
        """
        pass


class Response(ABC):

    def __init__(self, data, code, header):
        self._data = data
        self._code = code
        self._header = header

    @property
    def data(self):
        return self._data

    @property
    def code(self):
        return self._code

    @property
    def header(self):
        return self._header


# endregion
