import sqlite3
import syst.mworker as mworker
import syst.tools.filters as filters


conn = sqlite3.connect('./data/deletions.sqlite', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS chats_channel_modes (platform string, chat string, enabled boolean)')
conn.commit()

# we will keep it in memory to avoid requesting db with every message
chats_with_enabled_channel_modes = {}
chats_slow_modes = {}   # platform: {chat: [slowmode_in_seconds, last_message_date]}

cursor.execute('SELECT * FROM chats_channel_modes')

for platform, chat, isenabled in cursor.fetchall():
    if platform not in chats_with_enabled_channel_modes:
        chats_with_enabled_channel_modes[platform] = []

    if isenabled:
        chats_with_enabled_channel_modes[platform].append(chat)


@mworker.handler(lambda msg: filters.startswith(msg, 'удали', '!del', 'фикус, удали') and msg.author.admin and msg.replied)
def delete_one_message(wrapper, msg):
    wrapper.delmsg(msg.replied, msg)


@mworker.handler(lambda msg: filters.startswith(msg, '!delall') and msg.author.admin and msg.replied and msg.platform == 'telegram')
def delete_thread(wrapper, msg):
    messages_to_delete = range(msg.replied.message_id, msg.message_id + 1)
    wrapper.delmsg(*messages_to_delete, chat=msg.chat, by_id=True)


@mworker.handler(lambda msg: filters.startswith(msg, '!channelmode') and msg.author.admin)
def channel_mode(wrapper, msg):
    if msg.platform not in chats_with_enabled_channel_modes:
        chats_with_enabled_channel_modes[msg.platform] = []

    cursor.execute('SELECT enabled FROM chats_channel_modes WHERE platform=? AND chat=?', (msg.platform, str(msg.chat)))
    channel_mode_was_enabled = cursor.fetchone()

    if channel_mode_was_enabled is None:    # chat not exists. Create it, and set channel-mode to true
        cursor.execute('INSERT INTO chats_channel_modes VALUES (?, ?, 1)', (msg.platform, str(msg.chat)))
        conn.commit()
        chats_with_enabled_channel_modes[msg.platform].append(msg.chat)

        return wrapper.replymsg(msg, 'Channel-mode has been successfully activated')

    channel_mode_was_enabled = channel_mode_was_enabled[0]  # cause tuple returned. Now, we have a boolean value

    if not channel_mode_was_enabled:
        chats_with_enabled_channel_modes[msg.platform].append(msg.chat)
    elif msg.chat in chats_with_enabled_channel_modes[msg.platform]:
        chats_with_enabled_channel_modes[msg.platform].remove(msg.chat)

    cursor.execute('UPDATE chats_channel_modes SET enabled=? WHERE platform=? AND chat=?',
                   (int(not channel_mode_was_enabled), msg.platform, str(msg.chat)))
    conn.commit()

    wrapper.replymsg(msg, 'Channel-mode has been successfully ' + ('activated' if not channel_mode_was_enabled else 'deactivated'))


@mworker.handler(lambda msg: (msg.platform in chats_with_enabled_channel_modes and msg.chat in
                              chats_with_enabled_channel_modes[msg.platform] and not msg.author.admin))
def delete_message(wrapper, msg):
    wrapper.delmsg(msg)
