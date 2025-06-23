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
      localStorage.setItem('userId', data.user_id)

      await router.push('/')
      return { success: true, name: data.name }
    } catch (e) {
      console.error('登入錯誤', e)
      return { success: false, message: '❌ 帳號或密碼錯誤' }
    }
  }

  const logout = async () => {
    accessToken.value = ''
    username.value = ''
    localStorage.removeItem('accessToken')
    localStorage.removeItem('username')
    localStorage.removeItem('userId')

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
