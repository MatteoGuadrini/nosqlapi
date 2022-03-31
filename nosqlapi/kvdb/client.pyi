#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# client stub -- nosqlapi
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

from typing import Any, Union

from ..common.core import Connection, Selector, Session, Response, Batch


class KVConnection(Connection):

    def __init__(self, *args, **kwargs) -> None:
        self._return_data: Union[str, tuple, Response] = None


class KVSelector(Selector):

    def __init__(self, *args, **kwargs) -> None: ...

    def first_greater_or_equal(self, key: Any) -> Union[str, list, tuple]: ...

    def first_greater_than(self, key: Any) -> Union[str, list, tuple]: ...

    def last_less_or_equal(self, key: Any) -> Union[str, list, tuple]: ...

    def last_less_than(self, key: Any) -> Union[str, list, tuple]: ...

    def __str__(self) -> str: ...


class KVSession(Session):

    def copy(self, *args, **kwargs) -> Union[bool, Response]: ...


class KVResponse(Response): ...


class KVBatch(Batch): ...
