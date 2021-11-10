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

``CONNECTION`` is a global variable where to save a ``Connection`` object.

``SESSION`` is a global variable where to save a ``Session`` object.