import os
import sys
import telebot
from threading import Thread

import syst.types as types
import syst.mworker as mworker
from syst.tools.output import println


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


# MESSAGES

def sendmsg(msg, text, **kwargs):
    bot.send_message(msg.chat, text, reply_markup='html', **kwargs)


def replymsg(msg, text):
    sendmsg(msg, text, reply_to_message_id=msg.replied.message_id)


def editmsg(msg, text):
    bot.edit_message_text(text, msg.chat, msg.message_id)


def delmsg(msg):
    bot.delete_message(msg.chat, msg.message_id)


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

    message_object = types.Message(msg.content_type, msg.text, msg.chat.id, author, replied,
                                   msg.date, msg.message_id, msg.new_chat_members[1:], 'telegram')

    return message_object


# UPDATERS

@bot.message_handler(func=lambda call: True)
def msglistener(msg):
    message = get_message_object(msg)
    mworker.process_update(self, message)

    println('WRAPPER:telegram', f'[{msg.chat.title}] {get_username(msg)}: {msg.text}')


# INITIALIZATION

def init():
    Thread(target=bot.polling, kwargs={'none_stop': True}).start()
