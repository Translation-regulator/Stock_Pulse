<template>
  <div class="twii-switcher">
    <div class="switch-bar">
      <!-- 桌機按鈕 -->
      <div class="switch-buttons desktop-only">
        <button @click="mode = 'daily'" :class="{ active: mode === 'daily' }">日線</button>
        <button @click="mode = 'weekly'" :class="{ active: mode === 'weekly' }">週線</button>
        <button @click="mode = 'monthly'" :class="{ active: mode === 'monthly' }">月線</button>
      </div>

      <!-- 手機下拉選單 -->
      <div class="mobile-only">
        <select v-model="mode">
          <option
            v-for="option in availableModes"
            :key="option.value"
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>

      <!-- 即時加權指數 -->
      <TwiiRealtime />
    </div>

    <!-- 圖表顯示 -->
    <div v-show="mode === 'daily'">
      <TwiiDailyChart :show-chat="showChat" @open-chat="emit('open-chat')" />
    </div>
    <div v-show="mode === 'weekly'">
      <TwiiWeeklyChart :show-chat="showChat" @open-chat="emit('open-chat')" />
    </div>
    <div v-show="mode === 'monthly'">
      <TwiiMonthlyChart :show-chat="showChat" @open-chat="emit('open-chat')" />
    </div>
  </div>
</template>


<script setup>
import { ref } from 'vue'
import TwiiDailyChart from './TwiiDailyChart.vue'
import TwiiWeeklyChart from './TwiiWeeklyChart.vue'
import TwiiMonthlyChart from './TwiiMonthlyChart.vue'
import TwiiRealtime from './TwiiRealtime.vue'

const emit = defineEmits(['open-chat'])
const props = defineProps({
  showChat: { type: Boolean, default: false }
})

const mode = ref('daily')

const availableModes = [
  { value: 'daily', label: '日線' },
  { value: 'weekly', label: '週線' },
  { value: 'monthly', label: '月線' }
]
</script>

<style scoped>
.twii-switcher {
  box-sizing: border-box;
}

/* 上方按鈕與即時股價一排 */
.switch-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.switch-buttons {
  display: flex;
  gap: 10px;
}

button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  background: #1f2937;
  color: white;
  border: 1px solid #444;
  border-radius: 6px;
}
button.active {
  background-color: #6366f1;
  border-color: #6366f1;
}

.desktop-only {
  display: flex;
}

.mobile-only {
  display: none;
}

@media (max-width: 756px) {
  .desktop-only {
    display: none;
  }

  .mobile-only {
    display: block;
  }

.mobile-only select {
  appearance: none;        
  -webkit-appearance: none; 
  -moz-appearance: none;    
  background: #1f2937;     
  color: white;
  border: 1px solid #444;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  width: 100%;
  background-image: none;
}


  .mobile-only option {
    background-color: #1f2937;
    color: white;
  }
}

</style>