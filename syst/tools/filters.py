def startswith(msg, *variables, check_case=False):
    text = msg.content

    if not check_case:
        text = text.lower()

    for var in variables:
        if text.startswith(var):
            return True

    return False
