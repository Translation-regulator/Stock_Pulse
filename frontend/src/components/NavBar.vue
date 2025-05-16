<script setup>
import logo from '@/assets/StockPulse.png'
</script>

<template>
  <header class="navbar">
    <nav class="nav-inner">
      <div class="nav-title">
        <img :src="logo" class="title-picture" alt="StockPulse Logo" />
        <div class="title">StockPulse</div>
      </div>
      <div class="login">點我登入</div>
    </nav>
  </header>
</template>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: #1e1e2f;
  color: white;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* 內容容器限制寬度並置中 */
.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
}

/* Logo */
.title-picture {
  width: 50px;
  height: auto;
}

/* 左側區塊 */
.nav-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title {
  font-weight: bold;
  font-size: 28px;
  color: white;
}

/* 右側登入按鈕 */
.login {
  font-size: 16px;
  cursor: pointer;
  color: white;
}

</style>
