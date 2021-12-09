.. toctree::

Build a library
===============

In this section we will build a **NOSQL API** compliant library, using the ``nosqlapi`` library.
We will first build the core objects that will allow us to connect and operate with our database.

.. note::
    The following example is designed for a NOSQL database of the Document type; by changing the application logic of
    the various methods in the classes you can build a library for another type of NOSQL database in the same way.
    The procedures are the same.

Let's prepare the steps:

* Create a package (directory with an ``__init__.py`` file) named **pycouch**.
* write ``core.py``, with core classes and functions.
* write ``utils.py``, with utility classes and function, like ORM objects.

Core
----

The **core** classes must provide a connection and operation interface towards the database.
All *CRUD* operations will need to be supported. We can implement new ones, based on the type of database we support.

Create a ``core.py`` module.

.. code-block:: python

    #!/usr/bin/env python3
    # -*- encoding: utf-8 -*-
    # core.py

    """Python library for document CouchDB server"""

    import nosqlapi
    import urllib.request
    import json

Connection class
****************

Let's build the server connection class. Since we are connecting to a `CouchDB database <https://couchdb.apache.org/>`_,
we will take advantage of the *http API*.

We define the ``__init__`` constructor with all the info needed to perform operations with the database and create a ``Session`` object using the ``connect()`` method.

.. code-block:: python

    class Connection(nosqlapi.DocConnection):
        """CouchDB connection class; connect to CouchDB server."""
        def __init__(self, host='localhost', port=5984, username=None, password=None, ssl=None, tls=None, cert=None,
                    database=None, ca_cert=None, ca_bundle=None):
            super().__init__(self, host=host, port=port, username=username, password=password, ssl=ssl, tls=tls,
                            cert=cert, ca_cert=ca_cert, ca_bundle=ca_bundle)
            self.method = 'https://' if self.port == 6984 or self.port == 443 else 'http://'
            if self.username and self.password:
                auth = f'{self.username}:{self.password}@'
            self.url = f'{self.method}{auth}{self.host}:{self.port}'

Now let's define the ``close`` and ``connect`` methods, to create the database connection.

.. code-block:: python

        def close(self, clean=False):
            self._connected = False
            if clean:
                self.database = None
                self.host = None

        def connect(self):
            session_url = self.url + f'/{self.database}'
            if urllib.request.head(session_url).status_code == 200:
                session = Session(database=session_url)
                self._connected = True
                return session
            else:
                raise nosqlapi.ConnectError(f'I cannot connect to the server: {self.url}')

Now let's all define methods that operate at the database level.

.. code-block:: python

        def create_database(self, name, shards=8, replicas=3, partitioned=False):
            data = {"w": shards, "n": replicas}
            if partitioned:
                data['partitioned'] = partitioned
            req = urllib.request.Request(self.url + f'/{name}',
                                        data=json.dumps(data).encode('utf8'),
                                        method='PUT')
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req)
            if response.status_code == 201:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.DatabaseCreationError(f'Database creation unsuccessfully: {name}'),
                                header=response.header_items())

        def has_database(self, name):
            response = urllib.request.urlopen(self.url + f'/{name}')
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.DatabaseError(f'Database not found: {name}'),
                                header=response.header_items())

        def delete_database(self, name):
            req = urllib.request.Request(self.url + f'/{name}', method='DELETE')
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req)
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.DatabaseDeletionError(f'Database deletion unsuccessfully: {name}'),
                                header=response.header_items())

        def databases(self):
            response = urllib.request.urlopen(self.url + '/_all_dbs')
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.DatabaseError(f'Database not found: {name}'),
                                header=response.header_items())

        def show_database(self, name):
            response = urllib.request.urlopen(self.url + f'/{name}')
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.DatabaseError(f'Database not found: {name}'),
                                header=response.header_items())

Response class
**************

There isn't much to do with the ``Response`` class. We inherit directly from the ``nosqlapi.docdb.DocResponse`` class.

.. code-block:: python

    class Response(nosqlapi.DocResponse):
        """CouchDB response class; information about a certain transaction."""
        ...

Session class
*************

Ok, now build the ``Session`` class. This class used for CRUD operation on the specific database.
The ``acl`` property is used to retrieve the Access Control lists of the current database and therefore the read/write permissions of the current session.
The property ``indexes`` is used to retrieve all the indexes created for the current database.

.. code-block:: python

    class Session(nosqlapi.DocSession):
        """CouchDB session class; CRUD operation on the database."""
        @property
        def acl(self):
            response = urllib.request.urlopen(self.database + f'/_security')
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.SessionACLError(f'ACLs error'),
                                header=response.header_items())

        @property
        def indexes(self):
            response = urllib.request.urlopen(self.database + f'/_index')
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.SessionError(f'Index error'),
                                header=response.header_items())

Now let's all define CRUD (Create, Read, Update, Delete) methods. *Create* word is associated to ``insert`` and ``insert_many`` methods;
*Read* to ``get`` method, *Update* to ``update`` and ``update_many`` methods and *Delete* to ``delete`` method.
Each *CRUD* method is created to directly manage the data in the database to which the connection was created via the ``Connection`` object.

.. code-block:: python

        def get(self, document='_all_docs', rev=None, attachment=None, partition=None, local=False, key=None):
            url = self.database
            if partition:
                url += url + f'/{partition}/{document}'
            else:
                url += url + f'/{document}'
            if attachment:
                url += url + f'/{attachment}'
            if rev:
                url += url + f'?rev={rev}'
            elif key:
                url += url + f'?key={key}'
            if bool(local):
                url = self.database + f'/_local_docs'
            response = urllib.request.urlopen(url)
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.SessionFindingError(f'Document not found: {url}'),
                                header=response.header_items())

        def insert(self, name, data=None, attachment=None, partition=None):
             url = self.database + f'/{name}'
             if attachment:
                 url += url + f"/{attachment}"
             id = f"{partition}:{name}" if partition else name
             data = {"_id": id}
             if data:
                 data.update(data)
             req = urllib.request.Request(url,
                                     data=json.dumps(data).encode('utf8'),
                                     method='PUT')
             req.add_header('Content-Type', 'application/json')
             response = urllib.request.urlopen(req)
             if response.status_code == 201:
                 return Response(data=json.loads(response.read()),
                                 code=response.status_code,
                                 error=None,
                                 header=response.header_items())
             else:
                 return Response(data=None,
                                 code=response.status_code,
                                 error=noslapi.SessionInsertingError(f'Insert document {url} with data {data} failed'),
                                 header=response.header_items())

        def insert_many(self, *documents):
             url = f"{self.database}/_bulk_docs"
             data = {"docs": []}
             if documents:
                 data['docs'].extend(documents)
             req = urllib.request.Request(url,
                                     data=json.dumps(data).encode('utf8'),
                                     method='POST')
             req.add_header('Content-Type', 'application/json')
             response = urllib.request.urlopen(req)
             if response.status_code == 201:
                 return Response(data=json.loads(response.read()),
                                 code=response.status_code,
                                 error=None,
                                 header=response.header_items())
             else:
                 return Response(data=None,
                                 code=response.status_code,
                                 error=noslapi.SessionInsertingError('Bulk insert document failed'),
                                 header=response.header_items())

        def update(self, name, rev, data=None, partition=None):
             url = self.database + f'/{name}?rev={rev}'
             id = f"{partition}:{name}" if partition else name
             data = {"_id": id}
             if data:
                 data.update(data)
             req = urllib.request.Request(url,
                                     data=json.dumps(data).encode('utf8'),
                                     method='PUT')
             req.add_header('Content-Type', 'application/json')
             response = urllib.request.urlopen(req)
             if response.status_code == 201:
                 return Response(data=json.loads(response.read()),
                                 code=response.status_code,
                                 error=None,
                                 header=response.header_items())
             else:
                 return Response(data=None,
                                 code=response.status_code,
                                 error=noslapi.SessionUpdatingError(f'Update document {url} with data {data} failed'),
                                 header=response.header_items())

        def update_many(self, *documents):
             url = f"{self.database}/_bulk_docs"
             data = {"docs": []}
             if documents:
                 data['docs'].extend(documents)
             req = urllib.request.Request(url,
                                     data=json.dumps(data).encode('utf8'),
                                     method='POST')
             req.add_header('Content-Type', 'application/json')
             response = urllib.request.urlopen(req)
             if response.status_code == 201:
                 return Response(data=json.loads(response.read()),
                                 code=response.status_code,
                                 error=None,
                                 header=response.header_items())
             else:
                 return Response(data=None,
                                 code=response.status_code,
                                 error=noslapi.SessionUpdatingError('Bulk update document failed'),
                                 header=response.header_items())

        def delete(self, name, rev, partition=None):
             url = self.database + f'/{name}?rev={rev}'
             id = f"{partition}:{name}" if partition else name
             req = urllib.request.Request(url,
                                     data=json.dumps(data).encode('utf8'),
                                     method='DELETE')
             req.add_header('Content-Type', 'application/json')
             response = urllib.request.urlopen(req)
             if response.status_code == 201:
                 return Response(data=json.loads(response.read()),
                                 code=response.status_code,
                                 error=None,
                                 header=response.header_items())
             else:
                 return Response(data=None,
                                 code=response.status_code,
                                 error=noslapi.SessionDeletingError(f'Delete document {name} failed'),
                                 header=response.header_items())

The ``close`` method will only close the session, but not the connection.

.. code-block:: python

        def close(self):
            self.database = None

The ``find`` method is the one that allows searching for data in the database.
This method can accept strings or ``Selector`` objects, which help in the construction of the query in the database language.

.. code-block:: python

        def find(self, query):
            url = f"{self.database}/_find"
            if isinstance(query, Selector):
                query = query.build()
            req = urllib.request.Request(url,
                                     data=query.encode('utf8'),
                                     method='POST')
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req)
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.SessionFindingError(f'Find documents failed: {json.loads(response.read())}'),
                                header=response.header_items())

The ``grant`` and ``revoke`` methods are specific for enabling and revoking permissions on the current database.

.. code-block:: python

        def grant(self, admins, members):
            url = f"{self.database}/_security"
            data = {"admins": admins, "members": members}
            req = urllib.request.Request(url,
                                     data=json.dumps(data).encode('utf8'),
                                     method='PUT')
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req)
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.SessionACLError(f'Grant failed: {json.loads(response.read())}'),
                                header=response.header_items())

        def revoke(self):
            url = f"{self.database}/_security"
            data = {"admins": {"names": [], "roles": []}, "members": {"names": [], "roles": []}}
            req = urllib.request.Request(url,
                                     data=json.dumps(data).encode('utf8'),
                                     method='PUT')
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req)
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.SessionACLError(f'Revoke failed: {json.loads(response.read())}'),
                                header=response.header_items())

Now let's write the three methods for creating, modifying (also password reset) and deleting a user respectively: ``new_user``, ``set_user`` and ``delete_user``.

.. code-block:: python

        def new_user(self, name, password, roles=None, type='user'):
            if roles is None:
                roles = []
            server = self.database.split('/')
            url = f"{server[0]}//{server[2]}/_users/org.couchdb.user:{name}"
            data = {"name": name, "password": password, "roles": roles, "type": type}
            req = urllib.request.Request(url,
                                     data=json.dumps(data).encode('utf8'),
                                     method='PUT')
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req)
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.SessionACLError(f'New user failed: {json.loads(response.read())}'),
                                header=response.header_items())

        def set_user(self, name, password, rev, roles=None, type='user'):
            if roles is None:
                roles = []
            server = self.database.split('/')
            url = f"{server[0]}//{server[2]}/_users/org.couchdb.user:{name}"
            data = {"name": name, "password": password, "roles": roles, "type": type}
            req = urllib.request.Request(url,
                                     data=json.dumps(data).encode('utf8'),
                                     method='PUT')
            req.add_header('Content-Type', 'application/json')
            req.add_header(f"If-Match: {rev}")
            response = urllib.request.urlopen(req)
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.SessionACLError(f'Modify user or password failed: {json.loads(response.read())}'),
                                header=response.header_items())

        def delete_user(self, name, rev, admin=False):
            server = self.database.split('/')
            if admin:
                url = f"{server[0]}//{server[2]}/_users/org.couchdb.user:{name}"
            else:
                url = f"{server[0]}//{server[2]}/_config/admins/{name}"
            req = urllib.request.Request(url, method='DELETE')
            req.add_header('Content-Type', 'application/json')
            req.add_header(f"If-Match: {rev}")
            response = urllib.request.urlopen(req)
            if response.status_code == 200:
                return Response(data=json.loads(response.read()),
                                code=response.status_code,
                                error=None,
                                header=response.header_items())
            else:
                return Response(data=None,
                                code=response.status_code,
                                error=noslapi.SessionACLError(f'Delete user failed: {json.loads(response.read())}'),
                                header=response.header_items())