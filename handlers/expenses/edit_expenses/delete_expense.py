from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta
import aiogram_calendar

from handlers.expenses.add_expense import process_expense
import keyboards.keyboards as kb

from filters.admin_filter import check_super_admin
from database.models import User
import database.requests as rq
import database.help_function as hf
from datetime import time, date, datetime, timedelta
from filters.admin_filter import IsSuperAdmin
from filters.filters import validate_date, validate_overdue, validate_amount



router = Router()

storage = MemoryStorage()

import logging
import asyncio


@router.callback_query(F.data.startswith('delete_expense'))
async def process_delete_expense(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Удалить в разделе Редактировать Расход"""
    logging.info(f'process_delete_expense --- clb.data = {clb.data}')

    id_expense = int(clb.data.split('!')[-1])
    # title_expense = await rq.get_expense_by_id(id_expense)
    await rq.delete_expense(id_expense)
    #await hf.process_del_message_clb(4, bot, clb)
    keyboard = kb.keyboards_main_menu()
    await clb.message.answer(text=f'Запись о расходе успешно удалена.', reply_markup=keyboard)
    await process_expense(clb.message, bot)
    await clb.answer()