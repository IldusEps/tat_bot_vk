
from dotenv import load_dotenv
import os
from mysql.connector import connect, Error

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

_connection = None
_cursor = None


def get_connection_cursor():
    global _connection, _cursor
    if not _connection:
        _connection = connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database="words"
        )
        # logging.info(_connection)
    if not _cursor:
        _cursor = _connection.cursor()
    return _connection, _cursor


def ping():
    global _connection, _cursor
    if not _connection:
        _connection = connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database="words"
        )
    if not _cursor:
        _cursor = _connection.cursor()
    _connection.ping(reconnect=True)
    return _cursor


# List of stuff accessible to importers of this module. Just in case
__all__ = ['get_connection_cursor', 'ping']

# Edit: actually you can still refer to db._connection
# if you know that's the name of the variable.
# It's just left out from enumeration if you inspect the module
