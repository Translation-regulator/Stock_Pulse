<template>
  <div v-if="stocks.length">
    <h4>{{ category }}：共 {{ stocks.length }} 檔</h4>
    <div class="stock-wrapper">
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

    <div class="pagination-controls">
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
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  max-width: 900px;  /* 限制寬度以達成置中 */
}

.stock-btn {
  background: #333;
  color: white;
  border: none;
  width: 200px;
  height: 40px;
  font-size: 18px;
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


</style>