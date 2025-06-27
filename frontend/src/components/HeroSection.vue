<script setup>
import { useRouter } from 'vue-router'
import StockSearchInput from './StockSearchInput.vue'

const router = useRouter()

const handleSelect = (item) => {
  router.push(`/stock/${item.stock_id}`)
}
</script>

<template>
  <section class="hero">
    <div class="title">StockPulse</div>
    <p class="subtitle">即時行情‧即刻分享</p>
    <div class="input-group">
      <StockSearchInput @select="handleSelect" showSuggestions />
    </div>
  </section>
</template>


<style scoped>
.hero {
  text-align: center;
}
.title {
  font-size: 4rem;
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
  box-sizing: border-box;
  margin: 0;
  color: #ccc;
}

.input-group {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
