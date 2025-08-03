import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseService:


    def __init__(self, db_path: str = "user_profiles.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()


                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        total_tests INTEGER DEFAULT 0,
                        ai_consultations INTEGER DEFAULT 0,
                        favorite_categories TEXT DEFAULT '{}'
                    )
                ''')


                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS test_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        test_type TEXT NOT NULL,
                        results TEXT NOT NULL,
                        preferences TEXT,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                    )
                ''')


                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ai_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        messages_count INTEGER NOT NULL,
                        recommendations TEXT,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                    )
                ''')


                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS favorites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        salary TEXT NOT NULL,
                        added_at TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id),
                        UNIQUE(user_id, name)
                    )
                ''')


                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        achievement_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        icon TEXT NOT NULL,
                        category TEXT NOT NULL,
                        unlocked_at TEXT NOT NULL,
                        progress INTEGER DEFAULT 0,
                        max_progress INTEGER DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id),
                        UNIQUE(user_id, achievement_id)
                    )
                ''')


                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS achievement_progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        achievement_id TEXT NOT NULL,
                        current_progress INTEGER DEFAULT 0,
                        last_updated TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id),
                        UNIQUE(user_id, achievement_id)
                    )
                ''')

                conn.commit()
                logger.info("✅ База данных SQLite инициализирована")

        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
            raise

    def get_user_profile(self, user_id: str) -> Dict:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
                profile_row = cursor.fetchone()

                if not profile_row:
                    now = datetime.now().isoformat()
                    cursor.execute('''
                        INSERT INTO user_profiles (user_id, created_at, total_tests, ai_consultations, favorite_categories)
                        VALUES (?, ?, 0, 0, '{}')
                    ''', (user_id, now))
                    conn.commit()

                    return {
                        "user_id": user_id,
                        "created_at": now,
                        "stats": {
                            "total_tests": 0,
                            "ai_consultations": 0,
                            "favorite_categories": {}
                        },
                        "test_results": [],
                        "ai_sessions": [],
                        "favorites": []
                    }

                user_id_db, created_at, total_tests, ai_consultations, favorite_categories_json = profile_row
                favorite_categories = json.loads(favorite_categories_json)

                cursor.execute('''
                    SELECT date, test_type, results, preferences 
                    FROM test_results 
                    WHERE user_id = ? 
                    ORDER BY date DESC
                ''', (user_id,))

                test_results = []
                for row in cursor.fetchall():
                    test_results.append({
                        "date": row[0],
                        "type": row[1],
                        "results": json.loads(row[2]),
                        "preferences": json.loads(row[3]) if row[3] else {}
                    })

                cursor.execute('''
                    SELECT date, messages_count, recommendations 
                    FROM ai_sessions 
                    WHERE user_id = ? 
                    ORDER BY date DESC
                ''', (user_id,))

                ai_sessions = []
                for row in cursor.fetchall():
                    ai_sessions.append({
                        "date": row[0],
                        "messages_count": row[1],
                        "recommendations": row[2] or ""
                    })

                cursor.execute('''
                    SELECT name, category, salary, added_at 
                    FROM favorites 
                    WHERE user_id = ? 
                    ORDER BY added_at DESC
                ''', (user_id,))

                favorites = []
                for row in cursor.fetchall():
                    favorites.append({
                        "name": row[0],
                        "category": row[1],
                        "salary": row[2],
                        "added_at": row[3]
                    })

                return {
                    "user_id": user_id,
                    "created_at": created_at,
                    "stats": {
                        "total_tests": total_tests,
                        "ai_consultations": ai_consultations,
                        "favorite_categories": favorite_categories
                    },
                    "test_results": test_results,
                    "ai_sessions": ai_sessions,
                    "favorites": favorites
                }

        except Exception as e:
            logger.error(f"❌ Ошибка получения профиля пользователя {user_id}: {e}")
            return {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "stats": {"total_tests": 0, "ai_consultations": 0, "favorite_categories": {}},
                "test_results": [],
                "ai_sessions": [],
                "favorites": []
            }

    def save_test_result(self, user_id: str, test_type: str, results: List[Dict], preferences: Dict = None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO test_results (user_id, date, test_type, results, preferences)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    datetime.now().isoformat(),
                    test_type,
                    json.dumps(results, ensure_ascii=False),
                    json.dumps(preferences or {}, ensure_ascii=False)
                ))

                cursor.execute('''
                    UPDATE user_profiles 
                    SET total_tests = total_tests + 1 
                    WHERE user_id = ?
                ''', (user_id,))

                cursor.execute('''
                    SELECT favorite_categories 
                    FROM user_profiles 
                    WHERE user_id = ?
                ''', (user_id,))

                row = cursor.fetchone()
                if row:
                    favorite_categories = json.loads(row[0])

                    for prof in results[:2]:
                        category = prof.get("category", "Другое")
                        favorite_categories[category] = favorite_categories.get(category, 0) + 1

                    cursor.execute('''
                        UPDATE user_profiles 
                        SET favorite_categories = ? 
                        WHERE user_id = ?
                    ''', (json.dumps(favorite_categories, ensure_ascii=False), user_id))

                conn.commit()
                logger.info(f"✅ Результат теста сохранен для пользователя {user_id}")

        except Exception as e:
            logger.error(f"❌ Ошибка сохранения результата теста для {user_id}: {e}")

    def save_ai_session(self, user_id: str, session_data: Dict):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO ai_sessions (user_id, date, messages_count, recommendations)
                    VALUES (?, ?, ?, ?)
                ''', (
                    user_id,
                    datetime.now().isoformat(),
                    len(session_data.get("ai_context", [])),
                    session_data.get("ai_recommendations", "")
                ))

                cursor.execute('''
                    UPDATE user_profiles 
                    SET ai_consultations = ai_consultations + 1 
                    WHERE user_id = ?
                ''', (user_id,))

                conn.commit()
                logger.info(f"✅ ИИ-сессия сохранена для пользователя {user_id}")

        except Exception as e:
            logger.error(f"❌ Ошибка сохранения ИИ-сессии для {user_id}: {e}")

    def add_to_favorites(self, user_id: str, profession: Dict) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT COUNT(*) FROM favorites 
                    WHERE user_id = ? AND name = ?
                ''', (user_id, profession["name"]))

                if cursor.fetchone()[0] > 0:
                    return False

                cursor.execute('''
                    INSERT INTO favorites (user_id, name, category, salary, added_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    profession["name"],
                    profession["category"],
                    profession["salary"],
                    datetime.now().isoformat()
                ))

                conn.commit()
                logger.info(f"✅ Профессия '{profession['name']}' добавлена в избранное для {user_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Ошибка добавления в избранное для {user_id}: {e}")
            return False

    def clear_profile(self, user_id: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('DELETE FROM test_results WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM ai_sessions WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM favorites WHERE user_id = ?', (user_id,))

                cursor.execute('''
                    UPDATE user_profiles 
                    SET total_tests = 0, ai_consultations = 0, favorite_categories = '{}' 
                    WHERE user_id = ?
                ''', (user_id,))

                conn.commit()
                logger.info(f"✅ Профиль пользователя {user_id} очищен")

        except Exception as e:
            logger.error(f"❌ Ошибка очистки профиля {user_id}: {e}")

    def get_database_stats(self) -> Dict:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT COUNT(*) FROM user_profiles')
                total_users = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(*) FROM test_results')
                total_tests = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(*) FROM ai_sessions')
                total_ai_sessions = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(*) FROM favorites')
                total_favorites = cursor.fetchone()[0]

                return {
                    "total_users": total_users,
                    "total_tests": total_tests,
                    "total_ai_sessions": total_ai_sessions,
                    "total_favorites": total_favorites
                }

        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики БД: {e}")
            return {"total_users": 0, "total_tests": 0, "total_ai_sessions": 0, "total_favorites": 0}

    def backup_database(self, backup_path: str = None):
        if not backup_path:
            backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"✅ Резервная копия создана: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"❌ Ошибка создания резервной копии: {e}")
            return None


    def unlock_achievement(self, user_id: str, achievement_id: str, name: str, description: str, 
                          icon: str, category: str, progress: int = 1, max_progress: int = 1) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.now().isoformat()

                cursor.execute('''
                    SELECT id FROM achievements 
                    WHERE user_id = ? AND achievement_id = ?
                ''', (user_id, achievement_id))
                
                if cursor.fetchone():
                    return False

                cursor.execute('''
                    INSERT INTO achievements 
                    (user_id, achievement_id, name, description, icon, category, unlocked_at, progress, max_progress)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, achievement_id, name, description, icon, category, now, progress, max_progress))
                
                conn.commit()
                logger.info(f"🏆 Достижение разблокировано: {user_id} - {achievement_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка разблокировки достижения: {e}")
            return False

    def update_achievement_progress(self, user_id: str, achievement_id: str, progress: int, 
                                  max_progress: int = None) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.now().isoformat()

                cursor.execute('''
                    INSERT OR REPLACE INTO achievement_progress 
                    (user_id, achievement_id, current_progress, last_updated)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, achievement_id, progress, now))

                cursor.execute('''
                    UPDATE achievements 
                    SET progress = ?, max_progress = ?
                    WHERE user_id = ? AND achievement_id = ?
                ''', (progress, max_progress or progress, user_id, achievement_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления прогресса: {e}")
            return False

    def get_user_achievements(self, user_id: str) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT achievement_id, name, description, icon, category, 
                           unlocked_at, progress, max_progress
                    FROM achievements 
                    WHERE user_id = ?
                    ORDER BY unlocked_at DESC
                ''', (user_id,))
                
                achievements = []
                for row in cursor.fetchall():
                    achievements.append({
                        'achievement_id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'icon': row[3],
                        'category': row[4],
                        'unlocked_at': row[5],
                        'progress': row[6],
                        'max_progress': row[7]
                    })
                
                return achievements
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения достижений: {e}")
            return []

    def get_achievement_progress(self, user_id: str, achievement_id: str) -> Dict:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT current_progress, last_updated
                    FROM achievement_progress 
                    WHERE user_id = ? AND achievement_id = ?
                ''', (user_id, achievement_id))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'current_progress': row[0],
                        'last_updated': row[1]
                    }
                return {'current_progress': 0, 'last_updated': None}
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения прогресса: {e}")
            return {'current_progress': 0, 'last_updated': None}

    def get_achievements_stats(self, user_id: str) -> Dict:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT COUNT(*) FROM achievements WHERE user_id = ?
                ''', (user_id,))
                total_achievements = cursor.fetchone()[0]

                cursor.execute('''
                    SELECT category, COUNT(*) 
                    FROM achievements 
                    WHERE user_id = ? 
                    GROUP BY category
                ''', (user_id,))
                categories = dict(cursor.fetchall())

                cursor.execute('''
                    SELECT name, icon, unlocked_at 
                    FROM achievements 
                    WHERE user_id = ? 
                    ORDER BY unlocked_at DESC 
                    LIMIT 1
                ''', (user_id,))
                last_achievement = cursor.fetchone()
                
                return {
                    'total_achievements': total_achievements,
                    'categories': categories,
                    'last_achievement': {
                        'name': last_achievement[0],
                        'icon': last_achievement[1],
                        'unlocked_at': last_achievement[2]
                    } if last_achievement else None
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики достижений: {e}")
            return {'total_achievements': 0, 'categories': {}, 'last_achievement': None}

db_service = DatabaseService()

def update_achievement_progress(self, user_id: str, achievement_id: str, progress: int, 
                              max_progress: int = None) -> bool:
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()

            cursor.execute('''
                INSERT OR REPLACE INTO achievement_progress 
                (user_id, achievement_id, current_progress, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (user_id, achievement_id, progress, now))

            cursor.execute('''
                UPDATE achievements 
                SET progress = ?, max_progress = ?
                WHERE user_id = ? AND achievement_id = ?
            ''', (progress, max_progress or progress, user_id, achievement_id))
            
            conn.commit()
            return True
            
    except Exception as e:
        logger.error(f"❌ Ошибка обновления прогресса: {e}")
        return False

def get_user_achievements(self, user_id: str) -> List[Dict]:
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT achievement_id, name, description, icon, category, 
                       unlocked_at, progress, max_progress
                FROM achievements 
                WHERE user_id = ?
                ORDER BY unlocked_at DESC
            ''', (user_id,))
            
            achievements = []
            for row in cursor.fetchall():
                achievements.append({
                    'achievement_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'icon': row[3],
                    'category': row[4],
                    'unlocked_at': row[5],
                    'progress': row[6],
                    'max_progress': row[7]
                })
            
            return achievements
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения достижений: {e}")
        return []

def get_achievement_progress(self, user_id: str, achievement_id: str) -> Dict:
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT current_progress, last_updated
                FROM achievement_progress 
                WHERE user_id = ? AND achievement_id = ?
            ''', (user_id, achievement_id))
            
            row = cursor.fetchone()
            if row:
                return {
                    'current_progress': row[0],
                    'last_updated': row[1]
                }
            return {'current_progress': 0, 'last_updated': None}
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения прогресса: {e}")
        return {'current_progress': 0, 'last_updated': None}

def get_achievements_stats(self, user_id: str) -> Dict:
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(*) FROM achievements WHERE user_id = ?
            ''', (user_id,))
            total_achievements = cursor.fetchone()[0]

            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM achievements 
                WHERE user_id = ? 
                GROUP BY category
            ''', (user_id,))
            categories = dict(cursor.fetchall())

            cursor.execute('''
                SELECT name, icon, unlocked_at 
                FROM achievements 
                WHERE user_id = ? 
                ORDER BY unlocked_at DESC 
                LIMIT 1
            ''', (user_id,))
            last_achievement = cursor.fetchone()
            
            return {
                'total_achievements': total_achievements,
                'categories': categories,
                'last_achievement': {
                    'name': last_achievement[0],
                    'icon': last_achievement[1],
                    'unlocked_at': last_achievement[2]
                } if last_achievement else None
            }
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики достижений: {e}")
        return {'total_achievements': 0, 'categories': {}, 'last_achievement': None}