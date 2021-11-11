.. toctree::
   :maxdepth: 2


API
===

The following describes the object APIs that will build a connection to databases.
All the method names that are present below are common to all Nosql database types.

.. note::
    Some methods are specific to certain types of databases, so they will not be present in all objects.

Connection Objects
******************

The ``Connection`` object creates a layer concerning the connection to the server.
You can not specify any specific databases; in this way, the object will be used for the creation and management of all databases at the server level.

Connection attributes
---------------------

**.connected**

This read-only attribute contains a boolean value representing whether the connection has been established with the server.

Connection methods
------------------

**.close(*args, \*\*kwargs)**

Immediate closure of the connection with the database. Returns ``None``.

**.connect(*args, \*\*kwargs)**

Create a persistent session with a specific database. Returns an object of type ``Session``.

**.create_database(*args, \*\*kwargs)**

Creating a single database. Returns an object of type ``Response``.

**.has_database(*args, \*\*kwargs)**

Checking if exists a single database. Returns an object of type ``Response``.

**.delete_database(*args, \*\*kwargs)**

Deleting of a single database. Returns an object of type ``Response``.

**.delete_database(*args, \*\*kwargs)**

Deleting of a single database. Returns an object of type ``Response``.

**.databases(*args, \*\*kwargs)**

List all databases. Returns an object of type ``Response``.

**.show_database(*args, \*\*kwargs)**

Show an information of a specific database. Returns an object of type ``Response``.
