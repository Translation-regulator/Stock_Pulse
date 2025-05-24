<script setup>
import HeroSection from '../components/HeroSection.vue'
import HomepageVideo from '../components/HomepageVideo.vue'
import Footer from '../components/Footer.vue'
</script>

<template>
  <div class="home-page">
    <div class="content">
      <HeroSection />
      <HomepageVideo />
    </div>
    <Footer />
  </div>
</template>

<style scoped>
.home-page {
  flex: 1; 
  display: flex;
  flex-direction: column;
  background-color: #0d1117;
  overflow: hidden;
}

.content {
  flex: 1; 
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>

