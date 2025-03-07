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

router = Router()

storage = MemoryStorage()

import logging
import asyncio

class FeedbackFSM(StatesGroup):
    state_feedback = State()
  #  st_2 = State()
   # st_3 = State()




# Этот хэндлер срабатывает на команду /start если пользователь не админ
async def process_feedback(message: Message,  bot: Bot, state: FSMContext):
    logging.info(f'process_feedback')


    # перевод пользователя в режи ожидания отзыва
    await state.set_state(FeedbackFSM.state_feedback)

    #await hf.process_del_message_messsage(5, bot, message)

    list_events: list = []
    for event in await rq.get_events(): # какие есть мероприятия в таблице Event, если она пустая, то перевод в режим ожидания ввода названия
        key = event.id
        value = event.title_event
        #dict_events[key] = value
        list_events.append([value, f'{key}!feedback_event'])
    logging.info(f'list_events = {list_events}')

    if not list_events: # если пусто в таблце Event

        await message.answer(text=f'Мероприятий нет.')
    else: # если в таблице Event есть строки вывожу на кнопки
        keyboard = kb.create_kb_pagination(
            list_button=list_events,
            back=0,
            forward=2,
            count=5,
            prefix='feedback',
            #button_set_state='set_state_add_event'
        )
        await message.answer(text=f'<b>Добро пожаловать в EventPlannerBot!</b>\nОставьте отзыв о посещенном мероприятии.\n'
                             f'Выберите мероприятие на которое вы бы хотели оставить отзыв.', reply_markup=keyboard)



# >>>>
@router.callback_query(F.data.startswith('button_forward!feedback'))
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
        list_events.append([value, f'{key}!feedback_event'])

    keyboard = kb.create_kb_pagination(
                    list_button=list_events,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='feedback',
                    #button_set_state='set_state_add_event'
                )


    #keyboard = kb.kb_choise_learners(action='delete_learner', list_learners=list_learners, back=back, forward=forward, count=6)
    try:
        await clb.message.edit_text(text=f'<b>Добро пожаловать в EventPlannerBot!</b>\nОставьте отзыв о посещенном мерoприятии.\n'
                                    f'Выберите мероприятие на которое вы бы хотели оставить отзыв.', reply_markup=keyboard)

    except:
        await clb.message.edit_text(text=f'<b>Добро пожаловать в EventPlannerBot!</b>\nОставьте отзыв о посещеннoм мероприятии.\n'
                                    f'Выберите мероприятие на которое вы бы хотели оставить отзыв.', reply_markup=keyboard)
    await clb.answer()



# <<<<
@router.callback_query(F.data.startswith('button_back!feedback'))
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
        list_events.append([value, f'{key}!feedback_event'])

    keyboard = kb.create_kb_pagination(
                    list_button=list_events,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='feedback',
                    #button_set_state='set_state_add_event'
                )

    try:
        await clb.message.edit_text(text=f'<b>Добрo пожаловать в EventPlannerBot!</b>\nОставьте отзыв о посещенном мероприятии.\n'
                                    f'Выберите мероприятие на которое вы бы хотели оставить отзыв.', reply_markup=keyboard)

    except:
        await clb.message.edit_text(text=f'<b>Добро пожаловaть в EventPlannerBot!</b>\nОставьте отзыв о посещенном мероприятии.\n'
                                    f'Выберите мероприятие на которое вы бы хотели оставить отзыв.', reply_markup=keyboard)
    await clb.answer()


# @router.callback_query(F.data == 'set_state_add_event')
# async def process_set_state_add_event(clb: CallbackQuery, state: FSMContext) -> None:
#     """Была нажата кнопка 'добавить новое мероприятие', перевод в состояние ожидания ввода названия мероприятия"""
#     logging.info(f'process_set_state_add_event: {clb.message.chat.id} ----- clb.data = {clb.data}')
#     await state.set_state(StartFSM.state_inpup_event)
#     await clb.message.answer(text=f'Введите название мероприятия')


@router.callback_query(F.data.endswith('!feedback_event'))
async def process_input_estimation(clb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Сперва пользователь ставит оценку на инлайн клавиатуре"""
    logging.info(f'process_input_estimation: {clb.message.chat.id} ----- clb.data = {clb.data}')

    id_event = int(clb.data.split('!')[0])
    kb_dict = {'1': f'{id_event}!{1}!feedback_event_input',
               '2': f'{id_event}!{2}!feedback_event_input',
               '3': f'{id_event}!{3}!feedback_event_input',
               '4': f'{id_event}!{4}!feedback_event_input',
               '5': f'{id_event}!{5}!feedback_event_input'}
    await clb.message.answer(text=f'Поставте оценку мероприятию <b>"{await rq.get_event_by_id(id_event)}"</b>.',
                             reply_markup=kb.create_in_kb(1, **kb_dict))
    await clb.answer()


@router.callback_query(F.data.endswith('!feedback_event_input'))
async def process_input_feed(clb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Сохраняем оценку в FSM, перевод в состояние ожидания ввода отзыва"""
    logging.info(f'process_input_feed: {clb.message.chat.id} ----- clb.data = {clb.data}')

    id_event = int(clb.data.split('!')[0])
    estimation = int(clb.data.split('!')[1])

    await state.update_data(state_estimation_event = estimation)
    await state.update_data(state_id_event = id_event)
    await state.set_state(FeedbackFSM.state_feedback)
    #await hf.process_del_message_clb(1, bot, clb)
    await clb.message.answer(text='Пришлите отзыв о мероприятии.')
    await clb.answer()


@router.message(F.text, StateFilter(FeedbackFSM.state_feedback))
async def process_send_feedback(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_send_feedback: {message.chat.id} ----- message.text = {message.text}')

    text_feedback = message.text
    id_event = (await state.get_data())['state_id_event']
    estimation = (await state.get_data())['state_estimation_event']
    title_event = await rq.get_event_by_id(id_event)

    #tg_id_event = data_event.tg_id
    tg_id_admin_event = await rq.get_tg_id_from_event_by_id(id_event)
    logging.info(f'tg_id_event = {tg_id_admin_event}')
    user_name = (await rq.get_user_by_id(message.chat.id)).user_name
    user = user_name if user_name != 'user_name' else message.chat.id

    await bot.send_message(
        chat_id=tg_id_admin_event,
        text=f'Пользователь {user} оставил отзыв по мероприятию <b>"{title_event}"</b>:\nОценка: {estimation} \n{text_feedback}'
    )
    await message.answer(text='Благодарим за оставленный отзыв, нам очень важно вае мнение!')

    # сохраняем в БД этот отзыв
    dict_feedback = {'tg_id': message.chat.id, 'id_event': id_event, 'estimation': estimation, 'feedback': text_feedback}

    await rq.add_event_feedback(dict_feedback)
    await process_feedback(message, bot, state)