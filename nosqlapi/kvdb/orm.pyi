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

from typing import Iterator, Any

class Transaction:

    commands: list

    def __init__(self, commands: list = None) -> None:
        self._commands: list = commands

    def add(self, command: str, index: int = -1) -> None: ...

    def delete(self, index=-1) -> None: ...

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

    def append(self, item: Any) -> None: ...

    def pop(self, item: int = -1) -> None: ...

    def __getitem__(self, item: int) -> None: ...

    def __setitem__(self, key: int, value: Any) -> None: ...

    def __delitem__(self, key: int) -> None: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator: ...
