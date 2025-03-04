from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta
import aiogram_calendar


import keyboards.keyboards as kb

from filters.admin_filter import check_super_admin
from database.models import User
import database.requests as rq
import database.help_function as hf
from datetime import time, date, datetime, timedelta
from filters.admin_filter import IsSuperAdmin
from filters.filters import validate_date, validate_overdue, validate_amount
from handlers.expenses.edit_expenses.edit_expenses import process_edit_expense
from handlers.expenses.edit_expenses.edit_expenses import EditExpenseFSM


router = Router()

storage = MemoryStorage()

import logging
import asyncio


@router.callback_query(F.data.startswith('next_edit_expense!amount!'))  # f'Сумма {amount_expense}': f'next_edit_expense!amount!{id_expense}',
async def process_edit_amount_expense(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Редактировать Сумму, переводим в состояние ожидания ввода суммы  """
    logging.info(f'process_edit_amount_expense --- clb.data = {clb.data}')

    await state.set_state(EditExpenseFSM.state_edit_amount_expense)
    logging.info(f'await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')
    state_data = await state.get_data()
    if 'edit_title_expense' in list(state_data):
        title_expense = state_data['edit_title_expense']
    else:
        title_expense = (await rq.get_expense_by_id(state_data['id_expense_to_edit'])).title_expense
    await clb.message.edit_text(text=f'Пришлите сумму расходов для категории <b>"{title_expense}"</b>',
                                reply_markup=kb.create_in_kb(1, **{'Назад': f'edit_expense!{state_data["id_expense_to_edit"]}'}))  # Для кнопки НАЗАД f'edit_expense!{id_expense}
    await clb.answer()


@router.message(F.text, StateFilter(EditExpenseFSM.state_edit_amount_expense))
async def process_edit_amount_expense_input(message: Message, state: FSMContext, bot: Bot) -> None:
    """ отлавливание ввода суммы  изменённого Расхода, проверка на валидность (число), вывод календаря"""
    logging.info('process_edit_amount_expense_input')

    #await hf.process_del_message_messsage(2, bot, message)
    state_data = await state.get_data()
    amount_expense = message.text
    if amount_expense.isdigit():#validate_amount(amount=amount_expense):
        await state.update_data({'edit_amount_expense': amount_expense})
        await process_edit_expense(clb=message, state=state, bot=bot)
    else:
        dict_kb = {'Назад': f'edit_expense!{state_data["id_expense_to_edit"]}'}
        keyboard = kb.create_in_kb(1, **dict_kb)
        await message.answer(text=f'Некорректные данные, сумма расхода должна быть числом',
                             reply_markup=keyboard)
