import sqlite3
from threading import Lock


lock = Lock()
databases = {}  # name: (conn, cursor)


def threadsafe_db_call(func):
    def wrapper(*args, **kwargs):
        try:
            lock.acquire(True)

            func(*args, **kwargs)
        finally:
            lock.release()

    return wrapper


@threadsafe_db_call
def open_db(name, init_query=None):
    if name in databases:
        return

    conn = sqlite3.connect('data/' + name + '.db', check_same_thread=False)
    cursor = conn.cursor()

    databases[name] = (conn, cursor)

    if init_query:
        cursor.execute(init_query)
        conn.commit()


@threadsafe_db_call
def execute(name, sql, params=(), autocommit=False):
    assert name in databases

    try:
        lock.acquire(True)

        conn, cursor = databases[name]
        cursor.execute(sql, params)

        if autocommit:
            conn.commit()
    finally:
        lock.release()


@threadsafe_db_call
def commit(name):
    assert name in databases

    conn, cursor = databases[name]
    conn.commit()


@threadsafe_db_call
def fetchone(name):
    assert name in databases

    conn, cursor = databases[name]

    return cursor.fetchone()


@threadsafe_db_call
def fetchall(name):
    assert name in databases

    conn, cursor = databases[name]

    return cursor.fetchall()


@threadsafe_db_call
def fetchmany(name, size):
    assert name in databases

    conn, cursor = databases[name]

    return cursor.fetchmany(size)
