import sqlite3


databases = {}  # name: (conn, cursor)


def open_db(name, init_query=None):
    if name in databases:
        return

    conn = sqlite3.connect('data/' + name + '.db', check_same_thread=False)
    cursor = conn.cursor()

    databases[name] = (conn, cursor)

    if init_query:
        cursor.execute(init_query)
        conn.commit()


def execute(name, sql, params=(), autocommit=False):
    assert name in databases

    conn, cursor = databases[name]
    cursor.execute(sql, params)

    if autocommit:
        conn.commit()


def commit(name):
    assert name in databases

    conn, cursor = databases[name]
    conn.commit()


def fetchone(name):
    assert name in databases

    conn, cursor = databases[name]

    return cursor.fetchone()


def fetchall(name):
    assert name in databases

    conn, cursor = databases[name]

    return cursor.fetchall()


def fetchmany(name, size):
    assert name in databases

    conn, cursor = databases[name]

    return cursor.fetchmany(size)
