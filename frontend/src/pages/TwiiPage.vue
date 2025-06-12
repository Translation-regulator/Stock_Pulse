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
      💬 留言
    </button>
  </div>
</template>

<style scoped>
.twii-page {
  display: flex;
  height: calc(100vh - 60px);
  background-color: #121212;
  position: relative;
  padding-left: 10%;
  padding-right: 10%;
}

.chart-area {
  flex: 1;
  overflow: hidden;
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
