<template>
  <div class="chatroom-container">
    <h2>聊天室 - {{ roomId }}</h2>

    <div class="chatbox" ref="chatboxRef">
      <div v-for="(msg, idx) in messages" :key="idx" class="chat-message">
        {{ msg }}
      </div>
    </div>

    <input
      v-model="input"
      @keyup.enter="sendMessage"
      placeholder="輸入訊息並按 Enter"
      class="chat-input"
    />
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const roomId = route.params.roomId || 'default'
const { accessToken } = useAuth()

const input = ref('')
const messages = ref([])
const chatboxRef = ref(null)
let socket = null

const WS_BASE = import.meta.env.VITE_WS_BASE || 'ws://localhost:8000'

// 📌 自動滾動到最新訊息
watch(messages, async () => {
  await nextTick()
  if (chatboxRef.value) {
    chatboxRef.value.scrollTop = chatboxRef.value.scrollHeight
  }
})

// 📌 建立 WebSocket 連線
const connectSocket = () => {
  if (!accessToken.value) {
    console.warn('尚未取得 accessToken，延後建立 WebSocket')
    return
  }

  socket = new WebSocket(`${WS_BASE}/ws/chat/${roomId}?token=${accessToken.value}`)

  socket.onopen = () => {
    console.log('WebSocket 已連線')
  }

  socket.onmessage = (event) => {
    messages.value.push(event.data)
  }

  socket.onerror = (e) => {
    console.error('WebSocket 錯誤：', e)
  }

  socket.onclose = () => {
    console.warn('WebSocket 已關閉')
  }
}

onMounted(() => {
  let stopWatcher = null

  stopWatcher = watch(
    () => accessToken.value,
    (token) => {
      if (token) {
        connectSocket()
        stopWatcher && stopWatcher()  // ✅ 確保只監聽一次
      }
    },
    {
      immediate: true,
      flush: 'post'  // 避免初始化時機衝突
    }
  )
})



onBeforeUnmount(() => {
  if (socket) socket.close()
})

// 📌 發送訊息
function sendMessage() {
  if (!input.value.trim()) return

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(input.value)
    input.value = ''
  } else {
    console.warn('WebSocket 尚未連線，訊息未送出')
  }
}
</script>

<style scoped>
.chatroom-container {
  width: 70%;
  margin: 10% auto;
  border: 1px solid #333;
  padding: 1rem;
  background: #1e1e1e;
  border-radius: 12px;
  color: white;
}

.chatbox {
  height: 350px;
  overflow-y: auto;
  border: 1px solid #444;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  background-color: #121212;
  border-radius: 6px;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.chat-message {
  padding: 6px 10px;
  border-radius: 8px;
  background: #2a2a2a;
  max-width: 80%;
  word-wrap: break-word;
  line-height: 1.4;
}

.chat-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #444;
  border-radius: 6px;
  background: #1a1a1a;
  color: white;
}
</style>
