<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStockList } from '@/composables/useStockList'
import ChatroomWindow from '@/components/ChatroomWindow.vue'
import { useAuth } from '@/composables/useAuth'

const openWindows = ref([])
const stockList = ref([])
const searchQuery = ref('')
const hasSearched = ref(false)

const { isLoggedIn } = useAuth()

// 工具函數：隨機取 20 筆
function getRandom15(list) {
  return [...list].sort(() => Math.random() - 0.5).slice(0, 15)
}

const filteredStocks = computed(() => {
  const q = searchQuery.value.toLowerCase()

  if (!q) {
    // 無搜尋字串 → 隨機取 20 筆
    return getRandom15(stockList.value)
  }

  // 有搜尋字串 → 篩選後取前 20 筆
  const matched = stockList.value.filter(stock =>
    stock.stock_id.toLowerCase().startsWith(q) ||
    stock.stock_name.toLowerCase().startsWith(q)
  )

  return matched.slice(0, 15)
})



onMounted(async () => {
  try {
    const result = await useStockList()
    stockList.value = result.stockList
  } catch (e) {
    console.error('取得股票列表失敗', e)
  }
})

function openChatroom(roomId) {
  if (!openWindows.value.find(win => win.roomId === roomId)) {
    let stockName = '聊天室'
    if (roomId === 'Twii') {
      stockName = '大盤聊天室'
    } else {
      if (stockList.value.length === 0) {
        console.warn('股票清單尚未載入，無法開啟聊天室')
        return
      }
      const stock = stockList.value.find(s => s.stock_id === roomId)
      if (!stock) {
        console.warn(`[ChatLobby] 找不到股票代號：${roomId}`)
      }
      stockName = stock?.stock_name || '未知股票'
    }

    openWindows.value.push({ roomId, stockName })
  }
}

function closeChatroom(roomId) {
  openWindows.value = openWindows.value.filter(win => win.roomId !== roomId)
}
</script>

<template>
  <div class="chatroom-layout">
    <aside class="channel-list">
      <h2>聊天室頻道</h2>

      <div v-if="!isLoggedIn" class="guest-warning">
        請先登入以使用聊天室功能
      </div>

      <template v-else>
        <input
          v-model="searchQuery"
          @input="hasSearched = true"
          placeholder="搜尋股票代號或名稱"
          class="search-input"
        />
        <ul>
          <li>
            <button @click="openChatroom('Twii')">大盤聊天室</button>
          </li>
          <li v-for="stock in filteredStocks" :key="stock.stock_id">
            <button @click="openChatroom(stock.stock_id)">
              {{ stock.stock_id }}（{{ stock.stock_name }}）聊天室
            </button>
          </li>
        </ul>
        <div v-if="hasSearched && filteredStocks.length === 0" class="no-result">
          查無相關股票
        </div>
      </template>
    </aside>

    <Teleport to="body">
      <ChatroomWindow
        v-for="win in openWindows"
        :key="win.roomId"
        :room-id="win.roomId"
        :stock-name="win.stockName"
        @close="closeChatroom(win.roomId)"
      />
    </Teleport>
  </div>
</template>

<style scoped>
.chatroom-layout {
  display: flex;
  height: 100vh;
}

.channel-list {
  width: 240px;
  background-color: #1e293b;
  padding: 1rem;
  color: white;
  border-right: 1px solid #334155;
}

.channel-list h2 {
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.channel-list ul {
  list-style: none;
  padding: 0;
  margin-top: 1rem;
}

.channel-list li {
  margin: 0.5rem 0;
}

.channel-list button {
  color: #94a3b8;
  background: none;
  border: none;
  text-align: left;
  width: 100%;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
}

.channel-list button:hover {
  background-color: #334155;
  color: white;
}

.search-input {
  width: 100%;
  padding: 6px 10px;
  font-size: 14px;
  border-radius: 6px;
  border: 1px solid #334155;
  background: #0f172a;
  color: white;
  box-sizing: border-box;
}

.guest-warning {
  color: #f87171;
  font-size: 14px;
  background: #1f2937;
  padding: 0.75rem;
  border-radius: 8px;
}

.no-result {
  color: #94a3b8;
  font-size: 13px;
  margin-top: 1rem;
  text-align: center;
}
</style>
