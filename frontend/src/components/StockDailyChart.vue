<template>
  <ChartRenderer
    v-if="ohlc.length"
    :candles="ohlc"
    type="stock"
    :show-chat="showChat"
    @open-chat="emit('open-chat')"
    class="chart-renderer"
  />
     <div v-if="loading" class="loading-overlay">
  <div class="spinner"></div>
  <span style="margin-left: 0.8rem;">散財中...</span>
</div>
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
    const res = await api.get(`/stocks/${props.stockId}/daily`)
    ohlc.value = res.data
  } catch (err) {
    ohlc.value = []
    console.error('日線資料載入失敗', err)
  } finally {
    loading.value = false
  }
}

watch(() => props.stockId, fetchData, { immediate: true })
</script>
<style scoped>
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 20;
  background-color: rgba(0, 0, 0, 0.5); /* 半透明遮罩 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #facc15;
  pointer-events: none;
  backdrop-filter: blur(1px);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #facc15;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

</style>