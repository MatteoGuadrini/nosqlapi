"""Real production test with pytest.

This test suites is based on simple implementations of library for all four type of databases.
"""

import pytest
import nosqlapi


# ------------------Common Task------------------
def connect(of_type, *args, **kwargs):
    """Return connection and session"""
    from .test_columndb import MyDBConnection as ColumnCon
    from .test_docdb import MyDBConnection as DocCon
    from .test_kvdb import MyDBConnection as KVCon
    from .test_graphdb import MyDBConnection as GraphCon
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
    # Column type: create Connection object
    connection, _ = connect('column', 'prod-db.test.com', 'admin', 'password', 'db_users')
    assert isinstance(connection, nosqlapi.Connection)
    assert isinstance(connection, nosqlapi.ColumnConnection)
    # Column type: connect to database via Connection object
    session = connection.connect()
    assert isinstance(session, nosqlapi.Session)
    assert isinstance(session, nosqlapi.ColumnSession)
    assert connection.connected is True
    assert session.database == 'db_users'
    assert session.connection is not None
    assert 'admin' in session.description
    # Column type: close Session...but not Connection!
    session.close()
    assert session.database is None
    assert session.connection is None
    # Column type: close also Connection
    connection.close()
    assert connection.connected is False
    # Column type: now, connect other database
    doccon, docses = connect('doc', 'prod-db.test.com', 'admin', 'password')
    kvcon, kvses = connect('kv', 'prod-db.test.com', 'admin', 'password')
    graphcon, graphses = connect('graph', 'prod-db.test.com', 'admin', 'password')
    for con in (doccon, kvcon, graphcon):
        assert isinstance(con, nosqlapi.Connection)
    for con in (docses, kvses, graphses):
        assert isinstance(con, nosqlapi.Session)


def test_create_database_and_table():
    """Test create database and table"""
    connection, session = connect('column', 'prod-db.test.com', 'admin', 'password')
    # Column type: make a new database
    connection.create_database("db1")
    assert connection.has_database("db1")
    assert "db1" in connection.databases()
    # Column type: new session with new database db1
    _, session_db1 = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    # Column type: create new table into database db1: without ORM objects
    session_db1.create_table('table1', columns=[('id', int), ('name', str), ('age', int)], primary_key='id')
    assert session_db1.item_count == 1
    # Column type: create new table into database db1: with ORM objects
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
    # Column type: new database for other databases
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
    """Test Create, Read, Update, Delete"""
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    # Document type: insert data into database db1: without ORM objects
    ret = docsession.insert('db/doc1', '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}')
    assert docsession.item_count == 1
    assert isinstance(ret, (nosqlapi.Response, nosqlapi.DocResponse))
    assert ret.data == {'_id': '5099803df3f4948bd2f98391', 'revision': 1}
    # Document type: insert data into database db1: with ORM objects
    doc1 = nosqlapi.docdb.Document({"name": "Matteo", "age": 35})
    docsession.insert('db/doc1', doc1)
    assert docsession.item_count == 1
    assert ret.data == {'_id': '5099803df3f4948bd2f98391', 'revision': 1}
    # Graph type: get data into from db1
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    ret = graphsession.get('n:Person')
    assert graphsession.item_count == 1
    assert ret.data == {'n.name': ['Matteo', 'Arthur'], 'n.age': [35, 42]}
    assert isinstance(ret, (nosqlapi.Response, nosqlapi.GraphResponse))
    # KeyValue type: update a record
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    kvsession.update('key', 'new-value')
    assert kvsession.item_count == 1
    # Column type: delete record with conditions
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password')
    colsession.delete(table='table1', conditions=['name=Matteo', 'id=1'])
    assert colsession.item_count == 1


if __name__ == '__main__':
    pytest.main()
