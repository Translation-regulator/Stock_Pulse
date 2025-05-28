<template>
  <div class="portfolio-box">
    <div class="portfolio-header">
      <h2>持有股票市值 <span class="value">{{ totalValue.toLocaleString() }} TWD</span></h2>
      <div class="total-profit" :class="totalProfit >= 0 ? 'loss' : 'gain'">
        {{ totalProfit >= 0 ? '+' : '' }}{{ totalProfit.toLocaleString() }}
      </div>
    </div>

    <table class="stock-table">
      <thead>
        <tr>
          <th>股票</th>
          <th>即時股價</th>
          <th>漲跌</th>
          <th>昨收</th>
          <th>漲跌幅(%)</th>
          <th>持有股數</th>
          <th>持有價格</th>
          <th>個股市值</th>
          <th>損益</th>
          <th>購買時間</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(stock, index) in stocks" :key="index">
          <td class="stock-id">
            <span class="code">{{ stock.stock_id }}</span><br />
            <span class="symbol">{{ stock.symbol }}</span>
          </td>
          <td>
            <span v-if="!stock.realtime_price" style="color: #aaa">尚無報價</span>
            <span v-else>{{ stock.realtime_price }}</span>
            <StockRealtime :stock-id="stock.stock_id" @update="(data) => updateRealtime(data, index)" style="display: none" />
          </td>
          <td :class="getChangeClass(stock)">{{ getChangeSymbol(stock) }} {{ getChangeValue(stock) }}</td>
          <td>{{ stock.prev_close }}</td>
          <td :class="getChangeClass(stock)">{{ getChangeSymbol(stock) }} {{ getChangePercent(stock) }}%</td>
          <td>{{ stock.shares }}</td>
          <td>{{ stock.avg_price }}</td>
          <td>${{ (stock.realtime_price * stock.shares).toLocaleString() }}</td>
          <td :class="getProfitClass(stock)">{{ getProfit(stock) }}</td>
          <td>{{ stock.buy_date }}</td>
          <td>
            <button class="edit-row-button" @click="selectStock(index)">編輯</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="footer-action">
      <button class="add-button" @click="showAddModal = true">新增股票</button>
    </div>

    <AddStockModal :show="showAddModal" @close="showAddModal = false" @select="addStock" />
    <EditStockModal :show="showEditModal" :stock="selectedStock" @close="showEditModal = false" @save="updateStock" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AddStockModal from './AddStockModal.vue'
import EditStockModal from './EditStockModal.vue'
import StockRealtime from './StockRealtime.vue'

const showAddModal = ref(false)
const showEditModal = ref(false)
const selectedIndex = ref(null)
const selectedStock = ref(null)

const stocks = ref([])

function selectStock(index) {
  selectedIndex.value = index
  selectedStock.value = { ...stocks.value[index] }
  showEditModal.value = true
}

function updateStock(updatedStock) {
  if (selectedIndex.value !== null) {
    stocks.value[selectedIndex.value] = { ...updatedStock }
  }
  showEditModal.value = false
}

function addStock(item) {
  stocks.value.push({
    stock_id: item.stock_id,
    symbol: item.stock_name,
    shares: 0,
    avg_price: 0,
    buy_date: '',
    realtime_price: 0,
    prev_close: 0,
  })
}

function updateRealtime(data, index) {
  const stock = stocks.value[index]
  if (stock) {
    stock.realtime_price = data.price
    stock.prev_close = data.prev_close ?? stock.prev_close
  }
}

const totalValue = computed(() =>
  stocks.value.reduce((sum, s) => sum + s.realtime_price * s.shares, 0)
)
const totalProfit = computed(() =>
  stocks.value.reduce((sum, s) => sum + (s.realtime_price - s.avg_price) * s.shares, 0)
)

function getChangeClass(stock) {
  return stock.realtime_price >= stock.prev_close ? 'up' : 'down'
}
function getChangeSymbol(stock) {
  return stock.realtime_price >= stock.prev_close ? '▲' : '▼'
}
function getChangeValue(stock) {
  return Math.abs((stock.realtime_price - stock.prev_close).toFixed(2))
}
function getChangePercent(stock) {
  if (!stock.prev_close || stock.prev_close === 0) return '0.00'
  return (
    ((Math.abs(stock.realtime_price - stock.prev_close) / stock.prev_close) * 100).toFixed(2)
  )
}
function getProfit(stock) {
  const diff = (stock.realtime_price - stock.avg_price) * stock.shares
  const prefix = diff >= 0 ? '+' : ''
  return prefix + diff.toLocaleString()
}

function getProfitClass(stock) {
  const diff = (stock.realtime_price - stock.avg_price) * stock.shares
  return diff >= 0 ? 'loss' : 'gain'
}
</script>

<style scoped>
.portfolio-box {
  font-family: Arial, sans-serif;
  background: #1e1e1e;
  color: #eee;
  padding: 20px;
  border-radius: 6px;
  margin: 30px 10%;
  border: 1px solid #333;
}
.portfolio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.total-profit {
  font-size: 30px;
}
.value {
  font-size: 30px;
  margin-left: 0.5rem;
}
.profit {
  font-size: 30px;
}
.footer-action {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}
.add-button {
  background: #444;
  color: white;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.7;
}
.add-button:hover {
  background: #3399ff;
  opacity: 1;
}
.edit-row-button {
  padding: 0.2rem 0.6rem;
  font-size: 0.9rem;
  background: #4dabf7;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
}
.stock-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 16px;
  background-color: #2a2a2a;
}
.stock-table th,
.stock-table td {
  padding: 0.6rem;
  border-bottom: 1px solid #444;
  text-align: center;
}
.code {
  font-weight: bold;
  color: #4dabf7;
}
.symbol {
  font-size: 12px;
  color: #888;
}
.up {
  color: #ef5350;
}
.down {
  color: #00e676;
}
.gain {
  color: #00e676;

}
.loss {
  color: #ef5350;
}
</style>
