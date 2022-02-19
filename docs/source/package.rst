nosqlapi package
================

The package nosqlapi is a collection of interface, utility class and functions for build your own NOSQL python package.

This library offers API-based interfaces described above, helping to build a more coherent and integrated python library
for a NOSQL database, with names similar to another library using the same interfaces.

The benefit of using ``nosqlapi`` is to standardize the names and syntax for the end user, so as to make as few changes as possible to your software.

Installation
------------

To install the nosqlapi package, run ``pip`` as follows:

.. code-block:: console

    $ pip install nosqlapi #from pypi

    $ git clone https://github.com/MatteoGuadrini/nosqlapi.git #from official repo
    $ cd nosqlapi
    $ python setup.py install

.. toctree::
   :maxdepth: 2
   :caption: Modules:

   nosqlapi_common
   nosqlapi_kv
   nosqlapi_column
   nosqlapi_doc
   nosqlapi_graph
