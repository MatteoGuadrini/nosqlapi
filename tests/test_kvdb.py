import unittest
import pynosql.kvdb
from pynosql import (ConnectError, DatabaseError, DatabaseCreationError, DatabaseDeletionError, SessionError,
                     SessionInsertingError, SessionClosingError, SessionDeletingError, SessionUpdatingError,
                     SessionFindingError, SelectorAttributeError, SessionACLError)
from unittest import mock
from string import Template


class MyDBConnection(pynosql.kvdb.KVConnection):
    # Simulate socket.socket
    t = mock.Mock('AF_INET', 'SOCK_STREAM')
    t.connect = mock.MagicMock()
    t.send = mock.MagicMock()
    t.close = mock.MagicMock()

    def __bool__(self):
        if self.return_data:
            return True

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
        if self.database:
            self.t.send(f"CLIENT_CONNECT_WITH_DB={self.database}")
        else:
            self.t.send("CLIENT_CONNECT")
        # Check credential
        if self.username and self.password:
            self.t.send(f"\nCRED={self.username}:{self.password}")
        # while len(self.t.recv(2048)) > 0:
        self.t.recv = mock.MagicMock(return_value='OK_PACKET')
        self._return_data = self.t.recv(2048)
        if self.return_data != 'OK_PACKET':
            raise ConnectError(f'Server connection error: {self.return_data}')
        self.connection = self.t
        return MyDBSession(self.connection)

    def create_database(self, name):
        if self.connection:
            self.connection.send(f"CREATE_DB='{name}'")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_CREATED')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_CREATED':
                raise DatabaseCreationError(f'Database creation error: {self.return_data}')
        else:
            raise ConnectError(f"Server isn't connected")

    def has_database(self, name):
        if self.connection:
            self.connection.send(f"DB_EXISTS='{name}'")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_EXISTS')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_EXISTS':
                return False
            else:
                return True
        else:
            raise ConnectError(f"Server isn't connected")

    def delete_database(self, name):
        if self.connection:
            self.connection.send(f"DELETE_DB='{name}'")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_DELETED')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_DELETED':
                raise DatabaseDeletionError(f'Database deletion error: {self.return_data}')
        else:
            raise ConnectError(f"Server isn't connected")

    def databases(self):
        if self.connection:
            self.connection.send(f"GET_ALL_DBS")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='test_db db1 db2')
            self._return_data = self.t.recv(2048)
            if not self:
                raise DatabaseError(f'Request error: {self.return_data}')
            return MyDBResponse(self.return_data.split())
        else:
            raise ConnectError(f"Server isn't connected")


class MyDBSession(pynosql.kvdb.KVSession):

    def __init__(self, connection):
        super().__init__()
        self.session = connection
        self.session.send("SHOW_DESC")
        self.session.recv = mock.MagicMock(return_value="server=mykvdb.local\nport=12345\ndatabase=test_db")
        self._description = {item.split('=')[0]: item.split('=')[1]
                             for item in self.session.recv(2048).split('\n')}

    @property
    def item_count(self):
        return self._item_count

    @property
    def description(self):
        return self._description

    @property
    def acl(self):
        if 'database' not in self.description:
            raise ConnectError('connect to a database before request some ACLs')
        self.session.send(f"GET_ACL={self.description.get('database')}")
        self.session.recv = mock.MagicMock(return_value=f"test,user_read;admin,admins;root,admins")
        return MyDBResponse(
            data={item.split(',')[0]: item.split(',')[1]
                  for item in self.session.recv(2048).split(';')}
        )

    def get(self, key):
        self.session.send(f"GET={key}")
        self.session.recv = mock.MagicMock(return_value=f"{key}=value")
        if self.session.recv != 'KEY_NOT_FOUND':
            key, value = self.session.recv(2048).split('=')
            out = dict()
            out[key] = value
            self._item_count = 1
            return MyDBResponse(out)
        else:
            raise SessionError(f'key {key} not exists')

    def insert(self, key, value):
        self.session.send(f"INSERT={key},{value}")
        self.session.recv = mock.MagicMock(return_value="NEW_KEY_OK")
        if self.session.recv(2048) != "NEW_KEY_OK":
            raise SessionInsertingError(f'insert key {key} with value {value} failure')
        self._item_count = 1

    def insert_many(self, dict_: dict):
        self.session.send(f"INSERT_MANY={';'.join(','.join((k, v)) for k, v in dict_.items())}")
        self.session.recv = mock.MagicMock(return_value="NEW_KEY_OK")
        if self.session.recv(2048) != "NEW_KEY_OK":
            raise SessionInsertingError(f'insert many values failure: {self.session.recv}')
        self._item_count = len(dict_)

    def update(self, key, value):
        if self.get(key):
            self.session.send(f"UPDATE={key},{value}")
            self.session.recv = mock.MagicMock(return_value="UPDATE_KEY_OK")
            if self.session.recv(2048) != "UPDATE_KEY_OK":
                raise SessionUpdatingError(f'update key {key} with value {value} failure')
        self._item_count = 1

    def update_many(self, dict_):
        # For this type of database, not implement many updates
        raise NotImplementedError('update_many not implemented for this module')

    def delete(self, key):
        self.session.send(f"DELETE={key}")
        self.session.recv = mock.MagicMock(return_value="DELETE_OK")
        if self.session.recv(2048) != 'DELETE_OK':
            raise SessionDeletingError(f'key {key} not deleted')
        self._item_count = 0

    def close(self):
        self.session.close()
        if not self.session:
            SessionClosingError('session was not closed')
        self.session = None

    def find(self, selector):
        if isinstance(selector, str):
            self.session.send(f"FIND={selector}")
            self.session.recv = mock.MagicMock(return_value="key=value,key1=value1")
        elif isinstance(selector, pynosql.kvdb.KVSelector):
            self.session.send(f"FIND={selector.build()}")
            self.session.recv = mock.MagicMock(return_value="key=value,key1=value1")
        else:
            raise SessionFindingError(f'selector is incompatible')
        out = dict()
        for item in self.session.recv(2048).split(','):
            key, value = item.split('=')
            out[key] = value
        self._item_count = len(out)
        return MyDBResponse(out)

    def grant(self, database, user, role):
        self.session.send(f"GRANT={user},{role}:DATABASE={database}")
        self.session.recv = mock.MagicMock(return_value="GRANT_OK")
        if self.session.recv(2048) != "GRANT_OK":
            raise SessionACLError(f'grant {user} with role {role} on {database} failed: {self.session.recv(2048)}')
        return MyDBResponse({'user': user, 'role': role, 'db': database, 'status': "GRANT_OK"})

    def revoke(self, database, user, role=None):
        self.session.send(f"REVOKE={user},{role}:DATABASE={database}")
        self.session.recv = mock.MagicMock(return_value="REVOKE_OK")
        if self.session.recv(2048) != "REVOKE_OK":
            raise SessionACLError(f'revoke {user} with role {role} on {database} failed: {self.session.recv(2048)}')
        return MyDBResponse({'user': user, 'role': role, 'db': database, 'status': "REVOKE_OK"})


class MyDBResponse(pynosql.kvdb.KVResponse):
    pass


class MyDBSelector(pynosql.kvdb.KVSelector):

    def build(self):
        """Build string query selector

        :return: string
        """
        if not self.selector:
            raise SelectorAttributeError('selector is mandatory for build query')
        query = Template(
            """
{selector={$selector}"""
        )
        # Check field
        if self.fields:
            query.template += '\nfields={$fields}'
        # Check limit
        if self.limit:
            query.template += '\nlimit=$limit'
        # Finalize query
        query.template += '}'
        return query.safe_substitute(
            selector=self.selector,
            fields=self.fields,
            limit=self.limit
        )

    def first_greater_or_equal(self, key):
        self.selector = f'$ge:*{key}'
        return self.build()

    def first_greater_than(self, key):
        self.selector = f'$gt:*{key}'
        return self.build()

    def last_less_or_equal(self, key):
        self.selector = f'$le:*{key}'
        return self.build()

    def last_less_than(self, key):
        self.selector = f'$lt:*{key}'
        return self.build()


class KVConnectionTest(unittest.TestCase):

    def test_kvdb_connect(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')

    def test_kvdb_connect_with_user_passw(self):
        myconn = MyDBConnection('mykvdb.local', 12345, username='admin', password='admin000')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')

    def test_kvdb_close(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')

    def test_kvdb_create_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.create_database('test_db')
        self.assertEqual(myconn.return_data, 'DB_CREATED')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_kvdb_exists_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.has_database('test_db')
        self.assertEqual(myconn.return_data, 'DB_EXISTS')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.has_database, 'test_db')

    def test_kvdb_delete_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.delete_database('test_db')
        self.assertEqual(myconn.return_data, 'DB_DELETED')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.delete_database, 'test_db')

    def test_kvdb_get_all_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        dbs = myconn.databases()
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['test_db', 'db1', 'db2'])
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.databases)


class KVSessionTest(unittest.TestCase):
    myconn = MyDBConnection('mykvdb.local', 12345, 'test_db')
    mysess = myconn.connect()

    def test_session_instance(self):
        self.assertIsInstance(self.mysess, MyDBSession)

    def test_description_session(self):
        self.assertEqual(self.mysess.description, {'database': 'test_db', 'port': '12345', 'server': 'mykvdb.local'})

    def test_get_key(self):
        d = self.mysess.get('key')
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn('key', d)

    def test_insert_key(self):
        self.mysess.insert('key', 'value')
        self.assertEqual(self.mysess.item_count, 1)

    def test_insert_many_keys(self):
        self.mysess.insert_many({'key': 'value', 'key1': 'value1'})
        self.assertEqual(self.mysess.item_count, 2)

    def test_update_key(self):
        self.mysess.update('key', 'value')
        self.assertEqual(self.mysess.item_count, 1)

    def test_update_many_keys(self):
        self.assertRaises(NotImplementedError, self.mysess.update_many, {'key': 'value', 'key1': 'value1'})

    def test_delete_key(self):
        self.mysess.delete('key')
        self.assertEqual(self.mysess.item_count, 0)

    def test_find_string_keys(self):
        data = self.mysess.find('{selector=$like:key*}')
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(self.mysess.item_count, 2)

    def test_find_selector(self):
        sel = MyDBSelector()
        sel.selector = '$eq:key'
        sel.limit = 2
        self.assertIsInstance(sel, MyDBSelector)
        data = self.mysess.find(sel)
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(self.mysess.item_count, 2)

    def test_find_selector_other_method(self):
        sel = MyDBSelector()
        self.assertIsInstance(sel, MyDBSelector)
        data = self.mysess.find(sel.first_greater_or_equal('key'))
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(self.mysess.item_count, 2)

    def test_get_acl_connection(self):
        self.assertIn('root', self.mysess.acl)
        self.assertIn('admin', self.mysess.acl)
        self.assertIn('test', self.mysess.acl)

    def test_grant_user_connection(self):
        resp = self.mysess.grant('test_db', user='test', role='read_users')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'GRANT_OK')

    def test_revoke_user_connection(self):
        resp = self.mysess.revoke('test_db', user='test', role='read_users')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'REVOKE_OK')

    def test_close_session(self):
        self.mysess.close()
        self.assertEqual(self.mysess.session, None)
        KVSessionTest.mysess = KVSessionTest.myconn.connect()


if __name__ == '__main__':
    unittest.main()
