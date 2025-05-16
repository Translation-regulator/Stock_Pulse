export function parseFuglePayload(event) {
  try {
    const raw = JSON.parse(event.data)
    const payload = typeof raw.data === 'string' ? JSON.parse(raw.data) : raw.data
    return payload
  } catch (e) {
    console.error('❌ 無法解析 Fugle 資料：', e)
    return null
  }
}
