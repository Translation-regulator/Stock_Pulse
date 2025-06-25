<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StockChartSwitcher from '../components/StockChartSwitcher.vue'
import StockSearchInput from '../components/StockSearchInput.vue'
import SlideChatDrawer from '../components/SlideChatDrawer.vue'
import IndustryFilter from '../components/IndustryFilter.vue'
import StockList from '../components/StockList.vue'

const route = useRoute()
const router = useRouter()

const stockId = ref('')
const stockName = ref('')
const notFound = ref(false)
const loading = ref(false)
const showChat = ref(false)

const selectedIndustry = ref('')
const hasSelected = ref(false)

// 根據參數載入股票資訊
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

// 點選某支股票（搜尋或分類）
function handleStockSelect(stock) {
  stockId.value = stock.stock_id
  stockName.value = stock.stock_name
  hasSelected.value = true
  fetchStockInfo(stock.stock_id)
}

// 監看路由變化：進入股票 or 回搜尋
watch(() => route.params.stockId, (newId) => {
  if (newId) {
    hasSelected.value = true
    fetchStockInfo(newId)
  } else {
    // 返回搜尋狀態
    stockId.value = ''
    stockName.value = ''
    hasSelected.value = false
    notFound.value = false
  }
}, { immediate: true })
</script>

<template>
  <div class="stock-page">
    <div class="chart-area">
      <!-- 搜尋輸入框 -->
      <div class="input-group-wrapper">
        <!-- 返回搜尋按鈕靠左 -->
        <div class="back-button-wrapper">
          <button
            v-if="hasSelected && stockId"
            class="back-button"
            @click="router.push('/stock')"
          >
            返回搜尋
          </button>
        </div>

        <!-- 輸入框絕對置中 -->
        <div class="input-absolute-center">
          <StockSearchInput @select="handleStockSelect" />
        </div>
      </div>


      <!-- 搜尋分類列表 -->
      <template v-if="!hasSelected">
        <IndustryFilter @select="selectedIndustry = $event" />
        <StockList :category="selectedIndustry" @select="handleStockSelect" />
      </template>

      <!-- 主圖表內容 -->
      <div v-if="loading">資料載入中...</div>
      <StockChartSwitcher
        v-else-if="stockId && stockName"
        :stockId="stockId"
        :stockName="stockName"
      />
      <p v-else-if="notFound">查無此股票</p>
    </div>

    <!-- 聊天室 -->
    <SlideChatDrawer
      v-if="showChat && stockId"
      :isOpen="true"
      :roomId="stockId"
      :roomName="stockName"
      @close="showChat = false"
    />

    <!-- 開啟留言按鈕 -->
    <button
      v-if="stockId && !showChat"
      class="chat-toggle-button"
      @click="showChat = true"
    >
      留言
    </button>
  </div>
</template>

<style scoped>
.stock-page {
  display: flex;
  height: 100vh;
  background-color: #121212;
  color: white;
  padding-left: 2%;
  padding-right: 2%;
}

.chart-area {
  flex: 1;
  overflow: auto;
  box-sizing: border-box;
}

.input-group-wrapper {
  position: relative;
  height: 30px; /* 調整這個高度使容器有空間 */
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}

.back-button-wrapper {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
}

.input-absolute-center {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}


.input-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.back-button {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  background-color: #444;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.back-button:hover {
  background-color: #666;
}



.chat-toggle-button {
  position: fixed;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  writing-mode: vertical-rl;
  background-color: #2e6b30;
  color: white;
  border: none;
  border-radius: 8px 0 0 8px;
  padding: 0.5rem 0.3rem;
  cursor: pointer;
  z-index: 999;
  font-size: 0.9rem;
  opacity: 0.6;
}
</style>
