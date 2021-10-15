#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# orm -- nosqlapi
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

from nosqlapi.kvdb.orm import Keyspace as Ks
from typing import Any, Union, List, Iterator

class Keyspace(Ks): ...

class Table:

    name: str
    columns: List[str, Column]
    options: dict
    index: list


    def __init__(self, name: str, *columns: Union[str, Column], **options: Any) -> None:
        self._name: str = name
        self._columns: List[str, Column] = [column for column in columns]
        self._options: dict = options
        self._index: list = []

    def add_column(self, column: Union[str, Column]) -> None: ...

    def delete_column(self, index: int = -1) -> None: ...

    def set_option(self, option: dict) -> None: ...

    def get_rows(self) -> List[tuple]: ...

    def add_index(self, index) -> None: ...

    def delete_index(self, index: int = -1) -> None: ...

    def __getitem__(self, item: int) -> Union[str, Column]: ...

    def __setitem__(self, key: int, value: Any) -> None: ...

    def __delitem__(self, key:int = -1) -> None: ...

    def __iter__(self) -> Iterator: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...


class Column: ...

