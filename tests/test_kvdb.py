import unittest
import pynosql.kvdb
from pynosql import ConnectError, DatabaseError, DatabaseCreationError, DatabaseDeletionError
from unittest import mock


class KVConnection(unittest.TestCase):
    class MyDBConnection(pynosql.kvdb.KVConnection):

        def close(self):
            self.connection.close()
            self.connection = None

        def connect(self):
            # Simulate socket.socket
            t = mock.Mock('AF_INET', 'SOCK_STREAM')
            t.connect = mock.MagicMock()
            t.send = mock.MagicMock()
            t.recv = mock.MagicMock(return_value='OK_PACKET')
            # Connection
            t.connect(self.host, self.port)
            t.send("CLIENT_CONNECT_WITH_DB".encode())
            # while len(t.recv(2048)) > 0:
            self._return_data = t.recv(2048)
            if self.return_data != 'OK_PACKET':
                raise ConnectError(f'Server connection error: {self.return_data}')
            self.connection = t

        def create_database(self, name):
            self.connection.send(f"CREATE_DB='{name}'".encode())
            while len(self.connection.recv(2048)) > 0:
                self._return_data.append(self.connection.recv(2048))
            if self.return_data.decode() != 'DB_CREATED':
                raise DatabaseCreationError(f'Database creation error: {self.return_data.decode()}')

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

    def test_built_connect_class(self):
        myconn = self.MyDBConnection('mykvdb.local', 12345)
        myconn.connect()


if __name__ == '__main__':
    unittest.main()
