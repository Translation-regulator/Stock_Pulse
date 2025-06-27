<script setup>
import HeroSection from '../components/HeroSection.vue'
import HomepageVideo from '../components/HomepageVideo.vue'
import Footer from '../components/Footer.vue'
</script>

<template>
  <div class="home-page">
    <div class="bg-container">
    <div class="content">
      <HeroSection />
      <!--<HomepageVideo />-->
    </div>
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
  box-sizing: border-box;
  margin-top: 20px;

}

.bg-container {
  background-image: url('@/assets/homepagebackground.png');
  background-size: cover;         /* 拉滿容器 */
  background-position: center;    /* 置中 */
  background-repeat: no-repeat;   /* 不重複 */
  width: 100vw;
  height: 100vh;
}

@media (max-width: 768px) {
  .bg-container {
    background-size: contain;
    background-color: #000; /* 補上背景色避免空白太突兀 */
  }
}
</style>

