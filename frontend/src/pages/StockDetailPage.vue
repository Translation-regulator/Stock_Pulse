<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StockChartSwitcher from '../components/StockChartSwitcher.vue'
import SlideChatDrawer from '../components/SlideChatDrawer.vue'
import StockSearchInput from '../components/StockSearchInput.vue'

const route = useRoute()
const router = useRouter()

const stockId = ref('')
const stockName = ref('')
const loading = ref(false)
const notFound = ref(false)
const showChat = ref(false)

function handleStockSelect(stockCode) {
  router.push(`/stock/${stockCode}`)
}

async function fetchStockInfo(stockCode) {
  loading.value = true
  notFound.value = false
  try {
    const base = import.meta.env.VITE_API_BASE
    const res = await fetch(`${base}/stocks/info/${encodeURIComponent(stockCode)}`)
    if (!res.ok) throw new Error()
    const data = await res.json()
    stockId.value = data.stock_id
    stockName.value = data.stock_name
  } catch (err) {
    notFound.value = true
  } finally {
    loading.value = false
  }
}

watch(() => route.params.stockId, (newId) => {
  if (newId) fetchStockInfo(newId)
}, { immediate: true })
</script>

<template>
  <div class="stock-page">
    <div class="chart-area">
      <!-- 返回搜尋 -->
      <div class="top-center-button">
        <button class="back-button" @click="router.push('/stock')">返回搜尋</button>
        <StockSearchInput @select="handleStockSelect" class="wide-input" />
      </div>

      <!-- 圖表 + 留言 -->
      <div class="main-chart" :class="{ compressed: showChat }">
        <div class="chart-panel">
          <StockChartSwitcher
            :stock-id="stockId"
            :stock-name="stockName"
            :show-chat="showChat"     
            @open-chat="showChat = true"
          />
        </div>

        <SlideChatDrawer
          v-show="showChat"
          class="chat-panel"
          :isOpen="true"
          :roomId="stockId"
          :roomName="stockName"
          @close="showChat = false"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.stock-page {
  display: flex;
  height: 100vh;
  background-color: #121212;
  color: white;
  padding: 0 2%;
}

.chart-area {
  flex: 1;
  box-sizing: border-box;
  margin-top: 1rem;
  overflow: hidden;
}

.top-center-button {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.main-chart {
  display: flex;
  height: 90vh;
  position: relative;
  transition: all 0.3s ease;
}

.chart-panel {
  flex: 1;
  overflow: auto;
  transition: all 0.3s ease;
}

.chat-panel {
  width: 400px;
  position: relative;
  transition: all 0.3s ease;
}

.back-button {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  background-color: #121212;
  color: white;
  border: 1px solid #333;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.back-button:hover {
  background-color: #1e1e1e;
  border-color: #555;
}

/* 手機版 */
@media (max-width: 768px) {
  .stock-page {
    height: calc(100vh - 60px);
  }

  .chart-area {
    margin-top: 0.5rem;
  }

  .top-center-button {
    display: none;
  }

  .main-chart {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    transition: all 0.3s ease;
  }

  
  .chat-panel {
    height: 60vh;
    width: 100%;
    overflow: hidden;
    transition: height 0.3s ease;
    box-sizing: border-box;
    margin-top: 10px;
  }

  .main-chart.compressed > .chart-panel {
    height: 30vh;
  }

  .main-chart.compressed > .chat-panel {
    height: 40vh;
  }
}
</style>
