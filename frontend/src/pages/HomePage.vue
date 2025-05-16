<script setup>
import NavBar from '../components/NavBar.vue';
import TwiiRealtime from '../components/TwiiRealtime.vue'
import TwiChart from '../components/TwiiChart.vue'
</script>

<template>
  <NavBar/>
  <main>
    <TwiChart/>
  </main>
</template>

<style scoped>
  main {
    padding-top: 70px;
  }
</style>


