<template>
  <div class="stock-switcher">
    <div class="stock-id-name">{{ stockName }}（{{ stockId }}）</div>

    <div class="switch-bar">
      <!-- 桌機版按鈕 -->
      <div class="switch-buttons desktop-only">
        <button @click="mode = 'daily'" :class="{ active: mode === 'daily' }">日線</button>
        <button @click="mode = 'weekly'" :class="{ active: mode === 'weekly' }">週線</button>
        <button @click="mode = 'monthly'" :class="{ active: mode === 'monthly' }">月線</button>
      </div>

      <!-- 手機版下拉 -->
      <select class="mobile-only mode-select" v-model="mode">
        <option value="daily">日線</option>
        <option value="weekly">週線</option>
        <option value="monthly">月線</option>
      </select>

      <StockRealtime :stockId="stockId" />
    </div>

    <div v-if="loading" class="loading-overlay">💸 散財中...</div>

    <ChartRenderer
      v-else-if="ohlc.length"
      :candles="ohlc"
      type="stock"
      class="chart-renderer"
      @open-chat="emit('open-chat')"
    />

    <p v-else>找不到資料</p>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import ChartRenderer from './ChartRenderer.vue'
import StockRealtime from './StockRealtime.vue'
import api from '@/api'

const emit = defineEmits(['open-chat'])

const props = defineProps({
  stockId: String,
  stockName: String,
})

const mode = ref('daily')
const ohlc = ref([])
const loading = ref(false)

async function fetchData() {
  if (!props.stockId) return
  loading.value = true
  try {
    const res = await api.get(`/stocks/${props.stockId}/${mode.value}`)
    ohlc.value = res.data
  } catch (err) {
    console.error('取得個股資料失敗', err)
    ohlc.value = []
  } finally {
    loading.value = false
  }
}

watch(mode, fetchData)
watch(() => props.stockId, fetchData)
onMounted(fetchData)
</script>

<style scoped>
.stock-switcher {
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
  padding: 0.5rem;
  background-color: #0d1117;
  border-radius: 12px;
  border: 1px solid #30363d;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.chart-renderer {
  height: 100%;
}

.stock-id-name {
  color: #e6edf3;
  margin-bottom: 0.5rem;
  font-size: 20px;
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
    height: 75%;
  }
}
</style>
