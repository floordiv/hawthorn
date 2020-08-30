def startswith(msg, *variables, check_case=False):
    text = msg.content

    if not check_case:
        text = text.lower()

    for var in variables:
        if text.startswith(var):
            return True

    return False


def command(msg, *commands, prefix='!', check_case=False):
    text = msg.content

    if not check_case:
        text = text.lower()

    if text.startswith(prefix):
        without_prefix = text[len(prefix):]

        for user_command in commands:
            if without_prefix.startswith(user_command):
                return True

    return False


def getcommand(msg, *commands, prefix='!', check_case=False):
    source_text = msg.content[len(prefix):]
    text = source_text if check_case else source_text.lower()

    for user_command in commands:
        if text.startswith(user_command):
            return user_command, source_text[len(user_command):].lstrip()

    return None, None
