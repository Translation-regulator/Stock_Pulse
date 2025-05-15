<template>
  <div ref="chartContainer" class="chart-container"></div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { createChart } from 'lightweight-charts'

// 接收外部傳入的 K 線資料
const props = defineProps({
  candles: {
    type: Array,
    required: true
  }
})

const chartContainer = ref(null)
let chart = null
let series = null

onMounted(() => {
  setTimeout(() => {
    chart = createChart(chartContainer.value, {
      width: chartContainer.value.clientWidth || 800,
      height: 400,
      layout: {
        background: { color: '#ffffff' },
        textColor: '#000000',
      },
      grid: {
        vertLines: { color: '#e1e1e1' },
        horzLines: { color: '#e1e1e1' },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    })

    series = chart.addCandlestickSeries()
    series.setData(props.candles)
  }, 0)
})

// 如果資料有變化就更新圖表
watch(() => props.candles, (newData) => {
  if (series) {
    series.setData(newData)
  }
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  height: 400px;
}
</style>
