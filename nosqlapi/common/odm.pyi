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

from datetime import date, timedelta, time, datetime
from decimal import Decimal as Dc
from typing import Union, Any
from uuid import uuid1, UUID


class Null:

    def __repr__(self) -> str: ...


class List(list):
    pass


class Map(dict):
    pass


class Ascii(str):

    def __repr__(self) -> str: ...


class Blob(bytes):
    pass


class Boolean:

    def __init__(self, value: bool) -> None:
        self.value: bool = value

    def __repr__(self) -> str: ...

    def __bool__(self) -> str: ...


class Counter:

    def __init__(self, value: int = 0) -> None:
        self.value: int = int(value)

    def increment(self, value: int = 1) -> None: ...

    def decrement(self, value: int = 1) -> None: ...

    def __add__(self, other: int) -> None: ...

    def __sub__(self, other: int) -> None: ...

    def __repr__(self) -> str: ...


class Date(date):

    def __repr__(self) -> str: ...


class Decimal(Dc):
    pass


class Double(float):
    pass


class Duration(timedelta):

    def string_format(self) -> str: ...

    def __repr__(self) -> str: ...


class Float(float):
    pass


class Inet:

    def __init__(self, ip: str) -> None:
        self.ip: str = ip

    def __repr__(self) -> str: ...


class Int(int):

    def __init__(self, number: int) -> None:
        self.number: int = number

    def __repr__(self) -> str: ...


class SmallInt(Int):

    def __init__(self, number: int) -> None: ...


class Text(str):
    pass


class Time(time):

    def __repr__(self) -> str: ...


class Timestamp(datetime):

    def __repr__(self) -> str: ...


class Uuid:

    def __init__(self) -> None:
        self.uuid: Union[str, UUID] = uuid1()

    def __repr__(self) -> str: ...


Varchar: Any
Varint: Any
Array: Any
