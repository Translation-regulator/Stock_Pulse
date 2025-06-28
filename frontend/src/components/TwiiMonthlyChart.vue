<template>
  <div class="chart">
    <ChartRenderer
      v-if="data.length"
      :candles="data"
      type="index"
      :show-chat="showChat"
      @open-chat="$emit('open-chat')"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import ChartRenderer from './ChartRenderer.vue'

defineEmits(['open-chat'])

const props = defineProps({
  showChat: { type: Boolean, default: false }
})

const data = ref([])

onMounted(async () => {
  const res = await api.get('/twii/monthly')
  data.value = res.data
})
</script>
