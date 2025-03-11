import database.help_function as hf
import database.requests as rq
from filters.filters import validate_overdue
import logging

async def get_max_id_event() -> int:
    logging.info('get_max_id_event')
    """возвращает максимальное id (primery key) из таблицы Event"""

    events = await rq.get_events()
    count_id = 1
    for event in events:
        if event.id > count_id:
            count_id = event.id
    logging.info(f'return_max_id_event = {count_id}')
    return count_id

async def get_max_id_performers() -> int:
    logging.info('get_max_id_performers')
    """возвращает максимальное id (primery key) из таблицы Performers"""

    performers = await rq.get_performers()
    count_id = 1
    for performer in performers:
        if performer.id > count_id:
            count_id = performer.id
    logging.info(f'return_max_id_performer = {count_id}')
    return count_id

async def get_max_id_locations() -> int:
    logging.info('get_max_id_locations')
    """возвращает максимальное id (primery key) из таблицы Locations"""

    locations = await rq.get_locations()
    count_id = 1
    for location in locations:
        if location.id > count_id:
            count_id = location.id
    logging.info(f'return_max_id_location = {count_id}')
    return count_id



async def check_status_task() -> None:
    """Проходит по таблице Task, если задача просрочена и была в состоянии 'active': '🛠', то меняет на просрочена 'overdue' ❌"""
    logging.info('check_status_task')

    for task in await rq.get_tasks():
        if task.deadline_task and task.deadline_task != 'note':
            logging.info(f'task.deadline_task={task.deadline_task}')
            if not validate_overdue(task.deadline_task) and task.status_task == 'active':
                logging.info(f'not validate_overdue(task.deadline_task) = {not validate_overdue(task.deadline_task)} --- task.status_task = {task.status_task}')
                await rq.set_task(id_task=task.id, status_task='overdue')


async def process_del_message_clb(count: int, bot, clb):
    """Удаляем столько сообщений, сколько передали с count"""
    logging.info('process_del_message_clb')

    for i in range (count):
        try:
            await bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id-i)
        except:
            pass

async def process_del_message_messsage(count: int, bot, message):
    """Удаляем столько сообщений, сколько передали с count"""
    logging.info('process_del_message_message')

    for i in range (count):
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-i)
        except:
            pass