
from datetime import date, datetime, timedelta
from database import connect
import log

logging = log.get_logger("base")
connection, cursor = connect.get_connection_cursor()

# WRAPERS


def acting_user(update_count=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                if args[1] != None:
                    if update_count:
                        cursor.execute(
                            'UPDATE users_vk SET count = count + 1 WHERE user_id = %s', (args[1],))
                    else:
                        cursor.execute(
                            'UPDATE users_vk SET last_time = NOW() WHERE user_id = %s', (args[1],))
                    connection.commit()
            except Exception as e:
                logging.debug(
                    "decorator acting_user {!s}  {!s}\n{!s}".format(args[1], type(e), str(e)))

            return func(*args, **kwargs)

        return wrapper
    return decorator


def wraper_check_username(minutes):
    cache = {}
    lifetime = timedelta(seconds=minutes)

    def func(user_id, username):
        if user_id in cache:
            if datetime.now() >= cache[user_id]:
                del cache[user_id]
        if user_id not in cache:
            cursor.execute(
                'SELECT username FROM users_vk WHERE user_id = %s', (user_id,))
            res = cursor.fetchall()

            if res != []:
                if username != res[0][0]:
                    cursor.execute(
                        'UPDATE users_vk SET username = %s WHERE user_id = %s', (username, user_id,))
                    connection.commit()
                cache[user_id] = datetime.now() + lifetime

    return func


check_username = wraper_check_username(15)

# FUNCTIONS


def get_lang(bot, message, withState=False, user_name = ""):
    connect.ping()
    user_id = message.user_id
    if user_name == "":
        user_name = bot.get_user_name(user_id)
    check_username(user_id, user_name,)
    withState = ', state' if withState else ''

    cursor.execute(
        f'SELECT lang{withState} FROM users_vk WHERE user_id = %s', (user_id,))
    res = cursor.fetchall()

    if res == []:
        try:
            logging.info("Новый пользователь | user: %s" % (str(user_id),))
            cursor.execute(
                'INSERT INTO users_vk (user_id, username) VALUES(%s, %s)', (user_id, user_name, ))
            connection.commit()

            cursor.execute(
                f'SELECT lang{withState} FROM users_vk WHERE user_id = %s', (user_id,))
            res = cursor.fetchall()
        except Exception as e:
            logging.debug("{!s}\n{!s}".format(type(e), str(e)))

    if withState:
        return res[0][0], res[0][1]
    return res[0][0]


def set_lang(lang, user_id):
    cursor.execute(
        'UPDATE users_vk SET lang = "%s" WHERE user_id = %s', (+lang, user_id,))
    connection.commit()


def set_state(user_id, state):
    cursor.execute(
        'UPDATE users_vk SET state = "%s" WHERE user_id = %s', (state, user_id,))
    connection.commit()
