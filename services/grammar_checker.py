"""
Grammar analysis and explanation service for Umar Tutor Bot.
Analyzes English sentences submitted by users, detects common grammatical and structural
errors, provides corrected versions and detailed explanations in Uzbek.
"""
import re
from typing import Dict, Any, List

RULES = [
    {
        "pattern": r"\b(i|he|she|it|we|they|you)\s+am\s+go\b|\b(i|he|she|it|we|they|you)\s+is\s+go\b|\b(i|he|she|it|we|they|you)\s+are\s+go\b",
        "replacement": lambda m: "went" if "yesterday" in m.string.lower() or "last" in m.string.lower() or "ago" in m.string.lower() else "go",
        "title": "Noto'g'ri fe'l birikmasi (to be + V1)",
        "explanation": "Ingliz tilida 'am/is/are' yordamchi fe'llari to'g'ridan-to'g'ri oddiy fe'l (go) bilan birga ishlatilmaydi. Agar o'tgan zamonda bo'lsa Past Simple ('went'), agar hozirgi davomli zamon bo'lsa Present Continuous ('going') ishlatiladi.",
        "tip": "Past Simple uchun 'go' fe'lining 2-shakli: 'went'."
    },
    {
        "pattern": r"\b(i|you|we|they|he|she)\s+didn['’]?t\s+(went|saw|bought|came|had|took|did)\b",
        "title": "didn't dan keyin fe'lning 2-shakli (V2) qo'llanilishi",
        "explanation": "'Didn't' inkor yordamchi fe'lidan keyin doimo fe'lning 1-boshlang'ich shakli (infinitive) kelishi shart. O'tgan zamon ma'nosi 'did' orqali berib bo'lingan.",
        "tip": "To'g'ri qolip: didn't + go / didn't + see / didn't + buy."
    },
    {
        "pattern": r"\b(he|she|it)\s+don['’]?t\b",
        "replacement": "doesn't",
        "title": "Bosh bo'laklar moslashuvi (Subject-Verb Agreement)",
        "explanation": "Uchinchi shaxs birlikda (He, She, It) inkor gap tuzganda 'don't' emas, balki 'doesn't' ishlatiladi.",
        "tip": "He doesn't / She doesn't / It doesn't."
    },
    {
        "pattern": r"\b(i|we|you|they)\s+doesn['’]?t\b",
        "replacement": "don't",
        "title": "Bosh bo'laklar moslashuvi",
        "explanation": "I, You, We, They olmoshlari bilan Present Simple inkorida 'don't' ishlatiladi.",
        "tip": "I don't / They don't."
    },
    {
        "pattern": r"\b(he|she|it)\s+(like|work|live|play|speak|want|read|write)\b",
        "title": "Fe'lga -s/-es qo'shimchasi qo'yilmagan",
        "explanation": "Present Simple zamonida ega 3-shaxs birlik (He, She, It) bo'lganda, fe'l oxiriga '-s' yoki '-es' qo'shiladi.",
        "tip": "Masalan: He works, She speaks English, It plays."
    },
    {
        "pattern": r"\b(i|he|she|they|we)\s+am\s+agree\b|\b(i|he|she|they|we)\s+are\s+agree\b|\b(i|he|she|they|we)\s+is\s+agree\b",
        "title": "'Agree' fe'lining noto'g'ri qo'llanilishi",
        "explanation": "'Agree' ingliz tilida sifat emas, balki fe'l (rozi bo'lmoq) hisoblanadi. Shuning uchun 'to be' (am/is/are) qo'yilmaydi.",
        "tip": "To'g'ri shakli: 'I agree' yoki 'I don't agree'."
    },
    {
        "pattern": r"\b(i|he|she|we|they)\s+have\s+(\d+|twenty|thirty|eighteen|nineteen)\s+years\s+old\b",
        "title": "Yoshni aytishda xatolik (have o'rniga to be)",
        "explanation": "Ingliz tilida yosh 'have' fe'li bilan emas, balki 'to be' (am/is/are) bilan ifodalanadi.",
        "tip": "Masalan: 'I am 20 years old' yoki shunchaki 'I am 20'."
    },
    {
        "pattern": r"\bmore\s+(better|bigger|faster|easier|taller|smaller)\b",
        "title": "Ortiqcha qiyosiy daraja (Double Comparative)",
        "explanation": "Bir bo'g'inli sifatlarga allaqachon '-er' qo'shilgan bo'lsa, ularning oldiga yana 'more' qo'yish xato hisoblanadi.",
        "tip": "To'g'ri: 'better' (more better emas), 'bigger' (more bigger emas)."
    },
    {
        "pattern": r"\bgood\s+in\s+(english|math|sports|football|languages)\b",
        "title": "Predlog xatoligi: good at",
        "explanation": "Biror fan yoki sohada yaxshi bo'lishni ifodalashda 'good in' emas, doimo 'good at' ishlatiladi.",
        "tip": "I am good at English / She is good at maths."
    },
    {
        "pattern": r"\b(an\s+informations?|informations)\b",
        "title": "Sanalmaydigan otlar: Information",
        "explanation": "'Information' so'zi sanalmaydigan ot bo'lib, unga ko'plik qo'shimchasi '-s' qo'shilmaydi va 'an' noaniq artikli bilan kelmaydi.",
        "tip": "Agar bitta demoqchi bo'lsangiz: 'a piece of information' yoki shunchaki 'information'."
    },
    {
        "pattern": r"\b(advices|an\s+advice)\b",
        "title": "Sanalmaydigan otlar: Advice",
        "explanation": "'Advice' (maslahat) so'zi sanalmaydi. Unga '-s' qo'shilmaydi va 'an advice' deb ishlatilmaydi.",
        "tip": "To'g'ri shakl: 'some advice' yoki 'a piece of advice'."
    },
    {
        "pattern": r"\b(i|we|they|he|she)\s+listen\s+(music|to\s+me|the\s+radio)\b",
        "title": "'Listen' fe'lida 'to' predlogining tushib qolishi",
        "explanation": "Biror narsani tinglash haqida gapirganda 'listen' fe'lidan keyin doimo 'to' predlogi ishlatiladi.",
        "tip": "Masalan: 'listen to music', 'listen to the podcast'."
    },
    {
        "pattern": r"\bdepend\s+of\b",
        "title": "Predlog xatoligi: depend on",
        "explanation": "'Depend' fe'li o'zbek tiliga 'bog'liq bo'lmoq' deb tarjima qilinadi va doimo 'on' predlogi bilan keladi.",
        "tip": "To'g'ri shakli: 'It depends on the weather'."
    }
]

def analyze_grammar(text: str) -> Dict[str, Any]:
    """
    Analyzes sentence, detects patterns, and returns correction card.
    """
    clean_text = text.strip()
    if not clean_text:
        return {
            "has_error": False,
            "message": "Iltimos, tekshirish uchun inglizcha jumla yuboring."
        }

    detected_issues: List[Dict[str, str]] = []
    corrected_text = clean_text

    # Specific common sentence fix: "I am go to the school yesterday"
    lower_text = clean_text.lower()
    if "am go" in lower_text or "is go" in lower_text or "are go" in lower_text:
        if any(w in lower_text for w in ["yesterday", "last", "ago", "past"]):
            corrected_text = re.sub(r"\b(am|is|are)\s+go\b", "went", corrected_text, flags=re.IGNORECASE)
            detected_issues.append({
                "title": "Past Simple & Fe'l shakli",
                "explanation": "O'tgan zamon (yesterday/last...) haqida gapirganda 'am go' emas, 'go' fe'lining o'tgan zamon shakli bo'lgan 'went' ishlatiladi.",
                "tip": "I went to school yesterday."
            })
        else:
            corrected_text = re.sub(r"\b(am|is|are)\s+go\b", "am going", corrected_text, flags=re.IGNORECASE)
            detected_issues.append({
                "title": "Present Continuous",
                "explanation": "'to be' bilan fe'l kelganda hozirgi davomli zamonda fe'lga '-ing' qo'shiladi.",
                "tip": "I am going to school."
            })

    # "didn't went" -> "didn't go"
    if re.search(r"\bdidn['’]?t\s+went\b", lower_text):
        corrected_text = re.sub(r"\bdidn['’]?t\s+went\b", "didn't go", corrected_text, flags=re.IGNORECASE)
        detected_issues.append({
            "title": "Inkor o'tgan zamonda fe'l shakli",
            "explanation": "'Didn't' dan keyin fe'lning 1-shakli kelishi kerak ('didn't go').",
            "tip": "I didn't go to the party."
        })

    # "he don't" -> "he doesn't"
    if re.search(r"\b(he|she|it)\s+don['’]?t\b", lower_text):
        corrected_text = re.sub(r"\b(he|she|it)\s+don['’]?t\b", r"\1 doesn't", corrected_text, flags=re.IGNORECASE)
        detected_issues.append({
            "title": "Subject-Verb Agreement",
            "explanation": "He/She/It olmoshlari bilan inkor shaklda 'doesn't' ishlatiladi.",
            "tip": "He doesn't know / She doesn't like."
        })

    # "I am agree" -> "I agree"
    if re.search(r"\bi\s+am\s+agree\b", lower_text):
        corrected_text = re.sub(r"\bi\s+am\s+agree\b", "I agree", corrected_text, flags=re.IGNORECASE)
        detected_issues.append({
            "title": "Agree fe'lining ishlatilishi",
            "explanation": "'Agree' (rozi bo'lmoq) fe'l hisoblanadi, uning oldidan 'am' qo'yilmaydi.",
            "tip": "I agree with you."
        })

    # "more better" -> "better"
    if "more better" in lower_text:
        corrected_text = re.sub(r"\bmore\s+better\b", "better", corrected_text, flags=re.IGNORECASE)
        detected_issues.append({
            "title": "Qiyosiy daraja xatoligi",
            "explanation": "'Better' so'zi allaqachon 'good' ning qiyosiy darajasi, 'more' qo'shilmaydi.",
            "tip": "This book is better than that one."
        })

    # "good in english" -> "good at english"
    if re.search(r"\bgood\s+in\s+english\b", lower_text):
        corrected_text = re.sub(r"\bgood\s+in\s+english\b", "good at English", corrected_text, flags=re.IGNORECASE)
        detected_issues.append({
            "title": "Predlog birikmasi",
            "explanation": "Ingliz tilida bilim yoki mahoratni ifodalashda 'good at' birikmasi ishlatiladi.",
            "tip": "I am good at English."
        })

    # Check remaining generic rules
    for rule in RULES:
        if re.search(rule["pattern"], lower_text):
            # If not already recorded
            if not any(d["title"] == rule["title"] for d in detected_issues):
                detected_issues.append({
                    "title": rule["title"],
                    "explanation": rule["explanation"],
                    "tip": rule["tip"]
                })

    # Capitalization & basic punctuation check
    if corrected_text and corrected_text[0].islower():
        corrected_text = corrected_text[0].upper() + corrected_text[1:]
    if corrected_text and corrected_text[-1] not in [".", "!", "?"]:
        corrected_text += "."

    if detected_issues or corrected_text != clean_text:
        return {
            "has_error": True,
            "original": clean_text,
            "corrected": corrected_text,
            "issues": detected_issues
        }
    else:
        return {
            "has_error": False,
            "original": clean_text,
            "message": "Ajoyib! Siz yozgan jumlada jiddiy grammatik xatolik aniqlanmadi. Tabiiy va to'g'ri tuzilgan jumla! 🎉"
        }
