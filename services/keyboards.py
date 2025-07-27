from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🎯 Пройти тест")],
        [KeyboardButton(text="📊 Топ профессий"), KeyboardButton(text="💰 По зарплате")],
        [KeyboardButton(text="👤 Личный кабинет"), KeyboardButton(text="📚 Полезное")],
        [KeyboardButton(text="ℹ️ О боте")]
    ], resize_keyboard=True)
    return kb


def get_profile_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Мои результаты", callback_data="profile_results")],
        [InlineKeyboardButton(text="📈 Статистика тестов", callback_data="profile_stats")],
        [InlineKeyboardButton(text="⭐ Избранные профессии", callback_data="profile_favorites")],
        [InlineKeyboardButton(text="🗑️ Очистить историю", callback_data="profile_clear")]
    ])
    return kb


def get_mode_selection_kb(ai_available=True):
    buttons = [
        [KeyboardButton(text="📋 Классический тест")]
    ]

    if ai_available:
        buttons.append([KeyboardButton(text="🤖 ИИ-консультант")])
    else:
        buttons.append([KeyboardButton(text="🤖 ИИ-консультант (недоступен)")])

    buttons.append([KeyboardButton(text="⬅️ В главное меню")])

    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
    return kb


def get_ai_chat_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🎯 Получить рекомендации")],
        [KeyboardButton(text="⬅️ К выбору режима")]
    ], resize_keyboard=True)
    return kb


def get_ai_results_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Продолжить беседу", callback_data="ai_continue")],
        [InlineKeyboardButton(text="⭐ Добавить в избранное", callback_data="add_favorite")],
        [InlineKeyboardButton(text="🆕 Новая консультация", callback_data="ai_new_chat")],
        [InlineKeyboardButton(text="💾 Сохранить", callback_data="save")],
        [InlineKeyboardButton(text="🔄 В главное меню", callback_data="restart")]
    ])
    return kb

def get_audience_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👦 Подросток (14-18 лет)")],
        [KeyboardButton(text="👨 Взрослый (18+ лет)")],
        [KeyboardButton(text="⬅️ В главное меню")]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb

def get_interest_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="💻 IT"), KeyboardButton(text="🎨 Искусство")],
        [KeyboardButton(text="💼 Бизнес"), KeyboardButton(text="🏥 Медицина")],
        [KeyboardButton(text="⚙️ Инженерия"), KeyboardButton(text="🏗️ Строительство")],
        [KeyboardButton(text="🍽️ Гостиницы и рестораны"), KeyboardButton(text="✈️ Транспорт")],
        [KeyboardButton(text="📰 Медиа"), KeyboardButton(text="🏫 Образование")],
        [KeyboardButton(text="🚚 Логистика"), KeyboardButton(text="🔧 Техника")],
        [KeyboardButton(text="🌱 Наука"), KeyboardButton(text="🎭 Искусство")],
        [KeyboardButton(text="🌍 Наука"), KeyboardButton(text="🚆 Транспорт")],
        [KeyboardButton(text="🚒 Службы"), KeyboardButton(text="🌳 Сервис")],
        [KeyboardButton(text="🍰 Гостиницы и рестораны"), KeyboardButton(text="⚗️ Наука")],
        [KeyboardButton(text="🏋️ Спорт"), KeyboardButton(text="📬 Сервис")],
        [KeyboardButton(text="🚢 Транспорт"), KeyboardButton(text="🍣 Гостиницы и рестораны")],
        [KeyboardButton(text="⬅️ Назад")]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb

def get_people_tech_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👥 С людьми")],
        [KeyboardButton(text="🔧 С технологиями")],
        [KeyboardButton(text="⬅️ Назад")]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb

def get_risk_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛡️ Стабильность")],
        [KeyboardButton(text="🚀 Готов к риску")],
        [KeyboardButton(text="⬅️ Назад")]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb

def get_final_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Подробнее", callback_data="details")],
        [InlineKeyboardButton(text="⭐ В избранное", callback_data="add_favorite")],
        [InlineKeyboardButton(text="📖 Где учиться", callback_data="courses")],
        [InlineKeyboardButton(text="💾 Сохранить", callback_data="save")],
        [InlineKeyboardButton(text="🔄 Заново", callback_data="restart")]
    ])
    return kb

def get_profession_details_kb(prof_id):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Курсы", callback_data=f"courses_{prof_id}")],
        [InlineKeyboardButton(text="📊 Статистика сферы", callback_data=f"stats_{prof_id}")],
        [InlineKeyboardButton(text="⬅️ К результатам", callback_data="back_to_results")]
    ])
    return kb

def get_top_professions_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 По росту", callback_data="top_growth")],
        [InlineKeyboardButton(text="👥 Для работы с людьми", callback_data="top_people")],
        [InlineKeyboardButton(text="💻 IT-сфера", callback_data="top_it")],
        [InlineKeyboardButton(text="🎨 Творческие", callback_data="top_creative")]
    ])
    return kb

def get_salary_filter_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 50К+", callback_data="salary_50")],
        [InlineKeyboardButton(text="💰 80К+", callback_data="salary_80")],
        [InlineKeyboardButton(text="💰 100К+", callback_data="salary_100")],
        [InlineKeyboardButton(text="📊 Все по убыванию", callback_data="salary_all")]
    ])
    return kb

def get_useful_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Советы по поиску работы", callback_data="job_tips")],
        [InlineKeyboardButton(text="📝 Как составить резюме", callback_data="resume_tips")],
        [InlineKeyboardButton(text="🎓 Бесплатные курсы", callback_data="free_courses")],
        [InlineKeyboardButton(text="🔗 Полезные сайты", callback_data="useful_sites")]
    ])
    return kb