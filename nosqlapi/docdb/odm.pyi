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

from typing import Union, Any, Iterator, Callable

from nosqlapi.common.odm import Uuid
from nosqlapi.kvdb.odm import Keyspace


class Database(Keyspace): ...


class Collection:
    docs: list

    def __init__(self, name: str, *docs: Any) -> None:
        self.name: str = name
        self._docs: list = []

    def append(self, doc: Union[str, dict, Document]) -> None: ...

    def pop(self, doc: int = -1) -> None: ...

    def __getitem__(self, item: int) -> Union[str, dict, Document]: ...

    def __setitem__(self, key: int, value: Union[str, dict, Document]) -> None: ...

    def __delitem__(self, key: int) -> None: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator: ...


class Document:
    id: Union[str, Uuid]
    body: Any

    def __init__(self, value: Any = None, oid: Union[str, Uuid] = None, **values) -> None:
        self._body: dict = {}

    def to_json(self, indent: int = 2) -> str: ...

    def __getitem__(self, item: str) -> Any: ...

    def __setitem__(self, key: str, value: Any) -> None: ...

    def __delitem__(self, key: str) -> None: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator: ...


class Index:

    def __init__(self, name: str, data: dict) -> None:
        self.name: str = name
        self.data: dict = {}
        self.data.update(data)

    def __getitem__(self, item: str): ...

    def __setitem__(self, key: str, value: Any) -> None: ...

    def __delitem__(self, key: str) -> None: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...


def document(func: Callable) -> Document: ...
