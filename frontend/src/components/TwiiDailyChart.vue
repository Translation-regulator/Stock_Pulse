<template>
  <div class="chart">
    <ChartRenderer
      v-if="data.length"
      :candles="data"
      type="index"
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
import { ref, onMounted } from 'vue'
import api from '@/api'
import ChartRenderer from './ChartRenderer.vue'

defineEmits(['open-chat'])

const props = defineProps({
  showChat: { type: Boolean, default: false } 
})

const data = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/twii/daily')
    data.value = res.data
  } catch (err) {
    console.error('取得大盤資料失敗', err)
  } finally {
    loading.value = false
  }
})
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

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}
</style>
