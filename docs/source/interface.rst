.. toctree::
   :maxdepth: 2

Interface
=========

Access and `CRUD <https://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`_ operations in the various types of
databases are standardized in two objects: ``Connection`` and ``Session`` objects.

Constructors
************

Access to the database is made available through ``Connection`` objects. The module must provide the following constructor for these:

.. code-block:: pycon

    >>> connection = Connection(*args, **kwargs)

The ``Connection`` object allows you to access the database and operate directly at the database server level.
This object has a ``connect`` method that returns a ``Session`` object. It takes a number of parameters which are database dependent.

.. code-block:: pycon

    >>> session = connection.connect(*args, **kwargs)

With ``Session`` object you can operate directly on the database data specified when creating the ``Connection`` object.

.. note::
    This division of objects allows you to have more flexibility in case you want to change databases.
    It is not necessary to create a new object to connect to a different database.

Globals
*******

``api_level`` is a global variable to check compatibility with the names defined in this document. Currently the level is *1.0*.

``CONNECTION`` is a global variable where to save a global ``Connection`` object.

``SESSION`` is a global variable where to save a global ``Session`` object.

Exceptions
**********

All defined exceptions derive from the general exception ``Error`` based on ``Exception`` class, which tends not to be used directly.

.. code-block:: pycon

    >>> raise Error("Don't use this, but its subclasses!")

========================== ================= ===========
Name                       Base              Description
========================== ================= ===========
``Error``                  ``Exception``     Exception that is the base class of all other error exceptions. Use only for checks.
``UnknownError``           ``Error``         Exception raised when an unspecified error occurred.
``ConnectError``           ``Error``         Exception raised for errors that are related to the database connection.
``CloseError``             ``Error``         Exception raised for errors that are related to the database close connection.
``DatabaseError``          ``Error``         Exception raised for errors that are related to the database, generally.
``DatabaseCreationError``  ``DatabaseError`` Exception raised for errors that are related to the creation of a database.
``DatabaseDeletionError``  ``DatabaseError`` Exception raised for errors that are related to the deletion of a database.
``SessionError``           ``Error``         Exception raised for errors that are related to the session, generally.
``SessionInsertingError``  ``SessionError``  Exception raised for errors that are related to the inserting data on a database session.
``SessionUpdatingError``   ``SessionError``  Exception raised for errors that are related to the updating data on a database session.
``SessionDeletingError``   ``SessionError``  Exception raised for errors that are related to the deletion data on a database session.
``SessionClosingError``    ``SessionError``  Exception raised for errors that are related to the closing database session.
``SessionFindingError``    ``SessionError``  Exception raised for errors that are related to the finding data on a database session.
``SessionACLError``        ``SessionError``  Exception raised for errors that are related to the grant or revoke permission on a database.
``SelectorError``          ``Error``         Exception raised for errors that are related to the selectors in general.
``SelectorAttributeError`` ``SelectorError`` Exception raised for errors that are related to the selectors attribute.
========================== ================= ===========

The tree of exceptions:

.. code-block::

    Exception
    |__Error
       |__UnknownError
       |__ConnectError
       |__CloseError
       |__DatabaseError
       |  |__DatabaseCreationError
       |  |__DatabaseDeletionError
       |__SessionError
       |  |__SessionInsertingError
       |  |__SessionUpdatingError
       |  |__SessionDeletingError
       |  |__SessionClosingError
       |  |__SessionFindingError
       |  |__SessionACLError
       |__SelectorError
          |__SelectorAttributeError

Selectors
*********

NOSQL databases do not use SQL syntax, or if they do, it is encapsulated in a shell or interpreter.
The selection queries will be driven through ``Selector`` objects which will then be passed to the ``find`` method of a ``Session`` object.

.. code-block:: pycon

    >>> selector = Selector(*args, **kwargs)
    >>> session.find(selector)

.. note::
    A string representing the language of the selector can also be passed to the find method.