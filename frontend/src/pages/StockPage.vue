<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StockChartSwitcher from '../components/StockChartSwitcher.vue'
import StockSearchInput from '../components/StockSearchInput.vue'
import SlideChatDrawer from '../components/SlideChatDrawer.vue' 

const route = useRoute()
const router = useRouter()

const stockId = ref('')
const stockName = ref('')
const notFound = ref(false)
const loading = ref(false)
const showChat = ref(false)

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
    <!-- 左側圖表＋搜尋 -->
    <div class="chart-area">
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
    </div>

    <!-- 右側聊天室 -->
    <SlideChatDrawer
      v-if="showChat && stockId"
      :isOpen="true"
      :roomId="stockId"
      :roomName="stockName"
      @close="showChat = false"
    />

    <!-- 浮動留言按鈕 -->
    <button
      v-if="stockId && !showChat"
      class="chat-toggle-button"
      @click="showChat = true"
    >
      💬 留言
    </button>
  </div>
</template>

<style scoped>
.stock-page {
  display: flex;
  height: 100vh;
  background-color: #121212;
  color: white;
  padding-left: 10%;
  padding-right: 10%;
}

.chart-area {
  flex: 1;
  padding: 1rem rem;
  overflow: hidden;
  box-sizing: border-box;
}

.input-group {
  margin-top: 1rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: center;
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
