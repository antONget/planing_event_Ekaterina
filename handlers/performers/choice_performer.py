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
class AddPerformersFSM(StatesGroup):
    state_add_name_performer = State()
    state_add_photo_performer = State()
    state_after_add_performer = State()

# class PeriodExpenseFSM(StatesGroup):
#     state_start_perid_expense = State()
#     state_finish_period_expense = State()
###    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')

@router.message(F.text == 'Исполнители 🙋', IsSuperAdmin())
async def process_performers(message: Message, bot: Bot):
    logging.info('process_performers')
    #await hf.process_del_message_messsage(3, bot, message)

    keyboard = kb.keyboards_main_menu()
    await message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)

    dict_kb = {'Выбрать исполнителя': 'choice_performer', 'Изменить список': 'edit_performer'}
    keyboard = kb.create_in_kb(2, **dict_kb)
    await message.answer(text='Выберите действия для исполнителя.', reply_markup=keyboard)


@router.callback_query(F.data == 'choice_performer')
async def process_choise_category_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Выбрать исполнителя"""
    logging.info('process_choise_category_performer')


    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass

    # keyboard = kb.keyboards_main_menu()
    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
    dict_kb = {
        'Ведущий': 'category_performer!host',
        'Фотограф': 'category_performer!photograf',
        'Декоратор': 'category_performer!decorator',
        'Видеограф': 'category_performer!videograf',
        'Кейтеринг': 'category_performer!catering',
        'Диджей': 'category_performer!dj',
        'Назад': 'back_to_process_performers', # сделать отдельной функцией
        }
    keyboard = kb.create_in_kb(1, **dict_kb)
    await clb.message.edit_text(text=f'Какого исполнителя вы хотите выбрать?', reply_markup=keyboard)
    await clb.answer()



@router.callback_query(F.data.startswith('category_performer!'))
async def process_choise_name_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Категории исполнителя"""
    logging.info(f'process_choise_name_performer --- clb.data = {clb.data}')

    category = clb.data.split('!')[-1]
    await state.update_data(category = category)
    list_performers: list = []
    for performer in await rq.get_performers():
        if performer.category_performer == category:
            list_ = [performer.name_performer, f'name_performer!{performer.id}']
            list_performers.append(list_)
    logging.info(f'list_performers = {list_performers}')

    keyboard = kb.create_kb_pagination(
            list_button=list_performers,
            back=0,
            forward=2,
            count=5,
            prefix='choice_performer', # это для колбэка кнопок <<< и >>>
            button_go_away='choice_performer'
        )
    try:
        await clb.message.edit_text(text='Какого исполнителя вы хотите выбрать?', reply_markup=keyboard)
    except:
        #await hf.process_del_message_clb(1, bot, clb)
        await clb.message.answer(text='Какого исполнителя вы хотите выбрать?', reply_markup=keyboard)
    await clb.answer()

# >>>>
@router.callback_query(F.data.startswith('button_forward!choice_performer'))
async def process_forward_choice_performer(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_forward_choice_performer: {clb.message.chat.id} ----- clb.data = {clb.data}')

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')

    category = (await state.get_data())['category']

    list_performers: list = []
    for performer in await rq.get_performers():
        if performer.category_performer == category:
            list_ = [performer.name_performer, f'name_performer!{performer.id}']
            list_performers.append(list_)
    logging.info(f'list_performers = {list_performers}')

    keyboard = kb.create_kb_pagination(
                    list_button=list_performers,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='choice_performer',
                    button_go_away='choice_performer'
                )
    #logging.info(f'keyboard = {keyboard}')
    #await asyncio.sleep(7)

    try:
        await clb.message.edit_text(text='Какого испoлнителя вы хотите выбрать?', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Какого исполнитeля вы хотите выбрать?', reply_markup=keyboard)
    await clb.answer()


# <<<<
@router.callback_query(F.data.startswith('button_back!choice_performer'))
async def process_back_choice_performer(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_back_choice_performer: {clb.message.chat.id} ----- clb.data = {clb.data}')

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    category = (await state.get_data())['category']

    list_performers: list = []
    for performer in await rq.get_performers():
        if performer.category_performer == category:
            list_ = [performer.name_performer, f'name_performer!{performer.id}']
            list_performers.append(list_)
    logging.info(f'list_performers = {list_performers}')
    keyboard = kb.create_kb_pagination(
                    list_button=list_performers,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='choice_performer',
                    button_go_away='choice_performer'
                )
   # logging.info(f'keyboard = {keyboard}')
    try:
        await clb.message.edit_text(text='Какого исполнителя вы хотитe выбрать?', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Какого исполнителя вы хотите выбpать?', reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data.startswith('name_performer!'))  #  list_ = [performer.name_performer, f'name_performer!{performer.id}']
async def process_show_card_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем карточку исполнителя"""
    logging.info(f'process_show_card_performer --- clb.data = {clb.data}')

    #await hf.process_del_message_clb(1, bot, clb)





    # await clb.message.answer(
    #     text=


    id_performer = clb.data.split('!')[-1]
    data_ = await rq.get_performer_by_id(id_performer)
    # У всех есть посмотреть отзывы кнопка "Отзывы"
    # У фотографа, декоратора есть еще кнопка "Примеры работ"
    if data_.category_performer in ['photograf', 'decorator', 'catering']:
        keyboard = kb.create_in_kb(1, **{'Посмотреть профиль': f'show_profile_performer!{data_.id}',
                                         'Отзывы': f'show_feedback_performer!{data_.id}',
                                         'Примеры работ': f'show_examples_work_performer!{data_.id}',
                                         f'Выбрать исполнителя {data_.name_performer}': f'choice_performer_set_to_task!{data_.id}',  # Выбрать этот лофт/ресторан/фотографа и др.
                                         'Назад': f'category_performer!{data_.category_performer}'})
    elif data_.category_performer in ['host', 'videograf',  'dj']:
        keyboard = kb.create_in_kb(1, **{'Посмотреть профиль': f'show_profile_performer!{data_.id}',
                                         'Отзывы': f'show_feedback_performer!{data_.id}',
                                         f'Выбрать исполнителя {data_.name_performer}': f'choice_performer_set_to_task!{data_.id}',  # Выбрать этот лофт/ресторан/фотографа и др.
                                         'Назад': f'category_performer!{data_.category_performer}'})

    # media_group = []
    # for photo in data_.photo_performer.split(','):
    #     media_group.append(InputMediaPhoto(media=photo))
    # if media_group:
    #     # отправляем медиагруппу
    #     logging.info(f'media_group')
    #     await clb.message.answer_media_group(media=media_group)

    await clb.message.answer_photo(
        photo=data_.photo_performer,
        caption=
        f'{data_.name_performer} {data_.description_performer}\n'
        f'⭐️ <b>Рейтинг:</b> {data_.reiting_performer}\n'
        f'💶 <b>Стоимость:</b> {data_.cost_performer}\n'
        f'📞 <b>Телефон для связи:</b> {data_.phone_performer}\n',
        reply_markup=keyboard
    )


    # await clb.message.answer(
    #     text=
    #     f'{data_.name_performer} {data_.description_performer}\n'
    #     f'<b>Рейтинг:</b> {data_.reiting_performer}\n'
    #     f'<b>Стоимость:</b> {data_.cost_performer} руб/час\n'
    #     f'<b>Телефон для связи:</b> {data_.phone_performer}\n',
    #     reply_markup=keyboard
    # )
    await clb.answer()


@router.callback_query(F.data.startswith('show_profile_performer!'))  #  {'Посмотреть профиль': f'show_profile_performer!{data_.id}'
async def process_show_profile_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем ссылку на профиль исполнителя"""
    logging.info(f'process_show_profile_performer --- clb.data = {clb.data}')
    #await hf.process_del_message_clb(1, bot, clb)
    data_ = await rq.get_performer_by_id(clb.data.split('!')[-1])
    keyboard = kb.create_in_kb(1, **{'Назад': f'name_performer!{data_.id}'})
    await clb.message.answer(text=f'{data_.name_performer}\n{data_.profile_performer}', reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data.startswith('show_feedback_performer!'))  #  'Отзывы': f'show_feedback_performer!{data_.id}',
async def process_show_feedback_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем отзывы на исполнителя"""
    logging.info(f'process_show_feedback_performer --- clb.data = {clb.data}')
    #await hf.process_del_message_clb(1, bot, clb)
    id_performer = int(clb.data.split('!')[-1])
    # data_performer = await rq.get_performer_by_id(id_performer)
    keyboard = kb.create_in_kb(1, **{'Назад': f'name_performer!{id_performer}'})
    feedback: str = ''
    for data_ in await rq.get_feedbacks():
        if data_.id_performer == id_performer and not data_.feedback.startswith('!_?_!'):
            feedback += f'{data_.feedback}\n\n'
    if feedback == '':
        await clb.message.answer(text='Отзывов об исполнителе пока нет.', reply_markup=keyboard)
        await clb.answer()
        return
    await clb.message.answer(text=feedback, reply_markup=keyboard)
    await clb.answer()

@router.callback_query(F.data.startswith('show_examples_work_performer!'))  #  'Примеры работ': f'show_examples_work_performer!{data_.id}',
async def process_show_examples_work_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем примеры работ исполнителя"""
    logging.info(f'process_show_examples_work_performer --- clb.data = {clb.data}')
    #await hf.process_del_message_clb(1, bot, clb)
    id_performer = int(clb.data.split('!')[-1])
    keyboard = kb.create_in_kb(1, **{'Назад': f'name_performer!{id_performer}'})
    media_group = []
    for data_ in await rq.get_feedbacks():
        if data_.id_performer == id_performer and data_.feedback.startswith('!_?_!'):
            photos = data_.feedback.split('!_?_!')[1]


            for photo in photos.split(','):
                media_group.append(InputMediaPhoto(media=photo))
                logging.info(photo)
                logging.info(media_group)
    if media_group:
        # отправляем медиагруппу
        logging.info(f'media_group')
        await clb.message.answer(text='Примеры работ:')#, reply_markup=keyboard)
        await clb.message.answer_media_group(media=media_group)

        await clb.answer()

    else:
        await clb.message.answer(text='Примеров работ исполнителя пока нет. Их можно добавить в режире редактирования', reply_markup=keyboard)
        await clb.answer()
        return

    await clb.message.answer(text='Вернуться к карточке исполнителя', reply_markup=keyboard)
    await clb.answer()



@router.callback_query(F.data.startswith('choice_performer_set_to_task!'))  #  f'Выбрать локацию {data_.name_performer}': f'choice_performer_set_to_task!{data_.id}',
async def process_choice_performer_set_to_task(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """В таблицу Task устанавливаем эту локацию с пометкой 'performer' в графе status_task"""
    logging.info(f'process_choice_performer_set_to_task --- clb.data = {clb.data}')
    #await hf.process_del_message_clb(1, bot, clb)
    id_performer = int(clb.data.split('!')[-1])
    id_event = await rq.get_current_event_id()
    data_ = await rq.get_performer_by_id(id_performer)
    # создаем словарь и добавляем его в таблицу Task
    dict_task = {'tg_id': clb.message.chat.id, 'title_task': data_.name_performer, 'id_event': id_event, 'deadline_task': 'note', 'status_task': 'performer'}
    logging.info(dict_task)
    # можно или добавить эту локацию, если ее не было или заменить
    check_task_performer = 0 # проверка на наличие такого исполнителя в БД, чтобы 2 раза не добавлять
    for task in await rq.get_tasks():
        if task.status_task == 'performer' and id_event == task.id_event and data_.name_performer == task.title_task:
            check_task_performer = task.id
    if not check_task_performer:
        await rq.add_task(dict_task)
    keyboard = kb.create_in_kb(1, **{'Назад': f'name_performer!{id_performer}'})
    await clb.message.answer(text=f'Вы выбрали исполнителя {data_.name_performer} для мероприятия {await rq.get_current_event()}', reply_markup=keyboard)
    await clb.answer()




@router.callback_query(F.data == 'back_to_process_performers')
async def process_go_to_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку НАЗАД в исполнителяя"""
    logging.info(f'process_go_to_performer --- clb.data = {clb.data}')
    #await hf.process_del_message_clb(3, bot, clb)
    if clb.data == 'back_to_process_performers':
        await process_performers(clb.message, bot)
