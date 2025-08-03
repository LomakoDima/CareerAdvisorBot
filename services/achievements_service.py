from typing import Dict, List, Optional
from datetime import datetime
from database.database_service import db_service
import logging

logger = logging.getLogger(__name__)


class AchievementsService:
    ACHIEVEMENTS = {
        "first_test": {
            "name": "🎯 Первый шаг",
            "description": "Пройди свой первый карьерный тест",
            "icon": "🎯",
            "category": "Тестирование",
            "max_progress": 1
        },
        "test_master": {
            "name": "🧠 Мастер тестов",
            "description": "Пройди 10 тестов",
            "icon": "🧠",
            "category": "Тестирование",
            "max_progress": 10
        },
        "test_expert": {
            "name": "🏆 Эксперт тестирования",
            "description": "Пройди 25 тестов",
            "icon": "🏆",
            "category": "Тестирование",
            "max_progress": 25
        },

        "first_ai": {
            "name": "🤖 Первый ИИ-чат",
            "description": "Проведи первую консультацию с ИИ",
            "icon": "🤖",
            "category": "ИИ-консультации",
            "max_progress": 1
        },
        "ai_enthusiast": {
            "name": "💬 Энтузиаст ИИ",
            "description": "Проведи 5 ИИ-консультаций",
            "icon": "💬",
            "category": "ИИ-консультации",
            "max_progress": 5
        },
        "ai_master": {
            "name": "🧠 Мастер ИИ",
            "description": "Проведи 15 ИИ-консультаций",
            "icon": "🧠",
            "category": "ИИ-консультации",
            "max_progress": 15
        },

        "first_favorite": {
            "name": "⭐ Первое избранное",
            "description": "Добавь первую профессию в избранное",
            "icon": "⭐",
            "category": "Избранное",
            "max_progress": 1
        },
        "collector": {
            "name": "📚 Коллекционер",
            "description": "Добавь 5 профессий в избранное",
            "icon": "📚",
            "category": "Избранное",
            "max_progress": 5
        },
        "curator": {
            "name": "🎨 Куратор",
            "description": "Добавь 15 профессий в избранное",
            "icon": "🎨",
            "category": "Избранное",
            "max_progress": 15
        },

        "daily_user": {
            "name": "📅 Ежедневник",
            "description": "Используй бота 7 дней подряд",
            "icon": "📅",
            "category": "Активность",
            "max_progress": 7
        },
        "weekend_warrior": {
            "name": "⚡ Воин выходных",
            "description": "Используй бота 30 дней",
            "icon": "⚡",
            "category": "Активность",
            "max_progress": 30
        },
        "loyal_user": {
            "name": "👑 Лояльный пользователь",
            "description": "Используй бота 100 дней",
            "icon": "👑",
            "category": "Активность",
            "max_progress": 100
        },

        "explorer": {
            "name": "🔍 Исследователь",
            "description": "Попробуй все категории профессий",
            "icon": "🔍",
            "category": "Разнообразие",
            "max_progress": 1
        },
        "salary_hunter": {
            "name": "💰 Охотник за зарплатой",
            "description": "Посмотри профессии всех уровней зарплаты",
            "icon": "💰",
            "category": "Разнообразие",
            "max_progress": 1
        },

        "early_bird": {
            "name": "🐦 Ранняя пташка",
            "description": "Пройди тест до 9 утра",
            "icon": "🐦",
            "category": "Специальные",
            "max_progress": 1
        },
        "night_owl": {
            "name": "🦉 Ночная сова",
            "description": "Пройди тест после 23:00",
            "icon": "🦉",
            "category": "Специальные",
            "max_progress": 1
        },
        "speed_runner": {
            "name": "⚡ Спидраннер",
            "description": "Пройди тест менее чем за 30 секунд",
            "icon": "⚡",
            "category": "Специальные",
            "max_progress": 1
        }
    }

    @staticmethod
    def check_and_unlock_achievement(user_id: str, achievement_id: str, current_progress: int = 1) -> Optional[Dict]:
        if achievement_id not in AchievementsService.ACHIEVEMENTS:
            return None

        achievement_data = AchievementsService.ACHIEVEMENTS[achievement_id]
        max_progress = achievement_data["max_progress"]

        if current_progress >= max_progress:
            success = db_service.unlock_achievement(
                user_id=user_id,
                achievement_id=achievement_id,
                name=achievement_data["name"],
                description=achievement_data["description"],
                icon=achievement_data["icon"],
                category=achievement_data["category"],
                progress=current_progress,
                max_progress=max_progress
            )

            if success:
                return {
                    "achievement_id": achievement_id,
                    "name": achievement_data["name"],
                    "description": achievement_data["description"],
                    "icon": achievement_data["icon"],
                    "category": achievement_data["category"]
                }

        db_service.update_achievement_progress(user_id, achievement_id, current_progress, max_progress)
        return None

    @staticmethod
    def check_test_achievements(user_id: str, total_tests: int) -> List[Dict]:
        unlocked = []

        if total_tests == 1:
            achievement = AchievementsService.check_and_unlock_achievement(user_id, "first_test")
            if achievement:
                unlocked.append(achievement)

        if total_tests >= 10:
            achievement = AchievementsService.check_and_unlock_achievement(user_id, "test_master", total_tests)
            if achievement:
                unlocked.append(achievement)

        if total_tests >= 25:
            achievement = AchievementsService.check_and_unlock_achievement(user_id, "test_expert", total_tests)
            if achievement:
                unlocked.append(achievement)

        return unlocked

    @staticmethod
    def check_ai_achievements(user_id: str, total_ai_sessions: int) -> List[Dict]:
        unlocked = []

        if total_ai_sessions == 1:
            achievement = AchievementsService.check_and_unlock_achievement(user_id, "first_ai")
            if achievement:
                unlocked.append(achievement)

        if total_ai_sessions >= 5:
            achievement = AchievementsService.check_and_unlock_achievement(user_id, "ai_enthusiast", total_ai_sessions)
            if achievement:
                unlocked.append(achievement)

        if total_ai_sessions >= 15:
            achievement = AchievementsService.check_and_unlock_achievement(user_id, "ai_master", total_ai_sessions)
            if achievement:
                unlocked.append(achievement)

        return unlocked

    @staticmethod
    def check_favorites_achievements(user_id: str, total_favorites: int) -> List[Dict]:
        unlocked = []

        if total_favorites == 1:
            achievement = AchievementsService.check_and_unlock_achievement(user_id, "first_favorite")
            if achievement:
                unlocked.append(achievement)

        if total_favorites >= 5:
            achievement = AchievementsService.check_and_unlock_achievement(user_id, "collector", total_favorites)
            if achievement:
                unlocked.append(achievement)

        if total_favorites >= 15:
            achievement = AchievementsService.check_and_unlock_achievement(user_id, "curator", total_favorites)
            if achievement:
                unlocked.append(achievement)

        return unlocked

    @staticmethod
    def check_special_achievements(user_id: str, test_time: datetime = None, test_duration: int = None) -> List[Dict]:
        unlocked = []

        if test_time:
            hour = test_time.hour

            if hour < 9:
                achievement = AchievementsService.check_and_unlock_achievement(user_id, "early_bird")
                if achievement:
                    unlocked.append(achievement)

            if hour >= 23:
                achievement = AchievementsService.check_and_unlock_achievement(user_id, "night_owl")
                if achievement:
                    unlocked.append(achievement)

        if test_duration and test_duration < 30:
            achievement = AchievementsService.check_and_unlock_achievement(user_id, "speed_runner")
            if achievement:
                unlocked.append(achievement)

        return unlocked

    @staticmethod
    def get_user_achievements(user_id: str) -> List[Dict]:
        return db_service.get_user_achievements(user_id)

    @staticmethod
    def get_achievements_stats(user_id: str) -> Dict:
        return db_service.get_achievements_stats(user_id)

    @staticmethod
    def format_achievements_list(achievements: List[Dict]) -> str:
        if not achievements:
            return "🏆 Пока нет достижений.\n\nПройди тесты, используй ИИ-консультации и добавляй профессии в избранное, чтобы получить достижения!"

        text = "🏆 <b>Твои достижения:</b>\n\n"

        categories = {}
        for achievement in achievements:
            category = achievement['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(achievement)

        for category, category_achievements in categories.items():
            text += f"📂 <b>{category}:</b>\n"
            for achievement in category_achievements:
                unlocked_date = datetime.fromisoformat(achievement['unlocked_at']).strftime("%d.%m.%Y")
                text += f"  {achievement['icon']} <b>{achievement['name']}</b>\n"
                text += f"     {achievement['description']}\n"
                text += f"     📅 {unlocked_date}\n\n"

        return text

    @staticmethod
    def format_achievement_notification(achievement: Dict) -> str:
        return f"""🎉 <b>НОВОЕ ДОСТИЖЕНИЕ!</b>

{achievement['icon']} <b>{achievement['name']}</b>
{achievement['description']}

Поздравляем! Ты становишься лучше с каждым днем! 🚀""" 