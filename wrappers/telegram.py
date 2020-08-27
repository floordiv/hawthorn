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

wrapper = sys.modules[__name__]    # a link to the wrapper

DEFAULT_CHAT_LANG = 'en'


dbm.open_db('chat-langs', 'CREATE TABLE IF NOT EXISTS chats (platform string, chat string, lang string)')
dbm.execute('chat-langs', 'SELECT * FROM chats WHERE platform = "telegram"')
query_result = dbm.fetchall('chat-langs')  # ((chat_id, lang), (...))

if query_result:
    chat_langs = dict([(chat, lang) for platform, chat, lang in query_result])
else:
    chat_langs = {}


# MESSAGES

def sendmsg(msg, text, keyboard=None, **kwargs):
    text = locale_text(msg.chat, text)

    if keyboard:
        telebot_keyboard = keyboard.convert()
        kwargs['reply_markup'] = telebot_keyboard

        keyboard.handle()

    bot.send_message(msg.chat, text, parse_mode='html', **kwargs)


def replymsg(msg, text, keyboard=None, **kwargs):
    text = locale_text(msg.chat, text)

    if keyboard:
        telebot_keyboard = keyboard.convert()
        kwargs['reply_markup'] = telebot_keyboard

        keyboard.handle()

    sendmsg(msg, text, reply_to_message_id=msg.message_id, **kwargs)


def editmsg(msg, text, keyboard=None, **kwargs):
    text = locale_text(msg.chat, text)

    if keyboard:
        telebot_keyboard = keyboard.convert()
        kwargs['reply_markup'] = telebot_keyboard

        keyboard.handle()

    bot.edit_message_text(text, msg.chat, msg.message_id, **kwargs)


def delmsg(*msgs, chat=None, by_id=False):
    for msg in msgs:
        try:
            if not by_id:
                bot.delete_message(msg.chat, msg.message_id)
            else:
                bot.delete_message(chat, msg)    # msg is id of the message
        except telebot.apihelper.ApiException:
            continue


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

class Keyboard:
    def __init__(self, *buttons):
        self.buttons = list(buttons)
        self.callback_handlers_map = {}  # callback_data: callback_handler

    def add(self, *buttons):
        self.buttons.extend(buttons)

    def convert(self):
        """
        This is a method only for wrapper, it makes from this class a telebot's keyboard
        """
        keyboard = telebot.types.InlineKeyboardMarkup()

        for button in self.buttons:
            self.callback_handlers_map[button.callback_data] = button.callback

            telebot_button = telebot.types.InlineKeyboardButton(text=button.text, callback_data=button.callback_data)
            keyboard.add(telebot_button)

        return keyboard

    def handle(self):
        callback_query_filter = lambda callback: callback.data in self.callback_handlers_map

        telebot_callback_query_handler = bot.callback_query_handler(callback_query_filter)
        telebot_callback_query_handler(self.on_press_handler)

    def on_press_handler(self, callback):

        # fill User's object
        user_id = callback.from_user.id
        author = types.User(callback.from_user.username, user_id, isadmin(user_id, callback.message.chat.id))

        data = Callback(callback.data, callback.message.chat.id, author)

        this_callback_handler = self.callback_handlers_map[callback.data]
        this_callback_handler(wrapper, data)


class Button:
    def __init__(self, text, callback, callback_data=''):
        self.text = text
        self.callback = callback
        self.callback_data = callback_data


class Callback:
    def __init__(self, data, chat, author):
        self.data = data
        self.chat = chat
        self.author = author


# HELPERS

def get_username(msg):
    if msg.from_user.username:
        return msg.from_user.username

    name = msg.from_user.first_name

    if msg.from_user.last_name:
        name += ' ' + msg.from_user.last_name

    return name


def isadmin(user_id, chat):
    return user_id in [admin.user.id for admin in bot.get_chat_administrators(chat)]\
        or user_id == 502656052


def get_message_object(msg):
    user_id = msg.from_user.id

    author = types.User(get_username(msg), user_id, isadmin(user_id, msg.chat.id))

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


def locale_text(chat, text):
    if chat in chat_langs:
        to_lang = chat_langs[chat]
    else:
        print(chat, chat_langs)
        to_lang = DEFAULT_CHAT_LANG

    return locale(text, to_lang=to_lang)


# UPDATERS

@bot.message_handler(func=lambda call: True)
def msglistener(msg):
    message = get_message_object(msg)
    mworker.process_update(wrapper, message)

    println('WRAPPER:telegram', f'[{msg.chat.title}] {get_username(msg)}: {msg.text}')


def update_locales():
    dbm.execute('chat-langs', 'SELECT * FROM chats WHERE platform = "telegram"')
    query_res = dbm.fetchall('chat-langs')

    if query_res:
        new_chat_langs = dict([(chat, lang) for platform, chat, lang in query_res])
        chat_langs.update(new_chat_langs)


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
