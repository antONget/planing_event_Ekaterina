import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_data.config import Config, load_config
from handlers import start_handlers, other_handlers
from handlers.tasks import add_tasks, edit_tasks
from handlers.expenses import add_expense, my_expenses
from handlers.expenses.edit_expenses import (edit_date_expense, edit_expenses, edit_title_expense,
                                             edit_amount_expense, delete_expense)
from handlers.performers import choice_performer, edit_performer, add_performer
from handlers.locations import choice_location, edit_location, add_location
from handlers.feedback import feedback
from handlers.start_handlers import storage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.tasks.add_tasks import process_scheduler_send_task


from database.models import async_main
from aiogram.types import ErrorEvent
import traceback
from aiogram.types import FSInputFile

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    await async_main()

   # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        ###filename="py_log.log", # закомментировать при разработке
        ###filemode='w', # закомментировать при разработке
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )



    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(process_scheduler_send_task, 'cron', minute='*', args=(bot,))### minute
    scheduler.start()




    dp = Dispatcher(storage=storage)

    # Регистриуем роутеры в диспетчере
    dp.include_router(start_handlers.router)
    dp.include_router(add_tasks.router)
    dp.include_router(edit_tasks.router)
    dp.include_router(add_expense.router)
    dp.include_router(my_expenses.router)
    dp.include_router(edit_expenses.router)
    dp.include_router(edit_title_expense.router)
    dp.include_router(delete_expense.router)
    dp.include_router(edit_amount_expense.router)
    dp.include_router(edit_date_expense.router)
    dp.include_router(choice_performer.router)
    dp.include_router(edit_performer.router)
    dp.include_router(add_performer.router)
    dp.include_router(feedback.router)
    dp.include_router(choice_location.router)
    dp.include_router(edit_location.router)
    dp.include_router(add_location.router)

    dp.include_router(other_handlers.router)

    @dp.error()
    async def error_handler(event: ErrorEvent):
        logger.critical("Критическая ошибка: %s", event.exception, exc_info=True)
        await bot.send_message(chat_id=config.tg_bot.support_id,
                               text=f'{event.exception}')
        formatted_lines = traceback.format_exc()
        text_file = open('error.txt', 'w')
        text_file.write(str(formatted_lines))
        text_file.close()
        await bot.send_document(chat_id=config.tg_bot.support_id,
                                document=FSInputFile('error.txt'))


    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())