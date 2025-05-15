<template>
  <div>
    <ChartRenderer v-if="chartData.length > 0" :candles="chartData" />
    <p v-else>📉 載入中...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ChartRenderer from './ChartRenderer.vue'

const chartData = ref([])

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/twii/daily')  // 你後端 API
    const raw = res.data

    // 轉換為 Lightweight Charts 格式
    chartData.value = raw.map(item => ({
      time: item.date, // e.g. "2015-06-01"
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close
    }))
  } catch (error) {
    console.error('❌ 取得資料失敗', error)
  }
})
</script>
