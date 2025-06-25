<script setup>
import { ref } from 'vue'
import TwiiChartSwitcher from '../components/TwiiChartSwitcher.vue'
import SlideChatDrawer from '../components/SlideChatDrawer.vue'

const showChat = ref(false)
</script>

<template>
  <div class="twii-page">
    <!-- 左側圖表區 -->
    <div class="chart-area">
      <TwiiChartSwitcher />
    </div>

    <!-- 右側聊天室區（可選擇是否顯示） -->
    <SlideChatDrawer
      v-if="showChat"
      :isOpen="true"
      roomId="twii"
      roomName="台灣加權指數"
      @close="showChat = false"
    />

    <!-- 浮動留言按鈕 -->
    <button v-if="!showChat" class="chat-toggle-button" @click="showChat = true">
      留言
    </button>
  </div>
</template>

<style scoped>
.twii-page {
  display: flex;
  height: calc(100vh - 60px);
  background-color: #121212;
  position: relative;
  padding-left: 2%;
  padding-right: 2%;
}

.chart-area {
  flex: 1;
  overflow: hidden;
}

.chat-toggle-button {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  writing-mode: vertical-rl;
  background-color: #2e6b30;
  color: white;
  border: none;
  border-radius: 8px 0 0 8px;
  padding: 0.5rem 0.3rem;
  cursor: pointer;
  z-index: 999;
  font-size: 0.9rem;
  opacity: 0.6;
}
</style>
