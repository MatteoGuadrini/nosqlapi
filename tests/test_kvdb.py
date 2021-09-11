import unittest
from typing import Union, Any
import nosqlapi.kvdb
from nosqlapi.kvdb.orm import Keyspace, Item, Transaction
from nosqlapi import (ConnectError, DatabaseError, DatabaseCreationError, DatabaseDeletionError, SessionError,
                      SessionInsertingError, SessionClosingError, SessionDeletingError, SessionUpdatingError,
                      SessionFindingError, SelectorAttributeError, SessionACLError)
from unittest import mock
from string import Template


# Below classes is a emulation of FoundationDB like database


class MyDBConnection(nosqlapi.kvdb.KVConnection):
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
        return MyDBSession(self.connection, self.database)

    def create_database(self, name: Union[str, Keyspace]):
        if self.connection:
            name = name.name if isinstance(name, Keyspace) else name
            self.connection.send(f"CREATE_DB='{name}'")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_CREATED')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_CREATED':
                raise DatabaseCreationError(f'Database creation error: {self.return_data}')
        else:
            raise ConnectError(f"Server isn't connected")

    def has_database(self, name: Union[str, Keyspace]):
        if self.connection:
            name = name.name if isinstance(name, Keyspace) else name
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

    def delete_database(self, name: Union[str, Keyspace]):
        if self.connection:
            name = name.name if isinstance(name, Keyspace) else name
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

    def show_database(self, name: Union[str, Keyspace]):
        if self.connection:
            name = name.name if isinstance(name, Keyspace) else name
            self.connection.send(f"GET_DB={name}")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='name=test_db, size=0.4GB')
            self._return_data = self.t.recv(2048)
            if not self:
                raise DatabaseError(f'Request error: {self.return_data}')
            return MyDBResponse(self.return_data)
        else:
            raise ConnectError(f"Server isn't connected")


class MyDBSession(nosqlapi.kvdb.KVSession):

    def __init__(self, connection, database=None):
        super().__init__()
        self.session = connection
        self.session.send("SHOW_DESC")
        self.session.recv = mock.MagicMock(return_value="server=mykvdb.local\nport=12345\ndatabase=test_db")
        self._description = {item.split('=')[0]: item.split('=')[1]
                             for item in self.session.recv(2048).split('\n')}
        self._database = database

    @property
    def acl(self):
        if not self.database:
            raise ConnectError('connect to a database before request some ACLs')
        self.session.send(f"GET_ACL={self.description.get('database')}")
        self.session.recv = mock.MagicMock(return_value=f"test,user_read;admin,admins;root,admins")
        return MyDBResponse(
            data={item.split(',')[0]: item.split(',')[1]
                  for item in self.session.recv(2048).split(';')}
        )

    def get(self, key: Union[Any, Item]):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        key = key.key if isinstance(key, Item) else key
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
        if not self.database:
            raise ConnectError('connect to a database before some request')
        i = Item(key, value)
        self.session.send(f"INSERT={i.key},{i.value}")
        self.session.recv = mock.MagicMock(return_value="NEW_KEY_OK")
        if self.session.recv(2048) != "NEW_KEY_OK":
            raise SessionInsertingError(f'insert key {key} with value {value} failure')
        self._item_count = 1

    def insert_many(self, dict_: Union[dict, Keyspace]):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        if isinstance(dict_, Keyspace):
            self.session.send(f"INSERT_MANY={';'.join(','.join((item.key, item.value)) for item in dict_.store)}")
        else:
            self.session.send(f"INSERT_MANY={';'.join(','.join((k, v)) for k, v in dict_.items())}")
        self.session.recv = mock.MagicMock(return_value="NEW_KEY_OK")
        if self.session.recv(2048) != "NEW_KEY_OK":
            raise SessionInsertingError(f'insert many values failure: {self.session.recv}')
        self._item_count = len(dict_)

    def update(self, key, value):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        if self.get(key):
            i = Item(key, value)
            self.session.send(f"UPDATE={i.key},{i.value}")
            self.session.recv = mock.MagicMock(return_value="UPDATE_KEY_OK")
            if self.session.recv(2048) != "UPDATE_KEY_OK":
                raise SessionUpdatingError(f'update key {key} with value {value} failure')
        self._item_count = 1

    def update_many(self, dict_: Union[dict, Keyspace]):
        # For this type of database, not implement many updates
        raise NotImplementedError('update_many not implemented for this module')

    def delete(self, key: Union[Any, Item]):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        key = key.key if isinstance(key, Item) else key
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
        if not self.database:
            raise ConnectError('connect to a database before some request')
        if isinstance(selector, str):
            self.session.send(f"FIND={selector}")
            self.session.recv = mock.MagicMock(return_value="key=value,key1=value1")
        elif isinstance(selector, nosqlapi.kvdb.KVSelector):
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
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"GRANT={user},{role}:DATABASE={database}")
        self.session.recv = mock.MagicMock(return_value="GRANT_OK")
        if self.session.recv(2048) != "GRANT_OK":
            raise SessionACLError(f'grant {user} with role {role} on {database} failed: {self.session.recv(2048)}')
        return MyDBResponse({'user': user, 'role': role, 'db': database, 'status': "GRANT_OK"})

    def revoke(self, database, user, role=None):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"REVOKE={user},{role}:DATABASE={database}")
        self.session.recv = mock.MagicMock(return_value="REVOKE_OK")
        if self.session.recv(2048) != "REVOKE_OK":
            raise SessionACLError(f'revoke {user} with role {role} on {database} failed: {self.session.recv(2048)}')
        return MyDBResponse({'user': user, 'role': role, 'db': database, 'status': "REVOKE_OK"})

    def new_user(self, user, password, super_user=False):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"NEW={user}:PASSWORD={password}:ADMIN={super_user}")
        self.session.recv = mock.MagicMock(return_value="CREATION_OK")
        if self.session.recv(2048) != "CREATION_OK":
            raise SessionACLError(f'create user {user} failed: {self.session.recv(2048)}')
        return MyDBResponse({'user': user, 'status': self.session.recv(2048)})

    def set_user(self, user, password, super_user=False):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"USER={user}:PASSWORD={password}:ADMIN={super_user}")
        self.session.recv = mock.MagicMock(return_value="PASSWORD_CHANGED")
        if self.session.recv(2048) != "PASSWORD_CHANGED":
            raise SessionACLError(f'create user {user} failed: {self.session.recv(2048)}')
        return MyDBResponse({'user': user, 'status': self.session.recv(2048)})

    def delete_user(self, user):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"DELETE_USER={user}")
        self.session.recv = mock.MagicMock(return_value="USER_DELETED")
        if self.session.recv(2048) != "USER_DELETED":
            raise SessionACLError(f'create user {user} failed: {self.session.recv(2048)}')
        return MyDBResponse({'user': user, 'status': self.session.recv(2048)})


class MyDBResponse(nosqlapi.kvdb.KVResponse):
    pass


class MyDBSelector(nosqlapi.kvdb.KVSelector):

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

    def first_greater_or_equal(self, key: Union[Any, Item]):
        key = key.key if isinstance(key, Item) else key
        self.selector = f'$ge:*{key}'
        return self.build()

    def first_greater_than(self, key: Union[Any, Item]):
        key = key.key if isinstance(key, Item) else key
        self.selector = f'$gt:*{key}'
        return self.build()

    def last_less_or_equal(self, key: Union[Any, Item]):
        key = key.key if isinstance(key, Item) else key
        self.selector = f'$le:*{key}'
        return self.build()

    def last_less_than(self, key: Union[Any, Item]):
        key = key.key if isinstance(key, Item) else key
        self.selector = f'$lt:*{key}'
        return self.build()


class MyDBBatch(nosqlapi.kvdb.KVBatch):

    def execute(self):
        if isinstance(self.batch, Transaction):
            if self.batch.commands[0][1] != 'begin':
                self.batch.add('begin', 0)
            if self.batch.commands[-1][1] != 'end':
                self.batch.add('end')
            self.batch = f"{self.batch}"
        self.session.session.send(self.batch)
        self.session.session.recv = mock.MagicMock(return_value="BATCH_OK")
        if self.session.session.recv(2048) != "BATCH_OK":
            raise SessionError(f'batch error: {self.session.session.recv(2048)}')


class KVConnectionTest(unittest.TestCase):

    def test_kvdb_connect(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        with MyDBConnection('mykvdb.local', 12345) as myconn:
            myconn.connect()
            self.assertEqual(myconn.return_data, 'OK_PACKET')
        self.assertEqual(myconn.return_data, 'CLOSED')

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

    def test_kvdb_create_database_with_keyspace(self):
        ks = Keyspace('test_db')
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.create_database(ks)
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

    def test_kvdb_exists_database_with_keyspace(self):
        ks = Keyspace('test_db')
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.has_database(ks)
        self.assertEqual(myconn.return_data, 'DB_EXISTS')
        if myconn.return_data == 'DB_EXISTS':
            ks._exists = True
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

    def test_kvdb_delete_database_with_keyspace(self):
        ks = Keyspace('test_db')
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.delete_database(ks)
        self.assertEqual(myconn.return_data, 'DB_DELETED')
        if myconn.return_data == 'DB_DELETED':
            ks._exists = False
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

    def test_columndb_show_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        dbs = myconn.show_database('test_db')
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, 'name=test_db, size=0.4GB')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.databases)

    def test_columndb_show_database_with_keyspace(self):
        ks = Keyspace('test_db')
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        dbs = myconn.show_database(ks)
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, 'name=test_db, size=0.4GB')
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
        i = Item('key')
        d = self.mysess.get(i)
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn('key', d)

    def test_insert_key(self):
        self.mysess.insert('key', 'value')
        self.assertEqual(self.mysess.item_count, 1)

    def test_insert_many_keys(self):
        self.mysess.insert_many({'key': 'value', 'key1': 'value1'})
        self.assertEqual(self.mysess.item_count, 2)
        item = Item('key', 'value')
        item1 = Item('key1', 'value1')
        ks = Keyspace(None)
        ks.append(item)
        ks.append(item1)
        self.mysess.insert_many(ks)
        self.assertEqual(self.mysess.item_count, 2)

    def test_update_key(self):
        self.mysess.update('key', 'value')
        self.assertEqual(self.mysess.item_count, 1)

    def test_update_many_keys(self):
        self.assertRaises(NotImplementedError, self.mysess.update_many, {'key': 'value', 'key1': 'value1'})

    def test_delete_key(self):
        self.mysess.delete('key')
        self.assertEqual(self.mysess.item_count, 0)
        i = Item('key')
        self.mysess.delete(i)
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
        i = Item('key', 'value')
        data = self.mysess.find(sel.first_greater_or_equal(i))
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(self.mysess.item_count, 2)

    def test_batch(self):
        query = """
        begin
        UPDATE=key1,value1;
        UPDATE=key2,value3;
        UPDATE=key3,value3;
        end ;
        """
        batch = MyDBBatch(self.mysess, query)
        batch.execute()
        tr = Transaction()
        tr.add('UPDATE=key1,value1;')
        tr.add('UPDATE=key2,value2;')
        tr.add('UPDATE=key3,value3;')
        batch = MyDBBatch(self.mysess, tr)
        batch.execute()

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

    def test_new_user(self):
        resp = self.mysess.new_user('myuser', 'mypassword')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'CREATION_OK')

    def test_modify_password_user(self):
        resp = self.mysess.set_user('myuser', 'newpassword')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'PASSWORD_CHANGED')

    def test_delete_user(self):
        resp = self.mysess.delete_user('myuser')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'USER_DELETED')


if __name__ == '__main__':
    unittest.main()
