<template>
  <div class="stock-realtime">
    <span>{{ stockName }}（{{ stockId }}）：</span>
    <strong :class="isUp ? 'up' : 'down'">
      <template v-if="price !== null">
        {{ price.toFixed(2) }}
      </template>
      <template v-else>
        尚無成交
      </template>
    </strong>
    <span>     更新時間：</span>
    <span>{{ time || '載入中...' }}</span>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

// 👉 接收 props + emit
const props = defineProps({ stockId: String })
const emit = defineEmits(['update'])  // ⭐ 定義事件

const stockName = ref('')
const price = ref(null)
const time = ref('')
const isUp = ref(true)
let socket = null

const connectWebSocket = () => {
  if (!props.stockId) return
  if (socket) socket.close()

  const base = import.meta.env.VITE_WS_BASE
  socket = new WebSocket(`${base}/ws/stock/${props.stockId}`)

  socket.onopen = () => {
    console.log(`✅ WebSocket 已連線: /ws/stock/${props.stockId}`)
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.error) {
      console.error('⚠️ 後端錯誤:', data.error)
      return
    }

    stockName.value = data.stock_name

    if (typeof data.price === 'number') {
      isUp.value = price.value !== null ? data.price >= price.value : true
      price.value = data.price

      // emit 給父層
      emit('update', {
        stock_id: props.stockId,
        stock_name: stockName.value, 
        price: price.value,
        prev_close: data.prev_close,
      })
    }

    if (data.time) {
      time.value = new Date(parseInt(data.time)).toLocaleTimeString()
    }
  }

  socket.onerror = (err) => {
    console.error("⚠️ WebSocket 錯誤：", err)
  }

  socket.onclose = () => {
    console.warn("❌ WebSocket 關閉")
  }
}

onMounted(connectWebSocket)
watch(() => props.stockId, connectWebSocket)
onBeforeUnmount(() => { if (socket) socket.close() })
</script>

<style scoped>
.stock-realtime {
  font-size: 16px;
  padding: 0.5rem 1rem;
  background-color: #2a2a2b;
  border-radius: 8px;
  max-width: 400px;
  margin: 0.5rem 0rem;
}
.up {
  color: #e53935;
}
.down {
  color: #43a047;
}
</style>
