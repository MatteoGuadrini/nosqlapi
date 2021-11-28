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

        def create_database(self, name, shards=8, replicas=3, partitioned=False):
            data = {"w": shards, "n": replicas}
            if partitioned:
                data['partitioned'] = partitioned
            req = urllib.request.Request(self.url + f'/{name}',
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
