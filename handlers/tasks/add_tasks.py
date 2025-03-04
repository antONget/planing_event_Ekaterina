from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta
import database.help_function as hf

import keyboards.keyboards as kb

from filters.admin_filter import check_super_admin
from database.models import User
import database.requests as rq
from datetime import time, date, datetime, timedelta
from filters.admin_filter import IsSuperAdmin
from filters.filters import validate_date, validate_overdue



router = Router()

storage = MemoryStorage()

import logging
import asyncio

class TaskFSM(StatesGroup):
    state_add_task = State()
    state_add_deadline = State()
   # st_3 = State()



@router.message(F.text == 'Задачи 📜', IsSuperAdmin())
async def process_task(message: Message, bot: Bot):
    logging.info('process_task')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-i)
    #     except:
    #         pass

    keyboard = kb.keyboards_main_menu()
    await message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
    dict_kb = {'Добавить 📥': 'add_task', 'Мои задачи': 'my_tasks'}
    keyboard = kb.create_in_kb(1, **dict_kb)

    await message.answer(text='В этом разделе вы можете добавить, редактировать и удалять задачи мероприятия:', reply_markup=keyboard)


@router.callback_query(F.data == 'add_task')
async def process_add_task(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Добавить, перевод в состояние ожидания ввода Задачи"""
    logging.info('process_add_task')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass

    await state.set_state(TaskFSM.state_add_task)
    # keyboard = kb.keyboards_main_menu()

    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
    dict_kb = {'Назад': 'go_to_process_task'}
    keyboard = kb.create_in_kb(1, **dict_kb)

    await clb.message.edit_text(text='Пришлите наименование новой задачи', reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data == 'go_to_process_task')
async def go_to_process_task(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Назад в process_add_task, Запуск функции process_task"""
    logging.info('go_to_process_task')
    await state.set_state(state=None)# сбрасываем состояние
    await process_task(message=clb.message, bot=bot)
    await clb.answer()



@router.message(StateFilter(TaskFSM.state_add_task), F.text)
async def process_add_task_input_data(message: Message, state: FSMContext, bot: Bot) -> None:
    """Ввод и запись в state названия Задачи"""
    logging.info(f'process_add_task_input_date: {message.chat.id} ----- message.text = {message.text}')

    if 'Пришлите дедлайн для задачи' not in message.text: # так происходит, когда приходим с кнопки назад, там этот текст в колбэке
        title_new_task = message.text
        await state.update_data({'title_new_task': title_new_task})
    else:
        title_new_task = (await state.get_data())['title_new_task']

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-i)
    #     except:
    #         pass
    keyboard = kb.keyboards_main_menu()

    await message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)

    dict_kb = {'Записать как заметку': 'write_as_mark', 'Назад': 'go_to_process_add_task'}
    keyboard = kb.create_in_kb(1, **dict_kb)
    await message.answer(text=f'Пришлите дедлайн для задачи <b>"{title_new_task}"</b>. Формат записи: чч:мм дд.мм.гггг', reply_markup=keyboard)
    await state.set_state(TaskFSM.state_add_deadline)




@router.callback_query(F.data == 'go_to_process_add_task')
async def go_to_process_add_task(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Назад в process_add_task_input_data, Запуск функции process_add_task"""
    logging.info('go_to_process_add_task')
    await state.clear()
    await clb.answer()

    await process_add_task(clb=clb, state=state, bot=bot)



@router.message(StateFilter(TaskFSM.state_add_deadline))#, F.text)
async def process_add_task_deadline(message: Message, state: FSMContext, bot: Bot) -> None:
    """Ввод и запись в state дэдлайна Задачи"""
    logging.info(f'process_add_task_deadline: {message.chat.id} ----- message.text = {message.text}')

    dict_state = await state.get_data()
    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-i)
    #     except:
    #         pass
    if validate_date(message.text): # проверка на правильность формы записи
        if validate_overdue(message.text):
            await state.update_data({'title_new_task_deadline': message.text})

            # для связи с таблицей Event  записать id задачи из таблицы Current_event
            id_event = await rq.get_current_event_id()
            dict_task = {'tg_id': message.chat.id, 'title_task': dict_state['title_new_task'], 'id_event': id_event, 'deadline_task': message.text, }
            await rq.add_task(dict_task)

            keyboard = kb.keyboards_main_menu()
            await message.answer(text=f'Задача {dict_state["title_new_task"]} успешно добавлена',
                                 reply_markup=keyboard)
            await state.clear()
            await process_task(message=message, bot=bot)

        else: # если введенная дата просрочена
            logging.info('ПРОСРОЧКА')

            dict_kb = {'Назад': 'go_to_process_add_task_input_data'}
            keyboard = kb.create_in_kb(1, **dict_kb)
            await message.answer(text=f'Введенные дата и время остались в прошлом. Повторите ввод.'
                                      f' Пришлите дедлайн для задачи {dict_state["title_new_task"]}.'
                                      f' Формат записи: чч:мм дд.мм.гггг',
                                 reply_markup=keyboard)
            return

    else: # если дата не прошла валидацию форматта ввода
        logging.info('НЕ ПРОШЛА ВАЛИДАЦИЮ')

        dict_kb = {'Назад': 'go_to_process_add_task_input_data'}
        keyboard = kb.create_in_kb(1, **dict_kb)
        await message.answer(text=f'Некорректно указан дедлайн. Пришлите дедлайн для задачи'
                                  f' {dict_state["title_new_task"]}. Формат записи: чч:мм дд.мм.гггг',
                             reply_markup=keyboard)



@router.callback_query(F.data == 'write_as_mark')
async def process_write_as_mark(clb: CallbackQuery, bot: Bot, state: FSMContext):
    logging.info('process_write_as_mark')

    #await hf.process_del_message_clb(1, bot, clb)
    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass
    dict_state = await state.get_data()
    # для связи с таблицей Event  записать id задачи из таблицы Current_event
    id_event = await rq.get_current_event_id()
    dict_task = {'tg_id': clb.message.chat.id, 'title_task': dict_state['title_new_task'], 'id_event': id_event, 'status_task': 'note'}
    await rq.add_task(dict_task)
    keyboard = kb.keyboards_main_menu()
    await clb.message.answer(text=f'Задача записана как заметка', reply_markup=keyboard)
    await state.clear()
    await process_task(message=clb.message, bot=bot)
    await clb.answer()


#При выводе задач/заметок помечаем их:
            #✅ - выполненная задача
            #❌ - задача просрочена, время дедлайна прошло
            #🛠 - задача находится в работе
            #📝 - заметка

@router.callback_query(F.data == 'go_to_process_add_task_input_data')
async def go_to_process_add_task_input_data(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Назад в process_add_task_deadline, Запуск функции process_add_task_input_data"""
    logging.info('go_to_process_add_task_input_data')
    #await state.clear()
    #await state.set_state(TaskFSM.state_add_task)
    await process_add_task_input_data(message=clb.message, state=state, bot=bot)
    await clb.answer()



async def process_scheduler_send_task(bot: Bot):

    logging.info('process_scheduler_send_task')

    data_task = await rq.get_tasks()
    #current_day = date.today().strftime('%d-%m-%Y')
    time_now = datetime.now()

    #date_format = '%d-%m-%Y'  #'%Y.%m.%d %H:%M:%S.%f'    Формат записи: чч:мм дд.мм.гггг',
    list_tasks: list = []
    for task in data_task:
        if task.deadline_task != 'note' and task.status_task == 'active':
            time_, date_ = task.deadline_task.split(' ')
            hour, minutes = time_.split(':')
            day, month, year = date_.split('.')
            format_str_date_time = f'{year}.{month}.{day} {hour}:{minutes}:00.00'
            date_time = datetime.strptime(format_str_date_time, '%Y.%m.%d %H:%M:%S.%f')
            delta_deadline = date_time - time_now
            await asyncio.sleep(1)
            #if 82800 < delta_deadline.seconds <= 86400:
            #if 86360 < delta_deadline.seconds <= 86400:
            if delta_deadline.days<1 and delta_deadline.seconds>86360:
                logging.info(f'{date_time} - {time_now} = {date_time - time_now} {delta_deadline.seconds}')
                await bot.send_message(
                        chat_id=task.tg_id,
                        text=f'До назначенного вами срока выполнения задачи <b>"{task.title_task}"</b>, '
                        f'мероприятия <b>"{await rq.get_event_by_id(task.id_event)}"</b> остались одни сутки.'
                )
                # logging.info(f'{date_time} - {time_now} = {date_time - time_now} {delta_deadline.seconds}')