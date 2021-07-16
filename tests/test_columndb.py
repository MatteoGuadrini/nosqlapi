import unittest
import pynosql.columndb
from pynosql import (ConnectError, DatabaseCreationError, DatabaseDeletionError, DatabaseError, SessionError,
                     SessionInsertingError)
from unittest import mock
from typing import List


# Below classes is a simple emulation of Cassandra like database


class MyDBConnection(pynosql.columndb.ColumnConnection):
    # Simulate socket.socket
    t = mock.Mock('AF_INET', 'SOCK_STREAM')
    t.connect = mock.MagicMock()
    t.send = mock.MagicMock()
    t.close = mock.MagicMock()

    def __bool__(self):
        if self.return_data:
            return True

    def close(self):
        self.connection.close()
        self.connection = None
        self.t.recv = mock.MagicMock(return_value='CLOSED')
        self._return_data = self.t.recv(2048)
        if self.return_data != 'CLOSED':
            raise ConnectError(f'Close connection error: {self.return_data}')

    def connect(self):
        # Connection
        self.t.connect(self.host, self.port)
        if self.database:
            self.t.send(f"CLIENT_CONNECT_WITH_DB={self.database}")
        else:
            self.t.send("CLIENT_CONNECT")
        # Check credential
        if self.username and self.password:
            self.t.send(f"\nCRED={self.username}:{self.password}")
        # while len(self.t.recv(2048)) > 0:
        self.t.recv = mock.MagicMock(return_value='OK_PACKET')
        self._return_data = self.t.recv(2048)
        if self.return_data != 'OK_PACKET':
            raise ConnectError(f'Server connection error: {self.return_data}')
        self.connection = self.t
        return MyDBSession(self.connection)

    def create_database(self, name):
        if self.connection:
            self.connection.send(f"CREATE_DB='{name}'")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_CREATED')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_CREATED':
                raise DatabaseCreationError(f'Database creation error: {self.return_data}')
        else:
            raise ConnectError(f"Server isn't connected")

    def has_database(self, name):
        if self.connection:
            self.connection.send(f"DB_EXISTS='{name}'")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_EXISTS')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_EXISTS':
                return False
            else:
                return True
        else:
            raise ConnectError(f"Server isn't connected")

    def delete_database(self, name):
        if self.connection:
            self.connection.send(f"DELETE_DB='{name}'")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_DELETED')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_DELETED':
                raise DatabaseDeletionError(f'Database deletion error: {self.return_data}')
        else:
            raise ConnectError(f"Server isn't connected")

    def databases(self):
        if self.connection:
            self.connection.send(f"GET_ALL_DBS")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='test_db db1 db2')
            self._return_data = self.t.recv(2048)
            if not self:
                raise DatabaseError(f'Request error: {self.return_data}')
            # return MyDBResponse(self.return_data.split())
        else:
            raise ConnectError(f"Server isn't connected")


class MyDBSession(pynosql.columndb.ColumnSession):

    def __init__(self, connection):
        super().__init__()
        self.session = connection
        self.session.send("SHOW_DESC")
        self.session.recv = mock.MagicMock(return_value="server=mycolumndb.local\nport=12345\ndatabase=test_db"
                                                        "\nusername=admin")
        self._description = {item.split('=')[0]: item.split('=')[1]
                             for item in self.session.recv(2048).split('\n')}

    @property
    def item_count(self):
        return self._item_count

    @property
    def description(self):
        return self._description

    @property
    def acl(self):
        if 'database' not in self.description:
            raise ConnectError('connect to a database before request some ACLs')
        self.session.send(f"GET_ACL={self.description.get('database')}")
        self.session.recv = mock.MagicMock(return_value=f"test,user_read;admin,admins;root,admins")
        return MyDBResponse(
            data={item.split(',')[0]: item.split(',')[1]
                  for item in self.session.recv(2048).split(';')}
        )

    def get(self, table, *columns):
        self.session.send(f"SELECT {','.join(col for col in columns)} FROM {table}")
        self.session.recv = mock.MagicMock(return_value="name,age\nname1,age1\nname2,age2")
        if self.session.recv != 'NOT_FOUND':
            out = [tuple(row.split(','))
                   for row in self.session.recv(2048).split('\n')]
            self._item_count = len(out)
            return MyDBResponse(out)
        else:
            raise SessionError(f'columns or table not found')

    def insert(self,
               table,
               columns: tuple,
               values: tuple,
               ttl=None,
               timestamp=None,
               not_exists: bool = False):
        if not isinstance(columns, tuple):
            columns = tuple(columns)
        if not isinstance(values, tuple):
            values = tuple(values)
        query = f"INSERT INTO {table} {columns} VALUES {values}"
        if ttl and isinstance(ttl, int):
            query += f'\nUSING TTL {ttl}'
        if timestamp and ttl and isinstance(timestamp, int):
            query += f' AND TIMESTAMP {timestamp}'
        if bool(not_exists):
            query += f'\nIF NOT EXISTS'
        query += ';'
        self.session.send(query)
        self.session.recv = mock.MagicMock(return_value="INSERT_OK")
        if self.session.recv(2048) != "INSERT_OK":
            raise SessionInsertingError(f'insert into {columns} with value {values} failure: {self.session.recv(2048)}')
        self._item_count = 1

    def insert_many(self,
                    table,
                    columns: tuple,
                    values: List[tuple],
                    ttl=None,
                    timestamp=None,
                    not_exists: bool = False):
        query = "BEGIN BATCH\n"
        for value in values:
            if not isinstance(columns, tuple):
                columns = tuple(columns)
            query += f"INSERT INTO {table} {columns} VALUES {value}"
            if ttl and isinstance(ttl, int):
                query += f'\nUSING TTL {ttl}'
            if timestamp and ttl and isinstance(timestamp, int):
                query += f' AND TIMESTAMP {timestamp}'
            if bool(not_exists):
                query += f'\nIF NOT EXISTS'
            query += ';\n'
        query += 'APPLY BATCH;'
        batch = MyDBBatch(self, query)
        batch.execute()
        self._item_count = len(values)


class MyDBResponse(pynosql.columndb.ColumnResponse):
    pass


class MyDBBatch(pynosql.columndb.ColumnBatch):

    def execute(self):
        self.session.session.send(self.batch)
        self.session.session.recv = mock.MagicMock(return_value="BATCH_OK")
        if self.session.session.recv(2048) != "BATCH_OK":
            raise SessionError(f'batch error: {self.session.session.recv(2048)}')


class ColumnConnectionTest(unittest.TestCase):
    def test_kvdb_connect(self):
        myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')


if __name__ == '__main__':
    unittest.main()
