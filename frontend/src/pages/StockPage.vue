<template>
  <div class="stock-page">
    <h2>個股資訊</h2>

    <div class="search-group">
      <input
        v-model="searchQuery"
        @keyup.enter="fetchStockInfo"
        placeholder="輸入股號或股名"
        class="search-input"
      />
      <button class="search-btn" @click="fetchStockInfo">搜尋</button>
    </div>

    <div v-if="loading">📊 資料載入中...</div>
    <StockChartSwitcher
      v-else-if="stockId && stockName"
      :stockId="stockId"
      :stockName="stockName"
    />
    <p v-else-if="notFound">❌ 查無此股票</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StockChartSwitcher from '../components/StockChartSwitcher.vue'

const searchQuery = ref('')
const stockId = ref('')
const stockName = ref('')
const notFound = ref(false)
const loading = ref(false)

async function fetchStockInfo() {
  if (!searchQuery.value) return
  loading.value = true
  notFound.value = false

  try {
    const res = await fetch(`/api/stocks/info/${encodeURIComponent(searchQuery.value)}`)
    if (!res.ok) {
      stockId.value = ''
      stockName.value = ''
      notFound.value = true
      return
    }
    const data = await res.json()
    stockId.value = data.stock_id
    stockName.value = data.stock_name
  } catch (e) {
    console.error('取得個股資訊失敗', e)
    notFound.value = true
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.stock-page {
  margin: 1rem 5%;
  color: white;
}

.search-group {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.search-btn {
  padding: 0.75rem 1.25rem;
  font-size: 1rem;
  background: linear-gradient(to right, #6366f1, #9333ea);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}
.search-btn:hover {
  background: linear-gradient(to right, #4f46e5, #7e22ce);
}
</style>
