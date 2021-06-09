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


class Session(ABC):
    """Server session abstract class"""

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

# endregion