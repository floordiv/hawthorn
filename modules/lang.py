import sqlite3

import syst.mworker as mworker
import syst.tools.locale as locale
import syst.tools.filters as filters


DEFAULT_LANG = 'en'

conn = sqlite3.connect('./data/chat-langs.sqlite')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS chats (platform string, chat string, lang string)')


@mworker.handler(lambda msg: filters.startswith(msg, '/lang', '!lang'))
def setlang(wrapper, msg):
    available_langs = locale.get_langs()

    lang_to_change = msg.content[len('/lang'):].strip()

    cursor.execute('SELECT * FROM chats WHERE chat = ? AND platform = ?', (str(msg.chat), msg.platform))
    platform, chat, current_lang = cursor.fetchone()

    if not current_lang:
        cursor.execute('INSERT INTO chats VALUES (?, ?, ?)', (msg.platform, str(msg.chat), lang_to_change))
        conn.commit()
        current_lang = DEFAULT_LANG

    if lang_to_change == '':
        wrapper.replymsg(msg, f'Available languages: {", ".join(available_langs)}')
    elif lang_to_change not in available_langs:
        wrapper.replymsg(msg, f'Language not found: {lang_to_change}. Available languages: {", ".join(available_langs)}')
    elif lang_to_change == current_lang:
        wrapper.replymsg(msg, f'Language already installed: {current_lang}')
    else:
        cursor.execute('UPDATE chats SET lang = ? WHERE chat = ? AND platform = ?',
                       (lang_to_change, str(msg.chat), msg.platform))
        conn.commit()
        wrapper.update_locales()

        wrapper.replymsg(msg, f'Language successfully changed')
