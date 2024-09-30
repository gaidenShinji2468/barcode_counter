import sqlite3
from config import *

connection = sqlite3.connect(DB_NAME)


def exec_many(cbs):
    results = []
    try:
        for cb in cbs:
            results.append(cb(connection))
    except sqlite3.Error as e:
        print(f"Error when executing queries: {e}")
        connection.rollback()
    return results


def exec(cb):
    result = None
    try:
        result = cb(connection)
    except sqlite3.Error as e:
        print(f"Error when executing query: {e}")
        connection.rollback()
    return result


def disconnect():
    connection.close()
