import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000',
})

// ✅ 每次請求都自動加上 Authorization 標頭
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ✅ 若遇到 401，代表 token 過期 → 清除登入資訊並導回首頁
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('username')
      window.location.href = '/'  // 可改 router.push('/')，要看你在哪個環境執行
    }
    return Promise.reject(error)
  }
)

export default api
