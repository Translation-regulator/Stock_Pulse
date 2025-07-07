<template>
  <div class="stock-switcher">
    <div class="stock-id-name">{{ stockName }}（{{ stockId }}）</div>

    <div class="switch-bar">
      <div class="switch-buttons desktop-only">
        <button @click="mode = 'daily'" :class="{ active: mode === 'daily' }">日線</button>
        <button @click="mode = 'weekly'" :class="{ active: mode === 'weekly' }">週線</button>
        <button @click="mode = 'monthly'" :class="{ active: mode === 'monthly' }">月線</button>
      </div>

      <select class="mobile-only mode-select" v-model="mode">
        <option value="daily">日線</option>
        <option value="weekly">週線</option>
        <option value="monthly">月線</option>
      </select>

      <StockRealtime :stockId="stockId" />
    </div>

    <!-- 三種圖表 -->
    <div v-show="mode === 'daily'">
      <StockDailyChart :stock-id="stockId" :show-chat="showChat" @open-chat="emit('open-chat')" />
    </div>
    <div v-show="mode === 'weekly'">
      <StockWeeklyChart :stock-id="stockId" :show-chat="showChat" @open-chat="emit('open-chat')" />
    </div>
    <div v-show="mode === 'monthly'">
      <StockMonthlyChart :stock-id="stockId" :show-chat="showChat" @open-chat="emit('open-chat')" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StockRealtime from './StockRealtime.vue'
import StockDailyChart from './StockDailyChart.vue'
import StockWeeklyChart from './StockWeeklyChart.vue'
import StockMonthlyChart from './StockMonthlyChart.vue'

const emit = defineEmits(['open-chat'])

const props = defineProps({
  stockId: String,
  stockName: String,
  showChat: Boolean,
})

const mode = ref('daily')
</script>

<style scoped>
.stock-switcher {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  padding: 0.5rem;
  background-color: #0d1117;
  overflow: hidden;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 20;
  background-color: rgba(0, 0, 0, 0.5); /* 半透明遮罩 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #facc15;
  pointer-events: none;
  backdrop-filter: blur(1px);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #facc15;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.chart-renderer {
  flex: 1;
  height: 100%;
  overflow: auto;
}

.stock-id-name {
  color: #e6edf3;
  margin-bottom: 0.5rem;
  font-size: 30px;
}

.switch-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.0rem;
}

.switch-buttons {
  display: flex;
  gap: 10px;
}

button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  background: #1f2937;
  color: white;
  border: 1px solid #444;
  border-radius: 6px;
}
button.active {
  background-color: #6366f1;
  border-color: #6366f1;
}

.loading-overlay {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #facc15;
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.chart-renderer {
  flex: 1;
  height: 100%; 
}

.desktop-only {
  display: flex;
}
.mobile-only {
  display: none;
}

/* 手機樣式 */
@media (max-width: 756px) {
  .stock-switcher{
    height: calc(100vh - 80px);
  }
  .desktop-only {
    display: none;
  }
  .mobile-only {
    display: block;
  }

  .mode-select {
    padding: 0.5rem;
    font-size: 1rem;
    background-color: #1f2937;
    color: white;
    border: 1px solid #444;
    border-radius: 6px;
    -webkit-appearance: none;
    appearance: none;
    background-image: none;
  }

  .chart-renderer {
    height: 80%;
  }

  .stock-id-name {
    margin-bottom: 0;
  }

  .switch-bar {
    margin-bottom: 0;
  }
}
</style>
