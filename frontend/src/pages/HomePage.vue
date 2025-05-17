<script setup>
import NavBar from '../components/NavBar.vue'
import TwiiChartSwitcher from '../components/TwiiChartSwitcher.vue'
</script>

<template>
  <NavBar />
  <main>
    <TwiiChartSwitcher />
  </main>
</template>

<style scoped>
main {
  padding-top: 70px;
  width: 1200px;
  margin: 0 auto;
}
</style>
