from aiogram import F, Router, Bot


from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


import keyboards.keyboards as kb
import database.requests as rq
import database.help_function as hf

router = Router()

storage = MemoryStorage()

import logging

class EditExpenseFSM(StatesGroup):
    state_edit_title_expense = State()
    state_edit_amount_expense = State()
    state_edit_date_expense = State()
    state_after_input_title_expense = State()

    #state_finish_period_expense = State()


@router.callback_query(F.data.endswith('expense_category'))
@router.callback_query(F.data.endswith('expense_period'))
async def process_edit_expenses(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Cобран список или по периодам или по категориям, ! - разделитель, чтобы пользователь в названии его не перебил текстом"""

    logging.info(f'process_edit_expenses --- clb.data = {clb.data}')
    #await state.clear()
    id_expense = int(clb.data.split('!')[0])
    data_expense = await rq.get_expense_by_id(id_expense=id_expense)
    title_expense = data_expense.title_expense
    date_expense = data_expense.date_expense
    amount_expense = data_expense.amount_expense
    ##await hf.process_del_message_clb(4, bot, clb)
    #await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:', reply_markup=kb.keyboards_main_menu())
    kb_dict = {'Редактировать ✏️': f'edit_expense!{id_expense}',
                'Удалить ❌': f'delete_expense!{id_expense}',
                'Назад': 'my_expenses'}

    keyboard = kb.create_in_kb(2, **kb_dict)
    await clb.message.edit_text(text=f'Что необходимо сделать с записью о расходе <b>"{title_expense}"</b> \n{amount_expense} ₽\n🗓 {date_expense}?', reply_markup=keyboard)
    await state.clear()
    await state.update_data(id_expense_to_edit = id_expense)### для конопки ПОДТВЕРДИТЬ
    ## Проверь состояние
    logging.info(f'await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')
    # Структура FSM для редактирования Расходов
    # id_expense_to_edit -  ттот id строки, которую надо будет подправить
    # edit_title_expense, edit_amount_expense, edit_date_expense - те названия, суммы и даты Расходов, которые надо будет сохранить в строке id
    await clb.answer()




@router.callback_query(F.data.startswith('edit_expense'))
async def process_edit_expense(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Нажали кнопку Редактировать в разделе Редактировать Расход"""
    try:
        logging.info(f'process_edit_expense --- clb.data = {clb.data}')
    except:
        logging.info(f'process_edit_expense --- clb.data = -------')

    # В эту функцию я могу попасть двумя способами.
    # 1 - Кнопка "редактировать", без состояния.
    # 2 - Вызовом из функции process_edit_expense_category в состоянии state_edit_title_expense = State()
    # и если в состоянии state_edit_title_expense = State(), то название Расхода сохранить в FSM и показать на кнопке
    logging.info(f'await state.get_data() = {await state.get_data()} await state.get_state() = {await state.get_state()}')

    if await state.get_state() == None:
        id_expense = int(clb.data.split('!')[-1]) # этот id может быть с редактируемой строки, а может быть с новой

        data_expense = await rq.get_expense_by_id(id_expense)
        title_expense = data_expense.title_expense
        amount_expense = data_expense.amount_expense
        date_expense = data_expense.date_expense

    elif await state.get_state() == EditExpenseFSM.state_edit_title_expense: # ТОЛЬКО НОВОЕ ИМЯ по новому id. Остальные данные по id из state
        id_expense = int(clb.data.split('!')[-1]) # # ТОЛЬКО НОВОЕ ИМЯ по новому id. оно в колбэке
        title_expense = (await rq.get_expense_by_id(id_expense)).title_expense
        # установка этого имени в состояние
        await state.update_data(edit_title_expense = title_expense)

        # Остальные id по тому, что в state:
        id_expense = (await state.get_data())['id_expense_to_edit']
        #title_expense = (await state.get_data())['edit_title_expense'] if 'edit_title_expense' in list(await state.get_data()) else (await rq.get_expense_by_id(id_expense)).title_expense
        date_expense = (await state.get_data())['edit_date_expense'] if 'edit_date_expense' in list(await state.get_data()) else (await rq.get_expense_by_id(id_expense)).date_expense
        amount_expense = (await state.get_data())['edit_amount_expense'] if 'edit_amount_expense' in list(await state.get_data()) else (await rq.get_expense_by_id(id_expense)).amount_expense

    elif await state.get_state() == EditExpenseFSM.state_after_input_title_expense or await state.get_state() == EditExpenseFSM.state_edit_amount_expense or await state.get_state() == EditExpenseFSM.state_edit_date_expense:

        id_expense = (await state.get_data())['id_expense_to_edit']

        title_expense = (await state.get_data())['edit_title_expense'] if 'edit_title_expense' in list(await state.get_data()) else (await rq.get_expense_by_id(id_expense)).title_expense
        amount_expense = (await state.get_data())['edit_amount_expense'] if 'edit_amount_expense' in list(await state.get_data()) else (await rq.get_expense_by_id(id_expense)).amount_expense
        date_expense = (await state.get_data())['edit_date_expense'] if 'edit_date_expense' in list(await state.get_data()) else (await rq.get_expense_by_id(id_expense)).date_expense

    # Сбрасываем состояние
    await state.set_state(state=None)

    kb_dict = {f'Категория {title_expense}': f'next_edit_expense!category!{id_expense}',
                f'Сумма {amount_expense}': f'next_edit_expense!amount!{id_expense}',
                f'Дата {date_expense}':f'next_edit_expense!date!{id_expense}',
                'Подтвердить': f'confirm_expense_edit!{id_expense}',
                'Назад': f'{id_expense}!expense_category'}
    keyboard=kb.create_in_kb(1, **kb_dict)
    try:
        # await clb.message.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:',
        #                         reply_markup=kb.keyboards_main_menu())
        await clb.message.edit_text(text=f'Какое поле о записи расхода необходимо изменить?', reply_markup=keyboard)
        await clb.answer()
    except:
        #await hf.process_del_message_messsage(1, bot, clb)
        # await clb.answer(text=f'Вы работаете с мероприятием <b>"{await rq.get_current_event()}"</b>:',
                                # reply_markup=kb.keyboards_main_menu())
        await clb.answer(text=f'Какое поле о записи расхода необходимо изменить?', reply_markup=keyboard)




@router.callback_query(F.data.startswith('confirm_expense_edit!'))
async def process_confirm_edit_expense(clb: CallbackQuery, state: FSMContext, bot: Bot):
    """Подтвердить введенные изменения"""

    logging.info(f'process_confirm_edit_expense --- clb.data = {clb.data}')

    state_data = await state.get_data()
    id_expense = state_data['id_expense_to_edit']
    if 'edit_title_expense' in list(state_data):
        await rq.set_expense(id_expense=id_expense, title_expense=state_data['edit_title_expense'])
    if 'edit_amount_expense' in list(state_data):
        await rq.set_expense(id_expense=id_expense, amount_expense=state_data['edit_amount_expense'])
    if 'edit_date_expense'in (state_data):
        await rq.set_expense(id_expense=id_expense, date_expense=state_data['edit_date_expense'])
    await clb.message.answer(text=f'Расход <b>"{(await rq.get_expense_by_id(id_expense)).title_expense}"</b> успешно обнавлен.')
    await clb.answer()
    await process_edit_expense(clb, state, bot)
