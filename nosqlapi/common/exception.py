#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# exception -- nosqlapi
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


"""Exception module.

This module contains the hierarchy of exceptions included in the NOSQL API."""

# region global variable
__all__ = ['Error', 'UnknownError', 'ConnectError', 'CloseError', 'DatabaseError',
           'DatabaseCreationError', 'DatabaseDeletionError', 'SessionError',
           'SessionInsertingError', 'SessionUpdatingError', 'SessionClosingError',
           'SessionFindingError', 'SessionDeletingError', 'SessionACLError', 'SelectorError',
           'SelectorAttributeError']


# endregion

# Generic error
class Error(Exception):
    """Error that is the base class of all other error exceptions.
    You can use this to catch all errors with one single except statement.
    """
    pass


class UnknownError(Error):
    """Exception raised when an unspecified error occurred."""
    pass


# Connection error
class ConnectError(Error):
    """Exception raised for errors that are related to the database connection."""
    pass


class CloseError(ConnectError):
    """Exception raised for errors that are related to the database close connection."""
    pass


# Database error
class DatabaseError(Error):
    """Exception raised for errors that are related to the database, generally."""
    pass


class DatabaseCreationError(DatabaseError):
    """Exception raised for errors that are related to the creation of a database."""
    pass


class DatabaseDeletionError(DatabaseError):
    """Exception raised for errors that are related to the deletion of a database."""
    pass


# Session error
class SessionError(Error):
    """Exception raised for errors that are related to the session, generally."""
    pass


class SessionInsertingError(SessionError):
    """Exception raised for errors that are related to the inserting data on a database session."""
    pass


class SessionUpdatingError(SessionError):
    """Exception raised for errors that are related to the updating data on a database session."""
    pass


class SessionDeletingError(SessionError):
    """Exception raised for errors that are related to the deletion data on a database session."""
    pass


class SessionClosingError(SessionError):
    """Exception raised for errors that are related to the closing database session."""
    pass


class SessionFindingError(SessionError):
    """Exception raised for errors that are related to the finding data on a database session."""
    pass


class SessionACLError(SessionError):
    """Exception raised for errors that are related to the grant or revoke permission on a database."""
    pass


# Other error
class SelectorError(Error):
    """Exception raised for errors that are related to the selectors in general."""
    pass


class SelectorAttributeError(SelectorError):
    """Exception raised for errors that are related to the selectors attribute."""
    pass
