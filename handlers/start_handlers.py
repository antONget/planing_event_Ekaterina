from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


import keyboards.keyboards as kb
from filters.admin_filter import check_super_admin
from database.models import User
import database.requests as rq
import database.help_function as hf
from datetime import time, date, datetime, timedelta
from handlers.feedback.feedback import process_feedback

router = Router()

storage = MemoryStorage()

import logging
import asyncio

class StartFSM(StatesGroup):
    state_inpup_event = State()
  #  st_2 = State()
   # st_3 = State()




# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
@router.message(F.text == 'Выбрать новое мероприятие 🆕')
async def process_start_command(message: Message,  bot: Bot, state: FSMContext):
    logging.info(f'process_start_command')

    await state.set_state(state=None)
    # перевод пользователя в режи ожидания ввода нового мероприятия
    await state.set_state(StartFSM.state_inpup_event)

    # for i in range (10):
    #     try:
    #         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-i)
    #         logging.info(f'try --- i = {i}')
    #     except:
    #         logging.info(f'pass --- i = {i}')
    #         pass

    # добавление пользователя в БД если еще его там нет
    user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    if not user:
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = "user_name"

        data_user = {"tg_id": message.from_user.id,
                     "user_name": username}
        await rq.add_user(data=data_user)

    # Вывод клавиатуры в зависимости от статуса пользователя
    if await check_super_admin(telegram_id=message.from_user.id):
        # Если администратор, то
            # или список мероприятий,
            # или перевод в режим ожидания ввода названия мероприятия
        #dict_events: dict = {}
        list_events: list = []
        for event in await rq.get_events(): # какие есть мероприятия в таблице Event, если она пустая, то перевод в режим ожидания ввода названия
            key = event.id
            value = event.title_event
            #dict_events[key] = value
            list_events.append([value, f'{key}!events_start'])
        logging.info(f'list_events = {list_events}')

        if not list_events: # если пусто в таблце Event

            await message.answer(text=f'Введите название мероприятия')
        else: # если в таблице Event есть строки вывожу на кнопки
            keyboard = kb.create_kb_pagination(
                list_button=list_events,
                back=0,
                forward=2,
                count=5,
                prefix='start',
                #button_set_state='set_state_add_event'
            )
            await message.answer(text='Добавьте новое мероприятие или продолжите планировать уже созданное', reply_markup=keyboard)
    else: # Если э то не админ, запускаем функцию оставления отзыва
        await process_feedback(message, bot, state)


# >>>>
@router.callback_query(F.data.startswith('button_forward!start'))
async def process_forward(clb: CallbackQuery) -> None:
    logging.info(f'process_forward: {clb.message.chat.id} ----- clb.data = {clb.data}')
    #list_learners = [learner for learner in await rq.get_all_learners()]
    tg_id = clb.message.chat.id

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')
    list_events: list = []
    for event in await rq.get_events(): # какие есть мероприятия в таблице Event, если она пустая, то перевод в режим ожидания ввода названия
        key = event.id
        value = event.title_event
        list_events.append([value, f'{key}!events_start'])

    keyboard = kb.create_kb_pagination(
                    list_button=list_events,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='start',
                    #button_set_state='set_state_add_event'
                )


    #keyboard = kb.kb_choise_learners(action='delete_learner', list_learners=list_learners, back=back, forward=forward, count=6)
    try:
        await clb.message.edit_text(text='Добавьте новое мероприятие или продолжите планировать уже созданное', reply_markup=keyboard)

    except:
        await clb.message.edit_text(text='Добавьте новое мероприятие или продолжите планировать уже созданнoe', reply_markup=keyboard)
    await clb.answer()



# <<<<
@router.callback_query(F.data.startswith('button_back!start'))
async def process_forward(clb: CallbackQuery) -> None:
    logging.info(f'process_back: {clb.message.chat.id} ----- clb.data = {clb.data}')
    #list_learners = [learner for learner in await rq.get_all_learners()]
    tg_id = clb.message.chat.id

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    list_events: list = []
    for event in await rq.get_events(): # какие есть мероприятия в таблице Event, если она пустая, то перевод в режим ожидания ввода названия
        key = event.id
        value = event.title_event
        list_events.append([value, f'{key}!events_start'])

    keyboard = kb.create_kb_pagination(
                    list_button=list_events,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='start',
                    #button_set_state='set_state_add_event'
                )

    try:
        await clb.message.edit_text(text='Добавьте новое мероприятие или продолжите планировать уже созданное', reply_markup=keyboard)

    except:
        await clb.message.edit_text(text='Добавьте новое мероприятие или продолжите планировать уже созданнoe', reply_markup=keyboard)
    await clb.answer()


# @router.callback_query(F.data == 'set_state_add_event')
# async def process_set_state_add_event(clb: CallbackQuery, state: FSMContext) -> None:
#     """Была нажата кнопка 'добавить новое мероприятие', перевод в состояние ожидания ввода названия мероприятия"""
#     logging.info(f'process_set_state_add_event: {clb.message.chat.id} ----- clb.data = {clb.data}')
#     await state.set_state(StartFSM.state_inpup_event)
#     await clb.message.answer(text=f'Введите название мероприятия')




@router.message(StateFilter(StartFSM.state_inpup_event))#, F.text)
@router.message(F.text == 'Главное меню 🏠')
async def process_add_event(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_add_event: {message.chat.id} ----- message.text = {message.text}')

    tg_id = message.chat.id

    if message.text != 'Главное меню 🏠':

        # for i in range (9):
        #     try:
        #         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-i)
        #     except:
        #         pass

        title_event = message.text
        dict_event: dict = {'tg_id': tg_id, 'title_event': title_event}
        await rq.add_event(dict_event)

        # получаем максимальное значение id в таблице Event (именно туда было добавлено последнее Мероприятие)
        id_event = await hf.get_max_id_event()
        dict_current_event = {'id_event': id_event, 'tg_id': tg_id, 'title_event': title_event}

        current_event = await rq.get_current_event_all_model()
        if not current_event:
            await rq.add_current_event(dict_current_event)
        else:
            await rq.set_current_event(tg_id=tg_id, id_event=id_event, title_event=title_event)
    else:
        await state.set_state(state=None)
        title_event = await rq.get_current_event()

    await message.answer(
    text=f"Добро пожаловать в EventPlannerBot!\nЧат-бот поможет организовать корпоративное мероприятие: подберёт место проведения и исполнителей; "
        f"спланирует бюджет; напомнит о дедлайнах задач; соберет обратную связь.\n\nПожалуйста, выберите опцию для мероприятия <b>{title_event}</b>:",
        reply_markup=kb.keyboards_common_four_buttons())
    logging.info(f'await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')
    await state.clear()
    logging.info(f'СБРАСЫВАЕМ СОСТОЯНИЕ await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')



@router.callback_query(F.data.endswith('events_start')) # прихожу сюда по этой кнопке ['Мероприятие 8', '8!events_start']
async def show_start_main_menu(clb: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """Нажатие на мероприятие, показ реплай клавиатуры: 'Задачи', 'Выбрать место', 'Бюджет', 'Исполнители' """
    logging.info(f'show_start_main_menu --- clb.data = {clb.data}')
    await clb.answer()
    # если в стартовом хэндлере process_start_command не ввел название нового мероприятия, и нажал на Мероприятие,
    # то сбросить состояние
    await state.clear()
    # удаляю инлайн клавиатуру прошлого сообщения
    await clb.message.delete()

    # подготовка данных для таблицы CurrentEvent (текущее задание, с которым в данный момент работает пользователь)
    id_event = clb.data.split('!')[0]
    title_event = await rq.get_event_by_id(id_event=id_event)
    tg_id = await rq.get_tg_id_from_event_by_id(id_event=id_event)

    dict_current_event = {'id_event': id_event, 'tg_id': tg_id, 'title_event': title_event}

    current_event = await rq.get_current_event_all_model()
    current_event_bool = False
    for event in current_event:
        if event.id == 1:
           current_event_bool = True


    if not current_event_bool:
        await rq.add_current_event(dict_current_event)
    else:
        await rq.set_current_event(tg_id=tg_id, id_event=id_event, title_event=title_event)


    try:
        await clb.message.edit_text(
            text=f"Добро пожаловать в EventPlannerBot!\nЧат-бот поможет организовать корпоративное мероприятие: подберёт место проведения и исполнителей; "
                f"спланирует бюджет; напомнит о дедлайнах задач; соберет обратную связь.\n\nПожалуйста, выберите опцию для мероприятия <b>{title_event}</b>:",
            reply_markup=kb.keyboards_common_four_buttons()
            )
    except:
        await clb.message.answer(
        text=f"Добро пожаловать в EventPlannerBot!\nЧат-бот поможет организовать корпоративное мероприятие: подберёт место проведения и исполнителей; "
            f"спланирует бюджет; напомнит о дедлайнах задач; соберет обратную связь.\n\nПожалуйста, выберите опцию для мероприятия <b>{title_event}</b>:",
        reply_markup=kb.keyboards_common_four_buttons()
        )
    await clb.answer()