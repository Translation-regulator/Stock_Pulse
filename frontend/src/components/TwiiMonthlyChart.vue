<template>
  <div class="chart">
    <ChartRenderer v-if="data.length" :candles="data" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import ChartRenderer from './ChartRenderer.vue'

const data = ref([])

onMounted(async () => {
  const res = await api.get('/twii/monthly')
  data.value = res.data
})
</script>
