<template>
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
.industry-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin-bottom: 1rem;
}

.industry-btn {
  background: #333;
  color: white;
  border: none;
  width: 200px;             
  height: 40px;             
  font-size: 20px;          
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

