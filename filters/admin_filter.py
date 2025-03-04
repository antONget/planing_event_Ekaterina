from config_data.config import load_config, Config
from aiogram.filters import BaseFilter
from aiogram.types import Message
import logging

config: Config = load_config()


async def check_super_admin(telegram_id: int) -> bool:
    """
    Проверка на администратора
    :param telegram_id: id пользователя телеграм
    :return: true если пользователь администратор, false в противном случае
    """
    logging.info('check_manager')
    list_super_admin = config.tg_bot.admin_ids.split(',')
    logging.info(f'str(telegram_id) in list_super_admin  =  {str(telegram_id) in list_super_admin} {list_super_admin}')
    return str(telegram_id) in list_super_admin


class IsSuperAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        logging.info(f'await check_super_admin(telegram_id=message.chat.id) = {await check_super_admin(telegram_id=message.chat.id)}')
        return await check_super_admin(telegram_id=message.chat.id)