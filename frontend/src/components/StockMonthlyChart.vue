<template>
  <ChartRenderer
    v-if="ohlc.length"
    :candles="ohlc"
    type="stock"
    :show-chat="showChat"
    @open-chat="emit('open-chat')"
    class="chart-renderer"
  />
  <div v-if="loading" class="loading-overlay">📅 載入月線資料中...</div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import ChartRenderer from './ChartRenderer.vue'
import api from '@/api'

const props = defineProps({
  stockId: String,
  showChat: Boolean,
})

const emit = defineEmits(['open-chat'])

const ohlc = ref([])
const loading = ref(false)

async function fetchData() {
  if (!props.stockId) return
  loading.value = true
  try {
    const res = await api.get(`/stocks/${props.stockId}/monthly`)
    ohlc.value = res.data
  } catch (err) {
    ohlc.value = []
    console.error('月線資料載入失敗', err)
  } finally {
    loading.value = false
  }
}

watch(() => props.stockId, fetchData, { immediate: true })
</script>
