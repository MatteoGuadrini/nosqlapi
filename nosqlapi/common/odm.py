#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# odm -- nosqlapi
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

"""Module that contains some ODM common objects."""

# region Imports
import string
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta

from decimal import Decimal as Dc
from uuid import uuid1

# endregion

# region global variable
__all__ = ['Null', 'List', 'Map', 'Int', 'Inet', 'Ascii', 'Time', 'SmallInt', 'Decimal', 'Timestamp', 'Counter',
           'Date', 'Text', 'Blob', 'Boolean', 'Double', 'Uuid', 'Duration', 'Float', 'Varint', 'Varchar', 'Array']


# endregion

# region Classes
class Null:

    """Represents None"""

    def __repr__(self):
        return 'null'


class List(list):

    """Represents list of objects"""

    pass


class Map(dict):

    """Represents dict of objects"""

    pass


class Ascii(str):

    """Represents ASCII string"""

    def __init__(self, value=''):
        """ASCII string

        :param value: String printable characters
        """
        for char in value:
            if char not in string.printable:
                raise ValueError(f'The string "{value}" contains non-ASCII characters: {char}')


class Blob(bytes):

    """Represents bytes"""

    pass


class Boolean:

    """Represents bool"""

    def __init__(self, value):
        """Boolean object

        :param value: True of False
        """
        self.value = bool(value)

    def __repr__(self):
        return self.value.__repr__()

    def __bool__(self):
        return self.value


class Counter:

    """Represents integer counter"""

    def __init__(self, value=0):
        """Counter object

        :param value: Integer (default 0)
        """
        self.value = int(value)

    def increment(self, value=1):
        """Increment number

        :param value: Number (default 1)
        :return: None
        """
        self.value += value

    def decrement(self, value=1):
        """Decrement number

        :param value: Number (default 1)
        :return: None
        """
        self.value -= value

    def __add__(self, other):
        self.increment(other)

    def __sub__(self, other):
        self.decrement(other)

    def __repr__(self):
        return self.value.__repr__()


class Date(date):

    """Represents date in format %Y-%m-%d"""

    def __repr__(self):
        return self.strftime('%Y-%m-%d')


class Decimal(Dc):

    """Represents decimal number"""

    pass


class Double(float):

    """Represents float"""

    pass


class Duration(timedelta):

    """Represents duration ISO 8601 format: P[n]Y[n]M[n]DT[n]H[n]M[n]S"""

    def string_format(self):
        """ISO 8601 format: P[n]Y[n]M[n]DT[n]H[n]M[n]S

        :return: str
        """
        hours, minutes = self.seconds // 3600, self.seconds // 60 % 60
        seconds = self.seconds - (hours * 3600 + minutes * 60)
        return f'{self.days}d{hours}h{minutes}m{seconds}s'

    def __repr__(self):
        return self.string_format()


class Float(float):

    """Represents float"""

    pass


class Inet:

    """Represents ip address version 4 or 6 like string"""

    def __init__(self, ip):
        """Network ip address object

        :param ip: String ip value
        """
        self.ip = ip

    def __repr__(self):
        return self.ip


class Int(int):

    """Represents integer"""

    def __init__(self, number):
        """Integer object

        :param number: Integer
        """
        self.number = number

    def __repr__(self):
        return str(self.number)


class SmallInt(Int):

    """Represents small integer: -32767 to 32767"""

    def __init__(self, number):
        """Integer number from -32767 to 32767

        :param number: Integer
        """
        if number > 32767 or number < -32767:
            raise ValueError('the number must be between 32767 and -32767')
        super().__init__(number)


class Text(str):

    """Represents str"""

    pass


class Time(time):

    """Represents time"""

    def __repr__(self):
        return self.strftime('%H:%M:%S')


class Timestamp(datetime):

    """Represents datetime timestamp"""

    def __repr__(self):
        return self.timestamp().__repr__()


class Uuid:

    """Represents uuid version 1"""

    def __init__(self):
        """Uuid1 object"""
        self.uuid = uuid1()

    def __repr__(self):
        return self.uuid.__str__()


Varchar = Text
Varint = Int
Array = List

# endregion
