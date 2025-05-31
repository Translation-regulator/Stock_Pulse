<script setup>
import NavBar from './components/NavBar.vue'
import Footer from './components/Footer.vue';
</script>

<template>

    <NavBar />
    <router-view />

</template>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
}


</style>
