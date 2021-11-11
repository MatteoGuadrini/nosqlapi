.. nosqlapi documentation master file, created by
   sphinx-quickstart on Tue Nov  9 09:37:56 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to nosqlapi's documentation!
====================================

This library is defined to encourage similarity between Python modules used to access **NOSQL** databases.
In this way, I hope for consistency that leads to more easily understood modules,
code that generally gets more portability across databases and a broader scope of database connectivity from Python.
This document describes the *Python NOSQL database API* specification.

Supported NOSQL database types
******************************

NoSql databases are of four types:

- Key/Value database
- Column database
- Document database
- Graph database

For each type of database, *nosqlapi* offers standard interfaces, in order to unify as much as possible the names of methods and functions.


Key-Value database
------------------

A **key–value database**, or key–value store, is a data storage paradigm designed for storing, retrieving,
and managing associative arrays, and a data structure more commonly known today as a dictionary or hash table.
Dictionaries contain a collection of objects, or records, which in turn have many different fields within them, each containing data.
These records are stored and retrieved using a key that uniquely identifies the record, and is used to find the data within the database.

Column database
---------------

A **column-oriented DBMS** or columnar DBMS is a database management system (DBMS) that stores data tables by column rather than by row.
Practical use of a column store versus a row store differs little in the relational DBMS world.
Both columnar and row databases can use traditional database query languages like SQL to load data and perform queries.
Both row and columnar databases can become the backbone in a system to serve data for common extract, transform, load (ETL) and data visualization tools.
However, by storing data in columns rather than rows, the database can more precisely access the data it needs to answer
a query rather than scanning and discarding unwanted data in rows.

Document database
-----------------

A **document-oriented database**, or document store, is a computer program and data storage system designed for storing,
retrieving and managing document-oriented information, also known as semi-structured data.
Document-oriented databases are one of the main categories of NoSQL databases, and the popularity of the term
*"document-oriented database"* has grown with the use of the term NoSQL itself.
Graph databases are similar, but add another layer, the relationship, which allows them to link documents for rapid traversal.

Graph database
--------------

**Graph databases** are a type of NoSQL database, created to address the limitations of relational databases.
While the graph model explicitly lays out the dependencies between nodes of data, the relational model and other NoSQL
database models link the data by implicit connections. In other words, relationships are a first-class citizen in a
graph database and can be labelled, directed, and given properties. This is compared to relational approaches where
these relationships are implied and must be reified at run-time.
Graph databases are similar to 1970s network model databases in that both represent general graphs,
but network-model databases operate at a lower level of abstraction and lack easy traversal over a chain of edges.

Contents
========

.. toctree::
   :maxdepth: 2

   interface
   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
