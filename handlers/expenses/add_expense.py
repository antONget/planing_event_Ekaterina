from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta
import aiogram_calendar
from datetime import datetime, time, timedelta
from aiogram.filters.callback_data import CallbackData

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

class ExpenseFSM(StatesGroup):
    state_add_title_expense = State()
    state_add_amount_expense = State()
   # st_3 = State()



@router.message(F.text == 'Запланировать бюджет 💵', IsSuperAdmin())
async def process_expense(message: Message, bot: Bot):
    logging.info('process_expense')
    #await hf.process_del_message_messsage(3, bot, message)
    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-i)
    #     except:
    #         pass

    keyboard = kb.keyboards_main_menu()
    await message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)

    dict_kb = {'Добавить расход': 'add_expense', 'Мой бюджет': 'my_expenses'}
    keyboard = kb.create_in_kb(1, **dict_kb)
    await message.answer(text='В этом разделе вы можете добавлять, редактировать и удалять расходы.', reply_markup=keyboard)



@router.callback_query(F.data == 'add_expense')
async def process_add_title_expense(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Добавить расход, перевод в состояние ожидания ввода Расхода и если есть уже раходы - показать их"""
    logging.info('process_add_title_expense')
    # #await hf.process_del_message_clb(4, bot, clb)
    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass

    await state.set_state(ExpenseFSM.state_add_title_expense) # установка состояния ввода наименования Расхода


    list_expenses: list = []
    temp_list_this_expenses: list = []
    temp_dict_expenses: dict = {}
    for expense in await rq.get_expenses():
        if not expense.title_expense in temp_list_this_expenses:
            temp_list_this_expenses.append(expense.title_expense)
            temp_dict_expenses.update({expense.title_expense: [expense.id]})
            id_expense = expense.id
            title_expense = expense.title_expense
            list_expenses.append([title_expense, f'{id_expense}!add_expense_start'])
        else:
            temp_dict_expenses[expense.title_expense].append(expense.id)
    logging.info(f'list_events = {list_expenses} --- temp_list_this_expenses = {temp_list_this_expenses} ---- temp_dict_expenses = {temp_dict_expenses}')



    if not list_expenses: # если пусто в таблце Event
        await clb.message.edit_text(text=f'Пришлите наименование расхода')

    else: # если в таблице Event есть строки вывожу на кнопки
        # keyboard = kb.keyboards_main_menu()
        # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
        keyboard = kb.create_kb_pagination(
            list_button=list_expenses,
            back=0,
            forward=2,
            count=5,
            prefix='add_expense', # это для колбэка кнопок <<< и >>>
            button_go_away='button_back_process_expense' # через хэндлер "Назад", т.к. там надо вызвать мессаджную функцию
        )
        await clb.message.edit_text(text='Пришлите наименование расхода или выберите его из списка ранее добавленных', reply_markup=keyboard)
        await clb.answer()

# >>>>
@router.callback_query(F.data.startswith('button_forward!add_expense'))
async def process_forward_add_expense(clb: CallbackQuery) -> None:
    logging.info(f'process_forward_expense: {clb.message.chat.id} ----- clb.data = {clb.data}')

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')

    list_expenses: list = []
    temp_list_this_expenses: list = []
    # temp_dict_expenses: dict = {}
    for expense in await rq.get_expenses():
        if not expense.title_expense in temp_list_this_expenses:
            temp_list_this_expenses.append(expense.title_expense)
            # temp_dict_expenses.update({expense.title_expense: [expense.id]})
            id_expense = expense.id
            title_expense = expense.title_expense
            list_expenses.append([title_expense, f'{id_expense}!add_expense_start']) # F.data.endswith('add_expense_start')
        # else:
            # temp_dict_expenses[expense.title_expense].append(expense.id)


    keyboard = kb.create_kb_pagination(
                    list_button=list_expenses,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='add_expense', # это для колбэка кнопок <<< и >>>
                    button_go_away='button_back_process_expense' # через хэндлер "Назад", т.к. там надо вызвать мессаджную функцию
                )

    try:
        await clb.message.edit_text(text='Пришлите наименование расхода или выберите его из списка ранее добавленных', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Пришлите наименование расхода или выберите его из списка ранее добавленныx', reply_markup=keyboard)
    await clb.answer()



# <<<<
@router.callback_query(F.data.startswith('button_back!add_expense'))
async def process_forward_extense_category(clb: CallbackQuery) -> None:
    logging.info(f'process_back: {clb.message.chat.id} ----- clb.data = {clb.data}')

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    list_expenses: list = []
    temp_list_this_expenses: list = []
    # temp_dict_expenses: dict = {}
    for expense in await rq.get_expenses():
        if not expense.title_expense in temp_list_this_expenses:
            temp_list_this_expenses.append(expense.title_expense)
            # temp_dict_expenses.update({expense.title_expense: [expense.id]})
            id_expense = expense.id
            title_expense = expense.title_expense
            list_expenses.append([title_expense, f'{id_expense}!add_expense_start']) # F.data.endswith('add_expense_start')
        # else:
            # temp_dict_expenses[expense.title_expense].append(expense.id)




    keyboard = kb.create_kb_pagination(
                    list_button=list_expenses,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='add_expense', # это для колбэка кнопок <<< и >>>
                    button_go_away='button_back_process_expense' # через хэндлер "Назад", т.к. там надо вызвать мессаджную функцию
                )
    try:
        await clb.message.edit_text(text='Пришлите наименование расхода или выберите его из списка ранее добавленных', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Пришлите наименование расхода или выберите его из списка ранее добавленныx', reply_markup=keyboard)
    await clb.answer()


@router.message(StateFilter(ExpenseFSM.state_add_title_expense))#, F.text)
async def process_add_title_expense_input(message: Message, state: FSMContext, bot: Bot) -> None:
    """ отлавливание ввода наименования Расхода, перевод в состояние ожидания ввода суммы расхлда"""
    logging.info('process_add_title_expense_input')

    # for i in range (2):
    #     try:
    #         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-i)
    #     except:
    #         pass
    title_expense = message.text
    await state.update_data({'title_expense': title_expense})

    # keyboard = kb.keyboards_main_menu()
    # await message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
    dict_kb = {'Назад': 'add_expense'}
    keyboard = kb.create_in_kb(1, **dict_kb)
    await message.answer(text=f'Пришлите сумму расхода для категории <b>{title_expense}</b>', reply_markup=keyboard)

    await state.set_state(ExpenseFSM.state_add_amount_expense)



@router.callback_query(F.data.endswith('add_expense_start'))
async def process_add_title_expense_input_callback(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Для имеющегоя расхода, который высветился на инлайн клавиатуре, просим прислать сумму расходов """
    logging.info(f'process_add_title_expense_input_callback --- clb.data = {clb.data}')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass

    id_expense = int(clb.data.split('!')[0])
    title_expense = (await rq.get_expense_by_id(id_expense=id_expense)).title_expense
    await state.update_data({'title_expense': title_expense}) # Т.к. я сюда пришел через колбэк в state нет 'title_expense'. Добавляем.
    # keyboard = kb.keyboards_main_menu()
    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
    dict_kb = {'Назад': 'add_expense'}
    keyboard = kb.create_in_kb(1, **dict_kb)
    await clb.message.edit_text(text=f'Пришлите сумму расхода для категории <b>{title_expense}</b>', reply_markup=keyboard)
    await state.set_state(ExpenseFSM.state_add_amount_expense)
    await clb.answer()



@router.message(StateFilter(ExpenseFSM.state_add_amount_expense))
async def process_add_amount_expense_input(message: Message, state: FSMContext, bot: Bot) -> None:
    """ отлавливание ввода суммы Расхода, проверка на валидность (число), вывод календаря"""
    logging.info('process_add_title_expense_input')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-i)
    #     except:
    #         pass

    title_expense = (await state.get_data())['title_expense']
    amount_expense = message.text
    # проверка введенных данных на валидность
    if validate_amount(amount=amount_expense):
        await state.update_data({'amount_expense': amount_expense})

        calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
        calendar.set_dates_range(datetime(2024, 1, 1), datetime(2030, 12, 31))
        # получаем текущую дату
        current_date = datetime.now()
        # преобразуем ее в строку
        date1 = current_date.strftime('%m/%d/%y')
        # преобразуем дату в список
        list_date1 = date1.split('/')
        await message.answer(
            f'Укажите дату совершения расходов для категории <b>"{title_expense}"</b>:',
            reply_markup=await calendar.start_calendar(year=int('20'+list_date1[2]), month=int(list_date1[0]))
        )

    else:
        keyboard = kb.keyboards_main_menu()
        await message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
        dict_kb = {'Назад': 'add_expense'}
        keyboard = kb.create_in_kb(1, **dict_kb)
        await message.answer(text=f'Некорректные данные, сумма расхода должна быть числом', reply_markup=keyboard)

    #await state.set_state(ExpenseFSM.state_add_amount_expense)



@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(ExpenseFSM.state_add_amount_expense))
async def process_simple_calendar_start(clb: CallbackQuery, callback_data: CallbackData, state: FSMContext, bot: Bot):
    logging.info(f'process_simple_calendar_start {clb.message.chat.id}')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date = await calendar.process_selection(clb, callback_data)
    if selected:
        #data_note = date.strftime("%Y-%m-%d")
        await state.update_data(date_expense=date.strftime("%d-%m-%Y"))
        dict_data = await state.get_data()
        id_event = await rq.get_current_event_id()
        dict_expense_to_add_db = {'tg_id': clb.message.chat.id, 'title_expense': dict_data['title_expense'],
                                  'amount_expense': dict_data['amount_expense'],
                                  'id_event': id_event, 'date_expense': dict_data['date_expense']}
        await rq.add_expense(dict_expense_to_add_db)

        keyboard = kb.keyboards_main_menu()
        await clb.message.answer(text=f'Новый расход {dict_data["title_expense"]} на сумму'
                                      f' {dict_data["amount_expense"]} совершенный {dict_data["date_expense"]}'
                                      f' успешно добавлен в ваш бюджет',
                                 reply_markup=keyboard)
        logging.info(f'await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')
        await state.set_state(state=None)
        logging.info(f'await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')
        await state.clear()
        logging.info(f'await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')
        await process_expense(clb.message, bot)
    # else:
    #     await clb.answer(text=f'Вы ничего выбрали', show_alert=True)
    await clb.answer()








@router.callback_query(F.data == 'button_back_process_expense')

async def process_button_back_(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Назад в модуле  add_expense, спрашиваем состояние и в зависимосми от него запускаем нужную функцию"""
    logging.info('process_button_back_')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass
    current_state = await state.get_state()
    logging.info(f'current_state = {current_state}')
    if current_state == ExpenseFSM.state_add_title_expense:
        await process_expense(message=clb.message, bot=bot)
    await state.set_state(state=None)
    await clb.answer()
