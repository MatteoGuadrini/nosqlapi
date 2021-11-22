.. toctree::

nosqlapi column
===============

In this package we find abstract classes and ORM classes concerning the **column** database types.

client module
-------------

The **client** module contains the specific classes for *column* databases and they are based on the `core <nosqlapi_common.html#core-module>`_ classes.

.. automodule:: nosqlapi.columndb.client
    :members:
    :special-members:
    :show-inheritance:

client example
**************

This is an example of a library for connecting to a `cassandra <https://cassandra.apache.org/>`_ server.

.. code-block:: python

    # mykvdb.py
    import nosqlapi

    # this module is my library of NOSQL key-value database, like Redis database

    class Connection(nosqlapi.column.ColumnConnection):
        def __init__(host='localhost', port=7000, database=0, username=None, password=None, ssl=None, tls=None,
                     cert=None, ca_cert=None, ca_bundle=None): ...
        def close(self): ...
        def connect(self, *args, **kwargs): ...
        def create_database(self, database): ...
        def has_database(self, database): ...
        def databases(self): ...
        def delete_database(self): ...
        def show_database(self, database): ...


    class Session(nosqlapi.kvdb.KVSession):
        # define here all methods
        pass

    conn = Connection('mycassandra.local', 'testdb', username='admin', password='pa$$w0rd', tls=True)
    print(conn.show_database('testdb')      # ('testdb', 17983788, 123, False) -- name, size, rows, readonly
    sess = conn.connect()                   # Session object
    ...
