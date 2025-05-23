<template>
  <div class="stock-page">
    <div class="input-group">
      <input
        v-model="searchQuery"
        @keyup.enter="fetchStockInfo"
        placeholder="輸入股號或股名"
        class="input"
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

.input-group {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.input {
  padding: 0.8rem 1.5rem;
  width: 300px;
  font-size: 1rem;
  border-radius: 8px;
  border: none;
  background: #222;
  color: white;
  outline: none;
}

.search-btn {
  font-size: 1.2rem;
  background: #1f6feb;
  color: white;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.search-btn:hover {
  background: #3b82f6;
}
.search-btn:hover {
  background: linear-gradient(to right, #4f46e5, #7e22ce);
}
</style>
