from database.models import User,  Event, Tasks, CurrentEvent, Expenses, Performers, Locations, Feedback, async_session
from sqlalchemy import select
import logging
from dataclasses import dataclass



# ADD  ADD  ADD

# User
async def add_user(data: dict) -> None:
    """Добавление пользователя"""
    logging.info(f'add_user')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == data['tg_id']))
        if not user:
            session.add(User(**data))
            await session.commit()

# Event
async def add_event(data: dict) -> None:
    """ Добавление мероприятия """
    logging.info(f'add_event')
    async with async_session() as session:
        session.add(Event(**data))
        await session.commit()

# ECurrentEvent
async def add_current_event(data: dict) -> None:
    """ Добавление текущего мероприятия для работы с задачами этого мероприятия """
    logging.info(f'add_current_event')
    async with async_session() as session:
        session.add(CurrentEvent(**data))
        await session.commit()

# Task
async def add_task(data: dict) -> None:
    """ Добавление новой задачи текущего мероприятия """
    logging.info(f'add_task')
    async with async_session() as session:
        session.add(Tasks(**data))
        await session.commit()

# Expense
async def add_expense(data: dict) -> None:
    """ Добавление нового расхода """
    logging.info(f'add_expense')
    async with async_session() as session:
        session.add(Expenses(**data))
        await session.commit()

# Performer
async def add_performer(data: dict) -> None:
    """ Добавление нового исполнителя """
    logging.info(f'add_performer')
    async with async_session() as session:
        session.add(Performers(**data))
        await session.commit()

#  Locations
async def add_location(data: dict) -> None:
    """ Добавление новой локации """
    logging.info(f'add_location')
    async with async_session() as session:
        session.add(Locations(**data))
        await session.commit()

#  Feedbacks
async def add_feedback(data: dict) -> None:
    """ Добавление нового отзыва """
    logging.info(f'add_feedback')
    async with async_session() as session:
        session.add(Feedback(**data))
        await session.commit()

# GET  GET  GET

# User
async def get_user_by_id(tg_id: int) -> User:
    logging.info(f'get_user_by_id {tg_id}')
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

# Event
async def get_events() -> Event:
    logging.info(f'get_events')
    async with async_session() as session:
        return await session.scalars(select(Event))

async def get_event_by_id(id_event: int) -> str:
    logging.info('get_event_by_id')
    async with async_session() as session:
        event = await session.scalar(select(Event).where(Event.id == id_event))
        return event.title_event

async def get_tg_id_from_event_by_id(id_event: int) -> str:
    logging.info('get_tg_id_from_event_by_id')
    async with async_session() as session:
        event = await session.scalar(select(Event).where(Event.id == id_event))
        return event.tg_id

# CurrentEvent
async def get_current_event_all_model() -> CurrentEvent:
    """возвращает всю талицу CurrentEvent"""
    logging.info(f'get_current_event_all_model')
    async with async_session() as session:
        return await session.scalars(select(CurrentEvent))

async def get_current_event() -> str:
    """возвращает название мероприятия"""
    logging.info(f'get_current_event')
    async with async_session() as session:
        current_event = await session.scalar(select(CurrentEvent).where(CurrentEvent.id == 1))
        return current_event.title_event

async def get_current_event_id() -> int:
    """возвращает id мероприятия"""
    logging.info(f'get_current_event_id')
    async with async_session() as session:
        current_event = await session.scalar(select(CurrentEvent).where(CurrentEvent.id ==1))
        return current_event.id_event


#Tasks
async def get_tasks() -> Tasks:
    logging.info(f'get_tasks')
    async with async_session() as session:
        return await session.scalars(select(Tasks))


async def get_task_by_id(id_task: int) -> Tasks:
    """Возвращает строку задачи из таблицы Task по её id"""
    logging.info(f'get_task_by_id')
    async with async_session() as session:
        return await session.scalar(select(Tasks).where(Tasks.id == id_task))


#Expense
async def get_expenses() -> Expenses:
    logging.info(f'get_expenses')
    async with async_session() as session:
        return await session.scalars(select(Expenses))


async def get_expense_by_id(id_expense: int) -> Expenses:
    """Возвращает строку задачи из таблицы Expenses по её id"""
    logging.info(f'get_expense_by_id')
    async with async_session() as session:
        return await session.scalar(select(Expenses).where(Expenses.id == id_expense))

async def get_expense_by_title(title_expense: str) -> Expenses:
    """Возвращает строку задачи из таблицы Expenses по её title_expense"""
    logging.info(f'get_expense_by_id')
    async with async_session() as session:
        return await session.scalar(select(Expenses).where(Expenses.title_expense == title_expense))

# Performers
async def get_performers() -> Performers:
    logging.info(f'get_performers')
    async with async_session() as session:
        return await session.scalars(select(Performers))


async def get_performer_by_id(id_performer: int) -> Performers:
    """Возвращает строку задачи из таблицы Performers по её id"""
    logging.info(f'get_performer_by_id')
    async with async_session() as session:
        return await session.scalar(select(Performers).where(Performers.id == id_performer))

# Locations
async def get_locations() -> Locations:
    logging.info(f'get_locations')
    async with async_session() as session:
        return await session.scalars(select(Locations))


async def get_location_by_id(id_location: int) -> Locations:
    """Возвращает строку задачи из таблицы Locations по её id"""
    logging.info(f'get_location_by_id')
    async with async_session() as session:
        return await session.scalar(select(Locations).where(Locations.id == id_location))

# Feedback
async def get_feedbacks() -> Feedback:
    logging.info(f'get_feedbacks')
    async with async_session() as session:
        return await session.scalars(select(Feedback))

# async def get_feedback_by_id(id_performer: int) -> Locations:
#     """Возвращает строку отзыва из таблицы Feedbacks по её id"""
#     logging.info(f'get_feedback_by_id')
#     async with async_session() as session:
#         return await session.scalar(select(Feedback).where(Feedback.id_performer == id_performer))


# SET  SET  SET

# Current_event

async def set_current_event(tg_id: int, id_event: int, title_event: str ) -> CurrentEvent:
    logging.info(f'set_current_event {tg_id} {id_event} {title_event}')
    async with async_session() as session:
        current_event: CurrentEvent = await session.scalar(select(CurrentEvent).where(CurrentEvent.id == 1))
        current_event.tg_id = tg_id
        current_event.id_event = id_event
        current_event.title_event = title_event
        await session.commit()

# Tasks
async def set_task(id_task: int, title_task: str|None=None, deadline_task: str|None=None, status_task: str|None=None) -> Tasks:
    logging.info(f'set_task')
    async with async_session() as session:
        task: Tasks = await session.scalar(select(Tasks).where(Tasks.id == id_task))
        if title_task:
            task.title_task = title_task
        if deadline_task:
            task.deadline_task = deadline_task
        if status_task:
            task.status_task = status_task
        await session.commit()

# Expenses
async def set_expense(id_expense: int, title_expense: str|None=None, amount_expense: int|None=None, date_expense: str|None=None) -> Expenses:
    logging.info(f'set_expense')
    async with async_session() as session:
        expense: Expenses = await session.scalar(select(Expenses).where(Expenses.id == id_expense))
        if title_expense:
            expense.title_expense = title_expense
        if amount_expense:
            expense.amount_expense = amount_expense
        if date_expense:
            expense.date_expense = date_expense
        await session.commit()


# Performer
async def set_performer(id_performer: int,
                        name_performer: str|None=None,
                        photo_performer: str|None=None,
                        reiting_performer: str|None=None,
                        cost_performer: str|None=None,
                        phone_performer: str|None=None,
                        profile_performer: str|None=None,
                        description_performer: str|None=None,
                        ) -> Performers:
    """установка значений в таблицу Performers после редактирования"""
    logging.info(f'set_performer')
    async with async_session() as session:
        performer: Performers = await session.scalar(select(Performers).where(Performers.id == id_performer))
        if name_performer:
            performer.name_performer = name_performer
        if photo_performer:
            performer.photo_performer = photo_performer
        if reiting_performer:
            performer.reiting_performer = reiting_performer
        if cost_performer:
            performer.cost_performer = cost_performer
        if phone_performer:
            performer.phone_performer = phone_performer
        if profile_performer:
            performer.profile_performer = profile_performer
        if description_performer:
            performer.description_performer = description_performer

        await session.commit()




# Location
async def set_location(id_location: int,
                       name_location: str|None=None,
                       description_location: str|None=None,
                       photo_location: str|None=None,
                       adress_location: str|None=None,
                       area_location: str|None=None,
                       capacity_location: str|None=None,
                       reiting_location: str|None=None,
                       cost_location: str|None=None,
                       phone_location: str|None=None,
                       profile_location: str|None=None,
                       additional_photo_location: str|None=None,
                       ) -> Locations:
    """установка значений в таблицу Locations после редактирования"""
    logging.info(f'set_locations')
    async with async_session() as session:
        location: Locations = await session.scalar(select(Locations).where(Locations.id == id_location))
        if name_location:
            location.name_location = name_location
        if description_location:
            location.description_location = description_location
        if photo_location:
            location.photo_location = photo_location
        if adress_location:
            location.adress_location = adress_location
        if area_location:
            location.area_location = area_location
        if capacity_location:
            location.capacity_location = capacity_location
        if reiting_location:
            location.reiting_location = reiting_location
        if cost_location:
            location.cost_location = cost_location
        if phone_location:
            location.phone_location = phone_location
        if profile_location:
            location.profile_location = profile_location
        if additional_photo_location:
            location.additional_photo_location = additional_photo_location

        await session.commit()

# Feedback
async def set_feedback(id_feedback: int,
                       feedback: str|None=None,
                       ) -> Feedback:
    """установка значений в таблицу Feedback после редактирования"""
    logging.info(f'set_locations')
    async with async_session() as session:
        feedback: Feedback = await session.scalar(select(Feedback).where(Feedback.id == id_feedback))
        feedback.feedback = feedback

        await session.commit()

# async def update_product(product_id: int, column: str, new_value: str) -> None:
#     """
#     Обновление поля
#     :return:
#     """
#     logging.info('update_product')
#     async with async_session() as session:
#         await session.execute(update(Locations).where(Locations.id == product_id).values({column: new_value},))
#         await session.commit()


### DEL DEL DEL

# Task

async def delete_task(id_task: int) -> Tasks:
    logging.info(f'delete_task --- id_task = {id_task}')
    async with async_session() as session:
        task: Tasks = await session.scalar(select(Tasks).where(Tasks.id == id_task))
        await session.delete(task)
        await session.commit()

# Expenses
async def delete_expense(id_expense: int) -> Expenses:
    logging.info(f'delete_expense --- id_expense = {id_expense}')
    async with async_session() as session:
        expense: Expenses = await session.scalar(select(Expenses).where(Expenses.id == id_expense))
        await session.delete(expense)
        await session.commit()


# Performers
async def delete_performer(id_performer: int) -> Performers:
    logging.info(f'delete_performer --- id_performer = {id_performer}')
    async with async_session() as session:
        performer: Performers = await session.scalar(select(Performers).where(Performers.id == id_performer))
        await session.delete(performer)
        await session.commit()


# Locations
async def delete_location(id_location: int) -> Locations:
    logging.info(f'delete_location --- id_location = {id_location}')
    async with async_session() as session:
        location: Locations = await session.scalar(select(Locations).where(Locations.id == id_location))
        await session.delete(location)
        await session.commit()