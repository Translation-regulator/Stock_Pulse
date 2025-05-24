<template>
  <div class="video-wrapper">
    <video autoplay muted loop playsinline class="bg-video">
      <source src="/stock_chart.mp4" type="video/mp4" />
      您的瀏覽器不支援影片播放。
    </video>
  </div>
</template>

<style scoped>
.video-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.bg-video {
  width: 90vw;
  max-height: 45vh;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 20px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
}
</style>
