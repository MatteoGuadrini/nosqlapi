import unittest
from string import Template
from typing import Union, Any
from unittest import mock

import nosqlapi.kvdb
from nosqlapi import (ConnectError, DatabaseError, DatabaseCreationError, DatabaseDeletionError, SessionError,
                      SessionInsertingError, SessionClosingError, SessionDeletingError, SessionUpdatingError,
                      SessionFindingError, SelectorAttributeError, SessionACLError)
from nosqlapi.kvdb.odm import Keyspace, Item, Transaction, Index


# Below classes is a emulation of FoundationDB like database


class MyDBConnection(nosqlapi.kvdb.KVConnection):
    # Simulate socket.socket
    t = mock.Mock('AF_INET', 'SOCK_STREAM')
    t.connect = mock.MagicMock()
    t.send = mock.MagicMock()
    t.close = mock.MagicMock()

    def close(self):
        self._connected = False
        self.t.recv = mock.MagicMock(return_value='CLOSED')
        if self.t.recv(2048) != 'CLOSED':
            raise ConnectError(f'Close connection error: {self.t.recv(2048)}')

    def connect(self):
        # Connection
        self.t.connect(self.host, self.port)
        if self.database:
            self.t.send(f"CLIENT_CONNECT_WITH_DB={self.database}")
        else:
            self.t.send("CLIENT_CONNECT")
        # Check credential
        if self.user and self.password:
            self.t.send(f"\nCRED={self.user}:{self.password}")
        self.t.recv = mock.MagicMock(return_value='OK_PACKET')
        if self.t.recv(2048) != 'OK_PACKET':
            raise ConnectError(f'Server connection error: {self.t.recv(2048)}')
        self._connected = True
        return MyDBSession(self.t, self.database)

    def create_database(self, name: Union[str, Keyspace]):
        if self:
            name = name.name if isinstance(name, Keyspace) else name
            self.t.send(f"CREATE_DB='{name}'")
            self.t.recv = mock.MagicMock(return_value='DB_CREATED')
            if self.t.recv(2048) != 'DB_CREATED':
                raise DatabaseCreationError(f'Database creation error: {self.t.recv(2048)}')
        else:
            raise ConnectError(f"Server isn't connected")

    def has_database(self, name: Union[str, Keyspace]):
        if self:
            name = name.name if isinstance(name, Keyspace) else name
            self.t.send(f"DB_EXISTS='{name}'")
            self.t.recv = mock.MagicMock(return_value='DB_EXISTS')
            if self.t.recv(2048) != 'DB_EXISTS':
                return False
            else:
                return True
        else:
            raise ConnectError(f"Server isn't connected")

    def delete_database(self, name: Union[str, Keyspace]):
        if self:
            name = name.name if isinstance(name, Keyspace) else name
            self.t.send(f"DELETE_DB='{name}'")
            self.t.recv = mock.MagicMock(return_value='DB_DELETED')
            if self.t.recv(2048) != 'DB_DELETED':
                raise DatabaseDeletionError(f'Database deletion error: {self.t.recv(2048)}')
            return MyDBResponse(True)
        else:
            raise ConnectError(f"Server isn't connected")

    def databases(self):
        if self:
            self.t.send(f"GET_ALL_DBS")
            self.t.recv = mock.MagicMock(return_value='test_db db1 db2')
            if self.t.recv(2048) == 'DB_ERROR':
                raise DatabaseError(f'Request error: {self.t.recv(2048)}')
            return MyDBResponse(self.t.recv(2048).split())
        else:
            raise ConnectError(f"Server isn't connected")

    def show_database(self, name: Union[str, Keyspace]):
        if self:
            name = name.name if isinstance(name, Keyspace) else name
            self.t.send(f"GET_DB={name}")
            self.t.recv = mock.MagicMock(return_value='name=test_db, size=0.4GB')
            self._return_data = self.t.recv(2048)
            if self.t.recv(2048) == 'DB_ERROR':
                raise DatabaseError(f'Request error: {self.t.recv(2048)}')
            return MyDBResponse(self.t.recv(2048))
        else:
            raise ConnectError(f"Server isn't connected")


class MyDBSession(nosqlapi.kvdb.KVSession):

    @property
    def item_count(self):
        return self._item_count

    @property
    def description(self):
        self.connection.send("SHOW_DESC")
        self.connection.recv = mock.MagicMock(return_value="server=mykvdb.local\nport=12345\ndatabase=test_db")
        self._description = tuple([item.split('=')[1]
                                   for item in self.connection.recv(2048).split('\n')])
        return self._description

    @property
    def acl(self):
        if not self.connection:
            raise ConnectError('connect to a database before request some ACLs')
        self.connection.send(f"GET_ACL={self.description[2]}")
        self.connection.recv = mock.MagicMock(return_value="test,user_read;admin,admins;root,admins")
        return MyDBResponse(
            data={item.split(',')[0]: item.split(',')[1]
                  for item in self.connection.recv(2048).split(';')}
        )

    @property
    def indexes(self):
        if not self.connection:
            raise ConnectError('connect to a database before request indexes.')
        self.connection.send(f"GET_INDEX={self.description[2]}")
        self.connection.recv = mock.MagicMock(return_value="index1,index2")
        return MyDBResponse(
            data=[item for item in self.connection.recv(2048).split(',')]
        )

    def get(self, key: Union[Any, Item]):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        key = key.key if isinstance(key, Item) else key
        self.connection.send(f"GET={key}")
        self.connection.recv = mock.MagicMock(return_value=f"{key}=value")
        if self.connection.recv != 'KEY_NOT_FOUND':
            key, value = self.connection.recv(2048).split('=')
            out = dict()
            out[key] = value
            self._item_count = 1
            return MyDBResponse(out)
        else:
            raise SessionError(f'key {key} not exists')

    def insert(self, key, value):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        i = Item(key, value)
        self.connection.send(f"INSERT={i.key},{i.value}")
        self.connection.recv = mock.MagicMock(return_value="NEW_KEY_OK")
        if self.connection.recv(2048) != "NEW_KEY_OK":
            raise SessionInsertingError(f'insert key {key} with value {value} failure')
        self._item_count = 1

    def insert_many(self, dict_: Union[dict, Keyspace]):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(dict_, Keyspace):
            self.connection.send(f"INSERT_MANY={';'.join(','.join((item.key, item.value)) for item in dict_.store)}")
        else:
            self.connection.send(f"INSERT_MANY={';'.join(','.join((k, v)) for k, v in dict_.items())}")
        self.connection.recv = mock.MagicMock(return_value="NEW_KEY_OK")
        if self.connection.recv(2048) != "NEW_KEY_OK":
            raise SessionInsertingError(f'insert many values failure: {self.connection.recv}')
        self._item_count = len(dict_)

    def update(self, key, value):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if self.get(key):
            i = Item(key, value)
            self.connection.send(f"UPDATE={i.key},{i.value}")
            self.connection.recv = mock.MagicMock(return_value="UPDATE_KEY_OK")
            if self.connection.recv(2048) != "UPDATE_KEY_OK":
                raise SessionUpdatingError(f'update key {key} with value {value} failure')
        self._item_count = 1

    def update_many(self, dict_: Union[dict, Keyspace]):
        # For this type of database, not implement many updates
        raise NotImplementedError('update_many not implemented for this module')

    def delete(self, key: Union[Any, Item]):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        key = key.key if isinstance(key, Item) else key
        self.connection.send(f"DELETE={key}")
        self.connection.recv = mock.MagicMock(return_value="DELETE_OK")
        if self.connection.recv(2048) != 'DELETE_OK':
            raise SessionDeletingError(f'key {key} not deleted')
        self._item_count = 0

    def close(self):
        self.connection.close()
        if not self.connection:
            SessionClosingError('session was not closed')
        self._database = None

    def find(self, selector):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(selector, str):
            self.connection.send(f"FIND={selector}")
            self.connection.recv = mock.MagicMock(return_value="key=value,key1=value1")
        elif isinstance(selector, nosqlapi.kvdb.KVSelector):
            self.connection.send(f"FIND={selector.build()}")
            self.connection.recv = mock.MagicMock(return_value="key=value,key1=value1")
        else:
            raise SessionFindingError(f'selector is incompatible')
        out = dict()
        for item in self.connection.recv(2048).split(','):
            key, value = item.split('=')
            out[key] = value
        self._item_count = len(out)
        return MyDBResponse(out)

    def grant(self, database, user, role):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"GRANT={user},{role}:DATABASE={database}")
        self.connection.recv = mock.MagicMock(return_value="GRANT_OK")
        if self.connection.recv(2048) != "GRANT_OK":
            raise SessionACLError(f'grant {user} with role {role} on {database} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'user': user, 'role': role, 'db': database, 'status': "GRANT_OK"})

    def revoke(self, database, user, role=None):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"REVOKE={user},{role}:DATABASE={database}")
        self.connection.recv = mock.MagicMock(return_value="REVOKE_OK")
        if self.connection.recv(2048) != "REVOKE_OK":
            raise SessionACLError(f'revoke {user} with role {role} on {database} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'user': user, 'role': role, 'db': database, 'status': "REVOKE_OK"})

    def new_user(self, user, password, super_user=False):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"NEW={user}:PASSWORD={password}:ADMIN={super_user}")
        self.connection.recv = mock.MagicMock(return_value="CREATION_OK")
        if self.connection.recv(2048) != "CREATION_OK":
            raise SessionACLError(f'create user {user} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'user': user, 'status': self.connection.recv(2048)})

    def set_user(self, user, password, super_user=False):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"USER={user}:PASSWORD={password}:ADMIN={super_user}")
        self.connection.recv = mock.MagicMock(return_value="PASSWORD_CHANGED")
        if self.connection.recv(2048) != "PASSWORD_CHANGED":
            raise SessionACLError(f'create user {user} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'user': user, 'status': self.connection.recv(2048)})

    def delete_user(self, user):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"DELETE_USER={user}")
        self.connection.recv = mock.MagicMock(return_value="USER_DELETED")
        if self.connection.recv(2048) != "USER_DELETED":
            raise SessionACLError(f'create user {user} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'user': user, 'status': self.connection.recv(2048)})

    def add_index(self, name: Union[str, Index], key=None):
        if not self.connection:
            raise DatabaseError('database is not set')
        if isinstance(name, Index):
            key = name.key
            name = name.name
        self.connection.send(f"NEW_INDEX={name} WITH_KEY={key}")
        self.connection.recv = mock.MagicMock(return_value=f"INDEX_OK={name}")
        if self.connection.recv != 'KO':
            self._item_count = 1
            return MyDBResponse(self.connection.recv(2048).split('=')[1])
        else:
            raise SessionError(f'index not created: {name}')

    def delete_index(self, name: Union[str, Index]):
        if not self.connection:
            raise DatabaseError('database is not set')
        if isinstance(name, Index):
            name = name.name
        self.connection.send(f"DELETE_INDEX={name}")
        self.connection.recv = mock.MagicMock(return_value=f"INDEX_REMOVED={name}")
        if self.connection.recv != 'KO':
            self._item_count = 1
            return MyDBResponse(self.connection.recv(2048).split('=')[1])
        else:
            raise SessionError(f'index not removed: {name}')

    def copy(self, source, destination):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"COPY={source},{destination}")
        self.connection.recv = mock.MagicMock(return_value="COPY_KEY_OK")
        if self.connection.recv(2048) != "COPY_KEY_OK":
            raise SessionInsertingError(f'copy key {source} to {destination} failure')
        self._item_count = 1


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
    # Simulate socket.socket
    t = mock.Mock('AF_INET', 'SOCK_STREAM')
    t.send = mock.MagicMock()

    def execute(self):
        if isinstance(self.batch, Transaction):
            if self.batch.commands[0][1] != 'begin':
                self.batch.add('begin', 0)
            if self.batch.commands[-1][1] != 'end':
                self.batch.add('end')
            self.batch = f"{self.batch}"
        self.t.send(self.batch)
        self.t.recv = mock.MagicMock(return_value="BATCH_OK")
        if self.t.recv(2048) != "BATCH_OK":
            raise SessionError(f'batch error: {self.t.recv(2048)}')
        return MyDBResponse(self.t.recv(2048))


class KVConnectionTest(unittest.TestCase):

    def test_kvdb_connect(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        with MyDBConnection('mykvdb.local', 12345) as myconn:
            myconn.connect()
            self.assertTrue(myconn)
        self.assertFalse(myconn)

    def test_kvdb_connect_with_user_passw(self):
        myconn = MyDBConnection('mykvdb.local', port=12345, user='admin', password='admin000')
        myconn.connect()
        self.assertTrue(myconn)

    def test_kvdb_close(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        myconn.close()
        self.assertFalse(myconn)

    def test_kvdb_create_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        myconn.create_database('test_db')
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_kvdb_create_database_with_keyspace(self):
        ks = Keyspace('test_db')
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        myconn.create_database(ks)
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_kvdb_exists_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        myconn.has_database('test_db')
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.has_database, 'test_db')

    def test_kvdb_exists_database_with_keyspace(self):
        ks = Keyspace('test_db')
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        myconn.has_database(ks)
        if myconn.has_database(ks):
            ks._exists = True
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.has_database, 'test_db')

    def test_kvdb_delete_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        myconn.delete_database('test_db')
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.delete_database, 'test_db')

    def test_kvdb_delete_database_with_keyspace(self):
        ks = Keyspace('test_db')
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        myconn.delete_database(ks)
        if myconn.has_database(ks):
            ks._exists = False
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.delete_database, 'test_db')

    def test_kvdb_get_all_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        dbs = myconn.databases()
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['test_db', 'db1', 'db2'])
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.databases)

    def test_columndb_show_database(self):
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        dbs = myconn.show_database('test_db')
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, 'name=test_db, size=0.4GB')
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.databases)

    def test_columndb_show_database_with_keyspace(self):
        ks = Keyspace('test_db')
        myconn = MyDBConnection('mykvdb.local', 12345)
        myconn.connect()
        self.assertTrue(myconn)
        dbs = myconn.show_database(ks)
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, 'name=test_db, size=0.4GB')
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.databases)


class KVSessionTest(unittest.TestCase):
    myconn = MyDBConnection(host='mykvdb.local', port=12345, database='test_db')
    mysess = myconn.connect()

    def test_session_instance(self):
        self.assertIsInstance(self.mysess, MyDBSession)

    def test_description_session(self):
        self.assertEqual(self.mysess.description, ('mykvdb.local', '12345', 'test_db'))

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
        ks = Keyspace('db')
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
        batch = MyDBBatch(query, self.mysess)
        batch.execute()
        tr = Transaction()
        tr.add('UPDATE=key1,value1;')
        tr.add('UPDATE=key2,value2;')
        tr.add('UPDATE=key3,value3;')
        batch = MyDBBatch(tr, self.mysess)
        batch.execute()

    def test_call_batch(self):
        tr = Transaction()
        tr.add('UPDATE=key1,value1;')
        tr.add('UPDATE=key2,value2;')
        tr.add('UPDATE=key3,value3;')
        batch = MyDBBatch(tr, self.mysess)
        self.mysess.call(batch)

    def test_batch_add_remove_modify(self):
        query = ["begin", "UPDATE=key1,value1;", "UPDATE=key2,value2;", "UPDATE=key3,value3;"]
        batch = MyDBBatch(query, self.mysess)
        # Add element
        batch.batch.append("end ;")
        self.assertEqual(len(batch.batch), 5)
        # Modify element
        batch.batch[3] = "UPDATE=key4,value4;"
        self.assertEqual(batch.batch[3], "UPDATE=key4,value4;")
        # Delete element
        batch.batch.append("UNUSEFUL;")
        self.assertEqual(len(batch.batch), 6)
        del batch.batch[-1]
        self.assertEqual(len(batch.batch), 5)
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
        self.assertEqual(self.mysess.database, None)
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

    def test_add_index(self):
        resp = self.mysess.add_index('test_index', 'key')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, 'test_index')
        index = Index('test_index', 'key')
        resp = self.mysess.add_index(index)
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, 'test_index')

    def test_delete_index(self):
        resp = self.mysess.delete_index('test_index')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, 'test_index')
        index = Index('test_index', 'key')
        resp = self.mysess.delete_index(index)
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, 'test_index')

    def test_get_indexes(self):
        self.assertIn('index1', self.mysess.indexes)
        self.assertIn('index2', self.mysess.indexes)

    def test_copy_keys(self):
        self.mysess.insert('key', 'key1')
        self.assertEqual(self.mysess.item_count, 1)


if __name__ == '__main__':
    unittest.main()
