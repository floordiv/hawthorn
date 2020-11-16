import sqlite3


conn = sqlite3.connect('./test_database.db')
cursor = conn.cursor()

# CREATE TABLE chats (chat_id string, user_id string)
# INSERT INTO chats VALUES ('python_scripts', 'floordiv')
# SELECT * FROM chats WHERE chat = 'python_chats' AND username = 'floordiv'
# UPDATE chats SET karma = karma + 5 WHERE chat = 'python_scripts' AND username = 'floordiv'

sql = """
SELECT * FROM chats WHERE chat = 'python_scripts' AND username = 'floordiv'
"""


cursor.execute(sql)
value = cursor.fetchone()

print(value)

# conn.commit()
