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

"""Client module for graph NOSQL database."""

# region imports
from abc import ABC, abstractmethod

from ..common.core import Connection, Session, Selector, Response, Batch

# endregion

# region global variable
__all__ = ['GraphConnection', 'GraphSelector', 'GraphSession', 'GraphResponse', 'GraphBatch']


# endregion

# region classes

class GraphConnection(Connection, ABC):

    """Graph NOSQL database Connection class"""

    def __init__(self, *args, **kwargs):
        Connection.__init__(self, *args, **kwargs)


class GraphSession(Session, ABC):

    """Graph NOSQL database Session class"""

    @abstractmethod
    def link(self, *args, **kwargs):
        """Link node to another

        :return: Response
        """
        pass

    @abstractmethod
    def detach(self, *args, **kwargs):
        """Detach node

        :return: Response
        """
        pass


class GraphSelector(Selector, ABC):

    """Graph NOSQL database Selector class"""

    def __init__(self, *args, **kwargs):
        Selector.__init__(self, *args, **kwargs)


class GraphResponse(Response, ABC):

    """Response NOSQL database Session class"""

    pass


class GraphBatch(Batch, ABC):

    """Batch NOSQL database Session class"""

    pass

# endregion
