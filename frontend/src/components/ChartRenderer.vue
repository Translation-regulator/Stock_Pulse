<template>
  <div ref="chartContainer"></div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { createChart } from 'lightweight-charts'

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
        background: { color: '#f4f4f4' },   // 淡灰色背景
        textColor: '#333333',              // 深灰文字
      },
      grid: {
        vertLines: { color: '#e0e0e0' },    // 垂直格線 - 更淡
        horzLines: { color: '#e0e0e0' },    // 水平格線
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    })

    series = chart.addCandlestickSeries({
      upColor: '#ef5350',        // 紅色漲
      downColor: '#26a69a',      // 綠色跌
      borderVisible: false,
      wickUpColor: '#ef5350',
      wickDownColor: '#26a69a',
    })

    series.setData(props.candles)
  }, 0)
})

watch(() => props.candles, (newData) => {
  if (series) {
    series.setData(newData)
  }
})
</script>
