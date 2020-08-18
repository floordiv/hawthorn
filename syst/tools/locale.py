import json

import syst.tools.getfiles as getfiles


# why should I open locale files every time? Why can't I just open it once and keep it in the cache?
cache = {}


def locale(text, to_lang='ru'):
    locale_phrases = get_locale(to_lang)

    for phrase, localized_phrase in locale_phrases.items():
        if phrase in text:
            text = text.replace(phrase, localized_phrase)

    return text


def get_locale(lang):
    if lang in cache:
        return cache[lang]

    with open('locales/' + lang + '.json') as locale_file:
        cache[lang] = json.load(locale_file)

        return cache[lang]


def update_locale(lang):
    with open('locales/' + lang + '.json') as locale_file:
        cache[lang] = json.load(locale_file)


def get_langs():
    files = getfiles.from_folder('locales', lambda file: file.endswith('.json'))

    return [file[:-len('.json')] for file in files]
