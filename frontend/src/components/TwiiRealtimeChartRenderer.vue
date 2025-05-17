<template>
  <div ref="chartContainer" class="chart-container"></div>
</template>

<script setup>
import { onMounted, ref, watch, nextTick } from 'vue'
import { createChart } from 'lightweight-charts'

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

  const containerWidth = chartContainer.value.clientWidth || 800
  console.log('📏 容器寬度:', containerWidth)

  chart = createChart(chartContainer.value, {
    width: containerWidth,
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

  series = chart.addLineSeries({
    priceLineVisible: false,
    lastValueVisible: false,
  })

  chart.timeScale().scrollToRealTime()
  chart.timeScale().fitContent()

  // ➕ 補一次 resize 保險
  chart.resize(containerWidth, 300)

  window.addEventListener('resize', () => {
    chart.resize(chartContainer.value.clientWidth, 300)
  })
})

watch(
  () => props.data,
  (newData) => {
    console.log('📈 renderer 收到資料:', newData.length, newData.slice(-1)) // ⬅️ 加這行
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
