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
.. py:attribute:: connected

This read-only attribute contains a boolean value representing whether the connection has been established with the server.

Connection methods
------------------

.. function:: close(*args, **kwargs)

Immediate closure of the connection and session with the database. Returns ``None``.

.. function:: connect(*args, **kwargs)

Create a persistent session with a specific database. Returns an object of type ``Session``.

.. attention::
    A valid ``Session`` object must necessarily be instantiated with a valid *database* name.

.. function:: create_database(*args, **kwargs)

Create a single database. Returns an object of type ``Response``.

.. function:: has_database(*args, **kwargs)

Check if exists a single database. Returns an object of type ``Response``.

.. function:: delete_database(*args, **kwargs)

Delete of a single database. Returns an object of type ``Response``.

.. function:: databases(*args, **kwargs)

List all databases. Returns an object of type ``Response``.

.. function:: show_database(*args, **kwargs)

Show an information of a specific database. Returns an object of type ``Response``.


Session Objects
***************

The ``Session`` object represents the *session* to a database. With this object it is possible to operate directly on the data.

.. warning::
    This object is derived from the ``connect()`` method of a ``Connection`` object. It is also possible to instantiate the session
    object through a connect function, but it will be mandatory to specify a *database*.

Session attributes
------------------

.. py:attribute:: description

This read-only attribute contains the *session* parameters (can be ``str``, ``tuple`` or ``dict``).

.. py:attribute:: item_count

This read-only attribute contains the number of object returned of an operations (must be ``int``).

.. py:attribute:: database

This read-only attribute contains the name of database in current session (must be ``str``).

.. py:attribute:: acl

This read-only attribute contains the Access Control List in the current session (must be ``tuple``, ``dict`` or ``Response`` object).

.. py:attribute:: indexes

This read-only attribute contains the name of indexes of the current database (must be ``tuple``, ``dict`` or ``Response`` object).

Session methods
---------------

.. function:: get(*args, **kwargs)

Get one or more data from specific database. Returns an object of type ``Response``.

.. attention::
    This is the letter *R* of CRUD operations.

.. function:: insert(*args, **kwargs)

Insert one data on specific database. Returns an object of type ``Response``.

.. attention::
    This is the letter *C* of CRUD operations.

.. function:: insert_many(*args, **kwargs)

Insert one or more data on specific database. Returns an object of type ``Response``.

.. function:: update(*args, **kwargs)

Update one existing data on specific database. Returns an object of type ``Response``.

.. attention::
    This is the letter *U* of CRUD operations.

.. function:: update_many(*args, **kwargs)

Update one or more existing data on specific database. Returns an object of type ``Response``.

.. function:: delete(*args, **kwargs)

Delete one existing data on specific database. Returns an object of type ``Response``.

.. attention::
    This is the letter *D* of CRUD operations.

.. function:: close(*args, **kwargs)
    :noindex:

Close immediately current session. Returns ``None``.

.. function:: find(*args, **kwargs)

Find data on specific database with ``str`` selector or ``Selector`` object. Returns an object of type ``Response``.

.. function:: grant(*args, **kwargs)

Grant *Access Control List* on specific database. Returns an object of type ``Response``.

.. function:: revoke(*args, **kwargs)

Revoke *Access Control List* on specific database. Returns an object of type ``Response``

.. function:: new_user(*args, **kwargs)

Create new normal or admin user. Returns an object of type ``Response``

.. function:: set_user(*args, **kwargs)

Modify exists user or reset password. Returns an object of type ``Response``

.. function:: delete_user(*args, **kwargs)

Delete exists user. Returns an object of type ``Response``

.. function:: add_index(*args, **kwargs)

Add a new index to database. Returns an object of type ``Response``

.. function:: delete_index(*args, **kwargs)

Delete exists index to database. Returns an object of type ``Response``

.. function:: call(batch, *args, **kwargs)

Call a ``Batch`` object to execute one or more statement. Returns an object of type ``Response``

Selector Objects
****************

The ``Selector`` object represents the *query* string for find data from database.
Once instantiated, it can be an input to the ``Session``'s find method.

Selector attributes
-------------------
.. py:attribute:: selector

This read/write attribute represents the selector key/value than you want search.

.. py:attribute:: fields

This read/write attribute represents the fields key that returned from find operations.

.. py:attribute:: partition

This read/write attribute represents the name of partition/collection in a database.

.. py:attribute:: condition

This read/write attribute represents other condition to apply a selectors.

.. py:attribute:: order

This read/write attribute represents order returned from find operations.

.. py:attribute:: limit

This read/write attribute represents limit number of objects returned from find operations.

Selector methods
----------------

.. function:: build(*args, **kwargs)

Building a selector string in the dialect of a NOSQL language based on various property of the ``Selector`` object. Returns ``str``.