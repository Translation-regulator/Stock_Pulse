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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StockChartSwitcher from '../components/StockChartSwitcher.vue'
import StockSearchInput from '../components/StockSearchInput.vue'

const route = useRoute()
const router = useRouter()

const stockId = ref('')
const stockName = ref('')
const notFound = ref(false)
const loading = ref(false)

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

    // 路由同步更新
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

// 如果網址有 stockId 就自動查
onMounted(() => {
  const paramId = route.params.stockId
  if (paramId) {
    fetchStockInfo(paramId)
  }
})
</script>

<style scoped>
.stock-page {
  margin-left: 10%;
  margin-right: 10%;
  box-sizing: border-box;
  color: white;
}

.input-group {
  margin-top: 0.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}
</style>
