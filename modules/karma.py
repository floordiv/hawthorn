import sqlite3
from math import sqrt

import syst.mworker as mworker
import syst.tools.filters as filters


conn = sqlite3.connect('./data/karma.sqlite', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS chats (chat string, username string, karma float)')
conn.commit()

last_calls = {}  # chat: {user: last_called}


@mworker.handler(lambda msg: filters.command(msg, '+', '-', prefix='', only_command=True) and msg.replied)
def karma_action(wrapper, msg):
    if msg.replied.author.userid == msg.author.userid or floodwait(msg):
        return wrapper.replymsg(msg, 'No.')

    cursor.execute('SELECT * FROM chats WHERE chat = ? AND username = ?', (msg.chat, msg.author.userid))
    initiator = cursor.fetchone()

    if initiator is None:
        cursor.execute("INSERT INTO chats VALUES (?, ?, 1.0)", (msg.chat, msg.author.userid))
        conn.commit()

        chat, initiator_user_id, initiator_karma = msg.chat, msg.author.userid, 1.0
    elif initiator[2] <= .0:
        return wrapper.replymsg(msg, f'Your karma is not enough ({round(initiator[2], 2)})')
    else:
        chat, initiator_user_id, initiator_karma = initiator

    add_karma = round(sqrt(initiator_karma), 2)

    if msg.content[0] == '-':
        add_karma = -add_karma

    cursor.execute('SELECT * FROM chats WHERE chat = ? AND username = ?', (msg.chat, msg.replied.author.userid))
    user_exists = cursor.fetchone()

    if user_exists:
        cursor.execute('UPDATE chats SET karma = karma + ? WHERE chat = ? AND username = ?', (add_karma, msg.chat,
                                                                                               msg.replied.author.userid))
    else:
        cursor.execute('INSERT INTO chats VALUES (?, ?, ?)', (msg.chat, msg.replied.author.userid, 1 + add_karma))

    conn.commit()

    # get new user's karma
    cursor.execute('SELECT * FROM chats WHERE chat = ? AND username = ?', (msg.chat, msg.replied.author.userid))
    _, replied_userid, new_replied_user_karma = cursor.fetchone()
    new_replied_user_karma = round(new_replied_user_karma, 2)

    wrapper.replymsg(msg, f'You {"increased" if add_karma > 0 else "decreased"} {msg.replied.author.username}\'s karma up to '
                          f'{new_replied_user_karma} ({"+" if add_karma > 0 else ""}{add_karma})')


@mworker.handler(lambda msg: filters.command(msg, 'me', only_command=True))
def get_my_karma(wrapper, msg):
    cursor.execute('SELECT karma FROM chats WHERE chat = ? AND username = ?', (msg.chat, msg.author.userid))
    his_karma = cursor.fetchone()[0]

    if not his_karma:
        his_karma = 1.0

    wrapper.replymsg(msg, f'Your karma is {round(his_karma, 2)}')


def floodwait(msg):
    chat_exists = msg.chat in last_calls
    user_exists = chat_exists and msg.author.userid in last_calls[msg.chat]

    if not chat_exists:
        last_calls[msg.chat] = {msg.author.userid: msg.date}
    elif not user_exists:
        last_calls[msg.chat][msg.author.userid] = msg.date
    else:
        return msg.date - last_calls[msg.chat][msg.author.userid] < 15
