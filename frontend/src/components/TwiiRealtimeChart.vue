<template>
  <div class="twii-realtime-chart">
    <TwiiRealtimeChartRenderer v-if="data.length" :data="data.map(d => ({ ...d }))" />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import TwiiRealtimeChartRenderer from './TwiiRealtimeChartRenderer.vue'

const data = ref([])
const latest = ref(null)
let ws = null

onMounted(() => {
  ws = new WebSocket('/ws/twii')
  ws.onmessage = (event) => {
    const { time, value, raw_time } = JSON.parse(event.data)
    console.log('📩 收到即時資料:', { time, value, raw_time }) // ⬅️ 加這行
    data.value.push({ time, value })

    if (data.value.length > 120) {
      data.value.splice(0, data.value.length - 120)
    }

    console.log('📊 data.value 最新資料:', [...data.value].slice(-3)) // ⬅️ 加這行

    latest.value = { time, value, raw_time }
  }
})


onBeforeUnmount(() => {
  if (ws) ws.close()
})
</script>

<style scoped>
.twii-realtime-chart {
  padding: 20px;
}
.info-panel {
  margin-bottom: 10px;
  font-weight: bold;
  color: #007bff;
}
</style>
