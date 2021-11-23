.. toctree::

nosqlapi document
=================

In this package we find abstract classes and ORM classes concerning the **document** database types.

client module
-------------

The **client** module contains the specific classes for *document* databases and they are based on the `core <nosqlapi_common.html#core-module>`_ classes.

.. automodule:: nosqlapi.docdb.client
    :members:
    :special-members:
    :show-inheritance:

client example
**************

This is an example of a library for connecting to a `mongodb <https://www.mongodb.com/>`_ server.

.. code-block:: python

    # mydocdb.py
    import nosqlapi

    # this module is my library of NOSQL document database, like MongoDB database

    class Connection(nosqlapi.docdb.DocConnection):
        def __init__(host='localhost', port=27017, database=0, username=None, password=None, ssl=None, tls=None,
                     cert=None, ca_cert=None, ca_bundle=None): ...
        def close(self): ...
        def connect(self, *args, **kwargs): ...
        def create_database(self, database): ...
        def has_database(self, database): ...
        def databases(self): ...
        def delete_database(self): ...
        def show_database(self, database): ...


    class Session(nosqlapi.docdb.DocSession):
        # define here all methods
        pass

    conn = Connection('mymongo.local', username='admin', password='pa$$w0rd')
    print(conn.databases()                  # {"databases": [{"name": "admin", "sizeOnDisk": 978944, "empty": False}], "totalSize": 1835008, "ok": 1}
    sess = conn.connect()                   # Session object
    ...