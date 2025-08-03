

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.achievements_service import AchievementsService
from database.database_service import db_service
from datetime import datetime

def test_achievements():
    print("🧪 Тестирование системы достижений...")

    test_user_id = "test_user_123"
    
    print("\n1. Проверяем достижения за тесты...")

    unlocked = AchievementsService.check_test_achievements(test_user_id, 1)
    print(f"   Первый тест: {len(unlocked)} достижений разблокировано")
    
    unlocked = AchievementsService.check_test_achievements(test_user_id, 10)
    print(f"   10 тестов: {len(unlocked)} достижений разблокировано")
    
    unlocked = AchievementsService.check_test_achievements(test_user_id, 25)
    print(f"   25 тестов: {len(unlocked)} достижений разблокировано")
    
    print("\n2. Проверяем достижения за ИИ-консультации...")

    unlocked = AchievementsService.check_ai_achievements(test_user_id, 1)
    print(f"   Первая ИИ-консультация: {len(unlocked)} достижений разблокировано")
    
    unlocked = AchievementsService.check_ai_achievements(test_user_id, 5)
    print(f"   5 ИИ-консультаций: {len(unlocked)} достижений разблокировано")
    
    print("\n3. Проверяем достижения за избранное...")

    unlocked = AchievementsService.check_favorites_achievements(test_user_id, 1)
    print(f"   Первое избранное: {len(unlocked)} достижений разблокировано")
    
    unlocked = AchievementsService.check_favorites_achievements(test_user_id, 5)
    print(f"   5 избранных: {len(unlocked)} достижений разблокировано")
    
    print("\n4. Проверяем специальные достижения...")

    test_time = datetime.now()
    unlocked = AchievementsService.check_special_achievements(test_user_id, test_time, 25)
    print(f"   Спидраннер (25 сек): {len(unlocked)} достижений разблокировано")
    
    print("\n5. Получаем все достижения пользователя...")
    
    achievements = AchievementsService.get_user_achievements(test_user_id)
    print(f"   Всего достижений: {len(achievements)}")
    
    if achievements:
        print("   Список достижений:")
        for achievement in achievements[:3]:
            print(f"     {achievement['icon']} {achievement['name']} - {achievement['description']}")
    
    print("\n6. Получаем статистику достижений...")
    
    stats = AchievementsService.get_achievements_stats(test_user_id)
    print(f"   Общее количество: {stats['total_achievements']}")
    print(f"   Категории: {stats['categories']}")
    
    if stats['last_achievement']:
        print(f"   Последнее достижение: {stats['last_achievement']['name']}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_achievements() 