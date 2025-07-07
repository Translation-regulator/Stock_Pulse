<template>
  <div class="stock-page">
    <div class="chart-area" :class="{ 'half-height': showChat }">
      <StockChartSwitcher
        :stock-id="stockId"
        :stock-name="stockName"
        :show-chat="showChat"
        @open-chat="showChat = true"
      />
    </div>

    <SlideChatDrawer
      v-if="showChat"
      :isOpen="true"
      :roomId="stockId"
      :roomName="stockName"
      @close="showChat = false"
      class="chat-section"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StockChartSwitcher from '../components/StockChartSwitcher.vue'
import SlideChatDrawer from '../components/SlideChatDrawer.vue'

const route = useRoute()
const router = useRouter()

const stockId = ref('')
const stockName = ref('')
const loading = ref(false)
const notFound = ref(false)
const showChat = ref(false)

function handleStockSelect(stock) {
  router.push(`/stock/${stock.stock_id}`)
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

<style scoped>
.stock-page {
  display: flex;
  height: calc(100vh - 60px);
  background-color: #121212;
  padding: 0 2%;
  position: relative;
}

.chart-area {
  flex: 1;
  overflow: hidden;
  transition: height 0.3s ease;
}

.chat-section {
  width: 100%;
  max-width: 400px;
  height: 100%;
  transition: height 0.3s ease;
}

@media (max-width: 756px) {
  .stock-page {
    flex-direction: column;
  }

  .chart-area {
    flex: none;
    height: 100%;
  }

  .chart-area.half-height {
    height: 56vh;
  }

  .chat-section {
    flex: none;
    width: 100%;
    max-width: 100%;
    height: 37dvh;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    overflow: hidden;
  }

  .chat-section .chat-messages {
    flex: 1;
    overflow-y: auto;
  }

  .chat-section .chat-input {
    padding: 0.5rem;
    border-top: 1px solid #333;
    background-color: #1e1e1e;
  }
}
</style>
