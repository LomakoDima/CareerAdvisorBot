import json
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class ProfessionsService:
    def __init__(self, json_file_path: str = "database/proffessions.json"):
        self.json_file_path = json_file_path
        self.professions = []
        self.load_professions()
    
    def load_professions(self) -> None:
        try:
            project_root = Path(__file__).parent.parent
            file_path = project_root / self.json_file_path
            
            if not file_path.exists():
                raise FileNotFoundError(f"Файл {file_path} не найден")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                self.professions = json.load(file)
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON файла: {e}")
        except Exception as e:
            raise Exception(f"Ошибка загрузки файла профессий: {e}")
    
    def reload_professions(self) -> None:
        self.load_professions()
    
    def get_all_professions(self) -> List[Dict]:
        return self.professions.copy()
    
    def get_profession_by_id(self, profession_id: int) -> Optional[Dict]:
        for profession in self.professions:
            if profession.get("id") == profession_id:
                return profession
        return None
    
    def get_professions_by_category(self, category: str) -> List[Dict]:
        return [prof for prof in self.professions if prof.get("category") == category]
    
    def get_professions_by_audience(self, audience: str) -> List[Dict]:
        return [prof for prof in self.professions if audience in prof.get("audience", [])]
    
    def search_professions_by_name(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        return [
            prof for prof in self.professions 
            if query_lower in prof.get("name", "").lower()
        ]
    
    def get_professions_by_preferences(
        self, 
        audience: str, 
        category: str, 
        with_people: bool, 
        risk: bool,
        limit: int = 3
    ) -> List[Dict]:
        scored_professions = []

        for prof in self.professions:
            score = 0

            if audience not in prof.get("audience", []):
                continue
            if prof.get("category") != category:
                continue

            if prof.get("with_people") == with_people:
                score += 10
            if prof.get("risk") == risk:
                score += 10

            growth = prof.get("growth", "")
            if "🚀" in growth:
                score += 5

            scored_professions.append((prof, score))

        scored_professions.sort(key=lambda x: x[1], reverse=True)
        return [prof[0] for prof in scored_professions[:limit]]
    
    def get_professions_by_skills(self, skills: List[str]) -> List[Dict]:
        skills_lower = [skill.lower() for skill in skills]
        matching_professions = []
        
        for prof in self.professions:
            profession_skills = [skill.lower() for skill in prof.get("skills", [])]
            if any(skill in profession_skills for skill in skills_lower):
                matching_professions.append(prof)
        
        return matching_professions
    
    def get_professions_by_salary_range(self, min_salary: str = None, max_salary: str = None) -> List[Dict]:
        filtered_professions = []
        
        for prof in self.professions:
            salary = prof.get("salary", "")
            filtered_professions.append(prof)
        
        return filtered_professions
    
    def get_profession_stats(self) -> Dict:
        if not self.professions:
            return {"total": 0}
        
        categories = {}
        audiences = {"teen": 0, "adult": 0}
        with_people_count = 0
        risk_count = 0
        high_growth_count = 0
        
        for prof in self.professions:
            category = prof.get("category", "Неизвестно")
            categories[category] = categories.get(category, 0) + 1

            for audience in prof.get("audience", []):
                if audience in audiences:
                    audiences[audience] += 1

            if prof.get("with_people"):
                with_people_count += 1
            if prof.get("risk"):
                risk_count += 1
            if "🚀" in prof.get("growth", ""):
                high_growth_count += 1
        
        return {
            "total": len(self.professions),
            "categories": categories,
            "audiences": audiences,
            "with_people": with_people_count,
            "risk": risk_count,
            "high_growth": high_growth_count
        }
    
    def get_categories(self) -> List[str]:
        categories = set()
        for prof in self.professions:
            category = prof.get("category")
            if category:
                categories.add(category)
        return sorted(list(categories))
    
    def get_random_professions(self, count: int = 5) -> List[Dict]:
        import random
        if count >= len(self.professions):
            return self.professions.copy()
        
        return random.sample(self.professions, count)
    
    def add_profession(self, profession_data: Dict) -> bool:
        try:
            max_id = max([prof.get("id", 0) for prof in self.professions]) if self.professions else 0
            profession_data["id"] = max_id + 1

            self.professions.append(profession_data)

            self.save_professions()
            return True
            
        except Exception as e:
            print(f"Ошибка при добавлении профессии: {e}")
            return False
    
    def update_profession(self, profession_id: int, updated_data: Dict) -> bool:
        try:
            for i, prof in enumerate(self.professions):
                if prof.get("id") == profession_id:
                    updated_data["id"] = profession_id  # Сохраняем ID
                    self.professions[i] = updated_data
                    self.save_professions()
                    return True
            return False
            
        except Exception as e:
            print(f"Ошибка при обновлении профессии: {e}")
            return False
    
    def delete_profession(self, profession_id: int) -> bool:
        try:
            for i, prof in enumerate(self.professions):
                if prof.get("id") == profession_id:
                    del self.professions[i]
                    self.save_professions()
                    return True
            return False
            
        except Exception as e:
            print(f"Ошибка при удалении профессии: {e}")
            return False
    
    def save_professions(self) -> None:
        try:
            project_root = Path(__file__).parent.parent
            file_path = project_root / self.json_file_path
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.professions, file, ensure_ascii=False, indent=4)
                
        except Exception as e:
            raise Exception(f"Ошибка сохранения файла профессий: {e}")

professions_service = ProfessionsService() 