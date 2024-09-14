import psycopg2
from psycopg2.extensions import connection

from sms_circus.constants import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


def get_connection() -> connection:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        host=DB_HOST,
    )
    conn.set_session(autocommit=True)

    return conn
