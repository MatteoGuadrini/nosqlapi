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
    ret = docsession.insert('db1/doc1', '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}')
    assert docsession.item_count == 1
    assert isinstance(ret, (nosqlapi.Response, nosqlapi.DocResponse))
    assert ret.data == {'_id': '5099803df3f4948bd2f98391', 'revision': 1}
    # Document type: insert data into database db1: with ORM objects
    doc1 = nosqlapi.docdb.Document({"name": "Matteo", "age": 35})
    docsession.insert('db1/doc1', doc1)
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
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    colsession.delete(table='table1', conditions=['name=Matteo', 'id=1'])
    assert colsession.item_count == 1


def test_many_data_operation():
    """Test many inserts and many updates"""
    # Graph type: get data into from db1
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    ret = graphsession.insert_many(['matteo:Person', 'arthur:Person'],
                                   [{'name': 'Matteo', 'age': 35}, {'name': 'Arthur', 'age': 42}])
    assert graphsession.item_count == 2
    assert ret.data == [{'matteo.name': 'Matteo', 'matteo.age': 35}, {'arthur.name': 'Arthur', 'arthur.age': 42}]
    assert isinstance(ret, (nosqlapi.Response, nosqlapi.GraphResponse))
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    # Document type: update many data into database db1
    ret = docsession.update_many('db1',
                                 'name="Matteo"',
                                 '{"_id": "5099803df3f4948bd2f98391", "rev": 1, "name": "Matteo", "age": 35}',
                                 '{"_id": "5099803df3f4948bd2f98392", "rev": 1, "name": "Matteo", "age": 36}',
                                 '{"_id": "5099803df3f4948bd2f98393", "rev": 1, "name": "Matteo", "age": 37}')
    assert docsession.item_count == 3
    assert isinstance(ret, (nosqlapi.Response, nosqlapi.DocResponse))
    assert ret.data == {'insertedIds': ['5099803df3f4948bd2f98391',
                                        '5099803df3f4948bd2f98392',
                                        '5099803df3f4948bd2f98393']}


# ------------------Permissions------------------
def test_permission():
    """Test permission on database session"""
    # Column type: get permission after session
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    assert 'admin' in colsession.acl
    assert colsession.acl['admin'] == 'admins'
    # Document type: get permission after session
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    assert 'admin' == docsession.acl['user']
    assert docsession.acl['roles'] == ['administrator', 'all']
    # Graph type: get permission after session
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    assert 'admin' in graphsession.acl[0]
    assert graphsession.acl[0] == ['admin', 'GRANTED', 'access', 'database']
    # KeyValue type: get permission after session
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    assert 'admin' in kvsession.acl
    assert kvsession.acl['admin'] == 'admins'


def test_assign_permission():
    """Test assign permission to database"""
    # KeyValue type: create new user and grant database
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    new = kvsession.new_user('test', 'mypassword')
    grant = kvsession.grant('db1', user='test', role='read_users')
    assert isinstance(new, (nosqlapi.Response, nosqlapi.KVResponse))
    assert new['user'] == 'test'
    assert new['status'] == 'CREATION_OK'
    assert isinstance(grant, (nosqlapi.Response, nosqlapi.KVResponse))
    assert grant['role'] == 'read_users'
    assert grant['status'] == 'GRANT_OK'
    # Graph type: create new user and grant database
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    new = graphsession.new_user('test', 'mypassword')
    grant = graphsession.grant('db1', user='test', role='read_users')
    assert isinstance(new, (nosqlapi.Response, nosqlapi.GraphResponse))
    assert new.data == '0 rows, System updates: 1'
    assert isinstance(grant, (nosqlapi.Response, nosqlapi.GraphResponse))
    assert grant.data == '0 rows, System updates: 1'
    # Document type: create new user and grant database
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    new = docsession.new_user('test', 'mypassword')
    grant = docsession.grant('db1', user='test', role='read_users')
    assert isinstance(new, (nosqlapi.Response, nosqlapi.DocResponse))
    assert new['user'] == 'test'
    assert isinstance(grant, (nosqlapi.Response, nosqlapi.DocResponse))
    assert grant.code == 200
    # Column type: create new user and grant database
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    new = colsession.new_user('test', 'mypassword')
    grant = colsession.grant('db1', user='test', role='read_users')
    assert isinstance(new, (nosqlapi.Response, nosqlapi.ColumnResponse))
    assert new['role'] == 'test'
    assert new['status'] == 'CREATION_OK'
    assert isinstance(grant, (nosqlapi.Response, nosqlapi.ColumnResponse))
    assert grant['role'] == 'read_users'
    assert grant['status'] == 'GRANT_OK'


def test_revoke_permission():
    """Test revoke permission to database"""
    # KeyValue type: create new user and grant database
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    revoke = kvsession.revoke('db1', user='test', role='read_users')
    assert isinstance(revoke, (nosqlapi.Response, nosqlapi.KVResponse))
    assert revoke['status'] == 'REVOKE_OK'
    # Graph type: create new user and grant database
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    revoke = graphsession.revoke('db1', user='test', role='read_users')
    assert isinstance(revoke, (nosqlapi.Response, nosqlapi.GraphResponse))
    assert revoke.data == '0 rows, System updates: 1'
    # Document type: create new user and grant database
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    revoke = docsession.revoke('db1', role='read_users')
    assert isinstance(revoke, (nosqlapi.Response, nosqlapi.DocResponse))
    assert revoke.code == 200
    # Column type: create new user and grant database
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    revoke = colsession.revoke('db1', user='test', role='read_users')
    assert isinstance(revoke, (nosqlapi.Response, nosqlapi.ColumnResponse))
    assert revoke['status'] == 'REVOKE_OK'


if __name__ == '__main__':
    pytest.main()
