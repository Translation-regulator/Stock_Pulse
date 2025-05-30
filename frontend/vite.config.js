import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  base: './', // 讓 HTML 使用相對路徑，適合部署到 S3
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // 本機開發用
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000', // WebSocket 開發代理
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
