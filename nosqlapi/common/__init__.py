#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# __init__.py -- nosqlapi
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

"""Common interface classes for NOSQL database type."""

from nosqlapi.common.core import Batch, Session, Response, Selector, Connection
from nosqlapi.common.exception import (Error, UnknownError, ConnectError, CloseError, DatabaseError,
                                       DatabaseCreationError, DatabaseDeletionError, SessionError,
                                       SessionInsertingError, SessionUpdatingError, SessionClosingError,
                                       SessionFindingError, SessionDeletingError, SessionACLError, SelectorError,
                                       SelectorAttributeError)
from nosqlapi.common.odm import (Null, List, Map, Int, Inet, Ascii, Time, SmallInt, Decimal, Timestamp, Counter,
                                 Date, Text, Blob, Boolean, Double, Uuid, Duration, Float, Varint, Varchar, Array)
from nosqlapi.common.utils import api, Manager, global_session, cursor_response, apply_vendor, response
