# - *- coding: utf- 8 - *-
import time

from yookassa import (Configuration, Settings, Payment)

from aiogram.types import Message
from aiogram import Dispatcher

from tgbot.keyboards.inline_main import close_inl
from tgbot.services.api_sqlite import add_yoo_paymentx
from tgbot.utils.const_functions import ded
from tgbot.utils.misc_functions import send_admins
from tgbot.data.config import get_yoo_config


class YooKassaApi:
    def __init__(
            self,
            dp: Message | Dispatcher,
            pass_check=False,
            pass_user=False
    ):
        config = get_yoo_config()
        self.shop_id = config.get("shop_id")
        self.api_key = config.get("api_key")

        Configuration.configure(self.shop_id, self.api_key)

        self.dp = dp
        self.pass_check = pass_check
        self.pass_user = pass_user

    # Рассылка админам о нерабочей юкассе

    @staticmethod
    async def error_wallet():
        await send_admins("<b>🤖 ЮKassa недоступна или отключена ❌</b>\n"
                          "❗ Как можно быстрее решите проблему")

    async def check_account(self) -> dict:
        try:
            me = Settings.get_account_settings()
            return me
        except:
            return None

    # Обязательная проверка перед каждым запросом
    async def pre_checker(self):
        if self.shop_id is not None and self.api_key is not None:
            me = await self.check_account()

            if self.pass_check:
                if me is not None:
                    await self.dp.answer(
                        f"<b> Магазин в ЮKassa полностью функционирует ✅</b>\n"
                        f"◾ ID: <code>{me['account_id']}</code>\n"
                        f"◾ Статус: <code>{me['status']}</code>\n"
                        f"◾ Способы оплаты: <code>{','.join(me['payment_methods'])}</code>\n"
                        f"◾ Тестовый режим: <code>{me['test']}</code>\n",
                        reply_markup=close_inl,
                    )
                else:
                    await self.error_wallet()
            elif self.pass_user:
                if me is None:
                    await self.dp.edit_text(
                        "<b>❗ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                        "⌛ Попробуйте чуть позже.</b>")
                    await self.error_wallet()
                    return False
            return True
        else:
            if self.pass_user:
                await self.dp.edit_text(
                    "<b>❗ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                    "⌛ Попробуйте чуть позже.</b>")
            await self.error_wallet()
            return False

    async def bill(self, amount: int, _way: str):
        success = await self.pre_checker()
        if not success:
            return False, False, False
        bill_message = ded(f"""
                    <b>💰 Пополнение баланса</b>
                    ➖➖➖➖➖➖➖➖➖➖
                    💳 Для пополнения баланса, нажмите на кнопку ниже 
                    <code>Перейти к оплате</code> и оплатите выставленный вам счёт
                    ❗ У вас имеется 15 минут на оплату счета.
                    💰 Сумма пополнения: <code>{amount}₽</code>
                    ➖➖➖➖➖➖➖➖➖➖
                    🔄 После оплаты, нажмите на <code>Проверить оплату</code>
        """)
        bot_info = await self.dp.bot.get_me()
        botname = bot_info['username']

        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/{botname}"
            },
            "capture": True,
            "description": f"Заказ {time.time()}"
        })
        add_yoo_paymentx(
            yoo_id=payment.id, 
            amount=int(payment.amount.value),
            status="pending",
            confirm_url=payment.confirmation.confirmation_url,
            paid=False,
            created_at=payment.created_at
        )
        bill_url = payment.confirmation.confirmation_url
        return bill_message, bill_url, payment.id
    
    async def check_pay(self, id: str) -> tuple[str, int]:
        p = Payment.find_one(id)
        return p.status, int(p.amount.value)
