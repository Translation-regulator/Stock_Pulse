<script setup>
import { ref } from 'vue'
import TwiiChartSwitcher from '../components/TwiiChartSwitcher.vue'
import SlideChatDrawer from '../components/SlideChatDrawer.vue'

const showChat = ref(false)
</script>

<template>
  <div class="twii-page">
    <TwiiChartSwitcher />

    <!-- 💬 留言按鈕 -->
    <button class="chat-toggle-button" @click="showChat = true">
      💬 留言
    </button>

    <!-- 🪟 抽屜聊天室 -->
    <SlideChatDrawer
      :isOpen="showChat"
      roomId="twii"
      roomName="台灣加權指數"
      @close="showChat = false"
    />
  </div>
</template>

<style scoped>
.twii-page {
  position: relative;
  padding: 1rem;
}

.chat-toggle-button {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 999;
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 0.75rem 1.2rem;
  border-radius: 999px;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}
</style>
