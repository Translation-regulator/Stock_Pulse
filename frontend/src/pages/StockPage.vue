<template>
  <div class="stock-page">
    <div class="input-group">
      <div class="input-wrapper">
        <input
          v-model="searchQuery"
          @keydown="handleKeydown"
          @blur="handleBlur"
          @focus="handleFocus"
          placeholder="輸入股號或股名"
          class="input"
        />
        <ul v-if="suggestions.length" class="suggestions">
          <li
            v-for="(item, index) in suggestions"
            :key="item.stock_id"
            :class="{ highlighted: index === highlightedIndex }"
            @click="() => selectSuggestion(item)"
          >
            {{ item.stock_id }} - {{ item.stock_name }}
          </li>
        </ul>
      </div>
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
import { ref, watch, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StockChartSwitcher from '../components/StockChartSwitcher.vue'

const route = useRoute()
const router = useRouter()

const searchQuery = ref('')
const suggestions = ref([])
const highlightedIndex = ref(-1)

const stockId = ref('')
const stockName = ref('')
const notFound = ref(false)
const loading = ref(false)

async function fetchSuggestions() {
  if (!searchQuery.value.trim()) {
    suggestions.value = []
    return
  }

  const res = await fetch(`/api/stocks/search?q=${encodeURIComponent(searchQuery.value)}`)
  if (res.ok) {
    suggestions.value = await res.json()
    highlightedIndex.value = -1
  }
}

async function fetchStockInfo(query) {
  const finalQuery = query || searchQuery.value
  if (!finalQuery) return

  loading.value = true
  notFound.value = false
  suggestions.value = []
  highlightedIndex.value = -1

  try {
    const res = await fetch(`/api/stocks/info/${encodeURIComponent(finalQuery)}`)
    if (!res.ok) throw new Error()
    const data = await res.json()
    stockId.value = data.stock_id
    stockName.value = data.stock_name

    // ✅ 路由同步更新
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

function selectSuggestion(item) {
  searchQuery.value = item.stock_id
  fetchStockInfo(item.stock_id)
}

function handleKeydown(e) {
  if (!suggestions.value.length) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    highlightedIndex.value = (highlightedIndex.value + 1) % suggestions.value.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    highlightedIndex.value =
      (highlightedIndex.value - 1 + suggestions.value.length) % suggestions.value.length
  } else if (e.key === 'Enter') {
    if (highlightedIndex.value >= 0) {
      selectSuggestion(suggestions.value[highlightedIndex.value])
    } else {
      fetchStockInfo()
    }
  } else if (e.key === 'Escape') {
    suggestions.value = []
    highlightedIndex.value = -1
  }
}

function handleBlur() {
  setTimeout(() => {
    suggestions.value = []
    highlightedIndex.value = -1
  }, 100)
}

function handleFocus() {
  if (searchQuery.value.trim()) {
    fetchSuggestions()
  }
}

watch(highlightedIndex, async () => {
  await nextTick()
  const list = document.querySelectorAll('.suggestions li')
  const el = list[highlightedIndex.value]
  if (el) el.scrollIntoView({ block: 'nearest' })
})

watch(searchQuery, fetchSuggestions)

// ✅ 如果網址有 stockId（/stock/1101）就自動查
onMounted(() => {
  const paramId = route.params.stockId
  if (paramId) {
    searchQuery.value = paramId
    fetchStockInfo(paramId)
  }
})
</script>




<style scoped>
.stock-page {
  margin-left: 10%;
  margin-right: 10%;
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

.input-wrapper {
  position: relative;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #333;
  border-radius: 8px;
  list-style: none;
  padding: 0;
  margin-top: 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;

  /* ✅ 隱藏滾輪（可切換為美化樣式） */
  scrollbar-width: none;        /* Firefox */
  -ms-overflow-style: none;     /* IE 10+ */
}
.suggestions::-webkit-scrollbar {
  display: none;                /* Chrome, Safari */
}

/* 若你想要自訂深色滾輪，可取消上面並使用這段：
.suggestions::-webkit-scrollbar {
  width: 6px;
}
.suggestions::-webkit-scrollbar-track {
  background: transparent;
}
.suggestions::-webkit-scrollbar-thumb {
  background-color: #555;
  border-radius: 3px;
}
.suggestions::-webkit-scrollbar-thumb:hover {
  background-color: #888;
}
*/

.suggestions li {
  padding: 0.6rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid #444;
  color: white;
}

.suggestions li:hover,
.suggestions li.highlighted {
  background: #1f6feb;
}



</style>
