import json
import unittest
from unittest import mock
import nosqlapi.graphdb
from nosqlapi.graphdb import Database, Node, Label, Property, Relationship, RelationshipType, Index
from typing import List, Union
from nosqlapi import (ConnectError, DatabaseCreationError, DatabaseDeletionError, DatabaseError, SessionError,
                      SessionInsertingError, SessionUpdatingError, SessionDeletingError, SessionFindingError,
                      SessionACLError, SelectorAttributeError)


# Below classes is a simple emulation of Neo4j like database

class MyDBConnection(nosqlapi.graphdb.GraphConnection):
    # Simulate http requests
    req = mock.Mock()

    def close(self):
        self._connected = False

    def connect(self):
        # Connection
        if not self.port:
            self.port = 7474
        scheme = 'bolt://'
        url = f'{scheme}'
        if self.user and self.password:
            url += f'{self.user}:{self.password}@'
        url += f'{self.host}:{self.port}'
        self.req.post = mock.MagicMock(return_value={'body': 'server connected',
                                                     'status': 200,
                                                     'header': f'CONNECT TO {url}'
                                                               f'WITH TIMEOUT 30'})
        if self.req.post(url).get('status') != 200:
            raise ConnectError('server not respond')
        self._connected = True
        return MyDBSession(url, self.database)

    def create_database(self, name: Union[str, Database], not_exists=False, replace=False, options=None):
        if not_exists and replace:
            raise DatabaseCreationError('IF NOT EXISTS and OR REPLACE parts of this command cannot be used together')
        if self:
            if isinstance(name, Database):
                name = name.name
            if not self.port:
                self.port = 7474
            scheme = 'bolt://'
            url = f'{scheme}'
            if self.user and self.password:
                url += f'{self.user}:{self.password}@'
            url += f'{self.host}:{self.port}'
            cypher = f'CREATE DATABASE {name}'
            if not_exists:
                cypher += f' IF NOT EXISTS'
            elif replace:
                cypher += f' OR REPLACE'
            stm = {'statements': cypher}
            if options:
                stm['options'] = options
            self.req.post = mock.MagicMock(return_value={'body': '0 rows, System updates: 1',
                                                         'status': 200,
                                                         'header': cypher})
            ret = self.req.post(url, json.dumps(stm))
            if ret.get('status') != 200:
                raise DatabaseCreationError(f'Database creation error: {ret.get("status")}')
            return MyDBResponse(ret['body'],
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

    def delete_database(self, name: Union[str, Database], exists=False, dump=False, destroy=False):
        if self:
            if isinstance(name, Database):
                name = name.name
            if not self.port:
                self.port = 7474
            scheme = 'bolt://'
            url = f'{scheme}'
            if self.user and self.password:
                url += f'{self.user}:{self.password}@'
            url += f'{self.host}:{self.port}'
            cypher = f'DROP DATABASE {name}'
            if exists:
                cypher += ' IF EXISTS'
            if dump and destroy:
                raise DatabaseDeletionError('DUMP DATA and DESTROY DATA parts of this command cannot be used together')
            if dump:
                cypher += ' DUMP DATA'
            if destroy:
                cypher += ' DESTROY DATA'
            stm = {'statements': cypher}
            self.req.post = mock.MagicMock(return_value={'body': '0 rows, System updates: 1',
                                                         'status': 200,
                                                         'header': cypher})
            ret = self.req.post(url, json.dumps(stm))
            if ret.get('status') != 200:
                raise DatabaseDeletionError(f'Database deletion error: {ret.get("status")}')
            return MyDBResponse(ret['body'],
                                ret['status'],
                                ret['header'])
        else:
            raise ConnectError("server isn't connected")

    def databases(self):
        if self:
            if not self.port:
                self.port = 7474
            scheme = 'bolt://'
            url = f'{scheme}'
            if self.user and self.password:
                url += f'{self.user}:{self.password}@'
            url += f'{self.host}:{self.port}'
            cypher = 'SHOW DATABASES'
            stm = {'statements': cypher}
            self.req.get = mock.MagicMock(return_value={'body': '{"result": ["test_db", "db1", "db2"]}',
                                                        'status': 200,
                                                        'header': cypher})
            ret = self.req.get(url, json.dumps(stm))
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
        if self:
            if isinstance(name, Database):
                name = name.name
            if not self.port:
                self.port = 7474
            scheme = 'bolt://'
            url = f'{scheme}'
            if self.user and self.password:
                url += f'{self.user}:{self.password}@'
            url += f'{self.host}:{self.port}'
            cypher = f'USE {name}; CALL db.schema.visualization()'
            stm = {'statements': cypher}
            self.req.get = mock.MagicMock(return_value={'body': '{"result": {"nodes": ["matteo:Person"], '
                                                                '"relationships": [":WORK_IN"]}}',
                                                        'status': 200,
                                                        'header': cypher})
            ret = self.req.get(url, json.dumps(stm))
            dbs = json.loads(ret.get('body'))
            if dbs['result']:
                return MyDBResponse(dbs['result'],
                                    ret['status'],
                                    ret['header'])
            else:
                raise DatabaseError('no databases found on this server')
        else:
            raise ConnectError("server isn't connected")


class MyDBSession(nosqlapi.graphdb.GraphSession):
    # Simulate http requests
    req = mock.Mock()

    @property
    def acl(self):
        stm = {'statements': 'SHOW PRIVILEGES YIELD role, access, action, segment ORDER BY action'}
        self.req.post = mock.MagicMock(return_value={'body': '[["admin","GRANTED","access","database"],'
                                                             '["admin","GRANTED","constraint","database"],'
                                                             '["admin","GRANTED","dbms_actions","database"]]',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.connection, json.dumps(stm))
        if ret.get('status') != 200:
            raise ConnectError('server not respond')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    @property
    def indexes(self):
        stm = {'statements': 'SHOW INDEXES'}
        self.req.post = mock.MagicMock(return_value={'body': '["index1", "index2"]',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.connection, json.dumps(stm))
        if ret.get('status') != 200:
            raise ConnectError('server not respond')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    @property
    def item_count(self):
        return self._item_count

    @property
    def description(self):
        stm = {'statements': f'SHOW DATABASE {self.database}'}
        self.req.post = mock.MagicMock(return_value={'body': f'{{"nodes" : {{"name": "{self.database}"}}, '
                                                             f'"role": "standalone", "currentStatus": "online"}}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.connection, json.dumps(stm))
        if ret.get('status') != 200:
            raise ConnectError("server not respond or database doesn't exists")
        self._description = json.loads(ret.get('body'))
        return self._description

    def get(self,
            node: Union[str, Node],
            return_properties: list = None,
            properties: dict = None,
            relationship_label=None,
            relationship_object=None):
        if not self:
            raise ConnectError('connect to a server before some request')
        if isinstance(node, Node):
            obj, label = node.var, ':'.join(node.labels)
        else:
            obj, label = node.split(':', 1)
        cypher = 'MATCH '
        if properties:
            match_block = f'(:{label} {properties})' if not obj else f'({obj}:{label} {properties})'
        else:
            match_block = f'(:{label})' if not obj else f'({obj}:{label})'
        cypher += f'{match_block}'
        if relationship_label:
            if not relationship_object:
                raise SessionError('"relationship_label" and "relationship_object" both are needed')
            rel_obj, rel_obj_label = relationship_object.split(':')
            if rel_obj:
                cypher += f'-[:{relationship_label}]->({rel_obj}:{rel_obj_label})'
            else:
                cypher += f'-[:{relationship_label}]->(:{rel_obj_label})'
        stm = {'statements': cypher}
        self.req.post = mock.MagicMock(return_value={'body': '{"n.name": ["Matteo", "Arthur"],'
                                                             '"n.age": [35, 42]}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.connection, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def insert(self, node: Union[str, Node], properties: dict = None, return_properties: list = None):
        if not self:
            raise ConnectError('connect to a server before some request')
        if isinstance(node, Node):
            obj, label = node.var, ':'.join(node.labels)
        else:
            obj, label = node.split(':', 1)
        cypher = f"CREATE ({obj}:{label} {properties if properties else ''})"
        if return_properties:
            cypher += '\nRETURN ' + ','.join([f'{obj}.{prop}' for prop in return_properties])
        else:
            cypher += f'\nRETURN {obj}'
        stm = {'statements': cypher}
        self.req.post = mock.MagicMock(return_value={'body': '{"n.name": ["Matteo"],'
                                                             '"n.age": [35]}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.connection, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionInsertingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def insert_many(self, nodes: list, properties: List[dict] = None):
        if properties is None:
            properties = []
        if not self:
            raise ConnectError('connect to a server before some request')
        nodes = list(zip(nodes, properties))
        cypher = 'CREATE '
        ns = list()
        for node, prop in nodes:
            if isinstance(node, Node):
                obj, label = node.var, ':'.join(node.labels)
                prop = node.properties
            else:
                obj, label = node.split(':', 1)
            ns.append(f"({obj}:{label} {prop if prop else ''})")
        cypher += ','.join(ns)
        stm = {'statements': cypher}
        self.req.post = mock.MagicMock(return_value={'body': '[{"matteo.name": "Matteo",'
                                                             '"matteo.age": 35},'
                                                             '{"arthur.name": "Arthur",'
                                                             '"arthur.age": 42}]',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.connection, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionInsertingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def update(self, node: Union[str, Node], values=None, return_properties: list = None):
        if values is None:
            values = {}
        if not self:
            raise ConnectError('connect to a server before some request')
        if isinstance(node, Node):
            obj, label = node.var, ':'.join(node.labels)
        else:
            obj, label = node.split(':', 1)
        cypher = f"MATCH ({obj}:{label})\n"
        for prop, value in values.items():
            cypher += f"SET ({obj}.{prop} = {value}\n)"
        if return_properties:
            cypher += '\nRETURN ' + ','.join([f'{obj}.{prop}' for prop in return_properties])
        else:
            cypher += f'\nRETURN {obj}'
        stm = {'statements': cypher}
        self.req.post = mock.MagicMock(return_value={'body': '{"matteo.name": "Matteo",'
                                                             '"matteo.age": 42}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.connection, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionUpdatingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def update_many(self):
        raise NotImplementedError('for this operation use batch object')

    def delete(self, node: Union[str, Node], properties: dict = None, with_rel=False):
        if not self:
            raise ConnectError('connect to a server before some request')
        if isinstance(node, Node):
            obj, label = node.var, ':'.join(node.labels)
            if properties is None:
                properties = node.properties
        else:
            obj, label = node.split(':', 1)
        cypher = f"MATCH ({obj}:{label} {properties})\n" if properties else f"MATCH ({obj}:{label})\n"
        if not with_rel:
            cypher += f'DELETE {obj}'
        else:
            cypher += f'DETACH DELETE {obj}'
        stm = {'statements': cypher}
        self.req.post = mock.MagicMock(return_value={'body': '{}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.connection, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionDeletingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def close(self):
        self._database = None

    def find(self, selector):
        if not self:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '[{"matteo.name": "Matteo",'
                                                             '"matteo.age": 35},'
                                                             '{"arthur.name": "Arthur",'
                                                             '"arthur.age": 42}]',
                                                     'status': 200,
                                                     'header': selector.build()})
        if isinstance(selector, nosqlapi.graphdb.GraphSelector):
            ret = self.req.post(self.connection, selector.build())
        else:
            ret = self.req.post(self.connection, selector)
        if ret.get('status') != 200:
            raise SessionFindingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def grant(self, user, role):
        if not self:
            raise ConnectError('connect to a server before some request')
        cypher = f"GRANT ROLE {role} TO {user}"
        self.req.post = mock.MagicMock(return_value={'body': '0 rows, System updates: 1',
                                                     'status': 200,
                                                     'header': cypher})
        ret = self.req.post(self.connection, cypher)
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(ret.get('body'),
                            ret['status'],
                            ret['header'])

    def revoke(self, user, role):
        if not self:
            raise ConnectError('connect to a server before some request')
        cypher = f"REVOKE ROLE {role} TO {user}"
        self.req.post = mock.MagicMock(return_value={'body': '0 rows, System updates: 1',
                                                     'status': 200,
                                                     'header': cypher})
        ret = self.req.post(self.connection, cypher)
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(ret.get('body'),
                            ret['status'],
                            ret['header'])

    def new_user(self, user, password, password_change=True):
        if not self:
            raise ConnectError('connect to a server before some request')
        cypher = f"CALL dbms.security.createUser({user}, {password}, {password_change})"
        self.req.post = mock.MagicMock(return_value={'body': '0 rows, System updates: 1',
                                                     'status': 200,
                                                     'header': cypher})
        ret = self.req.post(self.connection, cypher)
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(ret.get('body'),
                            ret['status'],
                            ret['header'])

    def set_user(self, user, password):
        if not self:
            raise ConnectError('connect to a server before some request')
        cypher = f"ALTER USER {user} SET PASSWORD '{password}'"
        self.req.post = mock.MagicMock(return_value={'body': '0 rows, System updates: 1',
                                                     'status': 200,
                                                     'header': cypher})
        ret = self.req.post(self.connection, cypher)
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(ret.get('body'),
                            ret['status'],
                            ret['header'])

    def delete_user(self, user):
        if not self:
            raise ConnectError('connect to a server before some request')
        cypher = f"DROP USER {user}"
        self.req.post = mock.MagicMock(return_value={'body': '0 rows, System updates: 1',
                                                     'status': 200,
                                                     'header': cypher})
        ret = self.req.post(self.connection, cypher)
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(ret.get('body'),
                            ret['status'],
                            ret['header'])

    def link(self, node: Union[str, Node], linking_node, rel):
        if not self:
            raise ConnectError('connect to a server before some request')
        if isinstance(node, Node):
            obj, label = node.var, ':'.join(node.labels)
        else:
            obj, label = node.split(':', 1)
        cypher = f"CREATE ({obj}:{label})-[{rel}]->({linking_node})"
        stm = {'statements': cypher}
        self.req.post = mock.MagicMock(return_value={'body': '{"linked": true}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.connection, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionUpdatingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def detach(self, node: Union[str, Node], properties: dict = None):
        if not self:
            raise ConnectError('connect to a server before some request')
        if isinstance(node, Node):
            obj, label = node.var, ':'.join(node.labels)
            if properties is None:
                properties = node.properties
        else:
            obj, label = node.split(':', 1)
        cypher = f"MATCH ({obj}:{label} {properties})\n" if properties else f"MATCH ({obj}:{label})\n"
        cypher += f'DETACH DELETE {obj}'
        stm = {'statements': cypher}
        self.req.post = mock.MagicMock(return_value={'body': '{"detached": true}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.connection, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionUpdatingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def add_index(self, name: Union[str, Index], node: str = None, properties: list = None, options: dict = None):
        if not self:
            raise ConnectError('connect to a server before some request')
        if isinstance(name, Index):
            node = name.node
            properties = name.properties
            options = name.options
            name = name.name
        if node is None or properties is None:
            raise SessionInsertingError('node and properties are mandatory.')
        cypher = f'CREATE BTREE INDEX {name} IF NOT EXISTS FOR ({node}) ON ({",".join(prop for prop in properties)}) '
        if options:
            cypher += f'OPTIONS "{{" {",".join(f"{key}:{value}" for key, value in options.items())} "}}"'
        self.req.post = mock.MagicMock(return_value={'body': '0 rows, System updates: 1',
                                                     'status': 200,
                                                     'header': cypher})
        ret = self.req.post(self.connection, cypher)
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(ret.get('body'),
                            ret['status'],
                            ret['header'])

    def delete_index(self, node: Union[str, Index], tag=None):
        if not self:
            raise ConnectError('connect to a server before some request')
        if isinstance(node, Index):
            tag = node.properties
            node = node.name
        cypher = f'DROP INDEX ON:{node}({tag})'
        self.req.post = mock.MagicMock(return_value={'body': '0 rows, System updates: 1',
                                                     'status': 200,
                                                     'header': cypher})
        ret = self.req.post(self.connection, cypher)
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(ret.get('body'),
                            ret['status'],
                            ret['header'])


class MyDBResponse(nosqlapi.graphdb.GraphResponse):
    pass


class MyDBSelector(nosqlapi.graphdb.GraphSelector):

    def build(self):
        cypher = ''
        obj, label = self.selector.split(':', 1)
        if not self.selector:
            raise SelectorAttributeError("selector is mandatory")
        cypher += f'MATCH ({obj}:{label})\n'
        if self.condition:
            cypher += f'WHERE {self.condition}\n'
        if self.order:
            cypher += f'ORDER BY {self.order} DESC\n'
        if self.limit:
            cypher += f'LIMIT {self.limit}\n'
        if self.fields:
            cypher += 'RETURN ' + ','.join(f'{obj}.{field}' for field in self.fields)
        else:
            cypher += f'RETURN {obj}'
        return cypher


class MyDBBatch(nosqlapi.graphdb.GraphBatch):
    # Simulate http requests
    req = mock.Mock()

    def execute(self):
        stm = {'statements': '\n'.join(self.batch)}
        self.req.post = mock.MagicMock(return_value={'body': '{"matteo.name": "Matteo",'
                                                             '"matteo.age": 35}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.session, json.dumps(stm))
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])


class GraphConnectionTest(unittest.TestCase):

    def test_graphdb_connect(self):
        myconn = MyDBConnection('mygraphdb.local', port=12345, user='admin', password='test', database='db')
        myconn.connect()
        self.assertTrue(myconn)

    def test_graphdb_close(self):
        myconn = MyDBConnection('mygraphdb.local', port=12345, user='admin', password='test', database='db')
        myconn.connect()
        self.assertTrue(myconn)
        myconn.close()
        self.assertFalse(myconn)

    def test_graphdb_create_database(self):
        myconn = MyDBConnection('mygraphdb.local', port=12345, user='admin', password='test', database='db')
        myconn.connect()
        self.assertTrue(myconn)
        resp = myconn.create_database('test_db')
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        resp = myconn.create_database(Database('test_db'))
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_graphdb_create_database_if_not_exists(self):
        myconn = MyDBConnection('mygraphdb.local', port=12345, user='admin', password='test', database='db')
        myconn.connect()
        self.assertTrue(myconn)
        resp = myconn.create_database('test_db', not_exists=True)
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        resp = myconn.create_database('test_db', replace=True)
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        self.assertRaises(DatabaseCreationError, myconn.create_database, 'test_db', not_exists=True, replace=True)
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_graphdb_exists_database(self):
        myconn = MyDBConnection('mygraphdb.local', port=12345, user='admin', password='test', database='db')
        myconn.connect()
        self.assertTrue(myconn)
        self.assertTrue(myconn.has_database('test_db'))
        self.assertTrue(myconn.has_database(Database('test_db')))
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.has_database, 'test_db')

    def test_graphdb_delete_database(self):
        myconn = MyDBConnection('mygraphdb.local', port=12345, user='admin', password='test', database='db')
        myconn.connect()
        self.assertTrue(myconn)
        resp = myconn.delete_database(Database('test_db'))
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        resp = myconn.delete_database('test_db')
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        resp = myconn.delete_database('test_db', exists=True)
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        resp = myconn.delete_database('test_db', exists=True, destroy=True)
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        resp = myconn.delete_database('test_db', exists=True, dump=True)
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        self.assertRaises(DatabaseDeletionError, myconn.delete_database, 'test_db', dump=True, destroy=True)
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.delete_database, 'test_db')

    def test_graphdb_get_all_database(self):
        myconn = MyDBConnection('mygraphdb.local', port=12345, user='admin', password='test', database='db')
        myconn.connect()
        self.assertTrue(myconn)
        dbs = myconn.databases()
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['test_db', 'db1', 'db2'])
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.databases)

    def test_graphdb_show_database(self):
        myconn = MyDBConnection('mygraphdb.local', port=12345, user='admin', password='test', database='db')
        myconn.connect()
        self.assertTrue(myconn)
        dbs = myconn.show_database('test_db')
        self.assertIsInstance(dbs, MyDBResponse)
        dbs = myconn.show_database(Database('test_db'))
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, {'nodes': ['matteo:Person'], 'relationships': [':WORK_IN']})
        myconn.close()
        self.assertFalse(myconn)
        self.assertRaises(ConnectError, myconn.databases)


class GraphSessionTest(unittest.TestCase):
    myconn = MyDBConnection('mygraphdb.local', port=12345, user='admin', password='test', database='db')
    mysess = myconn.connect()

    def test_session_instance(self):
        self.assertIsInstance(self.mysess, MyDBSession)

    def test_description_session(self):
        self.assertEqual(self.mysess.description, {'nodes': {'name': 'db'},
                                                   'role': 'standalone',
                                                   'currentStatus': 'online'})

    def test_get_data(self):
        # Get all nodes with Person label
        d = self.mysess.get('n:Person')
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn('n.name', d)
        self.assertEqual(d.data['n.name'], ['Matteo', 'Arthur'])
        d = self.mysess.get(Node(var='n', labels=[Label('Person')]))
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn('n.name', d)
        self.assertEqual(d.data['n.name'], ['Matteo', 'Arthur'])
        # Get all nodes with Person label with returned properties
        d = self.mysess.get('n:Person', return_properties=['name', 'age'])
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn('n.age', d)
        self.assertEqual(d.data['n.age'], [35, 42])
        # Get all nodes with Person label match properties
        d = self.mysess.get('n:Person', properties={'name': 'Matteo'})
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn('Matteo', d.data['n.name'])
        # Get all nodes with Person label with relationship
        d = self.mysess.get('n:Person', relationship_label='WORK_IN', relationship_object='work:MyWork')
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn('Matteo', d.data['n.name'])
        self.assertRaises(SessionError, self.mysess.get, 'n:Person', relationship_label='WORK_IN')

    def test_insert_data(self):
        ret = self.mysess.insert('n:Person', {'name': 'Matteo', 'age': 35}, return_properties=['name', 'age'])
        self.assertEqual(ret.data, {'n.name': ['Matteo'], 'n.age': [35]})
        n = Node(var='n', labels=[Label('Person')], properties=Property({'name': 'Matteo', 'age': 35}))
        ret = self.mysess.insert(n, return_properties=['name', 'age'])
        self.assertEqual(ret.data, {'n.name': ['Matteo'], 'n.age': [35]})

    def test_insert_many_data(self):
        ret = self.mysess.insert_many(['matteo:Person', 'arthur:Person'],
                                      [{'name': 'Matteo', 'age': 35}, {'name': 'Arthur', 'age': 42}])
        self.assertEqual(ret.data, [{'matteo.name': 'Matteo', 'matteo.age': 35},
                                    {'arthur.name': 'Arthur', 'arthur.age': 42}])
        nodes = [Node(['Person'], {'name': 'Matteo', 'age': 35}, 'matteo'),
                 Node(['Person'], {'name': 'Arthur', 'age': 42}, 'arthur')]
        ret = self.mysess.insert_many(nodes)
        self.assertEqual(ret.data, [{'matteo.name': 'Matteo', 'matteo.age': 35},
                                    {'arthur.name': 'Arthur', 'arthur.age': 42}])

    def test_update_data(self):
        ret = self.mysess.update('matteo:Person', {'name': 'Matteo', 'age': 42}, return_properties=['name', 'age'])
        self.assertEqual(ret.data, {'matteo.name': 'Matteo', 'matteo.age': 42})
        n = Node(var='n', labels=[Label('Person')], properties=Property({'name': 'Matteo', 'age': 42}))
        ret = self.mysess.update(n, return_properties=['name', 'age'])
        self.assertEqual(ret.data, {'matteo.name': 'Matteo', 'matteo.age': 42})

    def test_update_many_data(self):
        self.assertRaises(NotImplementedError, self.mysess.update_many)

    def test_delete_data(self):
        # Delete all person
        ret = self.mysess.delete(':Person')
        self.assertEqual(ret.data, {})
        ret = self.mysess.delete(Node(['Person']))
        self.assertEqual(ret.data, {})
        # Delete all person with name "Matteo"
        ret = self.mysess.delete(':Person', properties={'name': 'Matteo'})
        self.assertEqual(ret.data, {})
        ret = self.mysess.delete(Node(['Person'], {'name': 'Matteo'}))
        self.assertEqual(ret.data, {})
        # Delete all person and with name "Matteo" and his relationships
        ret = self.mysess.delete(':Person', properties={'name': 'Matteo'}, with_rel=True)
        self.assertEqual(ret.data, {})
        ret = self.mysess.delete(Node(['Person'], {'name': 'Matteo'}), with_rel=True)
        self.assertEqual(ret.data, {})

    def test_find_selector(self):
        sel = MyDBSelector()
        sel.selector = 'people:Person'
        sel.condition = 'people.age>=35'
        sel.order = 'age'
        sel.fields = ['name', 'age']
        sel.limit = 2
        self.assertIsInstance(sel, MyDBSelector)
        data = self.mysess.find(sel)
        self.assertIsInstance(data, MyDBResponse)
        self.assertEqual(data.data, [{'matteo.name': 'Matteo', 'matteo.age': 35},
                                     {'arthur.name': 'Arthur', 'arthur.age': 42}])

    def test_get_acl_connection(self):
        self.assertIn(['admin', 'GRANTED', 'access', 'database'], self.mysess.acl)

    def test_grant_user_connection(self):
        resp = self.mysess.grant(user='test', role='read_users')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, '0 rows, System updates: 1')

    def test_revoke_user_connection(self):
        resp = self.mysess.revoke(user='test', role='read_users')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, '0 rows, System updates: 1')

    def test_new_user(self):
        resp = self.mysess.new_user('myuser', 'mypassword')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, '0 rows, System updates: 1')

    def test_modify_password_user(self):
        resp = self.mysess.set_user('myuser', 'newpassword')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, '0 rows, System updates: 1')

    def test_delete_user(self):
        resp = self.mysess.delete_user('myuser')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, '0 rows, System updates: 1')

    def test_close_session(self):
        self.mysess.close()
        self.assertEqual(self.mysess.database, None)
        GraphSessionTest.mysess = GraphSessionTest.myconn.connect()

    def test_batch(self):
        b = ["MATCH (p:Person {name: 'Matteo'})-[rel:WORKS_FOR]-(:Company {name: 'MyWork'})",
             "SET rel.startYear = date({year: 2018})", "RETURN p"]
        batch = MyDBBatch(b)
        resp = batch.execute()
        self.assertEqual(resp.data, {'matteo.name': 'Matteo', 'matteo.age': 35})

    def test_batch_add_remove_modify(self):
        b = ["MATCH (p:Person {name: 'Matteo'})-[rel:WORKS_FOR]-(:Company {name: 'MyWork'})",
             "SET rel.startYear = date({year: 2018})"]
        batch = MyDBBatch(b)
        # Add element
        batch.batch.append("RETURN p")
        self.assertEqual(len(batch.batch), 3)
        # Modify element
        batch.batch[1] = "SET rel.startYear = date({year: 2019})"
        self.assertEqual(batch.batch[1], "SET rel.startYear = date({year: 2019})")
        # Delete element
        batch.batch.append("UNUSEFUL;")
        self.assertEqual(len(batch.batch), 4)
        del batch.batch[-1]
        self.assertEqual(len(batch.batch), 3)
        batch.execute()

    def test_call_batch(self):
        b = """MATCH (p:Person {name: 'Matteo'})-[rel:WORKS_FOR]-(:Company {name: 'MyWork'})
    SET rel.startYear = date({year: 2018})
    RETURN p"""
        batch = MyDBBatch(b)
        resp = self.mysess.call(batch)
        self.assertEqual(resp.data, {'matteo.name': 'Matteo', 'matteo.age': 35})

    def test_link(self):
        ret = self.mysess.link('matteo:Person', 'open_source:JOB', ':WORK_IN')
        self.assertEqual(ret.data, {'linked': True})
        person = Node(['Person'], var='matteo')
        job = Node(['JOB'], var='open_source')
        rel = Relationship([RelationshipType('WORK_IN')])
        ret = self.mysess.link(person, job, rel)
        self.assertEqual(ret.data, {'linked': True})

    def test_detach_node(self):
        # Detach relationship for node
        ret = self.mysess.detach(':Person', properties={'name': 'Matteo'})
        self.assertEqual(ret.data, {'detached': True})
        person = Node(['Person'], {'name': 'Matteo'})
        ret = self.mysess.detach(person)
        self.assertEqual(ret.data, {'detached': True})

    def test_add_index(self):
        resp = self.mysess.add_index('index_name', 'n:node', ['n.properties_1', 'n.properties_2'], {'option': 'value'})
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        index = Index('index_name', 'n:node', ['n.properties_1', 'n.properties_2'], {'option': 'value'})
        resp = self.mysess.add_index(index)
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, '0 rows, System updates: 1')

    def test_delete_index(self):
        resp = self.mysess.delete_index('node', 'properties_1')
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, '0 rows, System updates: 1')
        index = Index('index_name', 'node', 'properties_1', None)
        resp = self.mysess.delete_index(index)
        self.assertIsInstance(resp, MyDBResponse)
        self.assertEqual(resp.data, '0 rows, System updates: 1')

    def test_get_indexes(self):
        self.assertIn('index1', self.mysess.indexes)
        self.assertIn('index2', self.mysess.indexes)

    def test_prop_decorator(self):
        # Simple function
        @nosqlapi.graphdb.prop
        def person_node(name, age, title):
            return {'name': name.title(), 'age': int(age), 'title': title.title()}

        pro = person_node('Matteo', 36, 'DevOps')
        self.assertIsInstance(pro, Property)
        pro2 = person_node('Arthur', 42, 'hitchhikers')
        self.assertIsInstance(pro2, Property)
        self.assertEqual(pro2['title'], 'Hitchhikers')

    def test_node_decorator(self):
        # Simple function
        @nosqlapi.graphdb.node
        def person(name, age, title):
            return {'name': name.title(), 'age': int(age), 'title': title.title()}

        node1 = person('Matteo', 36, 'DevOps')
        self.assertIsInstance(node1, Node)
        node2 = person('Arthur', 42, 'hitchhikers')
        self.assertIsInstance(node2, Node)
        self.assertEqual(node2.labels[0], 'person')


if __name__ == '__main__':
    unittest.main()
