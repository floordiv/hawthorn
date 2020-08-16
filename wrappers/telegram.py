import os
import sys
import time
import telebot
from time import sleep
from threading import Thread

import syst.types as types
import syst.tools.dbm as dbm
import syst.mworker as mworker
from syst.tools.locale import locale
from syst.tools.output import println
import syst.tools.dateparser as dateparser


if 'tg-token' not in os.listdir('data'):
    token = input('Your telegram token> ')

    with open('data/tg-token', 'w') as token_file:
        token_file.write(token)
else:
    with open('data/tg-token') as token:
        token = token.read().strip()


bot = telebot.TeleBot(token)
me = bot.get_me()

self = sys.modules[__name__]    # a link to the wrapper

dbm.open_db('chat-langs', 'CREATE TABLE IF NOT EXISTS chats (platform string, chat string, lang string)')
dbm.execute('chat-langs', 'SELECT * FROM chats WHERE platform = "telegram"')
query_result = dbm.fetchall('chat-langs')  # ((chat_id, lang), (...))

if query_result:
    chat_langs = dict([(chat, lang) for platform, chat, lang in query_result])
else:
    chat_langs = {}


# MESSAGES

def sendmsg(msg, text, **kwargs):
    if str(msg.chat) in chat_langs:
        text = locale(text, to_lang=chat_langs[str(msg.chat)])

    bot.send_message(msg.chat, text, parse_mode='html', **kwargs)


def replymsg(msg, text):
    if str(msg.chat) in chat_langs:
        text = locale(text, to_lang=chat_langs[str(msg.chat)])

    sendmsg(msg, text, reply_to_message_id=msg.message_id)


def editmsg(msg, text):
    if str(msg.chat) in chat_langs:
        text = locale(text, to_lang=chat_langs[str(msg.chat)])

    bot.edit_message_text(text, msg.chat, msg.message_id)


def delmsg(*msgs, chat=None, by_id=False):
    for msg in msgs:
        if not by_id:
            bot.delete_message(msg.chat, msg.message_id)
        else:
            bot.delete_message(chat, msg)    # msg is id of the message


# USER RESTRICTIONS

def mute(msg, duration='1m'):
    if not isinstance(duration, (list, tuple)):
        duration = [*duration]

    until_date = time.time() + dateparser.parse(*duration)
    bot.restrict_chat_member(msg.chat, msg.author.userid, until_date, False, False, False, False)


def unmute(msg, duration='366d'):
    if not isinstance(duration, (list, tuple)):
        duration = [*duration]

    until_date = time.time() + dateparser.parse(*duration)
    bot.restrict_chat_member(msg.chat, msg.author.userid, until_date, True, True, True, True)


def ban(msg, duration='1m'):
    if not isinstance(duration, (list, tuple)):
        duration = [*duration]

    until_date = time.time() + dateparser.parse(*duration)
    bot.kick_chat_member(msg.chat, msg.author.userid, until_date)


def unban(msg, duration='366d'):
    bot.unban_chat_member(msg.chat, msg.author.userid)


# BUTTONS

# TODO: implement buttons support


# HELPERS

def get_username(msg):
    if msg.from_user.username:
        return msg.from_user.username

    name = msg.from_user.first_name

    if msg.from_user.last_name:
        name += ' ' + msg.from_user.last_name

    return name


def get_message_object(msg):
    user_id = msg.from_user.id
    isadmin = user_id in [admin.user.id for admin in bot.get_chat_administrators(msg.chat.id)]\
              or user_id == 502656052

    author = types.User(get_username(msg), user_id, isadmin)

    if msg.reply_to_message:
        replied = get_message_object(msg.reply_to_message)
    else:
        replied = False

    if msg.new_chat_members:
        new_chat_members = msg.new_chat_members[1:]
    else:
        new_chat_members = None

    message_object = types.Message(msg.content_type,
                                   msg.text,
                                   msg.chat.id,
                                   author,
                                   msg.date,
                                   msg.message_id,
                                   replied,
                                   new_chat_members,
                                   'telegram')

    return message_object


# UPDATERS

@bot.message_handler(func=lambda call: True)
def msglistener(msg):
    message = get_message_object(msg)
    mworker.process_update(self, message)

    println('WRAPPER:telegram', f'[{msg.chat.title}] {get_username(msg)}: {msg.text}')


# INITIALIZATION

def init():
    Thread(target=polling).start()


def polling():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as exc:
            println('WRAPPER:telegram', f'An error occurred while polling: {exc}')
            println('WRAPPER:telegram', 'Re-connecting in 5 seconds...')
            sleep(5)
