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

core example
************

Classes on this module are *abstract* (interfaces), therefore, they cannot be instantiated as objects, but inherit them in their own classes.

.. code-block:: python

    import nosqlapi

    # this module is my library of NOSQL database

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
    conn.create_database(conn.database)     # use 'database' attribute equals 'new_db'
    if conn.has_database('new_db'):         # check if database exists
        sess = conn.connect()               # Session object
    else:
        raise nosqlapi.common.exception.ConnectError(f'Connection error with database {conn.database}')
    ...

exception module
----------------

In the **exception** module, we find the exceptions listed in the exceptions table in the `interface <interface.html#exceptions>`_ documentation.

.. note::
    You should never use the `Error` exception class as it is the basis for all exceptions.
    If you have a generic or unknown error, use `UnknownError` instead.

.. automodule:: nosqlapi.common.exception
    :members:
    :show-inheritance:

exception example
*****************

The exceptions stated in this form are used in certain circumstances. See the `table <interface.html#exceptions>`_ of exceptions to find out more.

.. code-block:: python

    import nosqlapi

    raise nosqlapi.common.exception.UnknownError('I have no idea what the hell happened!')
    raise nosqlapi.UnknownError('in short')


orm module
----------

In the **orm** module, we find generic classes represent real objects present in various NOSQL databases.

.. note::
    These objects are not mandatory for the implementation of their own NOSQL module.
    Rather they serve to help the end user have some consistency in python.

.. automodule:: nosqlapi.common.orm
    :members:
    :show-inheritance:

orm example
***********

The classes within the module are python representations of real objects in the database.

.. code-block:: python

    import nosqlapi

    null = nosqlapi.common.orm.Null()     # compare with null object into database
    null = nosqlapi.Null()                # in short
    map_ = nosqlapi.Map()                 # like dict
    inet = nosqlapi.Inet('192.168.1.1')   # ipv4/ipv6 addresses