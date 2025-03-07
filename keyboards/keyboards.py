from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging



def create_in_kb(width: int,
                 **kwargs: str) -> InlineKeyboardMarkup:

    kb_builder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []
    if kwargs:
        for button, callback_data in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=callback_data))
    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()



# клавиатура для пагинации (Общая)
def create_kb_pagination(
        list_button: list,
        back: int,
        forward: int,
        count:int,
        #clb_name: str,
        prefix: str, # это чтобы различались кнопки >>> и <<< при пагинации. Они начинаются: button_back и button_forward
        button_go_away: str | None=None,
        button_amount_expense_period: str | None=None,
        button_amount_expense_category: str | None=None,
        )->InlineKeyboardMarkup:
    logging.info('create_kb_pagination')

    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2

    # считаем сколько всего блоков по заданному количеству элементов в блоке
    count_buttons = len(list_button)
    whole = count_buttons // count
    remains = count_buttons % count
    max_forward = whole + 1
    # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for inside_list in list_button[back*count:(forward-1)*count]:
        text = inside_list[0]
        button = inside_list[1]
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    kb_builder.row(*buttons, width=1)

    if len(list_button) > 5:
        button_back = InlineKeyboardButton(text='<<<', callback_data=f'button_back!{prefix}!{str(back)}')
                                        #f'{prefix_wardrobe}_back!{str(back)}!{clb_name}')
        button_next = InlineKeyboardButton(text='>>>', callback_data=f'button_forward!{prefix}!{str(forward)}')
                                        #f'{prefix_wardrobe}_forward!{str(forward)}!{clb_name}')
        button_count = InlineKeyboardButton(text=f'{back+1}', callback_data='none')
        kb_builder.row(button_back, button_count, button_next)

    if button_amount_expense_category:
        button_amount_expense_category = InlineKeyboardButton(text='Сумма расходов', callback_data=button_amount_expense_category)
        kb_builder.row(button_amount_expense_category)

    if button_amount_expense_period:
        button_amount_expense_period = InlineKeyboardButton(text='Сумма расходов', callback_data=button_amount_expense_period)
        kb_builder.row(button_amount_expense_period)

    if button_go_away:
        button_go_away = InlineKeyboardButton(text='Назад', callback_data=button_go_away)
        kb_builder.row(button_go_away)

    return kb_builder.as_markup()


def keyboards_common_four_buttons() -> ReplyKeyboardMarkup:
    logging.info("keyboards_common_four_buttons")
    button_1 = KeyboardButton(text='Задачи 📄')
    button_2 = KeyboardButton(text='Выбрать место 📍')
    button_3 = KeyboardButton(text='Запланировать бюджет 💸')
    button_4 = KeyboardButton(text='Исполнители 🙋')
    button_5 = KeyboardButton(text='Посмотреть обратную связь 👀')
    button_6 = KeyboardButton(text='Переименовать мероприятие 💫')
    button_7 = KeyboardButton(text='Выбрать новое мероприятие 🆕')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1, button_2], [button_3, button_4], [button_5], [button_6], [button_7]],
        resize_keyboard=True
    )
    return keyboard


### TASK

# def keyboard_tast_1() -> InlineKeyboardMarkup:

#     logging.info("keyboard_tast_1")
#     button_1 = InlineKeyboardButton(text='Добавить 📥', callback_data=f'add_task')
#     button_2 = InlineKeyboardButton(text='Мои задачи',  callback_data=f'my_tasks')

#     keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]])
#     return keyboard



def keyboards_main_menu() -> ReplyKeyboardMarkup:
    logging.info("keyboards_main_menu")
    button_1 = KeyboardButton(text='Главное меню 🏠')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]], resize_keyboard=True)
    return keyboard