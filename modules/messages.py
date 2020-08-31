import syst.mworker as mworker
import syst.tools.filters as filters


messages = {}   # chat_id: receiver: text


@mworker.handler(lambda msg: filters.command(msg, 'message'))
def send_msg(wrapper, msg):
    _, message_text = filters.getcommand(msg, 'message')
    message_text = message_text.split()

    wrapper.delmsg(msg)

    if message_text[0].startswith('@') and message_text[1].startswith('@'):
        chat, receiver, *text = message_text
        text = ' '.join(text)
    else:
        chat, receiver, *text = msg.chat, *message_text
        text = ' '.join(text)

    if not receiver.startswith('@'):
        wrapper.delmsg(msg)
        return wrapper.sendmsg(msg, 'Private message syntax: !message [chat] @username text')

    if chat not in messages:
        messages[chat] = {receiver: text}
    else:
        messages[chat][receiver] = text

    keyboard = wrapper.Keyboard()
    keyboard.add(wrapper.Button('See message', on_press, callback_data=f'{receiver}'))

    wrapper.sendmsg(msg, f'{receiver}, you have a private message', keyboard=keyboard)


def on_press(wrapper, callback):
    chat, receiver = callback.chat, callback.data
    button_pressed_by = '@' + callback.author.username

    if button_pressed_by != receiver:
        return wrapper.alert(callback, 'Пшёл нах, не для тебя мама розу растила')

    wrapper.alert(callback, messages[chat][receiver])

    wrapper.editmsg(callback, f'{receiver} has read the message')
    del messages[chat][receiver]
