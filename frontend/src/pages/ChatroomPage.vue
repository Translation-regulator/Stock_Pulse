<template>
  <div class="chatroom-container" ref="chatroomRef">
    <h2>聊天室</h2>

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

  socket = new WebSocket(`${WS_BASE}/ws/chat?token=${accessToken.value}`)

  socket.onopen = () => {
    connected = true
    console.log('[WS] 已連線')
  }

  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data)
      console.log('[📨 收到訊息]', msg)

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
    console.warn('[WS] 已關閉，5 秒後重新連線')
    reconnectTimer = setTimeout(connectSocket, 5000)
  }
}


let stopWatcher

onMounted(() => {
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
  if (socket) {
    try {
      socket.close()
    } catch (e) {
      console.warn('關閉 WebSocket 發生錯誤：', e)
    }
  }
  if (reconnectTimer) clearTimeout(reconnectTimer)
})

function sendMessage() {
  if (!input.value.trim()) return

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ content: input.value.trim() }))
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
