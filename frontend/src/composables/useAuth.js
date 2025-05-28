import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const accessToken = ref(localStorage.getItem('access_token') || '')
const username = ref(localStorage.getItem('username') || '')

export function useAuth() {
  const router = useRouter()
  const isLoggedIn = computed(() => !!accessToken.value)

  const login = async (email, password) => {
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!res.ok) throw new Error('登入失敗')

      const data = await res.json()

      accessToken.value = data.access_token
      username.value = data.username

      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('username', data.username)

      alert('登入成功！')
      window.location.reload()
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
    localStorage.removeItem('access_token')
    localStorage.removeItem('username')

    alert('已登出')
    await router.reload()
  }

  return {
    accessToken,
    username,
    isLoggedIn,
    login,
    logout,
  }
}
