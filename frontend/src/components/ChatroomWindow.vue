<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useAuth } from '@/composables/useAuth'
import axios from 'axios'

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

// 格式化 UTC 字串為台灣時區的 HH:mm
function formatTime(utcString) {
  if (!utcString || isNaN(Date.parse(utcString))) return 'Invalid'
  const date = new Date(utcString)
  return date.toLocaleTimeString('zh-TW', {
    timeZone: 'Asia/Taipei',
    hour12: false,
    hour: '2-digit',
    minute: '2-digit'
  })
}

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
        time: formatTime(msg.time)  // ✅ WebSocket 時間處理
      })
      scrollToBottom()
    } catch (e) {
      console.error('無法解析訊息格式：', event.data)
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
  try {
    const res = await axios.get(`${API_BASE}/chat/history/${props.roomId}`)
    messages.value = res.data.map(msg => ({
      fromSelf: msg.username === username.value,
      username: msg.username,
      content: msg.content,
      time: formatTime(msg.time)  // 歷史訊息時間處理
    }))
    scrollToBottom()
  } catch (e) {
    console.error('❌ 載入歷史訊息失敗', e)
  }

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

  // 拖曳 + 初始位置
  const el = chatroomRef.value
  el.style.left = `${100 + Math.random() * 200}px`
  el.style.top = `${100 + Math.random() * 100}px`

  let isDragging = false
  let offsetX = 0, offsetY = 0
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
    <h2 style="text-align: center;">聊天室：{{ roomId }}（{{ stockName }}）</h2>

    <div class="chatbox" ref="chatboxRef">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="['chat-wrapper', msg.fromSelf ? 'from-self' : 'from-other']"
      >
        <!-- 顯示使用者名稱（只顯示對方） -->
        <div v-if="!msg.fromSelf" class="chat-username">{{ msg.username }}</div>

        <!-- 訊息氣泡 -->
        <div class="chat-bubble">
          {{ msg.content }}
        </div>

        <!-- 時間顯示在泡泡左下角（泡泡外） -->
        <div class="chat-time">{{ msg.time }}</div>
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
  height: 520px;
  z-index: 999;
  cursor: pointer;
  border: 1px solid #333;
  padding: 1rem;
  background: #1e1e1e;
  border-radius: 12px;
  color: white;
  user-select: none;
  overflow: hidden;
  box-sizing: border-box;
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

/* 每則訊息容器 */
.chat-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 70%;
  margin-bottom: 10px;
}

.from-self {
  align-self: flex-end;
  text-align: right;
}

.from-other {
  align-self: flex-start;
  text-align: left;
}

/* 使用者名稱 */
.chat-username {
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 4px;
  margin-left: 4px;
  color: #ccc;
}

/* 泡泡本體 */
.chat-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  background: #3b82f6; /* 自己的藍色 */
  color: white;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-word;
}

.from-other .chat-bubble {
  background: #2a2a2a; /* 對方的灰色 */
}

/* 泡泡左下角時間（泡泡外） */
.chat-time {
  font-size: 11px;
  opacity: 0.6;
  margin-top: 3px;
  margin-left: 4px;
  align-self: flex-start;
}

/* 訊息輸入框 */
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

/* 自訂卷軸樣式 */
.chatbox::-webkit-scrollbar {
  width: 8px;
}

.chatbox::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.chatbox::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

.chatbox::-webkit-scrollbar-thumb:hover {
  background: #666;
}

</style>
