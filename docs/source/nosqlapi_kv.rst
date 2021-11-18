.. toctree::

nosqlapi key-value
==================

In this package we find abstract classes and ORM classes concerning the **Key-Value** database types.

client module
-------------

The **client** module contains the specific classes for *key-value* databases and they are based on the `core <nosqlapi_common.html#core-module>`_ classes.

.. automodule:: nosqlapi.kvdb.client
    :members:
    :special-members:
    :show-inheritance:

client example
**************

This is an example of a library for connecting to a `redis <https://redis.io/>`_ server.

.. code-block:: python

    # mykvdb.py
    import nosqlapi

    # this module is my library of NOSQL key-value database, like Redis database

    class Connection(nosqlapi.kvdb.KVConnection):
        def __init__(host='localhost', port=6379, database=0, username=None, password=None, ssl=None, tls=None,
                     cert=None, ca_cert=None, ca_bundle=None): ...
        def close(self): ...
        def connect(self, *args, **kwargs): ...
        def create_database(self):
            raise nosqlapi.DatabaseCreationError('See your server configuration file.')
        def has_database(self, database): ...
        def databases(self): ...
        def delete_database(self): ...
        def show_database(self, database): ...

    conn = Connection('myredis.local', password='pa$$w0rd')
    print(conn.databases(conn.database))    # (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    sess = conn.connect()                   # Session object
    ...
