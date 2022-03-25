"""Real production test with pytest.

This test suites is based on simple implementations of library for all four type of databases.
"""
import sys
import pytest
import asyncio
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


def test_table_operations():
    """Test change/delete table for column database"""
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    # Column type: alter table table1
    colsession.alter_table('table1', add_columns=['first_name', 'last_name'], drop_columns=['name'])
    assert colsession.item_count == 1
    # Column type: compact table table1
    colsession.compact('table1', 'TimeWindowCompactionStrategy')
    assert colsession.item_count == 1
    # Column type: truncate table table1
    colsession.truncate('table1')
    assert colsession.item_count == 1
    # Column type: delete table table1
    colsession.delete_table('table1')
    assert colsession.item_count == 1


def test_delete_database():
    """Test delete database"""
    # KeyValue type: find a database
    kvconnection, _ = connect('kv', 'prod-db.test.com', 'admin', 'password')
    deleted = kvconnection.delete_database('test_db')
    assert bool(deleted) is True
    # Column type: find a database
    colconnection, _ = connect('column', 'prod-db.test.com', 'admin', 'password')
    deleted = colconnection.delete_database('test_db')
    assert bool(deleted) is True
    # Document type: find a database
    docconnection, _ = connect('doc', 'prod-db.test.com', 'admin', 'password')
    deleted = docconnection.delete_database('test_db')
    assert bool(deleted) is True
    # Graph type: find a database
    graphconnection, _ = connect('doc', 'prod-db.test.com', 'admin', 'password')
    deleted = graphconnection.delete_database('test_db')
    assert bool(deleted) is True


def test_copy_database():
    """Test copy database"""
    # Document type: find a database
    docconnection, _ = connect('doc', 'prod-db.test.com', 'admin', 'password')
    copied = docconnection.copy_database('db2', 'db3')
    assert copied['result'] == 'ok'


def test_context_manager():
    """Test Connection and Session object with context manager"""
    # KeyValue type: use like a context manager
    kvconnection, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    with kvconnection as conn:
        databases = conn.databases()
        assert databases.data == ['test_db', 'db1', 'db2']
    with kvsession as sess:
        indexes = sess.indexes
        assert 'index1' in indexes
    # Column type: use like a context manager
    colconnection, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    with colconnection as conn:
        databases = conn.databases()
        assert databases.data == ['test_db', 'db1', 'db2']
    with colsession as sess:
        indexes = sess.indexes
        assert 'index1' in indexes
    # Document type: use like a context manager
    docconnection, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    with docconnection as conn:
        databases = conn.databases()
        assert databases.data == ['test_db', 'db1', 'db2']
    with docsession as sess:
        indexes = sess.indexes
        assert 'index1' == indexes[0]['name']
    # Graph type: use like a context manager
    graphconnection, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    with graphconnection as conn:
        databases = conn.databases()
        assert databases.data == ['test_db', 'db1', 'db2']
    with graphsession as sess:
        indexes = sess.indexes
        assert 'index1' in indexes


def test_work_with_node():
    """Test link and detach node"""
    # Graph type: use like a context manager
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    with graphsession as sess:
        linked = sess.link(node='matteo:Person', linking_node='open_source:JOB', rel=':WORK_IN')
        assert linked.data == {'linked': True}
        detached = sess.detach(node=':Person', properties={'name': 'Matteo'})
        assert detached.data == {'detached': True}


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
    # KeyValue type: revoke access on database
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    revoke = kvsession.revoke('db1', user='test', role='read_users')
    assert isinstance(revoke, (nosqlapi.Response, nosqlapi.KVResponse))
    assert revoke['status'] == 'REVOKE_OK'
    # Graph type: revoke access on database
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    revoke = graphsession.revoke('db1', user='test', role='read_users')
    assert isinstance(revoke, (nosqlapi.Response, nosqlapi.GraphResponse))
    assert revoke.data == '0 rows, System updates: 1'
    # Document type: revoke access on database
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    revoke = docsession.revoke('db1', role='read_users')
    assert isinstance(revoke, (nosqlapi.Response, nosqlapi.DocResponse))
    assert revoke.code == 200
    # Column type: revoke access on database
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    revoke = colsession.revoke('db1', user='test', role='read_users')
    assert isinstance(revoke, (nosqlapi.Response, nosqlapi.ColumnResponse))
    assert revoke['status'] == 'REVOKE_OK'


def test_reset_password():
    """Test reset password for existing user"""
    # KeyValue type: create new user and grant database
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    reset = kvsession.set_user('test', 'newpassword')
    assert isinstance(reset, (nosqlapi.Response, nosqlapi.KVResponse))
    assert reset['user'] == 'test'
    assert reset['status'] == 'PASSWORD_CHANGED'
    # Graph type: create new user and grant database
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    reset = graphsession.set_user('test', 'newpassword')
    assert isinstance(reset, (nosqlapi.Response, nosqlapi.GraphResponse))
    assert reset.data == '0 rows, System updates: 1'
    # Document type: create new user and grant database
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    reset = docsession.set_user('test', 'newpassword')
    assert isinstance(reset, (nosqlapi.Response, nosqlapi.DocResponse))
    assert reset['user'] == 'test'
    # Column type: create new user and grant database
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    reset = colsession.set_user('test', 'newpassword')
    assert isinstance(reset, (nosqlapi.Response, nosqlapi.ColumnResponse))
    assert reset['role'] == 'test'
    assert reset['status'] == 'PASSWORD_CHANGED'


# ------------------Read Operation------------------
def test_read_databases():
    """Test read and find a database"""
    # KeyValue type: find a database
    kvconnection, _ = connect('kv', 'prod-db.test.com', 'admin', 'password')
    databases = kvconnection.databases()
    assert databases.data == ['test_db', 'db1', 'db2']
    assert kvconnection.has_database('db1') is True
    db = kvconnection.show_database('test_db')
    assert db.data == 'name=test_db, size=0.4GB'
    # Column type: find a database
    colconnection, _ = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    databases = colconnection.databases()
    assert databases.data == ['test_db', 'db1', 'db2']
    assert colconnection.has_database('db1') is True
    db = colconnection.show_database('test_db')
    assert db.data == ['table1', 'table2', 'table3']
    # Document type: find a database
    docconnection, _ = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    databases = docconnection.databases()
    assert databases.data == ['test_db', 'db1', 'db2']
    assert docconnection.has_database('db1') is True
    db = docconnection.show_database('test_db')
    assert db.data == {'name': 'test_db', 'size': '0.4GB'}
    # Graph type: find a database
    graphconnection, _ = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    databases = graphconnection.databases()
    assert databases.data == ['test_db', 'db1', 'db2']
    assert graphconnection.has_database('db1') is True
    db = graphconnection.show_database('test_db')
    assert db.data == {'name': 'test_db', 'size': '0.4GB'}


def test_find_data():
    """Test find data into a database"""
    from .test_kvdb import MyDBSelector as KVSelector
    from .test_columndb import MyDBSelector as ColSelector
    from .test_docdb import MyDBSelector as DocSelector
    from .test_graphdb import MyDBSelector as GraphSelector
    # Column type: find data with string
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    data = colsession.find('SELECT * from table1;')
    assert isinstance(data, (nosqlapi.Response, nosqlapi.ColumnResponse))
    assert data[0] == ('name', 'age')
    # Column type: find data with Selector object
    sel = ColSelector(selector='table1', fields=('name', 'age'))
    assert isinstance(sel, (nosqlapi.Selector, nosqlapi.ColumnSelector))
    assert sel.build() == "SELECT name,age FROM table1;"
    data = colsession.find(sel)
    assert data[1] == ('name1', 'age1')
    # KeyValue type: find data with string
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    data = kvsession.find('{selector=$like:key*}')
    assert isinstance(data, (nosqlapi.Response, nosqlapi.KVResponse))
    assert data['key'] == 'value'
    # KeyValue type: find data with Selector object
    sel = KVSelector(selector='$eq:key', limit=2)
    assert isinstance(sel, (nosqlapi.Selector, nosqlapi.KVSelector))
    assert sel.build() == '\n{selector={$eq:key}\nlimit=2}'
    data = kvsession.find(sel)
    assert data['key1'] == 'value1'
    # Document type: find data with string
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    data = docsession.find('{"name": "Matteo"}')
    assert isinstance(data, (nosqlapi.Response, nosqlapi.DocResponse))
    assert data['_id'] == '5099803df3f4948bd2f98391'
    # Document type: find data with Selector object
    sel = DocSelector(selector={"name": "Matteo"}, limit=2)
    assert isinstance(sel, (nosqlapi.Selector, nosqlapi.DocSelector))
    assert sel.build() == '{"selector": {"name": "Matteo"}, "limit": 2}'
    data = docsession.find(sel)
    assert data['name'] == 'Matteo'
    # Graph type: find data with string
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    data = graphsession.find('MATCH (people:Person) WHERE people.age>=35 ORDER BY age DESC LIMIT 2 RETURN '
                             'people.name,people.age')
    assert isinstance(data, (nosqlapi.Response, nosqlapi.GraphResponse))
    assert data[0]['matteo.name'] == 'Matteo'
    # Graph type: find data with Selector object
    sel = GraphSelector(selector='people:Person', condition='people.age>=35', order='age',
                        fields=['name', 'age'], limit=2)
    assert isinstance(sel, (nosqlapi.Selector, nosqlapi.GraphSelector))
    assert sel.build().split() == ['MATCH', '(people:Person)', 'WHERE', 'people.age>=35', 'ORDER', 'BY', 'age', 'DESC',
                                   'LIMIT', '2', 'RETURN', 'people.name,people.age']
    data = graphsession.find(sel)
    assert data[0]['matteo.age'] == 35


# ------------------Indexing------------------
def test_new_index():
    """Test create new index and assign it"""
    # Column type: create new index without ORM object
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    idx = colsession.add_index('index1', 'table1', 'name')
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.ColumnResponse))
    assert idx['index'] == 'index1'
    assert idx['status'] == 'INDEX_CREATED'
    # Column type: create new index with ORM object
    index = nosqlapi.columndb.Index(name='index1', table='table1', column='name')
    idx = colsession.add_index(index)
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.ColumnResponse))
    assert idx['index'] == 'index1'
    assert idx['status'] == 'INDEX_CREATED'
    # KeyValue type: create new index without ORM object
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    idx = kvsession.add_index('index1', 'name')
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.KVResponse))
    assert idx.data == 'index1'
    # KeyValue type: create new index with ORM object
    index = nosqlapi.kvdb.Index(name='index1', key='name')
    idx = kvsession.add_index(index)
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.KVResponse))
    assert idx.data == 'index1'
    # Document type: create new index without ORM object
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    idx = docsession.add_index('index1', {'age': 35, 'category': 1})
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.DocResponse))
    assert idx.code == 200
    assert idx['result'] == 'ok'
    # Document type: create new index with ORM object
    index = nosqlapi.docdb.Index(name='index1', data={'age': 35, 'category': 1})
    idx = docsession.add_index(index)
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.DocResponse))
    assert idx.code == 200
    assert idx['result'] == 'ok'
    # Graph type: create new index without ORM object
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    idx = graphsession.add_index('index1', 'n:Person', ['n.name', 'n.age'], {'option': 'value'})
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.GraphResponse))
    assert idx.data == '0 rows, System updates: 1'
    # Graph type: create new index with ORM object
    index = nosqlapi.graphdb.Index(name='index1',
                                   node='n:Person',
                                   properties=['n.name', 'n.age'],
                                   options={'option': 'value'})
    idx = graphsession.add_index(index)
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.GraphResponse))
    assert idx.data == '0 rows, System updates: 1'


def test_get_index():
    """Test get exists index"""
    # Column type: view indexes
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    indexes = colsession.indexes
    assert 'index1' in indexes
    # KeyValue type: view indexes
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    indexes = kvsession.indexes
    assert 'index1' in indexes
    # Document type: view indexes
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    indexes = docsession.indexes
    assert 'index1' == indexes[0]['name']
    # Graph type: view indexes
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    indexes = graphsession.indexes
    assert 'index1' in indexes


def test_delete_index():
    """Test delete specific index"""
    # Column type: delete new index
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    idx = colsession.delete_index('index1')
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.ColumnResponse))
    assert idx['status'] == 'INDEX_DELETED'
    # KeyValue type: delete new index
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    idx = kvsession.delete_index('index1')
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.KVResponse))
    assert idx.data == 'index1'
    # Document type: delete new index
    _, docsession = connect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
    idx = docsession.delete_index('index1')
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.DocResponse))
    assert idx['result'] == 'ok'
    assert idx.code == 200
    # Graph type: delete new index
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    idx = graphsession.delete_index('index1')
    assert isinstance(idx, (nosqlapi.Response, nosqlapi.GraphResponse))
    assert idx.data == '0 rows, System updates: 1'


# ------------------Batch Operation------------------
def test_batch():
    """Test batch operation"""
    from .test_columndb import MyDBBatch as ColBatch
    from .test_kvdb import MyDBBatch as KVBatch
    from .test_graphdb import MyDBBatch as GraphBatch
    # Column type: batch operations
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    ops = ['BEGIN BATCH', "UPDATE table SET name = 'Arthur' WHERE name=Matteo AND age=35;", "APPLY BATCH;"]
    batch = ColBatch(ops, colsession)
    ret = batch.execute()
    assert 'BATCH_OK' in ret
    # KeyValue type: batch operations
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    ops = "begin\nUPDATE=key1,value1;\nUPDATE=key2,value3;\nUPDATE=key3,value3;\nend;"
    batch = KVBatch(ops, kvsession)
    ret = batch.execute()
    assert 'BATCH_OK' in ret
    # Graph type: batch operations
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    ops = """MATCH (p:Person {name: 'Matteo'})-[rel:WORKS_FOR]-(:Company {name: 'MyWork'})
    SET rel.startYear = date({year: 2018})
    RETURN p"""
    batch = GraphBatch(ops, graphsession)
    ret = batch.execute()
    assert ret['matteo.name'] == 'Matteo'
    assert ret['matteo.age'] == 35


def test_call_batch():
    """Test batch operation"""
    from .test_columndb import MyDBBatch as ColBatch
    from .test_kvdb import MyDBBatch as KVBatch
    from .test_graphdb import MyDBBatch as GraphBatch
    # Column type: batch operations
    _, colsession = connect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
    ops = ['BEGIN BATCH', "UPDATE table SET name = 'Arthur' WHERE name=Matteo AND age=35;", "APPLY BATCH;"]
    batch = ColBatch(ops, colsession)
    ret = nosqlapi.Session.call(batch)
    assert 'BATCH_OK' in ret
    # KeyValue type: batch operations
    _, kvsession = connect('kv', 'prod-db.test.com', 'admin', 'password')
    ops = "begin\nUPDATE=key1,value1;\nUPDATE=key2,value3;\nUPDATE=key3,value3;\nend;"
    batch = KVBatch(ops, kvsession)
    ret = nosqlapi.Session.call(batch)
    assert 'BATCH_OK' in ret
    # Graph type: batch operations
    _, graphsession = connect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
    ops = """MATCH (p:Person {name: 'Matteo'})-[rel:WORKS_FOR]-(:Company {name: 'MyWork'})
    SET rel.startYear = date({year: 2018})
    RETURN p"""
    batch = GraphBatch(ops, graphsession)
    ret = nosqlapi.Session.call(batch)
    assert ret['matteo.name'] == 'Matteo'
    assert ret['matteo.age'] == 35


# ------------------asyncio------------------
async def aconnect(of_type, *args, **kwargs):
    await asyncio.sleep(0.1)
    conn, sess = connect(of_type, *args, **kwargs)
    return conn, sess


def test_async_connect():
    """Test asynchronous connection"""
    # Column type: async connect
    colconnection, colsession = asyncio.run(aconnect('column', 'prod-db.test.com', 'admin', 'password', 'db1'))
    assert isinstance(colconnection, (nosqlapi.Connection, nosqlapi.ColumnConnection))
    assert isinstance(colsession, (nosqlapi.Session, nosqlapi.ColumnSession))
    # KeyValue type: async connect
    kvconnection, kvsession = asyncio.run(aconnect('kv', 'prod-db.test.com', 'admin', 'password'))
    assert isinstance(kvconnection, (nosqlapi.Connection, nosqlapi.KVConnection))
    assert isinstance(kvsession, (nosqlapi.Session, nosqlapi.KVSession))
    # Document type: async connect
    docconnection, docsession = asyncio.run(aconnect('doc', 'prod-db.test.com', 'admin', 'password', 'db1'))
    assert isinstance(docconnection, (nosqlapi.Connection, nosqlapi.DocConnection))
    assert isinstance(docsession, (nosqlapi.Session, nosqlapi.DocSession))
    # Graph type: async connect
    graphconnection, graphsession = asyncio.run(aconnect('graph', 'prod-db.test.com', 'admin', 'password', 'db1'))
    assert isinstance(graphconnection, (nosqlapi.Connection, nosqlapi.GraphConnection))
    assert isinstance(graphsession, (nosqlapi.Session, nosqlapi.GraphSession))


def test_async_operation():
    """Test asynchronous operations"""

    async def doc_insert(doc, body):
        # Document type: insert
        _, docsession = await aconnect('doc', 'prod-db.test.com', 'admin', 'password', 'db1')
        await asyncio.sleep(0.1)
        return docsession.insert(doc, body)

    async def kv_update(key, value):
        # KeyValue type: update
        _, kvsession = await aconnect('kv', 'prod-db.test.com', 'admin', 'password')
        await asyncio.sleep(0.1)
        return kvsession.update(key, value)

    async def main():
        # Document type: insert document
        doc = 'db1/doc1'
        body = '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}'
        await doc_insert(doc, body)
        # KeyValue type: update key
        await kv_update('key', 'new-value')

    loop = asyncio.new_event_loop()
    ops = loop.create_task(main())
    loop.run_until_complete(ops)


def test_multiple_parallel_task():
    """Test parallel task with asyncio"""

    async def graph_get(node):
        # Graph type: get
        _, graphsession = await aconnect('graph', 'prod-db.test.com', 'admin', 'password', 'db1')
        await asyncio.sleep(0.1)
        return graphsession.get(node)

    async def column_delete(table, conditions):
        # Column type: delete
        _, colsession = await aconnect('column', 'prod-db.test.com', 'admin', 'password', 'db1')
        await asyncio.sleep(0.1)
        return colsession.update(table, conditions)

    if sys.version_info.minor >= 7:
        async def main():
            # Graph type: get node
            asyncio.create_task(graph_get('n:Person'))
            # KeyValue type: delete row
            asyncio.create_task(column_delete(table='table1', conditions=['name=Matteo', 'id=1']))

        asyncio.run(main())
    else:
        async def main():
            # Graph type: get node
            await graph_get('n:Person')
            # KeyValue type: delete row
            await column_delete(table='table1', conditions=['name=Matteo', 'id=1'])

        loop = asyncio.new_event_loop()
        ops = loop.create_task(main())
        loop.run_until_complete(ops)


if __name__ == '__main__':
    pytest.main()
