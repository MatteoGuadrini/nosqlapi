# nosqlapi

_nosqlapi_ is a library for building standard NOSQL python libraries.

> ATTENTION: This is **WIP** in _alpha_ version

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
Returns a `Session` object. It takes a number of parameters which are database dependent.

### Globals

`api_level`

String constant stating the supported DB API level.

Currently only the strings "1.0".

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

#### Connection methods

`.close()`

Closing the connection now.

`.connect()`

Connecting to database with the arguments when object has been instantiated.

`.create_database(parameters...)`

Creating a single database with position and keyword arguments.

`.has_database(parameters...)`

Checking if exists a single database with position and keyword arguments.

`.delete_database(parameters...)`

Deleting of a single database with position and keyword arguments.

`.databases()`

List all databases.

### Session Objects

`Session` objects should respond to the following methods.

> ATTENTION: Session object it will come instantiated if the Connection object contains a database value.

#### Session attributes

`.description`

This read-only attribute contains the session parameters (can be string, list or dictionary).

`.item_count`

This read-only attribute contains the number of object returned of an operations.

`.acl`

This read-only attribute contains the _Access Control List_ in the current session.


#### Session methods

`.get(parameters...)`

Getting one or more data on specific database with position and keyword arguments.

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

`.close()`

Closing the session and connection now.

`.find(parameters...)`

Finding data on specific database with string selector or `Selector` object with position and keyword arguments.

`.grant(parameters...)`

Granting ACL on specific database with position and keyword arguments.

`.revoke(parameters...)`

Revoking ACL on specific database with position and keyword arguments.

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

`.build()`

Building a _selector_ string in the dialect of a NOSQL language based on various property of the `Selector` object.

### Response Objects

`Response` objects should respond to the following attributes.

> `Response` objects is a species of an either type, because contains both success and error values

#### Response attributes

`.data`

This read-only attribute represents the effective data than returned (_Any_ object).

`.code`

This read-only attribute represents a number code of error or success in an operation.

`.header`

This read-only attribute represents a string information (header) of an operation.

`.error`

This read-only attribute represents a string error of an operation.

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