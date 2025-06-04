<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StockChartSwitcher from '../components/StockChartSwitcher.vue'
import StockSearchInput from '../components/StockSearchInput.vue'
import SlideChatDrawer from '../components/SlideChatDrawer.vue' // ✅ 加入

const route = useRoute()
const router = useRouter()

const stockId = ref('')
const stockName = ref('')
const notFound = ref(false)
const loading = ref(false)
const showChat = ref(false) // ✅ 控制聊天室抽屜

async function fetchStockInfo(query) {
  if (!query) return

  loading.value = true
  notFound.value = false

  try {
    const base = import.meta.env.VITE_API_BASE
    const res = await fetch(`${base}/stocks/info/${encodeURIComponent(query)}`)
    if (!res.ok) throw new Error()
    const data = await res.json()
    stockId.value = data.stock_id
    stockName.value = data.stock_name

    if (route.params.stockId !== data.stock_id) {
      router.push(`/stock/${data.stock_id}`)
    }
  } catch (e) {
    console.error('取得個股資訊失敗', e)
    notFound.value = true
  } finally {
    loading.value = false
  }
}

function handleStockSelect(stock) {
  stockId.value = stock.stock_id
  stockName.value = stock.stock_name
  fetchStockInfo(stock.stock_id)
}

onMounted(() => {
  const paramId = route.params.stockId
  if (paramId) {
    fetchStockInfo(paramId)
  }
})
</script>

<template>
  <div class="stock-page">
    <div class="input-group">
      <StockSearchInput @select="handleStockSelect" />
    </div>

    <div v-if="loading">資料載入中...</div>
    <StockChartSwitcher
      v-else-if="stockId && stockName"
      :stockId="stockId"
      :stockName="stockName"
    />
    <p v-else-if="notFound">查無此股票</p>

    <!-- 💬 留言按鈕 -->
    <button
      v-if="stockId"
      class="chat-toggle-button"
      @click="showChat = true"
    >
      💬 留言
    </button>

    <!-- 🪟 抽屜聊天室 -->
    <SlideChatDrawer
      :isOpen="showChat"
      :roomId="stockId"
      :roomName="stockName"
      @close="showChat = false"
    />
  </div>
</template>

<style scoped>
.stock-page {
  margin-left: 10%;
  margin-right: 10%;
  box-sizing: border-box;
  color: white;
  position: relative;
}

.input-group {
  margin-top: 0.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.chat-toggle-button {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 999;
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 0.75rem 1.2rem;
  border-radius: 999px;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}
</style>
