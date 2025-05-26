<template>
  <div class="twii-switcher">
    <!-- 按鈕與即時指數在同一排 -->
    <div class="switch-bar">
      <div class="switch-buttons">
        <button @click="mode = 'daily'" :class="{ active: mode === 'daily' }">日線</button>
        <button @click="mode = 'weekly'" :class="{ active: mode === 'weekly' }">週線</button>
        <button @click="mode = 'monthly'" :class="{ active: mode === 'monthly' }">月線</button>
      </div>
      <!-- 即時加權指數 -->
      <TwiiRealtime />
    </div>

    <!-- 圖表顯示 -->
    <div v-show="mode === 'daily'">
      <TwiiDailyChart />
    </div>
    <div v-show="mode === 'weekly'">
      <TwiiWeeklyChart />
    </div>
    <div v-show="mode === 'monthly'">
      <TwiiMonthlyChart />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

import TwiiDailyChart from './TwiiDailyChart.vue'
import TwiiWeeklyChart from './TwiiWeeklyChart.vue'
import TwiiMonthlyChart from './TwiiMonthlyChart.vue'
import TwiiRealtimeChart from './TwiiRealtimeChart.vue'
import TwiiRealtime from './TwiiRealtime.vue'

const mode = ref('daily')
</script>

<style scoped>
.twii-switcher {
  box-sizing: border-box;
  margin-left: 10%;
  margin-right: 10%;
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
</style>
