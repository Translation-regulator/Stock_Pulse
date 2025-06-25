<template>
  <div class="modal-overlay" v-if="show">
    <div class="modal">
      <h3>新增股票</h3>
      <div class="form-group">
        <label>搜尋股票</label>
        <StockSearchInput @select="selectSuggestion" />
      </div>
      <div class="button-group">
        <button @click="$emit('close')">取消</button>
        <button @click="confirmAdd" :disabled="!selected">新增</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StockSearchInput from './StockSearchInput.vue'

const props = defineProps({
  show: Boolean,
})
const emit = defineEmits(['close', 'select'])

const selected = ref(null)

const selectSuggestion = (item) => {
  selected.value = item
}

const confirmAdd = () => {
  if (selected.value) {
    emit('select', selected.value)
    emit('close')
  }
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
  z-index: 999;
}
.modal {
  background: #1e1e1e;
  color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
}
.form-group {
  margin-bottom: 1rem;
}
.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
button {
  background: #555;
  color: white;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>