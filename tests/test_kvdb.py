import unittest
import pynosql.kvdb
from pynosql import ConnectError, DatabaseError, DatabaseCreationError, DatabaseDeletionError
from unittest import mock


class MyDBConnection(pynosql.kvdb.KVConnection):
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
            return self.return_data.split()
        else:
            raise ConnectError(f"Server isn't connected")


class MyDBSession(pynosql.kvdb.KVSession):

    def __init__(self, connection):
        super().__init__()
        self.session = connection
        self.session.send("SHOW_DESC")
        self.session.recv = mock.MagicMock(return_value="server=mykvdb.local\nport=12345")
        self._description = self.session.recv(2048)

    @property
    def item_count(self):
        return self._item_count

    @property
    def description(self):
        return self._description

    def get(self, key):
        self.session.recv = mock.MagicMock(return_value="key=value")
        key, value = self.session.recv(2048).split('=')
        out = dict()
        out[key] = value
        return out

    def insert(self, key, value):
        pass

    def insert_many(self, dict_):
        pass

    def update(self, key, value):
        pass

    def update_many(self, dict_):
        pass

    def delete(self, key):
        pass

    def close(self):
        pass

    def find(self, selector):
        pass


class KVConnectionTest(unittest.TestCase):

    def test_kvdb_connect(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')

    def test_kvdb_close(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')

    def test_kvdb_create_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.create_database('test_db')
        self.assertEqual(myconn.return_data, 'DB_CREATED')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_kvdb_exists_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.has_database('test_db')
        self.assertEqual(myconn.return_data, 'DB_EXISTS')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.has_database, 'test_db')

    def test_kvdb_delete_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.delete_database('test_db')
        self.assertEqual(myconn.return_data, 'DB_DELETED')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.delete_database, 'test_db')

    def test_kvdb_get_all_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        self.assertEqual(myconn.databases(), ['test_db', 'db1', 'db2'])
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.databases)


if __name__ == '__main__':
    unittest.main()
