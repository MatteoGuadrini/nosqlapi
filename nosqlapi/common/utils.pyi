#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# utils stub -- nosqlapi
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

from typing import Union, Any, List

from nosqlapi import Response, Batch, Connection


def api(**methods: str) -> type: ...


def global_session(connection: Any, *args, **kwargs) -> None: ...


def cursor_response(resp: Response) -> List[tuple]: ...


def apply_vendor(name: str) -> None: ...


def response(data: Any) -> Response: ...


class Manager:
    item_count: int
    description: tuple
    database: Union[str, None]
    acl: Union[tuple, dict, Response]
    indexes: Union[tuple, dict, Response]

    def __init__(self, connection: Connection, *args, **kwargs) -> None:
        self.connection = connection
        self.session = self.connection.connect(*args, **kwargs)
        # Set session properties
        self._database = self.session.database
        self._acl = self.session.acl
        self._item_count = self.session.item_count
        self._description = self.session.description
        self._indexes = self.session.indexes

    def create_database(self, *args, **kwargs) -> Union[bool, Response]: ...

    def has_database(self, *args, **kwargs) -> Union[bool, Response]: ...

    def delete_database(self, *args, **kwargs) -> Union[bool, Response]: ...

    def databases(self, *args, **kwargs) -> Union[tuple, list, Response]: ...

    def show_database(self, *args, **kwargs) -> Union[Any, Response]: ...

    def get(self, *args, **kwargs) -> Union[tuple, dict, Response]: ...

    def insert(self, *args, **kwargs) -> Union[bool, Response]: ...

    def insert_many(self, *args, **kwargs) -> Union[bool, Response]: ...

    def update(self, *args, **kwargs) -> Union[bool, Response]: ...

    def update_many(self, *args, **kwargs) -> Union[bool, Response]: ...

    def delete(self, *args, **kwargs) -> Union[bool, Response]: ...

    def close(self, *args, **kwargs) -> None: ...

    def find(self, *args, **kwargs) -> Union[tuple, dict, Response]: ...

    def grant(self, *args, **kwargs) -> Union[tuple, Response]: ...

    def revoke(self, *args, **kwargs) -> Union[tuple, Response]: ...

    def new_user(self, *args, **kwargs) -> Union[bool, Response]: ...

    def set_user(self, *args, **kwargs) -> Union[bool, Response]: ...

    def delete_user(self, *args, **kwargs) -> Union[bool, Response]: ...

    def add_index(self, *args, **kwargs) -> Union[bool, Response]: ...

    def delete_index(self, *args, **kwargs) -> Union[bool, Response]: ...

    def call(self, batch: Batch, *args, **kwargs) -> Union[tuple, Response]: ...

    def change(self, connection: Union[object, Connection], *args, **kwargs) -> None: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def __bool__(self) -> bool: ...

    def __enter__(self) -> object: ...

    def __exit__(self, exc_type: type, exc_val: str, exc_tb: str) -> None: ...

    def __del__(self) -> None: ...
