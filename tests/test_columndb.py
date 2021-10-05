import unittest
import nosqlapi.columndb
from typing import Union
from nosqlapi.columndb.orm import Keyspace, Table, Column, Index
from nosqlapi.common.orm import Varchar, Varint, Timestamp
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

    def create_database(self, name: Union[str, Keyspace], not_exists: bool = False, replication=None,
                        durable_writes=None):
        if self.connection:
            if isinstance(name, Keyspace):
                name = name.name
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

    def has_database(self, name: Union[str, Keyspace]):
        if self.connection:
            if isinstance(name, Keyspace):
                name = name.name
            if name not in self.databases():
                return False
            else:
                return True
        else:
            raise ConnectError(f"Server isn't connected")

    def delete_database(self, name: Union[str, Keyspace], exists=False):
        if self.connection:
            if isinstance(name, Keyspace):
                name = name.name
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

    def show_database(self, name: Union[str, Keyspace]):
        if self.connection:
            if isinstance(name, Keyspace):
                name = name.name
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

    def get(self, table: Union[str, Table], *columns: Union[str, Column]):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        cols = []
        for column in columns:
            if isinstance(column, Column):
                cols.append(column.name)
            else:
                cols.append(column)
        self.session.send(f"SELECT {','.join(col for col in cols)} FROM {table}")
        self.session.recv = mock.MagicMock(return_value="name,age\nname1,age1\nname2,age2")
        if self.session.recv != 'NOT_FOUND':
            out = [tuple(row.split(','))
                   for row in self.session.recv(2048).split('\n')]
            self._item_count = len(out)
            return MyDBResponse(out)
        else:
            raise SessionError(f'columns or table not found')

    def insert(self,
               table: Union[str, Table],
               columns: tuple,
               values: tuple,
               ttl=None,
               timestamp: Union[int, Timestamp] = None,
               not_exists: bool = False):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        cols = []
        for column in columns:
            if isinstance(column, Column):
                cols.append(column.name)
            else:
                cols.append(column)
        columns = tuple(cols)
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
                    table: Union[str, Table],
                    columns: tuple,
                    values: List[tuple],
                    ttl=None,
                    timestamp: Union[int, Timestamp] = None,
                    not_exists: bool = False):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        query = "BEGIN BATCH\n"
        for value in values:
            cols = []
            for column in columns:
                if isinstance(column, Column):
                    cols.append(column.name)
                else:
                    cols.append(column)
            columns = tuple(cols)
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
               table: Union[str, Table],
               columns: tuple,
               values: tuple,
               ttl=None,
               timestamp: Union[int, Timestamp] = None):
        # For this operation only for this test, use Batch object
        raise NotImplementedError('For this operation only for this test, use Batch object')

    def update_many(self,
                    table: Union[str, Table],
                    columns: tuple,
                    values: List[tuple],
                    ttl=None,
                    timestamp: Union[int, Timestamp] = None):
        # For this operation only for this test, use Batch object
        raise NotImplementedError('For this operation only for this test, use Batch object')

    def delete(self, table: Union[str, Table], conditions: list, exists: bool = False):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
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

    def set_user(self, role, password):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"ALTER ROLE {role} WITH PASSWORD = {password}")
        self.session.recv = mock.MagicMock(return_value="PASSWORD_CHANGED")
        if self.session.recv(2048) != "PASSWORD_CHANGED":
            raise SessionACLError(f'create role {role} failed: {self.session.recv(2048)}')
        return MyDBResponse({'role': role, 'status': self.session.recv(2048)})

    def delete_user(self, role):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        self.session.send(f"DROP ROLE {role}")
        self.session.recv = mock.MagicMock(return_value="ROLE_DELETED")
        if self.session.recv(2048) != "ROLE_DELETED":
            raise SessionACLError(f'create role {role} failed: {self.session.recv(2048)}')
        return MyDBResponse({'role': role, 'status': self.session.recv(2048)})

    def add_index(self, name: Union[str, Index], table=None, column=None):
        if not self.database:
            raise ConnectError('connect to a database before some request')
        if isinstance(name, Index):
            column = name.column
            table = name.table
            name = name.name
        if table is None and column is None:
            raise SessionInsertingError('table name and column name is mandatory to create an index.')
        self.session.send(f"CREATE INDEX {name} ON {table} ({column});")
        self.session.recv = mock.MagicMock(return_value="INDEX_CREATED")
        if self.session.recv(2048) != "INDEX_CREATED":
            raise SessionACLError(f'create index {name} failed: {self.session.recv(2048)}')
        return MyDBResponse({'index': name, 'status': self.session.recv(2048)})


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
        myconn.create_database(Keyspace('test_db'))
        self.assertEqual(myconn.return_data, 'DB_CREATED')
        myconn.close()
        self.assertEqual(myconn.return_data, 'CLOSED')
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_columndb_exists_database(self):
        myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')
        self.assertTrue(myconn.has_database('test_db'))
        self.assertTrue(myconn.has_database(Keyspace('test_db')))
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
        myconn.delete_database(Keyspace('test_db'))
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
        dbs = myconn.show_database(Keyspace('test_db'))
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
        d = self.mysess.get('table', 'name', 'age')
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn(('name', 'age'), d)
        d = self.mysess.get(Table('table'), Column('name'), Column('age'))
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn(('name', 'age'), d)

    def test_insert_data(self):
        self.mysess.insert('table', columns=('name', 'age'), values=('Matteo', '35'))
        self.assertEqual(self.mysess.item_count, 1)
        name = Column('name', of_type=Varchar)
        age = Column('age', of_type=Varint)
        self.mysess.insert('table', columns=(name, age), values=(Varchar('Matteo'), Varint(35)))
        self.assertEqual(self.mysess.item_count, 1)

    def test_insert_data_with_ttl(self):
        self.mysess.insert('table', columns=('name', 'age'), values=('Matteo', '35'), ttl=123456)
        self.assertEqual(self.mysess.item_count, 1)

    def test_insert_data_with_timestamp(self):
        self.mysess.insert('table', columns=('name', 'age'), values=('Matteo', '35'), ttl=123456, timestamp=1626681089)
        self.assertEqual(self.mysess.item_count, 1)
        name = Column('name', of_type=Varchar)
        age = Column('age', of_type=Varint)
        self.mysess.insert('table', columns=(name, age), values=(Varchar('Matteo'), Varint(35)),
                           timestamp=Timestamp(2021, 8, 15))
        self.assertEqual(self.mysess.item_count, 1)

    def test_insert_data_with_if_not_exists(self):
        self.mysess.insert('table', columns=('name', 'age'), values=('Matteo', '35'), ttl=123456,
                           timestamp=1626681089, not_exists=True)
        self.assertEqual(self.mysess.item_count, 1)

    def test_insert_many_data(self):
        values = [('Matteo', '35'), ('Arthur', '42')]
        self.mysess.insert_many('table', columns=('name', 'age'), values=values)
        self.assertEqual(self.mysess.item_count, 2)
        values = [(Varchar('Matteo'), Varint(35)), (Varchar('Arthur'), Varint(42))]
        name = Column('name', of_type=Varchar)
        age = Column('age', of_type=Varint)
        self.mysess.insert_many('table', columns=(name, age), values=values)
        self.assertEqual(self.mysess.item_count, 2)

    def test_insert_many_data_with_ttl(self):
        values = [('Matteo', '35'), ('Arthur', '42')]
        self.mysess.insert_many('table', columns=('name', 'age'), values=values, ttl=123456)
        self.assertEqual(self.mysess.item_count, 2)

    def test_insert_many_data_with_timestamp(self):
        values = [('Matteo', '35'), ('Arthur', '42')]
        self.mysess.insert_many('table', columns=('name', 'age'), values=values, ttl=123456, timestamp=1626681089)
        self.assertEqual(self.mysess.item_count, 2)
        values = [(Varchar('Matteo'), Varint(35)), (Varchar('Arthur'), Varint(42))]
        name = Column('name', of_type=Varchar)
        age = Column('age', of_type=Varint)
        self.mysess.insert_many('table', columns=(name, age), values=values, ttl=123456,
                                timestamp=Timestamp(2021, 8, 15))
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
        self.mysess.delete(Table('table'), ['name=Matteo'])
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

    def test_modify_password_user(self):
        resp = self.mysess.set_user('myrole', 'newpassword')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'PASSWORD_CHANGED')

    def test_delete_user(self):
        resp = self.mysess.delete_user('myrole')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'ROLE_DELETED')

    def test_add_index(self):
        resp = self.mysess.add_index('index_name', 'table', 'column')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'INDEX_CREATED')
        index = Index(name='index_name', table='table', column='column')
        resp = self.mysess.add_index(index)
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'INDEX_CREATED')


if __name__ == '__main__':
    unittest.main()
