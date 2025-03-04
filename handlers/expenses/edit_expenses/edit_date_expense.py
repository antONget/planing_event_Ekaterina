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

import database.requests as rq
import database.help_function as hf
from datetime import time, date, datetime, timedelta

from handlers.expenses.edit_expenses.edit_expenses import process_edit_expense
from handlers.expenses.edit_expenses.edit_expenses import EditExpenseFSM


router = Router()

storage = MemoryStorage()

import logging
import asyncio





# Редактируем КАТЕГОРИЮ РАСХОДА date_expense

@router.callback_query(F.data.startswith('next_edit_expense!date'))  # f'Дата {date_expense}':f'next_edit_expense!date!{id_expense}',
async def process_edit_expense_date(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Редактировать Дату, показываем клавиатуру с календарем  """
    logging.info(f'process_edit_expense_вфеу --- clb.data = {clb.data}')

    # переводим в состояние ожидания ввода даты редактирования расхода
    await state.set_state(EditExpenseFSM.state_edit_date_expense)

    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2030, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%m/%d/%y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await clb.message.edit_text(
        f'Укажите дату совершения расходов для категории <b>"{await rq.get_current_event()}"</b>:',
        reply_markup=await calendar.start_calendar(year=int('20'+list_date1[2]), month=int(list_date1[0]))
    )
    await clb.answer()


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(EditExpenseFSM.state_edit_date_expense))
async def process_simple_calendar_edit_date_expense(clb: CallbackQuery, callback_data: CallbackData, state: FSMContext, bot: Bot):
    logging.info(f'process_simple_calendar_edit_date_expense {clb.message.chat.id}')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date = await calendar.process_selection(clb, callback_data)
    if selected:
        #data_note = date.strftime("%Y-%m-%d")
        await state.update_data(edit_date_expense=date.strftime("%d-%m-%Y"))
        await process_edit_expense(clb=clb, state=state, bot=bot)

       # dict_data = await state.get_data()
        #id_event = await rq.get_current_event_id()
        #dict_expense_to_add_db = {'tg_id': clb.message.chat.id, 'title_expense': dict_data['title_expense'], 'amount_expense': dict_data['amount_expense'],
                                 # 'id_event': id_event, 'date_expense': dict_data['date_expense']}
       # await rq.add_expense(dict_expense_to_add_db)

        #keyboard = kb.keyboards_main_menu()
        #await clb.message.answer(text=f'Новый расход {dict_data['title_expense']} на сумму {dict_data['amount_expense']} совершенный {dict_data['date_expense']} успешно добавлен в ваш бюджет',
         #                        reply_markup=keyboard)
        # logging.info(f'await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')
        # await state.set_state(state=None)
        # logging.info(f'await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')
        # await state.clear()
        # logging.info(f'await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')

    # else:
    #     await clb.answer(text=f'Вы ничего выбрали', show_alert=True)
    await clb.answer()
