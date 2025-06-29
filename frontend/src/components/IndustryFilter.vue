<template>
  <div class="industry-wrapper">
    <!-- 桌機版 -->
    <div class="industry-buttons desktop-only">
      <button
        v-for="industry in industries"
        :key="industry"
        @click="$emit('select', industry)"
        class="industry-btn"
      >
        {{ industry }}
      </button>
    </div>

    <!-- 手機版下拉選單 -->
    <div class="mobile-only">
      <select @change="$emit('select', $event.target.value)">
        <option disabled selected>請選擇產業</option>
        <option
          v-for="industry in industries"
          :key="industry"
          :value="industry"
        >
          {{ industry }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const industries = ref([])

onMounted(async () => {
  const res = await api.get('/stocks/industries')
  industries.value = res.data.filter(i => i && i.trim() !== '')
})
</script>

<style scoped>
.industry-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
}

.industry-buttons {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  max-width: 900px;
}

.industry-btn {
  background: #333;
  color: white;
  border: none;
  width: 150px;
  height: 30px;
  font-size: 16px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
}

.industry-btn:hover {
  background: #555;
}

.mobile-only {
  display: none;
}

.desktop-only {
  display: grid;
}

/* 手機 RWD 切換 */
@media (max-width: 768px) {
  .desktop-only {
    display: none;
  }

  .mobile-only {
    display: block;
    width: 100%;
    text-align: center;
    margin-top: 1rem;
  }

select {
  width: 80%;
  padding: 8px;
  font-size: 16px;
  border-radius: 6px;
  background: #222;
  color: white;
  border: 1px solid #444;
}

select:focus {
  outline: none;
  border-color: #888;
}

option {
  background-color: #222;
  color: white;
}

/* Chrome / Safari / Edge */
.chart-area::-webkit-scrollbar {
  width: 8px;
}

.chart-area::-webkit-scrollbar-track {
  background: #1e1e1e; /* 軌道背景：深色 */
}

.chart-area::-webkit-scrollbar-thumb {
  background-color: #444;  /* 滾動條顏色 */
  border-radius: 4px;       /* 圓角 */
}

.chart-area::-webkit-scrollbar-thumb:hover {
  background-color: #666;
}

/* Firefox 支援 */
.chart-area {
  scrollbar-width: thin;                /* 滾輪寬度 */
  scrollbar-color: #444 #1e1e1e;        /* thumb, track */
}


}
</style>
