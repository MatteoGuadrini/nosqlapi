#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# client stub -- nosqlapi
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

from ..common.core import Connection, Session, Selector, Response, Batch
from typing import Any, Union

class DocConnection(Connection):

    def __init__(self, host: str = None, port: int = None, username: str = None,
                 password: str = None, ssl: bool = None, tls: bool = None, cert: str = None,
                 ca_cert: str = None, ca_bundle: str = None) -> None:
        self.host: str = host
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.ssl: bool = ssl
        self.tls: bool = tls
        self.cert: str = cert
        self.ca_cert: str = ca_cert
        self.ca_bundle: str = ca_bundle
        self.connection: Any = None
        self._return_data: Union[str, tuple, Response] = None


class DocSession(Session): ...


class DocSelector(Selector): ...


class DocResponse(Response): ...


class DocBatch(Batch): ...

