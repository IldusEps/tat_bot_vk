import re
from telebot import types

from database import word_db
import log


logging = log.get_logger("base")


def register_commands(bot):
    @bot.inline_handler(func=lambda query: len(query.query) == 0)
    def empty_query(query):
        empty(query, bot)

    @bot.inline_handler(func=lambda query: re.match(r"^[А-ЯЁёа-яҗңһүәөҖҢҺҮӘӨ \-\|]+$", query.query) and len(query.query) > 1)
    def text_query(query):
        text(query, bot)


def empty(query, bot):
    hint = "Введите слово на русском или татарском языке"

    try:
        r = types.InlineQueryResultArticle(
            id='1',
            title="Бот \"Татарский язык\"",
            description=hint,
            input_message_content=types.InputTextMessageContent(
                "Введите слово")
        )
        bot.answer_inline_query(query.id, [r])
    except Exception as e:
        logging.debug(e)


def text(query, bot):
    user_id = query.from_user.id

    try:
        words = word_db.get_word(query.query, user_id,  0, True)
        tat_count = len(words)
        if re.match(r"[^җңһүәөҖҢҺҮӘӨ]", query.query):
            words += word_db.get_word(query.query, user_id,  1, True)

        inline_words = []
        if len(words) > 0:

            for e, word in enumerate(words):
                translation, buttons = word_db.translation_replace(
                    word["translation"])

                if e == 0:
                    logging.info(
                        "%s - %s... INLINE user: %s" % (word["word"], translation[0:20].replace("\n", ""), str(user_id),))

                translation = re.sub(
                    r"<\/?[^uiba\/]*?>|<\/?[^a\/](.*?(?<=a))>", "", translation)
                mess = f"Перевел  <u>{'с татарского🟢' if e < tat_count else 'с русского🇷🇺'}</u>\n<b>{words[0]["word"]}</b> \n{translation}"
                inline_words.append(types.InlineQueryResultArticle(
                    id=user_id+e, title=word["word"],
                    description=("с татарского🟢 " if e < tat_count else "с русского🇷🇺 ") + re.sub(
                        r"<.*?>|<a.*?\">", "", translation)[:100],
                    input_message_content=types.InputTextMessageContent(
                        mess,  "HTML")
                ))
        else:
            inline_words = [types.InlineQueryResultArticle(
                id='1', title="Ошибка",
                description="*Слово не найдено!*\nПопробуйте примерный поиск в боте",
                input_message_content=types.InputTextMessageContent(
                    message_text=":(", parse_mode="HTML")
            )]

        bot.answer_inline_query(query.id, inline_words)
    except Exception as e:
        logging.info("Ошибка chat_id: {!s}  {!s}\n{!s}".format(
            user_id, type(e), str(e)))
