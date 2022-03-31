#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# client -- nosqlapi
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

"""Client module for column NOSQL database."""

# region imports
from abc import ABC, abstractmethod

from ..common.core import Connection, Selector, Session, Response, Batch

# endregion

# region global variable
__all__ = ['ColumnConnection', 'ColumnSelector', 'ColumnSession', 'ColumnResponse', 'ColumnBatch']


# endregion


# region classes
class ColumnConnection(Connection, ABC):

    """Column NOSQL database Connection class"""

    def __init__(self, *args, **kwargs):
        Connection.__init__(self, *args, **kwargs)


class ColumnSelector(Selector, ABC):

    """Column NOSQL database Selector class"""

    def __init__(self, *args, **kwargs):
        Selector.__init__(self, *args, **kwargs)
        self._filtering = False

    @abstractmethod
    def all(self):
        """Star selector: SELECT *"""
        pass

    @abstractmethod
    def alias(self, *args, **kwargs):
        """Aliases the selector: SELECT col1 AS person"""
        pass

    @abstractmethod
    def cast(self, *args, **kwargs):
        """Casts a selector to a type: SELECT CAST(a AS double)"""
        pass

    @abstractmethod
    def count(self):
        """Selects the count of all returned rows: SELECT count(*)"""
        pass

    @property
    def filtering(self):
        """Filter data"""
        return self._filtering

    @filtering.setter
    def filtering(self, value):
        """Set filtering data

        :param value: Boolean value
        :return: None
        """
        value_ = bool(value)
        if not isinstance(value_, bool):
            raise ValueError(f'{value_} must be bool')
        self._filtering = value_


class ColumnSession(Session, ABC):

    """Column NOSQL database Session class"""

    @abstractmethod
    def create_table(self, *args, **kwargs):
        """Create table on database"""

        pass

    @abstractmethod
    def delete_table(self, *args, **kwargs):
        """Create table on database"""

        pass

    @abstractmethod
    def alter_table(self, *args, **kwargs):
        """Alter table or rename"""

        pass

    @abstractmethod
    def compact(self, *args, **kwargs):
        """Compact table or database"""

        pass

    @abstractmethod
    def truncate(self, *args, **kwargs):
        """Delete all data into a table"""

        pass


class ColumnResponse(Response, ABC):

    """Column NOSQL database Response class"""

    pass


class ColumnBatch(Batch, ABC):

    """Column NOSQL database Batch class"""

    pass
# endregion
