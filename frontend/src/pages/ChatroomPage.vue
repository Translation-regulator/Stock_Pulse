<template>
  <div class="chatroom-container" ref="chatroomRef">
    <h2>聊天室 - {{ roomId }}</h2>

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

<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const roomId = route.params.roomId || 'default'
const { accessToken, username } = useAuth()

const input = ref('')
const messages = ref([])
const chatboxRef = ref(null)
const chatroomRef = ref(null)
let socket = null

const WS_BASE = import.meta.env.VITE_WS_BASE || 'ws://localhost:8000'

// 📌 自動滾動到最底
function scrollToBottom() {
  nextTick(() => {
    if (chatboxRef.value) {
      chatboxRef.value.scrollTop = chatboxRef.value.scrollHeight
    }
  })
}
watch(messages, scrollToBottom)
onMounted(scrollToBottom)

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
    try {
      const msg = JSON.parse(event.data)
      console.log('[收到訊息]', msg)

      messages.value.push({
        fromSelf: msg.username === username.value,
        username: msg.username,
        content: msg.content,
        time: msg.time,
      })
    } catch (e) {
      console.error('無法解析訊息格式：', event.data)
    }
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
        stopWatcher && stopWatcher()
      }
    },
    { immediate: true, flush: 'post' }
  )

  // 📌 拖曳功能
  let isDragging = false
  let offsetX = 0
  let offsetY = 0

  const el = chatroomRef.value
  if (!el) return

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
})

// 📌 發送訊息
function sendMessage() {
  if (!input.value.trim()) return

  const now = new Date()
  const formattedTime = now.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })

  const payload = {
    username: username.value || '我',
    content: input.value,
    time: formattedTime,
  }

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(payload))
    input.value = ''
    input.value = ''
  } else {
    console.warn('WebSocket 尚未連線，訊息未送出')
  }
}
</script>

<style scoped>
.chatroom-container {
  position: fixed;
  top: 10%;
  left: 15%;
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
