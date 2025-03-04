import re
import logging
from datetime import datetime



def validate_date(time_date: str) -> bool:
    """
    Валидация на формат даты чч:мм дд.мм.гггг
    :param date:
    :return:
    """
    logging.info('validate_date')
    # Паттерн для времени и даты чч:мм дд.мм.гггг
    pattern = re.compile(r'^(?:[01]\d|2[0-3]):[0-5]\d (?:[0-2]\d|3[01])[.](?:[01]\d|1[0-2])[.](\d{4})$')
       # (r'\b(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-([0-9]{4})\b')

    # Проверка соответствия паттерну
    match = pattern.match(time_date)
    logging.info(f'validate_date --- return bool(match) = {bool(match)}')
    return bool(match)


def validate_overdue(time_date: str) -> bool:
    logging.info(f'validate_overdue --- time_date = {time_date}')

    input_time, input_date = time_date.split(' ')
    hour, minutes = input_time.split(':')
    day, month, year = input_date.split('.')
    format_str_date_time = f'{year}.{month}.{day} {hour}:{minutes}:00.00'
    input_date_time = datetime.strptime(format_str_date_time, '%Y.%m.%d %H:%M:%S.%f')
    time_now = datetime.now()
    if time_now < input_date_time: # проверка на НЕПРОСРОЧЕННОЙТЬ
        logging.info('НЕ просроченна')
        return True
    logging.info('ПРОСРОЧЕНА')
    return False


def validate_amount(amount: str) -> bool:
    """Возвращает True, если все символы в строке - числа """
    logging.info(f'validate_amount --- amount = {amount}')
    for c in amount:
        if not c.isdigit():
            return False
    return True


def validate_reiting(reiting: str) -> bool:
    """
    Валидация на формат рейтинга 4,8/5

    """
    logging.info('validate_reiting')

    if len(reiting) == 3 and reiting[-1] == '5' and reiting[-2] == '/' and reiting[0] in ('1', '2', '3', '4', '5'):
        logging.info(f'len = 3') # 5/5
        return True
    elif len(reiting) == 5 and reiting[-1] == '5' and reiting[-2] == '/' and reiting[1] == ',' and reiting[0].isdigit() and reiting[2].isdigit():
        logging.info(f'len = 5') # 4,9/5
        return True
    elif len(reiting) == 6 and reiting[-1] == '5' and reiting[-2] == '/' and reiting[1] == ',' and reiting[0].isdigit() and reiting[2].isdigit() and reiting[3].isdigit():
        logging.info(f'len = 5') # 4,79/5
        return True
    logging.info(f'----False----')
    return False


def validate_cost(cost: str) -> bool:
    """ Валидация на стоимости ЧИСЛО или нет """
    logging.info('validate_cost')

    for c in cost:
        if not c.isdigit():
            logging.info(f'----False----')
            return False
    logging.info(f'----True----')
    return True


def validate_russian_phone_number(phone_number):
    # Паттерн для российских номеров телефона
    # Российские номера могут начинаться с +7, 8, или без кода страны
    pattern = re.compile(r'^(\+7|8|7)?(\d{10})$')

    # Проверка соответствия паттерну
    match = pattern.match(phone_number)

    return bool(match)