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

# region Imports
from nosqlapi.kvdb.orm import Keyspace as Ks
from decimal import Decimal as Dc
from datetime import date
from datetime import timedelta
from datetime import time
from datetime import datetime
from uuid import uuid1


# endregion

# region Classes
class Ascii(str):
    pass


class Blob(bytes):
    pass


class Boolean:

    def __init__(self, value):
        self.value = bool(value)

    def __repr__(self):
        return self.value.__repr__()

    def __bool__(self):
        return self.value


class Counter:

    def __init__(self, value=0):
        self.value = int(value)

    def increment(self, value=1):
        self.value += value

    def decrement(self, value=1):
        self.value -= value

    def __add__(self, other):
        self.increment(other)

    def __sub__(self, other):
        self.decrement(other)

    def __repr__(self):
        return self.value.__repr__()


class Date(date):

    def __repr__(self):
        return self.strftime('%Y-%m-%d')


class Decimal(Dc):
    pass


class Double(float):
    pass


class Duration(timedelta):

    def string_format(self):
        hours, minutes = self.seconds // 3600, self.seconds // 60 % 60
        seconds = self.seconds - (hours * 3600 + minutes * 60)
        return f'{self.days}d{hours}h{minutes}m{seconds}s'

    def __repr__(self):
        return self.string_format()


class Float(float):
    pass


class Inet:

    def __init__(self, ip):
        self.ip = ip

    def __repr__(self):
        return self.ip


class Int(int):

    def __init__(self, number):
        self.number = number

    def __repr__(self):
        return str(self.number)


class SmallInt(Int):

    def __init__(self, number):
        if number > 32767 or number < -32767:
            raise ValueError('the number must be between 32767 and -32767')
        super().__init__(number)


class Text(str):
    pass


class Time(time):

    def __repr__(self):
        return self.strftime('%H:%M:%S')


class Timestamp(datetime):

    def __repr__(self):
        return self.timestamp().__repr__()


class Uuid:

    def __init__(self):
        self.uuid = uuid1()

    def __repr__(self):
        return self.uuid.__str__()


Keyspace = Ks


class Table:

    def __init__(self, name, *columns, **options):
        self._name = name
        self._columns = [column for column in columns]
        self._options = options

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def columns(self):
        return self._columns

    @property
    def options(self):
        return self._options

    def add_column(self, column):
        self._columns.append(column)

    def delete_column(self, index=-1):
        del self[index]

    def set_option(self, option):
        self._options.update(option)

    def get_rows(self):
        return [tuple([col[i] for col in self.columns])
                for i in range(len(self.columns))]

    def __getitem__(self, item):
        return self._columns[item]

    def __setitem__(self, key, value):
        self._columns[key] = value

    def __delitem__(self, key=-1):
        self._columns.pop(key)

    def __repr__(self):
        return f'{self.__class__.__name__} object, name={self.name}>'

    def __str__(self):
        return f'{self.columns}'


class Column:

    def __init__(self, name, of_type=None, max_len=None):
        self.name = name
        self._of_type = of_type
        self.max_len = max_len
        self._data = []
        self._auto_increment = False

    @property
    def of_type(self):
        return self._of_type

    @property
    def data(self):
        return self._data

    @property
    def auto_increment(self):
        return self._auto_increment

    @auto_increment.setter
    def auto_increment(self, value: bool):
        if value is not bool:
            raise TypeError('auto_increment must be a bool value')
        self._auto_increment = value

    def append(self, data=None):
        if self.max_len and len(self._data) >= self.max_len:
            raise IndexError(f'maximum number of satisfied data: {self.max_len}')
        if data is not self.of_type and self.of_type is not None:
            raise TypeError(f'the data must be of the type {self.of_type}')
        if self.auto_increment:
            if isinstance(self.of_type, (int, float)):
                try:
                    last = self.data[-1]
                    self._data.append(last + 1)
                except IndexError:
                    self._data.append(1)
        else:
            self._data.append(data)

    def pop(self, index=-1):
        self._data.pop(index)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key=-1):
        self.pop(key)

    def __repr__(self):
        return f'{self.__class__.__name__} object, name={self.name} type={self.of_type.__class__.__name__}>'

    def __str__(self):
        return f'{self.data}'

# endregion
