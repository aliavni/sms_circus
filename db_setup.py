from psycopg2.extensions import connection

from sms_circus.common.db import get_connection


def create_db_structure(con: connection) -> None:
    cursor = con.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id BIGSERIAL PRIMARY KEY,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL,
        failed BOOLEAN DEFAULT FALSE,
        phone TEXT NOT NULL,
        message TEXT NOT NULL
    );
    """)


if __name__ == "__main__":
    conn = get_connection()
    create_db_structure(conn)
    conn.close()
