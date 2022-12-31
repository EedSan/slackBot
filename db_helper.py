import os

import psycopg2 as connector  # migrated from mysql to postgresql
from dotenv import load_dotenv


def db_connection_open():
    load_dotenv()
    mydb = connector.connect(
        host=os.environ["db_host"],
        user=os.environ["db_user"],
        password=os.environ["db_password"],
        database=os.environ["db_database"])
    return mydb


def check_if_table_is_empty(cursor, table):
    cursor.execute(f"SELECT (CASE WHEN NOT EXISTS(SELECT NULL FROM {table}) THEN 1 ELSE 0 END) AS isEmpty")
    return cursor.fetchall()


def is_user_email_in_db(my_cursor, user_email_):
    my_cursor.execute("SELECT COUNT(*) FROM users WHERE user_email LIKE '{u_email}';".format(u_email=user_email_))
    return my_cursor.fetchall()[0][0]


def is_tag_in_db(my_cursor, tag_name_):
    my_cursor.execute("SELECT COUNT(*) FROM tags WHERE tags.tag_name LIKE '{tag_n}';".format(tag_n=tag_name_))
    return my_cursor.fetchall()[0][0]
