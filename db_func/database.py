import os
import sys
import sqlite3
import traceback
from sqlite3 import Error


def post_sql_query(sql_query):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'my.db')
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(sql_query)
        except Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
            pass
        result = cursor.fetchall()
        return result


def create_table():
    orders_query = '''CREATE TABLE IF NOT EXISTS DATA
                        (user_id TEXT,
                        phone TEXT,
                        chat_id TEXT);'''
    post_sql_query(orders_query)


def input_new_users(users):
    unique_objects = []
    for user in users:
        sql_selection = f"SELECT * FROM DATA WHERE "\
                            f"phone = '{user[0]}';"
        rows = post_sql_query(sql_selection)
        if not rows:
            query = f"INSERT INTO DATA (phone, user_id) VALUES ('{user[0]}', "\
                    f"'{user[1]}');"
            unique_objects.append(user)
            post_sql_query(query)
    return unique_objects


def check_phone(phone):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"phone = '{phone}';"
    rows = post_sql_query(sql_selection)
    return rows
