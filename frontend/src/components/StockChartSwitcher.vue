<template>
  <div class="stock-switcher">
    <!-- 桌機版 -->
    <div class="desktop-row desktop-only">
      <div class="left-block">
        <div class="stock-id-name">{{ stockName }}（{{ stockId }}）</div>
        <div class="switch-buttons">
          <button @click="mode = 'daily'" :class="{ active: mode === 'daily' }">日線</button>
          <button @click="mode = 'weekly'" :class="{ active: mode === 'weekly' }">週線</button>
          <button @click="mode = 'monthly'" :class="{ active: mode === 'monthly' }">月線</button>
        </div>
      </div>
      <div class="stock-realtime">
        <StockRealtime :stockId="stockId" />
      </div>
    </div>


    <!-- 手機版 -->
    <div class="mobile-row mobile-only">
      <div class="mobile-left">
        <select v-model="mode">
          <option value="daily">日線</option>
          <option value="weekly">週線</option>
          <option value="monthly">月線</option>
        </select>
      </div>
      <div class="mobile-right">
        <span class="stock-id-name-mobile"></span>
        <StockRealtime :stockId="stockId" :stockName="stockName" />
      </div>
    </div>

    <!-- 顯示對應圖表 -->
    <div v-show="mode === 'daily'">
      <StockDailyChart :stock-id="stockId" :show-chat="showChat" @open-chat="emit('open-chat')" />
    </div>
    <div v-show="mode === 'weekly'">
      <StockWeeklyChart :stock-id="stockId" :show-chat="showChat" @open-chat="emit('open-chat')" />
    </div>
    <div v-show="mode === 'monthly'">
      <StockMonthlyChart :stock-id="stockId" :show-chat="showChat" @open-chat="emit('open-chat')" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StockRealtime from './StockRealtime.vue'
import StockDailyChart from './StockDailyChart.vue'
import StockWeeklyChart from './StockWeeklyChart.vue'
import StockMonthlyChart from './StockMonthlyChart.vue'

const emit = defineEmits(['open-chat'])

const props = defineProps({
  stockId: String,
  stockName: String,
  showChat: Boolean,
})

const mode = ref('daily')
</script>

<style scoped>
.stock-switcher {
  box-sizing: border-box;
  padding: 0.5rem;
  background-color: #0d1117;
  overflow: hidden;
}

/* 桌機版列排法 */
.desktop-row {
  display: flex;
  justify-content: space-between; /* 左右分開 */
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.left-block {
  display: flex;
  align-items: center;
  gap: 1rem; /* 控制 stock name 和按鈕間距 */
}

.switch-buttons {
  display: flex;
  gap: 10px;
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

.stock-id-name {
  color: #e6edf3;
  font-size: 1.5rem;
  margin-right: 1rem;
}

.stock-realtime {
  white-space: nowrap;
  background-color: #2a2e36;
  padding: 0.3rem 0.8rem;
  border-radius: 6px;
  color: white;
  font-size: 0.95rem;
}

/* 手機樣式 */
.mobile-only {
  display: none;
}

/* 手機樣式微調 */
@media (max-width: 756px) {
  .desktop-only {
    display: none;
  }

  .mobile-only {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
    gap: 0.5rem;
  }

  .mobile-left select {
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

  .mobile-right {
    display: flex;
    flex-direction: row; 
    align-items: center;
    background-color: #2a2e36;
    border-radius: 6px;
    color: white;
    white-space: nowrap;
    box-sizing: border-box;
    text-align: center;
  }

  .stock-id-name-mobile {
    color: #e6edf3;
  }

}



</style>
