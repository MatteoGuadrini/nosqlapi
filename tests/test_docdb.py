import unittest
import nosqlapi.docdb
from unittest import mock


# Below classes is a simple emulation of MongoDB like database


class MyDBConnection(nosqlapi.docdb.DocConnection):
    # Simulate socket.socket
    req = mock.Mock()
    req.get = mock.MagicMock()
    req.put = mock.MagicMock()
    req.post = mock.MagicMock()
    req.delete = mock.MagicMock()
    req.head = mock.MagicMock()


class DocConnectionTest(unittest.TestCase):
    pass


class DocSessionTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
