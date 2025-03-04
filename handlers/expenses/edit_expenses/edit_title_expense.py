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





# Редактируем КАТЕГОРИЮ РАСХОДА title_expense

@router.callback_query(F.data.startswith('next_edit_expense!category'))
async def process_edit_expense_category(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Редактировать Категорию, показываем клавиатуру со всеми категориями, переводим в состояние ожидания ввода нового названия  """
    logging.info(f'process_edit_expense_category --- clb.data = {clb.data}')


    #await hf.process_del_message_clb(3, bot, clb)
    list_expenses: list = []
    temp_list_this_expenses: list = []
    temp_dict_expenses: dict = {}
    for expense in await rq.get_expenses():
        if expense.id_event == (await rq.get_current_event_id()): # траты только текущего мероприятия
            if not expense.title_expense in temp_list_this_expenses:
                temp_list_this_expenses.append(expense.title_expense)
               # temp_dict_expenses.update({expense.title_expense: [expense.id]})
                id_expense = expense.id
                title_expense = expense.title_expense
                list_expenses.append([title_expense, f'edit_expense!{id_expense}']) # 'Редактировать ✏️': f'edit_expense!{id_expense}'

       # else: # а если траты кагого-то другого мероприятия
        #    temp_dict_expenses[expense.title_expense].append(expense.id)
    logging.info(f'list_events = {list_expenses} --- temp_list_this_expenses = {temp_list_this_expenses} ---- temp_dict_expenses = {temp_dict_expenses}')

    if not list_expenses: # если пусто в таблце Event
        await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:',
                                 reply_markup=kb.keyboards_main_menu())
        await clb.message.answer(text=f'Пришлите наименование расхода')

    else: # если в таблице Event есть строки вывожу на кнопки
        keyboard = kb.create_kb_pagination(
            list_button=list_expenses,
            back=0,
            forward=2,
            count=5,
            prefix='edit_expense', # это для колбэка кнопок <<< и >>>
            button_go_away='process_edit_expense'
        )
        await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:',
                                 reply_markup=kb.keyboards_main_menu())
        await clb.message.answer(text='Пришлите наименование расхода или выберите его из списка ранее добавленных', reply_markup=keyboard)

        # Установка состояния ожидания ввода нового наименования Расхода для редактирования
        await state.set_state(EditExpenseFSM.state_edit_title_expense)
        await clb.answer()

# отлавливаем или введенное название по состоянию  или колбэк
# Но сперва пагинация

# >>>>
@router.callback_query(F.data.startswith('button_forward!edit_expense'))
async def process_forward_edit_expense(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_forward_edit_expense: {clb.message.chat.id} ----- clb.data = {clb.data}')

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')

    list_expenses: list = []
    temp_list_this_expenses: list = []
    temp_dict_expenses: dict = {}
    for expense in await rq.get_expenses():
        if expense.id_event == (await rq.get_current_event_id()):
            if not expense.title_expense in temp_list_this_expenses:
                temp_list_this_expenses.append(expense.title_expense)
                #temp_dict_expenses.update({expense.title_expense: [expense.id]})
                id_expense = expense.id
                title_expense = expense.title_expense
                list_expenses.append([title_expense, f'edit_expense!{id_expense}'])
                #await state.update_data(new_id_title_edit = id_expense)
       # else:
          #  temp_dict_expenses[expense.title_expense].append(expense.id)

    keyboard = kb.create_kb_pagination(
                    list_button=list_expenses,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='edit_expense', # это для колбэка кнопок <<< и >>>
                    button_go_away='process_edit_expense'
                )

    try:
        await clb.message.edit_text(text='Пришлите наименoвание расхода или выберите его из списка ранее добавленных', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Пришлите наименование расхода или выберите его из списка ранее добавленныx', reply_markup=keyboard)
    await clb.answer()



# <<<<
@router.callback_query(F.data.startswith('button_back!edit_expense'))
async def process_forward_extense_edit_category(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_forward_extense_edit_category: {clb.message.chat.id} ----- clb.data = {clb.data}')

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    list_expenses: list = []
    temp_list_this_expenses: list = []
    temp_dict_expenses: dict = {}
    for expense in await rq.get_expenses():
        if expense.id_event == (await rq.get_current_event_id()):
            if not expense.title_expense in temp_list_this_expenses:
                temp_list_this_expenses.append(expense.title_expense)
             #   temp_dict_expenses.update({expense.title_expense: [expense.id]})
                id_expense = expense.id
                title_expense = expense.title_expense
                list_expenses.append([title_expense, f'edit_expense!{id_expense}'])
                #await state.update_data(new_id_title_edit = id_expense)
       # else:
           # temp_dict_expenses[expense.title_expense].append(expense.id)

    keyboard = kb.create_kb_pagination(
                    list_button=list_expenses,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='edit_expense', # это для колбэка кнопок <<< и >>>
                    button_go_away='process_edit_expense'
                )
    try:
        await clb.message.edit_text(text='Пришлитe наименование расхода или выберите его из списка ранее добавленных', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Пришлите наименование расхода или выберите его из списка ранее добавленныx', reply_markup=keyboard)
    await clb.answer()


@router.message(F.text, StateFilter(EditExpenseFSM.state_edit_title_expense))
async def process_edit_title_expenses_state(message: Message, state: FSMContext, bot: Bot):
    new_title_expense = message.text

    logging.info(f'process_edit_expense_state  --- new_title_expense = {new_title_expense}')

    await state.update_data(edit_title_expense = new_title_expense)
    #await hf.process_del_message_messsage(4, bot, message)
    await state.set_state(EditExpenseFSM.state_after_input_title_expense)
    logging.info(f'{await state.get_data()} --- {await state.get_state()}')

    await process_edit_expense(clb=message, state=state, bot=bot)

    #await message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:',
     #                        reply_markup=kb.keyboards_main_menu())