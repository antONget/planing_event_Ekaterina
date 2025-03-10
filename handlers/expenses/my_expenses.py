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



router = Router()

storage = MemoryStorage()

import logging
import asyncio

class PeriodExpenseFSM(StatesGroup):
    state_start_perid_expense = State()
    state_finish_period_expense = State()



@router.callback_query(F.data == 'my_expenses')
async def process_my_expenses(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Мой бюджет"""
    logging.info('process_my_expenses')
    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass

    # keyboard = kb.keyboards_main_menu()
    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
    dict_kb = {'По категориям': 'category', 'За период': 'period'}
    keyboard = kb.create_in_kb(1, **dict_kb)
    await clb.message.edit_text(text=f'В этом разделе вы можете посмотреть свои расходы по категориям и за период.', reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data == 'category')
async def process_my_expenses_category(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Выбрали просмотр трат по категориям"""
    logging.info('process_my_expenses')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass

    list_expenses: list = []
    temp_list_this_expenses: list = []
    ##temp_dict_expenses: dict = {}
    for expense in await rq.get_expenses():
        if expense.id_event == (await rq.get_current_event_id()):
            if not expense.title_expense in temp_list_this_expenses:
                temp_list_this_expenses.append(expense.title_expense)
                ##temp_dict_expenses.update({expense.title_expense: [expense.id]})
                id_expense = expense.id
                title_expense = expense.title_expense
                list_expenses.append([title_expense, f'{id_expense}!for_keyboard_expense_category']) # F.data.endswith('for_keyboard_expense_category')
            #await state.update_data()
        ##else:
          ##  temp_dict_expenses[expense.title_expense].append(expense.id)
    logging.info(f'list_events = {list_expenses} --- temp_list_this_expenses = {temp_list_this_expenses}') ## temp_dict_expenses = {temp_dict_expenses}')
    ### my_expenses.py:77 #INFO     [2025-02-21 17:09:40,356] - root -
    ### list_events = [['Траты на ветер', '1!expense_category'], ['Нужные траты', '3!expense_category'], ['Продукты', '4!expense_category'], ['Автомобиль', '5!expense_category']] ---
    ### temp_list_this_expenses = ['Траты на ветер', 'Нужные траты', 'Продукты', 'Автомобиль'] ----
    # temp_dict_expenses = {'Траты на ветер': [1, 2], 'Нужные траты': [3], 'Продукты': [4], 'Автомобиль': [5, 6, 7, 8, 9, 10]}

    # Прохожу по словарю temp_dict_expenses и заношу его в state
    ##logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')
    ##for key_, value in temp_dict_expenses.items():
    ##    await state.update_data({key_: value})
    ##logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')

    if not list_expenses: # если пусто в таблце Event
        # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=kb.keyboards_main_menu())
        await clb.message.edit_text(text=f'Список расходов пуст.', reply_markup=kb.create_in_kb(1, **{'Назад': 'my_expenses'}))


    else: # если в таблице Event есть строки вывожу на кнопки
        # keyboard = kb.keyboards_main_menu()
        # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
        keyboard = kb.create_kb_pagination(
            list_button=list_expenses,
            back=0,
            forward=2,
            count=5,
            prefix='expense_category', # это для колбэка кнопок <<< и >>>
            button_go_away='my_expenses'
        )
        await clb.message.edit_text(text='Выберете расход из списка ранее дoбавленных', reply_markup=keyboard)
    await clb.answer()


# >>>>
@router.callback_query(F.data.startswith('button_forward!expense_category'))
async def process_forward_expense_category(clb: CallbackQuery) -> None:
    logging.info(f'process_forward_expense_category: {clb.message.chat.id} ----- clb.data = {clb.data}')

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')

    list_expenses: list = []
    temp_list_this_expenses: list = []
    for expense in await rq.get_expenses():
        if expense.id_event == (await rq.get_current_event_id()):
            if not expense.title_expense in temp_list_this_expenses:
                temp_list_this_expenses.append(expense.title_expense)
                id_expense = expense.id
                title_expense = expense.title_expense
                list_expenses.append([title_expense, f'{id_expense}!for_keyboard_expense_category']) # F.data.endswith('for_keyboard_expense_category')
    logging.info(f'list_expenses = {list_expenses}')
    keyboard = kb.create_kb_pagination(
                    list_button=list_expenses,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='expense_category',
                    button_go_away='my_expenses'
                )
    logging.info(f'keyboard = {keyboard}')
    #await asyncio.sleep(7)

    try:
        await clb.message.edit_text(text='Выберите расxoд из списка ранее добавленных', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Выберитe расход из списка ранее добавленныx', reply_markup=keyboard)
    await clb.answer()


# <<<<
@router.callback_query(F.data.startswith('button_back!expense_category'))
async def process_back_extense_category(clb: CallbackQuery) -> None:
    logging.info(f'process_back_extense_category: {clb.message.chat.id} ----- clb.data = {clb.data}')

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    list_expenses: list = []
    temp_list_this_expenses: list = []
    for expense in await rq.get_expenses():
        if expense.id_event == (await rq.get_current_event_id()):
            if not expense.title_expense in temp_list_this_expenses:
                temp_list_this_expenses.append(expense.title_expense)
                id_expense = expense.id
                title_expense = expense.title_expense
                list_expenses.append([title_expense, f'{id_expense}!for_keyboard_expense_category']) # F.data.endswith('for_keyboard_expense_category')


    keyboard = kb.create_kb_pagination(
                    list_button=list_expenses,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='expense_category',
                    button_go_away='my_expenses'
                )
    logging.info(f'keyboard = {keyboard}')
    try:
        await clb.message.edit_text(text='Выберите расxoд из списка ранее добавленных', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Выберитe расход из списка ранее добавленныx', reply_markup=keyboard)
    await clb.answer()



# Получаем
@router.callback_query(F.data.endswith('for_keyboard_expense_category'))
async def process_show_kb_from_category(clb: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    logging.info(f'process_show_kb_from_category: {clb.message.chat.id} ----- clb.data = {clb.data}')

    # #await hf.process_del_message_clb(3, bot, clb)

    ##title_expense = clb.data.split('!')[0]
    # По этому id получить название расхода и сформировать спимок списков по ключу с этим title_event
    id_expense = int(clb.data.split('!')[0])
    title_expense = (await rq.get_expense_by_id(id_expense)).title_expense
    # Для пагинации надо сформировать такой же список, для этого title_expense передаем в FSM
    await state.update_data(title_expense_from_process_show_kb_from_category = title_expense)
    list_expenses: list =[]
    # Для категории считаем сууму расходов тут
    amount_expense_category: int = 0
    for expense in await rq.get_expenses():
        if expense.title_expense == title_expense and expense.tg_id == clb.message.chat.id:
            list_ = [f'🗓 {expense.date_expense}   {expense.amount_expense} ₽', f'{expense.id}!expense_category']
            list_expenses.append(list_)
            amount_expense_category += int(expense.amount_expense)
    #rq.get_expense_by_title(title_expense):
    # для пагинации и формирования этого же списка нужен title_expense. Сохраняем его в state
    ##await state.update_data(title_expense_for_category_pagination = title_expense)
    ##data_state = await state.get_data()
    ##list_id_expense = data_state[title_expense]
    ## в состояние я ничего не передал. Проходим
    # По id из list_id_expense формируем список для кнопок, проходим по таблице Expenses
    # for id_expense in list_id_expense:
    #     data_expense = await rq.get_expense_by_id(id_expense=id_expense)
    #     list_ = [f'🗓 {data_expense.date_expense}   {data_expense.amount_expense} ₽', f'{id_expense}!expense_category']
    #     list_expenses.append(list_)
    #     # суммируем к  amount_expense_category сумму расхода данной категории по его id
    #     amount_expense_category += int(data_expense.amount_expense)

    # # Сохраняем в состоянии эту сумму amount_expense_category
    await state.update_data(amount_expense_category = amount_expense_category)

    # keyboard = kb.keyboards_main_menu()
    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
    keyboard = kb.create_kb_pagination(
        list_button=list_expenses,
        back=0,
        forward=2,
        count=5,
        prefix='for_keyboard_expense_category', # это для колбэка кнопок <<< и >>>
        button_go_away='category',
        button_amount_expense_category='button_amount_expense_category'
    )
    await clb.message.edit_text(text=f'Выберите запись о расходе из списка для расхода <b>"{title_expense}"</b>', reply_markup=keyboard)
    await clb.answer()




# >>>>
@router.callback_query(F.data.startswith('button_forward!for_keyboard_expense_category'))
async def process_forward_for_keyboard_expense_category(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_forward_for_keyboard_expense_category: {clb.message.chat.id} ----- clb.data = {clb.data}')

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')

    # data_state = await state.get_data()
    # title_expense = data_state['title_expense_for_category_pagination']
    # list_id_expense = data_state[title_expense]
    # list_expenses: list =[]

    # # По id из list_id_expense формируем список для кнопок, проходим по таблице Expenses
    # for id_expense in list_id_expense:
    #     data_expense = await rq.get_expense_by_id(id_expense=id_expense)
    #     list_ = [f'🗓 {data_expense.date_expense} {data_expense.amount_expense} ₽', f'{id_expense}!expense_category']
    #     list_expenses.append(list_)
    title_expense = (await state.get_data())['title_expense_from_process_show_kb_from_category']
    list_expenses: list =[]
    # Для категории считаем сууму расходов тут
    #amount_expense_category: int = 0
    for expense in await rq.get_expenses():
        if expense.title_expense == title_expense:
            list_ = [f'🗓 {expense.date_expense}   {expense.amount_expense} ₽', f'{expense.id}!expense_category']
            list_expenses.append(list_)
            #amount_expense_category += int(expense.amount_expense)


    keyboard = kb.create_kb_pagination(
                    list_button=list_expenses,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='for_keyboard_expense_category', # это для колбэка кнопок <<< и >>>
                    button_go_away='category',
                    button_amount_expense_category='button_amount_expense_category'
                )

    try:
        await clb.message.edit_text(text=f'Выберите запись о расходе из списка для расхода <b>"{title_expense}"</b>', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text=f'Выберите запись о расходе из спискa для расхода <b>"{title_expense}"</b>', reply_markup=keyboard)
    await clb.answer()



# <<<<
@router.callback_query(F.data.startswith('button_back!for_keyboard_expense_category'))
async def process_back_extense_period(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_back_extense_period: {clb.message.chat.id} ----- clb.data = {clb.data}')

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    # data_state = await state.get_data()
    # title_expense = data_state['title_expense_for_category_pagination']
    # list_id_expense = data_state[title_expense]
    # list_expenses: list =[]

    # # По id из list_id_expense формируем список для кнопок, проходим по таблице Expenses
    # for id_expense in list_id_expense:
    #     data_expense = await rq.get_expense_by_id(id_expense=id_expense)
    #     list_ = [f'🗓 {data_expense.date_expense} {data_expense.amount_expense} ₽', f'{id_expense}!expense_category']
    #     list_expenses.append(list_)

    title_expense = (await state.get_data())['title_expense_from_process_show_kb_from_category']
    list_expenses: list =[]
    # Для категории считаем сууму расходов тут
    #amount_expense_category: int = 0
    for expense in await rq.get_expenses():
        if expense.title_expense == title_expense:
            list_ = [f'🗓 {expense.date_expense}   {expense.amount_expense} ₽', f'{expense.id}!expense_category']
            list_expenses.append(list_)
            #amount_expense_category += int(expense.amount_expense)

    keyboard = kb.create_kb_pagination(
                    list_button=list_expenses,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='for_keyboard_expense_category', # это для колбэка кнопок <<< и >>>
                    button_go_away='category',
                    button_amount_expense_category='button_amount_expense_category'
                )

    try:
        await clb.message.edit_text(text=f'Выберите запись о расходе из списка для расхода <b>"{title_expense}"</b>', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text=f'Выберите запись о расходе из спискa для расхода <b>"{title_expense}"</b>', reply_markup=keyboard)
    await clb.answer()






# PERIOD

@router.callback_query(F.data == 'period')
async def process_my_expenses_period(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Выбрали просмотр трат за период"""
    logging.info('process_my_expenses_period')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass

    # keyboard = kb.keyboards_main_menu()
    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)

    await state.set_state(state=None)
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2030, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%m/%d/%y')
    # преобразуем дату в список
    list_date1 = date1.split('/')

    await clb.message.edit_text(
        f'Выберите начало периода',
        reply_markup=await calendar.start_calendar(year=int('20'+list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(PeriodExpenseFSM.state_start_perid_expense)
    await clb.answer()



async def process_buttons_press_finish(callback: CallbackQuery, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%d/%m/%Y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.edit_text(
        "Выберите конец периода",
        reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
    )
    await callback.answer()
    await state.set_state(PeriodExpenseFSM.state_finish_period_expense)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(PeriodExpenseFSM.state_start_perid_expense))
async def process_simple_calendar_start(callback_query: CallbackQuery, callback_data: CallbackData,
                                        state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date_start = await calendar.process_selection(callback_query, callback_data)
    if selected:
        # await callback_query.message.edit_text(
        #     f'Начало периода {date.strftime("%d-%m-%Y")}')
        await state.update_data(start_period=date_start.strftime("%d-%m-%Y"))
        await process_buttons_press_finish(callback_query, state=state)
        await callback_query.answer()


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(PeriodExpenseFSM.state_finish_period_expense))
async def process_simple_calendar_finish(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext, bot: Bot):
    logging.info(f'process_simple_calendar_finish')

    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date_finish = await calendar.process_selection(callback, callback_data)
    if selected:
        await state.update_data(finish_period=date_finish.strftime("%d-%m-%Y")) # преобразование в строку без времени и с типом записи dd-mm-yyyy
        data_ = await state.get_data()
        await state.set_state(state=None)


        #await callback.message.answer(text=f'Начало срока: {data_['start_period']} --- окончание срока: {data_['finish_period']} ')

        # составляем список кнопок для вывода в нужном интервале
        list_expenses: list =[]
        data_start_period = datetime.strptime(data_['start_period'], "%d-%m-%Y")
        data_finish_period = datetime.strptime(data_['finish_period'], "%d-%m-%Y")
        amount_expense_for_button: int = 0
        for expense in await rq.get_expenses():
            if expense.id_event == (await rq.get_current_event_id()):
                data_expanse = datetime.strptime(expense.date_expense, "%d-%m-%Y")
                if data_start_period <= data_expanse <= data_finish_period:
                    logging.info(f'Условие соблюдено!')
                    id_expense = expense.id
                    title_expense = f'"{expense.title_expense}" {expense.amount_expense} ₽' # Название __ сумма
                    list_expenses.append([title_expense, f'{id_expense}!expense_period']) # F.data.endswith('expense_category')
                    amount_expense_for_button += int(expense.amount_expense)

        logging.info(f'list_expenses = {list_expenses}')
        logging.info(f'amount_expense_for_button = {amount_expense_for_button}')
        await state.update_data(amount_expense_for_button = amount_expense_for_button)
        logging.info(f'await state.get_data() = {await state.get_data()}')

        ##await hf.process_del_message_clb(count=5, bot=bot, clb=callback)
        if not list_expenses: # если пусто в таблце Event
            # keyboard = kb.keyboards_main_menu()
            # await callback.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
            keyboard = kb.create_in_kb(1, **{'Назад': 'my_expenses'})
            await callback.message.edit_text(text=f'Список расходов пуст.', reply_markup=keyboard)
        else: # если в таблице Event есть строки вывожу на кнопки
            # keyboard = kb.keyboards_main_menu()
            # await callback.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
            keyboard = kb.create_kb_pagination(
                list_button=list_expenses,
                back=0,
                forward=2,
                count=5,
                prefix='expense_period', # это для колбэка кнопок <<< и >>>
                button_amount_expense_period='button_amount_expense_period',
                button_go_away='my_expenses'
            )
            await callback.message.edit_text(text='Выберите запись о расходе из списка', reply_markup=keyboard)
        await callback.answer()



# >>>>
@router.callback_query(F.data.startswith('button_forward!expense_period'))
async def process_forward_expense_perio(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_forward_expense_period: {clb.message.chat.id} ----- clb.data = {clb.data}')

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')

    data_ = await state.get_data()
    list_expenses: list =[]
    data_start_period = datetime.strptime(data_['start_period'], "%d-%m-%Y")
    data_finish_period = datetime.strptime(data_['finish_period'], "%d-%m-%Y")
    amount_expense_for_button: int = 0
    for expense in await rq.get_expenses():
        if expense.id_event == (await rq.get_current_event_id()):
            data_expanse = datetime.strptime(expense.date_expense, "%d-%m-%Y")
            if data_start_period <= data_expanse <= data_finish_period:
                logging.info(f'Условие соблюдено!')
                id_expense = expense.id
                title_expense = f'"{expense.title_expense}" {expense.amount_expense} ₽' # Название __ сумма
                list_expenses.append([title_expense, f'{id_expense}!expense_period']) # F.data.endswith('expense_category')
                amount_expense_for_button += int(expense.amount_expense)

    logging.info(f'amount_expense_for_button = {amount_expense_for_button}')
    await state.update_data(amount_expense_for_button = amount_expense_for_button)
    logging.info(f'await state.get_data() = {await state.get_data()}')


    keyboard = kb.create_kb_pagination(
                    list_button=list_expenses,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='expense_period', # это для колбэка кнопок <<< и >>>
                    button_amount_expense_period='button_amount_expense_period',
                    button_go_away='my_expenses'
                )

    try:
        await clb.message.edit_text(text='Выберите запись о расходе из списка', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Выберите запись о расходе из спискa', reply_markup=keyboard)
    await clb.answer()



# <<<<
@router.callback_query(F.data.startswith('button_back!expense_period'))
async def process_back_expense_period(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_back_expense_period: {clb.message.chat.id} ----- clb.data = {clb.data}')

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    data_ = await state.get_data()
    list_expenses: list =[]
    data_start_period = datetime.strptime(data_['start_period'], "%d-%m-%Y")
    data_finish_period = datetime.strptime(data_['finish_period'], "%d-%m-%Y")
    amount_expense_for_button: int = 0
    for expense in await rq.get_expenses():
        if expense.id_event == (await rq.get_current_event_id()):
            data_expanse = datetime.strptime(expense.date_expense, "%d-%m-%Y")
            if data_start_period <= data_expanse <= data_finish_period:
                logging.info(f'Условие соблюдено!')
                id_expense = expense.id
                title_expense = f'"{expense.title_expense}" {expense.amount_expense} ₽' # Название __ сумма
                list_expenses.append([title_expense, f'{id_expense}!expense_period']) # F.data.endswith('expense_category')
                amount_expense_for_button += int(expense.amount_expense)

    # logging.info(f'amount_expense_for_button = {amount_expense_for_button}')
    await state.update_data(amount_expense_for_button = amount_expense_for_button)
    # logging.info(f'await state.get_data() = {await state.get_data()}')

    keyboard = kb.create_kb_pagination(
                    list_button=list_expenses,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='expense_period', # это для колбэка кнопок <<< и >>>
                    button_amount_expense_period='button_amount_expense_period',
                    button_go_away='my_expenses'
                )

    try:
        await clb.message.edit_text(text='Выберите запись о расходе из списка', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Выберите запись о расходе из спискa', reply_markup=keyboard)
    await clb.answer()



@router.callback_query(F.data == 'button_amount_expense_period')
@router.callback_query(F.data == 'button_amount_expense_category')
async def process_button_amount_expense(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Сумма Расходов"""
    logging.info(f'process_button_amount_expense ---- await state.get_state() = {await state.get_state()} ---- await state.get_data() = {await state.get_data()}')

    # #await hf.process_del_message_clb(count=5, bot=bot, clb=clb)
    # keyboard = kb.keyboards_main_menu()
    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
    data_state = await state.get_data()

    if clb.data.endswith('period'):
        dict_kb = {'Назад': 'my_expenses'}
        keyboard = kb.create_in_kb(1, **dict_kb)
        start_period = data_state['start_period']
        finish_period = data_state['finish_period']
        amount_expense = data_state['amount_expense_for_button']
        await clb.message.edit_text(text=f'Сумма расходов за период {start_period} --- {finish_period} составляет: {amount_expense} рублей.', reply_markup=keyboard)

    elif clb.data.endswith('category'):
        dict_kb = {'Назад': 'my_expenses'}
        keyboard = kb.create_in_kb(1, **dict_kb)

        amount_expense_category = data_state['amount_expense_category']

        await clb.message.edit_text(text=f'Сумма расходов в категории составляет: {amount_expense_category} ₽.', reply_markup=keyboard)
    await clb.answer()
