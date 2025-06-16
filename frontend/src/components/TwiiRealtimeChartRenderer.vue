<template>
  <div ref="chartContainer" class="chart-container"></div>
</template>

<script setup>
import { onMounted, ref, watch, nextTick } from 'vue'
import { createChart, LineSeries } from 'lightweight-charts'

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
})

const chartContainer = ref(null)
let chart = null
let series = null

onMounted(async () => {
  await nextTick()

  const width = chartContainer.value.clientWidth || 800

  chart = createChart(chartContainer.value, {
    width,
    height: 300,
    layout: {
      backgroundColor: '#ffffff',
      textColor: '#000000',
    },
    grid: {
      vertLines: { color: '#eee' },
      horzLines: { color: '#eee' },
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: true,
      barSpacing: 10,
      tickMarkFormatter: (unixTime) => {
        const date = new Date(unixTime * 1000)
        return date.toLocaleTimeString('zh-TW', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })
      },
    },
    crosshair: {
      vertLine: { visible: false },
      horzLine: { visible: false },
    },
  })

  // ✅ v5 新寫法：加上 LineSeries 類別
  series = chart.addSeries(LineSeries, {
    priceLineVisible: false,
    lastValueVisible: false,
  })

  chart.timeScale().scrollToRealTime()
  chart.timeScale().fitContent()

  chart.resize(width, 300)

  window.addEventListener('resize', () => {
    chart.resize(chartContainer.value.clientWidth, 300)
  })
})

watch(
  () => props.data,
  (newData) => {
    if (series && chart && newData.length > 0) {
      series.setData(newData)
      chart.timeScale().scrollToRealTime()
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 300px;
  min-height: 300px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #fff;
}

</style>
