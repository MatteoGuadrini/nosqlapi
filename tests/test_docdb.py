import unittest
import nosqlapi.docdb
from nosqlapi.docdb.odm import Database, Document, Index, Collection
from typing import Union
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
        self._connected = False

    def connect(self):
        if not self.port:
            self.port = 27017
        scheme = 'https://' if self.ssl else 'http://'
        if self.user and self.password:
            scheme += f'{self.user}:{self.password}@'
        url = f'{scheme}{self.host}:{self.port}'
        self.req.get = mock.MagicMock(return_value={'body': 'server http response ok',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        if self.req.get(url).get('status') != 200:
            raise ConnectError('server not respond')
        self._connected = True
        return MyDBSession(url)

    def create_database(self, name: Union[str, Database]):
        self.req.put = mock.MagicMock(return_value={'body': '{"result": "ok"}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        if self:
            if isinstance(name, Database):
                name = name.name
            if not self.port:
                self.port = 27017
            scheme = 'https://' if self.ssl else 'http://'
            if self.user and self.password:
                scheme += f'{self.user}:{self.password}@'
            url = f'{scheme}{self.host}:{self.port}'
            ret = self.req.put(f"{url}/{name}")
            if ret.get('status') != 200:
                raise DatabaseCreationError(f'Database creation error: {ret.get("status")}')
            return MyDBResponse(json.loads(ret['body']),
                                ret['status'],
                                ret['header'])
        else:
            raise ConnectError("server isn't connected")

    def has_database(self, name: Union[str, Database]):
        if self:
            if isinstance(name, Database):
                name = name.name
            if name in self.databases():
                return True
            else:
                return False
        else:
            raise ConnectError("server isn't connected")

    def delete_database(self, name: Union[str, Database]):
        self.req.delete = mock.MagicMock(return_value={'body': '{"result": "ok"}',
                                                       'status': 200,
                                                       'header': '"Content-Type": [ "application/json" ]'})
        if self:
            if isinstance(name, Database):
                name = name.name
            if not self.port:
                self.port = 27017
            scheme = 'https://' if self.ssl else 'http://'
            if self.user and self.password:
                scheme += f'{self.user}:{self.password}@'
            url = f'{scheme}{self.host}:{self.port}'
            ret = self.req.delete(f"{url}/{name}")
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
        if self:
            if not self.port:
                self.port = 27017
            scheme = 'https://' if self.ssl else 'http://'
            if self.user and self.password:
                scheme += f'{self.user}:{self.password}@'
            url = f'{scheme}{self.host}:{self.port}'
            ret = self.req.get(f"{url}/databases")
            dbs = json.loads(ret.get('body'))
            if dbs['result']:
                return MyDBResponse(dbs['result'],
                                    ret['status'],
                                    ret['header'])
            else:
                raise DatabaseError('no databases found on this server')
        else:
            raise ConnectError("server isn't connected")

    def show_database(self, name: Union[str, Database]):
        self.req.get = mock.MagicMock(return_value={'body': '{"result": {"name": "test_db", "size": "0.4GB"}}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        if self:
            if isinstance(name, Database):
                name = name.name
            if not self.port:
                self.port = 27017
            scheme = 'https://' if self.ssl else 'http://'
            if self.user and self.password:
                scheme += f'{self.user}:{self.password}@'
            url = f'{scheme}{self.host}:{self.port}'
            ret = self.req.get(f"{url}/databases?name={name}")
            dbs = json.loads(ret.get('body'))
            if dbs['result']:
                return MyDBResponse(dbs['result'],
                                    ret['status'],
                                    ret['header'])
            else:
                raise DatabaseError('no databases found on this server')
        else:
            raise ConnectError("server isn't connected")

    def copy_database(self, source, destination, host='localhost', user=None, password=None):
        self.req.post = mock.MagicMock(return_value={'body': '{"result": "ok"}',
                                                     'status': 201,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        if self:
            if not self.port:
                self.port = 27017
            scheme = 'https://' if self.ssl else 'http://'
            scheme += f'{user}:{password}@' if user and not password else f'{self.user}:{self.password}@'
            url = f'{scheme}{self.host if not host else host}:{self.port}'
            doc = {'fromdb': source, 'todb': destination}
            ret = self.req.post(url, json.dumps(doc))
            if ret.get('status') != 201:
                raise DatabaseError(f'Database copy error: {ret.get("status")}')
            return MyDBResponse(json.loads(ret['body']),
                                ret['status'],
                                ret['header'])
        else:
            raise ConnectError("server isn't connected")


class MyDBSession(nosqlapi.docdb.DocSession):
    # Simulate http requests
    req = mock.Mock()

    @property
    def item_count(self):
        return self._item_count

    @property
    def description(self):
        self.req.get = mock.MagicMock(return_value={'body': '{"host" : "mydocdb.local",\n"version" : "1.0",\n'
                                                            '"uptime" : 123445566}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.get(f"{self.connection}/serverStatus")
        if ret.get('status') != 200:
            raise ConnectError('server not respond')
        self._description = json.loads(ret.get('body'))
        return self._description

    @property
    def acl(self):
        self.req.get = mock.MagicMock(return_value={'body': '{"user": "admin", "roles": ["administrator", "all"]}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.get(f"{self.connection}/privileges")
        if ret.get('status') != 200:
            raise ConnectError('server not respond')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    @property
    def indexes(self):
        self.req.get = mock.MagicMock(return_value={'body': '[{"v" : 2, "key" : {"orderDate" : 1}, "name" : "index1"}, '
                                                            '{"v" : 2, "key" : {"category" : 1}, "name" : "index2"}]',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.get(f"{self.connection}/getIndexes")
        if ret.get('status') != 200:
            raise ConnectError('server not respond')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def get(self, path):
        if not self.connection:
            raise ConnectError('connect to a server before some request')
        self.req.get = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                            '"name": "Matteo", "age": 35}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.get(f"{self.connection}/{path}")
        if ret.get('status') != 200:
            raise SessionError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def insert(self, path, doc: Union[str, Document]):
        if not self.connection:
            raise ConnectError('connect to a server before some request')
        if isinstance(doc, Document):
            doc = doc.to_json()
        self.req.post = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                             '"revision": 1}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.connection}/{path}", doc)
        if ret.get('status') != 200:
            raise SessionInsertingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        self._item_count = 1
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def insert_many(self, path, *docs: Union[str, Document]):
        if not self.connection:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"insertedIds": [ "5099803df3f4948bd2f98391", '
                                                             '"5099803df3f4948bd2f98392", '
                                                             '"5099803df3f4948bd2f98393"]}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.connection}/{path}", f"{[doc for doc in docs]}")
        if ret.get('status') != 200:
            raise SessionInsertingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        self._item_count = len(docs)
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def update(self, path, doc: Union[str, Document], rev):
        if not self.connection:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                             '"revision": 2}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        if isinstance(doc, Document):
            doc['revision'] = 2
            doc = doc.to_json()
        else:
            doc = json.loads(doc)
            doc['revision'] = 2
            doc = json.dumps(doc)
        ret = self.req.post(f"{self.connection}/{path}", doc)
        if ret.get('status') != 200:
            raise SessionUpdatingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        self._item_count = 1
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def update_many(self, path, query, *docs: Union[str, Document]):
        if not self.connection:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"insertedIds": [ "5099803df3f4948bd2f98391", '
                                                             '"5099803df3f4948bd2f98392", '
                                                             '"5099803df3f4948bd2f98393"]}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        doc_with_rev = {"docs": f"{list(docs)}", 'query': query}
        ret = self.req.post(f"{self.connection}/{path}", json.dumps(doc_with_rev))
        if ret.get('status') != 200:
            raise SessionUpdatingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        self._item_count = len(docs)
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def delete(self, path, rev=None):
        if not self.connection:
            raise ConnectError('connect to a server before some request')
        self.req.delete = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                               '"revision": 3}',
                                                       'status': 200,
                                                       'header': '"Content-Type": [ "application/json" ]'})
        if not rev:
            ret = self.req.delete(f"{self.connection}/{path}")
        else:
            ret = self.req.delete(f"{self.connection}/{path}?revision={rev}")
        if ret.get('status') != 200:
            raise SessionDeletingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        self._item_count = 1
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def close(self):
        self._database = None

    def find(self, selector):
        if not self.connection:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                             '"name": "Matteo", "age": 35}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        if isinstance(selector, nosqlapi.docdb.DocSelector):
            ret = self.req.post(f"{self.connection}/find", selector.build())
        else:
            ret = self.req.post(f"{self.connection}/find", selector)
        if ret.get('status') != 200:
            raise SessionFindingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        self._item_count = len(ret.get("body"))
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def grant(self, database: Union[str, Database], user, role):
        if not self.connection:
            raise ConnectError('connect to a server before some request')
        if isinstance(database, Database):
            database = database.name
        self.req.post = mock.MagicMock(return_value={'body': f'{{"user": "{user}",'
                                                             f'"role": "{role}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        role_ = dict()
        role_[user] = {"role": role, "db": database}
        ret = self.req.post(f"{self.connection}/grantRolesToUser", json.dumps(role_))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def revoke(self, database: Union[str, Database], role):
        if not self.connection:
            raise ConnectError('connect to a server before some request')
        if isinstance(database, Database):
            database = database.name
        self.req.post = mock.MagicMock(return_value={'body': f'{{"role": "{role}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        role_ = {"role": role, "db": database}
        ret = self.req.post(f"{self.connection}/revokeRolesFromUser", json.dumps(role_))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def new_user(self, user, password, roles: list = None, options: dict = None):
        if not self.connection:
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
        ret = self.req.post(f"{self.connection}/createUser", json.dumps(doc))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def set_user(self, user, password):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        doc = {'user': user,
               'pwd': password}
        self.req.post = mock.MagicMock(return_value={'body': f'{{"user": "{user}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.connection}/changeUserPassword", json.dumps(doc))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def delete_user(self, user):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        doc = {'user': user}
        self.req.post = mock.MagicMock(return_value={'body': f'{{"user": "{user}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.connection}/dropUser", json.dumps(doc))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def add_index(self, name: Union[str, Index], data: dict = None):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(name, Index):
            data = name.data
            name = name.name
        else:
            data = data
        doc = [data, {'name': name}]
        self.req.post = mock.MagicMock(return_value={'body': f'{{"result": "ok"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.connection}/createIndex", json.dumps(doc))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def delete_index(self, name: Union[str, Index]):
        if not self.connection:
            raise ConnectError('connect to a database before some request')
        if isinstance(name, Index):
            name = name.name
        doc = {'name': name}
        self.req.post = mock.MagicMock(return_value={'body': f'{{"result": "ok"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.connection}/dropIndex", json.dumps(doc))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def compact(self, obj: Union[str, Database, Collection], force=False, comment=None):
        if not self.connection:
            raise ConnectError('connect to a server before some request')
        if isinstance(obj, (Collection, Database)):
            obj = obj.name
        dict_req = {"compact": obj, "force": force, "comment": comment}
        self.req.post = mock.MagicMock(return_value={'body': '{"compaction": true}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.connection}/compact", json.dumps(dict_req))
        if ret.get('status') != 200:
            raise SessionError(f'error: {ret.get("body")}, status: {ret.get("status")}')
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
        myconn = MyDBConnection('mydocdb.local', port=12345, user='admin', password='test')
        mysess = myconn.connect()
        self.assertEqual(mysess.connection, 'http://admin:test@mydocdb.local:12345')

    def test_docdb_close(self):
        myconn = MyDBConnection('mydocdb.local', port=12345, user='admin', password='test')
        mysess = myconn.connect()
        self.assertEqual(mysess.connection, 'http://admin:test@mydocdb.local:12345')
        myconn.close()
        self.assertFalse(myconn)

    def test_docdb_create_database(self):
        myconn = MyDBConnection('mydocdb.local', port=12345, user='admin', password='test')
        mysess = myconn.connect()
        self.assertEqual(mysess.connection, 'http://admin:test@mydocdb.local:12345')
        resp = myconn.create_database('test_db')
        self.assertEqual(resp.data['result'], 'ok')
        db = Database('test_db')
        resp = myconn.create_database(db)
        self.assertEqual(resp.data['result'], 'ok')
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_docdb_exists_database(self):
        myconn = MyDBConnection('mydocdb.local', port=12345, user='admin', password='test')
        mysess = myconn.connect()
        self.assertEqual(mysess.connection, 'http://admin:test@mydocdb.local:12345')
        self.assertTrue(myconn.has_database('test_db'))
        db = Database('test_db')
        self.assertTrue(myconn.has_database(db))
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.has_database, 'test_db')

    def test_docdb_delete_database(self):
        myconn = MyDBConnection('mydocdb.local', port=12345, user='admin', password='test')
        mysess = myconn.connect()
        self.assertEqual(mysess.connection, 'http://admin:test@mydocdb.local:12345')
        resp = myconn.delete_database('test_db')
        self.assertEqual(resp.data['result'], 'ok')
        db = Database('test_db')
        resp = myconn.delete_database(db)
        self.assertEqual(resp.data['result'], 'ok')
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.delete_database, 'test_db')

    def test_docdb_get_all_database(self):
        myconn = MyDBConnection('mydocdb.local', port=12345, user='admin', password='test')
        mysess = myconn.connect()
        self.assertEqual(mysess.connection, 'http://admin:test@mydocdb.local:12345')
        dbs = myconn.databases()
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['test_db', 'db1', 'db2'])
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.databases)

    def test_columndb_show_database(self):
        myconn = MyDBConnection('mydocdb.local', port=12345, user='admin', password='test')
        mysess = myconn.connect()
        self.assertEqual(mysess.connection, 'http://admin:test@mydocdb.local:12345')
        dbs = myconn.show_database('test_db')
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, {'name': 'test_db', 'size': '0.4GB'})
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, {'name': 'test_db', 'size': '0.4GB'})
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.databases)

    def test_docdb_copy_database(self):
        myconn = MyDBConnection('mydocdb.local', port=12345, user='admin', password='test')
        mysess = myconn.connect()
        self.assertEqual(mysess.connection, 'http://admin:test@mydocdb.local:12345')
        resp = myconn.copy_database('test_db', 'test_db2')
        self.assertEqual(resp.data['result'], 'ok')
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')


class DocSessionTest(unittest.TestCase):
    myconn = MyDBConnection('mydocdb.local', port=12345, user='admin', password='test')
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
        ret = self.mysess.insert('db/doc1', Document({"name": "Matteo", "age": 35}))
        self.assertEqual(ret.data['revision'], 1)

    def test_insert_many_data(self):
        ret = self.mysess.insert_many('db',
                                      '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}',
                                      '{"_id": "5099803df3f4948bd2f98392", "name": "Matteo", "age": 35}',
                                      '{"_id": "5099803df3f4948bd2f98393", "name": "Matteo", "age": 35}')
        self.assertEqual(ret.data['insertedIds'], ["5099803df3f4948bd2f98391",
                                                   "5099803df3f4948bd2f98392",
                                                   "5099803df3f4948bd2f98393"])
        ret = self.mysess.insert_many('db',
                                      Document({"name": "Matteo", "age": 35}, oid="5099803df3f4948bd2f98391"),
                                      Document({"name": "Matteo", "age": 35}, oid="5099803df3f4948bd2f98392"),
                                      Document({"name": "Matteo", "age": 35}, oid="5099803df3f4948bd2f98393"))
        self.assertEqual(ret.data['insertedIds'], ["5099803df3f4948bd2f98391",
                                                   "5099803df3f4948bd2f98392",
                                                   "5099803df3f4948bd2f98393"])

    def test_update_data(self):
        ret = self.mysess.update('db/doc1', '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}', rev=1)
        self.assertEqual(ret.data['revision'], 2)
        ret = self.mysess.update('db/doc1', Document({"name": "Matteo", "age": 35}), rev=1)
        self.assertEqual(ret.data['revision'], 2)

    def test_update_many_data(self):
        ret = self.mysess.update_many('db',
                                      'name="Matteo"',
                                      Document({"name": "Matteo", "age": 35}, oid="5099803df3f4948bd2f98391"),
                                      Document({"name": "Matteo", "age": 35}, oid="5099803df3f4948bd2f98392"),
                                      Document({"name": "Matteo", "age": 35}, oid="5099803df3f4948bd2f98393"))
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
        self.assertEqual(self.mysess.database, None)
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

    def test_add_index(self):
        resp = self.mysess.add_index('index_name', {'orderDate': 1, 'category': 1})
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.data['result'], 'ok')
        index = Index(name='index_name', data={'orderDate': 1, 'category': 1})
        resp = self.mysess.add_index(index)
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.data['result'], 'ok')

    def test_delete_index(self):
        resp = self.mysess.delete_index('index_name')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.data['result'], 'ok')
        index = Index(name='index_name', data={'orderDate': 1, 'category': 1})
        resp = self.mysess.delete_index(index)
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.data['result'], 'ok')

    def test_get_indexes(self):
        indexes = self.mysess.indexes
        self.assertIn('index1', indexes.data[0]['name'])
        self.assertIn('index2', indexes.data[1]['name'])

    def test_compact_collection(self):
        ret = self.mysess.compact('col1', force=True, comment='Test compaction')
        self.assertEqual(ret.data, {'compaction': True})
        ret = self.mysess.compact(Collection('test'))
        self.assertEqual(ret.data, {'compaction': True})

    def test_document_decorator(self):
        # Simple function
        @nosqlapi.docdb.document
        def monitor(**values):
            data = {}
            data.update(values)
            return data

        col = monitor(cpu=72, ram=16)
        self.assertIsInstance(col, Document)
        col2 = monitor(cpu=72, ram=16)
        self.assertIsInstance(col2, Document)
        self.assertEqual(col2['cpu'], 72)


if __name__ == '__main__':
    unittest.main()
