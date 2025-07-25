PROFESSIONS = [
    {
        "id": 1,
        "name": "Программист",
        "category": "💻 IT",
        "audience": ["teen", "adult"],
        "with_people": False,
        "risk": False,
        "desc": "Создаёт программы и приложения. Подходит тем, кто любит технологии и стабильность.",
        "salary": "от 80,000₽",
        "skills": ["Python", "JavaScript", "SQL"],
        "education": "Высшее техническое или самообучение",
        "growth": "🚀 Высокий",
        "courses": ["Яндекс.Практикум", "GeekBrains", "Skillbox"]
    },
    {
        "id": 2,
        "name": "Врач",
        "category": "🏥 Медицина",
        "audience": ["teen", "adult"],
        "with_people": True,
        "risk": False,
        "desc": "Помогает людям, лечит болезни. Подходит тем, кто хочет работать с людьми и ценит стабильность.",
        "salary": "от 60,000₽",
        "skills": ["Медицинские знания", "Эмпатия", "Стрессоустойчивость"],
        "education": "Высшее медицинское образование + интернатура",
        "growth": "📈 Стабильный",
        "courses": ["Первый МГМУ", "СПбГМУ", "РНИМУ"]
    },
    {
        "id": 3,
        "name": "Дизайнер",
        "category": "🎨 Искусство",
        "audience": ["teen", "adult"],
        "with_people": False,
        "risk": True,
        "desc": "Создаёт визуальные решения. Подходит творческим людям, готовым к переменам.",
        "salary": "от 45,000₽",
        "skills": ["Adobe Creative Suite", "Креативность", "Чувство стиля"],
        "education": "Высшее художественное или курсы",
        "growth": "🎨 Творческий",
        "courses": ["Bang Bang Education", "Skillbox Design", "Contented"]
    },
    {
        "id": 4,
        "name": "Data Scientist",
        "category": "💻 IT",
        "audience": ["adult"],
        "with_people": False,
        "risk": True,
        "desc": "Анализирует большие данные и создаёт ML-модели. Для аналитического склада ума.",
        "salary": "от 120,000₽",
        "skills": ["Python", "R", "Machine Learning", "SQL"],
        "education": "Высшее техническое + курсы",
        "growth": "🚀 Очень высокий",
        "courses": ["Яндекс.Практикум", "SkillFactory", "OTUS"]
    },
    {
        "id": 5,
        "name": "Психолог",
        "category": "🏥 Медицина",
        "audience": ["adult"],
        "with_people": True,
        "risk": False,
        "desc": "Помогает людям решать психологические проблемы. Для эмпатичных людей.",
        "salary": "от 40,000₽",
        "skills": ["Эмпатия", "Активное слушание", "Психотерапия"],
        "education": "Высшее психологическое + сертификация",
        "growth": "📈 Растущий",
        "courses": ["Институт психотерапии", "Московский гештальт институт"]
    },
    {
        "id": 6,
        "name": "SMM-менеджер",
        "category": "💼 Бизнес",
        "audience": ["teen", "adult"],
        "with_people": True,
        "risk": True,
        "desc": "Продвигает бренды в социальных сетях. Для творческих и коммуникабельных людей.",
        "salary": "от 35,000₽",
        "skills": ["Контент-план", "Аналитика", "Креативность", "Таргетинг"],
        "education": "Любое + курсы и практика",
        "growth": "🚀 Высокий",
        "courses": ["Нетология", "Skillbox", "Convertmonster"]
    },
    {
        "id": 7,
        "name": "3D-художник",
        "category": "🎨 Искусство",
        "audience": ["teen", "adult"],
        "with_people": False,
        "risk": True,
        "desc": "Создаёт 3D-модели для игр и фильмов. Сочетание творчества и технологий.",
        "salary": "от 55,000₽",
        "skills": ["Blender", "Maya", "3ds Max", "Художественное видение"],
        "education": "Художественное или IT + портфолио",
        "growth": "🎮 Игровая индустрия",
        "courses": ["XYZ School", "Skillbox", "CG Incubator"]
    },
    {
        "id": 8,
        "name": "DevOps-инженер",
        "category": "💻 IT",
        "audience": ["adult"],
        "with_people": False,
        "risk": False,
        "desc": "Настраивает и поддерживает IT-инфраструктуру. Высокооплачиваемая стабильная сфера.",
        "salary": "от 100,000₽",
        "skills": ["Docker", "Kubernetes", "AWS", "Linux"],
        "education": "Высшее техническое + сертификации",
        "growth": "⚡ Очень востребован",
        "courses": ["Слёрм", "OTUS", "Linux Professional Institute"]
    },
    {
        "id": 9,
        "name": "Архитектор",
        "category": "🏗️ Строительство",
        "audience": ["adult"],
        "with_people": False,
        "risk": False,
        "desc": "Проектирует здания и сооружения. Для тех, кто любит планировать и работать с чертежами.",
        "salary": "от 70,000₽",
        "skills": ["AutoCAD", "3D-моделирование", "Строительные нормы"],
        "education": "Высшее архитектурное",
        "growth": "📈 Стабильный",
        "courses": ["Skillbox Архитектура", "МИСиС", "МАРХИ"]
    },
    {
        "id": 10,
        "name": "Финансовый аналитик",
        "category": "💼 Бизнес",
        "audience": ["adult"],
        "with_people": False,
        "risk": False,
        "desc": "Анализирует финансовые отчёты компаний и помогает принимать инвестиционные решения.",
        "salary": "от 90,000₽",
        "skills": ["Excel", "Финансовый анализ", "SQL", "Power BI"],
        "education": "Высшее экономическое или MBA",
        "growth": "📊 Перспективный",
        "courses": ["Coursera Finance", "SkillFactory Финансы", "Нетология"]
    },
    {
        "id": 11,
        "name": "Маркетолог",
        "category": "💼 Бизнес",
        "audience": ["teen", "adult"],
        "with_people": True,
        "risk": True,
        "desc": "Создаёт стратегии продвижения товаров и услуг. Для креативных и активных людей.",
        "salary": "от 50,000₽",
        "skills": ["Маркетинговая аналитика", "Digital Marketing", "SEO", "SMM"],
        "education": "Экономическое или курсы маркетинга",
        "growth": "🚀 Высокий",
        "courses": ["Skillbox Маркетинг", "Нетология", "Google Digital Garage"]
    },
    {
        "id": 12,
        "name": "Инженер-конструктор",
        "category": "⚙️ Инженерия",
        "audience": ["adult"],
        "with_people": False,
        "risk": False,
        "desc": "Проектирует детали и механизмы. Для тех, кто любит точность и технологии.",
        "salary": "от 80,000₽",
        "skills": ["SolidWorks", "AutoCAD", "Чтение чертежей"],
        "education": "Высшее инженерное",
        "growth": "📈 Стабильный",
        "courses": ["Skillbox CAD", "Курсы SolidWorks", "НИТУ МИСиС"]
    },
    {
        "id": 13,
        "name": "UX/UI дизайнер",
        "category": "🎨 Искусство",
        "audience": ["teen", "adult"],
        "with_people": False,
        "risk": True,
        "desc": "Проектирует удобные интерфейсы для сайтов и приложений.",
        "salary": "от 70,000₽",
        "skills": ["Figma", "UX-исследования", "Прототипирование"],
        "education": "Дизайн-курсы или самообучение",
        "growth": "🚀 Высокий",
        "courses": ["Coursera UX/UI", "Contented UX", "Skillbox Дизайн"]
    }
]


def get_profession_by_preferences(audience, interest, with_people, risk):
    """Умный поиск профессий с весовой системой"""
    scored_professions = []

    for prof in PROFESSIONS:
        score = 0

        # Основные критерии (обязательные)
        if audience not in prof["audience"]:
            continue
        if prof["category"] != interest:
            continue

        # Дополнительные критерии (весовые)
        if prof["with_people"] == with_people:
            score += 10
        if prof["risk"] == risk:
            score += 10

        # Бонусы за популярность
        if prof["growth"] in ["🚀 Высокий", "🚀 Очень высокий"]:
            score += 5

        scored_professions.append((prof, score))

    # Сортируем по убыванию очков
    scored_professions.sort(key=lambda x: x[1], reverse=True)
    return [prof[0] for prof in scored_professions[:3]]


def get_profession_stats():
    """Статистика по профессиям"""
    return {
        "total": len(PROFESSIONS),
        "it_count": len([p for p in PROFESSIONS if p["category"] == "💻 IT"]),
        "high_growth": len([p for p in PROFESSIONS if "🚀" in p["growth"]]),
        "with_people": len([p for p in PROFESSIONS if p["with_people"]])
    }