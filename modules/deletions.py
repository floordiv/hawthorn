import sqlite3
import syst.mworker as mworker
import syst.tools.filters as filters


conn = sqlite3.connect('./data/deletions.sqlite', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS chats_channel_modes (platform string, chat string, enabled boolean)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS chats_slow_modes (platform string, chat string, enabled boolean, timeout integer)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS users_slow_modes (platform string, chat string, enabled boolean, timeout integer)')
conn.commit()

# we will keep it in memory to avoid requesting db with every message
chats_with_enabled_channel_modes = {}   # platform: {chat: is_enabled}
chats_slow_modes = {}   # platform: {chat: [slowmode_in_seconds, last_message_date]}
chats_slow_modes_for_users = {}

cursor.execute('SELECT * FROM chats_channel_modes')
channel_modes = cursor.fetchall()

cursor.execute('SELECT * FROM chats_slow_modes')
chat_slow_modes_ = cursor.fetchall()

for platform, chat, isenabled in channel_modes:
    if platform not in chats_with_enabled_channel_modes:
        chats_with_enabled_channel_modes[platform] = {}

    chats_with_enabled_channel_modes[platform][chat] = isenabled


for platform, chat, isenabled, timeout in chat_slow_modes_:
    ...


@mworker.handler(lambda msg: filters.startswith(msg, 'удали', '!del', 'фикус, удали') and msg.author.admin and msg.replied)
def delete_one_message(wrapper, msg):
    wrapper.delmsg(msg.replied, msg)


@mworker.handler(lambda msg: filters.startswith(msg, '!delall') and msg.author.admin and msg.replied and msg.platform == 'telegram')
def delete_thread(wrapper, msg):
    messages_to_delete = range(msg.replied.message_id, msg.message_id + 1)
    wrapper.delmsg(*messages_to_delete, chat=msg.chat, by_id=True)


@mworker.handler(lambda msg: filters.startswith(msg, '!channelmode', '!cm') and msg.author.admin)
def channel_mode(wrapper, msg):
    if msg.platform not in chats_with_enabled_channel_modes:
        chats_with_enabled_channel_modes[msg.platform] = {}

    if msg.chat not in chats_with_enabled_channel_modes[msg.platform]:
        cursor.execute('SELECT enabled FROM chats_channel_modes WHERE platform=? AND chat=?', (msg.platform, str(msg.chat)))
        channel_mode_was_enabled = cursor.fetchone()

        if channel_mode_was_enabled is None:    # chat not exists. Create it, and set channel-mode to true
            cursor.execute('INSERT INTO chats_channel_modes VALUES (?, ?, 1)', (msg.platform, str(msg.chat)))
            conn.commit()
            chats_with_enabled_channel_modes[msg.platform][msg.chat] = True
            now_is_enabled = True
        else:
            channel_mode_was_enabled = channel_mode_was_enabled[0]  # cause tuple returned
            now_is_enabled = not channel_mode_was_enabled

            chats_with_enabled_channel_modes[msg.platform][msg.chat] = now_is_enabled
            cursor.execute('UPDATE chats_channel_modes SET enabled=? WHERE platform=? AND chat=?',
                           (int(now_is_enabled), msg.platform, str(msg.chat)))
            conn.commit()
    else:
        prev_value = chats_with_enabled_channel_modes[msg.platform][msg.chat]   # shortened variable name, nothing more
        now_is_enabled = not prev_value
        chats_with_enabled_channel_modes[msg.platform][msg.chat] = now_is_enabled

        cursor.execute('UPDATE chats_channel_modes SET enabled=? WHERE platform=? AND chat=?',
                       (int(now_is_enabled), msg.platform, str(msg.chat)))
        conn.commit()

    wrapper.replymsg(msg, 'Channel-mode has been successfully ' + ('activated' if now_is_enabled else 'deactivated'))


@mworker.handler(lambda msg: filters.startswith(msg, '!slowmode', '!slow-mode', '!sm') and msg.author.admin)
def slow_mode(wrapper, msg):
    wrapper.replymsg(msg, 'Not implemented yet.')


@mworker.handler(lambda msg: (msg.platform in chats_with_enabled_channel_modes and
                              chats_with_enabled_channel_modes[msg.platform].get(msg.chat) and not msg.author.admin))
def delete_message(wrapper, msg):
    wrapper.delmsg(msg)
