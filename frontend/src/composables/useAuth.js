import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const accessToken = ref(localStorage.getItem('accessToken') || '')
const username = ref(localStorage.getItem('username') || '')

export function useAuth() {
  const router = useRouter()
  const isLoggedIn = computed(() => !!accessToken.value)

  const login = async (email, password) => {
    try {
      const res = await api.post('/auth/login', { email, password })
      const data = res.data

      accessToken.value = data.access_token
      username.value = data.name

      localStorage.setItem('accessToken', data.access_token)
      localStorage.setItem('username', data.name)

      alert('登入成功！')
      await router.push('/')
      return true
    } catch (e) {
      console.error('登入錯誤', e)
      alert('❌ 帳號或密碼錯誤')
      return false
    }
  }

  const logout = async () => {
    accessToken.value = ''
    username.value = ''
    localStorage.removeItem('accessToken')
    localStorage.removeItem('username')

    alert('已登出')
    await router.push('/')
  }

  return {
    accessToken,
    username,
    isLoggedIn,
    login,
    logout,
  }
}
