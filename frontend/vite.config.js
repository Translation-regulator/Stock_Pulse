import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' 

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'), 
    },
  },
  server: {
    proxy: {
      // WebSocket 代理
      '/ws': {
        target: 'http://52.198.101.80:8000/',
        ws: true,
        changeOrigin: true,
      },
      // API 路由代理
      '/api': {
        target: 'http://52.198.101.80:8000/',
        changeOrigin: true,
      },
    },
  },
})
