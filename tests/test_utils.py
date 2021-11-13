import unittest
import nosqlapi
from test_kvdb import MyDBConnection as KVConn, MyDBResponse
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

    def test_manager_crud_operation(self):
        man = nosqlapi.Manager(KVConn(host='mykvdb.local', username='test', password='pass', database='test_db'))
        # Get operation
        d = man.get('key')
        self.assertEqual(repr(d), '<nosqlapi MyDBResponse object>')
        self.assertIn('key', d)
        # Find operation
        d = man.find('{selector=$like:key*}')
        self.assertEqual(d.data, {'key': 'value', 'key1': 'value1'})
        self.assertEqual(man.item_count, 2)
        # Delete operation
        man.delete('key')
        self.assertEqual(man.item_count, 0)
        # Insert and update operation
        man.insert('key', 'value')
        self.assertEqual(man.item_count, 1)
        man.update('key', 'new_value')
        self.assertEqual(man.item_count, 1)

    def test_connection_operation(self):
        man = nosqlapi.Manager(KVConn(host='mykvdb.local', username='test', password='pass', database='test_db'))
        # Create database
        man.create_database('test_db')
        self.assertEqual(man.connection.return_data, 'DB_CREATED')
        # Exists database
        man.has_database('test_db')
        self.assertEqual(man.connection.return_data, 'DB_EXISTS')
        # Delete database
        man.delete_database('test_db')
        self.assertEqual(man.connection.return_data, 'DB_DELETED')
        # All databases
        dbs = man.databases()
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['test_db', 'db1', 'db2'])
        # Show database
        db = man.show_database('test_db')
        self.assertIsInstance(db, MyDBResponse)
        self.assertEqual(db.data, 'name=test_db, size=0.4GB')

    def test_change_connection(self):
        man = nosqlapi.Manager(KVConn(host='mykvdb.local', username='test', password='pass', database='test_db'))
        self.assertIsInstance(man.connection, KVConn)
        self.assertIn('mykvdb.local', man.description)
        man.change(DocConn('mydocdb.local', 12345, username='admin', password='test'))
        self.assertIsInstance(man.connection, DocConn)
        self.assertEqual('mydocdb.local', man.description['host'])

    def test_global_session(self):
        man = nosqlapi.Manager(KVConn(host='mykvdb.local', username='test', password='pass', database='test_db'))
        self.assertIsInstance(man.connection, KVConn)
        self.assertIn('mykvdb.local', man.description)
        nosqlapi.global_session(DocConn('mydocdb.local', 12345, username='admin', password='test'))
        self.assertEqual('mydocdb.local', nosqlapi.SESSION.description['host'])


if __name__ == '__main__':
    unittest.main()
