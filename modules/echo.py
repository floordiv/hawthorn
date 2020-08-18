import syst.mworker as worker
import syst.tools.filters as filters


@worker.handler(lambda msg: filters.startswith(msg, 'повтори', 'say', 'фикус, повтори'))
def handler(wrapper, msg):
    text = msg.content[len('повтори'):]

    if text.endswith('и удали'):
        text = text[:-len('и удали')]

        wrapper.delmsg(msg)
        wrapper.sendmsg(msg, text)
    else:
        wrapper.replymsg(msg.replied or msg, text)
