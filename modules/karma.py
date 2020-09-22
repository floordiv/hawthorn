from math import sqrt

import syst.tools.dbm as dbm
import syst.mworker as mworker
import syst.tools.filters as filters


dbm.open_db('karma', 'CREATE TABLE IF NOT EXISTS chats (chat string, username string, karma float)')

last_calls = {}  # chat: {user: last_called}


@mworker.handler(lambda msg: filters.command(msg, '+', '-', prefix='', only_command=True) and msg.replied)
def karma_action(wrapper, msg):
    if msg.replied.author.userid == msg.author.userid:
        return wrapper.replymsg(msg, 'No.')

    dbm.execute('karma', 'SELECT * FROM chats WHERE chat = ? AND username = ?',
                params=(msg.chat, msg.author.userid))
    initiator = dbm.fetchone('karma')

    if initiator is None:
        dbm.execute('karma', f"INSERT INTO chats VALUES (?, ?, 1.0)", params=(msg.chat, msg.author.userid), autocommit=True)
        chat, initiator_user_id, initiator_karma = msg.chat, msg.author.userid, 1.0
    elif initiator[2] <= .0:
        return wrapper.replymsg(msg, f'Your karma is not enough ({round(initiator[2], 2)})')
    else:
        chat, initiator_user_id, initiator_karma = initiator

    add_karma = round(sqrt(initiator_karma), 2)

    if msg.content[0] == '-':
        add_karma = -add_karma

    dbm.execute('karma', f'SELECT * FROM chats WHERE chat = ? AND username = ?', params=(msg.chat, msg.replied.author.userid))
    user_exists = dbm.fetchone('karma')

    if user_exists:
        dbm.execute('karma', f'UPDATE chats SET karma = karma + ? WHERE chat = ? AND username = ?',
                    params=(add_karma, msg.chat, msg.replied.author.userid))
    else:
        dbm.execute('karma', f'INSERT INTO chats VALUES (?, ?, ?)', params=(msg.chat, msg.replied.author.userid, 1 + add_karma))

    dbm.commit('karma')

    # get new user's karma
    dbm.execute('karma', f'SELECT * FROM chats WHERE chat = ? AND username = ?', params=(msg.chat, msg.replied.author.userid))
    _, replied_userid, new_replied_user_karma = dbm.fetchone('karma')
    new_replied_user_karma = round(new_replied_user_karma, 2)

    wrapper.replymsg(msg, f'You {"increased" if add_karma > 0 else "decreased"} {msg.replied.author.username}\'s karma up to '
                          f'{new_replied_user_karma} ({"+" if add_karma > 0 else ""}{add_karma})')


@mworker.handler(lambda msg: filters.command(msg, 'me', only_command=True))
def get_my_karma(wrapper, msg):
    dbm.execute('karma', 'SELECT karma FROM chats WHERE chat = ? AND username = ?', params=(msg.chat, msg.author.userid))
    his_karma = dbm.fetchone('karma')[0]

    if not his_karma:
        his_karma = 1.0

    wrapper.replymsg(msg, f'Your karma is {his_karma}')
