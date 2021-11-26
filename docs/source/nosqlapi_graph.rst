.. toctree::

nosqlapi graph
==============

In this package we find abstract classes and ORM classes concerning the **graph** database types.

client module
-------------

The **client** module contains the specific classes for *graph* databases and they are based on the `core <nosqlapi_common.html#core-module>`_ classes.

.. automodule:: nosqlapi.graphdb.client
    :members:
    :special-members:
    :show-inheritance:

client example
**************

This is an example of a library for connecting to a `neo4j <https://neo4j.com/>`_ server.

.. code-block:: python

    # mygraphdb.py
    import nosqlapi

    # this module is my library of NOSQL graph database, like Neo4J database

    class Connection(nosqlapi.graphdb.GraphConnection):
        def __init__(host='localhost', port=7474, database=None, username=None, password=None, ssl=None, tls=None,
                     cert=None, ca_cert=None, ca_bundle=None): ...
        def close(self): ...
        def connect(self, *args, **kwargs): ...
        def create_database(self, database): ...
        def has_database(self, database): ...
        def databases(self): ...
        def delete_database(self): ...
        def show_database(self, database): ...


    class Session(nosqlapi.graphdb.GraphSession):
        # define here all methods
        pass

    conn = Connection('myneo.local', 'mydb', username='admin', password='pa$$w0rd')
    print(conn.show_database('mydb'))       # {"name": "mydb", "address": "myneo.local:7474", "role": "standalone", "requestedStatus": "online", "currentStatus": "online", "error": "", "default": False}
    sess = conn.connect()                   # Session object
    ...

orm module
----------

The **orm** module contains the specific object for *graph* databases.

.. automodule:: nosqlapi.graphdb.orm
    :members:
    :special-members:
    :show-inheritance:

orm example
***********

These objects represent the respective *graph* in databases.

.. code-block:: python

    import nosqlapi
    import mygraphdb

    # Create database
    db = nosqlapi.graphdb.orm.Database('test')
    # Create nodes
    node1 = nosqlapi.graphdb.Node(var='n1', labels=[nosqlapi.graphdb.Label('Person')],
                                  properties=nosqlapi.graphdb.Property({'name': 'Matteo', 'age': 35}))
    node2 = nosqlapi.graphdb.Node(var='n2', labels=[nosqlapi.graphdb.Label('Person')],
                                  properties=nosqlapi.graphdb.Property({'name': 'Julio', 'age': 53}))
    # Add nodes to database
    db.append(node1)
    db.append(node2)

    # Create database with nodes
    mydocdb.conn.create_database(db)