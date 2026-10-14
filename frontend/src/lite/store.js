import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { liteApi, readToken, writeToken } from './api'

export const useLiteStore = defineStore('lite', () => {
  const token = ref(readToken())
  const member = ref(null)
  const ready = ref(false)
  const toast = ref(null)
  let toastTimer = null

  const hasToken = computed(() => !!token.value)
  const isHost = computed(() => !!member.value?.is_host)

  const setToken = (value) => {
    token.value = value || null
    writeToken(value)
  }

  const notify = (message, kind = 'ok') => {
    clearTimeout(toastTimer)
    toast.value = { message, kind }
    toastTimer = setTimeout(() => { toast.value = null }, kind === 'error' ? 3500 : 1800)
  }

  // 서버 호출을 감싸 성공/실패 토스트를 띄운다. 실패하면 null을 반환한다.
  const act = async (fn, okMessage) => {
    try {
      const result = await fn()
      if (okMessage) notify(okMessage)
      return result
    } catch (error) {
      notify(error.message, 'error')
      return null
    }
  }

  const init = async () => {
    if (token.value) {
      try {
        const data = await liteApi.me()
        member.value = data.member
      } catch (error) {
        if (error.status === 401) {
          setToken(null)
          member.value = null
        } else {
          notify(error.message, 'error')
        }
      }
    }
    ready.value = true
  }

  const register = async (name) => {
    const data = await act(() => liteApi.createMember(name))
    if (!data) return false
    setToken(data.token)
    member.value = data.member
    notify(`${data.member.name}님, 반가워요`)
    return true
  }

  const claimHost = async (key) => {
    const data = await act(() => liteApi.claimHost(key), '운영자로 설정했어요')
    if (!data) return false
    member.value = data.member
    return true
  }

  // 새 토큰으로 me/가 성공한 뒤에만 저장한다. 실패하면 기존 토큰과 회원 정보를 유지한다.
  const recover = async (newToken) => {
    const data = await act(() => liteApi.me(newToken))
    if (!data) return false
    setToken(newToken)
    member.value = data.member
    return true
  }

  const logout = () => {
    setToken(null)
    member.value = null
  }

  return { token, member, ready, toast, hasToken, isHost, setToken, notify, act, init, register, claimHost, recover, logout }
})
