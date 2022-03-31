#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteo.guadrini
# core -- nosqlapi
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

"""Module that contains the core objects."""

# region imports
from abc import ABC, abstractmethod

from .exception import *

# endregion

# region global variable
API_NAME = 'nosqlapi'
__all__ = ['Connection', 'Selector', 'Session', 'Response', 'Batch']


# endregion

# region classes
class Connection(ABC):

    """Server connection abstract class

    The abstract class :class:`Connection` is used to create connection-type classes that will allow you to work
    directly on the layer at the database level.
    """

    def __init__(self,
                 host=None,
                 user=None,
                 password=None,
                 database=None,
                 port=None,
                 bind_address=None,
                 read_timeout=None,
                 write_timeout=None,
                 ssl=None,
                 ssl_ca=None,
                 ssl_cert=None,
                 tls=None,
                 ssl_key=None,
                 ssl_verify_cert=None,
                 max_allowed_packet=None
                 ):
        """Instantiate Connection object

        :param host: Name of host that contains database
        :param user: Username for connect to the host
        :param password: Password for connect to the host
        :param database: Name of database
        :param port: Tcp port
        :param bind_address: Hostname or an IP address for multiple network interfaces
        :param read_timeout: Timeout for reading from the connection in seconds
        :param write_timeout: Timeout for writing from the connection in seconds
        :param ssl: Ssl connection established
        :param ssl_ca: Ssl CA file specified
        :param ssl_cert: Ssl certificate file specified
        :param tls: Tls connection established
        :param ssl_key: Ssl private key file specified
        :param ssl_verify_cert: Verify certificate file
        :param max_allowed_packet: Max size of packet sent to server in bytes
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.bind_address = bind_address
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.ssl = ssl
        self.ssl_ca = ssl_ca
        self.ssl_cert = ssl_cert
        self.tls = tls
        self.ssl_key = ssl_key
        self.ssl_verify_cert = ssl_verify_cert
        self.max_allowed_packet = max_allowed_packet
        self._connected = False

    @property
    def connected(self):
        """Boolean representing the database connection

        :return: bool
        """
        return bool(self._connected)

    @abstractmethod
    def close(self, *args, **kwargs):
        """Close connection

        :return: None
        """
        pass

    @abstractmethod
    def connect(self, *args, **kwargs):
        """Connect database server

        :return: Session object
        """
        pass

    @abstractmethod
    def create_database(self, *args, **kwargs):
        """Create new database on server

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def has_database(self, *args, **kwargs):
        """Check if database exists

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def delete_database(self, *args, **kwargs):
        """Delete database on server

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def databases(self, *args, **kwargs):
        """Get all databases

        :return: Union[tuple, list, Response]
        """
        pass

    @abstractmethod
    def show_database(self, *args, **kwargs):
        """Show a database information

        :return : Union[Any, Response]
        """
        pass

    def __repr__(self):
        return f"<{API_NAME} {self.__class__.__name__} object>"

    def __str__(self):
        return f"host={self.host}, database={self.database}, connected={self.connected}"

    def __bool__(self):
        return True if self.connected else False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Selector(ABC):

    """Selector abstract class

    The abstract class :class:`Selector` is used to create selector-type classes, which represent a query in the
    specific language of the database.
    """

    def __init__(self, selector=None, fields=None, partition=None, condition=None, order=None, limit=None):
        """Instantiate Selector object

        :param selector: Selector part of the query string
        :param fields: Return fields
        :param partition: Partition or collection of data
        :param condition: Condition of query
        :param order: Order by specific selector
        :param limit: Limit result
        """
        self.selector = selector
        self.fields = fields
        self.partition = partition
        self.condition = condition
        self.order = order
        self.limit = limit

    @property
    def selector(self):
        """Value than you want search"""
        return self._selector

    @selector.setter
    def selector(self, value):
        """Value than you want search"""
        self._selector = value

    @property
    def fields(self):
        """Key that returned from find operations"""
        return self._fields

    @fields.setter
    def fields(self, value):
        """Key that returned from find operations"""
        self._fields = value

    @property
    def partition(self):
        """The name of partition or collection in a database"""
        return self._partition

    @partition.setter
    def partition(self, value):
        """The name of partition or collection in a database"""
        self._partition = value

    @property
    def condition(self):
        """Other condition to apply a selectors"""
        return self._condition

    @condition.setter
    def condition(self, value):
        """Other condition to apply a selectors"""
        self._condition = value

    @property
    def order(self):
        """Order returned from find operations"""
        return self._order

    @order.setter
    def order(self, value):
        """Order returned from find operations"""
        self._order = value

    @property
    def limit(self):
        """Limit number of objects returned from find operations"""
        return self._limit

    @limit.setter
    def limit(self, value):
        """Limit number of objects returned from find operations"""
        self._limit = value

    @abstractmethod
    def build(self, *args, **kwargs):
        """Build string query selector

        :return: string
        """
        pass

    def __repr__(self):
        return f"<{API_NAME} {self.__class__.__name__} object>"

    def __str__(self):
        return self.build()

    def __bool__(self):
        if self.selector:
            return True


class Session(ABC):

    """Server session abstract class

    The abstract class :class:`Session` is used to create session-type classes that will allow you to work
    directly on the layer at the data level.
    """

    def __init__(self, connection, database=None):
        """Instantiate Session object

        :param connection: Connection object or other object to serve connection
        :param database: database name
        """
        self._item_count = 0
        self._description = ()
        self._database = database
        self._connection = connection

    @property
    def database(self):
        """Name of database in current session"""
        return self._database

    @property
    def connection(self):
        """Connection of server in current session"""
        return self._connection

    @property
    @abstractmethod
    def item_count(self):
        """Number of item returned from latest CRUD operation"""
        return self._item_count

    @property
    @abstractmethod
    def description(self):
        """Contains the session parameters"""
        return self._description

    @property
    @abstractmethod
    def acl(self):
        """Access Control List in the current session"""
        pass

    @property
    @abstractmethod
    def indexes(self):
        """Name of indexes of the current database"""
        pass

    @abstractmethod
    def get(self, *args, **kwargs):
        """Get one or more value

        :return: Union[tuple, Response]
        """
        pass

    @abstractmethod
    def insert(self, *args, **kwargs):
        """Insert one value

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def insert_many(self, *args, **kwargs):
        """Insert one or more value

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        """Update one value

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def update_many(self, *args, **kwargs):
        """Update one or more value

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        """Delete one value

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def close(self, *args, **kwargs):
        """Close session

        :return: None
        """
        pass

    @abstractmethod
    def find(self, *args, **kwargs):
        """Find data

        :return: Union[tuple, Response]
        """
        pass

    @abstractmethod
    def grant(self, *args, **kwargs):
        """Grant users ACLs

        :return: Union[Any, Response]
        """
        pass

    @abstractmethod
    def revoke(self, *args, **kwargs):
        """Revoke users ACLs

        :return: Union[Any, Response]
        """
        pass

    @abstractmethod
    def new_user(self, *args, **kwargs):
        """Create new user

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def set_user(self, *args, **kwargs):
        """Modify exist user

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def delete_user(self, *args, **kwargs):
        """Delete exist user

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def add_index(self, *args, **kwargs):
        """Add index to database

        :return: Union[bool, Response]
        """
        pass

    @abstractmethod
    def delete_index(self, *args, **kwargs):
        """Delete index to database

        :return: Union[bool, Response]
        """
        pass

    @staticmethod
    def call(batch, *args, **kwargs):
        """Call a batch

        :return: Union[Any, Response]
        """
        if not hasattr(batch, 'execute'):
            raise SessionError('batch object must implements an "execute" method.')
        return batch.execute(*args, **kwargs)

    def __repr__(self):
        return f"<{API_NAME} {self.__class__.__name__} object>"

    def __str__(self):
        return f"connection=({self.connection}), description={self.description}"

    def __bool__(self):
        if self.connection:
            return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Response(ABC):

    """Server response abstract class

    The abstract class :class:`Response` is used to create response-type classes that represent response data to
    an operation.
    """

    __slots__ = ('_data', '_code', '_header', '_error')

    def __init__(self, data, code=None, header=None, error=None):
        """Instantiate Response object

        :param data: Data from operation
        :param code: Exit code of operation
        :param header: Header of operation
        :param error: Error string or Exception class
        """
        self._data = data
        self._code = code
        self._header = header
        self._error = error

    @property
    def data(self):
        """The effective data than returned"""
        return self._data

    @property
    def code(self):
        """Number code of error or success in an operation"""
        return self._code

    @property
    def header(self):
        """Information (header) of an operation"""
        return self._header

    @property
    def error(self):
        """Error of an operation"""
        return self._error

    @property
    def dict(self):
        """dict format for Response object"""
        return {'data': self._data,
                'code': self._code,
                'header': self._header,
                'error': self._error}

    def throw(self):
        """Raise or throw exception from error property

        :return: Exception
        """
        if isinstance(self.error, Exception):
            raise self.error
        else:
            raise Error(self.error)

    def __bool__(self):
        if self._error:
            return False
        if self._data:
            return True

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"<{API_NAME} {self.__class__.__name__} object>"

    def __len__(self):
        return self.data.__len__()

    def __contains__(self, item):
        return True if item in self.data else False

    def __getitem__(self, item):
        return self.data[item]


class Batch(ABC):

    """Batch abstract class

    The abstract class :class:`Batch` is used to create batch-type classes that represent a collection of
    operations to be performed at the same time.
    """

    def __init__(self, batch, session=None):
        """Instantiate Batch object

        :param batch: List of commands
        :param session: Session object or other compliant object
        """
        self._session = session
        self._batch = batch

    @property
    def session(self):
        """Session object"""
        return self._session

    @session.setter
    def session(self, value):
        """Session object"""
        if not hasattr(value, 'call'):
            raise SessionError(f'{value} not contains a valid session')
        self._session = value

    @property
    def batch(self):
        """String batch operation"""
        return self._batch

    @batch.setter
    def batch(self, value):
        """String batch operation"""
        self._batch = value

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute some batch statement

        :return: Union[tuple, Response]
        """
        pass

    def __getitem__(self, item):
        return self._batch[item]

    def __setitem__(self, key, value):
        self._batch[key] = value

    def __delitem__(self, key):
        del self._batch[key]

    def __repr__(self):
        return f"<{API_NAME} {self.__class__.__name__} object>"

    def __str__(self):
        return str(self.batch)

    def __bool__(self):
        if self.batch:
            return True

# endregion
