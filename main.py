from dotenv import load_dotenv

import os

from database import user
from handlers import admin_hndlrs, inline_mode, user_hndlrs, word_hndlrs
from VKBot.VKBot import Bot
import keyboards

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def text(bot, message, user_id):
        lang, state = user.get_lang(bot, message, 1)

        if state == 1:
            user_hndlrs.report_step_2(bot, message)
            return True

        if user_id in keyboards.ADMINS:
            if admin_hndlrs.text(message, bot, user_id):
                return True

        match message.text:
            case '🎲 Случайное слово':
                word_hndlrs.get_word(bot, message, True)

            case '🈳 Сменить язык':
                user_hndlrs.change_lang(bot, lang, user_id)

            case '⚠️ Сообщить о проблеме':
                user_hndlrs.report(bot, user_id)

            case _:
                word_hndlrs.get_word(bot, message)
                

bot = Bot(os.getenv("VK_API"), os.getenv("VK_API_VERSION"), text)

# word_hndlrs.register_commands(bot)
user_hndlrs.register_commands(bot)
# admin_hndlrs.register_commands(bot)
# inline_mode.register_commands(bot)

bot.run()