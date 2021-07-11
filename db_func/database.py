import os
import sys
import sqlite3
import traceback
from sqlite3 import Error
from loguru import logger


logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


@logger.catch
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


@logger.catch
def create_table():
    query = '''CREATE TABLE IF NOT EXISTS DATA
                        (user_id TEXT,
                        phone TEXT,
                        chat_id TEXT,
                        deal TEXT,
                        name TEXT);'''
    post_sql_query(query)
    query = '''CREATE TABLE IF NOT EXISTS TASKS
                        (user_id TEXT UNIQUE,
                        deal_id TEXT,
                        phone TEXT);'''
    post_sql_query(query)


@logger.catch
def add_user(phone, chat_id, deal, name):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"phone = '{phone}';"
    rows = post_sql_query(sql_selection)
    if not rows:
        query = f"INSERT INTO DATA (phone, chat_id, deal, name) VALUES ('{phone}', "\
                f"'{chat_id}', '{deal}', '{name}');"
        logger.info(post_sql_query(query))
    else:
        query = f"UPDATE DATA SET phone = '{phone}', chat_id = '{chat_id}', "\
                f"deal = '{deal}', name = '{name}' WHERE phone = '{phone}';"
        logger.info(post_sql_query(query))


@logger.catch
def input_new_users(users):
    unique_objects = []
    for user in users:
        logger.info(user)
        sql_selection = f"SELECT * FROM DATA WHERE "\
                            f"phone = '{user[0]}';"
        rows = post_sql_query(sql_selection)
        if not rows:
            query = f"INSERT INTO DATA (phone, user_id) VALUES ('{user[0]}', "\
                    f"'{user[1]}');"
            unique_objects.append(user)
            post_sql_query(query)
    return unique_objects


@logger.catch
def check_phone(phone):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"phone = '{phone}';"
    rows = post_sql_query(sql_selection)
    return rows


@logger.catch
def add_task(user_id, deal_id, phone):
    sql_selection = f"SELECT * FROM TASKS WHERE "\
                        f"user_id = '{user_id}';"
    rows = post_sql_query(sql_selection)
    if not rows:
        query = f"INSERT INTO TASKS (user_id, deal_id, phone) VALUES ('{user_id}', "\
                f"'{deal_id}', '{phone}');"
        post_sql_query(query)


@logger.catch
def get_all_tasks():
    query = f"SELECT * FROM TASKS;"
    tasks = post_sql_query(query)
    return tasks


@logger.catch
def task_active(user_id):
    sql_selection = f"SELECT * FROM TASKS WHERE "\
                        f"user_id = '{user_id}';"
    post_sql_query(sql_selection)
    return bool(post_sql_query(sql_selection))


@logger.catch
def delete_task(user_id):
    sql_selection = f"DELETE FROM TASKS WHERE "\
                        f"user_id = '{user_id}';"
    post_sql_query(sql_selection)


@logger.catch
def check_user(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    return rows
