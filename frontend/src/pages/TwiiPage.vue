<template>
  <div class="twii-page">
    <div class="chart-area" :class="{ 'half-height': showChat }">
      <TwiiChartSwitcher
        :show-chat="showChat"
        @open-chat="showChat = true"
      />
    </div>

    <SlideChatDrawer
      v-if="showChat"
      :isOpen="true"
      roomId="twii"
      roomName="台灣加權指數"
      @close="showChat = false"
      class="chat-section"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TwiiChartSwitcher from '../components/TwiiChartSwitcher.vue'   // ✅ 正確引用
import SlideChatDrawer from '../components/SlideChatDrawer.vue'

const showChat = ref(false)
</script>

<style scoped>
.twii-page {
  display: flex;
  height: calc(100vh - 60px);
  background-color: #121212;
  padding: 0 2%;
  position: relative;
}

.chart-area {
  flex: 1;
  overflow: hidden;
  transition: height 0.3s ease;
}

.chat-section {
  width: 100%;
  max-width: 400px;
  height: 100%;
  transition: height 0.3s ease;
}

@media (max-width: 756px) {
  .twii-page {
    flex-direction: column;
  }

  .chart-area {
    flex: none;
    height: 100%;
  }

  .chart-area.half-height {
    height: 56vh;
  }

  .chat-section {
    flex: none;
    width: 100%; 
    max-width: 100%;            
    height: 37dvh;            
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    overflow: hidden;          
  }

  .chat-section .chat-messages {
    flex: 1;
    overflow-y: auto;         
  }

  .chat-section .chat-input {
    padding: 0.5rem;
    border-top: 1px solid #333;
    background-color: #1e1e1e;
  }
}
</style>
