import syst.mworker as worker
import syst.tools.filters as filters


@worker.handler(lambda msg: filters.command(msg, 'повтори', 'say', 'фикус, повтори', prefix=''))
def handler(wrapper, msg):
    _, text = filters.getcommand(msg, 'повтори', 'say', 'фикус, повтори', prefix='')

    if text.lower().endswith('и удали'):
        text = text[:-len('и удали')]

        wrapper.delmsg(msg)

        if msg.replied:
            wrapper.replymsg(msg.replied, text)
        else:
            wrapper.sendmsg(msg, text)
    else:
        wrapper.replymsg(msg.replied or msg, text)
