<script setup>
import logo from '@/assets/StockPulse.png'
</script>

<template>
  <nav class="navbar">
    <!-- 左邊 Logo -->
    <div class="left">
      <img :src="logo" alt="StockPulse Logo" class="logo" />
    </div>
    <div class="center">
      <div class="menu">大盤指數</div>
      <div class="menu">個股資訊</div>
      <div class="menu">投資組合</div>
      <div class="menu more">聊天室</div>
    </div>
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
  gap: 3rem; /* 調整間距大小 */
  font-size: 26px;
}

.search {
  background-color: #222;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  border: none;
  width: 250px;
  outline: none;
  font-size: 0.9rem;
}

.right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.menu {
  color: white;
  text-decoration: none;
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
