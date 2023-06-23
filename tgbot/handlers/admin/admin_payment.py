# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.data.loader import dp
from tgbot.keyboards.inline_admin import payment_choice_finl
from tgbot.services.api_yookassa import YooKassaApi
from tgbot.services.api_sqlite import update_paymentx, get_paymentx
from tgbot.utils.misc.bot_filters import IsAdmin
from tgbot.data.config import get_yoo_config


###################################################################################
############################# ВЫБОР СПОСОБА ПОПОЛНЕНИЯ ############################
# Открытие способов пополнения
@dp.message_handler(IsAdmin(), text="🖲 Способы пополнений", state="*")
async def payment_systems(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("<b>🖲 Выберите способы пополнений</b>", reply_markup=payment_choice_finl())


# Включение/выключение самих способов пополнения
@dp.callback_query_handler(IsAdmin(), text_startswith="change_payment:")
async def payment_systems_edit(call: CallbackQuery):
    way_pay = call.data.split(":")[1]
    way_status = call.data.split(":")[2]

    yoo_config = get_yoo_config()

    if 'shop_id' in yoo_config and 'api_key' in yoo_config:
        if way_pay == "Yoo":
            update_paymentx(way_yoo=way_status)
    else:
        return await call.answer("❗ Добавьте в settings.ini API ключ ЮKassa перед включением Способов пополнений", True)

    await call.message.edit_text("<b>🖲 Выберите способы пополнений</b>", reply_markup=payment_choice_finl())


# Проверка работоспособности ЮKassa
@dp.message_handler(IsAdmin(), text="🤖 Проверить ЮKassa ♻", state="*")
async def payment_shop_check(message: Message, state: FSMContext):
    await state.finish()

    await YooKassaApi(message, pass_check=True).pre_checker()
