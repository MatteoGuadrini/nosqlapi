.. toctree::

Build a library
===============

In this section we will build a **NOSQL API** compliant library, using the ``nosqlapi`` library.
We will first build the core objects that will allow us to connect and operate with our database.

.. note::
    The following example is designed for a NOSQL database of the Document type; by changing the application logic of
    the various methods in the classes you can build a library for another type of NOSQL database in the same way.
    The procedures are the same.

Let's prepare the steps:

* write ``core.py``, with core classes and functions.
* write ``utils.py``, with utility classes and function, like ORM objects.

Core
----

The **core** classes must provide a connection and operation interface towards the database.
All *CRUD* operations will need to be supported. We can implement new ones, based on the type of database we support.

Create a ``core.py`` module.

.. code-block:: python

    #!/usr/bin/env python3
    # -*- encoding: utf-8 -*-
    # core.py

    """Python library for document CouchDB server"""

    import nosqlapi
    import urllib.request
