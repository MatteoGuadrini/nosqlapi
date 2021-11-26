# nosqlapi

_nosqlapi_ is a library for building standard NOSQL python libraries.

> ATTENTION: This is **WIP** in _beta_ version

## Introduction

This library is defined to encourage similarity between Python modules used to access NOSQL databases. 
In this way, I hope for consistency that leads to more easily understood modules, code that generally gets more 
portability across databases and a broader scope of database connectivity from Python.

This document describes the Python NOSQL database API specification.

## Module Interface

### Constructors

Access to the database is made available through connection objects. The module must provide the following constructor for these:

`Connection(parameters...)`

Constructor for creating a connection to the database.
This object has a `connect` method that returns a `Session` object. It takes a number of parameters which are database dependent.

### Globals

`api_level`

String constant stating the supported DB API level.

Currently, only the strings _"1.0"_.

`CONNECTION`

Connection object global variable.

`SESSION`

Session object global variable.

### Exceptions

`Error`

Exception that is the base class of all other error exceptions. You can use this to catch all errors with one single except statement.

`UnknownError`

Exception raised when an unspecified error occurred.
It must be a subclass of `Error`.

`ConnectError`

Exception raised for errors that are related to the database connection.
It must be a subclass of `Error`.

`CloseError`

Exception raised for errors that are related to the database close connection.
It must be a subclass of `Error`.

`DatabaseError`

Exception raised for errors that are related to the database, generally. 
It must be a subclass of `Error`.

`DatabaseCreationError`

Exception raised for errors that are related to the creation of a database. 
It must be a subclass of `DatabaseError`.

`DatabaseDeletionError`

Exception raised for errors that are related to the deletion of a database. 
It must be a subclass of `DatabaseError`.

`SessionError`

Exception raised for errors that are related to the session, generally. 
It must be a subclass of `Error`.

`SessionInsertingError`

Exception raised for errors that are related to the inserting data on a database session. 
It must be a subclass of `SessionError`.

`SessionUpdatingError`

Exception raised for errors that are related to the updating data on a database session. 
It must be a subclass of `SessionError`.

`SessionDeletingError`

Exception raised for errors that are related to the deletion data on a database session. 
It must be a subclass of `SessionError`.

`SessionClosingError`

Exception raised for errors that are related to the closing database session. 
It must be a subclass of `SessionError`.

`SessionFindingError`

Exception raised for errors that are related to the finding data on a database session. 
It must be a subclass of `SessionError`.

`SessionACLError`

Exception raised for errors that are related to the grant or revoke permission on a database. 
It must be a subclass of `SessionError`.

`SelectorError`

Exception raised for errors that are related to the selectors in general.
It must be a subclass of `Error`.

`SelectorAttributeError`

Exception raised for errors that are related to the selectors attribute. 
It must be a subclass of `SelectorError`.

This is the exception inheritance layout:

```
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
```

### Connection Objects

`Connection` objects should respond to the following methods.

#### Connection attributes

`.connected`

This read-only attribute contains a boolean value.

#### Connection methods

`.close(parameters...)`

Closing the connection now.

`.connect(parameters...)`

Connecting to database with the arguments when object has been instantiated and create a Session object to database.

`.create_database(parameters...)`

Creating a single database with position and keyword arguments.

`.has_database(parameters...)`

Checking if exists a single database with position and keyword arguments.

`.delete_database(parameters...)`

Deleting of a single database with position and keyword arguments.

`.databases(parameters...)`

List all databases.

`.show_database(parameters...)`

Show an information of a specific database

### Session Objects

`Session` objects should respond to the following methods.

> ATTENTION: Session object it will come instantiated if the Connection object contains a database value.

#### Session attributes

`.description`

This read-only attribute contains the session parameters (can be string, list or dictionary).

`.item_count`

This read-only attribute contains the number of object returned of an operations.

`.database`

This read-only attribute contains the name of database in current session.

`.acl`

This read-only attribute contains the _Access Control List_ in the current session.

`.indexes`

This read-only attribute contains the name of indexes of the current database.


#### Session methods

`.get(parameters...)`

Getting one or more data on specific database with position and keyword arguments.

`.insert(parameters...)`

Inserting one data on specific database with position and keyword arguments.

`.insert_many(parameters...)`

Inserting one or more data on specific database with position and keyword arguments.

`.update(parameters...)`

Updating one existing data on specific database with position and keyword arguments.

`.update_many(parameters...)`

Updating one or more existing data on specific database with position and keyword arguments.

`.delete(parameters...)`

Deleting one existing data on specific database with position and keyword arguments.

`.close(parameters...)`

Closing the session and connection now.

`.find(parameters...)`

Finding data on specific database with string selector or `Selector` object with position and keyword arguments.

`.grant(parameters...)`

Granting ACL on specific database with position and keyword arguments.

`.revoke(parameters...)`

Revoking ACL on specific database with position and keyword arguments.

`.new_user(parameters...)`

Creating new normal or admin user. 

`.set_user(parameters...)`

Modifying exists user or reset password.

`.delete_user(parameters...)`

Deleting exists user.

`.add_index(parameters...)`

Adding a new index to database.

`.delete_index(parameters...)`

Deleting exists index to database.

`.call(batch, parameters...)`

Calling a batch object to execute one or more statement.

### Selector Objects

`Selector` objects should respond to the following methods.

#### Selector attributes

`.selector`

This read/write attribute represents the _selector_ key/value than you want search.

`.fields`

This read/write attribute represents the _fields_ key that returned from find operations. 

`.partition`

This read/write attribute represents the name of _partition/collection_ in a database.

`.condition`

This read/write attribute represents other _condition_ to apply a selectors.

`.order`

This read/write attribute represents _order_ returned from find operations.

`.limit`

This read/write attribute represents _limit_ number of objects returned from find operations.

#### Selector methods

`.build(parameters...)`

Building a _selector_ string in the dialect of a NOSQL language based on various property of the `Selector` object.

### Response Objects

`Response` objects should respond to the following attributes.

> `Response` objects is a species of an either-data type, because contains both success and error values

#### Response attributes

`.data`

This read-only attribute represents the effective data than returned (_Any_ object).

`.code`

This read-only attribute represents a number code of error or success in an operation.

`.header`

This read-only attribute represents a string information (header) of an operation.

`.error`

This read-only attribute represents a string error of an operation.

`.dict`

This read-only attribute represents a dictionary transformation of Response object.

### Batch Objects

`Batch` objects should respond to the following methods.

#### Batch attributes

`.session`

This read/write attribute represents a `Session` object.

`.batch`

This read/write attribute represents a _batch_ operation.

#### Batch methods

`.execute(parameters...)`

Executing a _batch_ operation with position and keyword arguments.

## nosqlapi package

The package _nosqlapi_ is a collection of interface and utility class and functions for build your own NOSQL python package.

### Test and installation
To test this package.

```console
$ git clone https://github.com/MatteoGuadrini/nosqlapi.git
$ cd nosqlapi
$ python -m unittest discover tests
```

Instead, to install package.

```console
$ pip install nosqlapi #from pypi

$ git clone https://github.com/MatteoGuadrini/nosqlapi.git #from official repo
$ cd nosqlapi
$ python setup.py install
```

### Type of NoSql Database

NoSql databases are of four types:

- Key/Value database
- Column database
- Document database
- Graph database

For each type of database, _nosqlapi_ offers standard interfaces, in order to unify as much as possible the names of methods and functions.

For an example, just look at the relevant package test files.

Look as each test module has same class and each class has same method name.
For instance, look at **MyDBSession** class as inherit for each _nosqlapi_ type of abstract class:

```console
$ grep "class MyDBSession" tests/*
tests/test_columndb.py:class MyDBSession(nosqlapi.columndb.ColumnSession):
tests/test_docdb.py:class MyDBSession(nosqlapi.docdb.DocSession):
tests/test_graphdb.py:class MyDBSession(nosqlapi.graphdb.GraphSession):
tests/test_kvdb.py:class MyDBSession(nosqlapi.kvdb.KVSession):
```

### Key-Value database
A key–value database, or key–value store, is a data storage paradigm designed for storing, retrieving, and managing associative arrays, 
and a data structure more commonly known today as a dictionary or hash table. Dictionaries contain a collection of objects, or records, 
which in turn have many different fields within them, each containing data. These records are stored and retrieved using a key that 
uniquely identifies the record, and is used to find the data within the database.

```python
import nosqlapi.kvdb

# Redis like database
class RedisConnection(nosqlapi.kvdb.KVConnection):...
class RedisSession(nosqlapi.kvdb.KVSession):...
class RedisResponse(nosqlapi.kvdb.KVResponse):...
class RedisBatch(nosqlapi.kvdb.KVBatch):...
class RedisSelector(nosqlapi.kvdb.KVSelector):...

# Use Redis library
conn = RedisConnection(host='server.local', username='admin', password='pass', database='db')
sess = conn.connect()       # return RedisSession object
# Create a new database
conn.create_database('new_db')

# CRUD operation
C = sess.insert('key', 'value')         # Create
R = sess.get('key')                     # Read
U = sess.update('key', 'new_value')     # Update
D = sess.delete('key')                  # Delete

print(R)                                    # {'key': 'value'}
print(type(R))                              # <class 'RedisResponse'>
print(isinstance(R, nosqlapi.Response))     # True

# Extended CRUD operations
sess.insert_many({'key1': 'value1', 'Key2': 'value2'})
sess.update_many({'key1': 'new_value1', 'Key2': 'new_value2'})

# Complex select operation
sel = RedisSelector(selector='key:value id:1 ttl:300', limit=2)
sess.find(sel)

# Batch operations
op = 'SET hello "Hello"\nSET mykey "new"\nGET mykey\nSET anotherkey "will expire in a minute" EX 60'
batch = RedisBatch(batch=op, session=sess)
resp = batch.execute()
print(resp)            # ('OK', 'OK', {'mykey': 'new'}, 'OK')
print(type(resp))      # <class 'RedisResponse'>

```

### Column database
A column-oriented DBMS or columnar DBMS is a database management system (DBMS) that stores data tables by column rather than by row. 
Practical use of a column store versus a row store differs little in the relational DBMS world. Both columnar and row databases 
can use traditional database query languages like SQL to load data and perform queries. Both row and columnar databases can 
become the backbone in a system to serve data for common extract, transform, load (ETL) and data visualization tools. 
However, by storing data in columns rather than rows, the database can more precisely access the data it needs to answer 
a query rather than scanning and discarding unwanted data in rows.

```python
import nosqlapi.columndb

# Cassandra like database
class CassandraConnection(nosqlapi.columndb.ColumnConnection):...
class CassandraSession(nosqlapi.columndb.ColumnSession):...
class CassandraResponse(nosqlapi.columndb.ColumnResponse):...
class CassandraBatch(nosqlapi.columndb.ColumnBatch):...
class CassandraSelector(nosqlapi.columndb.ColumnSelector):...

# Use Cassandra library
conn = CassandraConnection(host='server.local', username='admin', password='pass', database='db')
sess = conn.connect()       # return CassandraSession object
# Create a new database
conn.create_database('new_db')

# CRUD operation
C = sess.insert(table='hitchhikers', columns=('id', 'name', 'age'), values=(1, 'Arthur', 42))            # Create
R = sess.get(table='hitchhikers', columns=('id', 'name', 'age'))                                         # Read
U = sess.update(table='hitchhikers', columns=('id', 'name', 'age'), values=(1, 'Arthur', 43))            # Update
D = sess.delete(table='hitchhikers', conditions=["name='Arthur'", 'age=43'])                             # Delete

print(R)                                    # [(1, 'Arthur', 42)]
print(type(R))                              # <class 'CassandraResponse'>
print(isinstance(R, nosqlapi.Response))     # True

# Extended CRUD operations
sess.insert_many(table='hitchhikers', columns=('id', 'name', 'age'), values=[(1, 'Arthur', 42), (2, 'Arthur', 43)])
sess.update_many(table='hitchhikers', columns=('id', 'name', 'age'), values=[(1, 'Arthur', 44), (2, 'Arthur', 45)])

# Complex select operation
sel = CassandraSelector()
# Table
sel.selector = 'hitchhikers'
# Columns
sel.fields = ['id', 'name', 'age']
sess.find(sel)

# Batch operations
op = "BEGIN BATCH\nINSERT INTO hitchhikers (id, name, age)\n VALUES (1, 'Arthur', 42)\nIF NOT EXISTS;\nAPPLY BATCH;"
batch = CassandraBatch(batch=op, session=sess)
resp = batch.execute()
print(resp)            # [(1, 'Arthur', 42)]
print(type(resp))      # <class 'CassandraResponse'>

```

### Document database
A document-oriented database, or document store, is a computer program and data storage system designed for storing, 
retrieving and managing document-oriented information, also known as semi-structured data.

Document-oriented databases are one of the main categories of NoSQL databases, and the popularity of the term 
_"document-oriented database"_ has grown with the use of the term NoSQL itself. Graph databases are similar, but add another 
layer, the relationship, which allows them to link documents for rapid traversal.

```python
import nosqlapi.docdb

# MongoDB like database
class MongoConnection(nosqlapi.docdb.DocConnection):...
class MongoSession(nosqlapi.docdb.DocSession):...
class MongoResponse(nosqlapi.docdb.DocResponse):...
class MongoBatch(nosqlapi.docdb.DocBatch):...
class MongoSelector(nosqlapi.docdb.DocSelector):...

# Use MongoDB library
conn = MongoConnection(host='server.local', username='admin', password='pass')
sess = conn.connect()       # return MongoSession object
# Create a new database
conn.create_database('new_db')

# CRUD operation
C = sess.insert(path='db/doc1', doc={"_id": "5099803df3f4948bd2f98391", "name": "Arthur", "age": 42})           # Create
R = sess.get(path='db/doc1')                                                                                    # Read
U = sess.update(path='db/doc1', doc={"_id": "5099803df3f4948bd2f98391", "name": "Arthur", "age": 43}, rev=2)    # Update
D = sess.delete(path='db/doc1', rev=2)                                                                          # Delete

print(R)                                    # {"_id": "5099803df3f4948bd2f98391", "rev"= 2, "name": "Arthur", "age": 42}
print(type(R))                              # <class 'MongoResponse'>
print(isinstance(R, nosqlapi.Response))     # True

# Extended CRUD operations
sess.insert_many(database='db', docs=[{"_id": "5099803df3f4948bd2f98391", "name": "Arthur", "age": 42}, 
                 {"_id": "5099803df3f4948bd2f98392", "name": "Arthur", "age": 43}])
sess.update_many(database='db', docs=[{"_id": "5099803df3f4948bd2f98391", "name": "Arthur", "age": 42, "rev": 2}, 
                 {"_id": "5099803df3f4948bd2f98392", "name": "Arthur", "age": 43, "rev": 2}])

# Complex select operation
sel = MongoSelector(selector={"name": "Arthur"}, fields=['_id', 'name', 'age'], limit=2)
sess.find(sel)

# Batch operations
op = [{"_id": "5099803df3f4948bd2f98391", "name": "Arthur", "age": 42}, {"_id": "5099803df3f4948bd2f98392", "name": "Arthur", "age": 43}]
batch = MongoBatch(batch=op, session=sess)
resp = batch.execute(crud='insert')
print(resp)            # [{"_id": "5099803df3f4948bd2f98391", "rev"= 2, "name": "Arthur", "age": 42}, {"_id": "5099803df3f4948bd2f98392", "rev"= 2, "name": "Arthur", "age": 43}]
print(type(resp))      # <class 'MongoResponse'>

```

### Graph database
Graph databases are a type of NoSQL database, created to address the limitations of relational databases. 
While the graph model explicitly lays out the dependencies between nodes of data, the relational model and other 
NoSQL database models link the data by implicit connections. In other words, relationships are a first-class citizen 
in a graph database and can be labelled, directed, and given properties. This is compared to relational approaches where 
these relationships are implied and must be reified at run-time. Graph databases are similar to 1970s network model 
databases in that both represent general graphs, but network-model databases operate at a lower level of abstraction 
and lack easy traversal over a chain of edges.

```python
import nosqlapi.graphdb

# Neo4j like database
class Neo4jConnection(nosqlapi.graphdb.GraphConnection):...
class Neo4jSession(nosqlapi.graphdb.GraphSession):...
class Neo4jResponse(nosqlapi.graphdb.GraphResponse):...
class Neo4jBatch(nosqlapi.graphdb.GraphBatch):...
class Neo4jSelector(nosqlapi.graphdb.GraphSelector):...

# Use Neo4j library
conn = Neo4jConnection(host='server.local', username='admin', password='pass', database='db')
sess = conn.connect()       # return Neo4jSession object
# Create a new database
conn.create_database('new_db')

# CRUD operation
C = sess.insert(node='n:Person', properties={'name': 'Arthur', 'age': 42})           # Create
R = sess.get(node='n:Person')                                                        # Read
U = sess.update(node='n:Person', properties={'name': 'Arthur', 'age': 42})           # Update
D = sess.delete(node='n:Person')                                                     # Delete

print(R)                                    # {'n.name': 'Arthur', 'n.age': 42}
print(type(R))                              # <class 'Neo4jResponse'>
print(isinstance(R, nosqlapi.Response))     # True

# Extended CRUD operations
sess.insert_many(nodes=['matteo:Person', 'arthur:Person'], properties=[{'name': 'Matteo', 'age': 35}, 
                                                                       {'name': 'Arthur', 'age': 42}])
sess.update_many(nodes=['matteo:Person', 'arthur:Person'], properties=[{'name': 'Matteo', 'age': 35}, 
                                                                       {'name': 'Arthur', 'age': 42}])
sess.link(node='arthur:Person{name: "Arthur"}', to_link='book:hitchhikers', relationship=':ACT_IN')
sess.detach(node='arthur:Person{name: "Arthur"}')

# Complex select operation
sel = Neo4jSelector(selector='people:Person', fields=['name', 'age'], condition='people.age>=35', order='age', limit=2)
sess.find(sel)

# Batch operations
op = "MATCH (p:Person {name: 'Arhur'})-[rel:ACT_IN]-(:Book {name: 'hitchhikers'})\nSET rel.startYear = date({year: 2018})\nRETURN p"
batch = Neo4jBatch(batch=op, session=sess)
resp = batch.execute()
print(resp)            # {'p.name': 'Arhur', 'p.age': 42}
print(type(resp))      # <class 'Neo4jResponse'>

```

### ORM (Object-relational mapping)
For each type of NOSQL database there is an _ORM (Object-relational mapping)_ module that contains classes and functions relating to the mapping of 
objects and/or operations concerning the specific database _CRUD operation_.

In the `nosqlapi.common.orm` module there are also classes that represent the data types of databases.

```pycon
>>> import nosqlapi.common.orm
>>> [t for t in dir(nosqlapi.common.orm) if not t.startswith('__')]
['Array', 'Ascii', 'Blob', 'Boolean', 'Counter', 'Date', 'Dc', 'Decimal', 'Double', 'Duration', 'Float', 'Inet', 'Int', 
'List', 'Map', 'Null', 'SmallInt', 'Text', 'Time', 'Timestamp', 'Uuid', 'Varchar']
```

### Utilities
The package also comes with useful classes and functions to help migrate a library to these APIs. 
Besides, these there are also some utilities for end users.

#### api decorator

```python
import nosqlapi
from pymongo import Connection

# This decorator allows you to map existing method names to API compliant methods.
@nosqlapi.api(database_names='databases', drop_database='delete_database', close_cursor='close')
class ApiConnection(Connection):
    pass

conn = ApiConnection('localhost', 27017, 'test_database')
hasattr(conn, 'databases')      # True
conn.databases()                # (test_database, 'db1', 'db2')
```

#### Manager session

```python
import nosqlapi
from neo4j import Neo4jConnection
from mymongo import MongoConnection

# Create manager for session API
man = nosqlapi.Manager(Neo4jConnection(host='server.local', username='admin', password='pass', database='db'))
print(type(man))        # <class 'Manager'>
print(man)              # database=db, description=('db', 'online')

# CRUD operation
C = man.insert(node='n:Person', properties={'name': 'Arthur', 'age': 42})           # Create
R = man.get(node='n:Person')                                                        # Read
U = man.update(node='n:Person', properties={'name': 'Arthur', 'age': 42})           # Update
D = man.delete(node='n:Person')                                                     # Delete

# Change session
man.change(MongoConnection(host='server.local', username='admin', password='pass', database='db'))
C = man.insert(path='db/doc1', doc={"_id": "5099803df3f4948bd2f98391", "name": "Arthur", "age": 42})           # Create
R = man.get(path='db/doc1')                                                                                    # Read
U = man.update(path='db/doc1', doc={"_id": "5099803df3f4948bd2f98391", "name": "Arthur", "age": 43}, rev=2)    # Update
D = man.delete(path='db/doc1', rev=2)                                                                          # Delete
```

## Open source
_nosqlapi_ is an open source project. Any contribute, It's welcome.

**A great thanks**.

For donations, press this

For me

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/guos)

For [Telethon](http://www.telethon.it/)

The Telethon Foundation is a non-profit organization recognized by the Ministry of University and Scientific and Technological Research.
They were born in 1990 to respond to the appeal of patients suffering from rare diseases.
Come today, we are organized to dare to listen to them and answers, every day of the year.

<a href="https://www.telethon.it/sostienici/dona-ora"> <img src="https://www.telethon.it/dev/_nuxt/img/c6d474e.svg" alt="Telethon" title="Telethon" width="200" height="104" /> </a>

[Adopt the future](https://www.ioadottoilfuturo.it/)


## Acknowledgments

Thanks to Mark Lutz for writing the _Learning Python_ and _Programming Python_ books that make up my python foundation.

Thanks to Kenneth Reitz and Tanya Schlusser for writing the _The Hitchhiker’s Guide to Python_ books.

Thanks to Dane Hillard for writing the _Practices of the Python Pro_ books.

Special thanks go to my wife, who understood the hours of absence for this development. 
Thanks to my children, for the daily inspiration they give me and to make me realize, that life must be simple.

Thanks Python!