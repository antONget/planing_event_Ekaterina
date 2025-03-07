

from aiogram import F, Router, Bot

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta
import aiogram_calendar
from handlers.locations.choice_location import AddLocationsFSM
import filters.filters as flt
from handlers.locations.choice_location import process_locations


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


# class AddlocationsFSM(StatesGroup):
#     state_add_name_location = State()
#     state_add_photo_location = State()
###    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')

class EditLocation(StatesGroup):
    state_edit_name = State()
    state_edit_description = State()
    state_edit_photo = State()
    state_edit_adress = State()
    state_edit_area = State()
    state_edit_capacity = State()
    state_edit_reiting = State()
    state_edit_cost = State()
    state_edit_phone = State()
    state_edit_profile = State()
    state_additional_photo = State()




@router.callback_query(F.data == 'edit_location') # 'Изменить список': 'edit_location'}
async def process_edit_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Выбрать локации"""
    await state.clear()
    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')
    logging.info('process_edit_location')

    dict_kb = {
        'Редактировать': 'start_edit_location',
        'Удалить': 'delete_location',
        'Добавить': 'add_location',
        }
    keyboard = kb.create_in_kb(2, **dict_kb)
    await clb.message.answer(text=f'Выберите действия для локации.', reply_markup=keyboard)
    await clb.answer()



@router.callback_query(F.data == 'start_edit_location')
@router.callback_query(F.data == 'delete_location')
@router.callback_query(F.data == 'add_location')
async def process_start_edit_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Категории локации"""
    logging.info(f'process_start_edit_location --- clb.data = {clb.data}')
    # также можно прийти сюда после удаления
    action = ''
    if clb.data == 'start_edit_location':
        action = 'next_edit_location'
    elif clb.data == 'delete_location':
        action = 'next_delete_location'
    elif clb.data == 'add_location':
        action = 'next_add_location' # Это в отдельный хэндлер и там переводить в режим ожидания ввода от пользователя данных
    # добавить в состояние action, т.к. в эту функцию прихожу и без колбэка,
    # делать проверку на наличие action
    if action: # записываю в FSM
        await state.update_data(action_from_state = action)
    else:
        action = (await state.get_data())['action_from_state']


    dict_kb = {
        'Ресторан': f'{action}!restaurant',
        'Лофт': f'{action}!loft',
        'Назад': 'edit_location',
        }
    keyboard = kb.create_in_kb(1, **dict_kb)
    await clb.message.edit_text(text=f'Какую локацию вы хотите выбрать?', reply_markup=keyboard)
    await clb.answer()



@router.callback_query(F.data.startswith('next_edit_location'))
@router.callback_query(F.data.startswith('next_delete_location'))
async def process_next_add_location_show_name(clb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Выводим  для дальнейших действий"""
    logging.info(f'process_next_add_location_show_name: {clb.message.chat.id} ----- clb.data = {clb.data}')

    if clb.data.startswith('next_edit_location'):
        button_back = 'start_edit_location'
        action = 'edit'
    elif clb.data.startswith('next_delete_location'):
        button_back = 'delete_location'
        action = 'delete'

    category = clb.data.split('!')[-1]
    #  сохраняем в состоянии инфу для пагинации: категорию, button_back
    await state.update_data(category = category)
    await state.update_data(button_back = button_back)
    await state.update_data(action = action)

    list_locations: list = []
    for location in await rq.get_locations():
        if location.category_location == category:
            list_ = [location.name_location, f'name_edit_location!{location.id}']
            list_locations.append(list_)
    logging.info(f'list_locations = {list_locations}')

    keyboard = kb.create_kb_pagination(
            list_button=list_locations,
            back=0,
            forward=2,
            count=5,
            prefix='edit_location', # это для колбэка кнопок <<< и >>>
            button_go_away=button_back
        )
    try:
        await clb.message.edit_text(text='Какого локации вы хотите выбрать?', reply_markup=keyboard)
    except:
        #await hf.process_del_message_clb(1, bot, clb)
        await clb.message.answer(text='Какого локации вы хотите выбрать?', reply_markup=keyboard)
    await clb.answer()



# >>>>
@router.callback_query(F.data.startswith('button_forward!edit_location'))
async def process_forward_next_add_location_show_name(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_forward_next_add_location_show_name: {clb.message.chat.id} ----- clb.data = {clb.data}')

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')

    category = (await state.get_data())['category']

    list_locations: list = []
    for location in await rq.get_locations():
        if location.category_location == category:
            list_ = [location.name_location, f'name_edit_location!{location.id}']
            list_locations.append(list_)
    logging.info(f'list_locations = {list_locations}')

    keyboard = kb.create_kb_pagination(
                    list_button=list_locations,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='choice_location',
                    button_go_away='choice_location'
                )
    logging.info(f'keyboard = {keyboard}')
    #await asyncio.sleep(7)

    try:
        await clb.message.edit_text(text='Какую локацию вы хотите выбрать?', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Какую лoкацию вы хотите выбрать?', reply_markup=keyboard)
    await clb.answer()


# <<<<
@router.callback_query(F.data.startswith('button_back!edit_location'))
async def process_back_next_add_location_show_name(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_back_next_add_location_show_name: {clb.message.chat.id} ----- clb.data = {clb.data}')

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    category = (await state.get_data())['category']

    list_locations: list = []
    for location in await rq.get_locations():
        if location.category_location == category:
            list_ = [location.name_location, f'name_edit_location!{location.id}']
            list_locations.append(list_)
    logging.info(f'list_locations = {list_locations}')
    keyboard = kb.create_kb_pagination(
                    list_button=list_locations,
                    back=back,
                    forward=forward,
                    count=5,
                    prefix='choice_location',
                    button_go_away='choice_location'
                )
    logging.info(f'keyboard = {keyboard}')
    try:
        await clb.message.edit_text(text='Какого локации вы хотитe выбрать?', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Какого локации вы хотите выбpать?', reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data.startswith('name_edit_location!'))  #  list_ = [location.name_location, f'name_edit_location!{location.id}']
async def process_edit_card_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем карточку локации для редактирования"""
    try:
        logging.info(f'process_edit_card_location --- clb.data = {clb.data}')
    except:
        logging.info(f'process_edit_card_location --- ')
    # Эту функцию я вызываю после окончания ввода новой карточки локации,там мессаджная функция,
    # поэтому нет колбэка. Надо взять id из БД, самую последнюю запись
    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')

    if await state.get_state() == None:
        id_location = clb.data.split('!')[-1]
        await state.update_data(id_location_state = id_location)
    elif await state.get_state() == AddLocationsFSM.state_after_add_location:
        id_location = await hf.get_max_id_locations()
        await state.update_data(id_location_state = id_location)
    else:
        id_location = (await state.get_data())['id_location_state']


    # если action  в состоянии удалить, то сделать это и return
    data_state = await state.get_data()

    if 'action' in list(data_state) and data_state['action'] == 'delete':
        try:
            await clb.message.answer(text=f'Локация {(await rq.get_location_by_id(id_location)).name_location} успешно удалена.')
            await clb.answer()
        except:
            await clb.answer(text=f'Локация {(await rq.get_location_by_id(id_location)).name_location} успешно удалена.')
        await rq.delete_location(id_location)

        await process_edit_location(clb, state, bot)
        logging.info(f'process_edit_location(clb, state, bot) ----- clb.data = {clb.data}')
        return


    #await hf.process_del_message_clb(1, bot, clb)
    data_ = await rq.get_location_by_id(id_location)

    keyboard = kb.create_in_kb(1, **{
        'Название': f'end_edit_location!name_location!{data_.id}',
        'Фото': f'end_edit_location!photo_location!{data_.id}',
        'Описание': f'end_edit_location!description_location!{data_.id}',
        'Адрес': f'end_edit_location!adress_location!{data_.id}',
        'Вместимость': f'end_edit_location!capacity_location!{data_.id}',
        'Площадь': f'end_edit_location!area_location!{data_.id}',
        'Рейтинг': f'end_edit_location!reiting_location!{data_.id}',
        'Стоимость': f'end_edit_location!cost_location!{data_.id}',
        'Телефон': f'end_edit_location!phone_location!{data_.id}',
        'Профиль': f'end_edit_location!profile_location!{data_.id}',
        'Добавить фотографии объекта': f'end_edit_location!edditional_photo_location!{data_.id}',
        'Подтвердить': f'confirm_change_edit_location',
        })

    state_ = await state.get_data() # name_edit_location
    name = state_['name_edit_location'] if 'name_edit_location' in list(state_) else data_.name_location
    photo = state_['photo_edit_location'] if 'photo_edit_location' in list(state_) else data_.photo_location
    description = state_['description_edit_location'] if 'description_edit_location' in list(state_) else data_.description_location
    adress = state_['adress_edit_location'] if 'adress_edit_location' in list(state_) else data_.adress_location
    area = state_['area_edit_location'] if 'area_edit_location' in list(state_) else data_.area_location
    capacity = state_['capacity_edit_location'] if 'capacity_edit_location' in list(state_) else data_.capacity_location
    reiting = state_['reiting_edit_location'] if 'reiting_edit_location' in list(state_) else data_.reiting_location
    cost = state_['cost_edit_location'] if 'cost_edit_location' in list(state_) else data_.cost_location
    phone = state_['phone_edit_location'] if 'phone_edit_location' in list(state_) else data_.phone_location
    profile = state_['profile_edit_location'] if 'profile_edit_location' in list(state_) else data_.profile_location

    #try:
        #await hf.process_del_message_clb(1, bot, clb)
    #except:
        #await hf.process_del_message_messsage(1, bot, message=clb.message)
    try:
        await clb.message.answer_photo(
            photo=photo,
            caption=
            f'<b>Название:</b> {name}\n'
            f'<b>Описание:</b> {description}\n'
            f'<b>Адрес:</b> {adress}\n'
            f'<b>Площадь:</b> {area}\n'
            f'<b>Вместимость:</b> {capacity}\n'
            f'<b>Рейтинг:</b> {reiting}\n'
            f'<b>Стоимость:</b> от {cost} руб/час\n'
            f'<b>Телефон для связи:</b> {phone}\n'
            f'<b>Профиль:</b> {profile}\n',
            reply_markup=keyboard
        )
        await clb.answer()
    except:
        await clb.answer_photo(
            photo=photo,
            caption=
            f'<b>Название:</b> {name}\n'
            f'<b>Описание:</b> {description}\n'
            f'<b>Адрес:</b> {adress}\n'
            f'<b>Площадь:</b> {area}\n'
            f'<b>Вместимость:</b> {capacity}\n'
            f'<b>Рейтинг:</b> {reiting}\n'
            f'<b>Стоимость:</b> от {cost} руб/час\n'
            f'<b>Телефон для связи:</b> {phone}\n'
            f'<b>Профиль:</b> {profile}\n',
            reply_markup=keyboard
        )
    #await clb.answer()


@router.callback_query(F.data.startswith('end_edit_location!'))  #   'Имя': f'end_edit_location!name_location!{data_.id}',
async def process_end_edit_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем ссылку на профиль локации"""
    logging.info(f'process_end_edit_location --- clb.data = {clb.data}')
    ##await hf.process_del_message_clb(1, bot, clb)
    data_ = await rq.get_location_by_id(int(clb.data.split('!')[-1]))
    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')
    state_data = await state.get_data()

    # В зависимости от кнопки колбэка переводим в нужный режим ожидания ввода данных
    clb_action = clb.data.split('!')[-2]
    id_location = clb.data.split('!')[-1]
    keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_location!{id_location}'})
    if clb_action == 'name_location':
        await state.set_state(EditLocation.state_edit_name)
        await clb.message.edit_caption(caption=f'Пришлите новое значение названия локации', reply_markup=keyboard)
    elif clb_action == 'description_location':
        await state.set_state(EditLocation.state_edit_description)
        await clb.message.edit_caption(caption=f'Пришлите новое описание локации', reply_markup=keyboard)

    elif clb_action == 'adress_location':
        await state.set_state(EditLocation.state_edit_adress)
        await clb.message.edit_caption(caption=f'Пришлите новый адрес локации', reply_markup=keyboard)
    elif clb_action == 'capacity_location':
        await state.set_state(EditLocation.state_edit_capacity)
        await clb.message.edit_caption(caption=f'Пришлите новое значение вместимости локации (значение должно быть числом)', reply_markup=keyboard)
    elif clb_action == 'area_location':
        await state.set_state(EditLocation.state_edit_area)
        await clb.message.edit_caption(caption=f'Пришлите новое значение площади локации (значение должно быть числом)', reply_markup=keyboard)
    elif clb_action == 'reiting_location':
        await state.set_state(EditLocation.state_edit_reiting)
        await clb.message.edit_caption(caption=f'Пришлите новое значение рейтинга в формате "4,8/5" или "5/5"', reply_markup=keyboard)
    elif clb_action == 'cost_location':
        await state.set_state(EditLocation.state_edit_cost)
        await clb.message.edit_caption(caption=f'Пришлите новое значение стоимости услуг локации в час (значение должно быть числом)', reply_markup=keyboard)
    elif clb_action == 'phone_location':
        await state.set_state(EditLocation.state_edit_phone)
        await clb.message.edit_caption(caption=f'Пришлите новый телефон локации в формате "+7(999)789-12-34"', reply_markup=keyboard)
    elif clb_action == 'profile_location':
        await state.set_state(EditLocation.state_edit_profile)
        await clb.message.edit_caption(caption=f'Пришлите ссылку на соц.сеть локации', reply_markup=keyboard)
    elif clb_action == 'photo_location':
        await state.set_state(EditLocation.state_edit_photo)
        await clb.message.edit_caption(caption=f'Пришлите новую фотографию локации', reply_markup=keyboard)

    elif clb_action == 'edditional_photo_location':
        await state.set_state(EditLocation.state_additional_photo)
        await clb.message.edit_caption(caption=f'Присылайте по одной дополнительные фотографии локации.', reply_markup=keyboard)

    await clb.answer()

    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')



@router.message(F.text, StateFilter(EditLocation.state_edit_name))
@router.message(F.text, StateFilter(EditLocation.state_edit_description))
@router.message(F.text, StateFilter(EditLocation.state_edit_adress))
@router.message(F.text, StateFilter(EditLocation.state_edit_area))
@router.message(F.text, StateFilter(EditLocation.state_edit_capacity))
@router.message(F.text, StateFilter(EditLocation.state_edit_reiting))
@router.message(F.text, StateFilter(EditLocation.state_edit_cost))
@router.message(F.text, StateFilter(EditLocation.state_edit_phone))
@router.message(F.text, StateFilter(EditLocation.state_edit_profile))
@router.message(F.photo, StateFilter(EditLocation.state_additional_photo))

async def process_edit_location_input_data(message: Message, state: FSMContext, bot: Bot) -> None:
    """ отлавливание ввода при редактировании локации"""
    logging.info(f'process_edit_location_input_data --- {message.text}')

    input_text = message.text
    #await hf.process_del_message_messsage(2, bot, message)

    current_state = await state.get_state()
    id_location = (await state.get_data())['id_location_state']

    if current_state == EditLocation.state_edit_name: # Имя
        await state.update_data(name_edit_location = input_text)
        await process_edit_card_location (clb=message, state=state, bot=bot)

    elif current_state == EditLocation.state_edit_description:  # Описание
        await state.update_data(description_edit_location = input_text)
        await process_edit_card_location (clb=message, state=state, bot=bot)

    elif current_state == EditLocation.state_edit_profile:  # Профиль -- ссылка на соцсеть
        await state.update_data(profile_edit_location = input_text)
        await process_edit_card_location (clb=message, state=state, bot=bot)

    elif current_state == EditLocation.state_edit_reiting: # Рейтинг
        if flt.validate_reiting(reiting=input_text):
            await state.update_data(reiting_edit_location = input_text)
            await process_edit_card_location (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_location!{id_location}'})
            await message.answer(text=f'Некорректно указаны данные. Пришлите новое значение рейтинга в формате "4,8/5"', reply_markup=keyboard)


    elif current_state == EditLocation.state_edit_cost: # Стоимость
        if flt.validate_cost(cost=input_text):
            await state.update_data(cost_edit_location = input_text)
            await process_edit_card_location (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_location!{id_location}'})
            await message.answer(text=f'Некорректно указаны данные.'
                                 f'Пришлите новое значение стоимости услуг локации в час (значение должно быть числом)',
                                 reply_markup=keyboard)

    elif current_state == EditLocation.state_edit_phone: # Телефон
        if flt.validate_russian_phone_number(input_text):
            await state.update_data(phone_edit_location = input_text)
            await process_edit_card_location (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_location!{id_location}'})
            await message.answer(text=f'Некорректно указаны данные. Пришлите новое значение в формате записи "+7(999)789-12-34"', reply_markup=keyboard)

    elif current_state == EditLocation.state_edit_photo: # Фото
        if message.photo:
            photo_edit_location = (await rq.get_location_by_id(id_location)).photo_location
            photo_edit_location = photo_edit_location+','+message.photo[-1].file_id
            await state.update_data(photo_edit_location = photo_edit_location)
            await process_edit_card_location (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_location!{id_location}'})
            await message.answer(text=f'Некорректно. Надо прислать именно фотографию.', reply_markup=keyboard)

    elif current_state == EditLocation.state_edit_area: # Плащадь
        if flt.validate_cost(cost=input_text):
            await state.update_data(area_edit_location = input_text)
            await process_edit_card_location (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_location!{id_location}'})
            await message.answer(text=f'Некорректно указаны данные.'
                                 f'Пришлите новое значение площади локации (значение должно быть числом)',
                                 reply_markup=keyboard)

    elif current_state == EditLocation.state_edit_capacity: # Вместимость state_edit_capacity
        if flt.validate_cost(cost=input_text):
            await state.update_data(capacity_edit_location = input_text)
            await process_edit_card_location (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_location!{id_location}'})
            await message.answer(text=f'Некорректно указаны данные.'
                                 f'Пришлите новое значение вместимости локации (значение должно быть числом)',
                                 reply_markup=keyboard)

    elif current_state == EditLocation.state_edit_adress:  # Адрес
        await state.update_data(adress_edit_location = input_text)
        await process_edit_card_location (clb=message, state=state, bot=bot)


    elif current_state == EditLocation.state_additional_photo: # Фотографии с примерами работ
        if message.photo:
            data_state = await state.get_data()
            if 'additional_photo_location' not in list(data_state):
                await state.update_data(additional_photo_location = message.photo[-1].file_id)
            else:
                current_str_photo = data_state['additional_photo_location']
                current_str_photo = current_str_photo+','+message.photo[-1].file_id
                await state.update_data(additional_photo_location = current_str_photo)
            await process_edit_card_location (clb=message, state=state, bot=bot)
        else:
            ### некорректно указаны данные
            keyboard = kb.create_in_kb(1, **{'Назад': f'name_edit_location!{id_location}'})
            await message.answer(text=f'Некорректно. Надо прислать именно фотографию.', reply_markup=keyboard)



@router.callback_query(F.data == 'confirm_change_edit_location')
async def process_confirm_edit_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Подтвердить введенные изменения в данных локации"""

    logging.info(f'process_confirm_edit_location --- clb.data = {clb.data}')

    state_data = await state.get_data()
    id_location = state_data['id_location_state']
    if 'name_edit_location' in list(state_data):
        await rq.set_location(id_location=id_location, name_location=state_data['name_edit_location'])
    if 'reiting_edit_location' in list(state_data):
        await rq.set_location(id_location=id_location, reiting_location=state_data['reiting_edit_location'])
    if 'cost_edit_location' in list(state_data):
        await rq.set_location(id_location=id_location, cost_location=state_data['cost_edit_location'])

    if 'photo_edit_location' in list(state_data):
        await rq.set_location(id_location=id_location, photo_location=state_data['photo_edit_location'])
    if 'phone_edit_location' in list(state_data):
        await rq.set_location(id_location=id_location, phone_location=state_data['phone_edit_location'])
    if 'profile_edit_location' in list(state_data):
        await rq.set_location(id_location=id_location, profile_location=state_data['profile_edit_location'])
    if 'description_edit_location' in list(state_data):
        await rq.set_location(id_location=id_location, description_location=state_data['description_edit_location'])

    if 'adress_edit_location' in list(state_data):
        await rq.set_location(id_location=id_location, adress_location=state_data['adress_edit_location'])
    if 'area_edit_location' in list(state_data):
        await rq.set_location(id_location=id_location, area_location=state_data['area_edit_location'])
    if 'capacity_edit_location' in list(state_data):
        await rq.set_location(id_location=id_location, capacity_location=state_data['capacity_edit_location'])
    if 'additional_photo_location' in list(state_data):
        await rq.set_location(id_location=id_location, additional_photo_location=state_data['additional_photo_location'])

    await clb.answer()
    #await hf.process_del_message_clb(5, bot, clb)
    keyboard = kb.keyboards_main_menu()
    await clb.message.answer(text=f'Данные успешно обновлены', reply_markup=keyboard)
    await process_locations(clb.message, bot)
