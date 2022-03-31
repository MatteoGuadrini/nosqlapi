#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# core stub -- nosqlapi
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


class Batch:
    session: Session
    batch: Any

    def __init__(self, batch: Any, session: Any = None) -> None:
        self._session: Session = session
        self._batch: Union[tuple, list, dict, set] = batch

    def execute(self, *args, **kwargs) -> Union[tuple, Response]: ...

    def __getitem__(self, item: Any) -> Any: ...

    def __setitem__(self, key: Union[tuple, int, float, str], value: Any) -> None: ...

    def __delitem__(self, key: Union[tuple, int, float, str]) -> None: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def __bool__(self) -> bool: ...


class Connection:
    connected: bool

    def __init__(self,
                 host: str = None,
                 user: str = None,
                 password: str = None,
                 database: str = None,
                 port: int = None,
                 bind_address: str = None,
                 read_timeout: int = None,
                 write_timeout: int = None,
                 ssl: bool = None,
                 ssl_ca: str = None,
                 ssl_cert: str = None,
                 tls: bool = None,
                 ssl_key: str = None,
                 ssl_verify_cert: bool = None,
                 max_allowed_packet: int = None) -> None:
        self.host: str
        self.user: str
        self.password: str
        self.database: str
        self.port: int
        self.bind_address: str
        self.read_timeout: int
        self.write_timeout: int
        self.ssl: bool
        self.ssl_ca: str
        self.ssl_cert: str
        self.tls: bool
        self.ssl_key: str
        self.ssl_verify_cert: bool
        self.max_allowed_packet: int
        self._connected: bool = False

    def close(self, *args, **kwargs) -> None: ...

    def connect(self, *args, **kwargs) -> Session: ...

    def create_database(self, *args, **kwargs) -> Union[bool, Response]: ...

    def has_database(self, *args, **kwargs) -> Union[bool, Response]: ...

    def delete_database(self, *args, **kwargs) -> Union[bool, Response]: ...

    def databases(self, *args, **kwargs) -> Union[tuple, list, Response]: ...

    def show_database(self, *args, **kwargs) -> Union[tuple, Response]: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def __bool__(self) -> bool: ...

    def __enter__(self): ...

    def __exit__(self, exc_type, exc_val, exc_tb): ...


class Selector:
    selector: Union[tuple, list, str]
    fields: Union[tuple, list, str]
    partition: str
    condition: Union[tuple, list, str]
    order: int
    limit: int

    def __init__(self, selector: Union[list, str] = None, fields: list = None, partition: str = None,
                 condition: Union[list, str] = None, order: int = None, limit: int = None): ...

    def build(self, *args, **kwargs) -> str: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def __bool__(self) -> bool: ...


class Session:
    item_count: int
    description: Union[tuple, dict]
    database: Union[str, None]
    connection: Any
    acl: Union[tuple, dict, Response]
    indexes: Union[tuple, dict, Response]

    def __init__(self, connection: Any, database: str = None) -> None:
        self._item_count: int = 0
        self._description: tuple = ()
        self._database: str = database

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

    @staticmethod
    def call(batch: Batch, *args, **kwargs) -> Union[tuple, Response]: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def __bool__(self) -> bool: ...

    def __enter__(self) -> None: ...

    def __exit__(self, exc_type: type, exc_val: str, exc_tb: str) -> None: ...


class Response:
    data: Any
    code: int
    header: Union[str, tuple]
    error: Union[str, Exception]
    dict: dict

    def __init__(self, data: Any, code: int = None, header: Union[str, tuple] = None,
                 error: Union[str, Exception] = None) -> None:
        self._data: Any = data
        self._code: int = code
        self._header: Union[str, tuple] = header
        self._error: Union[str, Exception] = error

    def __bool__(self) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __len__(self) -> int: ...

    def __contains__(self, item) -> bool: ...

    def __getitem__(self, item) -> Any: ...
