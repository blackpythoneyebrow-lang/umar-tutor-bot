"""
7-Day English Challenge Service for Umar Tutor Bot.
Manages daily missions, point accumulation, leaderboard standings,
and generates the final completion report + next 30-day study plan.
"""
from typing import Dict, Any, List

CHALLENGE_DAYS = [
    {
        "day": 1,
        "title": "1-Kun: Vocab Sprint (Lug'at)",
        "badge": "⚡",
        "points": 50,
        "desc": "Bugun 5 ta yangi so'zni o'rganing va mini-lug'at testini kamida 80% natija bilan yakunlang.",
        "action_text": "Lug'at testini boshlash",
        "action_target": "vocab"
    },
    {
        "day": 2,
        "title": "2-Kun: Speaking Icebreaker (Nutq)",
        "badge": "🎙️",
        "points": 50,
        "desc": "Speaking AI Coach bo'limida o'zingiz yoki kun tartibingiz haqida kamida 15 soniya erkin inglizcha gapiring.",
        "action_text": "Speaking mashqiga o'tish",
        "action_target": "speaking"
    },
    {
        "day": 3,
        "title": "3-Kun: Grammar Fixer (Grammatika)",
        "badge": "✍️",
        "points": 50,
        "desc": "Grammatika bo'limida 'Spot the Mistake' testini yechib, xato gaplarni toping.",
        "action_text": "Grammatika testiga o'tish",
        "action_target": "grammar"
    },
    {
        "day": 4,
        "title": "4-Kun: Listening Ear (Tinglash)",
        "badge": "🎧",
        "points": 50,
        "desc": "Listening darsidagi audio dialogni tinglang va savollarga to'liq javob bering.",
        "action_text": "Listening darsiga o'tish",
        "action_target": "listening"
    },
    {
        "day": 5,
        "title": "5-Kun: Real Roleplay (Jonli Suhbat)",
        "badge": "🏨",
        "points": 50,
        "desc": "Real Suhbat Simulyatorida (masalan, Mehmonxona yoki Restoranda) bot bilan kamida 3 ta gap almashing.",
        "action_text": "Suhbat Simulyatoriga o'tish",
        "action_target": "roleplay"
    },
    {
        "day": 6,
        "title": "6-Kun: Shadowing Fluency (Talaffuz)",
        "badge": "🌊",
        "points": 50,
        "desc": "Shadowing bo'limida berilgan nutqni diktor ortidan baland ovozda 3 marta takrorlang.",
        "action_text": "Shadowing mashqiga o'tish",
        "action_target": "shadowing"
    },
    {
        "day": 7,
        "title": "7-Kun: Final Master Quiz (Yakuniy Sinov)",
        "badge": "🏆",
        "points": 100,
        "desc": "O'tgan 6 kunlik mavzularni umumlashtiruvchi yakuniy testni topshiring va 30 kunlik shaxsiy o'quv rejasini oling!",
        "action_text": "Master Testni topshirish",
        "action_target": "quiz"
    }
]


def get_all_days_meta() -> List[Dict[str, Any]]:
    return CHALLENGE_DAYS


def generate_next_30_day_plan(user_name: str, total_points: int) -> Dict[str, Any]:
    """Generates the custom next 30-day study plan upon challenge completion."""
    return {
        "title": f"🎓 {user_name} uchun Shaxsiy 30 Kunlik O'quv Rejasi",
        "total_points": total_points,
        "level_achieved": "Active English Practitioner (B1 Target)",
        "phases": [
            {
                "phase": "1-10 Kun: So'z Boyligi va Barqaror Iboralar (Collocations)",
                "goal": "Kuniga 10 ta yangi so'z va 3 ta phrasal verb",
                "daily_routine": "Ertalab 5 daqiqa Vocab kartochkalari + tushdan keyin 1 ta mini-test."
            },
            {
                "phase": "11-20 Kun: Praktik Grammatika va Gap Tuzish",
                "goal": "Present Perfect, Shart ergash gaplar (Conditionals) va Modal fe'llar",
                "daily_routine": "Grammatika bo'limidagi tushuntirishlarni o'qib, jonli tekshiruv maydonida 5 tadan mustaqil gap tuzish."
            },
            {
                "phase": "21-30 Kun: Erkin Muloqot va Fluency (Ravonlik)",
                "goal": "To'xtovsiz gapirish, o'zbekcha o'ylamasdan inglizcha fikrlash",
                "daily_routine": "Har kuni 1 ta Roleplay simulyatorida yangi vaziyat suhbati + 5 daqiqa Shadowing."
            }
        ],
        "final_advice": "Eng muhimi — kunlik uzluksizlik (consistency). Kuniga 15 daqiqa dars qilish haftada bir marta 2 soat o'rgangandan ancha samaraliroq!"
    }
