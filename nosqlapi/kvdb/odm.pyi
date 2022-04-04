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

from typing import Iterator, Any, Union


class Transaction:
    commands: list

    def __init__(self, commands: list = None) -> None:
        self._commands: list = commands

    def add(self, command: str, index: int = -1) -> None: ...

    def delete(self, index=-1) -> None: ...

    def __getitem__(self, item: int) -> Any: ...

    def __setitem__(self, key: int, value: Any) -> None: ...

    def __delitem__(self, key: int) -> None: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def __iter__(self) -> Iterator: ...


class Keyspace:
    name: str
    exists: bool
    store: list

    def __init__(self, name: str) -> None:
        self._name: str = name
        self._exists: bool = False
        self._store: list = []

    def append(self, item: Union[dict, Item]) -> None: ...

    def pop(self, item: int = -1) -> None: ...

    def __getitem__(self, item: int) -> Any: ...

    def __setitem__(self, key: int, value: Any) -> None: ...

    def __delitem__(self, key: int) -> None: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator: ...


class Subspace(Keyspace):

    def __init__(self, name: str, sub: str = None, sep: str = '.') -> None: ...


class Item:
    key: Union[str, int, float, tuple]
    value: Any

    def __init__(self, key: Union[str, int, float, tuple], value: Any = None) -> None:
        self._key: Union[str, int, float, tuple] = key
        self._value: Any = value
        self.__dict: dict = {}

    def get(self) -> dict: ...

    def set(self, key: Union[str, int, float, tuple], value: Any = None) -> None: ...

    def __getitem__(self, item: Union[str, int, float, tuple]) -> Any: ...

    def __setitem__(self, key: Union[str, int, float, tuple], value: Any) -> None: ...

    def __delitem__(self, key: Union[str, int, float, tuple]) -> None: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...


class ExpiredItem(Item):
    ttl: int

    def __init__(self, key: Union[str, int, float, tuple], value: Any = None, ttl: int = None) -> None:
        super().__init__(key, value)
        self._ttl: int = ttl

    def __setitem__(self, key: Union[str, int, float, tuple], value: Any) -> None: ...

    def __repr__(self) -> str: ...


Index: Any
