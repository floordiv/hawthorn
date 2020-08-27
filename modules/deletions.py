import syst.tools.dbm as dbm
import syst.mworker as mworker
import syst.tools.filters as filters


dbm.open_db('user-deletions')


@mworker.handler(lambda msg: filters.startswith(msg, 'удали', '!del', 'фикус, удали') and msg.author.admin and msg.replied)
def delete_one_message(wrapper, msg):
    wrapper.delmsg(msg.replied, msg)


@mworker.handler(lambda msg: filters.startswith(msg, '!delall') and msg.author.admin and msg.replied and msg.platform == 'telegram')
def delete_thread(wrapper, msg):
    messages_to_delete = range(msg.replied.message_id, msg.message_id + 1)
    wrapper.delmsg(*messages_to_delete, chat=msg.chat, by_id=True)


@mworker.handler(lambda msg: False)
def channel_mode(wrapper, msg):
    ...
