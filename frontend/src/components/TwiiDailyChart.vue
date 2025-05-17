<template>
  <div class="chart">
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
    const res = await axios.get('http://localhost:8000/api/twii/daily')
    const raw = res.data

    chartData.value = raw.map(item => ({
      time: item.date,
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

