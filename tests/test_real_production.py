"""Real production test with pytest."""

import pytest
import nosqlapi


# ------------------Cassandra------------------
def connect(*args, **kwargs):
    """Return connection and session"""
    from .test_columndb import MyDBConnection as CassandraCon
    connection = CassandraCon(*args, **kwargs)
    session = connection.connect()
    return connection, session


def test_cassandra_connect_database():
    """Test connection on production Cassandra database"""
    from .test_columndb import (MyDBConnection as CassandraCon,
                                MyDBSession as CassandraSess)
    # Create Connection object
    connection = CassandraCon('prod-db.test.com', 'admin', 'password', 'db_users')
    assert isinstance(connection, nosqlapi.Connection)
    assert isinstance(connection, nosqlapi.ColumnConnection)
    assert isinstance(connection, CassandraCon)
    assert connection.connected is False
    # Connect to database via Connection object
    session = connection.connect()
    assert isinstance(session, nosqlapi.Session)
    assert isinstance(session, nosqlapi.ColumnSession)
    assert isinstance(session, CassandraSess)
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
    return connection, session


def test_cassandra_create_database_and_table():
    """Test create database and table"""
    connection, session = connect('mycolumndb.local', 'admin', 'password')
    # Make a new database
    connection.create_database("db1")
    assert connection.has_database("db1")
    assert "db1" in connection.databases()
    # New session with new database db1
    _, session_db1 = connect('mycolumndb.local', 'admin', 'password', 'db1')
    # Create new table into database db1: without ORM objects
    session_db1.create_table('table1', columns=[('id', int), ('name', str), ('age', int)], primary_key='id')
    assert session_db1.item_count == 1
    # Create new table into database db1: with ORM objects
    ids = nosqlapi.columndb.Column('id', of_type=nosqlapi.Varint, primary_key=True)
    assert isinstance(ids, nosqlapi.columndb.Column)
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


if __name__ == '__main__':
    pytest.main()
