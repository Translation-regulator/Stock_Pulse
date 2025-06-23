<template>
  <div v-if="visible" :class="['toast', type]">
    {{ message }}
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  message: String,
  type: {
    type: String,
    default: 'info' // success, error, info
  }
})

const visible = ref(false)

watch(() => props.message, () => {
  if (props.message) {
    visible.value = true
    setTimeout(() => (visible.value = false), 2500)
  }
})
</script>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  font-size: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
  z-index: 9999;
}

.toast.success {
  background: #d1fae5;
  color: #065f46;
}

.toast.error {
  background: #fee2e2;
  color: #991b1b;
}

.toast.info {
  background: #dbeafe;
  color: #1e40af;
}
</style>
