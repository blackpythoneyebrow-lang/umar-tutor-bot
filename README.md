# 🇬🇧 Umar Tutor — English Learning Telegram Bot

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green.svg)](https://docs.aiogram.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%20Async-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**Umar Tutor** — zamonaviy mobil ilova (UI/UX) ko'rinishida loyihalashtirilgan, ingliz tilini interaktiv va tizimli o'rganish uchun mo'ljallangan ishlab chiqarishga tayyor (production-ready) Telegram bot.

---

## 🌟 Asosiy Imkoniyatlar & Modullar

### 1. 🎯 Darajani Aniqlash (Placement Test)
* **6 ta CEFR darajasi**: A1, A2, B1, B2, C1, C2.
* **60 ta saralangan savollar bazasi**: Grammatika, leksika va til tushunchasi.
* **Ikki xil rejim**:
  * ⚡️ *Keng qamrovli diagnostik test*: Barcha darajalardan olingan savollar orqali real darajani aniqlash.
  * 🎯 *Darajaga ixtisoslashgan test*: Aniq bitta daraja (masalan, B1) bo'yicha 10 ta savol.
* Har bir savolga **tezkor izoh (explanation)** beriladi. Natija avtomatik hisoblanib, foydalanuvchi profiliga saqlanadi.

### 2. 📚 Darslar & Vazifalar (Homework & Quiz)
* Mavzulashtirilgan darslar (Present Simple, Past Simple, Present Perfect va h.k.).
* **Avto-tekshiriladigan testlar (Quizzes)**: Instant auto-grading va to'g'ri/noto'g'ri variantlarning pedagogik tushuntirishi.
* **Yozma vazifalar (Open-ended Writing Tasks)**: So'zlar soni, mavzuga oid kalit so'zlardan foydalanish va sintaksis tahlili orqali avtomatik baholash va namunaviy to'g'ri javobni (model answer) ko'rsatish.

### 3. 🎙 Speaking Practice Hub
* **Shadowing mashqlari**: Matnni ohang va intonatsiyaga e'tibor qaratgan holda baland ovozda o'qib berish.
* **Erkin suhbat (Free Speech) mavzulari**: 20-50 soniyalik erkin monologlar.
* **Ovozli xabarlarni tahlil qilish (Voice Handler)**: Telegram orqali yuborilgan `.ogg` ovozli xabarlarni qabul qiladi, davomiyligi, intonatsiya va nutq sur'atini baholaydi hamda foydali tavsiyalar beradi.
* **Sara manbalar integratsiyasi**: BBC 6 Minute English, British Council, ELSA Speak va VOA Learning English platformalariga to'g'ridan-to'g'ri havolalar.

### 4. 📖 Kunlik Lug'at (Vocabulary Builder)
* **Word of the Day**: So'zning so'z turkumi, CEFR darajasi, Xalqaro Fonetik Transkripsiyasi (IPA), ta'rifi, o'zbekcha tarjimasi va misollar.
* O'rganilgan so'zlarni saqlash va progress bar (`[🟦🟦⬜️⬜️] 12/20`).

### 5. ✍️ Grammar Helper (Grammar Correction Assistant)
* Foydalanuvchi ixtiyoriy inglizcha jumlani yuboradi (masalan: *"I am go to the school yesterday"*).
* Bot jumlani tahlil qiladi, xatoni topadi, to'g'ri variantni beradi (*"I went to school yesterday"*) va qoidani o'zbek tilida batafsil tushuntiradi.

### 6. 📊 Mening Profilim (My Progress & Streak)
* CEFR darajasi ko'krak nishoni (⭐️ B1 Intermediate ⭐️).
* Kunlik ketma-ketlik (🔥 Streak) hisoblagichi.
* Yechilgan testlar, uyga vazifalar, speaking mashqlari va to'plangan ballar statistikasi.
* Shaxsiy o'quv rejasi (Daily Learning Routine).

### 7. 👑 Administrator Paneli (Admin Dashboard)
* `/admin` buyrug'i yoki maxsus tugma orqali ochiladi.
* **Umumiy Statistika**: Jami foydalanuvchilar, bugungi faollar, o'rtacha test ballari, yuborilgan vazifalar soni.
* **Talabalar Ro'yxati**: CEFR darajalari (A1, A2, B1, B2, C1, C2) bo'yicha filtrlash.
* **Broadcast**: Barcha o'quvchilarga bir vaqtning o'zida e'lon va xabarlar tarqatish (avval ko'rib chiqish va tasdiqlash bilan).

---

## 🛠 Texnologik Stek

* **Til**: Python 3.11+
* **Framework**: `aiogram` 3.x (asinxron, Routers, FSMContext)
* **Ma'lumotlar Bazasi**: SQLite + `SQLAlchemy 2.0` (async) + `aiosqlite`
* **Sozlamalar**: `pydantic-settings` & `python-dotenv`
* **Deployment**: Long-Polling yoki Webhook (Render/Koyeb uchun optimallashgan aiohttp server)

---

## 🚀 O'rnatish va Ishga Tushirish (Lokal Muhitda)

### 1. Repozitoriyani yuklab oling va papkaga o'ting:
```bash
cd "c:/ingliz tili bot"
```

### 2. Python virtual muhitini yarating va faollashtiring:
```bash
python -m venv .venv

# Windows uchun:
.venv\Scripts\activate

# Linux / MacOS uchun:
source .venv/bin/activate
```

### 3. Kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

### 4. `.env` faylini sozlang:
`.env.example` faylidan nusxa olib, `.env` yarating:
```bash
cp .env.example .env
```
Fayl ichidagi qiymatlarni o'zgartiring:
```env
BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ  # @BotFather dan olingan token
ADMIN_IDS=12345678,87654321                    # O'zingizning Telegram ID raqamingiz
DATABASE_URL=sqlite+aiosqlite:///./umar_tutor.db
USE_WEBHOOK=False
PORT=8080
```

### 5. Botni ishga tushiring:
```bash
python main.py
```
*Bot avtomatik ravishda SQLite bazasi jadvallarini yaratadi va Telegramdan yangilanishlarni qabul qila boshlaydi.*

---

## ☁️ Render.com Platformasiga Bepul Joylashtirish (Deploy)

Render platformasida botni 2 xil usulda bepul ishga tushirish mumkin:

### Usul 1: Webhook orqali (Web Service) — Tavsiya etiladi!
Render'ning bepul Web Service ta'rifi 15 daqiqa harakatsizlikdan so'ng uxlaydi. Webhook rejimida Telegram har safar yangi xabar kelganda Render'ga HTTP so'rov yuboradi va servis avtomatik uyg'onadi!

1. [Render.com](https://render.com) saytida ro'yxatdan o'ting.
2. **New +** tugmasini bosing va **Web Service** ni tanlang.
3. GitHub repozitoriyangizni ulang.
4. Quyidagi parametrlarni kiriting:
   - **Name**: `umar-tutor-bot`
   - **Environment**: `Python 3` (yoki `Docker`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
5. **Environment Variables** bo'limiga quyidagilarni qo'shing:
   - `BOT_TOKEN`: Sizning bot tokeningiz
   - `ADMIN_IDS`: Telegram ID raqamingiz
   - `USE_WEBHOOK`: `True`
   - `WEBHOOK_URL`: `https://sizning-servis-nomingiz.onrender.com/webhook`
   - `PORT`: `8080`
6. **Create Web Service** tugmasini bosing. Tayyor!

### Usul 2: Background Worker orqali (Long-Polling)
Agar Long-Polling orqali doimiy ishlab turishini xohlasangiz:
- **Service Type**: Background Worker
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **USE_WEBHOOK**: `False`

---

## 🐳 Docker Orqali Ishga Tushirish

Loyihada engil `Dockerfile` va `docker-compose.yml` mavjud.

```bash
# Docker orqali build va run qilish:
docker compose up -d --build

# Loglarni ko'rish:
docker compose logs -f
```

---

## 📂 Loyiha Tuzilishi

```
c:/ingliz tili bot/
├── data/                       # Darslar, savollar va lug'atlar
│   ├── placement_test.json     # A1-C2 (60 ta savol va izohlar)
│   ├── vocabulary.json         # So'zlar kartasi va fonetikasi
│   ├── homework.json           # Darslar, testlar va writing shartlari
│   └── speaking_topics.json    # Shadowing matnlari va havolalar
├── database/                   # Ma'lumotlar bazasi
│   ├── base.py                 # SQLAlchemy 2.0 AsyncEngine
│   ├── models.py               # User, PlacementResult, Homework, Speaking
│   └── crud.py                 # Asinxron ma'lumotlar amallari
├── handlers/                   # Aiogram 3 routerlari
│   ├── start.py                # /start, menyu va qo'llanma
│   ├── testing.py              # CEFR test runner & baholash
│   ├── homework.py             # Darslar, quiz va writing
│   ├── speaking.py             # Voice handler & Shadowing
│   ├── vocabulary.py           # Word of the Day & flashcards
│   ├── grammar.py              # Grammatika xatolarini tahlil qilish
│   ├── profile.py              # Profil va streak
│   └── admin.py                # Admin boshqaruv paneli
├── keyboards/                  # Klaviaturalar va tugmalar
├── middlewares/                # DB session & User activity tracking
├── services/                   # Grammatika va ovoz baholash servislari
├── utils/                      # FSM holatlari (States)
├── config.py                   # Pydantic Settings
├── loader.py                   # Bot & Dispatcher
├── main.py                     # Entrypoint (Polling / Webhook)
├── Dockerfile                  # Konteynerlash
└── requirements.txt            # Bog'liqliklar
```

---

## 👤 Muallif & Qo'llab-quvvatlash
Loyiha: **"Umar Tutor" English Learning Bot**  
Agar savollaringiz yoki takliflaringiz bo'lsa, loyiha adminga murojaat qiling. O'qishlaringizda omad! 🇬🇧🚀
