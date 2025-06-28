<template>
  <div class="chart">
    <ChartRenderer
      v-if="data.length"
      :candles="data"
      type="index"
      @open-chat="$emit('open-chat')" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import ChartRenderer from './ChartRenderer.vue'

defineEmits(['open-chat'])  // 宣告 open-chat 事件

const data = ref([])

onMounted(async () => {
  const res = await api.get('/twii/monthly')
  data.value = res.data
})
</script>

