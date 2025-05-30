<template>
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
        @mousedown.prevent="() => selectSuggestion(item)"
      >
        {{ item.stock_id }} - {{ item.stock_name }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import api from '@/api'

const emit = defineEmits(['select'])

const searchQuery = ref('')
const suggestions = ref([])
const highlightedIndex = ref(-1)

async function fetchSuggestions() {
  if (!searchQuery.value.trim()) {
    suggestions.value = []
    return
  }

  try {
    const res = await api.get('/stocks/search', {
      params: { q: searchQuery.value }
    })
    suggestions.value = res.data
    highlightedIndex.value = -1
  } catch (err) {
    suggestions.value = []
    console.error('❌ 搜尋失敗', err)
  }
}

function selectSuggestion(item) {
  searchQuery.value = `${item.stock_id} - ${item.stock_name}`
  emit('select', item)
  suggestions.value = []
  highlightedIndex.value = -1
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
      if (suggestions.value.length === 1) {
        selectSuggestion(suggestions.value[0])
      }
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
</script>

<style scoped>
.input-wrapper {
  position: relative;
  width: 300px;
}
.input {
  padding: 0.8rem 1.5rem;
  width: 100%;
  font-size: 1rem;
  border-radius: 8px;
  border: none;
  background: #222;
  color: white;
  outline: none;
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
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.suggestions::-webkit-scrollbar {
  display: none;
}
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
