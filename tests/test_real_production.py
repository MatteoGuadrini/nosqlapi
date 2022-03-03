"""Real production test with pytest."""

import pytest
import nosqlapi


# ------------------Cassandra------------------
def test_connect_cassandra_database():
    """Test connection on production Cassandra database"""
    from .test_columndb import (MyDBConnection as CassandraCon,
                                MyDBSession as CassandraSess)
    # Create Connection object
    connection = CassandraCon('prod-db.test.com', 'admin', 'password', 'db_users')
    assert isinstance(connection, nosqlapi.Connection)
    assert isinstance(connection, nosqlapi.ColumnConnection)
    assert isinstance(connection, CassandraCon)
    assert connection.connected is False
    # Connect to database via Connection object
    session = connection.connect()
    assert isinstance(session, nosqlapi.Session)
    assert isinstance(session, nosqlapi.ColumnSession)
    assert isinstance(session, CassandraSess)
    assert connection.connected is True
    assert session.database == 'db_users'
    assert session.connection is not None
    assert 'admin' in session.description
    # Close Session...but not Connection!
    session.close()
    assert session.database is None
    assert session.connection is None
    # Close also Connection
    connection.close()
    assert connection.connected is False


if __name__ == '__main__':
    pytest.main()
