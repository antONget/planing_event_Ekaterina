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
class AddLocationsFSM(StatesGroup):
    state_add_name_location = State()
    state_add_photo_location = State()
    state_after_add_location = State()

# class PeriodExpenseFSM(StatesGroup):
#     state_start_perid_expense = State()
#     state_finish_period_expense = State()
###    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')

@router.message(F.text == 'Выбрать место 📍', IsSuperAdmin())
async def process_locations(message: Message, bot: Bot):
    logging.info('process_locations')
    #await hf.process_del_message_messsage(3, bot, message)

    keyboard = kb.keyboards_main_menu()
    await message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)

    dict_kb = {'Выбрать локацию': 'choice_location', 'Изменить список': 'edit_location'}
    keyboard = kb.create_in_kb(2, **dict_kb)
    await message.answer(text='Выберите действия для локации.', reply_markup=keyboard)


@router.callback_query(F.data == 'choice_location')
async def process_choise_category_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Выбрать локацию"""
    logging.info('process_choise_category_location')


    # for i in range (3):
    #     try:
    #         await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
    #     except:
    #         pass

    # keyboard = kb.keyboards_main_menu()
    # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=keyboard)
    dict_kb = {
        'Ресторан': 'category_location!restaurant',
        'Лофт': 'category_location!loft',
        'Назад': 'back_to_process_locations', # сделать отдельной функцией
        }
    keyboard = kb.create_in_kb(1, **dict_kb)
    await clb.message.edit_text(text=f'Какаого локацию вы хотите выбрать?', reply_markup=keyboard)
    await clb.answer()



@router.callback_query(F.data.startswith('category_location!'))
async def process_choise_name_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Категории локацию"""
    logging.info(f'process_choise_name_location --- clb.data = {clb.data}')

    category = clb.data.split('!')[-1]
    await state.update_data(category = category)
    list_locations: list = []
    for location in await rq.get_locations():
        if location.category_location == category:
            list_ = [location.name_location, f'name_location!{location.id}']
            list_locations.append(list_)
    logging.info(f'list_locations = {list_locations}')

    keyboard = kb.create_kb_pagination(
            list_button=list_locations,
            back=0,
            forward=2,
            count=5,
            prefix='choice_location', # это для колбэка кнопок <<< и >>>
            button_go_away='choice_location'
        )
    try:
        await clb.message.edit_text(text='Какую локацию вы хотите выбрать?', reply_markup=keyboard)
        await clb.answer()
    except:
        #await hf.process_del_message_clb(1, bot, clb)
        await clb.message.answer(text='Какую локацию вы хотите выбрать?', reply_markup=keyboard)
        await clb.answer()

# >>>>
@router.callback_query(F.data.startswith('button_forward!choice_location'))
async def process_forward_choice_location(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_forward_choice_location: {clb.message.chat.id} ----- clb.data = {clb.data}')

    forward = int(clb.data.split('!')[-1]) + 1
    back = forward - 2
    logging.info(f'forward = {forward} --- back = {back}')

    category = (await state.get_data())['category']

    list_locations: list = []
    for location in await rq.get_locations():
        if location.category_location == category:
            list_ = [location.name_location, f'name_location!{location.id}']
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
    #logging.info(f'keyboard = {keyboard}')
    #await asyncio.sleep(7)

    try:
        await clb.message.edit_text(text='Какую локацию вы хотитe выбрать?', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Какую локацию вы хoтите выбрать?', reply_markup=keyboard)
    await clb.answer()


# <<<<
@router.callback_query(F.data.startswith('button_back!choice_location'))
async def process_back_choice_location(clb: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_back_choice_location: {clb.message.chat.id} ----- clb.data = {clb.data}')

    back = int(clb.data.split('!')[-1]) - 1
    forward = back + 2
    logging.info(f'forward = {forward} --- back = {back}')

    category = (await state.get_data())['category']

    list_locations: list = []
    for location in await rq.get_locations():
        if location.category_location == category:
            list_ = [location.name_location, f'name_location!{location.id}']
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
   # logging.info(f'keyboard = {keyboard}')
    try:
        await clb.message.edit_text(text='Какую лoкацию вы хотитe выбрать?', reply_markup=keyboard)
    except:
        await clb.message.edit_text(text='Кaкую локацию вы хотите выбpать?', reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data.startswith('name_location!'))  #  list_ = [location.name_location, f'name_location!{location.id}']
async def process_show_card_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем карточку локацию"""
    logging.info(f'process_show_card_location --- clb.data = {clb.data}')

    #await hf.process_del_message_clb(1, bot, clb)
    id_location = clb.data.split('!')[-1]
    data_ = await rq.get_location_by_id(id_location)
    keyboard = kb.create_in_kb(1, **{'Посмотреть профиль': f'show_profile_location!{data_.id}',
                                     'Посмотреть фотографии локации': f'show_photo_location!{data_.id}',
                                     'Назад': f'category_location!{data_.category_location}'})
    #list_photo = data_.photo_location.split(',')
    #media_group.append(InputMediaPhoto(media=photo.split('!')[0], caption=caption))

    #logging.info(data_.photo_location.split(','))
    #logging.info(data_.photo_location.split(',')[1:])
    # media_group = []
    # for photo in data_.photo_location.split(','):
    #     media_group.append(InputMediaPhoto(media=photo))
    #     logging.info(photo)
    #     logging.info(media_group)
    # if media_group:
    #     # отправляем медиагруппу
    #     logging.info(f'media_group')
    #     await clb.message.answer_media_group(media=media_group)

    await clb.message.answer_photo(
        photo=data_.photo_location,
        caption=f'{data_.name_location} - {data_.description_location}\n'
        f'<b>Адрес:</b> {data_.adress_location}\n'
        f'<b>Площадь:</b> {data_.area_location}\n'
        f'<b>Вместимость:</b> {data_.capacity_location}\n'
        f'<b>Рейтинг:</b> {data_.reiting_location}\n'
        f'<b>Стоимость:</b> от {data_.cost_location} руб/час\n'
        f'<b>Телефон для связи:</b> {data_.phone_location}\n',
        reply_markup=keyboard
    )
    await clb.answer()

    # await clb.message.answer(
    #     text=
    #     f'{data_.name_location} - {data_.description_location}\n'
    #     f'<b>Адрес:</b> {data_.adress_location}\n'
    #     f'<b>Площадь:</b> {data_.area_location}\n'
    #     f'<b>Вместимость:</b> {data_.capacity_location}\n'
    #     f'<b>Рейтинг:</b> {data_.reiting_location}\n'
    #     f'<b>Стоимость:</b> от {data_.cost_location} руб/час\n'
    #     f'<b>Телефон для связи:</b> {data_.phone_location}\n',
    #     reply_markup=keyboard
    # )



   # logging.info(f'list_photo = {list_photo} --- list_photo[0] = {list_photo[0]}')

    # await clb.message.answer_photo(
    #     photo=data_.photo_location.split(',')[0],  #data_.photo_location,
    #     caption=
    #     f'{data_.name_location} - {data_.description_location}\n'
    #     f'<b>Адрес:</b> {data_.adress_location}\n'
    #     f'<b>Площадь:</b> {data_.area_location}\n'
    #     f'<b>Вместимость:</b> {data_.capacity_location}\n'
    #     f'<b>Рейтинг:</b> {data_.reiting_location}\n'
    #     f'<b>Стоимость:</b> от {data_.cost_location} руб/час\n'
    #     f'<b>Телефон для связи:</b> {data_.phone_location}\n',
    #     reply_markup=keyboard
    # )


@router.callback_query(F.data.startswith('show_profile_location!'))  #  {'Посмотреть профиль': f'show_profile_location!{data_.id}'
async def process_show_profile_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем ссылку на профиль локацию"""
    logging.info(f'process_show_profile_location --- clb.data = {clb.data}')
    #await hf.process_del_message_clb(1, bot, clb)
    id_location = int(clb.data.split('!')[-1])
    data_ = await rq.get_location_by_id(id_location)
    keyboard = kb.create_in_kb(1, **{'Назад': f'name_location!{id_location}'})
    await clb.message.answer(text=f'{data_.name_location}\n{data_.profile_location}', reply_markup=keyboard)
    await clb.answer()


@router.callback_query(F.data.startswith('show_photo_location!'))  #  'Посмотреть фотографии локации': f'show_photo_location!{data_.id}',
async def process_show_photo_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Показываем дополнительные фотографии локации"""
    logging.info(f'process_show_photo_location --- clb.data = {clb.data}')
    #await hf.process_del_message_clb(1, bot, clb)
    id_location = int(clb.data.split('!')[-1])
    data_ = await rq.get_location_by_id(id_location)
    keyboard = kb.create_in_kb(1, **{'Назад': f'name_location!{id_location}'})

    media_group = []
    if data_.additional_photo_location:
        for photo in data_.additional_photo_location.split(','):
            media_group.append(InputMediaPhoto(media=photo))
            logging.info(photo)
            logging.info(media_group)
        if media_group:
            # отправляем медиагруппу
            logging.info(f'media_group')
            await clb.message.answer_media_group(media=media_group)
            await clb.message.answer(text=f'Фотографии локации {data_.name_location}:', reply_markup=keyboard)
            await clb.answer()
            return
        else:
            await clb.message.answer(text='Примеров работ исполнителя пока нет. Их можно добавить в режире редактирования', reply_markup=keyboard)
            await clb.answer()
            return

    await clb.message.answer(text='Примеров работ исполнителя пока нет. Их можно добавить в режире редактирования', reply_markup=keyboard)
    await clb.answer()




@router.callback_query(F.data == 'back_to_process_locations')
async def process_go_to_location(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку НАЗАД в локациюя"""
    logging.info(f'process_go_to_location --- clb.data = {clb.data}')
    #await hf.process_del_message_clb(3, bot, clb)
    if clb.data == 'back_to_process_locations':
        await process_locations(clb.message, bot)
    await clb.answer()