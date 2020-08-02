import syst.mworker as worker


@worker.handler(lambda msg: msg.content.lower().startswith('повтори'))
def handler(wrapper, msg):
    text = msg.content[len('повтори'):]

    if text.endswith('и удали'):
        text = text[:-len('и удали')]

        wrapper.delmsg(msg)
        wrapper.sendmsg(msg, text)
    else:
        wrapper.replymsg(msg.replied or msg, text)
