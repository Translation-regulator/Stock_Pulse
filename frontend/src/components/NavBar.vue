<script setup>
import { ref, onMounted } from 'vue'
import logo from '@/assets/StockPulse.png'
import { RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import api from '@/api'
import Toast from '@/components/Toast.vue'
import burgerIcon from '@/assets/burger_menu.png'

const { accessToken, username, isLoggedIn, login, logout } = useAuth()

const showPopup = ref(false)
const isLoginMode = ref(true)
const showDropdown = ref(false)

const name = ref('')
const email = ref('')
const password = ref('')

const toastMsg = ref('')
const toastType = ref('info')

const showToast = (msg, type = 'info') => {
  toastMsg.value = msg
  toastType.value = type
}

const togglePopup = () => {
  showPopup.value = true
  isLoginMode.value = true
  email.value = 'test@example.com'
  password.value = 'test1234'
  name.value = '測試用戶'
}

const closePopup = () => {
  showPopup.value = false
  name.value = ''
  email.value = ''
  password.value = ''
}

const switchMode = () => {
  isLoginMode.value = !isLoginMode.value
}

const handleSubmit = async () => {
  if (!email.value.includes('@')) {
    showToast('Email 格式錯誤', 'error')
    return
  }
  if (!isLoginMode.value && password.value.length < 6) {
    showToast('密碼需至少六位數', 'error')
    return
  }

  if (isLoginMode.value) {
    const res = await login(email.value, password.value)
    if (res.success) {
      showToast('登入成功！', 'success')
      closePopup()
    } else {
      showToast(res.message, 'error')
    }
  } else {
    try {
      await api.post('/auth/register', {
        name: name.value,
        email: email.value,
        password: password.value
      })
      showToast('註冊成功，請重新登入', 'success')
      isLoginMode.value = true
    } catch (err) {
      const msg = err.response?.data?.detail || '註冊失敗'
      showToast(msg, 'error')
    }
  }
}

const handleLogout = async () => {
  await logout()
  showDropdown.value = false
  showToast('已成功登出', 'success')
}

onMounted(() => {
  window.addEventListener('open-login-modal', () => {
    showPopup.value = true
    isLoginMode.value = true
  })
})

const showMobileMenu = ref(false)
const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}
</script>

<template>
  <nav class="navbar">
    <div class="navbar-left">
      <RouterLink to="/">
        <img :src="logo" alt="StockPulse Logo" class="logo" />
      </RouterLink>
    </div>

    <!-- 中間選單：大螢幕用 -->
    <div class="navbar-center desktop-menu">
      <RouterLink to="/twii" class="menu">大盤指數</RouterLink>
      <RouterLink to="/stock" class="menu">個股資訊</RouterLink>
      <RouterLink to="/portfolio" class="menu">投資組合</RouterLink>
      <RouterLink to="/chat" class="menu">聊天室</RouterLink>
    </div>

    <!-- 中間選單：小螢幕用 -->
    <div class="navbar-center mobile-menu-button">
      <button class="hamburger" @click="toggleMobileMenu">
        <img :src="burgerIcon" alt="menu" />
      </button>
    </div>

    <div class="navbar-right">
      <div v-if="isLoggedIn" class="user-menu">
        <button class="signinup" @click="showDropdown = !showDropdown">
          {{ username }}
        </button>
        <div v-if="showDropdown" class="dropdown">
          <button @click="handleLogout">登出</button>
        </div>
      </div>
      <button v-else class="signinup" @click="togglePopup">登入/註冊</button>
    </div>
  </nav>

  <div v-if="showPopup" class="popup-overlay">
    <div class="popup-content">
      <button class="close-btn" @click="closePopup">✖</button>
      <h3>{{ isLoginMode ? '會員登入' : '會員註冊' }}</h3>

      <input v-if="!isLoginMode" v-model="name" type="text" placeholder="名稱" />
      <input v-model="email" type="email" placeholder="Email" />
      <input v-model="password" type="password" placeholder="密碼" />

      <button @click="handleSubmit">{{ isLoginMode ? '登入' : '註冊' }}</button>

      <p class="switch-hint">
        {{ isLoginMode ? '還沒有帳號？' : '已經有帳號？' }}
        <span @click="switchMode">{{ isLoginMode ? '點我註冊' : '點我登入' }}</span>
      </p>
    </div>
  </div>

  <Toast :message="toastMsg" :type="toastType" />

  <div v-if="showMobileMenu" class="mobile-menu-overlay" @click.self="showMobileMenu = false">
    <div class="mobile-menu">
      <RouterLink to="/twii" @click="showMobileMenu = false">大盤指數</RouterLink>
      <RouterLink to="/stock" @click="showMobileMenu = false">個股資訊</RouterLink>
      <RouterLink to="/portfolio" @click="showMobileMenu = false">投資組合</RouterLink>
      <RouterLink to="/chat" @click="showMobileMenu = false">聊天室</RouterLink>
      <button v-if="isLoggedIn" @click="handleLogout">登出</button>
      <button v-else @click="togglePopup">登入 / 註冊</button>
    </div>
  </div>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  height: 60px;
  width: 100%;
  background-color: #000;
  border-bottom: 1px solid #222;
  box-sizing: border-box;
  color: white;
  font-family: 'Segoe UI', sans-serif;
  padding: 0 2%; 
}

.navbar-left,
.navbar-right {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
}

/* 桌機選單（大螢幕用） */
.desktop-menu {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: clamp(1rem, 4vw, 3rem);
  font-size: clamp(16px, 2vw, 26px);
}

/* 手機漢堡按鈕（小螢幕用） */
.mobile-menu-button {
  display: none;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.logo {
  height: 40px;
  cursor: pointer;
}

.menu {
  color: white;
  text-decoration: none;
  padding: clamp(0.3rem, 0.8vw, 0.5rem) clamp(0.6rem, 1.5vw, 1rem);
  border: 1px solid #333;
  border-radius: 12px;
  background: transparent;
  font-size: clamp(16px, 2vw, 20px);
  transition: all 0.3s ease;
  white-space: nowrap;
}

.menu:hover {
  background: #1f2937;
  color: #60a5fa;
}

.menu.router-link-exact-active {
  font-weight: bold;
}

.signinup {
  background: linear-gradient(90deg, #1f6feb, #a030f9);
  color: white;
  padding: clamp(0.3rem, 1vw, 0.6rem) clamp(0.8rem, 2vw, 1.2rem);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: clamp(16px, 2vw, 20px);
}

.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.popup-content {
  position: relative;
  background: #111;
  color: white;
  padding: 2rem;
  border-radius: 12px;
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.popup-content input {
  padding: 0.5rem;
  border: 1px solid #444;
  border-radius: 6px;
  background: #222;
  color: white;
}

.popup-content button {
  background: linear-gradient(90deg, #1f6feb, #a030f9);
  color: white;
  border: none;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
}

.switch-hint {
  font-size: 14px;
  text-align: center;
}

.switch-hint span {
  color: #60a5fa;
  cursor: pointer;
  margin-left: 4px;
}

.user-menu {
  position: relative;
  display: inline-block;
}

.dropdown {
  position: absolute;
  right: 0;
  top: 110%;
  background-color: #111;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 0.5rem;
  z-index: 999;
}

.dropdown button {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 16px;
  padding: 0.3rem 1rem;
  width: 100%;
  text-align: left;
}

.dropdown button:hover {
  background-color: #222;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: transparent;
  color: white;
  border: none;
  font-size: 20px;
  cursor: pointer;
}

.close-btn:hover {
  color: #f87171;
}

.hamburger {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.3rem;
}

.hamburger img {
  height: 28px;
  width: 28px;
}

/* 小螢幕：隱藏主選單、顯示漢堡按鈕 */
@media (max-width: 768px) {
  .desktop-menu {
    display: none;
  }

  .mobile-menu-button {
    display: flex;
    justify-content: center;
    flex: 1;
  }

  .hamburger {
    display: block;
  }
}

.mobile-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  z-index: 999;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.mobile-menu {
  background-color: #111;
  width: 100%;
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  color: white;

  animation: slideDown 0.3s ease-out forwards;
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
  }
  to {
    transform: translateY(0%);
  }
}


.mobile-menu a,
.mobile-menu button {
  text-align: center;
  color: white;
  background: none;
  border: none;
  font-size: 26px;
  cursor: pointer;
  text-decoration: none;
}

.mobile-menu a:hover,
.mobile-menu button:hover {
  color: #60a5fa;
}
</style>
