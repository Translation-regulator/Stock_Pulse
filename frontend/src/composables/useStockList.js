// useStockList.js
import api from '@/api'

export async function useStockList() {
  try {
    const res = await api.get('/stocks/all')
    console.log('[useStockList] API 回傳結果:', res.data)
    return { stockList: res.data }
  } catch (e) {
    console.error('載入股號失敗', e)
    return { stockList: [] }
  }
}

