import syst.mworker as mworker
import syst.tools.dateparser as dateparser


functions_map = lambda wrapper: {'!ban':    wrapper.ban,
                                 '!unban':   wrapper.unban,
                                 '!mute':    wrapper.mute,
                                 '!unmute':  wrapper.unmute
                                 }


@mworker.handler(lambda msg: mworker.startswith(msg.content, ('!ban', '!unban', '!mute', '!unmute')) and msg.replied and msg.author.admin)
def handle_user_restrict(wrapper, msg):
    text = msg.content.split()
    method = text[0].lower()

    func = functions_map(wrapper)[method]
    duration = text[1:]
    duration_in_seconds = dateparser.parse(*duration)

    func(msg.replied, duration)

    # beauty output
    muted_or_banned = method[1:] + ('ned' if method.endswith('n') else 'd')
    restricted_for = dateparser.date_by_seconds(duration_in_seconds)

    if not restricted_for:
        restricted_for = 'forever'

    wrapper.sendmsg(msg, f'@{msg.replied.author.username}: {muted_or_banned} for {restricted_for}')
