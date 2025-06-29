<template>
  <div v-if="stocks.length">
    <h4>{{ category }}：共 {{ stocks.length }} 檔</h4>

    <!-- 桌機版：按鈕清單 -->
    <div class="stock-wrapper desktop-only">
      <div class="stock-list">
        <button
          v-for="s in pagedStocks"
          :key="s.stock_id"
          class="stock-btn"
          @click="$emit('select', s)"
        >
          {{ s.stock_id }} {{ s.stock_name }}
        </button>
      </div>
    </div>

    <!-- 手機版：表單下拉選單 -->
    <div class="mobile-only mobile-stock-select">
      <select @change="handleSelect">
        <option disabled selected>請選擇股票</option>
        <option
          v-for="s in stocks"
          :key="s.stock_id"
          :value="JSON.stringify(s)"
        >
          {{ s.stock_id }} {{ s.stock_name }}
        </option>
      </select>
    </div>

    <!-- 分頁控制（桌機版才顯示） -->
    <div class="pagination-controls desktop-only">
      <button @click="prevPage" :disabled="page === 1">⬅ 上一頁</button>
      <span>第 {{ page }} 頁 / 共 {{ totalPages }} 頁</span>
      <button @click="nextPage" :disabled="page === totalPages">下一頁 ➡</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import api from '@/api'

const props = defineProps({
  category: String
})

const stocks = ref([])
const page = ref(1)
const pageSize = 20

const totalPages = computed(() =>
  Math.ceil(stocks.value.length / pageSize)
)

const pagedStocks = computed(() => {
  const start = (page.value - 1) * pageSize
  const end = start + pageSize
  return stocks.value.slice(start, end)
})

function nextPage() {
  if (page.value < totalPages.value) page.value++
}

function prevPage() {
  if (page.value > 1) page.value--
}

// 用於手機版 select 選擇股票
function handleSelect(event) {
  const selected = JSON.parse(event.target.value)
  if (selected) {
    emit('select', selected)
  }
}

const emit = defineEmits(['select'])

watch(() => props.category, async (newCategory) => {
  if (!newCategory) return
  const res = await api.get('/stocks/industry', {
    params: { category: newCategory }
  })
  stocks.value = res.data
  page.value = 1
})
</script>

<style scoped>
h4 {
  font-size: 20px;
  text-align: center;
}

.stock-wrapper {
  display: flex;
  justify-content: center;
}

.stock-list {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  max-width: 900px;
}

.stock-btn {
  background: #333;
  color: white;
  border: none;
  width: 150px;
  height: 30px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  transition: 0.2s;
}

.stock-btn:hover {
  background: #555;
}

.pagination-controls {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  color: white;
}

.pagination-controls button {
  background: #444;
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.pagination-controls button[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 手機版 select 表單 */
.mobile-only {
  display: none;
}

.desktop-only {
  display: block;
}

/* 手機 RWD */
@media (max-width: 768px) {
  .desktop-only {
    display: none;
  }

  .mobile-only {
    display: block;
  }

  .mobile-stock-select {
    width: 100%;
    margin-top: 1rem;
    text-align: center;
  }

  .mobile-stock-select select {
    width: 80%;
    padding: 8px;
    font-size: 16px;
    border-radius: 6px;
    background: #222;
    color: white
  }
}
</style>
