<script setup>
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div class="app-layout">
    <NavBar />
    <router-view />
  </div>
</template>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
}

.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh; /* ✅ 控制整體畫面高度 */
}
</style>
