import json
import unittest
from unittest import mock
import nosqlapi.graphdb
from typing import List
from nosqlapi import (ConnectError, DatabaseCreationError, DatabaseDeletionError, DatabaseError, SessionError,
                      SessionInsertingError, SessionUpdatingError, SessionDeletingError)


# Below classes is a simple emulation of Neo4j like database

class MyDBConnection(nosqlapi.graphdb.GraphConnection):
    # Simulate http requests
    req = mock.Mock()

    def close(self):
        self.connection = None
        if self.connection is not None:
            raise ConnectError('Close connection error')

    def connect(self):
        # Connection
        if not self.port:
            self.port = 7474
        scheme = 'bolt://'
        url = f'{scheme}'
        if self.username and self.password:
            url += f'{self.username}:{self.password}@'
        url += f'{self.host}:{self.port}'
        if self.database:
            url += f'/{self.database}'
        else:
            raise ConnectError('database is mandatory')
        self.req.post = mock.MagicMock(return_value={'body': 'server connected',
                                                     'status': 200,
                                                     'header': f'CONNECT TO {url}'
                                                               f'WITH TIMEOUT 30'})
        if self.req.post(url).get('status') != 200:
            raise ConnectError('server not respond')
        self.connection = url
        return MyDBSession(self.connection)

    def create_database(self, name, not_exists=False, replace=False, options=None):
        if not_exists and replace:
            raise DatabaseCreationError('IF NOT EXISTS and OR REPLACE parts of this command cannot be used together')
        if self.connection:
            if not self.port:
                self.port = 7474
            scheme = 'bolt://'
            url = f'{scheme}'
            if self.username and self.password:
                url += f'{self.username}:{self.password}@'
            url += f'{self.host}:{self.port}'
            cypher = f'CREATE DATABASE {name}'
            if not_exists:
                cypher = f' IF NOT EXISTS'
            elif replace:
                cypher = f' OR REPLACE'
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

    def has_database(self, name):
        if self.connection:
            if name in self.databases():
                return True
            else:
                return False
        else:
            raise ConnectError("server isn't connected")

    def delete_database(self, name, exists=False, dump=False, destroy=False):
        if self.connection:
            if not self.port:
                self.port = 7474
            scheme = 'bolt://'
            url = f'{scheme}'
            if self.username and self.password:
                url += f'{self.username}:{self.password}@'
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
        if self.connection:
            if not self.port:
                self.port = 7474
            scheme = 'bolt://'
            url = f'{scheme}'
            if self.username and self.password:
                url += f'{self.username}:{self.password}@'
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


class MyDBSession(nosqlapi.graphdb.GraphSession):
    # Simulate http requests
    req = mock.Mock()

    def __init__(self, connection):
        super().__init__()
        db = connection.split('/')[-1]
        self.session = connection + '/data/transaction/commit'
        stm = {'statements': f'SHOW DATABASE {db}'}
        self.req.post = mock.MagicMock(return_value={'body': f'{{"nodes" : {{"name": {db}}}, '
                                                             f'"role": "standalone", "currentStatus": "online"}}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.session, json.dumps(stm))
        if ret.get('status') != 200:
            raise ConnectError("server not respond or database doesn't exists")
        self._description = json.loads(ret.get('body'))

    @property
    def acl(self):
        stm = {'statements': 'SHOW PRIVILEGES YIELD role, access, action, segment ORDER BY action'}
        self.req.post = mock.MagicMock(return_value={'body': '["admin","GRANTED","access","database"],'
                                                             '["admin","GRANTED","constraint","database"],'
                                                             '["admin","GRANTED","dbms_actions","database"]',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.session, json.dumps(stm))
        if ret.get('status') != 200:
            raise ConnectError('server not respond')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def get(self,
            node,
            return_properties: list = None,
            properties: dict = None,
            relationship_label=None,
            relationship_object=None):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        obj, label = node.split(':', 1)
        cypher = 'MATCH '
        if properties:
            match_block = f'(:{label} {properties})' if not obj else f'({obj}:{label} {properties})'
        else:
            match_block = f'(:{label})' if not obj else f'({obj}:{label})'
        cypher += f'{match_block}'
        if relationship_label:
            if not relationship_label and not relationship_object:
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
        ret = self.req.post(self.session, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def insert(self, node, properties: dict = None, return_properties: list = None):
        if not self.session:
            raise ConnectError('connect to a server before some request')
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
        ret = self.req.post(self.session, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionInsertingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def insert_many(self, nodes: list, properties: List[dict] = None):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        nodes = list(zip(nodes, properties))
        cypher = 'CREATE '
        ns = list()
        for node, prop in nodes:
            obj, label = node.split(':', 1)
            ns.append(f"({obj}:{label} {prop if prop else ''})")
        cypher += ','.join(ns)
        stm = {'statements': cypher}
        self.req.post = mock.MagicMock(return_value={'body': '{"n.name": ["Matteo", "Arthur"],'
                                                             '"n.age": [35, 42]}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.session, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionInsertingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def update(self, node, values: dict, return_properties: list = None):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        obj, label = node.split(':', 1)
        cypher = f"MATCH ({obj}:{label})\n"
        for prop, value in values:
            cypher += f"SET ({obj}.{prop} = {value}\n)"
        if return_properties:
            cypher += '\nRETURN ' + ','.join([f'{obj}.{prop}' for prop in return_properties])
        else:
            cypher += f'\nRETURN {obj}'
        stm = {'statements': cypher}
        self.req.post = mock.MagicMock(return_value={'body': '{"n.name": ["Matteo"],'
                                                             '"n.age": [42]}',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.session, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionUpdatingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def update_many(self, nodes: list, properties: List[dict] = None):
        raise NotImplemented('for this operation use batch object')

    def delete(self, node, properties: dict = None, with_rel=False):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        obj, label = node.split(':', 1)
        cypher = f"MATCH ({obj}:{label} {properties})\n" if properties else f"MATCH ({obj}:{label})\n"
        if not with_rel:
            cypher += f'DELETE {obj}'
        else:
            cypher += f'DETACH DELETE {obj}'
        stm = {'statements': cypher}
        self.req.post = mock.MagicMock(return_value={'body': '',
                                                     'status': 200,
                                                     'header': stm['statements']})
        ret = self.req.post(self.session, json.dumps(stm))
        if ret.get('status') != 200:
            raise SessionDeletingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def close(self):
        self.session = None


class MyDBResponse(nosqlapi.graphdb.GraphResponse):
    pass


class GraphConnectionTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
