<template>
  <div class="chat-lobby">
    <h1>聊天室大廳</h1>
    <p>請選擇一個聊天室進入：</p>
    <ul>
      <li v-for="stock in stockList" :key="stock">
        <RouterLink :to="`/chat/${stock}`">進入 {{ stock }} 聊天室</RouterLink>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const stockList = ref(['2330', '2317', '2454', '0050'])  // 模擬熱門聊天室
</script>

<style scoped>
.chat-lobby {
  padding: 2rem;
  color: white;
}
a {
  color: #3b82f6;
}
</style>
