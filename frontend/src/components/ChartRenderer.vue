<template>
  <div class="chart-container">
    <div ref="chartContainer" class="chart"></div>
    <div v-if="hoverData" class="hover-panel">
      <p>📅 {{ hoverData.date }}</p>
      <p>開盤：{{ hoverData.open }}</p>
      <p>最高：{{ hoverData.high }}</p>
      <p>最低：{{ hoverData.low }}</p>
      <p>收盤：{{ hoverData.close }}</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, nextTick } from 'vue'
import { createChart } from 'lightweight-charts'

const props = defineProps({
  candles: {
    type: Array,
    required: true
  }
})

const chartContainer = ref(null)
const hoverData = ref(null)
let chart = null
let series = null

onMounted(async () => {
  await nextTick()  // 等待 DOM 完全載入

  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth || 800,
    height: 400,
    layout: {
      background: { color: '#f4f4f4' },
      textColor: '#333333',
    },
    grid: {
      vertLines: { color: '#e0e0e0' },
      horzLines: { color: '#e0e0e0' },
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
    },
  })

  series = chart.addCandlestickSeries({
    upColor: '#ef5350',
    downColor: '#26a69a',
    borderVisible: false,
    wickUpColor: '#ef5350',
    wickDownColor: '#26a69a',
  })

  series.setData(props.candles)

chart.subscribeCrosshairMove(param => {
  if (!param || !param.time || !param.seriesData) {
    hoverData.value = null
    return
  }

  const ohlc = param.seriesData.get(series)
  console.log('🎯 ohlc:', ohlc)  // ← 看這個有沒有

  if (ohlc) {
    const dt = new Date(param.time * 1000)
    hoverData.value = {
      date: dt.toLocaleDateString('zh-TW'),
      open: ohlc.open,
      high: ohlc.high,
      low: ohlc.low,
      close: ohlc.close
    }
  } else {
    hoverData.value = null
  }
})


  window.addEventListener('resize', () => {
    chart.resize(chartContainer.value.clientWidth, 400)
  })
})

watch(() => props.candles, (newData) => {
  if (series) {
    series.setData(newData)
  }
})
console.log('🧪 實際資料內容：', props.candles.slice(0, 5).map(item => ({
  time: item.time,
  open: item.open,
  close: item.close
})))


</script>

<style scoped>
.chart-container {
  position: relative;
}
.chart {
  width: 100%;
  height: 100%;
}
.hover-panel {
  position: absolute;
  top: 10px;
  left: 10px;
  background: #ffffffdd;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.9rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  z-index: 10;
}
</style>
