<template>
  <div class="twii-realtime">
      <span>加權指數：</span>
      <strong :class="isUp ? 'up' : 'down'">{{ twii !== null ? twii.toFixed(2) : '載入中...' }}</strong>
      <span>  更新時間：</span>
      <span>{{ time || '載入中...' }}</span>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const twii = ref(null)
const time = ref('')
const isUp = ref(true)
let ws = null

onMounted(() => {
  const base = import.meta.env.VITE_WS_BASE
  ws = new WebSocket(`${base}/ws/twii`)
  ws.onmessage = (event) => {
    const payload = JSON.parse(event.data)
    if (payload?.value !== undefined) {
      if (twii.value !== null) {
        isUp.value = payload.value >= twii.value 
      }
      twii.value = payload.value
      time.value = payload.raw_time
    }
  }
})
onBeforeUnmount(() => {
  if (ws) ws.close()
})
</script>

<style scoped>
.twii-realtime {
  font-size: 1.0rem;
  padding: 0.5rem 1rem;
  background-color: #2a2a2b;
  border-radius: 8px;
  max-width: 400px;
}
.up {
  color: #e53935;
}
.down {
  color: #43a047;
}
</style>
