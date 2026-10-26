import { beforeEach, describe, it, expect } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import router from '@/router'

beforeEach(() => setActivePinia(createPinia()))

const go = async (path) => {
  await router.push(path)
  await router.isReady()
  return router.currentRoute.value
}

describe('주소 구성', () => {
  it('/ 는 LITE 홈이다', async () => {
    const route = await go('/')
    expect(route.fullPath).toBe('/')
    expect(route.name).toBe('LiteHome')
  })

  it('예전 /lite 링크는 /lite를 떼고 같은 화면으로 보낸다', async () => {
    expect((await go('/lite')).name).toBe('LiteHome')
    expect((await go('/lite/m/3/info')).fullPath).toBe('/m/3/info')
  })

  it('복구 링크의 #토큰은 리다이렉트 뒤에도 남는다', async () => {
    const route = await go('/lite/r#tok123')
    expect(route.path).toBe('/r')
    expect(route.hash).toBe('#tok123')
  })

  it('/admin 은 LITE 운영자 화면이다', async () => {
    expect((await go('/admin')).name).toBe('LiteAdmin')
  })

  it('기존 앱 주소는 /legacy 아래로 보낸다', async () => {
    expect((await go('/help')).fullPath).toBe('/legacy/help')
    expect((await go('/pay/abc?x=1')).fullPath).toBe('/legacy/pay/abc?x=1')
    expect((await go('/legacy/help')).name).toBe('Help')
  })

  it('로그인이 필요한 기존 화면은 /legacy/login 으로 보낸다', async () => {
    expect((await go('/dashboard')).fullPath).toBe('/legacy/login')
  })
})
