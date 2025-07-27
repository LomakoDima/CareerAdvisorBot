from datetime import datetime
from typing import Dict, List, Any
from database.database_service import db_service


class ProfileService:
    """Сервис для работы с профилями пользователей через SQLite"""

    @staticmethod
    def get_user_profile(user_id: str) -> Dict:
        """Получение профиля пользователя"""
        return db_service.get_user_profile(user_id)

    @staticmethod
    def save_test_result(user_id: str, test_type: str, results: List[Dict], preferences: Dict = None):
        """Сохранение результата теста"""
        db_service.save_test_result(user_id, test_type, results, preferences)

    @staticmethod
    def save_ai_session(user_id: str, session_data: Dict):
        """Сохранение ИИ-сессии"""
        db_service.save_ai_session(user_id, session_data)

    @staticmethod
    def add_to_favorites(user_id: str, profession: Dict) -> bool:
        """Добавление профессии в избранное"""
        return db_service.add_to_favorites(user_id, profession)

    @staticmethod
    def clear_profile(user_id: str):
        """Очистка профиля пользователя"""
        db_service.clear_profile(user_id)

    @staticmethod
    def get_profile_stats(user_id: str) -> str:
        """Получение статистики профиля пользователя"""
        profile = db_service.get_user_profile(user_id)
        stats = profile["stats"]

        top_category = "Пока нет предпочтений"
        if stats["favorite_categories"]:
            top_category = max(stats["favorite_categories"], key=stats["favorite_categories"].get)

        created = datetime.fromisoformat(profile["created_at"])
        days_active = (datetime.now() - created).days

        stats_text = f"""📊 <b>Твоя статистика:</b>

🎯 Пройдено тестов: {stats['total_tests']}
🤖 ИИ-консультаций: {stats['ai_consultations']}
⭐ Избранных профессий: {len(profile['favorites'])}
📅 Дней с нами: {days_active}

🏆 Твоя любимая сфера: {top_category}

💡 Всего сохранено результатов: {len(profile['test_results'])}

🗄️ <b>База данных:</b> SQLite (постоянное хранение)"""

        return stats_text

    @staticmethod
    def get_recent_results(user_id: str, limit: int = 3) -> str:
        """Получение последних результатов тестов"""
        profile = db_service.get_user_profile(user_id)
        results = profile["test_results"][:limit]  # Уже отсортированы по дате

        if not results:
            return "📝 Пока нет пройденных тестов. Пройди первый тест!"

        results_text = "📊 <b>Последние результаты:</b>\n\n"

        for i, result in enumerate(results, 1):
            date = datetime.fromisoformat(result["date"]).strftime("%d.%m.%Y %H:%M")
            test_type = "🤖 ИИ-тест" if result["type"] == "ai" else "📋 Классический"

            results_text += f"{i}. {test_type} ({date})\n"

            for j, prof in enumerate(result["results"][:2], 1):
                results_text += f"   {j}. {prof['name']} ({prof['category']})\n"
            results_text += "\n"

        return results_text

    @staticmethod
    def get_favorites(user_id: str) -> str:
        """Получение избранных профессий"""
        profile = db_service.get_user_profile(user_id)
        favorites = profile["favorites"]

        if not favorites:
            return "⭐ Пока нет избранных профессий.\nДобавляй интересные профессии в результатах тестов!"

        favorites_text = "⭐ <b>Избранные профессии:</b>\n\n"

        for i, fav in enumerate(favorites, 1):
            added_date = datetime.fromisoformat(fav["added_at"]).strftime("%d.%m")
            favorites_text += f"{i}. <b>{fav['name']}</b>\n"
            favorites_text += f"   {fav['category']} | {fav['salary']}\n"
            favorites_text += f"   📅 Добавлено: {added_date}\n\n"

        return favorites_text

    @staticmethod
    def get_database_info() -> str:
        """Информация о базе данных"""
        stats = db_service.get_database_stats()

        return f"""🗄️ <b>Информация о базе данных:</b>

👥 Всего пользователей: {stats['total_users']}
📋 Пройдено тестов: {stats['total_tests']}
🤖 ИИ-консультаций: {stats['total_ai_sessions']}
⭐ Избранных профессий: {stats['total_favorites']}

💾 Тип хранения: SQLite (постоянное)
🔄 Статус: Активна"""

    @staticmethod
    def create_backup() -> str:
        """Создание резервной копии базы данных"""
        backup_path = db_service.backup_database()
        if backup_path:
            return f"✅ Резервная копия создана: {backup_path}"
        else:
            return "❌ Ошибка создания резервной копии"