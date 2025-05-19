// ✅ src/pages/HomePage.vue
<script setup>
import NavBar from '../components/NavBar.vue'
import HeroSection from '../components/HeroSection.vue'
import HomepageVideo from '../components/HomepageVideo.vue'
import Footer from '../components/Footer.vue'
</script>

<template>
  <div class="home-page">
    <NavBar />

    <div class="content">
      <HeroSection />
      <HomepageVideo />
    </div>

    <Footer/>
  </div>
</template>


<style scoped>
.home-page {
  background-color: #0d1117;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

</style>