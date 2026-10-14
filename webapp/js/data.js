// =========================================================================
// Umar Tutor & English Buddy - Unified Multi-Level Educational Dataset
// Covers: Starter, A1, A2, B1, B2, IELTS
// Modules: Vocabulary, 5-Type Quizzes, Grammar, Listening + Scripts, Reading, Shadowing, Speaking
// =========================================================================

window.APP_DATA = {
  levels: ["Starter", "A1", "A2", "B1", "B2", "IELTS"],

  // -----------------------------------------------------------------------
  // 1. VOCABULARY BUILDER
  // -----------------------------------------------------------------------
  words: [
    // Starter
    {
      id: 101,
      word: "welcome",
      phonetics: "/ˈwel.kəm/",
      partOfSpeech: "noun / verb",
      level: "Starter",
      topic: "1-mavzu: Salomlashish & Tanishuv",
      definition: "Used to greet someone arriving in a polite way.",
      example: "Welcome to our English lesson!",
      translation_uz: "xush kelibsiz, kutib olmoq"
    },
    {
      id: 102,
      word: "family",
      phonetics: "/ˈfæm.əl.i/",
      partOfSpeech: "noun",
      level: "Starter",
      topic: "2-mavzu: Oila va Uy",
      definition: "A group of people related to each other, like parents and children.",
      example: "I love spending weekend evenings with my family.",
      translation_uz: "oila, xonadon"
    },
    {
      id: 103,
      word: "beautiful",
      phonetics: "/ˈbjuː.tɪ.fəl/",
      partOfSpeech: "adjective",
      level: "Starter",
      topic: "3-mavzu: Sifatlar va Ta'rif",
      definition: "Very pleasant to look at or hear.",
      example: "Samarkand is a beautiful ancient city.",
      translation_uz: "chiroyli, go'zal"
    },
    {
      id: 104,
      word: "friend",
      phonetics: "/frend/",
      partOfSpeech: "noun",
      level: "Starter",
      topic: "1-mavzu: Salomlashish & Tanishuv",
      definition: "A person you know well and like a lot.",
      example: "He is my best friend from school.",
      translation_uz: "do'st, o'rtoq"
    },
    // A1
    {
      id: 1,
      word: "habit",
      phonetics: "/ˈhæb.ɪt/",
      partOfSpeech: "noun",
      level: "A1",
      topic: "1-mavzu: Kundalik Odatlar",
      definition: "Something you do regularly and often without thinking about it.",
      example: "Reading English every morning is a great habit.",
      translation_uz: "odat, ko'nikma"
    },
    {
      id: 2,
      word: "journey",
      phonetics: "/ˈdʒɜː.ni/",
      partOfSpeech: "noun",
      level: "A1",
      topic: "2-mavzu: Sayohat va Shaharlar",
      definition: "An act of traveling from one place to another.",
      example: "They went on a long journey across the mountains.",
      translation_uz: "sayohat, uzoq yo'l"
    },
    {
      id: 3,
      word: "delicious",
      phonetics: "/dɪˈlɪʃ.əs/",
      partOfSpeech: "adjective",
      level: "A1",
      topic: "3-mavzu: Taomlar va Restoran",
      definition: "Having a very pleasant taste or smell.",
      example: "Traditional Uzbek plov is absolutely delicious.",
      translation_uz: "mazali, totli"
    },
    {
      id: 105,
      word: "explore",
      phonetics: "/ɪkˈsplɔːr/",
      partOfSpeech: "verb",
      level: "A1",
      topic: "2-mavzu: Sayohat va Shaharlar",
      definition: "To travel around a new place to learn about it.",
      example: "We explored historic streets and bazaars.",
      translation_uz: "tadqiq qilmoq, aylanib ko'rmoq"
    },
    // A2
    {
      id: 4,
      word: "confident",
      phonetics: "/ˈkɒn.fɪ.dənt/",
      partOfSpeech: "adjective",
      level: "A2",
      topic: "1-mavzu: Shaxsiyat va Xarakter",
      definition: "Feeling sure about your own abilities and success.",
      example: "You will become more confident with daily speaking practice.",
      translation_uz: "o'ziga ishongan, dadil"
    },
    {
      id: 5,
      word: "achieve",
      phonetics: "/əˈtʃiːv/",
      partOfSpeech: "verb",
      level: "A2",
      topic: "2-mavzu: Maqsad va Yutuqlar",
      definition: "To succeed in reaching a goal through hard effort.",
      example: "Set clear goals if you want to achieve high results.",
      translation_uz: "erishmoq, zabt etmoq"
    },
    {
      id: 106,
      word: "patience",
      phonetics: "/ˈpeɪ.ʃəns/",
      partOfSpeech: "noun",
      level: "A2",
      topic: "1-mavzu: Shaxsiyat va Xarakter",
      definition: "The ability to wait or continue calmly when things take time.",
      example: "Learning a new language requires patience and consistency.",
      translation_uz: "sabr-toqat, bardosh"
    },
    // B1
    {
      id: 6,
      word: "opportunity",
      phonetics: "/ˌɒp.əˈtjuː.nə.ti/",
      partOfSpeech: "noun",
      level: "B1",
      topic: "1-mavzu: Karyera va Ish Imkoniyatlari",
      definition: "A set of circumstances that makes it possible to do something.",
      example: "Studying English gives you international job opportunities.",
      translation_uz: "imkoniyat, qulay vaziyat"
    },
    {
      id: 7,
      word: "fluency",
      phonetics: "/ˈfluː.ən.si/",
      partOfSpeech: "noun",
      level: "B1",
      topic: "2-mavzu: Til O'rganish & Muloqot",
      definition: "The ability to speak or write a language easily, well and quickly.",
      example: "Daily conversation practice leads to true fluency.",
      translation_uz: "ravonlik, erkin so'zlashuv"
    },
    {
      id: 107,
      word: "profession",
      phonetics: "/prəˈfeʃ.ən/",
      partOfSpeech: "noun",
      level: "B1",
      topic: "1-mavzu: Karyera va Ish Imkoniyatlari",
      definition: "A type of job that requires advanced education or skill.",
      example: "Teaching is one of the most respected professions.",
      translation_uz: "kasb, soha"
    },
    // B2
    {
      id: 8,
      word: "perseverance",
      phonetics: "/ˌpɜː.sɪˈvɪə.rəns/",
      partOfSpeech: "noun",
      level: "B2",
      topic: "1-mavzu: Ruhiyat va Matonat",
      definition: "Continued effort to do something despite difficulties or delays.",
      example: "Through perseverance and determination, she passed the exam with top marks.",
      translation_uz: "matonat, sabot, qat'iyat"
    },
    {
      id: 9,
      word: "resilient",
      phonetics: "/rɪˈzɪl.jənt/",
      partOfSpeech: "adjective",
      level: "B2",
      topic: "2-mavzu: Stress va Moslashuvchanlik",
      definition: "Able to recover quickly from difficult conditions or stress.",
      example: "A resilient mindset helps students overcome setbacks.",
      translation_uz: "chidamli, bukilmas, bardoshli"
    },
    {
      id: 108,
      word: "adaptable",
      phonetics: "/əˈdæp.tə.bəl/",
      partOfSpeech: "adjective",
      level: "B2",
      topic: "2-mavzu: Stress va Moslashuvchanlik",
      definition: "Able to change easily to suit new situations.",
      example: "Successful professionals are highly adaptable to changing environments.",
      translation_uz: "moslashuvchan, epchil"
    },
    // IELTS
    {
      id: 10,
      word: "ubiquitous",
      phonetics: "/juːˈbɪk.wɪ.təs/",
      partOfSpeech: "adjective",
      level: "IELTS",
      topic: "1-mavzu: Zamonaviy Texnologiyalar",
      definition: "Present, appearing, or found everywhere simultaneously.",
      example: "Smartphones have become ubiquitous in modern urban societies.",
      translation_uz: "hamma yerda mavjud, keng tarqalgan"
    },
    {
      id: 11,
      word: "exacerbate",
      phonetics: "/ɪɡˈzæs.ə.beɪt/",
      partOfSpeech: "verb",
      level: "IELTS",
      topic: "2-mavzu: Ekologiya va Iqlim Muammolari",
      definition: "To make a problem, situation or feeling worse.",
      example: "Rapid deforestation severely exacerbates global climate instability.",
      translation_uz: "og'irlashtirmoq, battar yomonlashtirmoq"
    },
    {
      id: 12,
      word: "eloquent",
      phonetics: "/ˈel.ə.kwənt/",
      partOfSpeech: "adjective",
      level: "IELTS",
      topic: "3-mavzu: Notiqlik va Akademik Yozish",
      definition: "Fluent or persuasive in speaking or writing; highly expressive.",
      example: "Her eloquent essay received the highest score from the examiners.",
      translation_uz: "notiq, ta'sirchan, nozik so'zlovchi"
    }
  ],

  // -----------------------------------------------------------------------
  // 2. 5-TYPE INTERACTIVE QUIZZES
  // Types: mcq, error_spot, text_input, scramble, gap_fill
  // -----------------------------------------------------------------------
  quizzes: [
    // Starter: MCQ
    {
      id: "q_s1",
      level: "Starter",
      type: "mcq",
      question: "Hello! My name _____ Jasur.",
      options: ["am", "is", "are", "be"],
      correct: 1,
      explanation_uz: "Egalik birlikda (My name - 'it') bo'lgani uchun 'to be' fe'lining 'is' shakli ishlatiladi."
    },
    // Starter: Scramble
    {
      id: "q_s2",
      level: "Starter",
      type: "scramble",
      question: "Jumlani to'g'ri tartibda tering:",
      words: ["from", "I", "am", "Uzbekistan"],
      correctSentence: "I am from Uzbekistan",
      explanation_uz: "Ingliz tilida ega birinchi o'rinda keladi: Ega (I) + Fe'l (am) + Predlogli birikma (from Uzbekistan)."
    },
    // A1: MCQ
    {
      id: "q_a1_1",
      level: "A1",
      type: "mcq",
      question: "She _____ at a hospital every day.",
      options: ["work", "works", "working", "worked"],
      correct: 1,
      explanation_uz: "Present Simple'da uchinchi shaxs birlik (He/She/It) uchun fe'l oxiriga -s yoki -es qo'shiladi: 'works'."
    },
    // A1: Spot the error
    {
      id: "q_a1_2",
      level: "A1",
      type: "error_spot",
      question: "Quyidagi gapda qaysi so'z xato ishlatilgan?",
      sentence: "They doesn't like cold winter weather.",
      options: ["They", "doesn't", "like", "weather"],
      correctIndex: 1,
      correctWord: "doesn't",
      fix: "don't",
      explanation_uz: "'They' ko'plik olmoshi bo'lgani sababli inkor shaklida 'doesn't' emas, balki 'don't' ishlatiladi."
    },
    // A2: Student text input
    {
      id: "q_a2_1",
      level: "A2",
      type: "text_input",
      question: "'Go' fe'lining o'tgan zamon (Past Simple - V2) shaklini yozing:",
      acceptedAnswers: ["went", "Went"],
      hint: "Bosh harfi 'w'",
      explanation_uz: "'Go' noto'g'ri (irregular) fe'l bo'lib, uning Past Simple shakli 'went' bo'ladi."
    },
    // A2: Gap fill
    {
      id: "q_a2_2",
      level: "A2",
      type: "gap_fill",
      question: "Bo'sh joyni to'ldiring: 'I was born _____ 2005.'",
      options: ["in", "on", "at", "to"],
      correct: 0,
      explanation_uz: "Yillar (2005, 1999) va oylar oldidan har doim 'in' predlogi ishlatiladi."
    },
    // B1: MCQ
    {
      id: "q_b1_1",
      level: "B1",
      type: "mcq",
      question: "If it rains tomorrow, we _____ stay at home.",
      options: ["will", "would", "had", "are"],
      correct: 0,
      explanation_uz: "Birinchi shart mayli (First Conditional): If + Present Simple, kelasi zamonda 'will + V1' bo'ladi."
    },
    // B1: Scramble
    {
      id: "q_b1_2",
      level: "B1",
      type: "scramble",
      question: "So'zlarni to'g'ri tartibda joylashtiring:",
      words: ["never", "I", "have", "been", "to", "London"],
      correctSentence: "I have never been to London",
      explanation_uz: "Present Perfect'da 'never' so'zi yordamchi 'have' va asosiy fe'l 'been' orasida keladi."
    },
    // B2: Spot the Error
    {
      id: "q_b2_1",
      level: "B2",
      type: "error_spot",
      question: "Ushbu gapdagi grammatik xato so'zni aniqlang:",
      sentence: "Despite of the heavy rain, the students arrived on time.",
      options: ["Despite", "of", "heavy", "arrived"],
      correctIndex: 1,
      correctWord: "of",
      fix: "o'chirib tashlash",
      explanation_uz: "'Despite' so'zidan keyin 'of' ishlatilmaydi! ('In spite of' yoki shunchaki 'Despite' to'g'ri bo'ladi)."
    },
    // B2: Student text input
    {
      id: "q_b2_2",
      level: "B2",
      type: "text_input",
      question: "'She would have passed if she had studied' jumlasidagi shart turi qaysi? (Raqamini yozing: 1, 2 yoki 3)",
      acceptedAnswers: ["3", "uchinchi", "third", "Third conditional"],
      hint: "Past Perfect va would have + V3",
      explanation_uz: "O'tib ketgan voqelikka pushaymonlik bildirish Third Conditional (Uchinchi shart mayli) hisoblanadi."
    },
    // IELTS: MCQ
    {
      id: "q_ielts_1",
      level: "IELTS",
      type: "mcq",
      question: "Not only _____ the scholarship, but she also secured an internship in Cambridge.",
      options: ["she won", "did she win", "she did win", "won she"],
      correct: 1,
      explanation_uz: "Inversion (Inversiya) qoidasi: 'Not only' jumla boshida kelsa, so'roq gap tartibiga o'tadi: 'did she win'."
    },
    // IELTS: Scramble
    {
      id: "q_ielts_2",
      level: "IELTS",
      type: "scramble",
      question: "IELTS C1 darajadagi murakkab jumlani to'g'ri tartibda tering:",
      words: ["Seldom", "have", "witnessed", "such", "an", "extraordinary", "I", "breakthrough"],
      correctSentence: "Seldom have I witnessed such an extraordinary breakthrough",
      explanation_uz: "Salbiy modal adverb 'Seldom' gap boshiga chiqqanda yordamchi fe'l egadan oldinga o'tadi (Seldom have I witnessed)."
    }
  ],

  // -----------------------------------------------------------------------
  // 3. LEVEL-BASED GRAMMAR TOPICS (WITH WRONG VS CORRECT & DEEP EXPLANATIONS)
  // -----------------------------------------------------------------------
  grammarTopics: [
    {
      id: "g_starter",
      level: "Starter",
      title: "To Be (am / is / are) fe'li",
      formula: "Subject + am/is/are + Noun/Adjective",
      summary: "Ingliz tilida borliq, kasb, holat va yoshni ifodalashda 'to be' ishlatiladi.",
      wrongSentence: "I have 20 years old.",
      correctSentence: "I am 20 years old.",
      explanation_uz: "O'zbek tilida 'Mening yoshim 20 da' desak ham, ingliz tilida yosh 'have' bilan emas, faqat 'to be' (am/is/are) bilan ifodalanadi.",
      examples: [
        "I am a student. (Men talabaman)",
        "She is very smart. (U juda aqlli)",
        "They are at home. (Ular uyda)"
      ]
    },
    {
      id: "g_a1",
      level: "A1",
      title: "Present Simple (Oddiy Hozirgi Zamon)",
      formula: "I/You/We/They + V1  |  He/She/It + V1 + s/es",
      summary: "Muntazam, har kuni takrorlanadigan odatiy ish-harakatlar va faktlar uchun qo'llaniladi.",
      wrongSentence: "She go to school every day.",
      correctSentence: "She goes to school every day.",
      explanation_uz: "Uchinchi shaxs birlikda (He, She, It) fe'llarga doimo -s yoki -es qo'shimchasi qo'shiladi: go -> goes, play -> plays.",
      examples: [
        "I drink tea every morning.",
        "He watches English movies on Fridays.",
        "Do you live in Tashkent?"
      ]
    },
    {
      id: "g_a2",
      level: "A2",
      title: "Past Simple (O'tgan Zamon) & Noto'g'ri Fe'llar",
      formula: "Tasdiq: Subject + V2 / Ved  |  Inkor: Subject + didn't + V1",
      summary: "O'tmishda sodir bo'lib, tugallangan aniq voqealar (yesterday, last week, ago).",
      wrongSentence: "I didn't went to the party yesterday.",
      correctSentence: "I didn't go to the party yesterday.",
      explanation_uz: "'Didn't' yordamchi fe'li o'tgan zamonni o'ziga oladi, shuning uchun asosiy fe'l o'zining boshlang'ich (V1) shakliga qaytadi.",
      examples: [
        "We bought a new car last month.",
        "Did you finish your homework?",
        "She saw an interesting bird."
      ]
    },
    {
      id: "g_b1",
      level: "B1",
      title: "Present Perfect (Tugallangan Hozirgi Zamon)",
      formula: "Subject + have/has + V3 (Past Participle)",
      summary: "O'tmishda boshlangan yoki o'tmishda bo'lgan, ammo natijasi hozirga bevosita bog'liq ish-harakatlar.",
      wrongSentence: "I have seen him yesterday.",
      correctSentence: "I saw him yesterday. (yoki: I have already seen him)",
      explanation_uz: "Agar jumlada aniq o'tgan vaqt (yesterday, 2 days ago, in 2020) aytilsa, Present Perfect emas, faqat Past Simple ishlatiladi!",
      examples: [
        "I have lived in this city for 5 years.",
        "She has just arrived from London.",
        "Have you ever eaten sushi?"
      ]
    },
    {
      id: "g_b2",
      level: "B2",
      title: "Passive Voice (Majhul Nisbat)",
      formula: "Subject + to be + V3 (Past Participle)",
      summary: "Ish-harakatni kim bajarganidan ko'ra, harakatning ob'ekti yoki natijasi muhimroq bo'lganda qo'llanadi.",
      wrongSentence: "The letter was wrote by the manager.",
      correctSentence: "The letter was written by the manager.",
      explanation_uz: "Majhul nisbatda fe'lning 2-shakli (wrote) emas, faqat 3-shakli (written - Past Participle) ishlatiladi.",
      examples: [
        "The new bridge is being built right now.",
        "Millions of emails are sent every minute.",
        "English is spoken all over the globe."
      ]
    },
    {
      id: "g_ielts",
      level: "IELTS",
      title: "Inversion (Inversiya) & Complex Structures",
      formula: "Negative Adverb + Auxiliary Verb + Subject + Main Verb",
      summary: "IELTS 7.0+ yozma va og'zaki nutqda ta'sirchanlik (emphasis) berish uchun so'z tartibini almashtirish.",
      wrongSentence: "Rarely people realise how important discipline is.",
      correctSentence: "Rarely do people realise how important discipline is.",
      explanation_uz: "'Rarely', 'Never', 'Scarcely', 'Hardly' kabi inkor ma'nodagi so'zlar jumla boshida kelsa, yordamchi fe'l egadan oldinga o'tadi.",
      examples: [
        "Under no circumstances should you share your password.",
        "Not until late at night did they reach the campsite.",
        "Had I known about the deadline, I would have submitted earlier."
      ]
    }
  ],

  // -----------------------------------------------------------------------
  // 4. LISTENING MODULE (WITH AUDIO SCRIPT REVEAL & IELTS SECTION MODES)
  // -----------------------------------------------------------------------
  listening: [
    {
      id: "list_1",
      level: "A1",
      title: "At the London Cafe",
      speaker: "Barista & Anna",
      duration: "0:45",
      dialogueAudioText: "Barista: Good morning! Welcome to London Cafe. What can I get for you?\nAnna: Hello! Can I have a hot cappuccino and a chocolate croissant, please?\nBarista: Sure. That will be three pounds fifty.\nAnna: Here you go. Thank you very much!\nBarista: Enjoy your coffee, have a lovely day!",
      script: "Barista: Good morning! Welcome to London Cafe. What can I get for you?\nAnna: Hello! Can I have a hot cappuccino and a chocolate croissant, please?\nBarista: Sure. That will be three pounds fifty.\nAnna: Here you go. Thank you very much!\nBarista: Enjoy your coffee, have a lovely day!",
      question: "What did Anna order with her coffee?",
      options: ["An apple pie", "A chocolate croissant", "A sandwich", "A tea"],
      correct: 1,
      explanation_uz: "Anna 'Can I have a hot cappuccino and a chocolate croissant, please?' deb buyurtma berdi."
    },
    {
      id: "list_2",
      level: "B1",
      title: "Airport Check-In Conversation",
      speaker: "Passenger & Gate Officer",
      duration: "1:15",
      dialogueAudioText: "Officer: Next passenger please! May I see your passport and flight booking?\nPassenger: Yes, of course. Here is my passport and boarding pass for the flight to Istanbul.\nOfficer: Thank you. Are you checking any luggage today or do you only have cabin baggage?\nPassenger: Just this one backpack for the cabin. No check-in bags.\nOfficer: Excellent. Gate number 14 is boarding in forty minutes.",
      script: "Officer: Next passenger please! May I see your passport and flight booking?\nPassenger: Yes, of course. Here is my passport and boarding pass for the flight to Istanbul.\nOfficer: Thank you. Are you checking any luggage today or do you only have cabin baggage?\nPassenger: Just this one backpack for the cabin. No check-in bags.\nOfficer: Excellent. Gate number 14 is boarding in forty minutes.",
      question: "Which gate does the passenger need to go to?",
      options: ["Gate 4", "Gate 14", "Gate 40", "Gate 24"],
      correct: 1,
      explanation_uz: "Ofitser shunday dedi: 'Gate number 14 is boarding in forty minutes.' (14-darvoza)."
    },
    {
      id: "list_3",
      level: "IELTS",
      title: "IELTS Section 3: Academic Tutorial on Climate Change",
      speaker: "Professor Clark & Student Mark",
      duration: "2:05",
      dialogueAudioText: "Professor: Good afternoon, Mark. Let's look at your draft for the environmental dissertation. Your primary methodology is sound, but your secondary data concerning solar radiation requires more current empirical backing.\nMark: I understand, Professor. I relied largely on the 2018 United Nations symposium report. Should I incorporate the latest satellite telemetry from the European Space Agency instead?\nProfessor: Precisely. That will substantiate your hypotheses about polar ice fluctuations significantly.",
      script: "Professor: Good afternoon, Mark. Let's look at your draft for the environmental dissertation. Your primary methodology is sound, but your secondary data concerning solar radiation requires more current empirical backing.\nMark: I understand, Professor. I relied largely on the 2018 United Nations symposium report. Should I incorporate the latest satellite telemetry from the European Space Agency instead?\nProfessor: Precisely. That will substantiate your hypotheses about polar ice fluctuations significantly.",
      question: "What recommendation did the professor make regarding the student's research?",
      options: [
        "Change the research topic completely",
        "Use latest European Space Agency satellite data",
        "Submit the draft immediately without changes",
        "Remove all secondary data"
      ],
      correct: 1,
      explanation_uz: "Professor talabaga Yevropa Kosmik Agentligining (ESA) eng so'nggi sun'iy yo'ldosh ma'lumotlarini kiritishni tavsiya qildi ('Precisely. That will substantiate...')."
    }
  ],

  // -----------------------------------------------------------------------
  // 5. READING COMPREHENSION MODULE
  // -----------------------------------------------------------------------
  reading: [
    {
      id: "read_1",
      level: "A1",
      title: "A Day in Tashkent",
      readingTime: "2 min",
      passage: "Tashkent is the modern capital of Uzbekistan. Millions of friendly people live in this green and sunny city. In the morning, citizens often travel on the beautiful underground metro stations. Markets like Chorsu Bazaar are full of fresh fruits, hot bread, and fragrant spices. In the evening, families gather in city parks to walk under the tall plane trees.",
      vocabHighlights: [
        { word: "capital", uz: "poytaxt" },
        { word: "fragrant", uz: "xushbo'y" },
        { word: "gather", uz: "to'planmoq" }
      ],
      question: "Where do families usually spend their evenings according to the text?",
      options: ["In metro stations", "In city parks", "At the airport", "In shopping malls"],
      correct: 1,
      explanation_uz: "Matnda aytilgan: 'In the evening, families gather in city parks to walk under the tall plane trees.'"
    },
    {
      id: "read_2",
      level: "B1",
      title: "The Power of Habit and Fluency",
      readingTime: "3 min",
      passage: "Psychologists claim that it takes around 66 days to form a permanent habit. When learning a foreign language, consistency is far more beneficial than marathon cramming sessions. Dedicating twenty focused minutes each day to listening and vocabulary retention creates neural connections that make recall effortless. Small daily actions inevitably compound into extraordinary fluency.",
      vocabHighlights: [
        { word: "consistency", uz: "muntazamlik" },
        { word: "compound", uz: "katta natijaga aylanish" }
      ],
      question: "What is considered more effective than cramming sessions?",
      options: [
        "Studying only once a month",
        "Daily consistent practice of 20 minutes",
        "Memorizing dictionary pages overnight",
        "Taking long breaks"
      ],
      correct: 1,
      explanation_uz: "Matnga binoan: 'Dedicating twenty focused minutes each day... consistency is far more beneficial'."
    },
    {
      id: "read_3",
      level: "IELTS",
      title: "IELTS Academic Reading: Artificial Intelligence in Modern Linguistics",
      readingTime: "5 min",
      passage: "Paragraph A: The proliferation of Large Language Models (LLMs) has revolutionized computational linguistics. Unlike classical rule-based algorithmic parsers, modern transformer networks utilize billions of parameters to deduce semantic nuance and syntactic coherence.\n\nParagraph B: Nevertheless, prominent cognitive linguists argue that statistical token prediction does not equate to human conceptual understanding. While an AI model can construct impeccably eloquent prose, it lacks embodied experiential awareness of the physical world. Therefore, human pedagogy remains indispensable in language acquisition.",
      vocabHighlights: [
        { word: "proliferation", uz: "tez sur'atlarda ko'payish" },
        { word: "indispensable", uz: "o'rnini bosib bo'lmaydigan, ajralmas" }
      ],
      question: "According to Paragraph B, what fundamental quality do AI models lack?",
      options: [
        "Syntactic coherence",
        "Token prediction capabilities",
        "Embodied experiential awareness of the physical world",
        "Grammatical precision"
      ],
      correct: 2,
      explanation_uz: "Matndan iqtibos: '...it lacks embodied experiential awareness of the physical world.' (Jismoniy dunyoni his qilish/tajriba)."
    }
  ],

  // -----------------------------------------------------------------------
  // 6. SHADOWING PRACTICE MODULE
  // -----------------------------------------------------------------------
  shadowing: [
    {
      id: "shad_1",
      level: "A2",
      title: "Confident English Introductions",
      videoUrl: "https://www.youtube.com/embed/dELvS6Vl9pU",
      scriptLines: [
        { start: 0, text: "Hello everyone! It is a real pleasure to meet you today.", uz: "Barchaga salom! Bugun siz bilan uchrashganimdan juda xursandman." },
        { start: 4, text: "My name is Sardor, and I have been studying English for six months.", uz: "Mening ismim Sardor, va men 6 oydan beri ingliz tilini o'rganmoqdaman." },
        { start: 9, text: "I practice speaking every single morning to improve my pronunciation.", uz: "Talaffuzimni yaxshilash uchun har tong gapirishni mashq qilaman." }
      ]
    },
    {
      id: "shad_2",
      level: "B2",
      title: "Steve Jobs: Stay Hungry, Stay Foolish",
      videoUrl: "https://www.youtube.com/embed/UF8uR6Z6KLc",
      scriptLines: [
        { start: 0, text: "Your time is limited, so don't waste it living someone else's life.", uz: "Vaqtingiz cheklangan, shuning uchun birovning hayotini yashab uni behuda sarflamang." },
        { start: 5, text: "Don't be trapped by dogma, which is living with the results of other people's thinking.", uz: "O'zgalarning fikrlari natijasi bo'lgan aqidalar tuzog'iga tushib qolmang." },
        { start: 12, text: "Have the courage to follow your heart and intuition.", uz: "Yuragingiz va ichki sezgingizga ergashishga jasoratingiz yetsin." }
      ]
    },
    {
      id: "shad_3",
      level: "IELTS",
      title: "IELTS Band 9 Speaking Sample: Globalisation & Society",
      videoUrl: "https://www.youtube.com/embed/sRfe__ne8eE",
      scriptLines: [
        { start: 0, text: "Undoubtedly, globalization has engendered unprecedented cultural exchange across continental boundaries.", uz: "Shubhasiz, globallashuv qit'alararo misli ko'rilmagan madaniy almashinuvni keltirib chiqardi." },
        { start: 7, text: "However, one cannot overlook the erosion of indigenous linguistic traditions.", uz: "Biroq, mahalliy til an'analarining yemirilishini e'tibordan chetda qoldirib bo'lmaydi." },
        { start: 14, text: "A balanced framework is therefore imperative to safeguard cultural heritage.", uz: "Shu sababli, madaniy merosni asrash uchun muvozanatli tizim o'ta zarurdir." }
      ]
    }
  ],

  // -----------------------------------------------------------------------
  // 7. SPEAKING PROMPTS & AI EVALUATION BENCHMARKS
  // -----------------------------------------------------------------------
  speakingPrompts: [
    {
      id: "sp_starter",
      level: "Starter",
      title: "O'zingiz haqida gapirib bering",
      prompt: "Introduce yourself: What is your name? Where are you from? What is your hobby? (15-30 soniya gapiring)",
      sampleBandAnswer: "Hello! My name is Anvar. I am from Tashkent, Uzbekistan. I am twenty years old. I like playing football and learning English."
    },
    {
      id: "sp_a2",
      level: "A2",
      title: "Kundalik tartibingiz (Daily Routine)",
      prompt: "Describe your typical day: When do you wake up, what do you eat, and how do you spend your evening? (30-60 soniya)",
      sampleBandAnswer: "I usually get up at 7 o'clock in the morning. After washing my face, I have a healthy breakfast with my family. Then I go to work. In the evening, I study English lessons."
    },
    {
      id: "sp_b1",
      level: "B1",
      title: "Unutilmas sayohatingiz haqida",
      prompt: "Talk about an unforgettable trip you took. Where did you go, who with, and why was it memorable? (45-60 soniya)",
      sampleBandAnswer: "Last summer, I traveled to the historic city of Bukhara with my closest friends. The magnificent architectural monuments and delicious traditional cuisine made it truly unforgettable."
    },
    {
      id: "sp_ielts",
      level: "IELTS",
      title: "IELTS Speaking Part 2: Cue Card",
      prompt: "Describe a challenge you faced and successfully overcame.\nYou should say:\n• What the challenge was\n• When and where it happened\n• How you overcame it\n• And explain what you learned from this experience (1-2 daqiqa gapiring)",
      sampleBandAnswer: "I would like to recount an occasion when I prepared for a demanding university entrance examination within a remarkably compressed timeframe..."
    }
  ],

  // -----------------------------------------------------------------------
  // 8. INITIAL LIVE MEETINGS (TEACHER CLASSES)
  // -----------------------------------------------------------------------
  initialMeetings: [
    {
      id: 1,
      title: "🔴 IELTS Speaking Band 7.5+ Masterclass",
      level: "B2 - IELTS",
      datetime_str: "Bugun, 20:30",
      meeting_link: "https://t.me/umar_tutor_bot",
      platform: "Telegram Video Dars"
    },
    {
      id: 2,
      title: "🎯 Boshlang'ichlar uchun Talaffuz va Fonetika darsi",
      level: "Starter - A1",
      datetime_str: "Ertaga, 19:00",
      meeting_link: "https://zoom.us",
      platform: "Zoom Jonli Dars"
    }
  ],

  // -----------------------------------------------------------------------
  // 9. DAILY CHECKLIST TASKS
  // -----------------------------------------------------------------------
  dailyTasks: [
    { id: 1, title: "5 ta yangi so'z o'rganish va talaffuzini eshitish", completed: true },
    { id: 2, title: "Ovoz yozib ChatGPT'dan tahlil olish", completed: false },
    { id: 3, title: "5 savolli interaktiv testni ishlash", completed: false },
    { id: 4, title: "Listening dialogini eshitib, scriptini o'qish", completed: false },
    { id: 5, title: "10 daqiqa Shadowing mashqini bajarish", completed: false }
  ]
};
