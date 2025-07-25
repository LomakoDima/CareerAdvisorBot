import asyncio
import os
import logging
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI
from .professions import PROFESSIONS

load_dotenv()

# Настройка OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
logger = logging.getLogger(__name__)

class AICareerConsultant:
    def __init__(self):
        self.model = "gpt-4o-mini"  # Новый API поддерживает gpt-4.1/gpt-4o
        self.max_tokens = 1000
        self.temperature = 0.7

    def _get_system_prompt(self, mode="chat"):
        base_prompt = """Ты - опытный карьерный консультант с 15-летним стажем. 
        Твоя задача - помочь людям найти идеальную профессию на основе их интересов, навыков и целей.

        Доступные профессии в базе данных:
        """
        for prof in PROFESSIONS:
            base_prompt += f"- {prof['name']} ({prof['category']}): {prof['desc'][:100]}...\n"

        if mode == "chat":
            return base_prompt + """
            РЕЖИМ: Консультационная беседа
            - Веди дружелюбный и профессиональный диалог
            - Задавай уточняющие вопросы о интересах, навыках, опыте
            - Используй эмодзи для дружелюбности
            - Отвечай на русском языке
            - Не предлагай конкретные профессии до запроса рекомендаций
            - Помогай пользователю лучше понять себя
            """
        elif mode == "recommend":
            return base_prompt + """
            РЕЖИМ: Генерация рекомендаций
            - Проанализируй всю беседу с пользователем
            - Предложи 2-3 наиболее подходящие профессии из доступной базы
            - Для каждой профессии объясни, почему она подходит
            - Дай конкретные советы по развитию в выбранных направлениях
            - Используй структурированный формат с эмодзи
            - Отвечай на русском языке
            """

    async def get_response(self, messages: List[Dict], mode="chat") -> str:
        try:
            full_messages = [{"role": "system", "content": self._get_system_prompt(mode)}] + messages
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=self.model,
                messages=full_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "😔 Произошла ошибка. Попробуй ещё раз или используй классический тест."

ai_consultant = AICareerConsultant()

async def get_ai_career_recommendation(messages: List[Dict], mode="chat") -> str:
    return await ai_consultant.get_response(messages, mode)

async def is_openai_available() -> bool:
    try:
        if not os.getenv('OPENAI_API_KEY'):
            return False
        await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        logger.warning(f"OpenAI not available: {e}")
        return False

def create_career_analysis_prompt(user_data: Dict) -> str:
    return f"""
    Проанализируй следующую информацию о пользователе и дай персональные карьерные рекомендации:

    Возраст: {user_data.get('age', 'не указан')}
    Образование: {user_data.get('education', 'не указано')}
    Опыт работы: {user_data.get('experience', 'не указан')}
    Интересы: {user_data.get('interests', 'не указаны')}
    Навыки: {user_data.get('skills', 'не указаны')}
    Предпочтения по работе: {user_data.get('work_preferences', 'не указаны')}
    Готовность к рискам: {user_data.get('risk_tolerance', 'не указана')}

    Дай 2-3 конкретные рекомендации с объяснением выбора.
    """

async def get_personalized_recommendations(user_info: Dict) -> str:
    try:
        prompt = create_career_analysis_prompt(user_info)
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты - карьерный консультант. Дай структурированные рекомендации."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        return "😔 Не удалось получить персонализированные рекомендации. Попробуй классический тест!"

def extract_user_info_from_messages(messages: List[Dict]) -> Dict:
    user_info = {'age': None, 'education': None, 'experience': None, 'interests': [], 'skills': [], 'work_preferences': [], 'personality_traits': []}
    full_text = ' '.join([msg['content'] for msg in messages if msg['role'] == 'user']).lower()
    import re
    age_match = re.search(r'(\d{1,2})\s*(лет|года|возраст)', full_text)
    if age_match:
        user_info['age'] = int(age_match.group(1))
    education_keywords = ['университет', 'институт', 'колледж', 'школа', 'образование']
    user_info['education'] = any(k in full_text for k in education_keywords)
    interest_keywords = {
        'programming': ['программирование', 'код', 'разработка', 'python', 'javascript'],
        'design': ['дизайн', 'творчество', 'рисование', 'искусство'],
        'business': ['бизнес', 'продажи', 'менеджмент', 'управление'],
        'medicine': ['медицина', 'лечение', 'здоровье', 'врач'],
        'engineering': ['инженерия', 'техника', 'механика', 'конструирование']
    }
    for category, keywords in interest_keywords.items():
        if any(k in full_text for k in keywords):
            user_info['interests'].append(category)
    return user_info

async def enhance_ai_response(raw_response: str, context: List[Dict]) -> str:
    enhanced_response = raw_response
    for profession in PROFESSIONS:
        if profession['name'].lower() in raw_response.lower():
            additional_info = f"\n\n📋 <b>Дополнительно о профессии {profession['name']}:</b>\n"
            additional_info += f"💰 Зарплата: {profession['salary']}\n"
            additional_info += f"📈 Перспективы: {profession['growth']}\n"
            additional_info += f"🎓 Образование: {profession['education']}\n"
            if additional_info not in enhanced_response:
                enhanced_response += additional_info
    return enhanced_response
