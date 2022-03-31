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

"""Client module for key-value NOSQL database."""

# region imports
from abc import ABC, abstractmethod

from ..common.core import Connection, Selector, Session, Response, Batch

# endregion

# region global variable
__all__ = ['KVConnection', 'KVSelector', 'KVSession', 'KVResponse', 'KVBatch']


# endregion

# region classes
class KVConnection(Connection, ABC):

    """Key-value NOSQL database Connection class"""

    def __init__(self, *args, **kwargs):
        Connection.__init__(self, *args, **kwargs)


class KVSelector(Selector, ABC):

    """Key-value NOSQL database Selector class"""

    def __init__(self, *args, **kwargs):
        Selector.__init__(self, *args, **kwargs)

    @abstractmethod
    def first_greater_or_equal(self, key):
        """First greater or equal key by selector key

        :param key: key to search
        :return: Union[str, list, tuple]
        """
        pass

    @abstractmethod
    def first_greater_than(self, key):
        """First greater key by selector key

        :param key: key to search
        :return: Union[str, list, tuple]
        """
        pass

    @abstractmethod
    def last_less_or_equal(self, key):
        """Last less or equal key by selector key

        :param key: key to search
        :return: Union[str, list, tuple]
        """
        pass

    @abstractmethod
    def last_less_than(self, key):
        """Last less key by selector key

        :param key: key to search
        :return: Union[str, list, tuple]
        """
        pass

    def __str__(self):
        return f"selector: {self.selector}, fields: {self.fields}"


class KVSession(Session, ABC):

    """Key-value NOSQL database Session class"""

    @abstractmethod
    def copy(self, *args, **kwargs):
        """Copy key to other key

        :return: Union[bool, Response]
        """


class KVResponse(Response, ABC):

    """Key-value NOSQL database Response class"""

    pass


class KVBatch(Batch, ABC):

    """Key-value NOSQL database Batch class"""

    pass
# endregion
