<template>
  <div class="chat-drawer" :class="{ open: isOpen }">
    <div class="chat-header">
      <h3>💬 {{ roomName }} 討論區</h3>
      <button @click="$emit('close')">✖</button>
    </div>

    <div class="chat-messages">
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
import { ref, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import api from '@/api'

// ✅ 接收 props
const props = defineProps({
  isOpen: Boolean,
  roomId: String,
  roomName: String,
})

const emit = defineEmits(['close'])

const { isLoggedIn } = useAuth()

// ✅ 狀態管理
const newMessage = ref('')
const messages = ref([])
const guestName = ref(`訪客${Math.random().toString(36).slice(-4).toUpperCase()}`)

// ✅ 每次 roomId 變動時取得留言
watch(() => props.roomId, fetchComments, { immediate: true })

// ✅ 取得留言清單
async function fetchComments() {
  if (!props.roomId) return
  try {
    const res = await api.get(`/comments/${props.roomId}`)
    messages.value = res.data
  } catch (err) {
    console.error('取得留言失敗', err)
  }
}

// ✅ 傳送留言
async function sendMessage() {
  if (!newMessage.value.trim()) return

  try {
    const payload = {
      content: newMessage.value,
    }

    // 若未登入，加上訪客名稱
    if (!isLoggedIn.value) {
      payload.guest_name = guestName.value
    }

    // 送出留言
    await api.post(`/comments/${props.roomId}`, payload)

    // 重新抓留言清單（保證 user_name 正確）
    await fetchComments()

    // 清空輸入框
    newMessage.value = ''
  } catch (err) {
    console.error('送出留言失敗', err)
  }
}

// ✅ 格式化時間
function formatTime(ts) {
  if (!ts || typeof ts !== 'string') return ''
  return ts.replace('T', ' ').slice(0, 16)
}
</script>

<style scoped>
.chat-drawer {
  position: fixed;
  top: 0;
  right: -400px;
  width: 400px;
  height: 100%;
  background: #1e1e1e;
  color: white;
  box-shadow: -2px 0 5px rgba(0,0,0,0.3);
  transition: right 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  z-index: 1000;
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
</style>
