import { describe, expect, it } from 'vitest'

import { buildLightningAddress, buildLightningQrImageUrl, parseLightningAddress } from '@/utils/lightning'

describe('lightning utils', () => {
  it('선택형 provider로 lightning address를 조합한다', () => {
    const address = buildLightningAddress({
      provider: 'coinos',
      handle: 'alice',
      customAddress: '',
    })

    expect(address).toBe('alice@coinos.io')
  })

  it('custom provider는 입력값을 그대로 사용한다', () => {
    const address = buildLightningAddress({
      provider: 'custom',
      handle: '',
      customAddress: 'bob@custom.example',
    })

    expect(address).toBe('bob@custom.example')
  })

  it('저장된 주소를 provider 폼 데이터로 파싱한다', () => {
    const parsed = parseLightningAddress('satoshi@strike.me')

    expect(parsed.provider).toBe('strike')
    expect(parsed.handle).toBe('satoshi')
    expect(parsed.customAddress).toBe('')
  })

  it('알 수 없는 도메인은 custom으로 파싱한다', () => {
    const parsed = parseLightningAddress('maker@ln.example.com')

    expect(parsed.provider).toBe('custom')
    expect(parsed.customAddress).toBe('maker@ln.example.com')
  })

  it('QR 코드 URL을 생성한다', () => {
    const url = buildLightningQrImageUrl('lnbc10n1ptest')

    expect(url).toContain('api.qrserver.com')
    expect(url).toContain(encodeURIComponent('lnbc10n1ptest'))
  })
})
