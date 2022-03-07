"""Real production test with pytest.

This test suites is based on simple implementations of library for all four type of databases.
"""

import pytest
import nosqlapi
from .test_columndb import MyDBConnection as ColumnCon, MyDBSession as ColumnSes
from .test_docdb import MyDBConnection as DocCon
from .test_kvdb import MyDBConnection as KVCon
from .test_graphdb import MyDBConnection as GraphCon


# ------------------Common Task------------------
def connect(of_type, *args, **kwargs):
    """Return connection and session"""
    db_type = {
        'column': ColumnCon,
        'doc': DocCon,
        'kv': KVCon,
        'graph': GraphCon
    }
    connection = db_type[of_type](*args, **kwargs)
    session = connection.connect()
    return connection, session


def test_connect_database():
    """Test connection on production Cassandra database"""
    # Create Connection object
    connection, _ = connect('column', 'prod-db.test.com', 'admin', 'password', 'db_users')
    assert isinstance(connection, nosqlapi.Connection)
    assert isinstance(connection, nosqlapi.ColumnConnection)
    assert isinstance(connection, ColumnCon)
    # Connect to database via Connection object
    session = connection.connect()
    assert isinstance(session, nosqlapi.Session)
    assert isinstance(session, nosqlapi.ColumnSession)
    assert isinstance(session, ColumnSes)
    assert connection.connected is True
    assert session.database == 'db_users'
    assert session.connection is not None
    assert 'admin' in session.description
    # Close Session...but not Connection!
    session.close()
    assert session.database is None
    assert session.connection is None
    # Close also Connection
    connection.close()
    assert connection.connected is False
    # Now, connect other database
    doccon, docses = connect('doc', 'prod-db.test.com', 'admin', 'password')
    kvcon, kvses = connect('kv', 'prod-db.test.com', 'admin', 'password')
    graphcon, graphses = connect('graph', 'prod-db.test.com', 'admin', 'password')
    for con in (doccon, kvcon, graphcon):
        assert isinstance(con, nosqlapi.Connection)
    for con in (docses, kvses, graphses):
        assert isinstance(con, nosqlapi.Session)


def test_create_database_and_table():
    """Test create database and table"""
    connection, session = connect('column', 'mycolumndb.local', 'admin', 'password')
    # Make a new database
    connection.create_database("db1")
    assert connection.has_database("db1")
    assert "db1" in connection.databases()
    # New session with new database db1
    _, session_db1 = connect('column', 'mycolumndb.local', 'admin', 'password', 'db1')
    # Create new table into database db1: without ORM objects
    session_db1.create_table('table1', columns=[('id', int), ('name', str), ('age', int)], primary_key='id')
    assert session_db1.item_count == 1
    # Create new table into database db1: with ORM objects
    ids = nosqlapi.columndb.Column('id', of_type=nosqlapi.Varint, primary_key=True)
    assert isinstance(ids, nosqlapi.columndb.Column)
    assert issubclass(ids.of_type, (int, nosqlapi.Int, nosqlapi.Varint))
    assert ids.primary_key
    name = nosqlapi.columndb.Column('name', of_type=nosqlapi.Varchar)
    age = nosqlapi.columndb.Column('age', of_type=nosqlapi.Varint)
    table = nosqlapi.columndb.Table('table1')
    table.primary_key = ids.name
    session_db1.create_table('table1',
                             columns=[ids, name, age],
                             primary_key='id',
                             not_exists=False)
    assert session_db1.item_count == 1
    # New database for other databases
    doccon, _ = connect('doc', 'prod-db.test.com', 'admin', 'password')
    kvcon, _ = connect('kv', 'prod-db.test.com', 'admin', 'password')
    graphcon, _ = connect('graph', 'prod-db.test.com', 'admin', 'password')
    doccon.create_database("db1")
    assert doccon.has_database("db1")
    assert "db1" in doccon.databases()
    kvcon.create_database("db1")
    assert kvcon.has_database("db1")
    assert "db1" in kvcon.databases()
    graphcon.create_database("db1")
    assert graphcon.has_database("db1")
    assert "db1" in graphcon.databases()


def test_crud():
    """Test crud"""
    _, session = connect('column', 'mycolumndb.local', 'admin', 'password', 'db1')
    # Insert data into table table1 on database db1: without ORM objects
    session.insert('table1', columns=('name', 'age'), values=('Matteo', '35'))
    assert session.item_count == 1
    # Insert data into table table1 on database db1: with ORM objects
    name = nosqlapi.columndb.Column('name', of_type=nosqlapi.Varchar)
    age = nosqlapi.columndb.Column('age', of_type=nosqlapi.Varint)
    session.insert('table1', columns=(name, age), values=(nosqlapi.Varchar('Matteo'), nosqlapi.Varint(35)))
    assert session.item_count == 1
    # Insert many data into table table1 on database db1: without ORM objects
    values = [('Matteo', '35'), ('Arthur', '42')]
    session.insert('table1', columns=('name', 'age'), values=values)
    assert session.item_count == 1
    # Insert many data into table table1 on database db1: with ORM objects
    values = [(nosqlapi.Varchar('Matteo'), nosqlapi.Varint(35)), (nosqlapi.Varchar('Arthur'), nosqlapi.Varint(42))]
    name = nosqlapi.columndb.Column('name', of_type=nosqlapi.Varchar)
    age = nosqlapi.columndb.Column('age', of_type=nosqlapi.Varint)
    session.insert('table1', columns=(name, age), values=values)
    assert session.item_count == 1


if __name__ == '__main__':
    pytest.main()
