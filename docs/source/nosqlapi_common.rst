.. toctree::

nosqlapi common
===============

In this package you will find the modules that contain common interfaces and `ORMs <https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping>`_
(Object-relational mapping), shared by all four types of NOSQL database.


core module
-----------

In the **core** module, we find the abstract classes that form the basis of the classes of all four NOSQL database types.

.. note::
    In theory, you shouldn't use these classes to build your class module for the NOSQL database you plan to build,
    but you could; in all classes you have the necessary methods to iterate with the database server.

.. automodule:: nosqlapi.common.core
    :members:
    :special-members:
    :show-inheritance:

Usage example
*************

Classes are *abstract* (interfaces), therefore, they cannot be instantiated as objects, but inherit them in their own classes.

.. code-block:: python

    import nosqlapi

    class Connection(nosqlapi.common.Connection):
        def __init__(host=None, port=None, database=None, username=None, password=None, ssl=None, tls=None, cert=None,
                     ca_cert=None, ca_bundle=None): ...
        def close(self, force=False): ...
        def connect(self, retry=1): ...
        def create_database(self, database, exists=False): ...
        def has_database(self, database): ...
        def databases(self, return_obj=None): ...
        def delete_database(self, force=False): ...
        def show_database(self, database): ...

    conn = Connection('server.local', 1241, 'new_db', username='admin', password='pa$$w0rd', ssl=True)
    conn.create_database(conn.database)     # use 'database' attribute == 'new_db'
    if conn.has_database('new_db'):         # check if database exists
        sess = conn.connect()               # Session object
    else:
        raise nosqlapi.common.exception.ConnectError(f'Connection error with database {conn.database}')

