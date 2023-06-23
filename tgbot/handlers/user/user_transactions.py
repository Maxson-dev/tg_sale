# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.data.loader import dp
from tgbot.keyboards.inline_user import refill_bill_finl, refill_select_finl
from tgbot.services.api_yookassa import YooKassaApi
from tgbot.services.api_sqlite import \
      (update_userx, get_refillx, add_refillx, get_userx, get_yoo_paymentx, update_yoo_paymentx)
from tgbot.utils.const_functions import get_date, get_unix
from tgbot.utils.misc_functions import send_admins

min_input_rub = 50  # Минимальная сумма пополнения в рублях
max_input_rub = 300_000

# Выбор способа пополнения
@dp.callback_query_handler(text="user_refill", state="*")
async def refill_way(call: CallbackQuery, state: FSMContext):
    get_kb = refill_select_finl()

    if get_kb is not None:
        await call.message.edit_text("<b>💰 Выберите способ пополнения</b>", reply_markup=get_kb)
    else:
        await call.answer("⛔ Пополнение временно недоступно", True)


# Выбор способа пополнения
@dp.callback_query_handler(text_startswith="refill_select", state="*")
async def refill_way_select(call: CallbackQuery, state: FSMContext):
    get_way = call.data.split(":")[1]

    await state.update_data(here_pay_way=get_way)

    await state.set_state("here_refill_amount")
    await call.message.edit_text("<b>💰 Введите сумму пополнения</b>")


###################################################################################
#################################### ВВОД СУММЫ ###################################
# Принятие суммы для пополнения средств через ЮKassa
@dp.message_handler(state="here_refill_amount")
async def refill_get(message: Message, state: FSMContext):
    if not message.text.isdigit():
         await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств")

    cache_message = await message.answer("<b>♻ Подождите, платёж генерируется...</b>")
    pay_amount = int(message.text)

    if not (min_input_rub <= pay_amount <= 300000):
         await cache_message.edit_text(
            f"<b>❌ Неверная сумма пополнения</b>\n"
            f"▶ Cумма не должна быть меньше <code>{min_input_rub}₽</code> и больше <code>{max_input_rub}₽</code>\n"
            f"💰 Введите сумму для пополнения средств",
        )

    get_way = (await state.get_data())['here_pay_way']
    await state.finish()

    pay_msg, pay_link, pay_id = await (
        YooKassaApi(cache_message, pass_user=True)
    ).bill(pay_amount, get_way)

    if pay_msg:
        await cache_message.edit_text(pay_msg, reply_markup=refill_bill_finl(pay_link, pay_id, get_way))
       


###################################################################################
################################ ПРОВЕРКА ПЛАТЕЖЕЙ ################################
# Проверка оплаты через форму
@dp.callback_query_handler(text_startswith="Pay:Yoo")
async def refill_check_payment(call: CallbackQuery):
    id = call.data.split(":")[2]

    pay_status, pay_amount = await (
        YooKassaApi(call, pass_user=True)
    ).check_pay(id)

    match pay_status:
        case "succeeded":
            print("успешный платеж:", id)
            p = get_yoo_paymentx(id)
            if not p["paid"]:
                update_yoo_paymentx(id, paid=True, status="succeeded")
                await refill_success(call, id, pay_amount)
            else:
                await call.answer("❗ Ваше пополнение уже было зачислено.", True)
        case "canceled":
            print("отмененный платеж:", id)
            update_yoo_paymentx(id, paid=False, status="canceled")
            await call.message.edit_text("<b>❌ Платеж был отменен.</b>")
        case "waiting_for_capture" | "pending":
             print("платеж в ожидании:", id)
             await call.answer("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", True, cache_time=5)

##########################################################################################
######################################### ПРОЧЕЕ #########################################
# Зачисление средств
async def refill_success(call: CallbackQuery, pay_id, amount):
    get_user = get_userx(user_id=call.from_user.id)

    update_userx(
        call.from_user.id,
        user_balance=get_user['user_balance'] + amount,
        user_refill=get_user['user_refill'] + amount,
    )

    await call.message.edit_text(
        f"<b>💰 Вы пополнили баланс на сумму <code>{amount}₽</code>\n"
        f"Спасибо что вы с нами 💓</b>",
    )

    await send_admins(
        f"👤 Пользователь: <b>@{get_user['user_login']}</b> | <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> | <code>{get_user['user_id']}</code>\n"
        f"💰 Сумма пополнения: <code>{amount}₽</code>\n"
        f"🧾 ID платежа: <code>{pay_id}</code>"
    )
