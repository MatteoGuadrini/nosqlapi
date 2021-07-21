import unittest
import nosqlapi.docdb
from unittest import mock
from nosqlapi import (ConnectError)


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
        url = f'{scheme}{self.host}'
        self.req.get = mock.MagicMock(return_value={'body': 'server http response ok',
                                                    'status': 200,
                                                    'header': 'HTTP header OK'})
        if self.req.get(url).get('status') != 200:
            raise ConnectError('server not respond')
        self.connection = url
        # return MyDBSession(self.connection, self.database)


class DocConnectionTest(unittest.TestCase):
    pass


class DocSessionTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
