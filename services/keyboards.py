from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_audience_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👦 Подросток (14-18 лет)")],
        [KeyboardButton(text="👨 Взрослый (18+ лет)")]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb

def get_interest_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="💻 IT"), KeyboardButton(text="🎨 Искусство")],
        [KeyboardButton(text="💼 Бизнес"), KeyboardButton(text="🏥 Медицина")],
        [KeyboardButton(text="⚙️ Инженерия"), KeyboardButton(text="🏗️ Строительство")]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb

def get_people_tech_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👥 С людьми")],
        [KeyboardButton(text="🔧 С технологиями")]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb

def get_risk_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛡️ Стабильность")],
        [KeyboardButton(text="🚀 Готов к риску")]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb

def get_final_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 Сохранить результат", callback_data="save")],
        [InlineKeyboardButton(text="🔄 Пройти заново", callback_data="restart")],
        [InlineKeyboardButton(text="ℹ️ Подробнее о профессии", callback_data="details")]
    ])
    return kb

def get_back_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="⬅️ Назад")]
    ], resize_keyboard=True)
    return kb