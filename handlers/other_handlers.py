
from aiogram import Router, Bot
from aiogram.types import Message, FSInputFile
from handlers.expenses.add_expense import process_expense
from handlers.performers.choice_performer import process_performers
from handlers.tasks.add_tasks import process_task
from aiogram.filters import Command
import database.requests as rq
import logging
import database.help_function as hf

router = Router()

#
@router.message(Command('help'))
@router.message(Command('budget'))
@router.message(Command('location'))
@router.message(Command('executor'))
@router.message(Command('tasks'))
async def process_command(message: Message, bot: Bot):
    """Обработка команд
    /start - Перезапуск бота
    /help - Система присылает справочную информацию о командах
    /budget - Ведение бюджета
    /location - Выбор локации
    /executor - Выбор исполнителей
    /tasks - Отслеживание задач
    /feedback - Оставить обратную связь о мероприятии
     """
    #await hf.process_del_message_messsage(4, bot, message)
    if message.text == '/help':
        await message.answer(text=f'Список команд бота:\n'
                                f'/start - Перезапуск бота\n'
                                f'/help - Система присылает справочную информацию о командах\n'
                                f'/budget - Ведение бюджета\n'
                                f'/location - Выбор локации\n' # пока не сделано
                                f'/executor - Выбор исполнителей\n'
                                f'/tasks - Отслеживание задач\n'
                                f' /feedback - Оставить обратную связь о мероприятии (для администратора не доступен)\n')
    elif message.text == '/budget':
        await process_expense(message, bot)
    elif message.text == '/executor':
        await process_performers(message, bot)
    # elif message.text == '/location':
    #     await process_performers(message, bot)
    elif message.text == '/tasks':
        await process_task(message, bot)




# Хэндлер для сообщений, которые не попали в другие хэндлеры
@router.message()
async def send_answer(message: Message, bot: Bot):
    logging.info(f'message.text = {message.text}')
    tg_id = message.chat.id

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    #await message.answer(text=f'❌ <b>Неизвестная команда!</b>\n\n'
     #                    f'<i>Вы отправили сообщение напрямую в чат бота,</i>\n'
      #                   f'<i>или структура меню была изменена Админом.</i>\n\n'
       #                  f'ℹ️ Не отправляйте прямых сообщений боту\n'
        #                 f'или шуруйте в начало, нажав /start')
    if message.video:
        print(message.video.file_id)
    if message.photo:
        print(message.photo[-1].file_id)
    if message.text == '/get_logfile':
        file_path = "py_log.log"
        await message.answer_document(FSInputFile(file_path))

    if message.text == '/get_DB':
        file_path = "database/db.sqlite3"
        await message.answer_document(FSInputFile(file_path))
