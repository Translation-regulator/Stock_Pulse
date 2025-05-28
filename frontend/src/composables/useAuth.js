import { ref, computed } from 'vue'

const accessToken = ref(localStorage.getItem('access_token') || '')
const username = ref(localStorage.getItem('username') || '')

export function useAuth() {
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

      // 永久保存
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('username', data.username)

      return true
    } catch (e) {
      console.error(e)
      return false
    }
  }

  const logout = () => {
    accessToken.value = ''
    username.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('username')
  }

  return {
    accessToken,
    username,
    isLoggedIn,
    login,
    logout,
  }
}
