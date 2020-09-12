import syst.mworker as mworker
import syst.tools.filters as filters


@mworker.handler(lambda msg: filters.command(msg, 'msgid'))
def message_id(wrapper, msg):
    wrapper.replymsg(msg, msg.message_id)


@mworker.handler(lambda msg: filters.command(msg, 'chatid'))
def chat_id(wrapper, msg):
    wrapper.replymsg(msg, msg.chat)
