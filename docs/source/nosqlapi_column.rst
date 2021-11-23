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

    # mycolumndb.py
    import nosqlapi

    # this module is my library of NOSQL column database, like Cassandra database

    class Connection(nosqlapi.columndb.ColumnConnection):
        def __init__(host='localhost', port=7000, database=0, username=None, password=None, ssl=None, tls=None,
                     cert=None, ca_cert=None, ca_bundle=None): ...
        def close(self): ...
        def connect(self, *args, **kwargs): ...
        def create_database(self, database): ...
        def has_database(self, database): ...
        def databases(self): ...
        def delete_database(self): ...
        def show_database(self, database): ...


    class Session(nosqlapi.columndb.ColumnSession):
        # define here all methods
        pass

    conn = Connection('mycassandra.local', 'testdb', username='admin', password='pa$$w0rd', tls=True)
    print(conn.show_database('testdb')      # ('testdb', 17983788, 123, False) -- name, size, rows, readonly
    sess = conn.connect()                   # Session object
    ...

orm module
----------

The **orm** module contains the specific object for *column* databases.

.. automodule:: nosqlapi.columndb.orm
    :members:
    :special-members:
    :show-inheritance:

orm example
***********

These objects represent the respective *column* in databases.

.. code-block:: python

    import nosqlapi
    import mycolumndb

    keyspace = nosqlapi.columndb.orm.Keyspace('new_db')     # in short -> nosqlapi.columndb.Keyspace('new_db')
    # Make columns
    id = nosqlapi.columndb.Column('id', of_type=int)
    id.auto_increment = True                                # increment automatically
    name = nosqlapi.columndb.Column('name', of_type=str)
    # Set data
    id.append()
    name.append('Matteo Guadrini')
    # Make table
    table = nosqlapi.columndb.Table('peoples', id, name)
    # Add table to keyspace
    keyspace.append(table)

    # Create database and insert data
    mycolumndb.conn.create_database(keyspace)
    mycolumndb.sess.insert(keyspace.store[0])
