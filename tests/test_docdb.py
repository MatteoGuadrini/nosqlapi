import unittest
import nosqlapi.docdb
from nosqlapi.docdb.orm import Database
import json
from unittest import mock
from nosqlapi import (ConnectError, DatabaseCreationError, DatabaseDeletionError, DatabaseError, SessionError,
                      SessionInsertingError, SelectorAttributeError, SessionUpdatingError, SessionDeletingError,
                      SessionFindingError, SessionACLError)


# Below classes is a simple emulation of MongoDB like database


class MyDBConnection(nosqlapi.docdb.DocConnection):
    # Simulate http requests
    req = mock.Mock()

    def close(self):
        self.connection = None
        if self.connection is not None:
            raise ConnectError('Close connection error')

    def connect(self):
        # Connection
        if not self.port:
            self.port = 27017
        scheme = 'https://' if self.ssl else 'http://'
        if self.username and self.password:
            scheme += f'{self.username}:{self.password}@'
        url = f'{scheme}{self.host}:{self.port}'
        self.req.get = mock.MagicMock(return_value={'body': 'server http response ok',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        if self.req.get(url).get('status') != 200:
            raise ConnectError('server not respond')
        self.connection = url
        return MyDBSession(self.connection)

    def create_database(self, name: Database):
        self.req.put = mock.MagicMock(return_value={'body': '{"result": "ok"}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        if self.connection:
            if isinstance(name, Database):
                name = Database.name
            ret = self.req.put(f"{self.connection}/{name}")
            if ret.get('status') != 200:
                raise DatabaseCreationError(f'Database creation error: {ret.get("status")}')
            return MyDBResponse(json.loads(ret['body']),
                                ret['status'],
                                ret['header'])
        else:
            raise ConnectError("server isn't connected")

    def has_database(self, name: Database):
        if self.connection:
            if isinstance(name, Database):
                name = Database.name
            if name in self.databases():
                return True
            else:
                return False
        else:
            raise ConnectError("server isn't connected")

    def delete_database(self, name: Database):
        self.req.delete = mock.MagicMock(return_value={'body': '{"result": "ok"}',
                                                       'status': 200,
                                                       'header': '"Content-Type": [ "application/json" ]'})
        if self.connection:
            if isinstance(name, Database):
                name = Database.name
            ret = self.req.delete(f"{self.connection}/{name}")
            if ret.get('status') != 200:
                raise DatabaseDeletionError(f'Database deletion error: {ret.get("status")}')
            return MyDBResponse(json.loads(ret['body']),
                                ret['status'],
                                ret['header'])
        else:
            raise ConnectError("server isn't connected")

    def databases(self):
        self.req.get = mock.MagicMock(return_value={'body': '{"result": ["test_db", "db1", "db2"]}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        if self.connection:
            ret = self.req.get(f"{self.connection}/databases")
            dbs = json.loads(ret.get('body'))
            if dbs['result']:
                return MyDBResponse(dbs['result'],
                                    ret['status'],
                                    ret['header'])
            else:
                raise DatabaseError('no databases found on this server')
        else:
            raise ConnectError("server isn't connected")

    def show_database(self, name: Database):
        self.req.get = mock.MagicMock(return_value={'body': '{"result": {"name": "test_db", "size": "0.4GB"}}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        if self.connection:
            if isinstance(name, Database):
                name = Database.name
            ret = self.req.get(f"{self.connection}/databases?name={name}")
            dbs = json.loads(ret.get('body'))
            if dbs['result']:
                return MyDBResponse(dbs['result'],
                                    ret['status'],
                                    ret['header'])
            else:
                raise DatabaseError('no databases found on this server')
        else:
            raise ConnectError("server isn't connected")


class MyDBSession(nosqlapi.docdb.DocSession):
    # Simulate http requests
    req = mock.Mock()

    def __init__(self, connection):
        super().__init__()
        self.session = connection
        self.req.get = mock.MagicMock(return_value={'body': '{"host" : "mydocdb.local",\n"version" : "1.0",\n'
                                                            '"uptime" : 123445566}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.get(f"{self.session}/serverStatus")
        if ret.get('status') != 200:
            raise ConnectError('server not respond')
        self._description = json.loads(ret.get('body'))

    @property
    def acl(self):
        self.req.get = mock.MagicMock(return_value={'body': '{"user": "admin", "roles": ["administrator", "all"]}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.get(f"{self.session}/privileges")
        if ret.get('status') != 200:
            raise ConnectError('server not respond')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def get(self, path):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.get = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                            '"name": "Matteo", "age": 35}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.get(f"{self.session}/{path}")
        if ret.get('status') != 200:
            raise SessionError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def insert(self, path, doc):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                             '"revision": 1}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.session}/{path}", doc)
        if ret.get('status') != 200:
            raise SessionInsertingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def insert_many(self, path, *docs):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"insertedIds": [ "5099803df3f4948bd2f98391", '
                                                             '"5099803df3f4948bd2f98392", '
                                                             '"5099803df3f4948bd2f98393"]}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.session}/{path}", f"{[doc for doc in docs]}")
        if ret.get('status') != 200:
            raise SessionInsertingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def update(self, path, doc, rev):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                             '"revision": 2}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        doc_with_rev = json.loads(doc)
        doc_with_rev['revision'] = 2
        ret = self.req.post(f"{self.session}/{path}", json.dumps(doc_with_rev))
        if ret.get('status') != 200:
            raise SessionUpdatingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def update_many(self, path, query, *docs):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"insertedIds": [ "5099803df3f4948bd2f98391", '
                                                             '"5099803df3f4948bd2f98392", '
                                                             '"5099803df3f4948bd2f98393"]}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        doc_with_rev = {"docs": f"{list(docs)}", 'query': query}
        ret = self.req.post(f"{self.session}/{path}", json.dumps(doc_with_rev))
        if ret.get('status') != 200:
            raise SessionUpdatingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def delete(self, path, rev=None):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.delete = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                               '"revision": 3}',
                                                       'status': 200,
                                                       'header': '"Content-Type": [ "application/json" ]'})
        if not rev:
            ret = self.req.delete(f"{self.session}/{path}")
        else:
            ret = self.req.delete(f"{self.session}/{path}?revision={rev}")
        if ret.get('status') != 200:
            raise SessionDeletingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def close(self):
        self.session = None

    def find(self, selector):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                             '"name": "Matteo", "age": 35}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        if isinstance(selector, nosqlapi.docdb.DocSelector):
            ret = self.req.post(f"{self.session}/find", selector.build())
        else:
            ret = self.req.post(f"{self.session}/find", selector)
        if ret.get('status') != 200:
            raise SessionFindingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def grant(self, database, user, role):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': f'{{"user": "{user}",'
                                                             f'"role": "{role}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        role_ = dict()
        role_[user] = {"role": role, "db": database}
        ret = self.req.post(f"{self.session}/grantRolesToUser", json.dumps(role_))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def revoke(self, database, role):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': f'{{"role": "{role}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        role_ = {"role": role, "db": database}
        ret = self.req.post(f"{self.session}/revokeRolesFromUser", json.dumps(role_))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def new_user(self, user, password, roles: list = None, options: dict = None):
        if not self.session:
            raise ConnectError('connect to a database before some request')
        doc = {'user': user,
               'pwd': password}
        if roles:
            doc['roles'] = roles
        if options:
            doc['customData'] = options
        self.req.post = mock.MagicMock(return_value={'body': f'{{"user": "{user}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.session}/createUser", json.dumps(doc))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def set_user(self, user, password):
        if not self.session:
            raise ConnectError('connect to a database before some request')
        doc = {'user': user,
               'pwd': password}
        self.req.post = mock.MagicMock(return_value={'body': f'{{"user": "{user}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.session}/changeUserPassword", json.dumps(doc))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def delete_user(self, user):
        if not self.session:
            raise ConnectError('connect to a database before some request')
        doc = {'user': user}
        self.req.post = mock.MagicMock(return_value={'body': f'{{"user": "{user}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.session}/dropUser", json.dumps(doc))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])


class MyDBResponse(nosqlapi.docdb.DocResponse):
    pass


class MyDBSelector(nosqlapi.docdb.DocSelector):

    def build(self):
        query = dict()
        if not self.selector:
            raise SelectorAttributeError("selector is mandatory")
        query["selector"] = self.selector
        if self.fields:
            query["fields"] = self.fields
        if self.limit:
            query["limit"] = self.limit
        if self.partition:
            query["partition"] = self.partition
        if self.condition:
            query["condition"] = self.condition
        if self.order:
            query["order"] = self.order
        return json.dumps(query)


class DocConnectionTest(unittest.TestCase):
    def test_docdb_connect(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local:12345')

    def test_docdb_close(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local:12345')
        myconn.close()
        self.assertEqual(myconn.connection, None)

    def test_docdb_create_database(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local:12345')
        resp = myconn.create_database('test_db')
        self.assertEqual(resp.data['result'], 'ok')
        myconn.close()
        self.assertEqual(myconn.connection, None)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_docdb_exists_database(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local:12345')
        self.assertTrue(myconn.has_database('test_db'))
        myconn.close()
        self.assertEqual(myconn.connection, None)
        self.assertRaises(ConnectError, myconn.has_database, 'test_db')

    def test_docdb_delete_database(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local:12345')
        resp = myconn.delete_database('test_db')
        self.assertEqual(resp.data['result'], 'ok')
        myconn.close()
        self.assertEqual(myconn.connection, None)
        self.assertRaises(ConnectError, myconn.delete_database, 'test_db')

    def test_docdb_get_all_database(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local:12345')
        dbs = myconn.databases()
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['test_db', 'db1', 'db2'])
        myconn.close()
        self.assertEqual(myconn.connection, None)
        self.assertRaises(ConnectError, myconn.databases)

    def test_columndb_show_database(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local:12345')
        dbs = myconn.show_database('test_db')
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, {'name': 'test_db', 'size': '0.4GB'})
        myconn.close()
        self.assertEqual(myconn.connection, None)
        self.assertRaises(ConnectError, myconn.databases)


class DocSessionTest(unittest.TestCase):
    myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
    mysess = myconn.connect()

    def test_session_instance(self):
        self.assertIsInstance(self.mysess, MyDBSession)

    def test_description_session(self):
        self.assertEqual(self.mysess.description, {'host': 'mydocdb.local', 'version': '1.0', 'uptime': 123445566})

    def test_get_data(self):
        d = self.mysess.get('db/doc1')
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn('_id', d)
        self.assertEqual(d.data['_id'], '5099803df3f4948bd2f98391')

    def test_insert_data(self):
        ret = self.mysess.insert('db/doc1', '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}')
        self.assertEqual(ret.data['revision'], 1)

    def test_insert_many_data(self):
        ret = self.mysess.insert_many('db',
                                      '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}',
                                      '{"_id": "5099803df3f4948bd2f98392", "name": "Matteo", "age": 35}',
                                      '{"_id": "5099803df3f4948bd2f98393", "name": "Matteo", "age": 35}')
        self.assertEqual(ret.data['insertedIds'], ["5099803df3f4948bd2f98391",
                                                   "5099803df3f4948bd2f98392",
                                                   "5099803df3f4948bd2f98393"])

    def test_update_data(self):
        ret = self.mysess.update('db/doc1', '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}', rev=1)
        self.assertEqual(ret.data['revision'], 2)

    def test_update_many_data(self):
        ret = self.mysess.update_many('db',
                                      'name="Matteo"',
                                      '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}',
                                      '{"_id": "5099803df3f4948bd2f98392", "name": "Matteo", "age": 35}',
                                      '{"_id": "5099803df3f4948bd2f98393", "name": "Matteo", "age": 35}')
        self.assertEqual(ret.data['insertedIds'], ["5099803df3f4948bd2f98391",
                                                   "5099803df3f4948bd2f98392",
                                                   "5099803df3f4948bd2f98393"])

    def test_delete_data(self):
        ret = self.mysess.delete('db/doc1')
        self.assertEqual(ret.data['revision'], 3)

    def test_find_string_data(self):
        data = self.mysess.find('{"name": "Matteo"}')
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(data.data['_id'], '5099803df3f4948bd2f98391')

    def test_find_selector(self):
        sel = MyDBSelector()
        sel.selector = {"name": "Matteo"}
        sel.limit = 2
        self.assertIsInstance(sel, MyDBSelector)
        data = self.mysess.find(sel)
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(data.data['_id'], '5099803df3f4948bd2f98391')

    def test_get_acl_connection(self):
        self.assertIn('user', self.mysess.acl)

    def test_grant_user_connection(self):
        resp = self.mysess.grant('db', user='test', role='read_users')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['user'], 'test')

    def test_revoke_user_connection(self):
        resp = self.mysess.revoke('db', role='read_users')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data['role'], 'read_users')

    def test_close_session(self):
        self.mysess.close()
        self.assertEqual(self.mysess.session, None)
        DocSessionTest.mysess = DocSessionTest.myconn.connect()

    def test_new_user(self):
        resp = self.mysess.new_user('myuser', 'mypassword')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.data['user'], 'myuser')

    def test_modify_password_user(self):
        resp = self.mysess.set_user('myuser', 'newpassword')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.data['user'], 'myuser')

    def test_delete_user(self):
        resp = self.mysess.delete_user('myuser')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.data['user'], 'myuser')


if __name__ == '__main__':
    unittest.main()
