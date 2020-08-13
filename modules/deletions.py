import syst.mworker as mworker


@mworker.handler(lambda msg: msg.content.lower().startswith('удали') and msg.author.admin and msg.replied)
def delete_one_message(wrapper, msg):
    wrapper.delmsg(msg.replied, msg)


@mworker.handler(lambda msg: msg.content.lower().startswith('!delall') and msg.author.admin and msg.replied and msg.platform == 'telegram')
def delete_thread(wrapper, msg):
    messages_to_delete = range(msg.replied.message_id, msg.message_id + 1)
    wrapper.delmsg(*messages_to_delete, chat=msg.chat, by_id=True)
