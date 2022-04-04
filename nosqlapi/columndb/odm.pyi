#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# odm stub -- nosqlapi
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

from typing import Any, Union, List, Iterator, Callable

from nosqlapi.kvdb.odm import Keyspace as Ks


class Keyspace(Ks): ...


class Table:
    name: str
    columns: List[Column]
    options: dict
    index: list
    header: tuple
    primary_key: str

    def __init__(self, name: str, *columns: Column, **options: Any) -> None:
        self._name: str = name
        self._columns: List[Column] = [col for col in columns]
        self._options: dict = options
        self._index: list = []

    def add_column(self, *columns: Column) -> None: ...

    def delete_column(self, index: int = -1) -> None: ...

    def set_option(self, option: dict) -> None: ...

    def add_row(self, *rows: Union[list, tuple, set]) -> None: ...

    def delete_row(self, row: int = -1) -> None: ...

    def get_rows(self) -> List[tuple]: ...

    def add_index(self, index) -> None: ...

    def delete_index(self, index: int = -1) -> None: ...

    def __getitem__(self, item: int) -> Column: ...

    def __setitem__(self, key: int, value: Column) -> None: ...

    def __delitem__(self, key: int = -1) -> None: ...

    def __iter__(self) -> Iterator: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...


class Column:
    of_type: Any
    data: list
    auto_increment: Any
    primary_key: Any
    default: Callable

    def __init__(self, name: str,
                 data: Union[list, tuple] = None,
                 of_type: Any = None,
                 max_len: int = None,
                 auto_increment: bool = False,
                 primary_key: bool = False,
                 default: Callable = None) -> None:
        self.name: str = name
        self._of_type: Any = of_type
        self.max_len: int = max_len
        self._data: list = []
        self._default = default
        self._primary_key = primary_key
        self._auto_increment: bool = auto_increment

    def append(self, data: Any = None): ...

    def pop(self, index: int = -1): ...

    def __getitem__(self, item: int): ...

    def __setitem__(self, key: int, value: Any): ...

    def __delitem__(self, key: int = -1):  ...

    def __iter__(self) -> Iterator: ...

    def __len__(self) -> int: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...


Index: Any

def column(func: Callable) -> Column: ...
