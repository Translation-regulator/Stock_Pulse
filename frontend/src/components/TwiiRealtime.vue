<template>
  <div class="twii-realtime">
    <span>即時加權指數：</span>
    <span v-if="twii !== null">{{ parseFloat(twii).toFixed(2) }}</span>
    <span v-else>載入中...</span>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { parseFuglePayload } from '@/utils/fugle' // 如果你有分 utils 資料夾

const twii = ref(null)
let ws = null

onMounted(() => {
  console.log("📡 嘗試連接 WebSocket /ws/twii")
  ws = new WebSocket('/ws/twii')

  ws.onopen = () => {
    console.log('✅ WebSocket 成功連線')
  }

  ws.onmessage = (event) => {
    const payload = parseFuglePayload(event)
    console.log("🧪 解析後 payload：", payload)

    if (payload?.index !== undefined) {
      twii.value = payload.index
      console.log("✅ 更新 twii.value 成功 =", payload.index)
    }
  }

  ws.onerror = (e) => {
    console.error('❌ WebSocket 發生錯誤', e)
  }

  ws.onclose = () => {
    console.warn('🔌 WebSocket 已關閉')
  }
})

onBeforeUnmount(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<style scoped>
.twii-realtime {
  font-size: 1.5rem;
  font-weight: bold;
  padding: 1rem;
}

.up {
  color: #e53935; /* 紅色 */
}

.down {
  color: #43a047; /* 綠色 */
}
</style>
