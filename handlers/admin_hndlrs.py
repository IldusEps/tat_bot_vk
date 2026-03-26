from os import replace
import re
import subprocess

from handlers.utils import *
from keyboards import *
from database import analytics
import keyboards
import log

logging = log.get_logger("base")


def register_commands(bot):
    @bot.callback_query_handler(func=lambda call: re.match(r"send[0-9]+", call.data))
    def report_callback(call):
        report(call, bot)
        bot.answer_callback_query(callback_query_id=call.id)

    @bot.callback_query_handler(func=lambda call: re.match(r"Statistics", call.data))
    def statistics_callback(call):
        statistics(call, bot)
        bot.answer_callback_query(callback_query_id=call.id)

# inline-keyboards


def inlineKeyboard(label):
    match label:
        case "Statistics_0":
            return NewInlineKeyboard((("Пользователи", "Statistics_1"), ("Слова", "Statistics_3")))
        case "Statistics_1":
            return NewInlineKeyboard((("Сменить режим", "Statistics_2"), ("Кол-во слов", "Statistics_0")), ("Слова", "Statistics_3"))
        case "Statistics_2":
            return NewInlineKeyboard((("Сменить режим", "Statistics_1"), ("Кол-во слов", "Statistics_0")), ("Слова", "Statistics_3"))


# handlers
def text(message, bot, user_id):
    match message.text:
        case 'Статистика':
            analytics.statistics_query.cache_clear()
            count_day, count_users = analytics.get_statistics(0)
            bot.send_message(
                user_id, f"Всего слов за сегодня: {count_day}\nВсего пользователей: {count_users}", keyboard=inlineKeyboard("Statistics_0"), parse_mode="HTML")
            return True

        case 'Перезапуск бота':
            try:
                process = subprocess.run(['git', 'pull'], capture_output=True)
                bot.send_message(user_id, process.stdout)
                process = subprocess.run(
                    ['pm2', 'restart', 'bot'], capture_output=True)
                bot.send_message(user_id, process.stdout)
            except Exception as e:
                bot.send_message(user_id, "{!s}\n{!s}".format(type(e), str(e)))
            return True

        case 'Логи':
            try:
                bot.send_message(user_id, "Я тут")
                process = subprocess.run(
                    ['pm2', 'logs', '--err', 'bot', '--lines', '100', '--nostream'], capture_output=True, text=True)
                logging.info(process.stderr + process.stdout)
                lines = process.stderr + process.stdout
                if len(lines) < 4096:
                    bot.send_message(user_id, lines)
                else:
                    matches = re.finditer(
                        r"[\s\S]{1,3900}(\n|$)", lines, re.MULTILINE)
                    for match in matches:
                        bot.send_message(user_id, match.group(0))
            except Exception as e:
                bot.send_message(user_id, "{!s}\n{!s}".format(type(e), str(e)))
            return True


def report(call, bot):
    message = call.message
    if message.user_id == 215001844:
        bot.send_message(215001844, "Введите текст для пользователя")
        bot.register_next_step_handler(
            message, send_message_to_user(re.match(r"send([0-9]+)", call.data).group(1), bot))
        bot.answer_callback_query(callback_query_id=call.id)


def send_message_to_user(report_id, bot):
    ''' Второй этап после report '''
    def func(message):
        if message.user_id == 215001844:
            bot.send_message(215001844, "Текст отправлен")
            bot.send_message(
                report_id, f"Вы отправляли сообщение об ошибки.\n*Ответ от разработчика*:\n  {message.text}", parse_mode="Markdown")

    return func


def statistics(call, bot):
    message, user_id, message_id = get_call_info(call)
    if user_id in ADMINS:
        state_number = int(call.data.replace("Statistics_", ""))
        if state_number == 0:
            count_day, count_users = analytics.get_statistics(0)
            bot.edit_message_text(f"Всего слов за сегодня: {count_day}\nВсего пользователей: {count_users}",
                                  user_id, message_id,  keyboard=inlineKeyboard("Statistics_0"), parse_mode="HTML")
        else:
            users = analytics.get_statistics(state_number)
            if state_number == 1:
                text, parse_mode = users, "HTML"
            else:
                text, parse_mode = f"```\n{users}```", "MarkdownV2"

            matches = list(re.finditer(
                r"[\s\S]{1,3900}(\n|$)", text, re.MULTILINE))
            for matchNum, match in enumerate(matches):
                if matchNum == 0:
                    bot.edit_message_text(match.group(
                        0), user_id, message_id, parse_mode=parse_mode)
                elif matchNum == len(matches) - 1:
                    bot.send_message(user_id, match.group(
                        0), parse_mode='HTML', keyboard=inlineKeyboard(call.data))
                else:
                    bot.send_message(user_id, match.group(0),
                                     parse_mode='HTML')
        bot.answer_callback_query(callback_query_id=call.id)
