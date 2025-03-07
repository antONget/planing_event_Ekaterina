from sqlalchemy import BigInteger, ForeignKey, String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url="sqlite+aiosqlite:///database/db.sqlite3", echo=False)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String)#, default='username')


class Event(Base):
    __tablename__ = 'event'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    title_event: Mapped[str] = mapped_column(String)


class Tasks(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    title_task: Mapped[str] = mapped_column(String)
    id_event: Mapped[int] = mapped_column(Integer)
    deadline_task: Mapped[str] = mapped_column(String, default='note')
    status_task: Mapped[str] = mapped_column(String, default='active') # [active, complete]


class Expenses(Base):
    __tablename__ = 'expenses'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    title_expense: Mapped[str] = mapped_column(String)
    amount_expense: Mapped[str] = mapped_column(String, default='note')
    id_event: Mapped[int] = mapped_column(Integer)
    date_expense: Mapped[str] = mapped_column(String)


class CurrentEvent(Base):
    __tablename__ = 'current_event'
    id: Mapped[int] = mapped_column(primary_key=True)
    id_event: Mapped[int] = mapped_column(BigInteger)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    title_event: Mapped[str] = mapped_column(String)


class Performers(Base):
    __tablename__ = 'performers'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    name_performer: Mapped[str] = mapped_column(String)
    category_performer: Mapped[str] = mapped_column(String)
    photo_performer: Mapped[str] = mapped_column(String)
    reiting_performer: Mapped[str] = mapped_column(String, default='не указано')
    cost_performer: Mapped[str] = mapped_column(String, default='не указано')
    phone_performer: Mapped[str] = mapped_column(String, default='не указано')
    profile_performer: Mapped[str] = mapped_column(String, default='не указано')
    description_performer: Mapped[str] = mapped_column(String, default='не указано')


class Locations(Base):
    __tablename__ = 'locations'
    id: Mapped[int] = mapped_column(primary_key=True)
    name_location: Mapped[str] = mapped_column(String)
    category_location: Mapped[int] = mapped_column(BigInteger)
    description_location: Mapped[str] = mapped_column(String, default='не указано')
    photo_location: Mapped[str] = mapped_column(String)
    adress_location: Mapped[str] = mapped_column(String, default='не указано')
    area_location: Mapped[str] = mapped_column(String, default='не указано')
    capacity_location: Mapped[str] = mapped_column(String, default='не указано')
    reiting_location: Mapped[str] = mapped_column(String, default='не указано')
    cost_location: Mapped[str] = mapped_column(String, default='не указано')
    phone_location: Mapped[str] = mapped_column(String, default='не указано')
    profile_location: Mapped[str] = mapped_column(String, default='не указано')
    additional_photo_location: Mapped[str] = mapped_column(String, default='')


class Feedback(Base):
    __tablename__ = 'feedback'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    id_performer: Mapped[int] = mapped_column(BigInteger)
    feedback: Mapped[str] = mapped_column(String)


class EventFeedback(Base):
    __tablename__ = 'event_feedback'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
   # username: Mapped[str] = mapped_column(String)
    id_event: Mapped[int] = mapped_column(BigInteger)
    estimation: Mapped[int] = mapped_column(Integer, default=0)
    feedback: Mapped[str] = mapped_column(String)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)