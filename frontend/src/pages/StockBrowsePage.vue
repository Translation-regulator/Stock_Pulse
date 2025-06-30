<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import StockSearchInput from '../components/StockSearchInput.vue'
import IndustryFilter from '../components/IndustryFilter.vue'
import StockList from '../components/StockList.vue'

const router = useRouter()
const selectedIndustry = ref('')

function handleStockSelect(stock) {
  router.push(`/stock/${stock.stock_id}`)
}
</script>

<template>
  <div class="stock-page">
    <div class="chart-area">
      <!-- 搜尋輸入框 -->
      <div class="input-group-wrapper">
        <div class="input-absolute-center">
          <StockSearchInput @select="handleStockSelect" class="wide-input" />
        </div>
      </div>

      <!-- 分類選股 -->
      <IndustryFilter @select="selectedIndustry = $event" />
      <StockList :category="selectedIndustry" @select="handleStockSelect" />
    </div>
  </div>
</template>

<style scoped>
.stock-page {
  display: flex;
  height: 100vh;
  background-color: #121212;
  color: white;
  padding-left: 2%;
  padding-right: 2%;
}

.wide-input {
  width: 200px;
}

.chart-area {
  flex: 1;
  overflow: auto;
  box-sizing: border-box;
}

.input-group-wrapper {
  position: relative;
  height: 30px; /* 調整這個高度使容器有空間 */
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}

.back-button-wrapper {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
}

.input-absolute-center {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}


.input-center {
  flex: 1;
  display: flex;
  justify-content: center;
}



</style>

