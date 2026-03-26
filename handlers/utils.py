import vk_api
import random

def get_message_text(call):
    if hasattr(call, "message"):
        message = call.message
        text = call.data
    else:
        message = call
        text = message.text

    return message, text


def get_call_info(call):
    message = call.message
    user_id = message.user_id
    message_id = message.message_id

    return message, user_id, message_id
