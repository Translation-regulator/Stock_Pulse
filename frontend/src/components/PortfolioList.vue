<template>
  <div class="portfolio-box">
    <template v-if="isLoggedIn">
      <!-- 總市值與損益 -->
      <div class="portfolio-header">
        <h2>持有股票市值 <span class="value">{{ totalValue.toLocaleString() }} TWD</span></h2>
        <div class="total-profit" :class="totalProfit >= 0 ? 'loss' : 'gain'">
          {{ totalProfit >= 0 ? '+' : '' }}{{ totalProfit.toLocaleString() }}
        </div>
      </div>

      <!-- 桌機版表格 -->
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
          <tr v-for="(stock, index) in stocks" :key="stock.id">
            <td class="stock-id">
              <span class="code">{{ stock.stock_id }}</span><br />
              <span class="symbol">{{ stock.stock_name }}</span>
            </td>
            <td>
              <span v-if="!stock.realtime_price" style="color: #aaa">尚無報價</span>
              <span v-else>{{ stock.realtime_price }}</span>
            </td>
            <td :class="getChangeClass(stock)">{{ getChangeSymbol(stock) }} {{ getChangeValue(stock) }}</td>
            <td>{{ stock.prev_close }}</td>
            <td :class="getChangeClass(stock)">{{ getChangeSymbol(stock) }} {{ getChangePercent(stock) }}%</td>
            <td>{{ stock.shares.toLocaleString() }}</td>
            <td>{{ stock.buy_price.toLocaleString() }}</td>
            <td>${{ (stock.realtime_price * stock.shares).toLocaleString() }}</td>
            <td :class="getProfitClass(stock)">{{ getProfit(stock) }}</td>
            <td>{{ stock.buy_date }}</td>
            <td>
              <button class="edit-row-button" @click="selectStock(index)">編輯</button>
              <button class="delete-row-button" @click="deleteStock(stock.id, index)">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 手機版卡片樣式 -->
      <div class="stock-card-list mobile-only">
        <div v-for="(stock, index) in stocks" :key="stock.id" class="stock-card">
          <div class="top-row">
            <span class="code">{{ stock.stock_id }}</span>
            <span class="name">{{ stock.stock_name }}</span>
          </div>
          <div class="info-row">
            <div>即時：{{ stock.realtime_price }}</div>
            <div>昨收：{{ stock.prev_close }}</div>
          </div>
          <div class="info-row">
            <div>漲跌：<span :class="getChangeClass(stock)">{{ getChangeSymbol(stock) }} {{ getChangeValue(stock) }}</span></div>
            <div>幅度：<span :class="getChangeClass(stock)">{{ getChangePercent(stock) }}%</span></div>
          </div>
          <div class="info-row">
            <div>持有：{{ stock.shares.toLocaleString() }} 股</div>
            <div>均價：{{ stock.buy_price.toLocaleString() }}</div>
          </div>
          <div class="info-row">
            <div>市值：${{ (stock.realtime_price * stock.shares).toLocaleString() }}</div>
            <div>損益：<span :class="getProfitClass(stock)">{{ getProfit(stock) }}</span></div>
          </div>
          <div class="info-row">
            <div>日期：{{ stock.buy_date }}</div>
          </div>
          <div class="action-row">
            <button class="edit-row-button" @click="selectStock(index)">編輯</button>
            <button class="delete-row-button" @click="deleteStock(stock.id, index)">刪除</button>
          </div>
        </div>
      </div>

      <!-- 新增按鈕與 Modal -->
      <div class="footer-action">
        <button class="add-button" @click="showAddModal = true">新增股票</button>
      </div>
      <AddStockModal :show="showAddModal" @close="showAddModal = false" @select="addStock" />
      <EditStockModal :show="showEditModal" :stock="selectedStock" @close="showEditModal = false" @save="updateStock" />

      <!-- WebSocket 即時更新 -->
      <StockRealtime
        v-for="stockId in uniqueStockIds"
        :key="stockId"
        :stock-id="stockId"
        @update="updateRealtime"
        style="display: none"
      />
    </template>

    <template v-else>
      <div class="login-prompt">
        <h2>尚未登入</h2>
        <p>請先登入以查看您的投資組合</p>
        <button class="login-button" @click="goToLogin">登入</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AddStockModal from './AddStockModal.vue'
import EditStockModal from './EditStockModal.vue'
import StockRealtime from './StockRealtime.vue'
import { useAuth } from '@/composables/useAuth'
import api from '@/api'

const { accessToken, isLoggedIn } = useAuth()
const stocks = ref([])
const showAddModal = ref(false)
const showEditModal = ref(false)
const selectedIndex = ref(null)
const selectedStock = ref(null)

function goToLogin() {
  window.dispatchEvent(new Event('open-login-modal'))
}

async function loadPortfolio() {
  if (!accessToken.value) {
    stocks.value = []
    return
  }
  try {
    const res = await api.get('/portfolio/me')
    stocks.value = res.data.map(s => ({
      ...s,
      realtime_price: 0,
      prev_close: s.current_price
    }))
  } catch (err) {
    console.error('❌ 載入投資組合失敗', err)
    alert('讀取投資組合失敗')
  }
}

onMounted(loadPortfolio)
watch(accessToken, loadPortfolio)

function selectStock(index) {
  selectedIndex.value = index
  selectedStock.value = { ...stocks.value[index] }
  showEditModal.value = true
}

async function updateStock(updatedStock) {
  try {
    await api.put(`/portfolio/${updatedStock.id}`, updatedStock)
    await loadPortfolio()
    showEditModal.value = false
  } catch (err) {
    alert(err?.response?.data?.detail || '更新失敗')
  }
}

async function addStock(item) {
  const newStock = {
    stock_id: item.stock_id,
    stock_name: item.stock_name,
    shares: 0,
    buy_price: 0,
    buy_date: null,
    note: null
  }
  try {
    await api.post('/portfolio', newStock)
    await loadPortfolio()
  } catch (err) {
    alert('新增失敗')
  }
}

async function deleteStock(id, index) {
  if (!confirm('確定要刪除這筆股票嗎？')) return
  try {
    await api.delete(`/portfolio/${id}`)
    stocks.value.splice(index, 1)
  } catch (err) {
    alert('❌ 刪除失敗')
  }
}

function updateRealtime(data) {
  stocks.value
    .filter(s => s.stock_id === data.stock_id)
    .forEach(s => {
      s.realtime_price = data.price
      s.prev_close = data.prev_close ?? s.prev_close
      s.stock_name = data.stock_name ?? s.stock_name
    })
}

const totalValue = computed(() =>
  stocks.value.reduce((sum, s) => sum + s.realtime_price * s.shares, 0)
)
const totalProfit = computed(() =>
  stocks.value.reduce((sum, s) => sum + (s.realtime_price - s.buy_price) * s.shares, 0)
)

const getChangeClass = stock => stock.realtime_price >= stock.prev_close ? 'up' : 'down'
const getChangeSymbol = stock => stock.realtime_price >= stock.prev_close ? '▲' : '▼'
const getChangeValue = stock => Math.abs((stock.realtime_price - stock.prev_close).toFixed(2))
const getChangePercent = stock =>
  stock.prev_close
    ? ((Math.abs(stock.realtime_price - stock.prev_close) / stock.prev_close) * 100).toFixed(2)
    : '0.00'
const getProfit = stock => {
  const diff = (stock.realtime_price - stock.buy_price) * stock.shares
  return (diff >= 0 ? '+' : '') + diff.toLocaleString()
}
const getProfitClass = stock =>
  (stock.realtime_price - stock.buy_price) * stock.shares >= 0 ? 'loss' : 'gain'

const uniqueStockIds = computed(() => [...new Set(stocks.value.map(s => s.stock_id))])
</script>

<style scoped>
  .mobile-only {
    display: none;
  }
.portfolio-box {
  font-family: 'Noto Sans TC', sans-serif;
  background: #1e1e1e;
  color: #eee;
  padding: 20px;
  border-radius: 6px;
  margin: 10px 2%;
  border: 1px solid #333;
}
.portfolio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.value,
.total-profit {
  font-size: 30px;
}
.stock-table {
  width: 100%;
  border-collapse: collapse;
  font-size: clamp(14px, 1.2vw, 20px);
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
  font-size: clamp(14px, 1.2vw, 20px);
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
.edit-row-button,
.delete-row-button {
  padding: 0.2rem 0.6rem;
  font-size: 0.9rem;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
}
.edit-row-button {
  background: #4dabf7;
}
.delete-row-button {
  background: #e74c3c;
  margin-left: 5px;
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
.login-prompt {
  text-align: center;
  padding: 4rem 2rem;
}
.login-button {
  background: #3399ff;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  font-size: 1.1rem;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 1rem;
}
.login-button:hover {
  background: #1a73e8;
}

/* 手機版樣式 */
@media (max-width: 980px) {
  .stock-table {
    display: none;
  }
  .mobile-only {
    display: block;
  }
  .stock-card-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  .stock-card {
    background: #2a2a2a;
    border: 1px solid #444;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.4);
  }

  .stock-table {
    font-size: clamp(14px, 1.2vw, 20px);
  }

  .top-row {
    display: flex;
    justify-content: space-between;
    font-weight: bold;
    color: #4dabf7;
    margin-bottom: 0.5rem;
  }
  .name {
    color: #aaa;
    font-size: 0.9rem;
  }
  .info-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    margin: 0.3rem 0;
  }
  .info-row div {
    flex: 1;
  }
  .action-row {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 0.6rem;
  }
}
</style>
