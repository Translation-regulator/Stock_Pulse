<template>
  <div class="chart">
    <ChartRenderer v-if="data.length" :candles="data" />
    <p v-else>📉 載入中...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ChartRenderer from './ChartRenderer.vue'

const data = ref([])     

onMounted(async () => {
  const res = await axios.get('http://localhost:8000/api/twii/daily')
  data.value = res.data
})
</script>

