import syst.mworker as mworker


functions_map = lambda wrapper: {'!ban':    wrapper.ban,
                                 '!unban':   wrapper.unban,
                                 '!mute':    wrapper.mute,
                                 '!unmute':  wrapper.unmute
                                 }


@mworker.handler(lambda msg: mworker.startswith(msg.content, ('!ban', '!unban', '!mute', '!unmute')) and msg.replied and msg.author.admin)
def handle_user_restrict(wrapper, msg):
    text = msg.content.split()

    func = functions_map(wrapper)[text[0].lower()]
    duration = text[1:]

    func(msg.replied, duration)
