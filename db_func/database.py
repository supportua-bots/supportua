import os
import sys
import sqlite3
import traceback
from sqlite3 import Error
from loguru import logger


@logger.catch
def post_sql_query(sql_query):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'my.db')
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(sql_query)
        except Error as er:
            logger.info(sql_query)
            logger.info('SQLite error: %s' % (' '.join(er.args)))
            logger.info("Exception class is: ", er.__class__)
            logger.info('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            logger.info(traceback.format_exception(
                exc_type, exc_value, exc_tb))
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
                        (chat_id TEXT,
                        user_id TEXT,
                        deal_id TEXT,
                        phone TEXT,
                        checks TEXT);'''
    post_sql_query(query)


@logger.catch
def add_user(phone, chat_id, deal, name):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if not rows:
        query = f"INSERT INTO DATA (phone, chat_id, deal, name) VALUES ('{phone}', "\
                f"'{chat_id}', '{deal}', '{name}');"
        logger.info(post_sql_query(query))
    else:
        query = f"UPDATE DATA SET phone = '{phone}', chat_id = '{chat_id}', "\
                f"deal = '{deal}', name = '{name}' WHERE chat_id = '{chat_id}';"
        logger.info(post_sql_query(query))


@logger.catch
def input_new_users(users):
    unique_objects = []
    for user in users:
        # logger.info(user)
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
def check_user(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    return rows


@logger.catch
def add_task(chat_id, deal_id, phone):
    sql_selection = f"SELECT * FROM TASKS WHERE "\
                        f"chat_id = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if not rows:
        query = f"INSERT INTO TASKS (chat_id, deal_id, phone, checks) VALUES ('{chat_id}', "\
                f"'{deal_id}', '{phone}', '0');"
        post_sql_query(query)


@logger.catch
def get_all_tasks():
    query = f"SELECT * FROM TASKS;"
    tasks = post_sql_query(query)
    return tasks


@logger.catch
def update_task_counter(chat_id, counter):
    counter += 1
    query = f"UPDATE TASKS SET checks = '{counter}' WHERE chat_id = '{chat_id}';"
    tasks = post_sql_query(query)
    return tasks


# @logger.catch
# def task_active(user_id):
#     sql_selection = f"SELECT * FROM TASKS WHERE "\
#                         f"user_id = '{user_id}';"
#     post_sql_query(sql_selection)
#     return bool(post_sql_query(sql_selection))


@logger.catch
def delete_task(chat_id):
    sql_selection = f"DELETE FROM TASKS WHERE "\
                        f"chat_id = '{chat_id}';"
    post_sql_query(sql_selection)
