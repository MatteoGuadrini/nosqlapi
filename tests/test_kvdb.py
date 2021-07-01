import unittest
import pynosql.kvdb
from pynosql import ConnectError, DatabaseError, DatabaseCreationError, DatabaseDeletionError
from unittest import mock


class KVConnectionTest(unittest.TestCase):
    class MyDBConnection(pynosql.kvdb.KVConnection):
        # Simulate socket.socket
        t = mock.Mock('AF_INET', 'SOCK_STREAM')
        t.connect = mock.MagicMock()
        t.send = mock.MagicMock()
        t.close = mock.MagicMock()

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
            self.t.send("CLIENT_CONNECT_WITH_DB".encode())
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='OK_PACKET')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'OK_PACKET':
                raise ConnectError(f'Server connection error: {self.return_data}')
            self.connection = self.t

        def create_database(self, name):
            if self.connection:
                self.connection.send(f"CREATE_DB='{name}'".encode())
                # while len(self.t.recv(2048)) > 0:
                self.t.recv = mock.MagicMock(return_value='DB_CREATED')
                self._return_data = self.t.recv(2048)
                if self.return_data != 'DB_CREATED':
                    raise DatabaseCreationError(f'Database creation error: {self.return_data.decode()}')
            else:
                raise ConnectError(f"Server isn't connected")

        def has_database(self, name):
            self.connection.send(f"HAS_DB='{name}'".encode())
            while len(self.connection.recv(2048)) > 0:
                self._return_data.append(self.connection.recv(2048))
            if self.return_data.decode() != 'DB_EXISTS':
                return False
            else:
                return True

        def delete_database(self, name):
            self.connection.send(f"DELETE_DB='{name}'".encode())
            while len(self.connection.recv(2048)) > 0:
                self._return_data.append(self.connection.recv(2048))
            if self.return_data.decode() != 'DB_DELETED':
                raise DatabaseDeletionError(f'Database deletion error: {self.return_data.decode()}')

        def databases(self):
            self.connection.send(f"GET_ALL_DBS".encode())
            while len(self.connection.recv(2048)) > 0:
                self._return_data.append(self.connection.recv(2048))
            if self.return_data.decode() != 'OK_PACKET':
                raise DatabaseError(f'Request error: {self.return_data.decode()}')

    def test_kvdb_connect(self):
        myconn = self.MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')

    def test_kvdb_close(self):
        myconn = self.MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')

    def test_kvdb_create_database(self):
        myconn = self.MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.create_database('test_db')
        self.assertEqual(myconn.return_data, 'DB_CREATED')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')


if __name__ == '__main__':
    unittest.main()
