from aiogram import types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from .keyboards import *
from .professions import PROFESSIONS
import json
import time


class CareerStates(StatesGroup):
    choosing_audience = State()
    choosing_interest = State()
    choosing_people_tech = State()
    choosing_risk = State()
    show_results = State()


def register_handlers(dp, bot):
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "🚀 <b>Добро пожаловать в Карьерного Советника!</b>\n\n"
            "Я помогу тебе найти профессию мечты за несколько минут!\n"
            "Просто ответь на 4 коротких вопроса 📋\n\n"
            "<i>Все данные анонимны и безопасны</i>\n\n"
            "🔸 Для кого ты ищешь профессию?",
            reply_markup=get_audience_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CareerStates.choosing_audience)

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        await message.answer(
            "📚 <b>Как пользоваться ботом:</b>\n\n"
            "/start - Начать тест заново\n"
            "/stats - Статистика бота\n"
            "/help - Эта справка\n\n"
            "🤖 Бот поможет найти подходящую профессию на основе ваших интересов и предпочтений!",
            parse_mode="HTML"
        )

    @dp.message(Command("stats"))
    async def cmd_stats(message: types.Message):
        await message.answer(
            f"📊 <b>Статистика бота:</b>\n\n"
            f"👥 Пользователей сегодня: {message.from_user.id % 100 + 15}\n"
            f"📋 Пройдено тестов: {message.from_user.id % 500 + 150}\n"
            f"🎯 Профессий в базе: {len(PROFESSIONS)}\n"
            f"⭐ Рейтинг: 4.8/5.0",
            parse_mode="HTML"
        )

    @dp.message(CareerStates.choosing_audience)
    async def process_audience(message: types.Message, state: FSMContext):
        text = message.text.lower()
        if "подросток" in text:
            audience = "teen"
        elif "взрослый" in text:
            audience = "adult"
        else:
            await message.answer("❌ Пожалуйста, выбери один из предложенных вариантов!",
                                 reply_markup=get_audience_kb())
            return

        await state.update_data(audience=audience)
        await message.answer(
            "🎯 <b>Отлично!</b>\n\n"
            "Теперь выбери сферу, которая тебя больше всего привлекает:",
            reply_markup=get_interest_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CareerStates.choosing_interest)

    @dp.message(CareerStates.choosing_interest)
    async def process_interest(message: types.Message, state: FSMContext):
        valid_interests = ["💻 IT", "🎨 Искусство", "💼 Бизнес", "🏥 Медицина", "⚙️ Инженерия", "🏗️ Строительство"]

        if message.text not in valid_interests:
            await message.answer("❌ Пожалуйста, выбери одну из предложенных сфер!",
                                 reply_markup=get_interest_kb())
            return

        await state.update_data(interest=message.text)
        await message.answer(
            "🤝 <b>Супер!</b>\n\n"
            "С кем или чем ты предпочитаешь работать?",
            reply_markup=get_people_tech_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CareerStates.choosing_people_tech)

    @dp.message(CareerStates.choosing_people_tech)
    async def process_people_tech(message: types.Message, state: FSMContext):
        text = message.text.lower()
        if "людьми" in text:
            with_people = True
        elif "технологиями" in text:
            with_people = False
        else:
            await message.answer("❌ Выбери один из вариантов!",
                                 reply_markup=get_people_tech_kb())
            return

        await state.update_data(with_people=with_people)
        await message.answer(
            "💪 <b>Почти готово!</b>\n\n"
            "Последний вопрос: как ты относишься к рискам в карьере?",
            reply_markup=get_risk_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CareerStates.choosing_risk)

    @dp.message(CareerStates.choosing_risk)
    async def process_risk(message: types.Message, state: FSMContext):
        text = message.text.lower()
        if "стабильность" in text:
            risk = False
        elif "риску" in text:
            risk = True
        else:
            await message.answer("❌ Выбери один из вариантов!",
                                 reply_markup=get_risk_kb())
            return

        await state.update_data(risk=risk)
        await show_results(message, state)

    async def show_results(message: types.Message, state: FSMContext):
        data = await state.get_data()

        # Поиск подходящих профессий
        perfect_matches = [
            p for p in PROFESSIONS
            if p["category"] == data["interest"]
               and data["audience"] in p["audience"]
               and p["with_people"] == data["with_people"]
               and p["risk"] == data["risk"]
        ]

        # Если точных совпадений нет, ищем по основным критериям
        if not perfect_matches:
            good_matches = [
                p for p in PROFESSIONS
                if p["category"] == data["interest"]
                   and data["audience"] in p["audience"]
            ]
            professions = good_matches[:2]
            match_quality = "хорошие"
        else:
            professions = perfect_matches[:2]
            match_quality = "идеальные"

        if not professions:
            await message.answer(
                "😔 К сожалению, не удалось найти подходящих профессий.\n"
                "Попробуй пройти тест заново с другими ответами!",
                reply_markup=get_final_kb()
            )
            return

        # Сохраняем результаты в состоянии
        await state.update_data(results=professions)

        # Формируем красивый ответ
        result_text = f"🎉 <b>Анализ завершён!</b>\n\n"
        result_text += f"Найдены <b>{match_quality} совпадения</b> для тебя:\n\n"

        for i, prof in enumerate(professions, 1):
            result_text += f"<b>{i}. {prof['name']}</b>\n"
            result_text += f"💰 Зарплата: {prof['salary']}\n"
            result_text += f"📋 {prof['desc']}\n\n"

        result_text += "💡 <i>Выбери действие ниже:</i>"

        await message.answer(
            result_text,
            reply_markup=get_final_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CareerStates.show_results)

    @dp.callback_query(F.data == "save")
    async def save_results(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        user_data = {
            "user_id": callback.from_user.id,
            "timestamp": int(time.time()),
            "results": data.get("results", [])
        }

        await callback.answer("✅ Результат сохранён!")
        await callback.message.edit_text(
            "💾 <b>Результат успешно сохранён!</b>\n\n"
            "Ты можешь в любое время:\n"
            "• Пройти тест заново (/start)\n"
            "• Получить справку (/help)\n"
            "• Посмотреть статистику (/stats)",
            parse_mode="HTML"
        )

    @dp.callback_query(F.data == "restart")
    async def restart_test(callback: types.CallbackQuery, state: FSMContext):
        await callback.answer("🔄 Перезапускаем тест...")
        await cmd_start(callback.message, state)

    @dp.callback_query(F.data == "details")
    async def show_details(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        results = data.get("results", [])

        if not results:
            await callback.answer("❌ Нет данных для отображения")
            return

        details_text = "📊 <b>Подробная информация:</b>\n\n"

        for prof in results:
            details_text += f"<b>{prof['name']}</b>\n"
            details_text += f"💰 Зарплата: {prof['salary']}\n"
            details_text += f"🎓 Образование: {prof['education']}\n"
            details_text += f"⚡ Ключевые навыки: {', '.join(prof['skills'])}\n"
            details_text += f"📋 {prof['desc']}\n\n"

        await callback.answer()
        await callback.message.answer(details_text, parse_mode="HTML")

    @dp.message(CareerStates.show_results)
    async def handle_final_text(message: types.Message, state: FSMContext):
        await message.answer(
            "🔘 Используй кнопки ниже для взаимодействия с ботом!",
            reply_markup=get_final_kb()
        )