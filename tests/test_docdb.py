import unittest
import nosqlapi.docdb
import json
from unittest import mock
from nosqlapi import (ConnectError, DatabaseCreationError, DatabaseDeletionError, DatabaseError)


# Below classes is a simple emulation of MongoDB like database


class MyDBConnection(nosqlapi.docdb.DocConnection):
    # Simulate socket.socket
    req = mock.Mock()

    def close(self):
        self.connection = None
        if self.connection is not None:
            raise ConnectError('Close connection error')

    def connect(self):
        # Connection
        scheme = 'https://' if self.ssl else 'http://'
        if self.username and self.password:
            scheme += f'{self.username}:{self.password}@'
        url = f'{scheme}{self.host}'
        self.req.get = mock.MagicMock(return_value={'body': 'server http response ok',
                                                    'status': 200,
                                                    'header': 'HTTP header OK'})
        if self.req.get(url).get('status') != 200:
            raise ConnectError('server not respond')
        self.connection = url
        # return MyDBSession(self.connection, self.database)

    def create_database(self, name):
        self.req.put = mock.MagicMock(return_value={'body': '{"result": "ok"}',
                                                    'status': 200,
                                                    'header': 'HTTP header OK'})
        if self.connection:
            ret = self.req.put(f"{self.connection}/{name}")
            if ret.get('status') != 200:
                raise DatabaseCreationError(f'Database creation error: {ret.get("status")}')
            return MyDBResponse(json.loads(ret['body']),
                                ret['status'],
                                ret['header'])
        else:
            raise ConnectError("server isn't connected")

    def has_database(self, name):
        if self.connection:
            if name in self.databases():
                return True
            else:
                return False
        else:
            raise ConnectError("server isn't connected")

    def delete_database(self, name):
        self.req.delete = mock.MagicMock(return_value={'body': '{"result": "ok"}',
                                                       'status': 200,
                                                       'header': 'HTTP header OK'})
        if self.connection:
            ret = self.req.delete(f"{self.connection}/{name}")
            if ret.get('status') != 200:
                raise DatabaseDeletionError(f'Database deletion error: {ret.get("status")}')
            return MyDBResponse(json.loads(ret['body']),
                                ret['status'],
                                ret['header'])
        else:
            raise ConnectError("server isn't connected")

    def databases(self):
        self.req.get = mock.MagicMock(return_value={'body': '{"result": ["test", "db1", "db2"]}',
                                                    'status': 200,
                                                    'header': 'HTTP header OK'})
        if self.connection:
            ret = self.req.get(f"{self.connection}/databases")
            dbs = json.loads(ret.get('body'))
            if dbs:
                return MyDBResponse(json.loads(ret['body']),
                                    ret['status'],
                                    ret['header'])
            else:
                raise DatabaseError('no databases found on this server')
        else:
            raise ConnectError("server isn't connected")


class MyDBResponse(nosqlapi.docdb.DocResponse):
    pass


class DocConnectionTest(unittest.TestCase):
    pass


class DocSessionTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
