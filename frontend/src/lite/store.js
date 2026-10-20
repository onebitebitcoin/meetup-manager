import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { liteApi, readToken, writeToken } from './api'
import { randomNickname } from './nickname'

const NICKNAME_ATTEMPTS = 4

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

  // 이름을 묻지 않고 자동 닉네임으로 가입시킨다. 닉네임이 겹치면(409) 다시 뽑고, 마지막엔 숫자를 붙인다.
  let joining = null
  const ensureMember = () => {
    if (member.value) return Promise.resolve(true)
    joining ??= (async () => {
      for (let attempt = 0; attempt < NICKNAME_ATTEMPTS; attempt += 1) {
        const name = randomNickname({ suffix: attempt === NICKNAME_ATTEMPTS - 1 })
        try {
          const data = await liteApi.createMember(name)
          setToken(data.token)
          member.value = data.member
          notify(`${data.member.name}님, 반가워요`)
          return true
        } catch (error) {
          if (error.status === 409 && attempt < NICKNAME_ATTEMPTS - 1) continue
          notify(error.message, 'error')
          return false
        }
      }
      return false
    })().finally(() => { joining = null })
    return joining
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

  return { token, member, ready, toast, hasToken, isHost, setToken, notify, act, init, ensureMember, claimHost, recover, logout }
})
