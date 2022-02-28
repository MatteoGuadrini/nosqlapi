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
        def __init__(host='localhost', port=27017, database=None, username=None, password=None, ssl=None, tls=None,
                     cert=None, ca_cert=None, ca_bundle=None): ...
        def close(self): ...
        def connect(self, *args, **kwargs): ...
        def create_database(self, database): ...
        def has_database(self, database): ...
        def databases(self): ...
        def delete_database(self): ...
        def show_database(self, database): ...
        def copy_database(self, source, destination, force=False): ...


    class Session(nosqlapi.docdb.DocSession):
        # define here all methods
        pass

    conn = Connection('mymongo.local', username='admin', password='pa$$w0rd')
    print(conn.databases())                 # {"databases": [{"name": "admin", "sizeOnDisk": 978944, "empty": False}], "totalSize": 1835008, "ok": 1}
    sess = conn.connect()                   # Session object
    ...

orm module
----------

The **orm** module contains the specific object for *document* databases.

.. automodule:: nosqlapi.docdb.orm
    :members:
    :special-members:
    :show-inheritance:

orm example
***********

These objects represent the respective *document* in databases.

.. code-block:: python

    import nosqlapi
    import mydocdb

    # Create database
    db = nosqlapi.docdb.orm.Database('test')
    # Create documents
    doc1 = nosqlapi.docdb.Document(oid=1)
    doc2 = nosqlapi.docdb.Document(oid=2)
    # Add documents to database
    db.append(doc1)
    db.append(doc2)
    # Create Document object from document decorator
    @nosqlapi.docdb.document
    def user(name, age, salary):
        return {'name': name, 'age': age, 'salary': salary}

    # Create database with docs
    mydocdb.conn.create_database(db)
    # Add more doc
    mydocdb.sess.insert(user('Matteo Guadrini', 36, 25000))