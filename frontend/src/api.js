import axios from 'axios'

// ✅ API base 來自環境變數（開發預設為 localhost）
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// ✅ 自動附加 JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ✅ 遇到 401 → 清除登入資訊並導向首頁
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('username')

      // 若你在 Vue 中，也可改為 router.push('/')
      window.location.href = '/'
    }
    return Promise.reject(err)
  }
)

export default api
