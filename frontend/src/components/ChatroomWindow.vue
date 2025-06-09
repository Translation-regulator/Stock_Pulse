<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useAuth } from '@/composables/useAuth'
import axios from 'axios'

// 🟡 傳入 props：roomId（股票代號）、stockName（股票名稱）
const props = defineProps({
  roomId: String,
  stockName: String
})
const emit = defineEmits(['close'])

const { accessToken, username } = useAuth()
const input = ref('')
const messages = ref([])
const chatboxRef = ref(null)
const chatroomRef = ref(null)

let socket = null
let connected = false
let reconnectTimer = null
const WS_BASE = import.meta.env.VITE_WS_BASE || 'ws://localhost:8000'

function scrollToBottom() {
  nextTick(() => {
    if (chatboxRef.value) {
      chatboxRef.value.scrollTop = chatboxRef.value.scrollHeight
    }
  })
}
watch(messages, scrollToBottom)
onMounted(scrollToBottom)

const connectSocket = () => {
  if (connected || !accessToken.value) return
  socket = new WebSocket(`${WS_BASE}/ws/chat?token=${accessToken.value}&room=${props.roomId}`)

  socket.onopen = () => {
    connected = true
    console.log(`[WS] 房間 ${props.roomId} 已連線`)
  }

  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data)
      messages.value.push({
        fromSelf: msg.username === username.value,
        username: msg.username,
        content: msg.content,
        time: msg.time,
      })
    } catch (e) {
      console.error('❌ 無法解析訊息格式：', event.data)
    }
  }

  socket.onerror = (e) => {
    console.error('[WS] 錯誤：', e)
  }

  socket.onclose = () => {
    connected = false
    reconnectTimer = setTimeout(connectSocket, 5000)
  }
}

let stopWatcher
const API_BASE = import.meta.env.VITE_API_BASE
onMounted(async () => {
  // ✅ 載入歷史訊息
  try {
    const res = await axios.get(`${API_BASE}/chat/history/${props.roomId}`)
    messages.value = res.data.map(msg => ({
      fromSelf: msg.username === username.value,
      ...msg
    }))
  } catch (e) {
    console.error('❌ 載入歷史訊息失敗', e)
  }

  // ✅ 建立 WebSocket 即時連線
  stopWatcher = watch(
    () => accessToken.value,
    (token) => {
      if (token) {
        connectSocket()
        stopWatcher && stopWatcher()
      }
    },
    { immediate: true, flush: 'post' }
  )

  // ✅ 拖曳功能
  let isDragging = false
  let offsetX = 0
  let offsetY = 0

  nextTick(() => {
    const el = chatroomRef.value
    if (!el) return

    el.style.left = `${100 + Math.random() * 200}px`
    el.style.top = `${100 + Math.random() * 100}px`

    el.addEventListener('mousedown', (e) => {
      isDragging = true
      offsetX = e.clientX - el.offsetLeft
      offsetY = e.clientY - el.offsetTop
      document.body.style.userSelect = 'none'
    })

    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return
      el.style.left = `${e.clientX - offsetX}px`
      el.style.top = `${e.clientY - offsetY}px`
    })

    document.addEventListener('mouseup', () => {
      isDragging = false
      document.body.style.userSelect = ''
    })
  })
})

onBeforeUnmount(() => {
  if (socket) socket.close()
  if (reconnectTimer) clearTimeout(reconnectTimer)
})

function sendMessage() {
  if (!input.value.trim()) return
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ content: input.value.trim() }))
    input.value = ''
  }
}
</script>

<template>
  <div class="chatroom-container" ref="chatroomRef">
    <button class="chat-close" @click="emit('close')">✖</button>
    <h2>聊天室：{{ roomId }}（{{ stockName }}）</h2>

    <div class="chatbox" ref="chatboxRef">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="['chat-message', msg.fromSelf ? 'from-self' : 'from-other']"
      >
        <div class="chat-meta">
          <span class="chat-username">{{ msg.username }}</span>
          <span class="chat-timestamp">{{ msg.time }}</span>
        </div>
        <div class="chat-content">{{ msg.content }}</div>
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

<style scoped>
.chatroom-container {
  position: fixed;
  width: 400px;
  z-index: 999;
  cursor: move;
  border: 1px solid #333;
  padding: 1rem;
  background: #1e1e1e;
  border-radius: 12px;
  color: white;
  user-select: none;
}

.chat-close {
  position: absolute;
  top: 4px;
  right: 6px;
  background: transparent;
  color: white;
  border: none;
  font-size: 18px;
  cursor: pointer;
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
  display: flex;
  flex-direction: column;
  padding: 6px 10px;
  border-radius: 8px;
  max-width: 80%;
  word-wrap: break-word;
  line-height: 1.4;
  background: #2a2a2a;
}

.from-self {
  align-self: flex-end;
  background: #3b82f6;
  color: white;
}

.from-other {
  align-self: flex-start;
  background: #2a2a2a;
}

.chat-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #ccc;
  margin-bottom: 2px;
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
