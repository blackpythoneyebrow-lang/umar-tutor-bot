"""
Roleplay Conversation Simulator Service for Umar Tutor Bot.
Simulates real-world conversational English dialogues (Hotel, Cafe, Airport, Interview, Shopping),
tracks student turns, detects grammatical errors, and provides post-dialogue analysis with
CEFR score, explanations in Uzbek, and high-yield situational expressions.
"""
import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from services.grammar_checker import analyze_grammar

logger = logging.getLogger("umar_tutor.roleplay")

SCENARIOS = {
    "hotel": {
        "id": "hotel",
        "title": "Mehmonxona (Hotel Check-in & Stay)",
        "icon": "🏨",
        "character": "Sarah (Receptionist)",
        "role_uz": "Siz: Mehmon | Bot: Administrator (Sarah)",
        "level": "A2 - B1",
        "initial_message": "Good afternoon! Welcome to Grand Palace Hotel. How may I assist you today?",
        "initial_message_uz": "Xayrli kun! Grand Palace mehmonxonasiga xush kelibsiz. Sizga qanday yordam bera olaman?",
        "useful_phrases": [
            {"en": "I have a reservation under the name...", "uz": "Mening nomimga band qilingan joy (bron) bor edi..."},
            {"en": "Could you tell me what time breakfast is served?", "uz": "Nonushta soat nechada berilishini ayta olasizmi?"},
            {"en": "Could I have the Wi-Fi password, please?", "uz": "Wi-Fi parolini bera olasizmi, iltimos?"},
            {"en": "What time is check-out tomorrow?", "uz": "Ertaga xonani topshirish (check-out) soat nechada?"},
            {"en": "Could you arrange a taxi to the airport for me?", "uz": "Men uchun aeroportga taksi chaqirib bera olasizmi?"}
        ],
        "dialogue_tree": [
            {
                "keywords": ["reservation", "booked", "booking", "room", "check in", "name"],
                "reply": "Excellent! May I see your passport and booking confirmation number, please?",
                "reply_uz": "Juda yaxshi! Iltimos, pasportingiz va bron raqamingizni ko'rsata olasizmi?"
            },
            {
                "keywords": ["passport", "here", "sure", "id", "number", "card"],
                "reply": "Thank you! Everything is in order. You are in Room 402 on the 4th floor. Here is your key card. Breakfast is served from 7 to 10 AM.",
                "reply_uz": "Rahmat! Hammasi joyida. Siz 4-qavatdagi 402-xonadasiz. Mana kalit kartangiz. Nonushta ertalab 7:00 dan 10:00 gacha."
            },
            {
                "keywords": ["wifi", "internet", "password", "code", "connect"],
                "reply": "The Wi-Fi network is 'GrandPalace_Guest' and the password is 'Welcome2026'. Is there anything else you need?",
                "reply_uz": "Wi-Fi tarmog'i: 'GrandPalace_Guest', paroli: 'Welcome2026'. Sizga yana biror narsa kerakmi?"
            },
            {
                "keywords": ["breakfast", "food", "eat", "restaurant", "morning"],
                "reply": "Breakfast is a full buffet on the ground floor next to the garden. It is complimentary with your stay!",
                "reply_uz": "Nonushta 1-qavatda, bog' yonidagi shved stoli ko'rinishida beriladi. Bu xonangiz narxiga kiritilgan!"
            },
            {
                "keywords": ["thank", "thanks", "ok", "fine", "good", "great", "bye"],
                "reply": "You are very welcome! Enjoy your stay, and do not hesitate to dial '0' from your room if you need anything.",
                "reply_uz": "Arzimaydi! Maroqli dam oling, agar biror narsa kerak bo'lsa xonadagi telefondan '0' ni tering."
            }
        ],
        "default_replies": [
            ("Certainly! I would be delighted to help you with that. Could you please specify your preferred room type?", "Albatta! Sizga bu borada mamnuniyat bilan yordam beraman. Qaysi turdagi xonani ma'qul ko'rishingizni ayta olasizmi?"),
            ("Understood. I will make a note of that on your reservation record right away.", "Tushunarli. Buni darhol sizning bron ma'lumotlaringizga qayd etib qo'yaman."),
            ("That is absolutely fine. Is there any other request or amenity you would like for your stay?", "Hammasi tushunarli. Qolish davringiz uchun yana biror maxsus iltimosingiz bormi?")
        ]
    },
    "restaurant": {
        "id": "restaurant",
        "title": "Qahvaxona & Restoran (Ordering Food)",
        "icon": "☕",
        "character": "David (Waiter)",
        "role_uz": "Siz: Mijoz | Bot: Ofitsiant (David)",
        "level": "Starter - A2",
        "initial_message": "Hi there! Welcome to Central Bistro. Table for one, or are you waiting for someone?",
        "initial_message_uz": "Salom! Central Bistro'ga xush kelibsiz. Bir kishilik stolmi yoki birovni kutyapsizmi?",
        "useful_phrases": [
            {"en": "Could I see the menu, please?", "uz": "Menyuni ko'rsam bo'ladimi, iltimos?"},
            {"en": "What do you recommend for today?", "uz": "Bugun uchun nimani tavsiya qilasiz?"},
            {"en": "I would like to order a steak and a glass of water.", "uz": "Men steyk va bir stakan suv buyurtma qilmoqchiman."},
            {"en": "Could we have the bill, please?", "uz": "Hisobni olib kelsangiz, iltimos?"},
            {"en": "Can I pay by card or cash?", "uz": "Karta yoki naqd pulda to'lasam bo'ladimi?"}
        ],
        "dialogue_tree": [
            {
                "keywords": ["one", "table", "alone", "just me", "two", "window"],
                "reply": "Right this way! Here is the menu. Today's chef special is grilled salmon with asparagus. Can I get you something to drink first?",
                "reply_uz": "Bu tomonga marhamat! Mana menyu. Bugungi bosh oshpaz maxsus taomi — qovurilgan losos balig'i. Boshlanishiga ichimlik keltiraymi?"
            },
            {
                "keywords": ["water", "coffee", "tea", "cappuccino", "juice", "drink"],
                "reply": "Great choice, I will bring your drink right away. Have you decided on your main dish, or do you need a couple more minutes?",
                "reply_uz": "Ajoyib tanlov, ichimlikni hozir keltiraman. Asosiy taomni tanladingizmi yoki yana ikki daqiqa vaqt kerakmi?"
            },
            {
                "keywords": ["pizza", "burger", "salad", "pasta", "steak", "chicken", "order", "salmon", "meat"],
                "reply": "Delicious choice! How would you like that prepared? Any allergies or special dietary preferences?",
                "reply_uz": "Juda mazali tanlov! Taom qanday tayyorlanishini xohlaysiz? Allergiya yoki maxsus talablaringiz bormi?"
            },
            {
                "keywords": ["no", "none", "allergies", "medium", "well", "rare", "fine"],
                "reply": "Perfect. Your order is placed and should arrive in about 15 minutes. Enjoy your time!",
                "reply_uz": "Ajoyib. Buyurtmangiz qabul qilindi va 15 daqiqada tayyor bo'ladi. Vaqtingiz maroqli o'tsin!"
            },
            {
                "keywords": ["bill", "check", "pay", "card", "cash", "how much"],
                "reply": "Here is your bill. It comes to $24.50. You can pay with card contactless, or cash. Thank you for dining with us!",
                "reply_uz": "Mana hisobingiz. Jami $24.50 bo'ldi. Karta orqali tekkizib yoki naqd to'lashingiz mumkin. Bizni tanlaganingiz uchun rahmat!"
            }
        ],
        "default_replies": [
            ("Sounds wonderful! I will make sure the kitchen prepares that with utmost care.", "Juda soz! Oshxona buni eng a'lo darajada tayyorlashini ta'minlayman."),
            ("Would you like anything on the side with that, such as French fries or steamed rice?", "Ushbu taom yoniga biror qo'shimcha garnir, masalan kartoshka fri yoki guruch xohlaysizmi?"),
            ("Certainly! I will be right back with that.", "Albatta! Hozir darhol olib kelaman.")
        ]
    },
    "airport": {
        "id": "airport",
        "title": "Aeroport & Bojxona (Customs & Border)",
        "icon": "✈️",
        "character": "Officer Smith (Immigration)",
        "role_uz": "Siz: Sayohatchi | Bot: Bojxona xodimi",
        "level": "B1 - B2",
        "initial_message": "Good day. Passport and boarding pass, please. What is the purpose of your visit?",
        "initial_message_uz": "Xayrli kun. Pasport va chiqish chiptangizni bering. Tashrifingizdan maqsad nima?",
        "useful_phrases": [
            {"en": "I am traveling for tourism and sightseeing.", "uz": "Men sayohat va diqqatga sazovor joylarni ko'rish uchun keldim."},
            {"en": "I will be staying for ten days.", "uz": "Men 10 kun davomida qolaman."},
            {"en": "Here is my return ticket to Tashkent.", "uz": "Mana mening Toshkentga qaytish chiptam."},
            {"en": "I will be staying at the Hilton Hotel.", "uz": "Men Hilton mehmonxonasida istiqomat qilaman."},
            {"en": "I have nothing to declare.", "uz": "Menda deklaratsiya qilinadigan ortiqcha yuk yo'q."}
        ],
        "dialogue_tree": [
            {
                "keywords": ["tourist", "tourism", "vacation", "holiday", "visit", "sightseeing", "business"],
                "reply": "I see. How long do you plan to stay in the country, and where will you be staying?",
                "reply_uz": "Tushunarli. Mamlakatda qancha vaqt qolishni rejalashtiryapsiz va qayerda yashaysiz?"
            },
            {
                "keywords": ["hotel", "days", "weeks", "stay", "friend", "hostel", "apartment"],
                "reply": "Do you have a return ticket booked? May I see your booking confirmation, please?",
                "reply_uz": "Qaytish chiptangiz olinganmi? Chipta yoki bron tasdig'ini ko'rsata olasizmi?"
            },
            {
                "keywords": ["yes", "ticket", "here", "sure", "flight", "return"],
                "reply": "Thank you. Are you carrying any prohibited items, plants, seeds, or more than $10,000 in cash?",
                "reply_uz": "Rahmat. Yoningizda taqiqlangan buyumlar, o'simliklar yoki $10,000 dan ortiq naqd pul bormi?"
            },
            {
                "keywords": ["no", "nothing", "none", "declare", "safe"],
                "reply": "Everything looks great. Welcome to the United Kingdom! Have a pleasant stay.",
                "reply_uz": "Hammasi a'lo darajada. Buyuk Britaniyaga xush kelibsiz! Sayohatingiz maroqli o'tsin."
            }
        ],
        "default_replies": [
            ("Thank you for the clarification. Please place your right index finger on the fingerprint scanner.", "Aniqlik uchun rahmat. Iltimos, o'ng ko'rsatkich barmog'ingizni skanerga qo'ying."),
            ("Understood. And what is your occupation back in your home country?", "Tushunarli. O'z vataningizda qaysi sohada faoliyat yuritasiz?"),
            ("All documents are verified. You are clear to proceed to baggage claim.", "Hamma hujjatlar tasdiqlandi. Yuk qabul qilish zaliga o'tishingiz mumkin.")
        ]
    },
    "interview": {
        "id": "interview",
        "title": "Ish Suhbatida (Job Interview)",
        "icon": "💼",
        "character": "Ms. Anderson (HR Director)",
        "role_uz": "Siz: Nomzod | Bot: HR Direktori",
        "level": "B1 - B2",
        "initial_message": "Hello! Welcome to our corporate office. Please take a seat. Could you start by introducing yourself?",
        "initial_message_uz": "Salom! Ofisimizga xush kelibsiz. Marhamat, o'tiring. O'zingiz haqingizda qisqacha tanishtirishdan boshlasak?",
        "useful_phrases": [
            {"en": "I have three years of experience working as...", "uz": "Men ... sifatida 3 yillik ish tajribasiga egaman."},
            {"en": "My greatest strength is my ability to solve problems quickly.", "uz": "Eng kuchli tomonim — muammolarni tezkorlik bilan hal qila olishimdir."},
            {"en": "I am passionate about continuous professional development.", "uz": "Men doimiy kasbiy rivojlanishga katta qiziqish bilan yondashaman."},
            {"en": "I work very effectively in high-pressure team environments.", "uz": "Men yuqori mas'uliyatli jamoaviy muhitda juda samarali ishlayman."},
            {"en": "What are the opportunities for career growth here?", "uz": "Bu yerda martaba (karyera) bo'yicha o'sish imkoniyatlari qanday?"}
        ],
        "dialogue_tree": [
            {
                "keywords": ["name", "experience", "work", "graduated", "years", "student", "developer", "designer", "english"],
                "reply": "That sounds very promising! What would you say is your greatest professional strength?",
                "reply_uz": "Juda yaxshi! Sizning eng kuchli kasbiy mahoratingiz nima deb o'ylaysiz?"
            },
            {
                "keywords": ["strength", "problem", "fast", "team", "hardworking", "communication", "learn", "responsible"],
                "reply": "Impressive. Can you share an example of a difficult challenge you faced at work or study, and how you solved it?",
                "reply_uz": "Qoyilmaqom. Ishingizda yoki o'qishingizda duch kelgan murakkab qiyinchilik va uni qanday hal qilganingizga misol keltira olasizmi?"
            },
            {
                "keywords": ["project", "time", "solved", "fixed", "team", "helped", "result", "difficult", "task"],
                "reply": "Excellent problem-solving approach. Why do you want to join our organization specifically?",
                "reply_uz": "Muammoni hal qilishda juda to'g'ri yondashuv. Aynan nima uchun bizning kompaniyada ishlashni xohlaysiz?"
            },
            {
                "keywords": ["grow", "company", "culture", "opportunity", "best", "future", "goals"],
                "reply": "Thank you for sharing your thoughts. We were very impressed by your communication and drive. Do you have any questions for us?",
                "reply_uz": "Fikrlaringiz uchun rahmat. Suhbat va g'ayratingiz bizda iliq taassurot qoldirdi. Bizga savollaringiz bormi?"
            }
        ],
        "default_replies": [
            ("That is a very insightful perspective. How do you handle tight deadlines or stressful situations?", "Juda qiziqarli yondashuv. Qisqa muddatli topshiriqlar va bosim ostidagi vaziyatlarni qanday boshqarasiz?"),
            ("Very clear explanation. How do you envision your professional journey over the next 3 to 5 years?", "Juda aniq tushuntirish. Keyingi 3-5 yilda o'z kasbiy yo'lingizni qanday tasavvur qilasiz?"),
            ("Thank you for your honesty. We appreciate candidates who value continuous improvement.", "Samimiyligingiz uchun rahmat. Biz doimiy o'sishga intiluvchi nomzodlarni juda qadrlaymiz.")
        ]
    },
    "shopping": {
        "id": "shopping",
        "title": "Do'konda Xarid (Shopping & Retail)",
        "icon": "🛍️",
        "character": "Emma (Store Assistant)",
        "role_uz": "Siz: Xaridor | Bot: Do'kon maslahatchisi",
        "level": "Starter - A1",
        "initial_message": "Hello! Welcome to TrendStyle. Let me know if you are looking for anything specific today!",
        "initial_message_uz": "Salom! TrendStyle do'koniga xush kelibsiz. Agar biror maxsus kiyim qidirayotgan bo'lsangiz, bemalol ayting!",
        "useful_phrases": [
            {"en": "Do you have this jacket in a medium size?", "uz": "Ushbu kurtkaning M (o'rta) o'lchami bormi?"},
            {"en": "Where are the fitting rooms located?", "uz": "Kiyinib ko'rish xonalari qayerda joylashgan?"},
            {"en": "Does this come in other colors, like black or navy?", "uz": "Buning qora yoki ko'k kabi boshqa ranglari bormi?"},
            {"en": "How much does this pair of shoes cost?", "uz": "Ushbu poyabzal necha pul turadi?"},
            {"en": "Is this on discount or sale?", "uz": "Bu kiyimga chegirma bormi?"}
        ],
        "dialogue_tree": [
            {
                "keywords": ["jacket", "shirt", "pants", "shoes", "dress", "t-shirt", "jeans", "looking for", "buy"],
                "reply": "We have a fantastic new collection right here! What size and color would you prefer?",
                "reply_uz": "Bizda aynan shu bo'yicha ajoyib yangi kolleksiya bor! Qaysi o'lcham va rangni xohlaysiz?"
            },
            {
                "keywords": ["medium", "small", "large", "black", "blue", "white", "size"],
                "reply": "Here you go! We have size M in black. Would you like to try it on? The fitting rooms are right around the corner.",
                "reply_uz": "Mana, marhamat! Qora rangdagi M o'lchamimiz bor. Kiyib ko'rishni xohlaysizmi? Kiyinish xonasi burchakning o'zida."
            },
            {
                "keywords": ["fits", "tight", "loose", "good", "perfect", "like", "try"],
                "reply": "It looks wonderful on you! Today we have a 15% discount on all autumn items, so it comes to just $35.",
                "reply_uz": "Sizga juda yarashdi! Bugun kuzgi kiyimlarga 15% chegirma bor, shuning uchun jami $35 bo'ladi."
            },
            {
                "keywords": ["take", "buy", "pay", "card", "cash", "price"],
                "reply": "Splendid! Follow me to the cash register. I can bag this up for you right away. Card or cash?",
                "reply_uz": "Ajoyib! Kassaga marhamat qiling. Hozir siz uchun paketga solib beraman. Karta orqali yoki naqdmi?"
            }
        ],
        "default_replies": [
            ("We can certainly check our stockroom for your requested size. Give me just one moment!", "Siz so'ragan o'lcham omborimizda bor-yo'qligini darhol tekshirib beraman. Bir daqiqa kutasizmi?"),
            ("That color is extremely popular this season. It pairs nicely with our lightweight denim.", "Bu rang bu mavsumda juda ommabop. Bizning jinsi shimlarimiz bilan juda mos tushadi."),
            ("Would you like a matching belt or scarf to go with that?", "Ushbu kiyimga mos keladigan kamar yoki sharf ham ko'rishni xohlaysizmi?")
        ]
    }
}


def get_scenario_metadata(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Returns scenario configuration without internal state."""
    sc = SCENARIOS.get(scenario_id)
    if not sc:
        return None
    return {
        "id": sc["id"],
        "title": sc["title"],
        "icon": sc["icon"],
        "character": sc["character"],
        "role_uz": sc["role_uz"],
        "level": sc["level"],
        "initial_message": sc["initial_message"],
        "initial_message_uz": sc["initial_message_uz"],
        "useful_phrases": sc["useful_phrases"]
    }


def list_all_scenarios() -> List[Dict[str, Any]]:
    """Returns all available roleplay scenarios for picker UI."""
    return [get_scenario_metadata(k) for k in SCENARIOS.keys()]


def process_roleplay_turn(scenario_id: str, user_message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Processes single roleplay turn:
    1. Checks grammar of user_message.
    2. Determines appropriate bot response matching conversation flow.
    3. Returns response text, Uzbek translation, and any detected errors.
    """
    sc = SCENARIOS.get(scenario_id, SCENARIOS["hotel"])
    clean_msg = (user_message or "").strip()

    # Step 1: Grammar Check on student input
    grammar_res = analyze_grammar(clean_msg)
    detected_mistakes = []
    if grammar_res.get("has_errors") and grammar_res.get("corrections"):
        for c in grammar_res["corrections"]:
            detected_mistakes.append({
                "wrong": c.get("matched_text", ""),
                "correct": c.get("replacement") or "To'g'rilangan shakl",
                "explanation_uz": c.get("explanation", "")
            })

    # Step 2: Contextual response generation
    bot_reply = ""
    bot_reply_uz = ""
    msg_lower = clean_msg.lower()

    # Match against scenario dialogue tree keywords
    tree = sc.get("dialogue_tree", [])
    matched_entry = None
    for entry in tree:
        for kw in entry["keywords"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", msg_lower):
                matched_entry = entry
                break
        if matched_entry:
            break

    if matched_entry:
        bot_reply = matched_entry["reply"]
        bot_reply_uz = matched_entry["reply_uz"]
    else:
        # Fallback to smart rotating default responses
        defaults = sc.get("default_replies", [("I understand. Please tell me more.", "Tushunarli. Batafsilroq ayta olasizmi?")])
        idx = len(history) % len(defaults)
        bot_reply, bot_reply_uz = defaults[idx]

    turn_count = len(history) + 1
    is_finished = turn_count >= 8

    return {
        "bot_reply": bot_reply,
        "bot_reply_uz": bot_reply_uz,
        "detected_mistakes": detected_mistakes,
        "turn_count": turn_count,
        "is_finished": is_finished
    }


def analyze_full_roleplay(scenario_id: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Performs comprehensive post-dialogue evaluation:
    - Analyzes all user utterances for grammar & vocabulary errors.
    - Computes Fluency Score (0-100) and CEFR rating.
    - Extracts high-yield native situational phrases.
    - Generates actionable advice in Uzbek.
    """
    sc = SCENARIOS.get(scenario_id, SCENARIOS["hotel"])
    user_turns = [h["text"] for h in history if h.get("sender") == "user" and h.get("text")]

    all_mistakes = []
    total_words = 0

    for turn in user_turns:
        words = turn.split()
        total_words += len(words)
        res = analyze_grammar(turn)
        if res.get("has_errors") and res.get("corrections"):
            for c in res["corrections"]:
                all_mistakes.append({
                    "wrong": c.get("matched_text", turn),
                    "correct": c.get("replacement") or "To'g'rilangan shakl",
                    "reason_uz": c.get("explanation", "Grammatik qolip mos kelmadi.")
                })

    # Fluency & Score calculation
    turn_count = len(user_turns)
    if turn_count == 0:
        base_score = 60
        cefr = "Starter"
    elif turn_count < 3:
        base_score = 75 - (len(all_mistakes) * 5)
        cefr = "A1"
    elif turn_count < 6:
        base_score = 85 - (len(all_mistakes) * 4)
        cefr = "A2"
    else:
        base_score = 94 - (len(all_mistakes) * 3)
        cefr = "B1" if base_score >= 80 else "A2"

    final_score = max(50, min(98, base_score))

    summary_uz = (
        f"Siz '{sc['title']}' mavzusidagi suhbatni muvaffaqiyatli yakunladingiz! "
        f"Jami {turn_count} ta dialog almashinuvi amalga oshirildi ({total_words} ta so'z ishlatildi). "
        f"{'Nutqingiz juda ravon va tushunarli boʻldi!' if final_score >= 85 else 'Fikrlaringiz tushunarli, ammo baʼzi grammatik nozikliklarga eʼtibor berish lozim.'}"
    )

    return {
        "success": True,
        "scenario_title": sc["title"],
        "score": final_score,
        "cefr_level": cefr,
        "turn_count": turn_count,
        "total_words": total_words,
        "summary_uz": summary_uz,
        "mistakes": all_mistakes,
        "useful_phrases": sc.get("useful_phrases", [])
    }
