
from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_ids: str  #list[int]  # Список id администраторов бота
    support_id: int # Мой id для отправки сообщений об ошибке


@dataclass
class Config:
    tg_bot: TgBot


# Создаем функцию, которая будет читать файл .env и возвращать
# экземпляр класса Config с заполненными полями token и admin_ids
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=env('ADMIN_IDS'),
            #admin_ids=list(map(int, env.list('ADMIN_IDS'))),
            support_id=env('SUPPORT_ID')
        )
    )
