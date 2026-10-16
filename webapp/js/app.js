/**
 * Umar Tutor & English Buddy - Unified Application Engine
 * Handles: Multi-Role (Student & Teacher), 6 Levels (Starter to IELTS),
 * 5-Type Quizzes, Speaking AI Coach, Grammar Diffs, Listening with Script Reveal,
 * Reading, Shadowing, Progress Analytics, and Teacher CMS & Marking Hub.
 */

const tg = window.Telegram?.WebApp;
const ADMIN_IDS = [786373932, 8737899414, 2011411073];

// Global App State
const state = {
  currentScreen: 'screen-home',
  history: [],
  activeLevel: 'B1',
  activeRole: 'student', // 'student' or 'teacher'
  isAdmin: false,
  user: {
    id: 1,
    telegram_id: null,
    full_name: 'Foydalanuvchi',
    access_code: 'STU-1001',
    level: 'B1',
    streak_days: 1,
    skills: { vocab: 0, grammar: 0, speaking: 0, listening: 0, reading: 0, quiz: 0 },
    weak_points: [
      "Hali mashqlar bajarilmadi. Boshlash uchun o'quv bo'limlaridan birini tanlang."
    ]
  },
  // Vocab State
  vocabIndex: 0,
  vocabFilterList: [],
  selectedVocabTopic: 'all',
  // Speaking State
  isRecording: false,
  recordSeconds: 0,
  recordInterval: null,
  recognition: null,
  spokenText: "",
  mediaStream: null,
  mediaRecorder: null,
  audioChunks: [],
  recordedAudioUrl: null,
  // Quiz State
  quizList: [],
  quizIndex: 0,
  quizScore: 0,
  quizMistakes: [],
  scrambleSelected: [],
  selectedErrorToken: null,
  // Grammar State
  grammarIndex: 0,
  grammarList: [],
  // Listening State
  listeningIndex: 0,
  isListeningPlaying: false,
  listeningTimer: null,
  listeningSeconds: 0,
  // Reading & Shadowing
  readingIndex: 0,
  shadowingIndex: 0,
  shadowingLineIndex: 0,
  shadowingSpeed: 1.0,
  // Teacher Portal State
  teacherTab: 'tab-analytics',
  teacherStudents: [],
  teacherMeetings: [],
  teacherSubmissions: []
};

// =========================================================================
// APPLICATION INITIALIZATION
// =========================================================================
document.addEventListener('DOMContentLoaded', () => {
  initTelegramSDK();
  loadSavedUserSession();
  parseUrlParameters();
  loadSavedAvatar();
  initSpeechEngine();
  initWaveformCanvas();
  applyActiveLevel(state.activeLevel, false);
  fetchActiveLiveMeetings();
  fetchTeacherMaterials();
});

function initTelegramSDK() {
  if (!tg) return;
  try {
    tg.ready();
    tg.expand();
    tg.enableClosingConfirmation();
    if (tg.setHeaderColor) {
      tg.setHeaderColor('#ffffff');
      tg.setBackgroundColor('#f8fafc');
    }
    // Auto-fill Telegram user profile
    const tgUser = tg.initDataUnsafe?.user;
    if (tgUser) {
      state.user.telegram_id = tgUser.id;
      state.user.full_name = [tgUser.first_name, tgUser.last_name].filter(Boolean).join(' ') || tgUser.username || 'Foydalanuvchi';
      if (ADMIN_IDS.includes(Number(tgUser.id))) {
        state.isAdmin = true;
        localStorage.setItem('umar_tutor_is_admin', 'true');
      }
      syncUserUI();
      checkUserStatusFromBackend(tgUser.id);
    }

    if (tg.BackButton) {
      tg.BackButton.onClick(() => {
        if (state.history.length > 0) {
          const prev = state.history.pop();
          navigateScreen(prev, null, false);
        } else {
          navigateScreen('screen-home', null, false);
        }
      });
    }
  } catch (e) {
    console.log('Telegram SDK note:', e);
  }
}

async function checkUserStatusFromBackend(telegramId) {
  try {
    const res = await fetch(`/api/user-data?telegram_id=${telegramId}`);
    const data = await res.json();
    if (data && data.is_admin) {
      state.isAdmin = true;
      localStorage.setItem('umar_tutor_is_admin', 'true');
    }
    if (data && data.access_code && data.access_code !== 'STU-8821') {
      state.user = { ...state.user, ...data };
      if (data.level) applyActiveLevel(data.level, false);
    }
    syncUserUI();
  } catch (e) {}
}

function triggerHaptic(type = 'light') {
  if (tg?.HapticFeedback) {
    try {
      tg.HapticFeedback.impactOccurred(type);
    } catch (e) {}
  }
}

function loadSavedUserSession() {
  try {
    const savedRole = localStorage.getItem('umar_tutor_role');
    const savedLevel = localStorage.getItem('umar_tutor_level');
    const savedCode = localStorage.getItem('umar_tutor_code');
    const savedName = localStorage.getItem('umar_tutor_name');

    if (savedRole) state.activeRole = savedRole;
    if (savedLevel) state.activeLevel = savedLevel;
    if (savedCode) state.user.access_code = savedCode;
    if (savedName) state.user.full_name = savedName;

    updateHeaderRoleBadge();
    syncUserUI();
  } catch (e) {}
}

function parseUrlParameters() {
  try {
    const params = new URLSearchParams(window.location.search);
    const roleParam = params.get('role');
    const codeParam = params.get('code');
    const userIdParam = params.get('user_id');
    const tabParam = params.get('tab');

    if (roleParam === 'admin' || roleParam === 'teacher') {
      state.activeRole = 'teacher';
      state.isAdmin = true;
      localStorage.setItem('umar_tutor_role', 'teacher');
      localStorage.setItem('umar_tutor_is_admin', 'true');
      updateHeaderRoleBadge();
      
      const adminNotice = document.getElementById('admin-detected-notice');
      if (adminNotice) adminNotice.style.display = 'block';

      if (tabParam === 'cms') {
        navigateScreen('screen-teacher-portal');
        switchTeacherTab('tab-cms');
      } else {
        navigateScreen('screen-teacher-portal');
      }
    } else if (roleParam === 'student') {
      state.activeRole = 'student';
      localStorage.setItem('umar_tutor_role', 'student');
      updateHeaderRoleBadge();

      const isAdminSaved = localStorage.getItem('umar_tutor_is_admin') === 'true' || state.isAdmin;
      const banner = document.getElementById('admin-view-banner');
      if (banner && isAdminSaved) {
        banner.style.display = 'block';
      }
    }

    if (codeParam) {
      state.user.access_code = codeParam;
      localStorage.setItem('umar_tutor_code', codeParam);
      syncUserUI();
      fetch(`/api/user-data?code=${encodeURIComponent(codeParam)}`)
        .then(r => r.json())
        .then(data => {
          if (data && data.success !== false) {
            state.user = { ...state.user, ...data };
            if (data.is_admin) {
              state.isAdmin = true;
              localStorage.setItem('umar_tutor_is_admin', 'true');
            }
            if (data.level) applyActiveLevel(data.level, false);
            syncUserUI();
          }
        })
        .catch(() => {});
    }

    if (userIdParam) {
      state.user.telegram_id = parseInt(userIdParam);
      checkUserStatusFromBackend(userIdParam);
    }
  } catch (e) {
    console.log('URL parameters note:', e);
  }
}

function syncUserUI() {
  const homeName = document.getElementById('home-user-name');
  const homeCode = document.getElementById('home-user-code');
  const homeStreak = document.getElementById('home-streak-days');
  const homeAccuracy = document.getElementById('home-accuracy');
  const homeHeroLevel = document.getElementById('home-hero-level');
  const headerName = document.getElementById('header-user-name');
  const headerRole = document.getElementById('header-user-role-badge');
  const headerAdminBtn = document.getElementById('header-admin-btn');
  const adminQuickCard = document.getElementById('admin-quick-card');
  const adminCardTitle = document.getElementById('admin-card-title');

  const displayName = state.user.full_name || 'Foydalanuvchi';
  if (homeName) homeName.innerText = displayName;
  if (headerName) headerName.innerText = displayName;
  if (homeCode) homeCode.innerText = state.user.access_code || 'STU-1001';
  if (homeStreak) homeStreak.innerText = state.user.streak_days || 1;
  if (homeHeroLevel) homeHeroLevel.innerText = state.activeLevel || 'B1';

  const isUserAdmin = state.isAdmin || localStorage.getItem('umar_tutor_is_admin') === 'true' || (state.user.telegram_id && ADMIN_IDS.includes(Number(state.user.telegram_id)));

  if (isUserAdmin) {
    state.isAdmin = true;
    if (headerAdminBtn) {
      headerAdminBtn.style.display = 'inline-flex';
      headerAdminBtn.innerText = state.activeRole === 'teacher' ? "👨‍🎓 Talaba Ko'rinishi" : "👑 Admin";
    }
    if (adminQuickCard) {
      adminQuickCard.style.display = 'flex';
      if (adminCardTitle) {
        adminCardTitle.innerText = state.activeRole === 'teacher' ? "👑 Siz Admin Rejimidamiz" : "Admin & O'qituvchi Boshqaruvi";
      }
    }
    if (headerRole) {
      headerRole.innerText = state.activeRole === 'teacher' ? "👑 Admin" : "👑 Admin (Talaba)";
      headerRole.className = "role-badge teacher-badge";
    }
  } else {
    if (headerAdminBtn) headerAdminBtn.style.display = 'none';
    if (adminQuickCard) adminQuickCard.style.display = 'none';
    if (headerRole) {
      headerRole.innerText = "👨‍🎓 O'quvchi";
      headerRole.className = "role-badge student-badge";
    }
  }

  const skillsValues = Object.values(state.user.skills || {});
  const totalScore = skillsValues.reduce((a, b) => a + b, 0);
  const avgScore = skillsValues.length > 0 && totalScore > 0 ? Math.round(totalScore / skillsValues.length) : 0;
  if (homeAccuracy) homeAccuracy.innerText = avgScore + '%';

  const progressRing = document.getElementById('progress-overall-percent');
  if (progressRing) progressRing.innerText = avgScore + '%';
}

function toggleAdminStudentMode() {
  triggerHaptic('medium');
  if (state.activeRole === 'teacher') {
    state.activeRole = 'student';
    localStorage.setItem('umar_tutor_role', 'student');
    showToast("👨‍🎓 O'quvchi ko'rinishiga o'tildi");
    navigateScreen('screen-home');
  } else {
    state.activeRole = 'teacher';
    localStorage.setItem('umar_tutor_role', 'teacher');
    showToast("👑 Admin boshqaruv paneliga xush kelibsiz!");
    navigateScreen('screen-teacher');
  }
  syncUserUI();
}

function enterStudentViewAsAdmin() {
  state.activeRole = 'student';
  localStorage.setItem('umar_tutor_role', 'student');
  showToast("👨‍🎓 O'quvchi ko'rinishiga o'tildi");
  navigateScreen('screen-home');
  syncUserUI();
}

function returnToAdminPanel() {
  state.activeRole = 'teacher';
  localStorage.setItem('umar_tutor_role', 'teacher');
  showToast("👑 Admin boshqaruv paneliga qaytildi");
  navigateScreen('screen-teacher');
  syncUserUI();
}

// =========================================================================
// SCREEN ROUTER & NAVIGATION
// =========================================================================
function navigateScreen(targetScreenId, navEl = null, pushHistory = true) {
  triggerHaptic('light');

  const currentEl = document.getElementById(state.currentScreen);
  const targetEl = document.getElementById(targetScreenId);

  if (!targetEl) return;

  if (pushHistory && state.currentScreen !== targetScreenId) {
    state.history.push(state.currentScreen);
  }

  // Hide all screens & show target
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  targetEl.classList.add('active');
  state.currentScreen = targetScreenId;

  // Telegram BackButton visibility
  if (tg?.BackButton) {
    if (targetScreenId === 'screen-welcome' || targetScreenId === 'screen-home') {
      tg.BackButton.hide();
    } else {
      tg.BackButton.show();
    }
  }

  // Update bottom nav highlights
  document.querySelectorAll('.bottom-nav-bar .nav-item').forEach(item => item.classList.remove('active'));
  if (navEl) {
    navEl.classList.add('active');
  } else {
    // Map screen to nav item
    const navMap = {
      'screen-home': 0,
      'screen-vocab': 1,
      'screen-speaking': 2,
      'screen-quiz': 3,
      'screen-progress': 4
    };
    const navItems = document.querySelectorAll('.bottom-nav-bar .nav-item');
    if (navMap[targetScreenId] !== undefined && navItems[navMap[targetScreenId]]) {
      navItems[navMap[targetScreenId]].classList.add('active');
    }
  }

  // Refresh modules based on screen
  if (targetScreenId === 'screen-vocab') renderCurrentVocabWord();
  if (targetScreenId === 'screen-speaking') renderSpeakingPrompt();
  if (targetScreenId === 'screen-quiz') renderQuizQuestion();
  if (targetScreenId === 'screen-grammar') renderCurrentGrammarTopic();
  if (targetScreenId === 'screen-listening') renderListeningLesson();
  if (targetScreenId === 'screen-reading') renderReadingPassage();
  if (targetScreenId === 'screen-shadowing') renderShadowingLesson();
  if (targetScreenId === 'screen-progress') renderProgressStats();
  if (targetScreenId === 'screen-teacher') loadTeacherPortalData();
}

// =========================================================================
// LEVEL CONTROLLER (STARTER, A1, A2, B1, B2, IELTS)
// =========================================================================
function toggleLevelMenu() {
  const menu = document.getElementById('level-dropdown-menu');
  if (menu) menu.classList.toggle('show');
}

function changeGlobalLevel(level) {
  triggerHaptic('medium');
  toggleLevelMenu();
  applyActiveLevel(level, true);
}

function applyActiveLevel(level, sendToApi = true) {
  state.activeLevel = level;
  localStorage.setItem('umar_tutor_level', level);

  const label = document.getElementById('current-level-label');
  if (label) label.innerText = level;

  const heroLevel = document.getElementById('home-hero-level');
  if (heroLevel) heroLevel.innerText = level;

  // Filter datasets
  state.vocabIndex = 0;
  state.quizIndex = 0;
  state.quizMistakes = [];
  state.grammarIndex = 0;

  // Update level chips across screens
  ['vocab', 'speaking', 'quiz', 'grammar', 'listening', 'reading', 'shadowing'].forEach(id => {
    const chip = document.getElementById(`${id}-level-chip`);
    if (chip) chip.innerText = level;
  });

  // Re-render active screen
  if (state.currentScreen === 'screen-vocab') renderCurrentVocabWord();
  if (state.currentScreen === 'screen-quiz') renderQuizQuestion();
  if (state.currentScreen === 'screen-grammar') renderCurrentGrammarTopic();
  if (state.currentScreen === 'screen-listening') renderListeningLesson();
  if (state.currentScreen === 'screen-reading') renderReadingPassage();
  if (state.currentScreen === 'screen-shadowing') renderShadowingLesson();

  if (sendToApi && state.user.telegram_id) {
    fetch('/api/update-level', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ telegram_id: state.user.telegram_id, level })
    }).catch(() => {});
  }
}

// =========================================================================
// REGISTRATION, LOGIN & ADMIN VIEW CONTROLLER
// =========================================================================
function openRegisterModal() {
  triggerHaptic('light');
  const modal = document.getElementById('register-modal');
  if (modal) modal.style.display = 'flex';
  const nameInput = document.getElementById('reg-student-name');
  if (nameInput && !nameInput.value && state.user.full_name !== 'Talaba') {
    nameInput.value = state.user.full_name;
  }
}

function closeRegisterModal() {
  const modal = document.getElementById('register-modal');
  if (modal) modal.style.display = 'none';
}

function openLoginModal() {
  triggerHaptic('light');
  const modal = document.getElementById('login-modal');
  if (modal) modal.style.display = 'flex';
  if (state.isAdmin) {
    const notice = document.getElementById('admin-detected-notice');
    if (notice) notice.style.display = 'block';
  }
}

function closeLoginModal() {
  const modal = document.getElementById('login-modal');
  if (modal) modal.style.display = 'none';
}

function switchLoginRole(role) {
  triggerHaptic('light');
  const tabStu = document.getElementById('login-tab-student');
  const tabTeach = document.getElementById('login-tab-teacher');
  const formStu = document.getElementById('login-student-form');
  const formTeach = document.getElementById('login-teacher-form');

  if (tabStu) tabStu.classList.toggle('active', role === 'student');
  if (tabTeach) tabTeach.classList.toggle('active', role === 'teacher');
  if (formStu) formStu.style.display = role === 'student' ? 'block' : 'none';
  if (formTeach) formTeach.style.display = role === 'teacher' ? 'block' : 'none';
}

async function submitStudentRegister() {
  triggerHaptic('heavy');
  const name = document.getElementById('reg-student-name')?.value.trim();
  const level = document.getElementById('reg-student-level')?.value || 'Starter';
  const customCode = document.getElementById('reg-student-code')?.value.trim();

  if (!name) {
    alert("Iltimos, ism va familiyangizni kiriting!");
    return;
  }

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        full_name: name,
        level: level,
        code: customCode,
        telegram_id: state.user.telegram_id
      })
    });
    const data = await res.json();
    if (data.success && data.user) {
      state.user = { ...state.user, ...data.user };
      state.activeRole = 'student';
      state.isAdminStudentView = false;
      localStorage.setItem('umar_tutor_role', 'student');
      localStorage.setItem('umar_tutor_code', data.user.access_code);
      localStorage.setItem('umar_tutor_name', data.user.full_name);
      localStorage.setItem('umar_tutor_level', data.user.level);

      applyActiveLevel(data.user.level, false);
      closeRegisterModal();
      updateHeaderRoleBadge();
      syncUserUI();
      alert(`🎉 Tabriklaymiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n🔑 Sizning shaxsiy kodingiz: ${data.user.access_code}\n\nUshbu kodni eslab qoling, keyingi safar kirishda shu koddan foydalanasiz!`);
      navigateScreen('screen-home');
    } else {
      alert(data.message || "Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.");
    }
  } catch (e) {
    alert("Server bilan bog'lanishda xatolik. Qaytadan urinib ko'ring.");
  }
}

async function submitStudentLogin() {
  triggerHaptic('heavy');
  const code = document.getElementById('login-student-code')?.value.trim();
  if (!code) {
    alert("Iltimos, shaxsiy kodingizni kiriting!");
    return;
  }

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        role: 'student',
        code: code,
        telegram_id: state.user.telegram_id
      })
    });
    const data = await res.json();
    if (data.success && data.user) {
      state.user = { ...state.user, ...data.user };
      state.activeRole = 'student';
      state.isAdminStudentView = false;
      localStorage.setItem('umar_tutor_role', 'student');
      localStorage.setItem('umar_tutor_code', state.user.access_code);
      localStorage.setItem('umar_tutor_name', state.user.full_name);
      if (state.user.level) {
        applyActiveLevel(state.user.level, false);
      }
      closeLoginModal();
      updateHeaderRoleBadge();
      syncUserUI();
      navigateScreen('screen-home');
    } else {
      alert(data.message || "Bunday kodli o'quvchi topilmadi! Iltimos, kodni to'g'ri kiriting yoki ro'yxatdan o'ting.");
    }
  } catch (e) {
    alert("Server bilan bog'lanishda xatolik.");
  }
}

async function submitTeacherLogin(asStudentView = false) {
  triggerHaptic('heavy');
  const pass = document.getElementById('login-teacher-password')?.value.trim();

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        role: 'teacher',
        password: pass,
        telegram_id: state.user.telegram_id
      })
    });
    const data = await res.json();
    if (data.success) {
      state.isAdmin = true;
      localStorage.setItem('umar_tutor_is_admin', 'true');
      closeLoginModal();

      if (asStudentView) {
        enterStudentViewAsAdmin();
      } else {
        state.activeRole = 'teacher';
        state.isAdminStudentView = false;
        localStorage.setItem('umar_tutor_role', 'teacher');
        updateHeaderRoleBadge();
        navigateScreen('screen-teacher');
      }
    } else {
      alert(data.message || "Noto'g'ri o'qituvchi paroli! (Parol: UMAR2026)");
    }
  } catch (e) {
    if (pass === 'UMAR2026' || pass === 'admin' || state.isAdmin) {
      state.isAdmin = true;
      closeLoginModal();
      if (asStudentView) {
        enterStudentViewAsAdmin();
      } else {
        state.activeRole = 'teacher';
        state.isAdminStudentView = false;
        updateHeaderRoleBadge();
        navigateScreen('screen-teacher');
      }
    } else {
      alert("Noto'g'ri o'qituvchi paroli! (Parol: UMAR2026)");
    }
  }
}

function enterStudentViewAsAdmin() {
  triggerHaptic('medium');
  state.isAdminStudentView = true;
  state.activeRole = 'student';
  const banner = document.getElementById('admin-view-banner');
  if (banner) banner.style.display = 'block';
  updateHeaderRoleBadge();
  navigateScreen('screen-home');
}

function returnToAdminPanel() {
  triggerHaptic('heavy');
  state.isAdminStudentView = false;
  state.activeRole = 'teacher';
  const banner = document.getElementById('admin-view-banner');
  if (banner) banner.style.display = 'none';
  updateHeaderRoleBadge();
  navigateScreen('screen-teacher');
}

function openAuthModal() {
  openLoginModal();
}

function closeAuthModal() {
  closeLoginModal();
}

function handleTeacherEntry() {
  if (state.activeRole === 'teacher' || state.isAdmin) {
    navigateScreen('screen-teacher');
  } else {
    openLoginModal();
    switchLoginRole('teacher');
  }
}

function updateHeaderRoleBadge() {
  const badge = document.getElementById('header-user-role-badge');
  if (!badge) return;
  if (state.activeRole === 'teacher') {
    badge.className = 'role-badge teacher-badge';
    badge.innerText = "👨‍🏫 O'qituvchi";
  } else {
    badge.className = 'role-badge student-badge';
    badge.innerText = state.isAdminStudentView ? "👑 Admin (O'quvchi)" : "👨‍🎓 O'quvchi";
  }
}

// =========================================================================
// 1. VOCABULARY MODULE (AUDIO TTS & POST-STUDY QUIZ)
// =========================================================================
function getFilteredWords() {
  const allWords = window.APP_DATA?.words || [];
  let levelWords = allWords.filter(w => w.level === state.activeLevel);
  if (levelWords.length === 0) levelWords = allWords;

  if (state.selectedVocabTopic && state.selectedVocabTopic !== 'all') {
    const topicFiltered = levelWords.filter(w => w.topic === state.selectedVocabTopic);
    if (topicFiltered.length > 0) return topicFiltered;
  }
  return levelWords;
}

function updateVocabTopicDropdown() {
  const select = document.getElementById('vocab-topic-select');
  if (!select) return;

  const allWords = window.APP_DATA?.words || [];
  const levelWords = allWords.filter(w => w.level === state.activeLevel);
  const topics = Array.from(new Set(levelWords.map(w => w.topic).filter(Boolean)));

  let html = `<option value="all">Barcha dars mavzulari (${levelWords.length} ta so'z)</option>`;
  topics.forEach(t => {
    const count = levelWords.filter(w => w.topic === t).length;
    const isSelected = state.selectedVocabTopic === t ? 'selected' : '';
    html += `<option value="${t}" ${isSelected}>${t} (${count} ta)</option>`;
  });
  select.innerHTML = html;
}

function onVocabTopicChange() {
  triggerHaptic('light');
  const select = document.getElementById('vocab-topic-select');
  if (select) {
    state.selectedVocabTopic = select.value;
    state.vocabIndex = 0;
    renderCurrentVocabWord();
  }
}

function renderCurrentVocabWord() {
  updateVocabTopicDropdown();
  const words = getFilteredWords();
  if (words.length === 0) return;

  if (state.vocabIndex >= words.length) state.vocabIndex = 0;
  if (state.vocabIndex < 0) state.vocabIndex = words.length - 1;

  const current = words[state.vocabIndex];

  document.getElementById('vocab-word').innerText = current.word;
  document.getElementById('vocab-phonetics').innerText = current.phonetics;
  document.getElementById('vocab-pos').innerText = current.partOfSpeech;
  document.getElementById('vocab-translation').innerText = current.translation_uz;
  document.getElementById('vocab-definition').innerText = current.definition;
  document.getElementById('vocab-example').innerText = `"${current.example}"`;
  document.getElementById('vocab-counter').innerText = `${state.vocabIndex + 1} / ${words.length}`;
  document.getElementById('vocab-level-chip').innerText = current.level;

  const topicTag = document.getElementById('vocab-topic-tag');
  if (topicTag) {
    topicTag.innerText = current.topic || `${current.level} Mavzusi`;
  }
}

function prevVocabWord() {
  triggerHaptic('light');
  state.vocabIndex--;
  renderCurrentVocabWord();
}

function nextVocabWord() {
  triggerHaptic('light');
  state.vocabIndex++;
  renderCurrentVocabWord();
}

function markWordLearned() {
  triggerHaptic('medium');
  state.user.skills.vocab = Math.min(100, state.user.skills.vocab + 2);
  alert("So'z o'rganilgan deb belgilandi! Lug'at balingiz oshdi ✨");
  nextVocabWord();
}

function playWordAudio(wordText, buttonEl = null) {
  if (!wordText) return;
  triggerHaptic('medium');

  const btn = buttonEl || document.getElementById('btn-speak-vocab');
  if (btn) btn.classList.add('playing');

  const cleanWord = encodeURIComponent(wordText.trim().replace(/[^a-zA-Z\s-]/g, ''));
  const googleTtsUrl = `https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q=${cleanWord}`;
  const dictTtsUrl = `https://api.dictionaryapi.dev/media/pronunciations/en/${cleanWord.toLowerCase()}-us.mp3`;

  const audio = new Audio();
  let finished = false;

  const cleanup = () => {
    if (!finished) {
      finished = true;
      if (btn) btn.classList.remove('playing');
    }
  };

  audio.onended = cleanup;
  audio.onerror = () => {
    // Try secondary dictionary audio
    const secondaryAudio = new Audio(dictTtsUrl);
    secondaryAudio.onended = cleanup;
    secondaryAudio.onerror = () => {
      // Fallback to SpeechSynthesis
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(wordText);
        utterance.lang = 'en-US';
        utterance.rate = 0.85;
        utterance.onend = cleanup;
        utterance.onerror = cleanup;
        window.speechSynthesis.speak(utterance);
      } else {
        cleanup();
      }
    };
    secondaryAudio.play().catch(() => {
      // If secondary audio fails to play, speech synth fallback
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(wordText);
        utterance.lang = 'en-US';
        utterance.rate = 0.85;
        utterance.onend = cleanup;
        utterance.onerror = cleanup;
        window.speechSynthesis.speak(utterance);
      } else {
        cleanup();
      }
    });
  };

  audio.src = googleTtsUrl;
  audio.play().catch(err => {
    console.log("Direct play catch, trying fallback:", err);
    audio.onerror();
  });

  // Safety timer to remove animation
  setTimeout(cleanup, 2500);
}

function playCurrentWordAudio() {
  const words = getFilteredWords();
  const current = words[state.vocabIndex];
  if (!current) return;
  playWordAudio(current.word, document.getElementById('btn-speak-vocab'));
}

function startVocabSpecificQuiz() {
  triggerHaptic('heavy');
  // Generate dynamic vocab quiz questions based on active level words
  const words = getFilteredWords();
  const generatedQuiz = words.map((w, idx) => {
    // Generate 3 fake options
    const otherWords = window.APP_DATA.words.filter(ow => ow.word !== w.word);
    const fake1 = otherWords[(idx + 1) % otherWords.length].translation_uz;
    const fake2 = otherWords[(idx + 2) % otherWords.length].translation_uz;
    const fake3 = otherWords[(idx + 3) % otherWords.length].translation_uz;

    const options = [w.translation_uz, fake1, fake2, fake3].sort(() => Math.random() - 0.5);
    const correctIdx = options.indexOf(w.translation_uz);

    return {
      id: `vq_${w.id}`,
      level: w.level,
      type: 'mcq',
      question: `"${w.word}" so'zining to'g'ri o'zbekcha tarjimasi qaysi?`,
      options: options,
      correct: correctIdx,
      explanation_uz: `"${w.word}" (${w.phonetics}) so'zining ma'nosi: ${w.translation_uz}. Misol: ${w.example}`
    };
  });

  state.quizList = generatedQuiz;
  state.quizIndex = 0;
  state.quizScore = 0;
  state.quizMistakes = [];
  navigateScreen('screen-quiz');
}

// =========================================================================
// 2. SPEAKING PRACTICE (CHATGPT AI FEEDBACK ENGINE)
// =========================================================================
function renderSpeakingPrompt() {
  const prompts = window.APP_DATA?.speakingPrompts || [];
  const activePrompt = prompts.find(p => p.level === state.activeLevel) || prompts[0];

  document.getElementById('speaking-prompt-title').innerText = activePrompt.title;
  document.getElementById('speaking-prompt-desc').innerText = activePrompt.prompt;
  document.getElementById('speaking-level-chip').innerText = activePrompt.level;
}

function initSpeechEngine() {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRec) {
    try {
      state.recognition = new SpeechRec();
      state.recognition.continuous = true;
      state.recognition.interimResults = true;
      state.recognition.lang = 'en-US';

      state.recognition.onresult = (event) => {
        let fullTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          fullTranscript += event.results[i][0].transcript + ' ';
        }
        state.spokenText = fullTranscript.trim();
        const liveBox = document.getElementById('speaking-live-transcript-box');
        const liveText = document.getElementById('speaking-live-transcript-text');
        if (liveBox && liveText && state.spokenText) {
          liveBox.style.display = 'block';
          liveText.innerText = state.spokenText;
        }
      };

      state.recognition.onerror = (e) => {
        console.log('Speech recognition event:', e?.error || e);
        // CRITICAL FIX: NEVER call stopSpeakingRecord() on error!
        // In mobile WebViews, silence triggers 'no-speech' error after 2s which must be ignored.
      };

      state.recognition.onend = () => {
        // If recording is still active, restart SpeechRecognition automatically
        if (state.isRecording) {
          try {
            state.recognition.start();
          } catch (e) {}
        }
      };
    } catch (e) {
      console.log('Speech engine error:', e);
    }
  }
}

function toggleSpeakingRecord() {
  if (state.isRecording) {
    stopSpeakingRecord();
  } else {
    startSpeakingRecord();
  }
}

function startSpeakingRecord() {
  triggerHaptic('heavy');
  state.isRecording = true;
  state.recordSeconds = 0;
  state.spokenText = "";
  state.audioChunks = [];

  const btn = document.getElementById('mic-toggle-btn');
  const status = document.getElementById('recording-status');
  const timerEl = document.getElementById('recording-timer');
  const feedbackCard = document.getElementById('speaking-ai-feedback-card');
  const playerBox = document.getElementById('student-voice-playback-box');
  const liveBox = document.getElementById('speaking-live-transcript-box');
  const liveText = document.getElementById('speaking-live-transcript-text');

  if (btn) btn.classList.add('recording');
  if (status) status.innerText = "Tinglamoqda... Gapiring (ingliz tilida)";
  if (feedbackCard) feedbackCard.style.display = 'none';
  if (playerBox) playerBox.style.display = 'none';
  if (liveBox) liveBox.style.display = 'none';
  if (liveText) liveText.innerText = '...';

  // Request microphone and start MediaRecorder for student playback
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      state.mediaStream = stream;
      try {
        state.mediaRecorder = new MediaRecorder(stream);
        state.mediaRecorder.ondataavailable = (e) => {
          if (e.data && e.data.size > 0) state.audioChunks.push(e.data);
        };
        state.mediaRecorder.onstop = () => {
          if (state.audioChunks.length > 0) {
            const blob = new Blob(state.audioChunks, { type: 'audio/webm' });
            state.recordedAudioUrl = URL.createObjectURL(blob);
            const player = document.getElementById('student-voice-audio');
            const box = document.getElementById('student-voice-playback-box');
            if (player && box) {
              player.src = state.recordedAudioUrl;
              box.style.display = 'block';
            }
          }
          if (state.mediaStream) {
            state.mediaStream.getTracks().forEach(t => t.stop());
          }
        };
        state.mediaRecorder.start();
      } catch (err) {
        console.log("MediaRecorder init note:", err);
      }
    }).catch(err => {
      console.log("Microphone access note:", err);
    });
  }

  state.recordInterval = setInterval(() => {
    state.recordSeconds++;
    const mins = String(Math.floor(state.recordSeconds / 60)).padStart(2, '0');
    const secs = String(state.recordSeconds % 60).padStart(2, '0');
    if (timerEl) timerEl.innerText = `${mins}:${secs}`;

    // Auto-stop after 90 seconds
    if (state.recordSeconds >= 90) stopSpeakingRecord();
  }, 1000);

  if (state.recognition) {
    try {
      state.recognition.start();
    } catch (e) {}
  }
}

function stopSpeakingRecord() {
  triggerHaptic('medium');
  state.isRecording = false;
  clearInterval(state.recordInterval);

  const btn = document.getElementById('mic-toggle-btn');
  const status = document.getElementById('recording-status');
  if (btn) btn.classList.remove('recording');
  if (status) status.innerText = "Audio tahlil qilinmoqda (ChatGPT AI)... ⏳";

  if (state.mediaRecorder && state.mediaRecorder.state !== 'inactive') {
    try {
      state.mediaRecorder.stop();
    } catch (e) {}
  }

  if (state.recognition) {
    try {
      state.recognition.stop();
    } catch (e) {}
  }

  // Analyze speaking
  analyzeSpeakingTranscript();
}

function submitManualSpeakingText() {
  triggerHaptic('medium');
  const inputEl = document.getElementById('manual-speaking-text');
  const text = (inputEl?.value || "").trim();
  if (!text) {
    alert("Iltimos, avval mavzuga mos javobingizni yozing!");
    return;
  }
  state.spokenText = text;
  const status = document.getElementById('recording-status');
  if (status) status.innerText = "Yozma javob tahlil qilinmoqda (ChatGPT AI)... ⏳";
  analyzeSpeakingTranscript();
}

async function analyzeSpeakingTranscript() {
  let userText = (state.spokenText || "").trim();
  const promptTitle = document.getElementById('speaking-prompt-title')?.innerText || "Speaking";

  try {
    const res = await fetch('/api/speaking/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: userText,
        level: state.activeLevel,
        prompt_title: promptTitle,
        telegram_id: state.user.telegram_id
      })
    });
    const feedback = await res.json();
    renderSpeakingAIFeedback(feedback);
  } catch (e) {
    // Client-side realistic evaluator
    const words = userText.split(/\s+/).filter(Boolean);
    const wc = words.length;

    if (wc === 0) {
      renderSpeakingAIFeedback({
        score: 25,
        band: "2.5 - 3.0",
        status: "poor",
        transcription: "Nutq aniqlanmadi (ovoz eshitilmadi)",
        word_count: 0,
        has_error: true,
        relevance_badge: "❌ Savolga javob berilmadi",
        relevance_desc: "Hech qanday ovoz yoki matn kiritilmadi.",
        grammar_errors: [{
          original: "-",
          corrected: "Iltimos, mikrofonni yoqib ovoz chiqarib gapiring yoki matn yozing",
          reason_uz: "Ovoz aniqlanmadi yoki mikrofon ruxsati berilmagan."
        }],
        pronunciation_tip: "❌ Ovoz aniqlanmadi. Qaytadan urinib ko'ring.",
        feedback_uz: "Birorta ham so'z eshitilmadi. Mikrofon tugmasini bosib, balandroq gapiring yoki pastda matn sifatida yozing."
      });
    } else if (wc < 4) {
      renderSpeakingAIFeedback({
        score: 40,
        band: "3.5 - 4.0",
        status: "poor",
        transcription: userText,
        word_count: wc,
        has_error: true,
        relevance_badge: "⚠️ Qisman javob berildi",
        relevance_desc: "Nutq juda qisqa bo'lgani sababli savol to'liq ochilmadi.",
        grammar_errors: [{
          original: userText,
          corrected: "Mavzu bo'yicha to'liq gap tuzing (Subject + Verb + Object)",
          reason_uz: "Nutq juda qisqa bo'lgani sababli to'liq baholab bo'lmadi."
        }],
        pronunciation_tip: "⚠️ Qisqa ibora. Kamida 2-3 ta to'liq gap tuzish tavsiya etiladi.",
        feedback_uz: `Siz atigi ${wc} ta so'z aytdingiz ('${userText}'). ChatGPT tahlili uchun to'liqroq gapiring!`
      });
    } else {
      let score = 72;
      let status = "warning";
      let band = "5.5 - 6.0";
      let grammarErrors = [];

      const lower = userText.toLowerCase();
      if (lower.includes("he go") || lower.includes("she go")) {
        grammarErrors.push({ original: "he/she go", corrected: "he/she goes", reason_uz: "Present Simple 3-shaxsda fe'lga -s/es qo'shiladi." });
      }
      if (lower.includes("i are")) {
        grammarErrors.push({ original: "I are", corrected: "I am", reason_uz: "I olmoshi bilan 'am' ishlatiladi." });
      }
      if (lower.includes("yesterday i go")) {
        grammarErrors.push({ original: "yesterday I go", corrected: "yesterday I went", reason_uz: "O'tgan zamon (Past Simple) uchun went kerak." });
      }

      if (grammarErrors.length > 0) {
        score = 55;
        status = "poor";
        band = "4.5 - 5.0";
      } else if (wc >= 12) {
        score = 86;
        status = "good";
        band = "6.5 - 7.0";
      }

      renderSpeakingAIFeedback({
        score: score,
        band: band,
        status: status,
        transcription: userText,
        word_count: wc,
        has_error: grammarErrors.length > 0,
        relevance_badge: "✅ To'liq javob berildi",
        relevance_desc: "Berilgan mavzu bo'yicha fikr ifodalandi.",
        grammar_errors: grammarErrors,
        pronunciation_tip: grammarErrors.length > 0 ? "⚠️ Intonatsiya va so'z urg'ulariga e'tibor qarating." : "✅ Aniq va tushunarli talaffuz.",
        feedback_uz: grammarErrors.length > 0
          ? "Nutqingizda xatolar aniqlandi. Xatolarni to'g'rilab, qayta mashq qiling!"
          : "Juda yaxshi! Fikr ravon ifodalangan."
      });
    }
  }

  const status = document.getElementById('recording-status');
  if (status) status.innerText = "Tahlil yakunlandi! Natijalarni pastda ko'ring 👇";
}

function renderSpeakingAIFeedback(feedback) {
  const card = document.getElementById('speaking-ai-feedback-card');
  if (!card) return;

  const scoreNum = document.getElementById('feedback-score-num');
  const scoreCircle = document.getElementById('feedback-score-circle');
  if (scoreNum) scoreNum.innerText = feedback.score;

  const status = feedback.status || (feedback.score < 60 ? 'poor' : feedback.score < 75 ? 'warning' : 'good');
  if (scoreCircle) {
    scoreCircle.className = `score-badge-circle ${status}`;
  }

  const statusBanner = document.getElementById('feedback-status-banner');
  const statusIcon = document.getElementById('feedback-status-icon');
  const statusText = document.getElementById('feedback-status-text');
  if (statusBanner) {
    statusBanner.className = `feedback-status-banner ${status}`;
    statusBanner.style.display = 'flex';
    if (status === 'poor') {
      if (statusIcon) statusIcon.innerText = '❌';
      if (statusText) statusText.innerText = "Xatolar ko'p yoki qoniqarsiz — Qaytadan mashq qiling!";
    } else if (status === 'warning') {
      if (statusIcon) statusIcon.innerText = '⚠️';
      if (statusText) statusText.innerText = "O'rtacha natija — Yaxshilash kerak";
    } else {
      if (statusIcon) statusIcon.innerText = '✅';
      if (statusText) statusText.innerText = "Ajoyib natija! Ravon va aniq nutq";
    }
  }

  const relBadge = document.getElementById('feedback-relevance-badge');
  const relDesc = document.getElementById('feedback-relevance-desc');
  if (relBadge && feedback.relevance_badge) {
    relBadge.innerText = feedback.relevance_badge;
  }
  if (relDesc && feedback.relevance_desc) {
    relDesc.innerText = feedback.relevance_desc;
  }

  document.getElementById('feedback-band').innerText = feedback.band;
  document.getElementById('feedback-words-count').innerText = `${feedback.word_count || 0} ta`;
  document.getElementById('feedback-transcription-text').innerText = `"${feedback.transcription}"`;
  document.getElementById('feedback-pronunciation-tip').innerText = feedback.pronunciation_tip;
  document.getElementById('feedback-coach-text').innerText = feedback.feedback_uz;

  const errList = document.getElementById('feedback-grammar-list');
  if (errList) {
    if (feedback.grammar_errors && feedback.grammar_errors.length > 0) {
      errList.innerHTML = feedback.grammar_errors.map(err => `
        <div class="feedback-error-item" style="border-left: 3px solid #ef4444; padding-left: 8px; margin-bottom: 8px;">
          <div><span class="error-orig" style="color: #fca5a5; text-decoration: line-through;">${err.original}</span> ➔ <span class="error-corr" style="color: #86efac; font-weight: bold;">${err.corrected}</span></div>
          <div class="error-why">💡 ${err.reason_uz}</div>
        </div>
      `).join('');
    } else if (feedback.score < 60) {
      errList.innerHTML = `<div style="color: #fca5a5; font-size: 13px;">❌ Nutq hajmi yetarli bo'lmadi yoki jiddiy xatolar aniqlandi.</div>`;
    } else {
      errList.innerHTML = `<div style="color: #86efac; font-size: 13px;">✅ Ajoyib! Grammatik xatolar topilmadi.</div>`;
    }
  }

  card.style.display = 'block';
  state.user.skills.speaking = feedback.score;
}


// Canvas waveform generator
function initWaveformCanvas() {
  const canvas = document.getElementById('waveform-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function draw() {
    requestAnimationFrame(draw);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const centerY = canvas.height / 2;
    const numBars = 36;
    const barWidth = 4;
    const gap = (canvas.width - (numBars * barWidth)) / (numBars - 1);

    for (let i = 0; i < numBars; i++) {
      let height = 4;
      if (state.isRecording) {
        height = Math.sin(Date.now() / 150 + i * 0.4) * 22 + Math.random() * 12 + 6;
      }
      ctx.fillStyle = state.isRecording ? '#38bdf8' : 'rgba(255, 255, 255, 0.15)';
      ctx.fillRect(i * (barWidth + gap), centerY - height / 2, barWidth, height);
    }
  }
  draw();
}

// =========================================================================
// 3. 5-TYPE QUIZZES ENGINE (MCQ, ERROR SPOT, TEXT, SCRAMBLE, GAP FILL)
// =========================================================================
function getFilteredQuizzes() {
  if (state.quizList && state.quizList.length > 0) return state.quizList;
  const allQuizzes = window.APP_DATA?.quizzes || [];
  const levelQuizzes = allQuizzes.filter(q => q.level === state.activeLevel);
  return levelQuizzes.length > 0 ? levelQuizzes : allQuizzes;
}

function renderQuizQuestion() {
  const quizzes = getFilteredQuizzes();
  const summaryCard = document.getElementById('quiz-summary-card');
  const container = document.getElementById('quiz-interactive-body');
  const submitActionRow = document.getElementById('quiz-submit-action-row');

  dismissMistakeCard();

  if (state.quizIndex >= quizzes.length) {
    // Show summary
    if (summaryCard) {
      summaryCard.style.display = 'block';
      const pct = Math.round((state.quizScore / quizzes.length) * 100);
      document.getElementById('quiz-final-score-text').innerText = `${pct}%`;
      // Update Quiz skill %
      state.user.skills.quiz = pct;
      syncQuizResultToServer(pct);
    }
    document.querySelector('.quiz-container-card').style.display = 'none';
    return;
  }

  if (summaryCard) summaryCard.style.display = 'none';
  document.querySelector('.quiz-container-card').style.display = 'block';

  const q = quizzes[state.quizIndex];
  document.getElementById('quiz-question-title').innerText = q.question;
  document.getElementById('quiz-progress-text').innerText = `${state.quizIndex + 1} / ${quizzes.length}`;
  document.getElementById('quiz-streak-counter').innerText = `🔥 ${state.quizScore} to'g'ri`;

  // Render question type label
  const typeMap = {
    mcq: "Standart Test",
    scramble: "So'z Tartibi (Scramble)",
    error_spot: "Xato Gapni Topish",
    text_input: "O'zingiz Yozadigan Savol",
    gap_fill: "Bo'sh Joyni To'ldirish"
  };
  document.getElementById('quiz-type-label').innerText = typeMap[q.type] || "Savol";

  container.innerHTML = "";
  submitActionRow.style.display = 'none';

  // TYPE 1: MCQ (Standard Test)
  if (q.type === 'mcq') {
    container.innerHTML = `
      <div class="quiz-options-list">
        ${q.options.map((opt, idx) => `
          <button class="quiz-option-btn" onclick="handleMcqChoice(${idx}, this)">
            <span style="opacity: 0.6;">${String.fromCharCode(65 + idx)}.</span> ${opt}
          </button>
        `).join('')}
      </div>
    `;
  }
  // TYPE 2: SCRAMBLE (Word Order Arrangement)
  else if (q.type === 'scramble') {
    state.scrambleSelected = [];
    container.innerHTML = `
      <div id="scramble-slots" class="scramble-slots-box">
        <span style="font-size: 12px; color: var(--text-dim);">So'zlarni bosib jumlani tartiblang...</span>
      </div>
      <div id="scramble-source" class="scramble-source-box">
        ${q.words.map((w, idx) => `
          <button class="scramble-chip" data-idx="${idx}" onclick="handleScrambleClick('${w}', this)">${w}</button>
        `).join('')}
      </div>
      <div style="margin-top: 10px;">
        <button class="btn-secondary" style="font-size: 12px;" onclick="resetScramble()">Qayta terish ↺</button>
      </div>
    `;
    submitActionRow.style.display = 'block';
  }
  // TYPE 3: ERROR SPOT (Spot the mistake in sentence)
  else if (q.type === 'error_spot') {
    container.innerHTML = `
      <div class="error-sentence-box">
        ${q.sentence.split(' ').map((word, idx) => {
          const cleanWord = word.replace(/[^a-zA-Z'’]/g, '');
          const isSelectable = q.options.some(opt => opt.toLowerCase() === cleanWord.toLowerCase());
          return `
            <span class="error-word-token ${isSelectable ? 'selectable' : ''}" 
                  onclick="${isSelectable ? `handleErrorWordSelect('${cleanWord}', this)` : ''}">
              ${word}
            </span>
          `;
        }).join('')}
      </div>
      <div style="font-size: 12px; color: var(--text-dim);">Xato deb hisoblagan so'zingiz ustiga bosing</div>
    `;
    submitActionRow.style.display = 'block';
  }
  // TYPE 4: TEXT INPUT (Student types the word)
  else if (q.type === 'text_input') {
    container.innerHTML = `
      <div style="margin-bottom: 12px;">
        <input id="quiz-student-input" class="quiz-text-input" type="text" placeholder="Javobingizni bu yerga yozing..." autocomplete="off">
        ${q.hint ? `<div style="font-size: 11px; color: #93c5fd; margin-top: 4px;">💡 Maslahat: ${q.hint}</div>` : ''}
      </div>
    `;
    submitActionRow.style.display = 'block';
  }
  // TYPE 5: GAP FILL (Fill the blank)
  else if (q.type === 'gap_fill') {
    container.innerHTML = `
      <div class="quiz-options-list">
        ${q.options.map((opt, idx) => `
          <button class="quiz-option-btn" onclick="handleGapFillChoice(${idx}, '${opt}', this)">
            <span style="opacity: 0.6;">${String.fromCharCode(65 + idx)}.</span> ${opt}
          </button>
        `).join('')}
      </div>
    `;
  }
}

// Handler: MCQ Choice
function handleMcqChoice(chosenIdx, btn) {
  triggerHaptic('medium');
  const quizzes = getFilteredQuizzes();
  const q = quizzes[state.quizIndex];

  document.querySelectorAll('.quiz-option-btn').forEach(b => b.disabled = true);

  if (chosenIdx === q.correct) {
    btn.classList.add('correct');
    state.quizScore++;
    setTimeout(() => {
      state.quizIndex++;
      renderQuizQuestion();
    }, 1000);
  } else {
    btn.classList.add('wrong');
    const correctBtn = document.querySelectorAll('.quiz-option-btn')[q.correct];
    if (correctBtn) correctBtn.classList.add('correct');

    showMistakeCard({
      userAnswer: q.options[chosenIdx],
      correctAnswer: q.options[q.correct],
      explanation: q.explanation_uz,
      questionText: q.question
    });
  }
}

// Handler: Gap Fill Choice
function handleGapFillChoice(chosenIdx, chosenWord, btn) {
  triggerHaptic('medium');
  const quizzes = getFilteredQuizzes();
  const q = quizzes[state.quizIndex];

  document.querySelectorAll('.quiz-option-btn').forEach(b => b.disabled = true);

  if (chosenIdx === q.correct) {
    btn.classList.add('correct');
    state.quizScore++;
    setTimeout(() => {
      state.quizIndex++;
      renderQuizQuestion();
    }, 1000);
  } else {
    btn.classList.add('wrong');
    const correctBtn = document.querySelectorAll('.quiz-option-btn')[q.correct];
    if (correctBtn) correctBtn.classList.add('correct');

    showMistakeCard({
      userAnswer: chosenWord,
      correctAnswer: q.options[q.correct],
      explanation: q.explanation_uz,
      questionText: q.question
    });
  }
}

// Handler: Scramble Chips
function handleScrambleClick(word, btn) {
  triggerHaptic('light');
  btn.style.display = 'none';
  state.scrambleSelected.push(word);

  const slotContainer = document.getElementById('scramble-slots');
  slotContainer.innerHTML = state.scrambleSelected.map(w => `<span class="scramble-chip in-slot">${w}</span>`).join('');
}

function resetScramble() {
  state.scrambleSelected = [];
  document.getElementById('scramble-slots').innerHTML = `<span style="font-size: 12px; color: var(--text-dim);">So'zlarni bosib jumlani tartiblang...</span>`;
  document.querySelectorAll('#scramble-source .scramble-chip').forEach(b => b.style.display = 'inline-block');
}

// Handler: Error Word Select
function handleErrorWordSelect(word, el) {
  triggerHaptic('light');
  document.querySelectorAll('.error-word-token').forEach(e => e.classList.remove('selected'));
  el.classList.add('selected');
  state.selectedErrorToken = word;
}

// Submit for Scramble, Error Spot, and Text Input
function submitCurrentInteractiveAnswer() {
  triggerHaptic('medium');
  const quizzes = getFilteredQuizzes();
  const q = quizzes[state.quizIndex];

  if (q.type === 'scramble') {
    const studentSentence = state.scrambleSelected.join(' ');
    if (studentSentence.toLowerCase() === q.correctSentence.toLowerCase()) {
      state.quizScore++;
      alert("✅ Barakalla! To'g'ri so'z tartibi.");
      state.quizIndex++;
      renderQuizQuestion();
    } else {
      showMistakeCard({
        userAnswer: studentSentence || "(bo'sh)",
        correctAnswer: q.correctSentence,
        explanation: q.explanation_uz,
        questionText: q.question
      });
    }
  } else if (q.type === 'error_spot') {
    if (!state.selectedErrorToken) {
      alert("Iltimos, avval xato so'zni tanlang!");
      return;
    }
    if (state.selectedErrorToken.toLowerCase() === q.correctWord.toLowerCase()) {
      state.quizScore++;
      alert(`✅ To'g'ri topdingiz! "${q.correctWord}" so'zi xato edi.`);
      state.quizIndex++;
      renderQuizQuestion();
    } else {
      showMistakeCard({
        userAnswer: state.selectedErrorToken,
        correctAnswer: q.correctWord,
        explanation: q.explanation_uz,
        questionText: q.sentence
      });
    }
  } else if (q.type === 'text_input') {
    const studentInput = document.getElementById('quiz-student-input')?.value.trim() || "";
    const isCorrect = q.acceptedAnswers.some(ans => ans.toLowerCase() === studentInput.toLowerCase());

    if (isCorrect) {
      state.quizScore++;
      alert("✅ Ajoyib! Javobingiz to'g'ri.");
      state.quizIndex++;
      renderQuizQuestion();
    } else {
      showMistakeCard({
        userAnswer: studentInput || "(hech narsa yozilmadi)",
        correctAnswer: q.acceptedAnswers[0],
        explanation: q.explanation_uz,
        questionText: q.question
      });
    }
  }
}

// Show Instant Mistake Card
function showMistakeCard({ userAnswer, correctAnswer, explanation, questionText }) {
  triggerHaptic('heavy');
  const card = document.getElementById('quiz-mistake-card');
  if (!card) return;

  document.getElementById('mistake-user-answer').innerText = userAnswer;
  document.getElementById('mistake-correct-answer').innerText = correctAnswer;
  document.getElementById('mistake-explanation-text').innerText = explanation;

  // Track mistake
  state.quizMistakes.push({
    question_text: questionText,
    user_answer: userAnswer,
    correct_answer: correctAnswer,
    explanation: explanation,
    category: "quiz",
    level: state.activeLevel
  });

  card.style.display = 'block';
}

function dismissMistakeCard() {
  const card = document.getElementById('quiz-mistake-card');
  if (card && card.style.display === 'block') {
    card.style.display = 'none';
    state.quizIndex++;
    renderQuizQuestion();
  }
}

function restartCurrentQuiz() {
  state.quizIndex = 0;
  state.quizScore = 0;
  state.quizMistakes = [];
  renderQuizQuestion();
}

function syncQuizResultToServer(score) {
  if (state.user.telegram_id) {
    fetch('/api/quiz/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        telegram_id: state.user.telegram_id,
        score: score,
        mistakes: state.quizMistakes
      })
    }).catch(() => {});
  }
}

// =========================================================================
// 4. GRAMMAR MODULE & LIVE AI CHECKER
// =========================================================================
function getFilteredGrammar() {
  const allGrammar = window.APP_DATA?.grammarTopics || [];
  const levelGrammar = allGrammar.filter(g => g.level === state.activeLevel);
  return levelGrammar.length > 0 ? levelGrammar : allGrammar;
}

function renderCurrentGrammarTopic() {
  const topics = getFilteredGrammar();
  if (topics.length === 0) return;

  if (state.grammarIndex >= topics.length) state.grammarIndex = 0;
  if (state.grammarIndex < 0) state.grammarIndex = topics.length - 1;

  const g = topics[state.grammarIndex];
  document.getElementById('grammar-topic-title').innerText = g.title;
  document.getElementById('grammar-topic-formula').innerText = g.formula;
  document.getElementById('grammar-topic-summary').innerText = g.summary;
  document.getElementById('grammar-wrong-sentence').innerText = g.wrongSentence;
  document.getElementById('grammar-correct-sentence').innerText = g.correctSentence;
  document.getElementById('grammar-explanation-uz').innerText = g.explanation_uz;

  const exList = document.getElementById('grammar-examples-list');
  if (exList && g.examples) {
    exList.innerHTML = g.examples.map(ex => `<li>${ex}</li>`).join('');
  }
}

function prevGrammarTopic() {
  triggerHaptic('light');
  state.grammarIndex--;
  renderCurrentGrammarTopic();
}

function nextGrammarTopic() {
  triggerHaptic('light');
  state.grammarIndex++;
  renderCurrentGrammarTopic();
}

async function checkCustomSentenceGrammar() {
  const input = document.getElementById('grammar-input-text');
  const sentence = input?.value.trim();
  if (!sentence) {
    alert("Iltimos, tahlil qilish uchun jumla kiriting!");
    return;
  }

  const resultBox = document.getElementById('grammar-live-result-box');
  resultBox.style.display = 'block';
  resultBox.innerHTML = `<div style="color: var(--text-muted); font-size: 13px;">Sun'iy intellekt tahlil qilmoqda... ⚡</div>`;

  try {
    const res = await fetch('/api/check-grammar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: sentence })
    });
    const result = await res.json();
    if (result.has_error) {
      resultBox.innerHTML = `
        <div class="diff-comparison-box">
          <div class="diff-card diff-wrong">
            <span class="diff-tag wrong-tag">❌ Aniqlangan XATO:</span>
            <div>${result.original}</div>
          </div>
          <div class="diff-card diff-correct">
            <span class="diff-tag correct-tag">✅ TO'G'RI VARIANT:</span>
            <div>${result.corrected}</div>
          </div>
        </div>
        <div class="grammar-deep-explanation">
          <div class="deep-exp-title">💡 Qoida va Tushuntirish:</div>
          <p class="deep-exp-text">${result.message}</p>
        </div>
      `;
    } else {
      resultBox.innerHTML = `
        <div style="background: rgba(34, 197, 94, 0.15); border: 1px solid #22c55e; border-radius: var(--radius-md); padding: 14px; color: #86efac;">
          ✅ Gapda hech qanday grammatik xatolik topilmadi! Barakalla.
        </div>
      `;
    }
  } catch (e) {
    resultBox.innerHTML = `<div style="color: #f87171;">Server bilan aloqada xatolik.</div>`;
  }
}

// =========================================================================
// 5. LISTENING STUDIO (AUDIO SCRIPT REVEAL & IELTS)
// =========================================================================
function getFilteredListening() {
  const allList = window.APP_DATA?.listening || [];
  const levelList = allList.filter(l => l.level === state.activeLevel);
  return levelList.length > 0 ? levelList : allList;
}

function renderListeningLesson() {
  const lessons = getFilteredListening();
  const current = lessons[state.listeningIndex] || lessons[0];
  if (!current) return;

  document.getElementById('listening-lesson-title').innerText = current.title;
  document.getElementById('listening-speakers-text').innerText = `${current.speaker} • ${current.duration}`;
  document.getElementById('listening-question-text').innerText = current.question;
  document.getElementById('listening-script-content').innerText = current.script;

  // Options
  const optContainer = document.getElementById('listening-options-container');
  optContainer.innerHTML = current.options.map((opt, idx) => `
    <button class="quiz-option-btn" onclick="handleListeningAnswer(${idx}, ${current.correct}, '${current.explanation_uz}', this)">
      <span style="opacity: 0.6;">${String.fromCharCode(65 + idx)}.</span> ${opt}
    </button>
  `).join('');

  // Reset script box
  const scriptBox = document.getElementById('listening-script-box');
  if (scriptBox) scriptBox.style.display = 'none';
  const feedback = document.getElementById('listening-feedback-msg');
  if (feedback) feedback.style.display = 'none';
}

function toggleListeningAudio() {
  triggerHaptic('medium');
  const lessons = getFilteredListening();
  const current = lessons[state.listeningIndex] || lessons[0];
  const btn = document.getElementById('btn-play-listening');

  if (state.isListeningPlaying) {
    state.isListeningPlaying = false;
    btn.innerText = "▶";
    clearInterval(state.listeningTimer);
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  } else {
    state.isListeningPlaying = true;
    btn.innerText = "⏸";

    // Play dialog via SpeechSynthesis
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(current.dialogueAudioText);
      utterance.lang = 'en-US';
      utterance.rate = 0.9;
      utterance.onend = () => {
        state.isListeningPlaying = false;
        btn.innerText = "▶";
      };
      window.speechSynthesis.speak(utterance);
    }

    // Simulate progress slider
    state.listeningSeconds = 0;
    const bar = document.getElementById('audio-progress-bar');
    const label = document.getElementById('audio-time-label');

    state.listeningTimer = setInterval(() => {
      state.listeningSeconds++;
      const pct = Math.min(100, (state.listeningSeconds / 45) * 100);
      if (bar) bar.style.width = `${pct}%`;
      const mins = String(Math.floor(state.listeningSeconds / 60)).padStart(1, '0');
      const secs = String(state.listeningSeconds % 60).padStart(2, '0');
      if (label) label.innerText = `${mins}:${secs}`;
      if (pct >= 100) clearInterval(state.listeningTimer);
    }, 1000);
  }
}

function handleListeningAnswer(chosenIdx, correctIdx, explanation, btn) {
  triggerHaptic('medium');
  document.querySelectorAll('#listening-options-container .quiz-option-btn').forEach(b => b.disabled = true);

  const feedback = document.getElementById('listening-feedback-msg');
  feedback.style.display = 'block';

  if (chosenIdx === correctIdx) {
    btn.classList.add('correct');
    feedback.innerHTML = `<span style="color: #86efac; font-weight: 700;">✅ To'g'ri javob!</span> ${explanation}`;
    state.user.skills.listening = Math.min(100, state.user.skills.listening + 4);
  } else {
    btn.classList.add('wrong');
    document.querySelectorAll('#listening-options-container .quiz-option-btn')[correctIdx].classList.add('correct');
    feedback.innerHTML = `<span style="color: #fca5a5; font-weight: 700;">❌ Noto'g'ri.</span> ${explanation}`;
  }

  // Automatically reveal script so student can read along
  const scriptBox = document.getElementById('listening-script-box');
  if (scriptBox) scriptBox.style.display = 'block';
}

function toggleListeningScript() {
  triggerHaptic('light');
  const box = document.getElementById('listening-script-box');
  if (box) {
    box.style.display = box.style.display === 'none' ? 'block' : 'none';
  }
}

// =========================================================================
// 6. READING HUB & 7. SHADOWING
// =========================================================================
function renderReadingPassage() {
  const readings = window.APP_DATA?.reading || [];
  const current = readings.find(r => r.level === state.activeLevel) || readings[0];
  if (!current) return;

  document.getElementById('reading-article-title').innerText = current.title;
  document.getElementById('reading-time-badge').innerText = `⏱ ${current.readingTime}`;
  document.getElementById('reading-article-body').innerText = current.passage;
  document.getElementById('reading-question-text').innerText = current.question;

  // Vocab chips
  const chipsContainer = document.getElementById('reading-vocab-chips');
  if (chipsContainer && current.vocabHighlights) {
    chipsContainer.innerHTML = current.vocabHighlights.map(vh => `
      <span class="vocab-chip-item"><b>${vh.word}</b>: ${vh.uz}</span>
    `).join('');
  }

  // Questions
  const optContainer = document.getElementById('reading-options-container');
  optContainer.innerHTML = current.options.map((opt, idx) => `
    <button class="quiz-option-btn" onclick="handleReadingAnswer(${idx}, ${current.correct}, '${current.explanation_uz}', this)">
      <span style="opacity: 0.6;">${String.fromCharCode(65 + idx)}.</span> ${opt}
    </button>
  `).join('');
}

function handleReadingAnswer(chosenIdx, correctIdx, explanation, btn) {
  triggerHaptic('medium');
  document.querySelectorAll('#reading-options-container .quiz-option-btn').forEach(b => b.disabled = true);

  const feedback = document.getElementById('reading-feedback-msg');
  feedback.style.display = 'block';

  if (chosenIdx === correctIdx) {
    btn.classList.add('correct');
    feedback.innerHTML = `<span style="color: #86efac; font-weight: 700;">✅ To'g'ri javob!</span> ${explanation}`;
    state.user.skills.reading = Math.min(100, state.user.skills.reading + 3);
  } else {
    btn.classList.add('wrong');
    document.querySelectorAll('#reading-options-container .quiz-option-btn')[correctIdx].classList.add('correct');
    feedback.innerHTML = `<span style="color: #fca5a5; font-weight: 700;">❌ Noto'g'ri.</span> ${explanation}`;
  }
}

// Shadowing
function renderShadowingLesson() {
  const shadows = window.APP_DATA?.shadowing || [];
  const current = shadows.find(s => s.level === state.activeLevel) || shadows[0];
  if (!current) return;

  document.getElementById('shadowing-title').innerText = current.title;
  const frame = document.getElementById('shadowing-video-frame');
  if (frame && current.videoUrl) frame.src = current.videoUrl;

  state.shadowingLineIndex = 0;
  renderCurrentShadowingLine();

  const linesContainer = document.getElementById('shadowing-all-lines');
  if (linesContainer && current.scriptLines) {
    linesContainer.innerHTML = current.scriptLines.map((line, idx) => `
      <div class="shadow-line-item ${idx === 0 ? 'active' : ''}" onclick="selectShadowingLine(${idx})">
        <div><b>${idx + 1}.</b> ${line.text}</div>
        <div style="color: #86efac; font-size: 11px;">${line.uz}</div>
      </div>
    `).join('');
  }
}

function renderCurrentShadowingLine() {
  const shadows = window.APP_DATA?.shadowing || [];
  const current = shadows.find(s => s.level === state.activeLevel) || shadows[0];
  if (!current || !current.scriptLines) return;

  const line = current.scriptLines[state.shadowingLineIndex] || current.scriptLines[0];
  document.getElementById('shadowing-en-line').innerText = `"${line.text}"`;
  document.getElementById('shadowing-uz-line').innerText = `"${line.uz}"`;
}

function selectShadowingLine(idx) {
  state.shadowingLineIndex = idx;
  renderCurrentShadowingLine();
  document.querySelectorAll('.shadow-line-item').forEach((el, i) => {
    el.classList.toggle('active', i === idx);
  });
  speakCurrentShadowingLine();
}

function speakCurrentShadowingLine() {
  triggerHaptic('light');
  const shadows = window.APP_DATA?.shadowing || [];
  const current = shadows.find(s => s.level === state.activeLevel) || shadows[0];
  if (!current || !current.scriptLines) return;
  const line = current.scriptLines[state.shadowingLineIndex];

  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(line.text);
    utterance.lang = 'en-US';
    utterance.rate = state.shadowingSpeed;
    window.speechSynthesis.speak(utterance);
  }
}

function repeatShadowingLine() {
  speakCurrentShadowingLine();
}

function setShadowingSpeed(speed, btn) {
  state.shadowingSpeed = speed;
  document.querySelectorAll('.speed-pill').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

// =========================================================================
// 8. PROGRESS & AI WEAK POINTS RECOMMENDATIONS
// =========================================================================
function renderProgressStats() {
  const skills = state.user.skills;
  const avg = Math.round(Object.values(skills).reduce((a, b) => a + b, 0) / 6);

  document.getElementById('progress-overall-percent').innerText = `${avg}%`;
  document.getElementById('progress-level-badge').innerText = `${state.activeLevel} Level`;

  // Circular ring offset
  const ring = document.getElementById('overall-ring-progress');
  if (ring) {
    const strokeDash = 314;
    const offset = strokeDash - (strokeDash * (avg / 100));
    ring.style.strokeDashoffset = offset;
  }

  // 6 skill values
  ['vocab', 'grammar', 'speaking', 'listening', 'reading', 'quiz'].forEach(s => {
    const valEl = document.getElementById(`skill-val-${s}`);
    const barEl = document.getElementById(`skill-bar-${s}`);
    if (valEl) valEl.innerText = `${skills[s]}%`;
    if (barEl) barEl.style.width = `${skills[s]}%`;
  });

  // Weak points
  const weakContainer = document.getElementById('weak-points-list');
  if (weakContainer) {
    const list = state.user.weak_points || [];
    weakContainer.innerHTML = list.map(item => `
      <div class="weak-point-item">📌 ${item}</div>
    `).join('');
  }
}

// =========================================================================
// 9. TEACHER & ADMIN PORTAL (ERROR ANALYTICS, CMS, MEETINGS, MARKING)
// =========================================================================
function switchTeacherTab(tabId, btn) {
  triggerHaptic('light');
  document.querySelectorAll('.teacher-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.teacher-tab-pane').forEach(p => p.classList.remove('active'));

  btn.classList.add('active');
  const pane = document.getElementById(tabId);
  if (pane) pane.classList.add('active');

  state.teacherTab = tabId;
  if (tabId === 'tab-analytics') loadTeacherAnalytics();
  if (tabId === 'tab-cms') { renderCmsFormFields(); loadCmsExistingMaterialsList(); }
  if (tabId === 'tab-meetings') loadTeacherMeetings();
  if (tabId === 'tab-marking') loadTeacherSubmissions();
  if (tabId === 'tab-avatar') loadSavedAvatar();
}

function loadTeacherPortalData() {
  loadTeacherAnalytics();
  renderCmsFormFields();
  loadCmsExistingMaterialsList();
}

async function loadTeacherAnalytics() {
  try {
    const res = await fetch('/api/teacher/analytics');
    const data = await res.json();

    document.getElementById('teacher-stat-users').innerText = data.total_users || 8;
    document.getElementById('teacher-stat-active').innerText = data.active_today || 3;
    document.getElementById('teacher-stat-mistakes').innerText = data.total_mistakes || 16;

    // Render top error questions
    const errContainer = document.getElementById('teacher-top-errors-list');
    if (errContainer) {
      if (data.top_mistakes && data.top_mistakes.length > 0) {
        errContainer.innerHTML = data.top_mistakes.map(m => `
          <div class="error-item-card">
            <div><b>Savol:</b> "${m.question}"</div>
            <div style="color: #86efac; margin: 2px 0;">To'g'ri javob: ${m.correct_answer}</div>
            <div style="font-size: 11px; color: #fca5a5;">Xato soni: ${m.error_count} marta • 💡 ${m.explanation}</div>
          </div>
        `).join('');
      } else {
        errContainer.innerHTML = `
          <div class="error-item-card">
            <div><b>Savol:</b> "She _____ at a hospital every day."</div>
            <div style="color: #86efac; margin: 2px 0;">To'g'ri javob: works</div>
            <div style="font-size: 11px; color: #fca5a5;">Xato soni: 6 marta • 💡 Present Simple 3-shaxsda -s qo'shiladi</div>
          </div>
        `;
      }
    }

    // Load student roster
    const rosterRes = await fetch('/api/teacher/students');
    const students = await rosterRes.json();
    const rosterTable = document.getElementById('teacher-students-table');
    if (rosterTable && students.length > 0) {
      rosterTable.innerHTML = students.map(s => `
        <div class="student-row-item">
          <div>
            <b>${s.full_name}</b>
            <div style="font-size: 11px; color: var(--accent-cyan);">${s.access_code} • ${s.level}</div>
          </div>
          <div style="text-align: right;">
            <b style="color: #38bdf8;">${s.avg_score}%</b>
            <div style="font-size: 10px; color: var(--text-dim);">Streak: 🔥 ${s.streak_days}</div>
          </div>
        </div>
      `).join('');
    }
  } catch (e) {}
}

function renderCmsFormFields() {
  const cat = document.getElementById('cms-category-select')?.value || 'vocab';
  const container = document.getElementById('cms-dynamic-fields-container');
  if (!container) return;

  if (cat === 'vocab') {
    container.innerHTML = `
      <div class="form-group"><label class="form-label">Dars / Mavzu Nomi:</label><input id="cms-v-topic" class="form-input" placeholder="Masalan: 3-dars: Texnologiya va Internet"></div>
      <div class="form-group"><label class="form-label">Inglizcha So'z:</label><input id="cms-v-word" class="form-input" placeholder="Masalan: comprehensive"></div>
      <div class="form-group"><label class="form-label">Fonetika (IPA):</label><input id="cms-v-ph" class="form-input" placeholder="/ˌkɒm.prɪˈhen.sɪv/"></div>
      <div class="form-group"><label class="form-label">O'zbekcha Tarjimasi:</label><input id="cms-v-uz" class="form-input" placeholder="har tomonlama, to'liq"></div>
      <div class="form-group"><label class="form-label">Inglizcha Ta'rif (Definition):</label><input id="cms-v-def" class="form-input" placeholder="Complete and including everything that is necessary"></div>
      <div class="form-group"><label class="form-label">Misol Jumla (Example):</label><input id="cms-v-ex" class="form-input" placeholder="We offer a comprehensive English course."></div>
    `;
  } else if (cat === 'quiz') {
    container.innerHTML = `
      <div class="form-group"><label class="form-label">Savol Matni:</label><input id="cms-q-text" class="form-input" placeholder="She didn't _____ to school."></div>
      <div class="form-group"><label class="form-label">Savol Turi:</label>
        <select id="cms-q-type" class="form-input">
          <option value="mcq">Standart Variantli (MCQ)</option>
          <option value="error_spot">Xato Gapni Topish</option>
          <option value="text_input">Student Yozadigan</option>
          <option value="gap_fill">Bo'sh Joyni To'ldirish</option>
        </select>
      </div>
      <div class="form-group"><label class="form-label">Variantlar (vergul bilan ajrating):</label><input id="cms-q-opts" class="form-input" placeholder="go, went, gone, goes"></div>
      <div class="form-group"><label class="form-label">To'g'ri Javob (yoki raqami):</label><input id="cms-q-corr" class="form-input" placeholder="go (yoki 0)"></div>
      <div class="form-group"><label class="form-label">O'zbekcha Tushuntirish (Explanation):</label><input id="cms-q-exp" class="form-input" placeholder="Didn't dan keyin fe'lning 1-shakli keladi"></div>
    `;
  } else if (cat === 'grammar') {
    container.innerHTML = `
      <div class="form-group"><label class="form-label">Mavzu Nomi:</label><input id="cms-g-title" class="form-input" placeholder="Second Conditional"></div>
      <div class="form-group"><label class="form-label">Qoida / Formula:</label><input id="cms-g-formula" class="form-input" placeholder="If + Past Simple, would + V1"></div>
      <div class="form-group"><label class="form-label">Ko'p Uchraydigan Xato Gap:</label><input id="cms-g-wrong" class="form-input" placeholder="If I have money, I would buy a car."></div>
      <div class="form-group"><label class="form-label">To'g'ri Gap:</label><input id="cms-g-correct" class="form-input" placeholder="If I had money, I would buy a car."></div>
      <div class="form-group"><label class="form-label">O'zbekcha Chuqur Tushuntirish:</label><textarea id="cms-g-exp" class="form-input" style="height: 60px;" placeholder="Hozirgi paytdagi xayoliy holatlar uchun..."></textarea></div>
    `;
  } else if (cat === 'listening') {
    container.innerHTML = `
      <div class="form-group"><label class="form-label">Dars Nomi:</label><input id="cms-l-title" class="form-input" placeholder="Job Interview Dialog"></div>
      <div class="form-group"><label class="form-label">Audio Matn (Suhbat):</label><textarea id="cms-l-dialog" class="form-input" style="height: 70px;" placeholder="Interviewer: Welcome..."></textarea></div>
      <div class="form-group"><label class="form-label">Transkript (Script):</label><textarea id="cms-l-script" class="form-input" style="height: 70px;" placeholder="To'liq matn..."></textarea></div>
      <div class="form-group"><label class="form-label">Tushunish Savoli:</label><input id="cms-l-q" class="form-input" placeholder="What position is being offered?"></div>
    `;
  } else if (cat === 'reading') {
    container.innerHTML = `
      <div class="form-group"><label class="form-label">Maqola Sarlavhasi:</label><input id="cms-r-title" class="form-input" placeholder="The Future of Renewable Energy"></div>
      <div class="form-group"><label class="form-label">O'qish Matni (Passage):</label><textarea id="cms-r-text" class="form-input" style="height: 90px;" placeholder="Solar energy is becoming..."></textarea></div>
      <div class="form-group"><label class="form-label">Savol:</label><input id="cms-r-q" class="form-input" placeholder="Why is solar energy growing?"></div>
    `;
  } else if (cat === 'shadowing') {
    container.innerHTML = `
      <div class="form-group"><label class="form-label">Dars Nomi:</label><input id="cms-s-title" class="form-input" placeholder="TED Talk: The Skill of Self Confidence"></div>
      <div class="form-group"><label class="form-label">Video Havolasi (YouTube Embed):</label><input id="cms-s-url" class="form-input" placeholder="https://www.youtube.com/embed/..."></div>
      <div class="form-group"><label class="form-label">Subtitr Qatori (Inglizcha):</label><input id="cms-s-line-en" class="form-input" placeholder="Confidence is a skill that can be developed."></div>
      <div class="form-group"><label class="form-label">Subtitr Qatori (O'zbekcha):</label><input id="cms-s-line-uz" class="form-input" placeholder="O'ziga ishonch rivojlantirish mumkin bo'lgan mahoratdir."></div>
    `;
  }
}

async function submitCmsContent() {
  triggerHaptic('heavy');
  const cat = document.getElementById('cms-category-select').value;
  const level = document.getElementById('cms-level-select').value;

  let payload = {};
  let title = "Yangi dars";

  if (cat === 'vocab') {
    title = document.getElementById('cms-v-word')?.value.trim();
    if (!title) { alert("Iltimos, so'zni kiriting!"); return; }
    const topic = document.getElementById('cms-v-topic')?.value.trim() || `${level} Mavzusi`;
    payload = {
      word: title,
      topic: topic,
      phonetics: document.getElementById('cms-v-ph')?.value.trim() || "/.../",
      translation_uz: document.getElementById('cms-v-uz')?.value.trim() || "",
      definition: document.getElementById('cms-v-def')?.value.trim() || "",
      example: document.getElementById('cms-v-ex')?.value.trim() || ""
    };
    window.APP_DATA.words.push({ id: Date.now(), level, partOfSpeech: "noun", ...payload });
    updateVocabTopicDropdown();
  } else if (cat === 'quiz') {
    title = document.getElementById('cms-q-text')?.value.trim();
    if (!title) { alert("Iltimos, savol matnini kiriting!"); return; }
    const opts = document.getElementById('cms-q-opts')?.value.split(',').map(s => s.trim()).filter(Boolean) || ["A", "B", "C", "D"];
    const corr = document.getElementById('cms-q-corr')?.value.trim() || opts[0];
    const corrIdx = opts.indexOf(corr) >= 0 ? opts.indexOf(corr) : 0;
    payload = {
      question: title,
      type: document.getElementById('cms-q-type')?.value || 'mcq',
      options: opts,
      correct: corrIdx,
      explanation_uz: document.getElementById('cms-q-exp')?.value.trim() || "To'g'ri javob berildi."
    };
    window.APP_DATA.quizzes.push({ id: `q_${Date.now()}`, level, ...payload });
  } else if (cat === 'grammar') {
    title = document.getElementById('cms-g-title')?.value.trim();
    if (!title) { alert("Iltimos, grammatika mavzusi nomini kiriting!"); return; }
    payload = {
      title: title,
      formula: document.getElementById('cms-g-formula')?.value.trim() || "Grammar Rule",
      summary: document.getElementById('cms-g-exp')?.value.trim() || "Mavzu qoidasi",
      wrongSentence: document.getElementById('cms-g-wrong')?.value.trim() || "",
      correctSentence: document.getElementById('cms-g-correct')?.value.trim() || "",
      explanation_uz: document.getElementById('cms-g-exp')?.value.trim() || "Qoidaga ko'ra to'g'ri shakli.",
      examples: [
        { en: document.getElementById('cms-g-correct')?.value.trim() || title, uz: "Namuna gap" }
      ]
    };
    window.APP_DATA.grammarTopics.push({ id: Date.now(), level, ...payload });
  } else if (cat === 'listening') {
    title = document.getElementById('cms-l-title')?.value.trim();
    if (!title) { alert("Iltimos, dars nomini kiriting!"); return; }
    payload = {
      title: title,
      audioDuration: "1:00",
      dialog: document.getElementById('cms-l-dialog')?.value.trim() || "",
      transcript: document.getElementById('cms-l-script')?.value.trim() || "",
      question: document.getElementById('cms-l-q')?.value.trim() || "Dialog mazmunini tushundingizmi?",
      options: ["Ha", "Yo'q", "Boshqa"],
      correct: 0,
      explanation_uz: "Suhbat matniga asosan to'g'ri javob."
    };
    window.APP_DATA.listening.push({ id: Date.now(), level, ...payload });
  } else if (cat === 'reading') {
    title = document.getElementById('cms-r-title')?.value.trim();
    if (!title) { alert("Iltimos, matn sarlavhasini kiriting!"); return; }
    payload = {
      title: title,
      readTime: "3 min",
      passage: document.getElementById('cms-r-text')?.value.trim() || "",
      question: document.getElementById('cms-r-q')?.value.trim() || "Matn nima haqida?",
      options: ["Fikr 1", "Fikr 2", "Fikr 3"],
      correct: 0,
      explanation_uz: "Matn mazmuniga ko'ra."
    };
    window.APP_DATA.reading.push({ id: Date.now(), level, ...payload });
  } else if (cat === 'shadowing') {
    title = document.getElementById('cms-s-title')?.value.trim();
    if (!title) { alert("Iltimos, dars nomini kiriting!"); return; }
    payload = {
      title: title,
      videoUrl: document.getElementById('cms-s-url')?.value.trim() || "https://www.youtube.com/embed/dQw4w9WgXcQ",
      lines: [
        {
          start: "0:02",
          en: document.getElementById('cms-s-line-en')?.value.trim() || "",
          uz: document.getElementById('cms-s-line-uz')?.value.trim() || ""
        }
      ]
    };
    window.APP_DATA.shadowing.push({ id: Date.now(), level, ...payload });
  }

  try {
    const res = await fetch('/api/teacher/add-content', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        category: cat,
        level: level,
        title: title,
        data: payload,
        created_by: "Teacher Umar"
      })
    });
    const result = await res.json();
    alert("✅ Material muvaffaqiyatli saqlandi va dasturga joylandi!");
    loadCmsExistingMaterialsList();
  } catch (e) {
    alert("✅ Material muvaffaqiyatli joylandi!");
    loadCmsExistingMaterialsList();
  }
}

// Meetings
async function fetchActiveLiveMeetings() {
  try {
    const res = await fetch('/api/meetings');
    const meetings = await res.json();
    if (meetings && meetings.length > 0) {
      const banner = document.getElementById('live-meeting-banner');
      const text = document.getElementById('banner-meeting-text');
      const btn = document.getElementById('banner-meeting-btn');

      if (banner && text && btn) {
        text.innerText = `🔴 ${meetings[0].title} (${meetings[0].datetime_str})`;
        btn.href = meetings[0].meeting_link;
        banner.style.display = 'flex';
      }
    }
  } catch (e) {}
}

async function loadTeacherMeetings() {
  try {
    const res = await fetch('/api/meetings');
    const meetings = await res.json();
    const container = document.getElementById('teacher-meetings-list');
    if (container) {
      container.innerHTML = meetings.map(m => `
        <div style="background: rgba(255,255,255,0.04); padding: 10px; border-radius: var(--radius-sm); margin-bottom: 8px;">
          <b>${m.title}</b>
          <div style="font-size: 11px; color: #38bdf8;">${m.datetime_str} • ${m.level}</div>
          <a href="${m.meeting_link}" target="_blank" style="color: #86efac; font-size: 11px;">${m.meeting_link}</a>
        </div>
      `).join('');
    }
  } catch (e) {}
}

async function createMeetingFromTeacher() {
  triggerHaptic('heavy');
  const title = document.getElementById('meet-title-input').value.trim();
  const level = document.getElementById('meet-level-input').value.trim();
  const time = document.getElementById('meet-time-input').value.trim();
  const link = document.getElementById('meet-link-input').value.trim();

  if (!title || !link) {
    alert("Iltimos, mavzu va havolani kiriting!");
    return;
  }

  await fetch('/api/teacher/meetings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title,
      level,
      datetime_str: time,
      meeting_link: link
    })
  });

  alert("Jonli dars e'lon qilindi va bannerda ko'rsatiladi 📢");
  loadTeacherMeetings();
  fetchActiveLiveMeetings();
}

// Marking Hub
async function loadTeacherSubmissions() {
  try {
    const res = await fetch('/api/teacher/submissions');
    const subs = await res.json();
    const container = document.getElementById('teacher-submissions-queue');
    if (container) {
      if (subs && subs.length > 0) {
        container.innerHTML = subs.map(sub => `
          <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--surface-border); border-radius: var(--radius-md); padding: 12px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between;">
              <b>${sub.student_name} (${sub.student_level})</b>
              <span class="badge-pill">${sub.type}</span>
            </div>
            <div style="font-size: 12px; color: var(--text-muted); margin: 4px 0;">${sub.title}</div>
            <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: var(--radius-sm); font-size: 13px; font-style: italic; margin-bottom: 8px;">
              "${sub.content}"
            </div>
            <div style="display: flex; gap: 8px;">
              <input id="grade-score-${sub.id}" class="form-input" style="width: 70px;" type="number" placeholder="Ball" value="${sub.score || 85}">
              <input id="grade-comment-${sub.id}" class="form-input" style="flex: 1;" type="text" placeholder="O'qituvchi izohi (Feedback)" value="${sub.teacher_feedback || ''}">
              <button class="btn-primary-sm" onclick="gradeStudentSubmission(${sub.id})">Saqlash ✓</button>
            </div>
          </div>
        `).join('');
      } else {
        container.innerHTML = `<div style="color: var(--text-muted); font-size: 13px;">Hozircha baholanmagan yangi topshiriqlar yo'q.</div>`;
      }
    }
  } catch (e) {}
}

async function gradeStudentSubmission(id) {
  triggerHaptic('heavy');
  const score = document.getElementById(`grade-score-${id}`).value;
  const comment = document.getElementById(`grade-comment-${id}`).value;

  await fetch('/api/teacher/review', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      submission_id: id,
      score: parseInt(score),
      feedback: comment
    })
  });

  alert("Topshiriq baholandi va o'quvchi profiliga saqlandi ✨");
  loadTeacherSubmissions();
}

// =========================================================================
// 10. COURSE MATERIALS SYNC & TEACHER AVATAR MANAGER
// =========================================================================
async function fetchTeacherMaterials() {
  try {
    const res = await fetch('/api/teacher/content');
    const materials = await res.json();
    if (materials && Array.isArray(materials)) {
      materials.forEach(m => {
        if (!m.data) return;
        const lvl = m.level || 'B1';

        if (m.category === 'vocab' && m.data.word) {
          const exists = window.APP_DATA.words.some(w => w.word.toLowerCase() === m.data.word.toLowerCase());
          if (!exists) {
            window.APP_DATA.words.push({
              id: m.id,
              level: lvl,
              partOfSpeech: m.data.partOfSpeech || 'noun',
              word: m.data.word,
              topic: m.data.topic || m.title || `${lvl} Mavzusi`,
              phonetics: m.data.phonetics || '/.../',
              translation_uz: m.data.translation_uz || '',
              definition: m.data.definition || '',
              example: m.data.example || ''
            });
          }
        } else if (m.category === 'quiz' && m.data.question) {
          const exists = window.APP_DATA.quizzes.some(q => q.id === m.id || q.question === m.data.question);
          if (!exists) {
            window.APP_DATA.quizzes.push({
              id: m.id,
              level: lvl,
              type: m.data.type || 'mcq',
              question: m.data.question,
              options: m.data.options || ["A", "B", "C", "D"],
              correct: m.data.correct !== undefined ? m.data.correct : 0,
              explanation_uz: m.data.explanation_uz || ''
            });
          }
        } else if (m.category === 'grammar' && m.data.title) {
          const exists = window.APP_DATA.grammarTopics.some(g => g.id === m.id || g.title === m.data.title);
          if (!exists) {
            window.APP_DATA.grammarTopics.push({
              id: m.id,
              level: lvl,
              title: m.data.title,
              formula: m.data.formula || '',
              summary: m.data.summary || '',
              wrongSentence: m.data.wrongSentence || '',
              correctSentence: m.data.correctSentence || '',
              explanation_uz: m.data.explanation_uz || '',
              examples: m.data.examples || [{ en: m.data.correctSentence || m.data.title, uz: "Namuna" }]
            });
          }
        } else if (m.category === 'listening' && m.data.title) {
          const exists = window.APP_DATA.listening.some(l => l.id === m.id || l.title === m.data.title);
          if (!exists) {
            window.APP_DATA.listening.push({
              id: m.id,
              level: lvl,
              title: m.data.title,
              audioDuration: m.data.audioDuration || "1:00",
              dialog: m.data.dialog || '',
              transcript: m.data.transcript || '',
              question: m.data.question || 'Savol',
              options: m.data.options || ["A", "B"],
              correct: m.data.correct || 0,
              explanation_uz: m.data.explanation_uz || ''
            });
          }
        } else if (m.category === 'reading' && m.data.title) {
          const exists = window.APP_DATA.reading.some(r => r.id === m.id || r.title === m.data.title);
          if (!exists) {
            window.APP_DATA.reading.push({
              id: m.id,
              level: lvl,
              title: m.data.title,
              readTime: m.data.readTime || "3 min",
              passage: m.data.passage || '',
              question: m.data.question || 'Savol',
              options: m.data.options || ["A", "B"],
              correct: m.data.correct || 0,
              explanation_uz: m.data.explanation_uz || ''
            });
          }
        } else if (m.category === 'shadowing' && m.data.title) {
          const exists = window.APP_DATA.shadowing.some(s => s.id === m.id || s.title === m.data.title);
          if (!exists) {
            window.APP_DATA.shadowing.push({
              id: m.id,
              level: lvl,
              title: m.data.title,
              videoUrl: m.data.videoUrl || 'https://www.youtube.com/embed/dQw4w9WgXcQ',
              lines: m.data.lines || []
            });
          }
        }
      });
      updateVocabTopicDropdown();
    }
  } catch (e) {}
}

async function loadCmsExistingMaterialsList() {
  const container = document.getElementById('cms-materials-list-container');
  if (!container) return;

  const filterCat = document.getElementById('cms-filter-category')?.value || 'all';
  const filterLvl = document.getElementById('cms-filter-level')?.value || 'all';

  container.innerHTML = '<div style="color: var(--text-dim); font-size: 12px; text-align: center; padding: 12px;">Yuklanmoqda... ⏳</div>';

  try {
    const res = await fetch('/api/teacher/content');
    const materials = await res.json();
    if (!materials || !Array.isArray(materials) || materials.length === 0) {
      container.innerHTML = '<div style="color: var(--text-dim); font-size: 12px; text-align: center; padding: 12px;">Hozircha admin tomonidan yangi material qo\'shilmagan. Yuqoridagi formadan yangi material qo\'shishingiz mumkin! 📝</div>';
      return;
    }

    const filtered = materials.filter(m => {
      const matchCat = filterCat === 'all' || m.category === filterCat;
      const matchLvl = filterLvl === 'all' || m.level === filterLvl;
      return matchCat && matchLvl;
    });

    if (filtered.length === 0) {
      container.innerHTML = '<div style="color: var(--text-dim); font-size: 12px; text-align: center; padding: 12px;">Bu filtr bo\'yicha material topilmadi.</div>';
      return;
    }

    container.innerHTML = filtered.map(m => {
      const catIcons = { vocab: '📖 Lug\'at', quiz: '🎮 Quiz', grammar: '✍️ Grammatika', listening: '🎧 Listening', reading: '📰 Reading', shadowing: '🎬 Shadowing' };
      const icon = catIcons[m.category] || m.category;
      return `
        <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 8px 10px; margin-bottom: 6px;">
          <div style="flex: 1; min-width: 0;">
            <div style="display: flex; gap: 6px; align-items: center;">
              <span style="font-size: 10px; background: #0284c7; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: 700;">${icon}</span>
              <span style="font-size: 10px; background: rgba(56,189,248,0.2); color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-weight: 700;">${m.level}</span>
            </div>
            <div style="font-size: 12px; font-weight: 600; color: #fff; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              ${m.title}
            </div>
          </div>
          <button onclick="deleteCmsMaterial(${m.id})" style="background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid rgba(239,68,68,0.4); border-radius: 6px; padding: 4px 8px; font-size: 11px; cursor: pointer; margin-left: 8px; font-weight: 600;">
            🗑 O'chirish
          </button>
        </div>
      `;
    }).join('');
  } catch (e) {
    container.innerHTML = '<div style="color: #f87171; font-size: 12px; text-align: center; padding: 12px;">Materiallarni yuklashda xatolik.</div>';
  }
}

async function deleteCmsMaterial(materialId) {
  if (!confirm("Haqiqatan ham bu materialni o'chirmoqchimisiz?")) return;
  triggerHaptic('heavy');
  try {
    const res = await fetch('/api/teacher/delete-content', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: materialId })
    });
    const data = await res.json();
    if (data.success) {
      if (window.APP_DATA) {
        window.APP_DATA.words = window.APP_DATA.words.filter(w => w.id !== materialId);
        window.APP_DATA.quizzes = window.APP_DATA.quizzes.filter(q => q.id !== materialId && q.id !== `q_${materialId}`);
        window.APP_DATA.grammarTopics = window.APP_DATA.grammarTopics.filter(g => g.id !== materialId);
        window.APP_DATA.listening = window.APP_DATA.listening.filter(l => l.id !== materialId);
        window.APP_DATA.reading = window.APP_DATA.reading.filter(r => r.id !== materialId);
        window.APP_DATA.shadowing = window.APP_DATA.shadowing.filter(s => s.id !== materialId);
      }
      loadCmsExistingMaterialsList();
      alert("✅ Material muvaffaqiyatli o'chirildi!");
    } else {
      alert("O'chirishda xatolik.");
    }
  } catch (e) {
    alert("Server bilan bog'lanishda xatolik.");
  }
}

async function loadSavedAvatar() {
  const localAvatar = localStorage.getItem('umar_tutor_avatar');
  if (localAvatar) {
    applyAvatarToUI(localAvatar);
  }
  try {
    const res = await fetch('/api/teacher/avatar');
    const data = await res.json();
    if (data.avatar_url && data.avatar_url !== 'assets/robot.svg') {
      applyAvatarToUI(data.avatar_url);
      localStorage.setItem('umar_tutor_avatar', data.avatar_url);
    }
  } catch (e) {}
}

function applyAvatarToUI(avatarUrl) {
  if (!avatarUrl) return;
  document.querySelectorAll('.teacher-avatar-target').forEach(img => {
    img.src = avatarUrl;
  });
  const preview = document.getElementById('teacher-avatar-preview');
  if (preview) preview.src = avatarUrl;
}

function handleAvatarFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (e) => {
    const base64Data = e.target.result;
    applyAvatarToUI(base64Data);
    localStorage.setItem('umar_tutor_avatar', base64Data);

    try {
      const res = await fetch('/api/teacher/upload-avatar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ avatar_data: base64Data })
      });
      const data = await res.json();
      if (data.success && data.avatar_url) {
        applyAvatarToUI(data.avatar_url);
        localStorage.setItem('umar_tutor_avatar', data.avatar_url);
      }
      alert("✅ Admin surati muvaffaqiyatli o'rnatildi va saqlandi!");
    } catch (err) {
      alert("✅ Surat saqlandi!");
    }
  };
  reader.readAsDataURL(file);
}

async function saveAvatarFromUrl() {
  const input = document.getElementById('teacher-avatar-url-input');
  const url = input?.value?.trim();
  if (!url) {
    alert("Iltimos, rasm havolasini (URL) kiriting!");
    return;
  }
  applyAvatarToUI(url);
  localStorage.setItem('umar_tutor_avatar', url);

  try {
    await fetch('/api/teacher/upload-avatar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ avatar_data: url })
    });
    alert("✅ Yangi surat havolasi saqlandi!");
  } catch (e) {
    alert("✅ Surat saqlandi!");
  }
}

async function resetAvatarToDefault() {
  const defaultRobot = 'assets/robot.svg';
  applyAvatarToUI(defaultRobot);
  localStorage.removeItem('umar_tutor_avatar');
  try {
    await fetch('/api/teacher/upload-avatar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ avatar_data: 'reset' })
    });
    alert("Robot rasmi qaytarildi!");
  } catch (e) {}
}

