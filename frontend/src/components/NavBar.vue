<script setup>
import logo from '@/assets/StockPulse.png'
import { RouterLink } from 'vue-router'
</script>

<template>
  <nav class="navbar">
    <!-- 左邊 Logo -->
    <RouterLink to="/" class="left" >
      <img :src="logo" alt="StockPulse Logo" class="logo" />
    </RouterLink>

    <!-- 中間選單 -->
    <div class="center">
      <RouterLink to="/twii" class="menu">大盤指數</RouterLink>
      <RouterLink to="#" class="menu">個股資訊</RouterLink>
      <RouterLink to="#" class="menu">投資組合</RouterLink>
      <RouterLink to="#" class="menu more">聊天室</RouterLink>
    </div>

    <!-- 右邊登入 -->
    <div>
      <button class="signinup">登入/註冊</button>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  width: 100%;
  background-color: #000;
  border-bottom: 1px solid #222;
  box-sizing: border-box;
  color: white;
  font-family: 'Segoe UI', sans-serif;
  padding-left: 5%;
  padding-right: 5%;

}


.left .logo {
  height: 40px;
  cursor: pointer;
}

.center {
  flex: 1;
  display: flex;
  justify-content: center;
  gap: 3rem;
  font-size: 26px;
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
</style>
