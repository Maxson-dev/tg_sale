# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.services.api_sqlite import get_paymentx


# Выбор способов пополнения
def refill_select_finl():
    keyboard = InlineKeyboardMarkup()

    get_payments = get_paymentx()

    if get_payments['way_yoo'] == "True":
        keyboard.add(InlineKeyboardButton("💳 ЮKassa", callback_data="refill_select:Yoo"))
    else:
        return None

    keyboard.add(InlineKeyboardButton("🔙 Вернуться", callback_data="user_profile"))

    return keyboard


# Проверка киви платежа
def refill_bill_finl(pay_link: str, pay_id: str, pay_way: str):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("🌀 Перейти к оплате", url=pay_link)
    ).add(
        InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"Pay:{pay_way}:{pay_id}")
    )

    return keyboard


# Кнопки при открытии самого товара
def products_open_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("💰 Купить товар", callback_data=f"buy_item_open:{position_id}:{remover}")
    ).add(
        InlineKeyboardButton("🔙 Вернуться", callback_data=f"buy_category_open:{category_id}:{remover}")
    )

    return keyboard


# Подтверждение покупки товара
def products_confirm_finl(position_id, get_count):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"buy_item_confirm:yes:{position_id}:{get_count}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"buy_item_confirm:not:{position_id}:{get_count}")
    )

    return keyboard


# Ссылка на поддержку
def user_support_finl(user_name):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("💌 Написать в поддержку", url=f"https://t.me/{user_name}"),
    )

    return keyboard
