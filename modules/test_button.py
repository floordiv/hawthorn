import syst.mworker as mworker


def simple_button(wrapper, data):
    wrapper.sendmsg(data, 'hello!')


@mworker.handler(lambda msg: msg.content.startswith('!button'))
def create_button(wrapper, msg):
    keyboard = wrapper.Keyboard()
    button = wrapper.Button('Hello?', simple_button, callback_data='ok')
    keyboard.add(button)

    wrapper.sendmsg(msg, 'Simple button test', keyboard=keyboard)
