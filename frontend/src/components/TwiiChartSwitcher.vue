<template>
  <div class="twii-switcher">
    <div class="switch-buttons">
      <button @click="mode = 'daily'" :class="{ active: mode === 'daily' }">日線</button>
      <button @click="mode = 'weekly'" :class="{ active: mode === 'weekly' }">週線</button>
      <button @click="mode = 'monthly'" :class="{ active: mode === 'monthly' }">月線</button>
      <button @click="mode = 'realtime'" :class="{ active: mode === 'realtime' }">即時</button>
    </div>

    <div v-show="mode === 'daily'">
      <TwiiDailyChart />
    </div>
    <div v-show="mode === 'weekly'">
      <TwiiWeeklyChart />
    </div>
    <div v-show="mode === 'monthly'">
      <TwiiMonthlyChart />
    </div>
    <div v-show="mode === 'realtime'">
      <TwiiRealtime />
      <TwiiRealtimeChart />
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
  padding: 20px;
}
.switch-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 1rem;
}
button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  background: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}
</style>
