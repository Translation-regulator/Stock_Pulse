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
    <div class="chart-area" :class="{ 'with-chat': showChat }">
      <!-- 返回搜尋 -->
      <div class="top-center-button">
        <button class="back-button" @click="router.push('/stock')">返回搜尋</button>
        <StockSearchInput @select="handleStockSelect" class="wide-input" />
      </div>

      <!-- 圖表 -->
      <div class="main-chart">
        <div class="chart-panel">
          <StockChartSwitcher
            :stock-id="stockId"
            :stock-name="stockName"
            @open-chat="showChat = true"
          />
        </div>

        <!-- 留言區 -->
        <SlideChatDrawer
          v-if="showChat"
          class="chat-panel"
          :isOpen="true"
          :roomId="stockId"
          :roomName="stockName + ' 討論區'"
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

/* 左側圖表區 */
.chart-panel {
  flex: 1;
  overflow: auto;
  transition: all 0.3s ease;
}

/* 右側留言板（桌機） */
.chat-panel {
  width: 400px;
  position: relative;
  transition: all 0.3s ease;
}

/* 返回按鈕 */
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

  .chart-panel {
    flex: 1;
    height: 100%;
    transition: all 0.3s ease;
    overflow: auto;
  }

  .with-chat .chart-panel {
    height: 50%;
  }

  .chat-panel {
    height: 0;
    width: 100%;
    overflow: hidden;
    transition: height 0.3s ease;
  }

  .with-chat .chat-panel {
    height: 50%;
  }
}
</style>

