<template>
  <div class="chart">
    <ChartRenderer v-if="data.length" :candles="data" type="index" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import ChartRenderer from './ChartRenderer.vue'

const data = ref([])

onMounted(async () => {
  const res = await api.get('/twii/weekly')
  data.value = res.data
})

</script>
