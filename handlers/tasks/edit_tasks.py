from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta
from handlers.tasks.add_tasks import process_task

import keyboards.keyboards as kb

from filters.admin_filter import check_super_admin
from database.models import User
import database.requests as rq
import database.help_function as hf
from datetime import time, date, datetime, timedelta
from filters.admin_filter import IsSuperAdmin
from filters.filters import validate_date, validate_overdue



router = Router()

storage = MemoryStorage()

import logging
import asyncio


class EditTaskFSM(StatesGroup):
    state_edit_title_task = State()
    state_edit_deadline = State()



@router.callback_query(F.data == 'my_tasks')
async def process_my_tasks(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Мои задачи. Показать Задачи"""
    logging.info('process_my_tasks')

    await state.clear()

    id_event = await rq.get_current_event_id()
    title_event = await rq.get_current_event()
    list_tasks: list = []
    dict_status: dict = {'active': '🛠', 'complete': '✅', 'overdue': '❌', 'note': '📝',}

    # Запускаю функцию проверки просроченности задач, в активных задачах с просроченным временем ставлю статус overdue
    await hf.check_status_task()

    for task in await rq.get_tasks(): # какие есть мероприятия в таблице Event, если она пустая, то перевод в режим ожидания ввода названия
        if id_event == task.id_event and task.status_task!='location' and task.status_task!='performer' and task.tg_id == clb.message.chat.id: # если эта Задача принадлежит нужному Мероприятию

            text_button = f'{task.title_task} {dict_status[task.status_task]}'
            callback = f'do_task!{task.id}!{task.title_task}!{task.status_task}!{task.id_event}'
            #dict_events[key] = value
            list_tasks.append([text_button, callback])
    logging.info(f'list_tasks = {list_tasks}')

    # keyboard = kb.keyboards_main_menu()
    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{title_event}"</b>:', reply_markup=keyboard)

    if not list_tasks: # если пусто в таблце Task
        await clb.message.edit_text(text=f'Для мероприятия <b>"{title_event}"</b> задачи не созданы.')
    else: # если в таблице Event есть строки вывожу на кнопки
        keyboard = kb.create_kb_pagination(
            list_button=list_tasks,
            back=0,
            forward=2,
            count=5,
            prefix='task',
            button_go_away='go_to_process_task',
        )
        await clb.message.edit_text(text='В этом разделе вы можете просмотреть, отредактировать или удалить созданные задачи и заметки', reply_markup=keyboard)
    await clb.answer()




# >>>>
@router.callback_query(F.data.startswith('button_forward!task'))
async def process_forward_task(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_forward_task: {clb.message.chat.id} ----- clb.data = {clb.data}')

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')

    id_event = await rq.get_current_event_id()
    title_event = await rq.get_current_event()
    list_tasks: list = []
    dict_status: dict = {'active': '🛠', 'complete': '✅', 'overdue': '❌', 'note': '📝',}

    # Запускаю функцию проверки просроченности задач, в активных задачах с просроченным временем ставлю статус overdue
    await hf.check_status_task()

    for task in await rq.get_tasks(): # какие есть мероприятия в таблице Event, если она пустая, то перевод в режим ожидания ввода названия
        if id_event == task.id_event and task.status_task!='location' and task.status_task!='performer' and task.tg_id == clb.message.chat.id: # если эта Задача принадлежит нужному Мероприятию

            text_button = f'{task.title_task} {dict_status[task.status_task]}'
            callback = f'do_task!{task.id}!{task.title_task}!{task.status_task}!{task.id_event}'
            #dict_events[key] = value
            list_tasks.append([text_button, callback])
    logging.info(f'list_tasks = {list_tasks}')


    keyboard = kb.create_kb_pagination(
                    list_button=list_tasks,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='task',
                    button_go_away='go_to_process_task',
                )
    #logging.info(f'keyboard = {keyboard}')
    #await asyncio.sleep(7)

    try:
        await clb.message.edit_text(text='В этом разделе вы можете просмотреть, отредактировать или удалить созданные задачи и заметки', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='В этом разделe вы можете просмотреть, отредактировать или удалить созданные задачи и заметки', reply_markup=keyboard)
    await clb.answer()


# <<<<
@router.callback_query(F.data.startswith('button_back!task'))
async def process_back_choice_performer(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_back_choice_performer: {clb.message.chat.id} ----- clb.data = {clb.data}')

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    id_event = await rq.get_current_event_id()
    title_event = await rq.get_current_event()
    list_tasks: list = []
    dict_status: dict = {'active': '🛠', 'complete': '✅', 'overdue': '❌', 'note': '📝',}

    # Запускаю функцию проверки просроченности задач, в активных задачах с просроченным временем ставлю статус overdue
    await hf.check_status_task()

    for task in await rq.get_tasks(): # какие есть мероприятия в таблице Event, если она пустая, то перевод в режим ожидания ввода названия
        if id_event == task.id_event and task.status_task!='location' and task.status_task!='performer' and task.tg_id == clb.message.chat.id: # если эта Задача принадлежит нужному Мероприятию

            text_button = f'{task.title_task} {dict_status[task.status_task]}'
            callback = f'do_task!{task.id}!{task.title_task}!{task.status_task}!{task.id_event}'
            #dict_events[key] = value
            list_tasks.append([text_button, callback])
    logging.info(f'list_tasks = {list_tasks}')



    keyboard = kb.create_kb_pagination(
                    list_button=list_tasks,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='task',
                    button_go_away='go_to_process_task',
                )
   # logging.info(f'keyboard = {keyboard}')
    try:
        await clb.message.edit_text(text='В этом разделе вы можетe просмотреть, отредактировать или удалить созданные задачи и заметки', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='В этом разделe вы можете просмотреть, отредактировать или удaлить созданные задачи и заметки', reply_markup=keyboard)
    await clb.answer()




@router.callback_query(F.data.startswith('do_task'))
async def process_do_task(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку конкретной задачи. Что делаем с Задачей"""
    logging.info(f'process_do_task --- callback.data = {clb.data}') # callback = f'do_task!{task.id}!{task.title_task}!{task.status_task}!{task.id_event}'

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass

    id_task = clb.data.split('!')[-4]
    title_task = clb.data.split('!')[-3]
    status_task = clb.data.split('!')[-2]
    id_event = clb.data.split('!')[-1]
    await state.clear()
    await state.update_data({'id_task': id_task, 'status_task': status_task, 'id_event': id_event})

    title_event = await rq.get_current_event()

    # keyboard = kb.keyboards_main_menu()
    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{title_event}"</b>:', reply_markup=keyboard)

    note_task = 'заметкой' if status_task == 'note' else 'задачей'
    if status_task in ['active', 'overdue']:
        kb_dict = {'Редактировать ✏️': f'edit_tast!{id_task}!{title_task}!{status_task}!{id_event}',
                'Удалить ❌': f'delete_tast!{id_task}!{title_task}!{status_task}!{id_event}',
                'Отметить как выполненную':f'mark_as_complete!{id_task}!{title_task}!{status_task}!{id_event}',
                'Назад': 'go_to_process_my_tasks'}
        keyboard=kb.create_in_kb(1, **kb_dict)
    else:
        kb_dict = {'Редактировать ✏️': f'edit_tast!{id_task}!{title_task}!{status_task}!{id_event}',
                'Удалить ❌': f'delete_tast!{id_task}!{title_task}!{status_task}!{id_event}',
                'Назад': 'go_to_process_my_tasks'}
        keyboard=kb.create_in_kb(2, **kb_dict)
    await clb.message.edit_text(text=f'Что необходимо сделать с {note_task} <b>"{title_task}"</b>:', reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data == 'go_to_process_my_tasks')
async def go_to_process_my_tasks(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Назад в process_do_task, Запуск функции process_my_tasks"""
    logging.info('go_to_process_my_tasks')

    await process_my_tasks(clb=clb, state=state, bot=bot)
    await clb.answer()



@router.callback_query(F.data.startswith('edit_tast'))
async def process_edit_task(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Редактировать. Что делаем дальше"""
    try:
        logging.info(f'process_edit_task --- clb.data = {clb.data}') # callback = f'edit_tast!{id_task}!{title_task}!{status_task}!{id_event}'
    except:
        logging.info(f'process_edit_task --- clb.data =')

    # получил новое название задачи или деадлайна - сбрасывай состояние
    await state.set_state(state=None)

    dict_data_state = await state.get_data()
    if 'new_title_task' in list(dict_data_state)  or 'new_deadline' in list(dict_data_state): # работаем с message а не clb
        id_task = dict_data_state['id_task']
        status_task = dict_data_state['status_task']
        id_event = dict_data_state['id_event']
        title_event = await rq.get_current_event()

        title_task = dict_data_state['new_title_task'] if 'new_title_task' in list(dict_data_state) else (await rq.get_task_by_id(id_task=id_task)).title_task
        deadline = dict_data_state['new_deadline'] if 'new_deadline' in list(dict_data_state) else (await rq.get_task_by_id(id_task=id_task)).deadline_task

    else:
        id_task = clb.data.split('!')[-4]
        title_task = clb.data.split('!')[-3]
        status_task = clb.data.split('!')[-2]
        id_event = clb.data.split('!')[-1]
        title_event = await rq.get_current_event()
        deadline = (await rq.get_task_by_id(id_task=id_task)).deadline_task

    note_task = 'заметки' if status_task == 'note' else 'задачи'
    if status_task != 'note': # Если это задача, то можно поменять и дедлайн
        kb_dict = {f'Название "{title_task}"': f'edit_title_task!{id_task}!{title_task}!{status_task}!{id_event}',
                f'Deadline {deadline}': f'edit_deadline_task!{id_task}!{title_task}!{status_task}!{id_event}',
                'Подтвердить':f'confirm_task',
                'Назад': f'do_task!{id_task}!{title_task}!{status_task}!{id_event}'}

    else:
        kb_dict = {f'Название "{title_task}"': f'edit_title_task?{id_task}!{title_task}!{status_task}!{id_event}',
                'Подтвердить':f'confirm_task',
                'Назад': f'do_task!{id_task}!{title_task}!{status_task}!{id_event}'}

    keyboard_reply = kb.keyboards_main_menu()
    keyboard=kb.create_in_kb(1, **kb_dict)

    if 'new_title_task' in list(dict_data_state)  or 'new_deadline' in list(dict_data_state): # работаем с message а не clb:
        #await hf.process_del_message_messsage(3, bot, message=clb)
        await clb.answer(text=f'Вы работаете с мероприятием <b>"{title_event}"</b>:', reply_markup=keyboard_reply) # тут clb это message прри вызове другой функции
        await clb.answer(text=f'Какое поле для {note_task} <b>"{title_task}"</b> необходимо изменить?', reply_markup=keyboard)
    else:
        #await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{title_event}"</b>:', reply_markup=keyboard_reply)
        await clb.message.edit_text(text=f'Какое поле для {note_task} <b>"{title_task}"</b> необходимо изменить?', reply_markup=keyboard)
        await clb.answer()


@router.callback_query(F.data.startswith('edit_title_task'))
@router.callback_query(F.data.startswith('edit_deadline_task'))
async def process_edit_title_deadline_task(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Название или Deadline в разделе Редактировать Задачу, перевод в состояние ожидания ввода нового имени Задачи"""
    logging.info(f'process_edit_title_deadline_task --- clb.data = {clb.data}')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass


    # keyboard = kb.keyboards_main_menu()
    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
    callback_data = clb.data.split('?')[-1] # пристёгиваем к кнопке назад информационную часть колбэка
    dict_kb = {'Назад': f'edit_tast!{callback_data}'}
    keyboard = kb.create_in_kb(1, **dict_kb)

    title_task = clb.data.split('!')[-3]
    if 'edit_title_task' in clb.data:
        await state.set_state(EditTaskFSM.state_edit_title_task)
        await clb.message.edit_text(text='Пришлите наименование новой задачи', reply_markup=keyboard)
        await clb.answer()
    elif 'edit_deadline_task' in clb.data:
        await state.set_state(EditTaskFSM.state_edit_deadline)
        await clb.message.edit_text(text=f'Пришлите дедлайн для задачи <b>"{title_task}"</b>. Формат записи: чч:мм дд.мм.гггг', reply_markup=keyboard)
        await clb.answer()


@router.message(StateFilter(EditTaskFSM.state_edit_title_task))
async def process_edit_title_task_input_text(message: Message, state: FSMContext, bot: Bot) -> None:
    """Ввод и запись в state нового названия Задачи"""
    logging.info(f'process_edit_title_task_input_text: {message.chat.id} ----- message.text = {message.text}')
    new_title_task = message.text
    await state.update_data({'new_title_task': new_title_task})
    await process_edit_task(clb = message, state = state, bot=bot)


@router.message(StateFilter(EditTaskFSM.state_edit_deadline))
async def process_edit_deadline_task_input_text(message: Message, state: FSMContext, bot: Bot) -> None:
    """Ввод и запись в state нового deadline Задачи"""
    logging.info(f'process_edit_deadline_task_input_text: {message.chat.id} ----- message.text = {message.text}')

    dict_data_state = await state.get_data()
    new_dedline = message.text
    id_task = dict_data_state['id_task']
    dict_data_state = await state.get_data()
    title_task = dict_data_state['new_title_task'] if 'new_title_task' in list(dict_data_state) else (await rq.get_task_by_id(id_task=id_task)).title_task
    status_task = (await rq.get_task_by_id(id_task=id_task)).status_task
    id_event = (await rq.get_task_by_id(id_task=id_task)).id_event

    #await hf.process_del_message_messsage(2, bot, message)
    if validate_date(new_dedline): # проверка на правильность формы записи
        if validate_overdue(new_dedline):
            await state.update_data({'new_deadline': new_dedline})
            await process_edit_task(clb = message, state = state, bot=bot)

        else: # если введенная дата просрочена
            logging.info('ПРОСРОЧКА')
            dict_kb = {'Назад': f'edit_tast!{id_task}!{title_task}!{status_task}!{id_event}'},   #'go_to_process_edit_task'} # f'edit_tast!{id_task}!{title_task}!{status_task}!{id_event}',
            keyboard = kb.create_in_kb(1, **dict_kb)
            await message.answer(text=f'Введенные дата и время остались в прошлом. Повторите ввод. Пришлите дедлайн для задачи {title_task}. Формат записи: чч:мм дд.мм.гггг', reply_markup=keyboard)
            return

    else: # если дата не прошла валидацию форматта ввода
        logging.info('НЕ ПРОШЛА ВАЛИДАЦИЮ')
        dict_kb = {'Назад': f'edit_tast!{id_task}!{title_task}!{status_task}!{id_event}'}     #'go_to_process_edit_task'}gggg
        keyboard = kb.create_in_kb(1, **dict_kb)
        await message.answer(text=f'Некорректно указан дедлайн. Пришлите дедлайн для задачи {title_task}. Формат записи: чч:мм дд.мм.гггг', reply_markup=keyboard)


@router.callback_query(F.data == 'go_to_process_edit_task')
async def go_to_process_edit_tasks(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Назад в process_edit_deadline_task_input_text, Запуск функции process_edit_task"""
    logging.info('go_to_process_edit_task')

    await process_edit_task(clb=clb, state=state, bot=bot)
    await clb.answer()


@router.callback_query(F.data.startswith('delete_tast'))
async def process_delete_tast(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Удалить разделе Редактировать Задачу"""
    logging.info('process_delete_tast')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass

    title_task = clb.data.split('!')[-3]
    id_task = clb.data.split('!')[-4]
    await rq.delete_task(id_task=id_task)
    keyboard = kb.keyboards_main_menu()
    await clb.message.answer(text=f'Задача <b>"{title_task}"</b> успешно удалена.', reply_markup=keyboard)
    await process_task(clb.message, bot)
    await clb.answer()



@router.callback_query(F.data.startswith('confirm_task'))
async def process_confirm_edit_task(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Подтвердить."""
    logging.info(f'process_confirm_edit_task ---')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass
    #     try:
    #         await bot.delete_message(chat_id=clb.chat.id, message_id=clb.message_id-i) # clb это message
    #     except:
    #         pass

    dict_data_state = await state.get_data()
    id_task = dict_data_state['id_task']
    if 'new_title_task' in list(dict_data_state):
        title_task = dict_data_state['new_title_task']
        await rq.set_task(id_task=id_task, title_task=title_task)
    else:
        title_task = (await rq.get_task_by_id(id_task)).title_task
    if 'deadline_task' in list(dict_data_state):
        deadline_task = dict_data_state['deadline_task']
        await rq.set_task(id_task=id_task, deadline_task=deadline_task)
    keyboard = kb.keyboards_main_menu()
    await clb.message.answer(text=f'Задача <b>"{title_task}"</b> успешно обновлена.', reply_markup=keyboard)
    await clb.answer()
    await process_task(clb.message, bot)


    #сделать отметить задачу как выполненной
    #'Отметить как выполненную':f'mark_as_complete!{id_task}!{title_task}!{status_task}!{id_event}
@router.callback_query(F.data.startswith('mark_as_complete'))
async def process_mark_as_complete(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Отметить задачу как выполненную."""
    logging.info(f'process_mark_as_complete ---')

    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass
    id_task = clb.data.split('!')[-4]
    await rq.set_task(id_task=id_task, status_task='complete')
    await clb.answer()
    await process_my_tasks(clb=clb, state=state, bot= Bot)
    # await process_do_task(clb=clb, state=state, bot= Bot)
