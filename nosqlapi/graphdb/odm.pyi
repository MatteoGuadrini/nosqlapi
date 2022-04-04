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


from typing import Any, Union, Callable

from nosqlapi.kvdb.odm import Keyspace
from ..common.odm import Text


class Label(Text): ...


class Property(dict):

    def __repr__(self) -> None: ...


class RelationshipType(Label): ...


class Database(Keyspace):
    online: bool

    def __init__(self, name: str, address: str = None, role: str = None,
                 status: str = None, default: bool = False) -> None:
        self.address: str = address
        self.role: str = role
        self.status: str = status
        self.default: bool = default


class Node:

    def __init__(self, labels: list, properties: Union[dict, Property] = None, var: str = '') -> None:
        self.labels: list = []
        self.properties: Union[dict, Property] = Property()
        self.var: str = var

    def add_label(self, label: Union[str, Label]) -> None: ...

    def delete_label(self, index: int = -1) -> None: ...

    def __getitem__(self, item: str) -> Any: ...

    def __setitem__(self, key: str, value: Any) -> None: ...

    def __delitem__(self, key: str) -> None: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...


class Relationship(Node):

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...


Index: Any

def prop(func: Callable) -> Property: ...

def node(func: Callable) -> Node: ...
