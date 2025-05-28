<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal">
      <h3>編輯持股</h3>

      <div class="form-group">
        <label>股票代號或名稱</label>
        <input
          v-model="searchQuery"
          @input="onSearch"
          placeholder="輸入股票代號或名稱"
        />
        <ul v-if="suggestions.length" class="suggestions">
          <li v-for="item in suggestions" :key="item.stock_id" @click="selectSuggestion(item)">
            {{ item.stock_id }} - {{ item.stock_name }}
          </li>
        </ul>
      </div>

      <div class="form-group">
        <label>持有股數</label>
        <input type="number" v-model.number="editedStock.shares" />
      </div>

      <div class="form-group">
        <label>持有價格</label>
        <input type="number" v-model.number="editedStock.avg_price" />
      </div>

      <div class="form-group">
        <label>購買時間</label>
        <input type="date" v-model="editedStock.buy_date" />
      </div>

      <div class="actions">
        <button @click="$emit('close')">取消</button>
        <button @click="save">儲存</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  show: Boolean,
  stock: Object,
})
const emits = defineEmits(['close', 'save'])

const editedStock = ref({ ...props.stock })
const searchQuery = ref('')
const suggestions = ref([])

watch(() => props.stock, (newVal) => {
  editedStock.value = { ...newVal }
  searchQuery.value = newVal.stock_id || ''
})

const onSearch = async () => {
  if (searchQuery.value.length < 4) return
  const q = searchQuery.value.trim()
  try {
    const res = await axios.get(`/api/stocks/search?q=${q}`)
    suggestions.value = res.data
  } catch (err) {
    suggestions.value = []
  }
}

const selectSuggestion = (item) => {
  editedStock.value.stock_id = item.stock_id
  editedStock.value.symbol = item.stock_name
  searchQuery.value = `${item.stock_id} - ${item.stock_name}`
  suggestions.value = []
}

const save = () => {
  emits('save', { ...editedStock.value })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal {
  background: #222;
  color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}
.form-group {
  margin-bottom: 1rem;
}
input {
  width: 100%;
  padding: 0.5rem;
  background: #333;
  color: #fff;
  border: 1px solid #555;
  border-radius: 4px;
}
.suggestions {
  background: #444;
  list-style: none;
  margin-top: 4px;
  padding: 0;
  border-radius: 4px;
  max-height: 150px;
  overflow-y: auto;
  z-index: 10;
}
.suggestions li {
  padding: 0.5rem;
  cursor: pointer;
}
.suggestions li:hover {
  background: #666;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
button {
  padding: 0.5rem 1rem;
  background: #4dabf7;
  border: none;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background: #3399ff;
}
</style>
