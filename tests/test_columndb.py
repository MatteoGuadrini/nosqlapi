import unittest
import nosqlapi.columndb
from nosqlapi import (ConnectError, DatabaseError, DatabaseCreationError, DatabaseDeletionError, SessionError,
                      SessionInsertingError, SessionClosingError, SessionDeletingError,
                      SessionFindingError, SelectorAttributeError, SessionACLError)
from unittest import mock
from typing import List


# Below classes is a simple emulation of Cassandra like database


class MyDBConnection(nosqlapi.columndb.ColumnConnection):
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

    def create_database(self, name, not_exists: bool = False, replication=None, durable_writes=None):
        if self.connection:
            query = f"CREATE  KEYSPACE '{name}'"
            if not_exists:
                query += " IF NOT EXISTS"
            if replication:
                query += f" WITH REPLICATION = {replication}"
            if durable_writes is not None:
                query += f" AND DURABLE_WRITES = {str(bool(durable_writes)).lower()}"
            self.connection.send(query)
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_CREATED')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_CREATED':
                raise DatabaseCreationError(f'Database creation error: {self.return_data}')
        else:
            raise ConnectError(f"Server isn't connected")

    def has_database(self, name):
        if self.connection:
            if name not in self.databases():
                return False
            else:
                return True
        else:
            raise ConnectError(f"Server isn't connected")

    def delete_database(self, name, exists=False):
        if self.connection:
            query = f'DROP KEYSPACE'
            if exists:
                query += ' IF EXISTS'
            query += f' {name};'
            self.connection.send(query)
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_DELETED')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_DELETED':
                raise DatabaseDeletionError(f'Database deletion error: {self.return_data}')
        else:
            raise ConnectError(f"Server isn't connected")

    def databases(self):
        if self.connection:
            self.connection.send(f"DESCRIBE KEYSPACES;")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='test_db db1 db2')
            self._return_data = self.t.recv(2048)
            if not self:
                raise DatabaseError(f'Request error: {self.return_data}')
            return MyDBResponse(self.return_data.split())
        else:
            raise ConnectError(f"Server isn't connected")

    def show_database(self, name):
        if self.connection:
            self.connection.send(f"DESCRIBE KEYSPACE {name};")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='table1 table2 table3')
            self._return_data = self.t.recv(2048)
            if not self:
                raise DatabaseError(f'Request error: {self.return_data}')
            return MyDBResponse(self.return_data.split())
        else:
            raise ConnectError(f"Server isn't connected")


class MyDBSession(nosqlapi.columndb.ColumnSession):

    def __init__(self, connection, database=None):
        super().__init__()
        self.session = connection
        self.session.send("SHOW_DESC")
        self.session.recv = mock.MagicMock(return_value="server=mycolumndb.local\nport=12345\ndatabase=test_db"
                                                        "\nusername=admin")
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

    def get(self, table, *columns):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"SELECT {','.join(col for col in columns)} FROM {table}")
        self.session.recv = mock.MagicMock(return_value="name,age\nname1,age1\nname2,age2")
        if self.session.recv != 'NOT_FOUND':
            out = [tuple(row.split(','))
                   for row in self.session.recv(2048).split('\n')]
            self._item_count = len(out)
            return MyDBResponse(out)
        else:
            raise SessionError(f'columns or table not found')

    def insert(self,
               table,
               columns: tuple,
               values: tuple,
               ttl=None,
               timestamp=None,
               not_exists: bool = False):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        if not isinstance(columns, tuple):
            columns = tuple(columns)
        if not isinstance(values, tuple):
            values = tuple(values)
        query = f"INSERT INTO {table} {columns} VALUES {values}"
        if ttl and isinstance(ttl, int):
            query += f'\nUSING TTL {ttl}'
        if timestamp and ttl and isinstance(timestamp, int):
            query += f' AND TIMESTAMP {timestamp}'
        if bool(not_exists):
            query += f'\nIF NOT EXISTS'
        query += ';'
        self.session.send(query)
        self.session.recv = mock.MagicMock(return_value="INSERT_OK")
        if self.session.recv(2048) != "INSERT_OK":
            raise SessionInsertingError(f'insert into {columns} with value {values} failure: {self.session.recv(2048)}')
        self._item_count = 1

    def insert_many(self,
                    table,
                    columns: tuple,
                    values: List[tuple],
                    ttl=None,
                    timestamp=None,
                    not_exists: bool = False):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        query = "BEGIN BATCH\n"
        for value in values:
            if not isinstance(columns, tuple):
                columns = tuple(columns)
            query += f"INSERT INTO {table} {columns} VALUES {value}"
            if ttl and isinstance(ttl, int):
                query += f'\nUSING TTL {ttl}'
            if timestamp and ttl and isinstance(timestamp, int):
                query += f' AND TIMESTAMP {timestamp}'
            if bool(not_exists):
                query += f'\nIF NOT EXISTS'
            query += ';\n'
        query += 'APPLY BATCH;'
        batch = MyDBBatch(self, query)
        batch.execute()
        self._item_count = len(values)

    def update(self,
               table,
               columns: tuple,
               values: tuple,
               ttl=None,
               timestamp=None):
        # For this operation only for this test, use Batch object
        raise NotImplementedError('For this operation only for this test, use Batch object')

    def update_many(self,
                    table,
                    columns: tuple,
                    values: List[tuple],
                    ttl=None,
                    timestamp=None):
        # For this operation only for this test, use Batch object
        raise NotImplementedError('For this operation only for this test, use Batch object')

    def delete(self, table, conditions: list, exists: bool = False):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        query = f"DELETE FROM {table} WHERE {' AND '.join(condition for condition in conditions)}"
        if bool(exists):
            query += f'\nIF EXISTS'
        query += ';'
        self.session.send(query)
        self.session.recv = mock.MagicMock(return_value="DELETION:1")
        if "DELETION" not in self.session.recv(2048):
            raise SessionDeletingError(f'deleting from {table} failure: {self.session.recv(2048)}')
        self._item_count = int(self.session.recv(2048).split(':')[1])

    def close(self):
        self.session.close()
        if not self.session:
            SessionClosingError('session was not closed')
        self.session = None

    def find(self, selector: nosqlapi.columndb.ColumnSelector):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        if isinstance(selector, nosqlapi.columndb.ColumnSelector):
            self.session.send(selector.build())
            self.session.recv = mock.MagicMock(return_value="name,age\nname1,age1\nname2,age2")
        else:
            raise SessionFindingError('selector is incompatible')
        out = [tuple(row.split(','))
               for row in self.session.recv(2048).split('\n')]
        self._item_count = len(out)
        return MyDBResponse(out)

    def grant(self, database, user, role):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"GRANT {user} ON {database} TO {role};")
        self.session.recv = mock.MagicMock(return_value="GRANT_OK")
        if self.session.recv(2048) != "GRANT_OK":
            raise SessionACLError(f'grant {user} with role {role} on {database} failed: {self.session.recv(2048)}')
        return MyDBResponse({'user': user, 'role': role, 'db': database, 'status': "GRANT_OK"})

    def revoke(self, database, user, role=None):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"REVOKE {user} ON {database} TO {role};")
        self.session.recv = mock.MagicMock(return_value="REVOKE_OK")
        if self.session.recv(2048) != "REVOKE_OK":
            raise SessionACLError(f'revoke {user} with role {role} on {database} failed: {self.session.recv(2048)}')
        return MyDBResponse({'user': user, 'role': role, 'db': database, 'status': "REVOKE_OK"})

    def new_user(self, role, password, login=True, super_user=False):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"CREATE ROLE {role} WITH PASSWORD = {password} "
                          f"AND SUPERUSER = {super_user} AND LOGIN = {login};")
        self.session.recv = mock.MagicMock(return_value="CREATION_OK")
        if self.session.recv(2048) != "CREATION_OK":
            raise SessionACLError(f'create role {role} failed: {self.session.recv(2048)}')
        return MyDBResponse({'role': role, 'status': self.session.recv(2048)})


class MyDBResponse(nosqlapi.columndb.ColumnResponse):
    pass


class MyDBBatch(nosqlapi.columndb.ColumnBatch):

    def execute(self):
        self.session.session.send(self.batch)
        self.session.session.recv = mock.MagicMock(return_value="BATCH_OK")
        if self.session.session.recv(2048) != "BATCH_OK":
            raise SessionError(f'batch error: {self.session.session.recv(2048)}')


class MyDBSelector(nosqlapi.columndb.ColumnSelector):

    def build(self):
        """Build string query selector

        :return: string
        """
        if not self.selector:
            raise SelectorAttributeError('selector is mandatory for build query')
        if not self.fields:
            raise SelectorAttributeError('fields is mandatory for build query')
        query = 'SELECT '
        # Check field
        if self.fields:
            query += f"{','.join(self.fields)}"
        else:
            query += "*"
        # Check partition
        if self.partition:
            query += f' DISTINCT {self.partition}'
        # Check selector == table
        query += f' FROM {self.selector}'
        # Check condition
        if self.condition:
            query += f" WHERE {' AND '.join(condition for condition in self.condition)}"
        # Check order
        if self.order:
            query += f" ORDER BY {self.order} DESC"
        # Check limit
        if self.limit:
            query += f" LIMIT {self.limit}"
        # Check limit
        if self.filtering:
            query += " ALLOW FILTERING"
        # Finalize query
        query += ';'
        return query

    def all(self):
        """Star selector: SELECT *..."""
        self.fields = '*'
        self.build()

    def alias(self, what, alias):
        """Aliases the selector: SELECT count(*) AS total"""
        self.fields = [f"{what} AS {alias}"]
        self.build()

    def cast(self, column, type_):
        """Casts a selector to a type: SELECT CAST(a AS double)"""
        self.fields = [f'CAST({column} AS {type_})']
        self.build()

    def count(self, column='*'):
        """Selects the count of all returned rows: SELECT count(*)"""
        self.fields = [f'count({column})']
        self.build()


class ColumnConnectionTest(unittest.TestCase):
    def test_columndb_connect(self):
        myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')

    def test_columndb_close(self):
        myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')

    def test_columndb_create_database(self):
        myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.create_database('test_db')
        self.assertEqual(myconn.return_data, 'DB_CREATED')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_columndb_exists_database(self):
        myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        self.assertTrue(myconn.has_database('test_db'))
        self.assertFalse(myconn.has_database('casual'))
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.has_database, 'test_db')

    def test_columndb_delete_database(self):
        myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        myconn.delete_database('test_db')
        self.assertEqual(myconn.return_data, 'DB_DELETED')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.delete_database, 'test_db')

    def test_columndb_get_all_database(self):
        myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        dbs = myconn.databases()
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['test_db', 'db1', 'db2'])
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.databases)

    def test_columndb_show_database(self):
        myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        dbs = myconn.show_database('test_db')
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['table1', 'table2', 'table3'])
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.databases)


class ColumnSessionTest(unittest.TestCase):
    myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass', database='test_db')
    mysess = myconn.connect()

    def test_session_instance(self):
        self.assertIsInstance(self.mysess, MyDBSession)

    def test_description_session(self):
        self.assertEqual(self.mysess.description, {'database': 'test_db', 'port': '12345',
                                                   'server': 'mycolumndb.local', 'username': 'admin'})

    def test_get_column(self):
        d = self.mysess.get('table', 'col1', 'col2')
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn(('name', 'age'), d)

    def test_insert_data(self):
        self.mysess.insert('table', columns=('name', 'age'), values=('Matteo', '35'))
        self.assertEqual(self.mysess.item_count, 1)

    def test_insert_data_with_ttl(self):
        self.mysess.insert('table', columns=('name', 'age'), values=('Matteo', '35'), ttl=123456)
        self.assertEqual(self.mysess.item_count, 1)

    def test_insert_data_with_timestamp(self):
        self.mysess.insert('table', columns=('name', 'age'), values=('Matteo', '35'), ttl=123456, timestamp=1626681089)
        self.assertEqual(self.mysess.item_count, 1)

    def test_insert_data_with_if_not_exists(self):
        self.mysess.insert('table', columns=('name', 'age'), values=('Matteo', '35'), ttl=123456,
                           timestamp=1626681089, not_exists=True)
        self.assertEqual(self.mysess.item_count, 1)

    def test_insert_many_data(self):
        values = [('Matteo', '35'), ('Arthur', '42')]
        self.mysess.insert_many('table', columns=('name', 'age'), values=values)
        self.assertEqual(self.mysess.item_count, 2)

    def test_insert_many_data_with_ttl(self):
        values = [('Matteo', '35'), ('Arthur', '42')]
        self.mysess.insert_many('table', columns=('name', 'age'), values=values, ttl=123456)
        self.assertEqual(self.mysess.item_count, 2)

    def test_insert_many_data_with_timestamp(self):
        values = [('Matteo', '35'), ('Arthur', '42')]
        self.mysess.insert_many('table', columns=('name', 'age'), values=values, ttl=123456, timestamp=1626681089)
        self.assertEqual(self.mysess.item_count, 2)

    def test_insert_many_data_with_if_not_exists(self):
        values = [('Matteo', '35'), ('Arthur', '42')]
        self.mysess.insert_many('table', columns=('name', 'age'), values=values, ttl=123456,
                                timestamp=1626681089, not_exists=True)
        self.assertEqual(self.mysess.item_count, 2)

    def test_update_data(self):
        self.assertRaises(NotImplementedError, self.mysess.update, 'table', ('name', 'age'), ('Matteo', '35'))

    def test_update_many_data(self):
        self.assertRaises(NotImplementedError, self.mysess.update_many, 'table', ('name', 'age'),
                          [('Matteo', '35'), ('Arthur', '42')])

    def test_delete_data(self):
        self.mysess.delete('table', ['name=Matteo'])
        self.assertEqual(self.mysess.item_count, 1)

    def test_delete_data_with_more_conditions(self):
        self.mysess.delete('table', ['name=Matteo', 'age>=34'])
        self.assertEqual(self.mysess.item_count, 1)

    def test_find_selector(self):
        sel = MyDBSelector()
        sel.selector = 'table'
        sel.fields = ['name', 'age']
        self.assertIsInstance(sel, MyDBSelector)
        data = self.mysess.find(sel)
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(self.mysess.item_count, 3)

    def test_find_selector_with_all(self):
        sel = MyDBSelector()
        sel.selector = 'table'
        sel.all()
        sel.partition = 'users'
        self.assertIsInstance(sel, MyDBSelector)
        data = self.mysess.find(sel)
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(self.mysess.item_count, 3)

    def test_find_selector_with_alias(self):
        sel = MyDBSelector()
        sel.selector = 'table'
        sel.alias('name', 'cn')
        self.assertIsInstance(sel, MyDBSelector)
        data = self.mysess.find(sel)
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(self.mysess.item_count, 3)

    def test_find_selector_with_cast(self):
        sel = MyDBSelector()
        sel.selector = 'table'
        sel.fields = ['name', 'age']
        sel.cast('age', 'float')
        self.assertIsInstance(sel, MyDBSelector)
        data = self.mysess.find(sel)
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(self.mysess.item_count, 3)

    def test_find_selector_with_count(self):
        sel = MyDBSelector()
        sel.selector = 'table'
        sel.fields = ['name', 'age']
        sel.count('age')
        self.assertIsInstance(sel, MyDBSelector)
        data = self.mysess.find(sel)
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(self.mysess.item_count, 3)

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
        ColumnSessionTest.mysess = ColumnSessionTest.myconn.connect()

    def test_batch(self):
        query = """
        BEGIN BATCH
            UPDATE table SET name = 'Arthur' WHERE name=Matteo AND age=35;
        APPLY BATCH ;
        """
        batch = MyDBBatch(self.mysess, query)
        batch.execute()

    def test_new_user(self):
        resp = self.mysess.new_user('myrole', 'mypassword')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'CREATION_OK')


if __name__ == '__main__':
    unittest.main()
