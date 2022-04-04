.. toctree::

nosqlapi common
===============

In this package you will find the modules that contain common interfaces and `ODMs <https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping>`_
(Object-Data Mapping), shared by all four types of NOSQL database.

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

    # mymodule.py
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


odm module
----------

In the **odm** module, we find generic classes represent real objects present in various NOSQL databases.

.. note::
    These objects are not mandatory for the implementation of their own NOSQL module.
    Rather they serve to help the end user have some consistency in python.

.. automodule:: nosqlapi.common.odm
    :members:
    :special-members:
    :show-inheritance:

odm example
***********

The classes within the module are python representations of real objects in the database.

.. code-block:: python

    import nosqlapi

    null = nosqlapi.common.odm.Null()     # compare with null object into database
    null = nosqlapi.Null()                # in short
    map_ = nosqlapi.Map()                 # like dict
    inet = nosqlapi.Inet('192.168.1.1')   # ipv4/ipv6 addresses

utils module
------------

In the **utils** module, we find classes and functions that help the end user's work.

.. note::
    The functions and classes in this module are meant for the work of the end user and not for those who build libraries.

.. automodule:: nosqlapi.common.utils
    :members:
    :special-members:
    :show-inheritance:

utils example
*************

This is an example of a ``Manager`` object, used to change manage multiple sessions to different types of databases.

.. code-block:: python

    import nosqlapi
    import mymodule
    import othermodule

    connection = mymodule.Connection('server.local', 1241, 'new_db', username='admin', password='pa$$w0rd', ssl=True)
    manager = nosqlapi.common.utils.Manager(connection)

    # Change connection and session
    new_connection = othermodule.Connection('server2.local', 1241, 'other_db', username='admin', password='pa$$w0rd', ssl=True)
    manager.change(new_connection)

    # use connection methods
    manager.create_database('db')
    manager.databases()

    # use session methods
    manager.acl
    manager.get('key')

The ``api`` decorator function allows you to return existing classes so that the methods can match the NOSQL api described in this documentation.

.. code-block:: python

    import nosqlapi
    import pymongo

    @nosqlapi.common.utils.api(database_names='databases', drop_database='delete_database', close_cursor='close')
    class ApiConnection(pymongo.Connection): ...

    connection = ApiConnection('localhost', 27017, 'test_database')

    print(hasattr(connection, 'databases'))     # True

The ``global_session`` function allows you to instantiate a global connection and session.

.. code-block:: python

    import nosqlapi
    import mymodule

    connection = mymodule.Connection('server.local', 1241, 'new_db', username='admin', password='pa$$w0rd', ssl=True)
    nosqlapi.common.utils.global_session(connection)

    print(nosqlapi.CONNECTION)  # Connection object
    print(nosqlapi.SESSION)     # Session object

The ``cursor_response`` function allows you to convert a Response object into a classic list of tuples.

.. code-block:: python

    import nosqlapi
    import mymodule

    connection = mymodule.Connection('server.local', 1241, 'new_db', username='admin', password='pa$$w0rd', ssl=True)
    resp = connection.databases()

    print(resp)                     # Response object
    print(cursor_response(resp))    # [('db1', 'db2')]

The ``apply_vendor`` function allows you to rename representation object from *nosqlapi* to other name

.. code-block:: pycon

    >>> import nosqlapi
    >>> class Response(nosqlapi.Response): ...
    >>> resp = Response('some data')
    >>> resp
    <nosqlapi Response object>
    >>> nosqlapi.apply_vendor('pymongo')
    >>> resp
    <pymongo Response object>