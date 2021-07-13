#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# client -- pynosql
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

"""Client module for column NOSQL database."""
from abc import ABC, abstractmethod
from ..common.core import Selector, Session, Response
from ..kvdb.client import KVConnection


class ColumnConnection(KVConnection, ABC):
    """Column NOSQL database Connection class"""

    pass


class ColumnSelector(Selector, ABC):
    """Column NOSQL database Selector class"""

    def __init__(self):
        super().__init__()
        self._filtering = False

    @abstractmethod
    def add(self, selector):
        """More selector: SELECT col1 + col2..."""
        pass

    @abstractmethod
    def all(self):
        """Star selector: SELECT *..."""
        pass

    @abstractmethod
    def alias(self, alias):
        """Aliases the selector: SELECT count(*) AS total"""
        pass

    @abstractmethod
    def cast(self, selector, target_type):
        """Casts a selector to a type: SELECT CAST(a AS double)"""
        pass

    @abstractmethod
    def count(self):
        """Selects the count of all returned rows: SELECT count(*)"""
        pass

    @property
    def filtering(self):
        return self._filtering

    @filtering.setter
    def filtering(self, value: bool):
        value_ = bool(value)
        if not isinstance(value_, bool):
            raise ValueError(f'{value_} must be bool')
        self._filtering = value_


class ColumnSession(Session, ABC):
    """Column NOSQL database Session class"""

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute some statement

        :return: Response
        """
        pass


class ColumnResponse(Response, ABC):
    """Column NOSQL database Response class"""

    pass