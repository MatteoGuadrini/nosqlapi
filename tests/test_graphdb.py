import unittest
from unittest import mock
import nosqlapi.graphdb
from nosqlapi import (ConnectError)

# Below classes is a simple emulation of Neo4j like database

class MyDBConnection(nosqlapi.graphdb.GraphConnection):
    # Simulate http requests
    req = mock.Mock()

    def close(self):
        self.connection = None
        if self.connection is not None:
            raise ConnectError('Close connection error')

    def connect(self):
        # Connection
        if not self.port:
            self.port = 7474
        scheme = 'bolt://'
        url = f'{scheme}'
        if self.username and self.password:
            url += f'{self.username}:{self.password}@'
        url += f'{self.host}:{self.port}'
        self.req.get = mock.MagicMock(return_value={'body': 'server connected',
                                                    'status': 200,
                                                    'header': f'CONNECT TO {url}'
                                                              f'WITH TIMEOUT 30'})
        if self.req.get(url).get('status') != 200:
            raise ConnectError('server not respond')
        self.connection = url
        # return MyDBSession(self.connection)


class GraphConnectionTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
