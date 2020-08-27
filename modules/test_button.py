import syst.mworker as mworker


def default_keyboard(wrapper):
    keyboard = wrapper.Keyboard()
    button = wrapper.Button('Hello?', simple_button, callback_data='ok')
    keyboard.add(button)

    return keyboard


def simple_button(wrapper, data):
    wrapper.editmsg(data, '@' + data.author.username + ' ok!!', keyboard=default_keyboard(wrapper))


@mworker.handler(lambda msg: msg.content.startswith('!button'))
def create_button(wrapper, msg):
    keyboard = wrapper.Keyboard()
    button = wrapper.Button('Hello?', simple_button, callback_data='ok')
    keyboard.add(button)

    wrapper.sendmsg(msg, 'Simple button test', keyboard=keyboard)
