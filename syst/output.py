from datetime import datetime


def println(name=None, text=None):
    if text is None:
        name, text = 'INFO', name

    print(f'[{datetime.now()}] [{name}] {text}')
