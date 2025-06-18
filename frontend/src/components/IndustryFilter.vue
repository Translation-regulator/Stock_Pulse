<template>
  <div class="industry-wrapper">
    <div class="industry-buttons">
      <button
        v-for="industry in industries"
        :key="industry"
        @click="$emit('select', industry)"
        class="industry-btn"
      >
        {{ industry }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const industries = ref([])

onMounted(async () => {
  const res = await api.get('/stocks/industries')
  industries.value = res.data.filter(i => i && i.trim() !== '')
})
</script>

<style scoped>
.industry-wrapper {
  display: flex;
  justify-content: center;  /* 讓整塊按鈕區塊置中 */
  width: 100%;
}

.industry-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 每列 4 個 */
  gap: 10px;
  max-width: 900px;  
}

.industry-btn {
  background: #333;
  color: white;
  border: none;
  width: 200px;
  height: 40px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
}

.industry-btn:hover {
  background: #555;
}
</style>
