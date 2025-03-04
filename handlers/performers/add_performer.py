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

import keyboards.keyboards as kb

from filters.admin_filter import check_super_admin
from database.models import User
import database.requests as rq
import database.help_function as hf
from datetime import time, date, datetime, timedelta
from filters.admin_filter import IsSuperAdmin
from filters.filters import validate_date, validate_overdue, validate_amount
from handlers.performers.edit_performer import process_edit_card_performer
router = Router()

storage = MemoryStorage()

import logging


###    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')


@router.callback_query(F.data.startswith('next_add_performer'))
async def process_next_add_performer(clb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Переводим в режим ожидания ввода Имени И Фамилии исплнителя от пользователя"""
    logging.info(f'process_next_add_performer: {clb.message.chat.id} ----- clb.data = {clb.data}')

    #await hf.process_del_message_clb(1, bot, clb)
    await state.set_state(AddPerformersFSM.state_add_name_performer)
    await clb.message.answer(text=f'Пришлите имя исполнителя')
    # В состояние записываем категорию, которая пришла с колбэком
    await state.update_data(category_add_performer = clb.data.split('!')[-1])
    await clb.answer()


@router.message(F.text, StateFilter(AddPerformersFSM.state_add_name_performer))
async def process_next_add_performer_name(message: Message, state: FSMContext, bot: Bot) -> None:
    """ отлавливание ввода Имени пользователя"""
    logging.info(f'process_next_add_performer_name --- {message.text}')

    name_add_performer = message.text
    await state.update_data(name_add_performer = name_add_performer)
    #await hf.process_del_message_messsage(2, bot, message)
    await message.answer(text=f'Пришлите фото исполнителя')
    await state.set_state(AddPerformersFSM.state_add_photo_performer)


@router.message(F.photo, StateFilter(AddPerformersFSM.state_add_photo_performer))
async def process_next_add_performer_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    """ отлавливание ввода фотографии, сохранение в БД, перевод в функцию Редактирования карточки"""
    logging.info(f'process_next_add_performer_photo')

    photo_add_performer = message.photo[-1].file_id
    await state.update_data(photo_add_performer = photo_add_performer)
    data_ = await state.get_data()
    dict_performer = {
        'tg_id': message.chat.id,
        'name_performer': data_['name_add_performer'],
        'category_performer': data_['category_add_performer'],
        'photo_performer': data_['photo_add_performer']
        }
    await rq.add_performer(dict_performer)

    #await hf.process_del_message_messsage(2, bot, message)

    # id_performer = await hf.get_max_id_performers()

    # data_ = await rq.get_performer_by_id(id_performer)

    # keyboard = kb.create_in_kb(1, **{
    #     'Имя': f'end_edit_performer!name_performer!{data_.id}',
    #     'Фото': f'end_edit_performer!photo_performer!{data_.id}',
    #     'Описание': f'end_edit_performer!description_performer!{data_.id}',
    #     'Рейтинг': f'end_edit_performer!reiting_performer{data_.id}',
    #     'Стоимость': f'end_edit_performer!cost_performer!{data_.id}',
    #     'Телефон': f'end_edit_performer!phone_performer!{data_.id}',
    #     'Профиль': f'end_edit_performer!profile_performer!{data_.id}',
    #     'Подтвердить': f'confirm_change_edit_performer',
    #     })

    await message.answer(text=f'Вы можете продолжать редактировать карточку исполнителя')#, reply_markup=keyboard)
    logging.info('process_next_add_performer_photo --- end funcion')

    await state.set_state(AddPerformersFSM.state_after_add_performer)
    logging.info(f'await state.get() = {await state.get_state()} --- await state.get_data() = {await state.get_data()}')
    ### запускаем редактирование по этой карточке
    await process_edit_card_performer (clb=message, state=state, bot=bot)
