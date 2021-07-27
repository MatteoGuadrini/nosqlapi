import unittest
from unittest import mock
import nosqlapi.graphdb


# Below classes is a simple emulation of Neo4j like database

class MyDBConnection(nosqlapi.graphdb.GraphConnection):
    # Simulate http requests
    req = mock.Mock()


class GraphConnectionTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
