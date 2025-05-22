<template>
  <div class="stock-switcher">
    <h2>{{ stockName }}（{{ stockId }}）</h2>

    <div class="switch-buttons">
      <button @click="mode = 'daily'" :class="{ active: mode === 'daily' }">日線</button>
      <button @click="mode = 'weekly'" :class="{ active: mode === 'weekly' }">週線</button>
      <button @click="mode = 'monthly'" :class="{ active: mode === 'monthly' }">月線</button>
    </div>

    <div v-if="loading">📊 資料載入中...</div>
    <ChartRenderer v-else-if="ohlc.length" :candles="ohlc" />
    <p v-else>❌ 找不到資料</p>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import ChartRenderer from './ChartRenderer.vue'

const props = defineProps({
  stockId: String,
  stockName: String,
})

const mode = ref('daily') // 'daily' | 'weekly' | 'monthly'
const ohlc = ref([])
const loading = ref(false)

async function fetchData() {
  if (!props.stockId) return
  loading.value = true
  try {
    const res = await fetch(`/api/stocks/${props.stockId}/${mode.value}`)
    if (!res.ok) {
      ohlc.value = []
      return
    }
    const data = await res.json()
    ohlc.value = data
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
  padding: 1.5rem;
  background-color: #0d1117;
  border-radius: 12px;
  border: 1px solid #30363d;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.05);
  margin-top: 1rem;
}

h2 {
  color: #e6edf3;
  margin-bottom: 1rem;
}

.switch-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 1rem;
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
</style>
