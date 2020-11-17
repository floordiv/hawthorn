import syst.mworker as mworker
import syst.tools.filters as filters
import syst.tools.dateparser as dateparser


functions_map = lambda wrapper: {
                                 'ban':     wrapper.ban,
                                 'unban':   wrapper.unban,
                                 'mute':    wrapper.mute,
                                 'unmute':  wrapper.unmute
                                 }


@mworker.handler(lambda msg: filters.command(msg, 'ban', 'unban', 'mute', 'unmute') and msg.replied and msg.author.admin
                 and not msg.replied.author.admin)
def handle_user_restrict(wrapper, msg):
    command, text = filters.getcommand(msg, 'ban', 'unban', 'mute', 'unmute')

    if text:
        duration = text.split()
        restricted_for = dateparser.date_by_seconds(dateparser.parse(*duration))
    else:
        duration, restricted_for = 'forever', 'forever'

    func = functions_map(wrapper)[command]
    func(msg.replied, duration)

    # beauty output
    restrict_method = command + ('ned' if command.endswith('n') else 'd')

    wrapper.sendmsg(msg, f'@{msg.replied.author.username}: {restrict_method} for {restricted_for}')
