<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const inputValue = ref('')
const router = useRouter()

const handleSearch = async () => {
  if (!inputValue.value.trim()) return

  try {
    const res = await fetch(`/api/stocks/info/${encodeURIComponent(inputValue.value)}`)
    if (!res.ok) throw new Error()
    const data = await res.json()
    router.push(`/stock/${data.stock_id}`) // ✅ 導向個股頁面
  } catch (e) {
    alert('❌ 查無此股票，請重新輸入')
  }
}
</script>


<template>
  <section class="hero">
    <div class="title">StockPulse</div>
    <p class="subtitle">即時行情‧即刻分享</p>
    <div class="input-group">
    <input
      v-model="inputValue"
      @keyup.enter="handleSearch"
      placeholder="請輸入股號或名稱"
      class="input"
    />
    </div>
  </section>
</template>

<style scoped>
.hero {
  text-align: center;
}
.title {
  font-size: clamp(2rem, 5vw, 4rem);
  font-weight: bold;
  background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet, red);
  background-size: 300% auto;
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  -webkit-text-fill-color: transparent;
  animation: rainbowFlow 4s linear infinite;
  text-align: center;
}

@keyframes rainbowFlow {
  0% {
    background-position: 100% 0%;
  }
  100% {
    background-position: 0% 0%;
  }
}

.subtitle {
  font-size: 2rem;
  margin-top: 0.5rem;
  color: #ccc;
}

.input-group {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.input {
  padding: 0.8rem 1.5rem;
  width: 300px;
  font-size: 1rem;
  border-radius: 8px;
  border: none;
  background: #222;
  color: white;
  outline: none;
}

.search-btn {
  font-size: 1.2rem;
  background: #1f6feb;
  color: white;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.search-btn:hover {
  background: #3b82f6;
}
</style>
