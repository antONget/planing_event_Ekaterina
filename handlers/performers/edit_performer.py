from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta
import aiogram_calendar
from handlers.performers.choice_performer import AddPerformersFSM
import filters.filters as flt
from handlers.performers.choice_performer import process_performers


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


# class AddPerformersFSM(StatesGroup):
#     state_add_name_performer = State()
#     state_add_photo_performer = State()
###    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')

class EditPerformer(StatesGroup):
    state_edit_name = State()
    state_edit_description = State()
    state_edit_reiting = State()
    state_edit_cost = State()
    state_edit_phone = State()
    state_edit_profile = State()
    state_edit_photo = State()
    state_edit_feedback = State()
    state_edit_examples_work= State()


@router.callback_query(F.data == 'edit_performer') # 'Изменить список': 'edit_performer'}
async def process_edit_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Выбрать исполнителя"""
    await state.clear()
    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')
    logging.info('process_edit_performer')

    dict_kb = {
        'Редактировать': 'start_edit_performer',
        'Удалить': 'delete_performer',
        'Добавить': 'add_performer',
        }
    keyboard = kb.create_in_kb(2, **dict_kb)
    await clb.message.edit_text(text=f'Выберите действия для исполнителя.', reply_markup=keyboard)
    await clb.answer()



@router.callback_query(F.data == 'start_edit_performer')
@router.callback_query(F.data == 'delete_performer')
@router.callback_query(F.data == 'add_performer')
async def process_start_edit_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Категории исполнителя"""
    logging.info(f'process_start_edit_performer --- clb.data = {clb.data}')
    # также можно прийти сюда после удаления
    action = ''
    if clb.data == 'start_edit_performer':
        action = 'next_edit_performer'
    elif clb.data == 'delete_performer':
        action = 'next_delete_performer'
    elif clb.data == 'add_performer':
        action = 'next_add_performer' # Это в отдельный хэндлер и там переводить в режим ожидания ввода от пользователя данных
    # добавить в состояние action, т.к. в эту функцию прихожу и без колбэка,
    # делать проверку на наличие action
    if action: # записываю в FSM
        await state.update_data(action_from_state = action)
    else:
        action = (await state.get_data())['action_from_state']


    dict_kb = {
        'Ведущий': f'{action}!host',
        'Фотограф': f'{action}!photograf',
        'Декоратор': f'{action}!decorator',
        'Видеограф': f'{action}!videograf',
        'Кейтеринг': f'{action}!catering',
        'Диджей': f'{action}!dj',
        'Назад': 'edit_performer',
        }
    keyboard = kb.create_in_kb(1, **dict_kb)
    await clb.message.edit_text(text=f'Какого исполнителя вы хотите выбрать?', reply_markup=keyboard)
    await clb.answer()



@router.callback_query(F.data.startswith('next_edit_performer'))
@router.callback_query(F.data.startswith('next_delete_performer'))
async def process_next_add_performer_show_name(clb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Выводим Имени И Фамилии исплнителей для дальнейших действий"""
    logging.info(f'process_next_add_performer_show_name: {clb.message.chat.id} ----- clb.data = {clb.data}')

    if clb.data.startswith('next_edit_performer'):
        button_back = 'start_edit_performer'
        action = 'edit'
    elif clb.data.startswith('next_delete_performer'):
        button_back = 'delete_performer'
        action = 'delete'

    category = clb.data.split('!')[-1]
    #  сохраняем в состоянии инфу для пагинации: категорию, button_back
    await state.update_data(category = category)
    await state.update_data(button_back = button_back)
    await state.update_data(action = action)

    list_performers: list = []
    for performer in await rq.get_performers():
        if performer.category_performer == category:
            list_ = [performer.name_performer, f'name_edit_performer!{performer.id}']
            list_performers.append(list_)
    logging.info(f'list_performers = {list_performers}')

    keyboard = kb.create_kb_pagination(
            list_button=list_performers,
            back=0,
            forward=2,
            count=5,
            prefix='edit_performer', # это для колбэка кнопок <<< и >>>
            button_go_away=button_back
        )
    try:
        await clb.message.edit_text(text='Какого исполнителя вы хотите выбрать?', reply_markup=keyboard)
    except:
        #await hf.process_del_message_clb(1, bot, clb)
        await clb.message.answer(text='Какого исполнителя вы хотите выбрать?', reply_markup=keyboard)
    await clb.answer()



# >>>>
@router.callback_query(F.data.startswith('button_forward!edit_performer'))
async def process_forward_next_add_performer_show_name(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_forward_next_add_performer_show_name: {clb.message.chat.id} ----- clb.data = {clb.data}')

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')

    category = (await state.get_data())['category']

    list_performers: list = []
    for performer in await rq.get_performers():
        if performer.category_performer == category:
            list_ = [performer.name_performer, f'name_edit_performer!{performer.id}']
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
    logging.info(f'keyboard = {keyboard}')
    #await asyncio.sleep(7)

    try:
        await clb.message.edit_text(text='Какого испoлнителя вы хотите выбрать?', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Какого исполнитeля вы хотите выбрать?', reply_markup=keyboard)
    await clb.answer()


# <<<<
@router.callback_query(F.data.startswith('button_back!edit_performer'))
async def process_back_next_add_performer_show_name(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_back_next_add_performer_show_name: {clb.message.chat.id} ----- clb.data = {clb.data}')

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    category = (await state.get_data())['category']

    list_performers: list = []
    for performer in await rq.get_performers():
        if performer.category_performer == category:
            list_ = [performer.name_performer, f'name_edit_performer!{performer.id}']
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
    logging.info(f'keyboard = {keyboard}')
    try:
        await clb.message.edit_text(text='Какого исполнителя вы хотитe выбрать?', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Какого исполнителя вы хотите выбpать?', reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data.startswith('name_edit_performer!'))  #  list_ = [performer.name_performer, f'name_edit_performer!{performer.id}']
async def process_edit_card_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем карточку исполнителя для редактирования"""
    try:
        logging.info(f'process_edit_card_performer --- clb.data = {clb.data}')
    except:
        logging.info(f'process_edit_card_performer --- ')
    # Эту функцию я вызываю после окончания ввода новой карточки исполнителя,там мессаджная функция,
    # поэтому нет колбэка. Надо взять id из БД, самую последнюю запись
    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')

    if await state.get_state() == None:
        id_performer = clb.data.split('!')[-1]
        await state.update_data(id_performer_state = id_performer)
    elif await state.get_state() == AddPerformersFSM.state_after_add_performer:
        id_performer = await hf.get_max_id_performers()
        await state.update_data(id_performer_state = id_performer)
    else:
        id_performer = (await state.get_data())['id_performer_state']


    # если action  в состоянии удалить, то сделать это и return
    data_state = await state.get_data()

    if 'action' in list(data_state) and data_state['action'] == 'delete':
        try:
            await clb.message.answer(text=f'Исполнитель {(await rq.get_performer_by_id(id_performer)).name_performer} успешно удален.')
            await clb.answer()
        except:
            await clb.answer(text=f'Исполнитель {(await rq.get_performer_by_id(id_performer)).name_performer} успешно удален.')
        await rq.delete_performer(id_performer)

        await process_edit_performer(clb, state, bot)
        logging.info(f'process_edit_performer(clb, state, bot) ----- clb.data = {clb.data}')
        await clb.answer()
        return


    #await hf.process_del_message_clb(1, bot, clb)
    data_ = await rq.get_performer_by_id(id_performer)
    if data_.category_performer in ['photograf', 'decorator', 'catering']:
        keyboard = kb.create_in_kb(1, **{
            'Имя': f'end_edit_performer!name_performer!{data_.id}',
            'Фото': f'end_edit_performer!photo_performer!{data_.id}',
            'Описание': f'end_edit_performer!description_performer!{data_.id}',
            'Рейтинг': f'end_edit_performer!reiting_performer!{data_.id}',
            'Стоимость': f'end_edit_performer!cost_performer!{data_.id}',
            'Телефон': f'end_edit_performer!phone_performer!{data_.id}',
            'Профиль': f'end_edit_performer!profile_performer!{data_.id}',
            'Добавить отзыв': f'end_edit_performer!feedback_performer!{data_.id}',
            'Добавить примеры работ': f'end_edit_performer!examples_work_performer!{data_.id}',
            'Подтвердить': f'confirm_change_edit_performer',
            })
    elif data_.category_performer in ['host', 'videograf',  'dj']:
        keyboard = kb.create_in_kb(1, **{
            'Имя': f'end_edit_performer!name_performer!{data_.id}',
            'Фото': f'end_edit_performer!photo_performer!{data_.id}',
            'Описание': f'end_edit_performer!description_performer!{data_.id}',
            'Рейтинг': f'end_edit_performer!reiting_performer!{data_.id}',
            'Стоимость': f'end_edit_performer!cost_performer!{data_.id}',
            'Телефон': f'end_edit_performer!phone_performer!{data_.id}',
            'Профиль': f'end_edit_performer!profile_performer!{data_.id}',
            'Добавить отзыв': f'end_edit_performer!feedback_performer!{data_.id}',
            'Подтвердить': f'confirm_change_edit_performer',
            })


    state_ = await state.get_data() # name_edit_performer
    name = state_['name_edit_performer'] if 'name_edit_performer' in list(state_) else data_.name_performer
    description = state_['description_edit_performer'] if 'description_edit_performer' in list(state_) else data_.description_performer
    reiting = state_['reiting_edit_performer'] if 'reiting_edit_performer' in list(state_) else data_.reiting_performer
    cost = state_['cost_edit_performer'] if 'cost_edit_performer' in list(state_) else data_.cost_performer
    phone = state_['phone_edit_performer'] if 'phone_edit_performer' in list(state_) else data_.phone_performer
    photo = state_['photo_edit_performer'] if 'photo_edit_performer' in list(state_) else data_.photo_performer
    profile = state_['profile_edit_performer'] if 'profile_edit_performer' in list(state_) else data_.profile_performer
    #try:
        #await hf.process_del_message_clb(1, bot, clb)
    #except:
        #await hf.process_del_message_messsage(1, bot, message=clb.message)
    try:
        await clb.message.answer_photo(
            photo=photo,
            caption=
            f'<b>Имя:</b> {name}\n'
            f'<b>Описание:</b> {description}\n'
            f'<b>Рейтинг:</b> {reiting}\n'
            f'<b>Стоимость:</b> {cost} \n'
            f'<b>Телефон для связи:</b> {phone}\n'
            f'<b>Профиль:</b> {profile}\n',
            reply_markup=keyboard)
        await clb.answer()
    except:
        await clb.answer_photo(
            photo=photo,
            caption=
            f'<b>Имя:</b> {name}\n'
            f'<b>Описание:</b> {description}\n'
            f'<b>Рейтинг:</b> {reiting}\n'
            f'<b>Стоимость:</b> {cost} \n'
            f'<b>Телефон для связи:</b> {phone}\n'
            f'<b>Профиль:</b> {profile}\n',
            reply_markup=keyboard
        )
    await clb.answer()



@router.callback_query(F.data.startswith('end_edit_performer!'))  #   'Имя': f'end_edit_performer!name_performer!{data_.id}',
async def process_end_edit_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем ссылку на профиль исполнителя"""
    logging.info(f'process_end_edit_performer --- clb.data = {clb.data}')
    ##await hf.process_del_message_clb(1, bot, clb)
    data_ = await rq.get_performer_by_id(int(clb.data.split('!')[-1]))
    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')
    state_data = await state.get_data()

    # В зависимости от кнопки колбэка переводим в нужный режим ожидания ввода данных
    clb_action = clb.data.split('!')[-2]
    id_performer = clb.data.split('!')[-1]
    keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_performer!{id_performer}'})
    if clb_action == 'name_performer':
        await state.set_state(EditPerformer.state_edit_name)
        await clb.message.edit_caption(caption=f'Пришлите новое значение имени и фамилии исполнителя', reply_markup=keyboard)
    elif clb_action == 'description_performer':
        await state.set_state(EditPerformer.state_edit_description)
        await clb.message.edit_caption(caption=f'Пришлите новое описание исполнителя', reply_markup=keyboard)
    elif clb_action == 'reiting_performer':
        await state.set_state(EditPerformer.state_edit_reiting)
        await clb.message.edit_caption(caption=f'Пришлите новое значение рейтинга в формате "4,8/5"', reply_markup=keyboard)
    elif clb_action == 'cost_performer':
        await state.set_state(EditPerformer.state_edit_cost)
        await clb.message.edit_caption(caption=f'Пришлите новое значение стоимости услуг исполнителя (например, 40000 руб. за 6 часов или 1500 руб./час)', reply_markup=keyboard)
    elif clb_action == 'phone_performer':
        await state.set_state(EditPerformer.state_edit_phone)
        await clb.message.edit_caption(caption=f'Пришлите новое значение в формате записи "+7(999)789-12-34"', reply_markup=keyboard)
    elif clb_action == 'profile_performer':
        await state.set_state(EditPerformer.state_edit_profile)
        await clb.message.edit_caption(caption=f'Пришлите ссылку на соц.сеть исполнителя', reply_markup=keyboard)
    elif clb_action == 'photo_performer':
        await state.set_state(EditPerformer.state_edit_photo)
        await clb.message.edit_caption(caption=f'Пришлите новую фотографию исполнителя', reply_markup=keyboard)
    elif clb_action == 'feedback_performer':
        await state.set_state(EditPerformer.state_edit_feedback)
        await clb.message.edit_caption(caption=f'Пришлите отзыв об исполнителe', reply_markup=keyboard)
    elif clb_action == 'examples_work_performer':
        await state.set_state(EditPerformer.state_edit_examples_work)
        await clb.message.edit_caption(caption=f'Присылайте по одной фотографии. Для завершения и сохранения нажмите "Подтвердить"', reply_markup=keyboard)

    await clb.answer()


    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')








@router.message(F.text, StateFilter(EditPerformer.state_edit_name))
@router.message(F.text, StateFilter(EditPerformer.state_edit_description))
@router.message(F.text, StateFilter(EditPerformer.state_edit_reiting))
@router.message(F.text, StateFilter(EditPerformer.state_edit_cost))
@router.message(F.text, StateFilter(EditPerformer.state_edit_phone))
@router.message(F.text, StateFilter(EditPerformer.state_edit_profile))
@router.message(F.photo, StateFilter(EditPerformer.state_edit_photo))
@router.message(F.text, StateFilter(EditPerformer.state_edit_feedback))
@router.message(F.photo, StateFilter(EditPerformer.state_edit_examples_work))

async def process_edit_performer_input_data(message: Message, state: FSMContext, bot: Bot) -> None:
    """ отлавливание ввода при редактировании исполнителя"""
    logging.info(f'process_edit_performer_input_data --- {message.text}')

    input_text = message.text
    #await hf.process_del_message_messsage(2, bot, message)

    current_state = await state.get_state()
    id_performer = (await state.get_data())['id_performer_state']
    if current_state == EditPerformer.state_edit_name: # Имя
        await state.update_data(name_edit_performer = input_text)
        await process_edit_card_performer (clb=message, state=state, bot=bot)

    elif current_state == EditPerformer.state_edit_description:  # Описание
        await state.update_data(description_edit_performer = input_text)
        await process_edit_card_performer (clb=message, state=state, bot=bot)

    elif current_state == EditPerformer.state_edit_profile:  # Профиль -- ссылка на соцсеть
        await state.update_data(profile_edit_performer = input_text)
        await process_edit_card_performer (clb=message, state=state, bot=bot)

    elif current_state == EditPerformer.state_edit_reiting: # Рейтинг
        if flt.validate_reiting(reiting=input_text):
            await state.update_data(reiting_edit_performer = input_text)
            await process_edit_card_performer (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_performer!{id_performer}'})
            await message.answer(text=f'Некорректно указаны данные. Пришлите новое значение рейтинга в формате "4,8/5"', reply_markup=keyboard)


    elif current_state == EditPerformer.state_edit_cost: # Стоимость
        await state.update_data(cost_edit_performer = input_text)
        await process_edit_card_performer (clb=message, state=state, bot=bot)

    elif current_state == EditPerformer.state_edit_phone: # Телефон
        if flt.validate_russian_phone_number(input_text):
            await state.update_data(phone_edit_performer = input_text)
            await process_edit_card_performer (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_performer!{id_performer}'})
            await message.answer(text=f'Некорректно указаны данные. Пришлите новое значение в формате записи "+7(999)789-12-34"', reply_markup=keyboard)

    elif current_state == EditPerformer.state_edit_photo: # Фото
        if message.photo:
            await state.update_data(photo_edit_performer = message.photo[-1].file_id)
            await process_edit_card_performer (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_performer!{id_performer}'})
            await message.answer(text=f'Некорректно. Надо прислать именно фотографию.', reply_markup=keyboard)

    elif current_state == EditPerformer.state_edit_feedback:  # Отзыв
        dict_feedback: dict = {'tg_id': message.chat.id, 'id_performer': id_performer, 'feedback': input_text}
        #await state.update_data(description_edit_performer = input_text)
        await rq.add_feedback(dict_feedback)
        await message.answer(text=f'Отзыв об исполнителе успешно добавлен')
        await process_edit_card_performer (clb=message, state=state, bot=bot)

    elif current_state == EditPerformer.state_edit_examples_work: # Фотографии с примерами работ
        if message.photo:
            data_state = await state.get_data()
            if 'photo_examples_work' not in list(data_state):
                await state.update_data(photo_examples_work = message.photo[-1].file_id)
            else:
                current_str_photo = data_state['photo_examples_work']
                current_str_photo = current_str_photo+','+message.photo[-1].file_id
                await state.update_data(photo_examples_work = current_str_photo)
            await process_edit_card_performer (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_performer!{id_performer}'})
            await message.answer(text=f'Некорректно. Надо прислать именно фотографию.', reply_markup=keyboard)


@router.callback_query(F.data == 'confirm_change_edit_performer')
async def process_confirm_edit_performer(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Подтвердить введенные изменения в данных исполнителя"""

    logging.info(f'process_confirm_edit_performer --- clb.data = {clb.data}')

    state_data = await state.get_data()
    id_performer = state_data['id_performer_state']
    if 'name_edit_performer' in list(state_data):
        await rq.set_performer(id_performer=id_performer, name_performer=state_data['name_edit_performer'])
    if 'reiting_edit_performer' in list(state_data):
        await rq.set_performer(id_performer=id_performer, reiting_performer=state_data['reiting_edit_performer'])
    if 'cost_edit_performer' in list(state_data):
        await rq.set_performer(id_performer=id_performer, cost_performer=state_data['cost_edit_performer'])

    if 'photo_edit_performer' in list(state_data):
        await rq.set_performer(id_performer=id_performer, photo_performer=state_data['photo_edit_performer'])
    if 'phone_edit_performer' in list(state_data):
        await rq.set_performer(id_performer=id_performer, phone_performer=state_data['phone_edit_performer'])
    if 'profile_edit_performer' in list(state_data):
        await rq.set_performer(id_performer=id_performer, profile_performer=state_data['profile_edit_performer'])
    if 'description_edit_performer' in list(state_data):
        await rq.set_performer(id_performer=id_performer, description_performer=state_data['description_edit_performer'])
    if 'photo_examples_work' in list(state_data):
        # надо сперва найти строку где сохраняется эта информация
        id_feedback: int = 0
        for data_ in await rq.get_feedbacks():
            if data_.id_performer == id_performer and data_.feedback.startswith('!_?_!'):
                id_feedback = data_.id
        if id_feedback == 0: #  т.е. такой строки не найдено. Добавляем новую строку методом add_feedback
            await rq.add_feedback({'tg_id': clb.message.chat.id, 'id_performer': id_performer, 'feedback': '!_?_!'+state_data['photo_examples_work']})
        else:
            await rq.set_feedback(id_feedback, '!_?_!'+state_data['photo_examples_work'])

    #await hf.process_del_message_clb(5, bot, clb)
    keyboard = kb.keyboards_main_menu()
    await clb.message.answer(text=f'Данные успешно обновлены', reply_markup=keyboard)
    await clb.answer()
    await process_performers(clb.message, bot)