<template>
  <div class="chart">
    <ChartRenderer v-if="data.length" :candles="data" type="index" />
    <div v-if="loading" class="loading-overlay">💸 散財中...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import ChartRenderer from './ChartRenderer.vue'

const data = ref([])
const loading = ref(true) // 補上 loading 狀態

onMounted(async () => {
  try {
    const res = await api.get('/twii/daily')
    data.value = res.data
  } catch (err) {
    console.error('取得大盤資料失敗', err)
  } finally {
    loading.value = false // 資料抓完就關掉 loading
  }
})
</script>

<style scoped>
.loading-overlay {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #facc15;
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}
</style>
