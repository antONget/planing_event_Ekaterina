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

import keyboards.keyboards as kb

from filters.admin_filter import check_super_admin
from database.models import User
import database.requests as rq
import database.help_function as hf
from datetime import time, date, datetime, timedelta
from filters.admin_filter import IsSuperAdmin
from filters.filters import validate_date, validate_overdue, validate_amount
from handlers.locations.edit_location import process_edit_card_location
router = Router()

storage = MemoryStorage()

import logging


###    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')


@router.callback_query(F.data.startswith('next_add_location'))
async def process_next_add_location(clb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Переводим в режим ожидания ввода Локации от пользователя"""
    logging.info(f'process_next_add_location: {clb.message.chat.id} ----- clb.data = {clb.data}')

    #await hf.process_del_message_clb(1, bot, clb)
    await state.set_state(AddLocationsFSM.state_add_name_location)
    await clb.message.answer(text=f'Пришлите назване локации')
    # В состояние записываем категорию, которая пришла с колбэком
    await state.update_data(category_add_location = clb.data.split('!')[-1])
    await clb.answer()


@router.message(F.text, StateFilter(AddLocationsFSM.state_add_name_location))
async def process_next_add_location_name(message: Message, state: FSMContext, bot: Bot) -> None:
    """ отлавливание ввода названия Локации"""
    logging.info(f'process_next_add_location_name --- {message.text}')

    name_add_location = message.text
    await state.update_data(name_add_location = name_add_location)
    #await hf.process_del_message_messsage(2, bot, message)
    await message.answer(text=f'Пришлите фото локации')
    await state.set_state(AddLocationsFSM.state_add_photo_location)


@router.message(F.photo, StateFilter(AddLocationsFSM.state_add_photo_location))
async def process_next_add_location_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    """ отлавливание ввода фотографии, сохранение в БД, перевод в функцию Редактирования карточки"""
    logging.info(f'process_next_add_location_photo')

    photo_add_location = message.photo[-1].file_id
    await state.update_data(photo_add_location = photo_add_location)
    data_ = await state.get_data()
    dict_location = {
        'name_location': data_['name_add_location'],
        'category_location': data_['category_add_location'],
        'photo_location': data_['photo_add_location'],
        'tg_id': message.chat.id
        }
    await rq.add_location(dict_location)

    #await hf.process_del_message_messsage(2, bot, message)

    # id_location = await hf.get_max_id_locations()

    # data_ = await rq.get_location_by_id(id_location)

    # keyboard = kb.create_in_kb(1, **{
    #     'Имя': f'end_edit_location!name_location!{data_.id}',
    #     'Фото': f'end_edit_location!photo_location!{data_.id}',
    #     'Описание': f'end_edit_location!description_location!{data_.id}',
    #     'Рейтинг': f'end_edit_location!reiting_location{data_.id}',
    #     'Стоимость': f'end_edit_location!cost_location!{data_.id}',
    #     'Телефон': f'end_edit_location!phone_location!{data_.id}',
    #     'Профиль': f'end_edit_location!profile_location!{data_.id}',
    #     'Подтвердить': f'confirm_change_edit_location',
    #     })

    await message.answer(text=f'Вы можете продолжать редактировать карточку локации')#, reply_markup=keyboard)
    logging.info('process_next_add_location_photo --- end funcion')

    await state.set_state(AddLocationsFSM.state_after_add_location)
    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')
    ### запускаем редактирование по этой карточке
    await process_edit_card_location (clb=message, state=state, bot=bot)
