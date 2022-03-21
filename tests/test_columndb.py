import unittest
from typing import List
from typing import Union
from unittest import mock

import nosqlapi.columndb
from nosqlapi import (ConnectError, DatabaseError, DatabaseCreationError, DatabaseDeletionError, SessionError,
                      SessionInsertingError, SessionClosingError, SessionDeletingError,
                      SessionFindingError, SelectorAttributeError, SessionACLError)
from nosqlapi.columndb.orm import Keyspace, Table, Column, Index
from nosqlapi.common.orm import Varchar, Varint, Timestamp


# Below classes is a simple emulation of Cassandra like database


class MyDBConnection(nosqlapi.columndb.ColumnConnection):
    # Simulate socket.socket
    t = mock.Mock('AF_INET', 'SOCK_STREAM')
    t.connect = mock.MagicMock()
    t.send = mock.MagicMock()
    t.close = mock.MagicMock()

    def close(self):
        self.t.close()
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

    def create_database(self, name: Union[str, Keyspace], not_exists: bool = False, replication=None,
                        durable_writes=None):
        if self:
            if isinstance(name, Keyspace):
                name = name.name
            query = f"CREATE  KEYSPACE '{name}'"
            if not_exists:
                query += " IF NOT EXISTS"
            if replication:
                query += f" WITH REPLICATION = {replication}"
            if durable_writes is not None:
                query += f" AND DURABLE_WRITES = {str(bool(durable_writes)).lower()}"
            self.t.send(query)
            self.t.recv = mock.MagicMock(return_value='DB_CREATED')
            if self.t.recv(2048) != 'DB_CREATED':
                raise DatabaseCreationError(f'Database creation error: {self.t.recv(2048)}')
        else:
            raise ConnectError(f"Server isn't connected")

    def has_database(self, name: Union[str, Keyspace]):
        if self:
            if isinstance(name, Keyspace):
                name = name.name
            if name not in self.databases():
                return False
            else:
                return True
        else:
            raise ConnectError(f"Server isn't connected")

    def delete_database(self, name: Union[str, Keyspace], exists=False):
        if self:
            if isinstance(name, Keyspace):
                name = name.name
            query = f'DROP KEYSPACE'
            if exists:
                query += ' IF EXISTS'
            query += f' {name};'
            self.t.send(query)
            self.t.recv = mock.MagicMock(return_value='DB_DELETED')
            if self.t.recv(2048) != 'DB_DELETED':
                raise DatabaseDeletionError(f'Database deletion error: {self.t.recv(2048)}')
        else:
            raise ConnectError(f"Server isn't connected")

    def databases(self):
        if self:
            self.t.send(f"DESCRIBE KEYSPACES;")
            self.t.recv = mock.MagicMock(return_value='test_db db1 db2')
            if self.t.recv(2048) == 'DB_ERROR':
                raise DatabaseError(f'Request error: {self.t.recv(2048)}')
            return MyDBResponse(self.t.recv(2048).split())
        else:
            raise ConnectError(f"Server isn't connected")

    def show_database(self, name: Union[str, Keyspace]):
        if self:
            if isinstance(name, Keyspace):
                name = name.name
            self.t.send(f"DESCRIBE KEYSPACE {name};")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='table1 table2 table3')
            if self.t.recv(2048) == 'DB_ERROR':
                raise DatabaseError(f'Request error: {self.t.recv(2048)}')
            return MyDBResponse(self.t.recv(2048).split())
        else:
            raise ConnectError(f"Server isn't connected")


class MyDBSession(nosqlapi.columndb.ColumnSession):

    @property
    def acl(self):
        if not self.connection:
            raise ConnectError('connect to a database before request some ACLs')
        self.connection.send(f"LIST ALL PERMISSIONS OF {self.description[2]}")
        self.connection.recv = mock.MagicMock(return_value=f"test,user_read;admin,admins;root,admins")
        return MyDBResponse(
            data={item.split(',')[0]: item.split(',')[1]
                  for item in self.connection.recv(2048).split(';')}
        )

    @property
    def indexes(self):
        if not self.connection:
            raise ConnectError('connect to a database before request indexes')
        self.connection.send('SELECT * FROM "IndexInfo";')
        self.connection.recv = mock.MagicMock(return_value=f"index1,index2")
        return MyDBResponse(
            data=[item for item in self.connection.recv(2048).split(',')]
        )

    @property
    def item_count(self):
        return self._item_count

    @property
    def description(self):
        self.connection.recv = mock.MagicMock(return_value="server=mycolumndb.local\nport=12345\ndatabase=test_db"
                                                           "\nusername=admin")
        self._description = tuple([item.split('=')[1]
                                   for item in self.connection.recv(2048).split('\n')])
        return self._description

    def get(self, table: Union[str, Table], *columns: Union[str, Column]):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        cols = []
        for column in columns:
            if isinstance(column, Column):
                cols.append(column.name)
            else:
                cols.append(column)
        self.connection.send(f"SELECT {','.join(col for col in cols)} FROM {table}")
        self.connection.recv = mock.MagicMock(return_value="name,age\nname1,age1\nname2,age2")
        if self.connection.recv != 'NOT_FOUND':
            out = [tuple(row.split(','))
                   for row in self.connection.recv(2048).split('\n')]
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
        if not self.connection:
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
        self.connection.send(query)
        self.connection.recv = mock.MagicMock(return_value="INSERT_OK")
        if self.connection.recv(2048) != "INSERT_OK":
            raise SessionInsertingError(
                f'insert into {columns} with value {values} failure: {self.connection.recv(2048)}')
        self._item_count = 1

    def insert_many(self,
                    table: Union[str, Table],
                    columns: tuple,
                    values: List[tuple],
                    ttl=None,
                    timestamp: Union[int, Timestamp] = None,
                    not_exists: bool = False):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        query = ["BEGIN BATCH"]
        for value in values:
            cols = []
            for column in columns:
                if isinstance(column, Column):
                    cols.append(column.name)
                else:
                    cols.append(column)
            columns = tuple(cols)
            query.append(f"INSERT INTO {table} {columns} VALUES {value}")
            if ttl and isinstance(ttl, int):
                query.append(f'USING TTL {ttl}')
            if timestamp and ttl and isinstance(timestamp, int):
                query.append(f'AND TIMESTAMP {timestamp}')
            if bool(not_exists):
                query.append(f'IF NOT EXISTS')
            query.append(';')
        query.append('APPLY BATCH;')
        batch = MyDBBatch(query, self)
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
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        query = f"DELETE FROM {table} WHERE {' AND '.join(condition for condition in conditions)}"
        if bool(exists):
            query += f'\nIF EXISTS'
        query += ';'
        self.connection.send(query)
        self.connection.recv = mock.MagicMock(return_value="DELETION:1")
        if "DELETION" not in self.connection.recv(2048):
            raise SessionDeletingError(f'deleting from {table} failure: {self.connection.recv(2048)}')
        self._item_count = int(self.connection.recv(2048).split(':')[1])

    def close(self):
        self._connection = None
        if not self.connection:
            SessionClosingError('session was not closed')
        self._database = None

    def find(self, selector: Union[str, nosqlapi.columndb.ColumnSelector]):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(selector, nosqlapi.columndb.ColumnSelector):
            self.connection.send(selector.build())
            self.connection.recv = mock.MagicMock(return_value="name,age\nname1,age1\nname2,age2")
        elif isinstance(selector, str):
            self.connection.send(selector)
            self.connection.recv = mock.MagicMock(return_value="name,age\nname1,age1\nname2,age2")
        else:
            raise SessionFindingError('selector is incompatible')
        out = [tuple(row.split(','))
               for row in self.connection.recv(2048).split('\n')]
        self._item_count = len(out)
        return MyDBResponse(out)

    def grant(self, database, user, role):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"GRANT {user} ON {database} TO {role};")
        self.connection.recv = mock.MagicMock(return_value="GRANT_OK")
        if self.connection.recv(2048) != "GRANT_OK":
            raise SessionACLError(f'grant {user} with role {role} on {database} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'user': user, 'role': role, 'db': database, 'status': "GRANT_OK"})

    def revoke(self, database, user, role=None):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"REVOKE {user} ON {database} TO {role};")
        self.connection.recv = mock.MagicMock(return_value="REVOKE_OK")
        if self.connection.recv(2048) != "REVOKE_OK":
            raise SessionACLError(f'revoke {user} with role {role} on {database} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'user': user, 'role': role, 'db': database, 'status': "REVOKE_OK"})

    def new_user(self, role, password, login=True, super_user=False):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"CREATE ROLE {role} WITH PASSWORD = {password} "
                             f"AND SUPERUSER = {super_user} AND LOGIN = {login};")
        self.connection.recv = mock.MagicMock(return_value="CREATION_OK")
        if self.connection.recv(2048) != "CREATION_OK":
            raise SessionACLError(f'create role {role} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'role': role, 'status': self.connection.recv(2048)})

    def set_user(self, role, password):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"ALTER ROLE {role} WITH PASSWORD = {password}")
        self.connection.recv = mock.MagicMock(return_value="PASSWORD_CHANGED")
        if self.connection.recv(2048) != "PASSWORD_CHANGED":
            raise SessionACLError(f'create role {role} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'role': role, 'status': self.connection.recv(2048)})

    def delete_user(self, role):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        self.connection.send(f"DROP ROLE {role}")
        self.connection.recv = mock.MagicMock(return_value="ROLE_DELETED")
        if self.connection.recv(2048) != "ROLE_DELETED":
            raise SessionACLError(f'create role {role} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'role': role, 'status': self.connection.recv(2048)})

    def add_index(self, name: Union[str, Index], table=None, column=None):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(name, Index):
            column = name.column
            table = name.table
            name = name.name
        if table is None and column is None:
            raise SessionInsertingError('table name and column name is mandatory to create an index.')
        self.connection.send(f"CREATE INDEX {name} ON {table} ({column});")
        self.connection.recv = mock.MagicMock(return_value="INDEX_CREATED")
        if self.connection.recv(2048) != "INDEX_CREATED":
            raise SessionACLError(f'create index {name} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'index': name, 'status': self.connection.recv(2048)})

    def delete_index(self, name: Union[str, Index]):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(name, Index):
            name = name.name
        self.connection.send(f"DROP INDEX IF EXISTS {self.database}.{name};")
        self.connection.recv = mock.MagicMock(return_value="INDEX_DELETED")
        if self.connection.recv(2048) != "INDEX_DELETED":
            raise SessionACLError(f'create index {name} failed: {self.connection.recv(2048)}')
        return MyDBResponse({'index': name, 'status': self.connection.recv(2048)})

    def compact(self, table: Union[str, Table], strategy):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        compaction_strategy = ('TimeWindowCompactionStrategy',
                               'SizeTieredCompactionStrategy',
                               'LeveledCompactionStrategy')
        if strategy not in compaction_strategy:
            raise ValueError(f'{strategy} is not a compaction strategy!')
        query = f"ALTER TABLE {table} WITH compaction = {{ 'class' : '{strategy}' }}"
        self.connection.send(query)
        self.connection.recv = mock.MagicMock(return_value="COMPACT:1")
        if "COMPACT" not in self.connection.recv(2048):
            raise SessionError(f'compact {table} failure: {self.connection.recv(2048)}')
        self._item_count = int(self.connection.recv(2048).split(':')[1])

    def alter_table(self, table: Union[str, Table], add_columns=None, drop_columns=None, properties=None):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        query = f"ALTER TABLE {self.database}.{table}\n"
        if not add_columns and not drop_columns and not properties:
            raise ValueError('populate one of these args: add_columns, drop_columns or properties')
        if add_columns:
            query += f"ADD {add_columns}\n"
        if drop_columns:
            query += f"DROP {drop_columns}\n"
        if properties:
            query += f"WITH {properties}"
        self.connection.send(query)
        self.connection.recv = mock.MagicMock(return_value="ALTER_TABLE:1")
        if "ALTER_TABLE" not in self.connection.recv(2048):
            raise SessionError(f'alter table {table} failure: {self.connection.recv(2048)}')
        self._item_count = int(self.connection.recv(2048).split(':')[1])

    def create_table(self, table: Union[str, Table], columns: Union[List[tuple], List[Column]] = None, primary_key=None,
                     not_exists=True):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        query = f"CREATE TABLE {'IF NOT EXISTS' if not_exists else ''} {self.database}.{table} (\n"
        if columns:
            form = []
            for column in columns:
                if isinstance(column, Column):
                    form += f'{column.name} {column.of_type}'
                else:
                    form += f'{column[0]} {column[1]}'
            query += ',\n'.join(form)
        if primary_key:
            query += f"PRIMARY KEY (\n"
            form = []
            for column in primary_key:
                if isinstance(column, Column):
                    form += f'{column.name}'
                else:
                    form += f'{column}'
            query += ','.join(form) + f")"
        query += ')'
        self.connection.send(query)
        self.connection.recv = mock.MagicMock(return_value="CREATE_TABLE:1")
        if "CREATE_TABLE" not in self.connection.recv(2048):
            raise SessionError(f'create table {table} failure: {self.connection.recv(2048)}')
        self._item_count = int(self.connection.recv(2048).split(':')[1])

    def delete_table(self, table: Union[str, Table], exists=True):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        query = f"CREATE TABLE {'IF EXISTS' if exists else ''} {self.database}.{table}"
        self.connection.send(query)
        self.connection.recv = mock.MagicMock(return_value="DROP_TABLE:1")
        if "DROP_TABLE" not in self.connection.recv(2048):
            raise SessionError(f'delete table {table} failure: {self.connection.recv(2048)}')
        self._item_count = int(self.connection.recv(2048).split(':')[1])

    def truncate(self, table: Union[str, Table]):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(table, Table):
            table = table.name
        query = f"TRUNCATE {self.database}.{table}"
        self.connection.send(query)
        self.connection.recv = mock.MagicMock(return_value="TRUNCATE:1")
        if "TRUNCATE" not in self.connection.recv(2048):
            raise SessionError(f'delete table {table} failure: {self.connection.recv(2048)}')
        self._item_count = int(self.connection.recv(2048).split(':')[1])


class MyDBResponse(nosqlapi.columndb.ColumnResponse):
    pass


class MyDBBatch(nosqlapi.columndb.ColumnBatch):
    # Simulate socket.socket
    t = mock.Mock('AF_INET', 'SOCK_STREAM')
    t.send = mock.MagicMock()

    def execute(self):
        self.t.send('\n'.join(self.batch))
        self.t.recv = mock.MagicMock(return_value="BATCH_OK")
        if self.t.recv(2048) != "BATCH_OK":
            raise SessionError(f'batch error: {self.t.recv(2048)}')
        return MyDBResponse(self.t.recv(2048))


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
        myconn = MyDBConnection('mycolumndb.local', port=12345, user='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertTrue(myconn)

    def test_columndb_close(self):
        myconn = MyDBConnection('mycolumndb.local', port=12345, user='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertTrue(myconn)
        myconn.close()
        self.assertFalse(myconn)

    def test_columndb_create_database(self):
        myconn = MyDBConnection('mycolumndb.local', port=12345, user='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertTrue(myconn)
        myconn.create_database('test_db')
        myconn.create_database(Keyspace('test_db'))
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_columndb_exists_database(self):
        myconn = MyDBConnection('mycolumndb.local', port=12345, user='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertTrue(myconn)
        self.assertTrue(myconn.has_database('test_db'))
        self.assertTrue(myconn.has_database(Keyspace('test_db')))
        self.assertFalse(myconn.has_database('casual'))
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.has_database, 'test_db')

    def test_columndb_delete_database(self):
        myconn = MyDBConnection('mycolumndb.local', port=12345, user='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertTrue(myconn)
        myconn.delete_database('test_db')
        myconn.delete_database(Keyspace('test_db'))
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.delete_database, 'test_db')

    def test_columndb_get_all_database(self):
        myconn = MyDBConnection('mycolumndb.local', port=12345, user='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertTrue(myconn)
        dbs = myconn.databases()
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['test_db', 'db1', 'db2'])
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.databases)

    def test_columndb_show_database(self):
        myconn = MyDBConnection('mycolumndb.local', port=12345, user='admin', password='pass', database='test_db')
        myconn.connect()
        self.assertTrue(myconn)
        dbs = myconn.show_database('test_db')
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['table1', 'table2', 'table3'])
        dbs = myconn.show_database(Keyspace('test_db'))
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['table1', 'table2', 'table3'])
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.databases)


class ColumnSessionTest(unittest.TestCase):
    myconn = MyDBConnection('mycolumndb.local', port=12345, user='admin', password='pass', database='test_db')
    mysess = myconn.connect()

    def test_session_instance(self):
        self.assertIsInstance(self.mysess, MyDBSession)

    def test_description_session(self):
        self.assertEqual(self.mysess.description, ('mycolumndb.local', '12345', 'test_db', 'admin'))

    def test_get_column(self):
        d = self.mysess.get('table', 'name', 'age')
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn(('name', 'age'), d)
        d = self.mysess.get(Table('table'), Column('name'), Column('age'))
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn(('name', 'age'), d)

    def test_create_table(self):
        self.mysess.create_table('table', columns=[('name', 'Varchar'), ('age', 'Varint')], primary_key=('name',))
        self.assertEqual(self.mysess.item_count, 1)
        name = Column('name', of_type=Varchar)
        age = Column('age', of_type=Varint)
        self.mysess.create_table('table', columns=[name, age], primary_key=('name',))
        self.assertEqual(self.mysess.item_count, 1)

    def test_delete_table(self):
        self.mysess.delete_table('table')
        self.assertEqual(self.mysess.item_count, 1)
        self.mysess.delete_table(Table('table'))
        self.assertEqual(self.mysess.item_count, 1)

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
        self.assertEqual(self.mysess.database, None)
        ColumnSessionTest.mysess = ColumnSessionTest.myconn.connect()

    def test_batch(self):
        query = ['BEGIN BATCH', "UPDATE table SET name = 'Arthur' WHERE name=Matteo AND age=35;", "APPLY BATCH ;"]
        batch = MyDBBatch(query, self.mysess)
        batch.execute()

    def test_call_batch(self):
        query = ['BEGIN BATCH', "UPDATE table SET name = 'Arthur' WHERE name=Matteo AND age=35;", "APPLY BATCH ;"]
        batch = MyDBBatch(query, self.mysess)
        self.mysess.call(batch)

    def test_batch_add_remove_modify(self):
        query = ['BEGIN BATCH', "UPDATE table SET name = 'Arthur' WHERE name=Matteo AND age=35;"]
        batch = MyDBBatch(query, self.mysess)
        # Add element
        batch.batch.append("APPLY BATCH ;")
        self.assertEqual(len(batch.batch), 3)
        # Modify element
        batch.batch[1] = "UPDATE table SET name = 'Matteo' WHERE name=Matteo AND age=35;"
        self.assertEqual(batch.batch[1], "UPDATE table SET name = 'Matteo' WHERE name=Matteo AND age=35;")
        # Delete element
        batch.batch.append("UNUSEFUL;")
        self.assertEqual(len(batch.batch), 4)
        del batch.batch[-1]
        self.assertEqual(len(batch.batch), 3)
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

    def test_delete_index(self):
        resp = self.mysess.delete_index('index_name')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'INDEX_DELETED')
        index = Index(name='index_name', table='table', column='column')
        resp = self.mysess.delete_index(index)
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['status'], 'INDEX_DELETED')

    def test_get_indexes(self):
        self.assertIn('index1', self.mysess.indexes)
        self.assertIn('index2', self.mysess.indexes)

    def test_compact_table(self):
        self.mysess.compact('table', 'TimeWindowCompactionStrategy')
        self.assertEqual(self.mysess.item_count, 1)
        self.mysess.compact(Table('table'), 'TimeWindowCompactionStrategy')
        self.assertEqual(self.mysess.item_count, 1)
        self.assertRaises(ValueError, self.mysess.compact, 'table', 'OtherCompactionStrategy')

    def test_alter_table(self):
        self.mysess.alter_table('table', add_columns=['col1', 'col2'], drop_columns=['col6'])
        self.assertEqual(self.mysess.item_count, 1)
        self.mysess.alter_table(Table('table'), add_columns=['col1', 'col2'], drop_columns=['col6'])
        self.assertEqual(self.mysess.item_count, 1)
        self.assertRaises(ValueError, self.mysess.alter_table, 'table')

    def test_truncate_table(self):
        self.mysess.truncate('table')
        self.assertEqual(self.mysess.item_count, 1)
        self.mysess.truncate(Table('table'))
        self.assertEqual(self.mysess.item_count, 1)

    def test_column_decorator(self):
        # Simple function
        @nosqlapi.columndb.column
        def ids(start=0, end=10):
            return list(range(start, end))

        col = ids()
        self.assertIsInstance(col, Column)
        col2 = ids(2, 20)
        self.assertIsInstance(col2, Column)
        self.assertEqual(col2[0], 2)


if __name__ == '__main__':
    unittest.main()
