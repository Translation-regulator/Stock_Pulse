<script setup>
import { ref, computed, onMounted } from 'vue'
import logo from '@/assets/StockPulse.png'
import { RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import api from '@/api' 

const { accessToken, username, isLoggedIn, login, logout } = useAuth()

const showPopup = ref(false)
const isLoginMode = ref(true)
const showDropdown = ref(false)

const name = ref('')
const email = ref('')
const password = ref('')

const togglePopup = () => {
  showPopup.value = !showPopup.value
  isLoginMode.value = true
}

const switchMode = () => {
  isLoginMode.value = !isLoginMode.value
}

const handleSubmit = async () => {
  const url = isLoginMode.value ? '/auth/login' : '/auth/register'
  const payload = isLoginMode.value
    ? { email: email.value, password: password.value }
    : { name: name.value, email: email.value, password: password.value }

  try {
    const res = await api.post(url, payload)  
    const data = res.data                     

    if (isLoginMode.value) {
      localStorage.setItem('accessToken', data.access_token)
      localStorage.setItem('username', data.name)
      accessToken.value = data.access_token
      username.value = data.name
      alert('登入成功！')
    }

    showPopup.value = false
  } catch (err) {
    const msg = err.response?.data?.detail || '伺服器錯誤'
    alert(msg)
  }
}
onMounted(() => {
  window.addEventListener('open-login-modal', () => {
    showPopup.value = true
    isLoginMode.value = true
  })
})

</script>

<template>
  <nav class="navbar">
    <div class="navbar-left">
      <RouterLink to="/">
        <img :src="logo" alt="StockPulse Logo" class="logo" />
      </RouterLink>
    </div>

    <div class="navbar-center">
      <RouterLink to="/twii" class="menu">大盤指數</RouterLink>
      <RouterLink to="/stock" class="menu">個股資訊</RouterLink>
      <RouterLink to="/portfolio" class="menu">投資組合</RouterLink>
      <RouterLink to="/chat" class="menu">聊天室</RouterLink>
    </div>

    <div class="navbar-right">
      <div v-if="isLoggedIn" class="user-menu">
        <button class="signinup" @click="showDropdown = !showDropdown">
          歡迎，{{ username }} ▼
        </button>
        <div v-if="showDropdown" class="dropdown">
          <button @click="logout">登出</button>
        </div>
      </div>
      <button v-else class="signinup" @click="togglePopup">登入/註冊</button>
    </div>
  </nav>


  <div v-if="showPopup" class="popup-overlay" @click.self="showPopup = false">
    <div class="popup-content">
      <h3 v-if="isLoginMode">會員登入</h3>
      <h3 v-else>會員註冊</h3>

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
  padding: 0 10%; 
}

.navbar-left,
.navbar-right {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
}

.navbar-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: clamp(1rem, 4vw, 3rem);
  font-size: clamp(16px, 2vw, 26px);
}

.logo {
  height: 40px;
  cursor: pointer;
}

.menu {
  color: white;
  text-decoration: none;
}

.menu.router-link-exact-active {
  font-weight: bold;
}

.signinup {
  background: linear-gradient(90deg, #1f6feb, #a030f9);
  color: white;
  padding: 0.4rem 1rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 20px;
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

</style>