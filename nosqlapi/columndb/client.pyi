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

from ..common.core import Selector, Session, Response, Batch
from ..kvdb.client import KVConnection


class ColumnConnection(KVConnection): ...


class ColumnSelector(Selector):
    filtering: Any

    def __init__(self, *args, **kwargs):
        self._filtering: bool = False

    def all(self) -> Union[str, list, tuple]: ...

    def alias(self, *args, **kwargs) -> Union[str, list, tuple]: ...

    def cast(self, *args, **kwargs) -> Union[str, list, tuple]: ...

    def count(self) -> Union[str, list, tuple]: ...


class ColumnSession(Session):

    def create_table(self, *args, **kwargs) -> Union[bool, Response]: ...

    def delete_table(self, *args, **kwargs) -> Union[bool, Response]: ...

    def alter_table(self, *args, **kwargs) -> Union[bool, Response]: ...

    def compact(self, *args, **kwargs) -> Union[bool, Response]: ...

    def truncate(self, *args, **kwargs) -> Union[bool, Response]: ...


class ColumnResponse(Response): ...


class ColumnBatch(Batch): ...
