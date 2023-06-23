# - *- coding: utf- 8 - *-
import configparser

# Токен бота
BOT_TOKEN = configparser.ConfigParser()
BOT_TOKEN.read("settings.ini")
BOT_TOKEN = BOT_TOKEN['settings']['token'].strip().replace(' ', '')
BOT_TIMEZONE = "Europe/Moscow"  # Временная зона бота


PATH_DATABASE = "tgbot/data/database.db"  # Путь к БД
PATH_LOGS = "tgbot/data/logs.log"  # Путь к Логам
BOT_VERSION = "1.4.88"  # Версия бота


# Получение администраторов бота
def get_admins() -> list[int]:
    read_admins = configparser.ConfigParser()
    read_admins.read("settings.ini")

    admins = read_admins['settings']['admin_id'].strip().replace(" ", "")

    if "," in admins:
        admins = admins.split(",")
    else:
        if len(admins) >= 1:
            admins = [admins]
        else:
            admins = []

    while "" in admins: admins.remove("")
    while " " in admins: admins.remove(" ")
    while "\r" in admins: admins.remove("\r")
    while "\n" in admins: admins.remove("\n")

    admins = list(map(int, admins))

    return admins

def get_yoo_config() -> dict[str, str]:
    parser = configparser.ConfigParser()
    parser.read("settings.ini")
    return parser['yookassa']

BOT_DESCRIPTION = f'''
<b>🏴‍☠️ Bot Version: <code>{BOT_VERSION}</code> 🏴‍☠️</b>
<b>🎰 Бот разработан и поддерживается продолжателями идей МММ и Сергея Мавроди 🎰</b>
<b>💵 Заряду на скам лохов 🪤🦣🦣🦣 и гринд налика 💵</b>
<b>💰💊💉🚬🎰🚀🚁💵💴💶💶💳💎</b>
'''.strip()
