<template>
  <div class="chart">
    <ChartRenderer v-if="data.length" :candles="data" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ChartRenderer from './ChartRenderer.vue'

const data = ref([])

onMounted(async () => {
  const res = await axios.get('http://localhost:8000/api/twii/weekly')
  data.value = res.data
})
</script>
