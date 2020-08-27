class Message:
    def __init__(self, msgtype, content, chat, author, date, msgid, replied, new_members, platform):
        self.content_type = msgtype
        self.content = content
        self.chat = chat
        self.author = author
        self.replied = replied
        self.date = date
        self.message_id = msgid
        self.new_members = new_members
        self.platform = platform


class User:
    def __init__(self, username, user_id, isadmin):
        self.username = username
        self.userid = user_id
        self.admin = isadmin

    def __str__(self):
        return f'User(username={self.username}, userid={self.userid}, admin={self.admin})'


class Button:
    def __init__(self, text, callback, callback_data=''):
        self.text = text
        self.callback = callback
        self.callback_data = callback_data

    def __str__(self):
        return f'Button(text={self.text}, callback_handler={self.callback}, callback_data={self.callback_data})'


class Callback:
    def __init__(self, data, chat, message_id, author):
        self.data = data
        self.chat = chat
        self.message_id = message_id
        self.author = author
