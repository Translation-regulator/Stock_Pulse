<template>
  <div class="portfolio-page">
    <h2 class="title">我的投資組合</h2>

    <!-- 🔹 統計總覽 -->
    <div class="summary">
      <p>總成本：{{ totalCost }} 元</p>
      <p>總市值：{{ totalValue }} 元</p>
      <p :class="['profit-rate', totalProfitRate >= 0 ? 'up' : 'down']">
        報酬率：{{ totalProfitRate.toFixed(2) }}%
      </p>
    </div>

    <!-- 🔹 投資組合表格 -->
    <table class="portfolio-table">
      <thead>
        <tr>
          <th>股票代碼</th>
          <th>名稱</th>
          <th>股數</th>
          <th>均價</th>
          <th>現價</th>
          <th>報酬率</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="stock in portfolio" :key="stock.id">
          <td>{{ stock.stock_id }}</td>
          <td>{{ stock.name }}</td>
          <td>{{ stock.shares }}</td>
          <td>{{ stock.avg_price }}</td>
          <td>{{ stock.current_price }}</td>
          <td :class="stock.profit_rate >= 0 ? 'up' : 'down'">
            {{ stock.profit_rate.toFixed(2) }}%
          </td>
          <td>
            <button @click="editStock(stock)">編輯</button>
            <button @click="deleteStock(stock.id)">刪除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 新增持股 -->
    <button class="add-btn" @click="showAddModal = true">➕ 新增持股</button>

    <!-- 彈出表單（簡化版） -->
    <div v-if="showAddModal" class="modal">
      <div class="modal-content">
        <h3>新增持股</h3>
        <input v-model="newStock.stock_id" placeholder="股票代碼" />
        <input v-model.number="newStock.shares" placeholder="股數" type="number" />
        <input v-model.number="newStock.avg_price" placeholder="均價" type="number" />
        <button @click="addStock">確認</button>
        <button @click="showAddModal = false">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const portfolio = ref([
  { id: 1, stock_id: '2330.TW', name: '台積電', shares: 10, avg_price: 620, current_price: 630, profit_rate: ((630 - 620) / 620) * 100 },
  { id: 2, stock_id: '2317.TW', name: '鴻海', shares: 20, avg_price: 120, current_price: 117, profit_rate: ((117 - 120) / 120) * 100 },
])

const showAddModal = ref(false)
const newStock = ref({ stock_id: '', shares: 0, avg_price: 0 })

function addStock() {
  portfolio.value.push({
    id: Date.now(),
    stock_id: newStock.value.stock_id,
    name: '（尚未查詢）',
    shares: newStock.value.shares,
    avg_price: newStock.value.avg_price,
    current_price: newStock.value.avg_price, // 模擬現價
    profit_rate: 0,
  })
  showAddModal.value = false
  newStock.value = { stock_id: '', shares: 0, avg_price: 0 }
}

function deleteStock(id) {
  portfolio.value = portfolio.value.filter(s => s.id !== id)
}

function editStock(stock) {
  alert(`尚未實作編輯功能（stock_id: ${stock.stock_id}）`)
}

const totalCost = computed(() =>
  portfolio.value.reduce((sum, s) => sum + s.avg_price * s.shares, 0)
)
const totalValue = computed(() =>
  portfolio.value.reduce((sum, s) => sum + s.current_price * s.shares, 0)
)
const totalProfitRate = computed(() =>
  ((totalValue.value - totalCost.value) / totalCost.value) * 100
)
</script>

<style scoped>
.portfolio-page {
  color: white;
  background-color: #0d1117;
  padding-left: 5%;
  padding-right: 5%;
}

.title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.summary { 
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.portfolio-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.portfolio-table th,
.portfolio-table td {
  padding: 0.5rem 1rem;
  border-bottom: 1px solid #333;
  text-align: center;
}

.up {
  color: #16c784;
}

.down {
  color: #ea3943;
}

.add-btn {
  background-color: #2563eb;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: #1f2937;
  padding: 1rem;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
 