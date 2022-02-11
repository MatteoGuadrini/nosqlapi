#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# client -- nosqlapi
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

"""Client module for document NOSQL database."""

# region imports
from abc import ABC, abstractmethod

from ..common.core import Connection, Session, Selector, Response, Batch

# endregion

# region global variable
__all__ = ['DocConnection', 'DocSelector', 'DocSession', 'DocResponse', 'DocBatch']


# endregion

# region classes
class DocConnection(Connection, ABC):

    """Document NOSQL database Connection class"""

    def __init__(self, *args, **kwargs):
        Connection.__init__(self, *args, **kwargs)

    @abstractmethod
    def copy_database(self, *args, **kwargs):
        """Copy database

        :return : Union[Any, Response]
        """
        pass


class DocSession(Session, ABC):

    """Document NOSQL database Session class"""

    @abstractmethod
    def compact(self, *args, **kwargs):
        """Compact data or database"""

        pass


class DocSelector(Selector, ABC):

    """Document NOSQL database Selector class"""

    pass


class DocResponse(Response, ABC):

    """Document NOSQL database Response class"""

    pass


class DocBatch(Batch, ABC):

    """Document NOSQL database Batch class"""

    pass

# endregion
