<template>
  <div class="chat-drawer" :class="{ open: isOpen }">
    <div class="chat-header">
      <h3>💬 {{ roomName }} 討論區</h3>
      <button @click="$emit('close')">✖</button>
    </div>

    <div class="chat-messages" ref="messageContainer">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="chat-message"
      >
        <div class="chat-meta">
          <strong>{{ msg.user_name || msg.guest_name || '匿名' }}</strong>
          <span class="timestamp">{{ formatTime(msg.created_at) }}</span>
        </div>
        <div class="chat-content">{{ msg.content }}</div>
      </div>
    </div>

    <div class="chat-input">
      <input
        v-model="newMessage"
        placeholder="輸入留言內容..."
        @keyup.enter="sendMessage"
      />
      <button @click="sendMessage">送出</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useAuth } from '@/composables/useAuth'
import api from '@/api'

const props = defineProps({
  isOpen: Boolean,
  roomId: String,
  roomName: String,
})

const emit = defineEmits(['close'])
const { isLoggedIn } = useAuth()

const newMessage = ref('')
const messages = ref([])
const guestName = ref(`訪客${Math.random().toString(36).slice(-4).toUpperCase()}`)

// 加入 ref 以便滾動控制
const messageContainer = ref(null)

function scrollToBottom() {
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

// 每次 roomId 變動時取得留言
watch(() => props.roomId, fetchComments, { immediate: true })

// 取得留言清單
async function fetchComments() {
  if (!props.roomId) return
  try {
    const res = await api.get(`/comments/${props.roomId}`)
    messages.value = res.data
    await nextTick() // 等 DOM 更新完成再滾動
    scrollToBottom()
  } catch (err) {
    console.error('取得留言失敗', err)
  }
}

// 傳送留言
async function sendMessage() {
  if (!newMessage.value.trim()) return

  try {
    const payload = { content: newMessage.value }

    if (!isLoggedIn.value) {
      payload.guest_name = guestName.value
    }

    await api.post(`/comments/${props.roomId}`, payload)
    await fetchComments()
    newMessage.value = ''
  } catch (err) {
    console.error('送出留言失敗', err)
  }
}

// 格式化時間
function formatTime(ts) {
  if (!ts || typeof ts !== 'string') return ''
  return ts.replace('T', ' ').slice(0, 16)
}
</script>

<style scoped>
.chat-drawer {
  width: 400px;
  height: 100%;
  background: #1e1e1e;
  color: white;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  box-sizing: border-box;
  margin-left: 20px;
}

.chat-drawer.open {
  right: 0;
}

.chat-header {
  padding: 1rem;
  background: #2c2c2c;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  min-height: 0; 
}

.chat-message {
  margin-bottom: 1rem;
  border-bottom: 1px solid #444;
  padding-bottom: 0.5rem;
}

.chat-meta {
  font-size: 0.85rem;
  color: #ccc;
  display: flex;
  justify-content: space-between;
}

.chat-input {
  padding: 1rem;
  border-top: 1px solid #333;
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0; 
  background-color: #1e1e1e;
}

.chat-input input {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 4px;
}

.chat-input button {
  background: #4caf50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #2c2c2c;
}

.chat-messages::-webkit-scrollbar-thumb {
  background-color: #555;
  border-radius: 4px;
  border: 2px solid #2c2c2c;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background-color: #888;
}

/* 手機 RWD：滿版寬度、固定高度、不撐爆 */
@media (max-width: 756px) {
  .chat-drawer {
    width: clamp(250px, 90vw, 400px);
    height: 50vh;
    margin-left: 0;
    border-radius: 8px;
    box-shadow: none;
    margin-top: 10px;
  }

  .chat-header,
  .chat-messages,
  .chat-input {
    padding: 0.75rem;
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
  }

  .chat-input {
    flex-shrink: 0;
    border-top: 1px solid #333;
    background-color: #1e1e1e;
  }
}


</style>
