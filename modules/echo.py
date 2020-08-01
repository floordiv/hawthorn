import syst.mworker as worker


@worker.handler(lambda msg: msg.text.startswith('повтори'))
def handler(wrapper, msg):
    wrapper.sendmsg(msg, msg.text[len('повтори'):])
