<template>
  <div class="chart">
    <ChartRenderer
      v-if="data.length"
      :candles="data"
      type="stock"
      :show-chat="showChat"
      @open-chat="$emit('open-chat')"
    />
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <span style="margin-left: 0.8rem;">散財中...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '@/api'
import ChartRenderer from './ChartRenderer.vue'

defineEmits(['open-chat'])

const props = defineProps({
  stockId: String,
  showChat: { type: Boolean, default: false }
})

const data = ref([])
const loading = ref(false)

async function fetchData() {
  if (!props.stockId) return
  loading.value = true
  try {
    const res = await api.get(`/stocks/${props.stockId}/daily`)
    data.value = res.data
  } catch (err) {
    console.error('日線資料載入失敗', err)
    data.value = []
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
  background-color: rgba(0, 0, 0, 0.5);
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

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}
</style>
