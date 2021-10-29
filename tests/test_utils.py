import unittest
import nosqlapi
from test_kvdb import MyDBConnection as KVConn
from test_docdb import MyDBConnection as DocConn


# Mock of pymongo Connection object with some method (not all)
@nosqlapi.api(database_names='databases', drop_database='delete_database', close_cursor='close')
class Connection:

    def database_names(self):
        return 'test_db', 'db1', 'db2'

    def drop_database(self):
        return True

    def close_cursor(self):
        return True


class TestUtils(unittest.TestCase):

    def test_api_decorator(self):
        pymongo_conn = Connection()
        self.assertEqual(hasattr(pymongo_conn, 'database_names'), True)
        self.assertEqual(hasattr(pymongo_conn, 'databases'), True)
        self.assertEqual(pymongo_conn.close_cursor(), True)
        self.assertEqual(pymongo_conn.close(), pymongo_conn.close_cursor())
        self.assertEqual(pymongo_conn.database_names(), pymongo_conn.databases())

    def test_manager_object(self):
        man = nosqlapi.Manager(KVConn(host='mykvdb.local', username='test', password='pass', database='test_db'))
        self.assertEqual(man.database, 'test_db')
        self.assertEqual(man.acl.data, {'test': 'user_read', 'admin': 'admins', 'root': 'admins'})
        self.assertEqual(man.description, ('mykvdb.local', '12345', 'test_db'))


if __name__ == '__main__':
    unittest.main()
