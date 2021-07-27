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


class GraphConnectionTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
