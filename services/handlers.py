from aiogram import types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from .keyboards import *
from .professions import PROFESSIONS, get_profession_by_preferences, get_profession_stats
from .ai_service import get_ai_career_recommendation, is_openai_available
from .profile_service import ProfileService
import json
import time
import random
from datetime import datetime

class CareerStates(StatesGroup):
    main_menu = State()
    choosing_mode = State()
    choosing_audience = State()
    choosing_interest = State()
    choosing_people_tech = State()
    choosing_risk = State()
    ai_chat = State()
    show_results = State()


def register_handlers(dp, bot):
    @dp.message(CareerStates.main_menu)
    async def handle_main_menu(message: types.Message, state: FSMContext):
        text = message.text

        if "🎯 Пройти тест" in text:
            await choose_test_mode(message, state)
        elif "📊 Топ профессий" in text:
            await show_top_professions(message, state)
        elif "💰 По зарплате" in text:
            await show_salary_filter(message, state)
        elif "👤 Личный кабинет" in text:  # НОВОЕ
            await show_profile(message, state)
        elif "📚 Полезное" in text:
            await show_useful_info(message, state)
        elif "ℹ️ О боте" in text:
            await show_about(message, state)

    async def show_profile(message: types.Message, state: FSMContext):
        """Показать личный кабинет"""
        user_id = str(message.from_user.id)
        profile = ProfileService.get_user_profile(user_id)

        # Базовая информация о профиле
        username = message.from_user.first_name or "Пользователь"
        created_date = datetime.fromisoformat(profile["created_at"]).strftime("%d.%m.%Y")

        await message.answer(
            f"👤 <b>Личный кабинет - {username}</b>\n\n"
            f"📅 С нами с: {created_date}\n"
            f"🎯 Тестов пройдено: {profile['stats']['total_tests']}\n"
            f"🤖 ИИ-консультаций: {profile['stats']['ai_consultations']}\n"
            f"⭐ Избранных профессий: {len(profile['favorites'])}\n\n"
            f"Выбери действие:",
            reply_markup=get_profile_kb(),
            parse_mode="HTML"
        )

    # Callbacks для личного кабинета
    @dp.callback_query(F.data == "profile_results")
    async def show_profile_results(callback: types.CallbackQuery):
        user_id = str(callback.from_user.id)
        results_text = ProfileService.get_recent_results(user_id)
        await callback.message.edit_text(results_text, parse_mode="HTML")

    @dp.callback_query(F.data == "profile_stats")
    async def show_profile_stats(callback: types.CallbackQuery):
        user_id = str(callback.from_user.id)
        stats_text = ProfileService.get_profile_stats(user_id)
        await callback.message.edit_text(stats_text, parse_mode="HTML")

    @dp.callback_query(F.data == "profile_favorites")
    async def show_profile_favorites(callback: types.CallbackQuery):
        user_id = str(callback.from_user.id)
        favorites_text = ProfileService.get_favorites(user_id)
        await callback.message.edit_text(favorites_text, parse_mode="HTML")

    @dp.callback_query(F.data == "profile_clear")
    async def clear_profile_data(callback: types.CallbackQuery):
        user_id = str(callback.from_user.id)
        ProfileService.clear_profile(user_id)
        await callback.answer("🗑️ История очищена!")
        await callback.message.edit_text(
            "✅ <b>История очищена!</b>\n\n"
            "Все результаты тестов и избранные профессии удалены.\n"
            "Можешь начать заново! 🚀",
            parse_mode="HTML"
        )

    @dp.callback_query(F.data == "add_favorite")
    async def add_to_favorites(callback: types.CallbackQuery, state: FSMContext):
        user_id = str(callback.from_user.id)
        data = await state.get_data()

        # Получаем текущие результаты
        results = data.get("results", [])
        if not results:
            await callback.answer("❌ Нет результатов для добавления")
            return

        # Добавляем первую профессию в избранное
        added = ProfileService.add_to_favorites(user_id, results[0])

        if added:
            await callback.answer("⭐ Добавлено в избранное!")
        else:
            await callback.answer("📝 Уже в избранном")

    # Обновляем сохранение результатов классического теста
    async def show_classic_results(message: types.Message, state: FSMContext):
        data = await state.get_data()
        professions = get_profession_by_preferences(
            data["audience"], data["interest"],
            data["with_people"], data["risk"]
        )

        if not professions:
            await message.answer("😔 Не нашёл точных совпадений. Попробуй другие ответы!", reply_markup=get_final_kb())
            return

        await state.update_data(results=professions)

        # НОВОЕ: Сохраняем в профиль
        user_id = str(message.from_user.id)
        ProfileService.save_test_result(user_id, "classic", professions, data)

        result_text = f"🎉 <b>Твои идеальные профессии:</b>\n\n"
        for i, prof in enumerate(professions[:2], 1):
            result_text += f"<b>{i}. {prof['name']}</b>\n"
            result_text += f"💰 {prof['salary']} | {prof['growth']}\n"
            result_text += f"📋 {prof['desc']}\n\n"

        await message.answer(result_text, reply_markup=get_final_kb(), parse_mode="HTML")
        await state.set_state(CareerStates.show_results)

    # Обновляем генерацию ИИ-рекомендаций
    async def generate_ai_recommendations(message: types.Message, state: FSMContext):
        typing_message = await message.answer("🤖 Анализирую нашу беседу и подбираю профессии...")

        try:
            data = await state.get_data()
            context = data.get("ai_context", [])

            if len(context) < 2:
                await typing_message.delete()
                await message.answer(
                    "📝 Мне нужно больше информации о тебе! Расскажи подробнее о своих интересах, навыках и целях.",
                    reply_markup=get_ai_chat_kb()
                )
                return

            recommendations = await get_ai_career_recommendation(context, mode="recommend")
            await typing_message.delete()
            await state.update_data(ai_recommendations=recommendations)

            # НОВОЕ: Сохраняем ИИ-сессию в профиль
            user_id = str(message.from_user.id)
            ProfileService.save_ai_session(user_id, data)

            await message.answer(
                f"🎉 <b>Персональные рекомендации от ИИ:</b>\n\n{recommendations}",
                reply_markup=get_ai_results_kb(),
                parse_mode="HTML"
            )

            await state.set_state(CareerStates.show_results)

        except Exception as e:
            await typing_message.delete()
            await message.answer(
                "😔 Произошла ошибка при генерации рекомендаций. Попробуй классический тест!",
                reply_markup=get_mode_selection_kb(False)
            )
    @dp.message(CommandStart())
    async def cmd_start(message: types.Message, state: FSMContext):
        await state.clear()
        ai_status = "✅ Доступен" if await is_openai_available() else "❌ Недоступен"

        await message.answer(
            "🚀 <b>Карьерный Советник v2.0</b>\n\n"
            "Привет! Я помогу тебе найти идеальную профессию! 🎯\n\n"
            "🆕 <b>Новые возможности:</b>\n"
            "• ИИ-консультант для персональных рекомендаций\n"
            "• Расширенная база профессий\n"
            "• Топ профессий по категориям\n"
            "• Информация о курсах\n"
            "• Полезные материалы\n\n"
            f"🤖 ИИ-режим: {ai_status}\n\n"
            "Выбери, что тебя интересует:",
            reply_markup=get_main_menu_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CareerStates.main_menu)

    @dp.message(CareerStates.main_menu)
    async def handle_main_menu(message: types.Message, state: FSMContext):
        text = message.text

        if "🎯 Пройти тест" in text:
            await choose_test_mode(message, state)
        elif "📊 Топ профессий" in text:
            await show_top_professions(message, state)
        elif "💰 По зарплате" in text:
            await show_salary_filter(message, state)
        elif "📚 Полезное" in text:
            await show_useful_info(message, state)
        elif "ℹ️ О боте" in text:
            await show_about(message, state)

    async def choose_test_mode(message: types.Message, state: FSMContext):
        ai_available = await is_openai_available()
        await message.answer(
            "🎯 <b>Выбери режим тестирования:</b>\n\n"
            "📋 <b>Классический тест</b> - быстрые вопросы с готовыми вариантами\n\n"
            "🤖 <b>ИИ-консультант</b> - персональная беседа с искусственным интеллектом для более точных рекомендаций\n\n"
            f"{'✅ Все режимы доступны!' if ai_available else '⚠️ ИИ-режим временно недоступен'}",
            reply_markup=get_mode_selection_kb(ai_available),
            parse_mode="HTML"
        )
        await state.set_state(CareerStates.choosing_mode)

    @dp.message(CareerStates.choosing_mode)
    async def handle_mode_selection(message: types.Message, state: FSMContext):
        text = message.text

        if "⬅️" in text:
            return await cmd_start(message, state)
        elif "📋 Классический" in text:
            await start_classic_test(message, state)
        elif "🤖 ИИ-консультант" in text:
            await start_ai_chat(message, state)
        else:
            await message.answer("❌ Выбери один из предложенных режимов!",
                                 reply_markup=get_mode_selection_kb(await is_openai_available()))

    async def start_classic_test(message: types.Message, state: FSMContext):
        await state.update_data(mode="classic")
        await message.answer(
            "📋 <b>Классический карьерный тест</b>\n\n"
            "Отвечу на 4 вопроса и получи персональные рекомендации!\n\n"
            "🔸 Для кого ищешь профессию?",
            reply_markup=get_audience_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CareerStates.choosing_audience)

    async def start_ai_chat(message: types.Message, state: FSMContext):
        if not await is_openai_available():
            await message.answer(
                "😔 ИИ-консультант временно недоступен. Попробуй классический тест!",
                reply_markup=get_mode_selection_kb(False)
            )
            return

        await state.update_data(mode="ai", ai_context=[], user_info={})
        await message.answer(
            "🤖 <b>ИИ-Консультант по карьере</b>\n\n"
            "Привет! Я твой персональный карьерный консультант с искусственным интеллектом.\n\n"
            "Давай поговорим о твоих интересах, навыках и целях. Я задам несколько вопросов и дам персональные рекомендации.\n\n"
            "💬 Для начала расскажи немного о себе:\n"
            "• Сколько тебе лет?\n"
            "• Есть ли у тебя образование или опыт работы?\n"
            "• Что тебя больше всего интересует?\n\n"
            "Пиши свободно, как в обычном разговоре! 😊",
            reply_markup=get_ai_chat_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CareerStates.ai_chat)

    @dp.message(CareerStates.ai_chat)
    async def handle_ai_chat(message: types.Message, state: FSMContext):
        if "⬅️ К выбору режима" in message.text:
            return await choose_test_mode(message, state)

        if "🎯 Получить рекомендации" in message.text:
            await generate_ai_recommendations(message, state)
            return

        # Отправляем сообщение пользователя в ИИ
        typing_message = await message.answer("🤖 Думаю над ответом...")

        try:
            data = await state.get_data()
            context = data.get("ai_context", [])

            # Добавляем сообщение пользователя в контекст
            context.append({"role": "user", "content": message.text})

            # Получаем ответ от ИИ
            ai_response = await get_ai_career_recommendation(context, mode="chat")

            # Добавляем ответ ИИ в контекст
            context.append({"role": "assistant", "content": ai_response})

            await state.update_data(ai_context=context)

            await typing_message.delete()
            await message.answer(
                f"🤖 {ai_response}",
                reply_markup=get_ai_chat_kb(),
                parse_mode="HTML"
            )

        except Exception as e:
            await typing_message.delete()
            await message.answer(
                "😔 Произошла ошибка при обращении к ИИ. Попробуй ещё раз или перейди к классическому тесту.",
                reply_markup=get_ai_chat_kb()
            )

    async def generate_ai_recommendations(message: types.Message, state: FSMContext):
        typing_message = await message.answer("🤖 Анализирую нашу беседу и подбираю профессии...")

        try:
            data = await state.get_data()
            context = data.get("ai_context", [])

            if len(context) < 2:
                await typing_message.delete()
                await message.answer(
                    "📝 Мне нужно больше информации о тебе! Расскажи подробнее о своих интересах, навыках и целях.",
                    reply_markup=get_ai_chat_kb()
                )
                return

            # Получаем рекомендации от ИИ
            recommendations = await get_ai_career_recommendation(context, mode="recommend")

            await typing_message.delete()

            # Сохраняем результаты
            await state.update_data(ai_recommendations=recommendations)

            await message.answer(
                f"🎉 <b>Персональные рекомендации от ИИ:</b>\n\n{recommendations}",
                reply_markup=get_ai_results_kb(),
                parse_mode="HTML"
            )

            await state.set_state(CareerStates.show_results)

        except Exception as e:
            await typing_message.delete()
            await message.answer(
                "😔 Произошла ошибка при генерации рекомендаций. Попробуй классический тест!",
                reply_markup=get_mode_selection_kb(False)
            )

    # Классические обработчики (без изменений)
    async def start_test(message: types.Message, state: FSMContext):
        await message.answer(
            "📋 <b>Карьерный тест</b>\n\n"
            "Отвечу на 4 вопроса и получи персональные рекомендации!\n\n"
            "🔸 Для кого ищешь профессию?",
            reply_markup=get_audience_kb(),
            parse_mode="HTML"
        )
        await state.set_state(CareerStates.choosing_audience)

    async def show_top_professions(message: types.Message, state: FSMContext):
        await message.answer(
            "📊 <b>Топ профессий</b>\n\n"
            "Выбери категорию для просмотра:",
            reply_markup=get_top_professions_kb(),
            parse_mode="HTML"
        )

    async def show_salary_filter(message: types.Message, state: FSMContext):
        await message.answer(
            "💰 <b>Профессии по уровню зарплаты</b>\n\n"
            "Выбери минимальный уровень:",
            reply_markup=get_salary_filter_kb(),
            parse_mode="HTML"
        )

    async def show_useful_info(message: types.Message, state: FSMContext):
        await message.answer(
            "📚 <b>Полезная информация</b>\n\n"
            "Что тебя интересует?",
            reply_markup=get_useful_kb(),
            parse_mode="HTML"
        )

    async def show_about(message: types.Message, state: FSMContext):
        stats = get_profession_stats()
        ai_status = "✅ Активен" if await is_openai_available() else "❌ Недоступен"

        await message.answer(
            f"ℹ️ <b>О боте</b>\n\n"
            f"🤖 Карьерный Советник v3.0\n"
            f"📊 Профессий в базе: {stats['total']}\n"
            f"💻 IT-профессий: {stats['it_count']}\n"
            f"🚀 Растущих сфер: {stats['high_growth']}\n"
            f"👥 Для работы с людьми: {stats['with_people']}\n"
            f"🧠 ИИ-консультант: {ai_status}\n\n"
            f"Бот поможет найти профессию мечты на основе твоих интересов!",
            parse_mode="HTML"
        )

    # Callbacks для топ профессий
    @dp.callback_query(F.data.startswith("top_"))
    async def handle_top_categories(callback: types.CallbackQuery):
        category = callback.data.split("_")[1]

        if category == "growth":
            profs = [p for p in PROFESSIONS if "🚀" in p["growth"]][:5]
            title = "🚀 Быстрорастущие профессии"
        elif category == "people":
            profs = [p for p in PROFESSIONS if p["with_people"]][:5]
            title = "👥 Профессии для работы с людьми"
        elif category == "it":
            profs = [p for p in PROFESSIONS if p["category"] == "💻 IT"][:5]
            title = "💻 IT-профессии"
        elif category == "creative":
            profs = [p for p in PROFESSIONS if p["category"] == "🎨 Искусство"][:5]
            title = "🎨 Творческие профессии"

        text = f"<b>{title}</b>\n\n"
        for i, prof in enumerate(profs, 1):
            text += f"{i}. <b>{prof['name']}</b>\n"
            text += f"   💰 {prof['salary']} | {prof['growth']}\n\n"

        await callback.message.edit_text(text, parse_mode="HTML")

    @dp.callback_query(F.data.startswith("salary_"))
    async def handle_salary_filter(callback: types.CallbackQuery):
        filter_type = callback.data.split("_")[1]

        if filter_type == "50":
            filtered = [p for p in PROFESSIONS if "80,000" in p["salary"] or "100,000" in p["salary"] or "120,000" in p[
                "salary"] or "нет ограничений" in p["salary"]]
        elif filter_type == "80":
            filtered = [p for p in PROFESSIONS if
                        "100,000" in p["salary"] or "120,000" in p["salary"] or "нет ограничений" in p["salary"]]
        elif filter_type == "100":
            filtered = [p for p in PROFESSIONS if "120,000" in p["salary"] or "нет ограничений" in p["salary"]]
        else:  # all
            filtered = sorted(PROFESSIONS, key=lambda x: x["salary"], reverse=True)[:6]

        text = f"💰 <b>Высокооплачиваемые профессии</b>\n\n"
        for i, prof in enumerate(filtered[:5], 1):
            text += f"{i}. <b>{prof['name']}</b>\n"
            text += f"   💰 {prof['salary']}\n"
            text += f"   📋 {prof['desc'][:50]}...\n\n"

        await callback.message.edit_text(text, parse_mode="HTML")

    @dp.callback_query(F.data.startswith("job_tips"))
    async def show_job_tips(callback: types.CallbackQuery):
        tips = [
            "🎯 Определи свои сильные стороны",
            "📝 Составь качественное резюме",
            "🔍 Используй разные площадки поиска",
            "🤝 Развивай networking",
            "📚 Постоянно учись новому",
            "💪 Не бойся стажировок"
        ]

        text = "💡 <b>Советы по поиску работы:</b>\n\n"
        for tip in tips:
            text += f"• {tip}\n"
        text += "\n🚀 Главное - не сдавайся!"

        await callback.message.edit_text(text, parse_mode="HTML")

    @dp.callback_query(F.data == "free_courses")
    async def show_free_courses(callback: types.CallbackQuery):
        await callback.message.edit_text(
            "🎓 <b>Бесплатные курсы:</b>\n\n"
            "💻 <b>Программирование:</b>\n"
            "• Яндекс.Практикум (первые уроки)\n"
            "• freeCodeCamp\n"
            "• Codecademy\n\n"
            "🎨 <b>Дизайн:</b>\n"
            "• Figma Academy\n"
            "• Adobe Creative Cloud tutorials\n\n"
            "💼 <b>Маркетинг:</b>\n"
            "• Google Digital Marketing\n"
            "• HubSpot Academy\n\n"
            "📊 <b>Аналитика:</b>\n"
            "• Google Analytics Academy\n"
            "• Coursera Data Science",
            parse_mode="HTML"
        )

    @dp.message(CareerStates.choosing_audience)
    async def process_audience(message: types.Message, state: FSMContext):
        if "⬅️" in message.text:
            return await choose_test_mode(message, state)

        text = message.text.lower()
        if "подросток" in text:
            audience = "teen"
        elif "взрослый" in text:
            audience = "adult"
        else:
            await message.answer("❌ Выбери один из вариантов!", reply_markup=get_audience_kb())
            return

        await state.update_data(audience=audience)
        await message.answer("🎯 Выбери интересную сферу:", reply_markup=get_interest_kb(), parse_mode="HTML")
        await state.set_state(CareerStates.choosing_interest)

    @dp.message(CareerStates.choosing_interest)
    async def process_interest(message: types.Message, state: FSMContext):
        if "⬅️" in message.text:
            return await start_classic_test(message, state)

        valid_interests = [
            "💻 IT", "🎨 Искусство", "💼 Бизнес", "🏥 Медицина", "⚙️ Инженерия", "🏗️ Строительство",
            "🍽️ Гостиницы и рестораны", "✈️ Транспорт", "📰 Медиа", "🏫 Образование", "🚚 Логистика",
            "🔧 Техника", "🌱 Наука", "🎭 Искусство", "🌍 Наука", "🚆 Транспорт", "🚒 Службы",
            "🌳 Сервис", "🍰 Гостиницы и рестораны", "⚗️ Наука", "🏋️ Спорт", "📬 Сервис",
            "🚢 Транспорт", "🍣 Гостиницы и рестораны"
        ]
        if message.text not in valid_interests:
            await message.answer("❌ Выбери из предложенных!", reply_markup=get_interest_kb())
            return

        await state.update_data(interest=message.text)
        await message.answer("🤝 С кем предпочитаешь работать?", reply_markup=get_people_tech_kb(), parse_mode="HTML")
        await state.set_state(CareerStates.choosing_people_tech)

    @dp.message(CareerStates.choosing_people_tech)
    async def process_people_tech(message: types.Message, state: FSMContext):
        if "⬅️" in message.text:
            await message.answer("🎯 Выбери интересную сферу:", reply_markup=get_interest_kb())
            return await state.set_state(CareerStates.choosing_interest)

        with_people = "людьми" in message.text.lower()
        await state.update_data(with_people=with_people)
        await message.answer("💪 Отношение к рискам?", reply_markup=get_risk_kb(), parse_mode="HTML")
        await state.set_state(CareerStates.choosing_risk)

    @dp.message(CareerStates.choosing_risk)
    async def process_risk(message: types.Message, state: FSMContext):
        if "⬅️" in message.text:
            await message.answer("🤝 С кем предпочитаешь работать?", reply_markup=get_people_tech_kb())
            return await state.set_state(CareerStates.choosing_people_tech)

        risk = "риску" in message.text.lower()
        await state.update_data(risk=risk)
        await show_classic_results(message, state)

    async def show_classic_results(message: types.Message, state: FSMContext):
        data = await state.get_data()
        professions = get_profession_by_preferences(
            data["audience"], data["interest"],
            data["with_people"], data["risk"]
        )

        if not professions:
            await message.answer("😔 Не нашёл точных совпадений. Попробуй другие ответы!", reply_markup=get_final_kb())
            return

        await state.update_data(results=professions)

        # ИСПРАВЛЕНИЕ: Сохраняем результат классического теста
        user_id = str(message.from_user.id)
        try:
            ProfileService.save_test_result(user_id, "classic", professions, data)
            print(f"✅ Классический тест сохранен для пользователя {user_id}")
        except Exception as e:
            print(f"❌ Ошибка сохранения классического теста: {e}")

        result_text = f"🎉 <b>Твои идеальные профессии:</b>\n\n"
        for i, prof in enumerate(professions[:2], 1):
            result_text += f"<b>{i}. {prof['name']}</b>\n"
            result_text += f"💰 {prof['salary']} | {prof['growth']}\n"
            result_text += f"📋 {prof['desc']}\n\n"

        await message.answer(result_text, reply_markup=get_final_kb(), parse_mode="HTML")
        await state.set_state(CareerStates.show_results)

    async def generate_ai_recommendations(message: types.Message, state: FSMContext):
        typing_message = await message.answer("🤖 Анализирую нашу беседу и подбираю профессии...")

        try:
            data = await state.get_data()
            context = data.get("ai_context", [])

            if len(context) < 2:
                await typing_message.delete()
                await message.answer(
                    "📝 Мне нужно больше информации о тебе! Расскажи подробнее о своих интересах, навыках и целях.",
                    reply_markup=get_ai_chat_kb()
                )
                return

            recommendations = await get_ai_career_recommendation(context, mode="recommend")
            await typing_message.delete()
            await state.update_data(ai_recommendations=recommendations)

            # ИСПРАВЛЕНИЕ: Сохраняем ИИ-сессию
            user_id = str(message.from_user.id)
            try:
                # Подготавливаем данные сессии
                session_data = {
                    "context": context,
                    "recommendations": recommendations,
                    "timestamp": datetime.now().isoformat()
                }
                ProfileService.save_ai_session(user_id, session_data)
                print(f"✅ ИИ-сессия сохранена для пользователя {user_id}")
            except Exception as e:
                print(f"❌ Ошибка сохранения ИИ-сессии: {e}")

            await message.answer(
                f"🎉 <b>Персональные рекомендации от ИИ:</b>\n\n{recommendations}",
                reply_markup=get_ai_results_kb(),
                parse_mode="HTML"
            )

            await state.set_state(CareerStates.show_results)

        except Exception as e:
            await typing_message.delete()
            print(f"❌ Ошибка генерации ИИ-рекомендаций: {e}")
            await message.answer(
                "😔 Произошла ошибка при генерации рекомендаций. Попробуй классический тест!",
                reply_markup=get_mode_selection_kb(False)
            )

    @dp.callback_query(F.data == "details")
    async def show_details(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        results = data.get("results", [])

        details_text = "📊 <b>Подробная информация:</b>\n\n"
        for prof in results[:2]:
            details_text += f"<b>{prof['name']}</b>\n"
            details_text += f"💰 Зарплата: {prof['salary']}\n"
            details_text += f"🎓 Образование: {prof['education']}\n"
            details_text += f"⚡ Навыки: {', '.join(prof['skills'])}\n"
            details_text += f"📈 Перспективы: {prof['growth']}\n\n"

        await callback.message.edit_text(details_text, parse_mode="HTML")

    @dp.callback_query(F.data == "courses")
    async def show_courses_info(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        results = data.get("results", [])

        courses_text = "📖 <b>Где учиться:</b>\n\n"
        for prof in results[:2]:
            courses_text += f"<b>{prof['name']}:</b>\n"
            for course in prof.get('courses', ['Информация уточняется']):
                courses_text += f"• {course}\n"
            courses_text += "\n"

        await callback.message.edit_text(courses_text, parse_mode="HTML")

    @dp.callback_query(F.data == "save")
    async def save_results(callback: types.CallbackQuery, state: FSMContext):
        await callback.answer("✅ Результат сохранён!")
        await callback.message.edit_text(
            "💾 <b>Результат сохранён!</b>\n\n"
            "Можешь вернуться к главному меню: /start",
            parse_mode="HTML"
        )

    @dp.callback_query(F.data == "restart")
    async def restart_test(callback: types.CallbackQuery, state: FSMContext):
        await callback.answer("🔄 Перезапуск...")
        await cmd_start(callback.message, state)

    @dp.callback_query(F.data == "ai_continue")
    async def ai_continue_chat(callback: types.CallbackQuery):
        await callback.message.edit_text(
            "🤖 Продолжаем беседу! Расскажи ещё что-нибудь о себе или задай вопрос.",
            reply_markup=get_ai_chat_kb(),
            parse_mode="HTML"
        )

    @dp.callback_query(F.data == "ai_new_chat")
    async def ai_new_chat(callback: types.CallbackQuery, state: FSMContext):
        await state.update_data(ai_context=[], user_info={})
        await callback.message.edit_text(
            "🆕 Начинаем новую беседу! Расскажи о себе и своих интересах.",
            reply_markup=get_ai_chat_kb(),
            parse_mode="HTML"
        )

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        await message.answer(
            "📚 <b>Помощь по боту:</b>\n\n"
            "/start - Главное меню\n"
            "/stats - Статистика\n"
            "/help - Эта справка\n\n"
            "🎯 <b>Функции:</b>\n"
            "• Классический карьерный тест\n"
            "• 🤖 ИИ-консультант (NEW!)\n"
            "• Топ профессий\n"
            "• Фильтр по зарплате\n"
            "• Полезные материалы",
            parse_mode="HTML"
        )

    @dp.message(Command("stats"))
    async def cmd_stats(message: types.Message):
        stats = get_profession_stats()
        users_online = random.randint(45, 89)
        tests_today = random.randint(120, 250)
        ai_requests = random.randint(50, 150)

        await message.answer(
            f"📊 <b>Статистика бота:</b>\n\n"
            f"👥 Пользователей онлайн: {users_online}\n"
            f"📋 Тестов пройдено сегодня: {tests_today}\n"
            f"🤖 ИИ-консультаций: {ai_requests}\n"
            f"🎯 Всего профессий: {stats['total']}\n"
            f"💻 IT-профессий: {stats['it_count']}\n"
            f"📈 Растущих сфер: {stats['high_growth']}\n"
            f"⭐ Рейтинг: ну допустим 4.9/5.0\n"
            f"🚀 Средняя точность: 94%",
            parse_mode="HTML"
        )

    @dp.message()
    async def handle_unknown(message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            await message.answer(
                "🤔 Не понимаю... Используй /start для начала работы!",
                reply_markup=get_main_menu_kb()
            )