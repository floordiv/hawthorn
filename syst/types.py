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
