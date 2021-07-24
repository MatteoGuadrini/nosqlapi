#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# exception -- nosqlapi
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

"""Exception module for NOSQL databases."""


# Generic error
class Error(Exception):
    pass


class UnknownError(Error):
    pass


# Connection error
class ConnectError(Error):
    pass


class CloseError(ConnectError):
    pass


# Database error
class DatabaseError(Error):
    pass


class DatabaseCreationError(DatabaseError):
    pass


class DatabaseDeletionError(DatabaseError):
    pass


# Session error
class SessionError(Error):
    pass


class SessionInsertingError(SessionError):
    pass


class SessionUpdatingError(SessionError):
    pass


class SessionDeletingError(SessionError):
    pass


class SessionClosingError(SessionError):
    pass


class SessionFindingError(SessionError):
    pass


class SessionACLError(SessionError):
    pass


# Other error
class SelectorError(Error):
    pass


class SelectorAttributeError(SelectorError):
    pass
