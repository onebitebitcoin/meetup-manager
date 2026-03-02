export const LIGHTNING_PROVIDER_DOMAINS = {
  walletofsatoshi: 'walletofsatoshi.com',
  coinos: 'coinos.io',
  strike: 'strike.me',
}

export const LIGHTNING_PROVIDER_OPTIONS = [
  { value: 'walletofsatoshi', label: '@walletofsatoshi' },
  { value: 'coinos', label: '@coinos' },
  { value: 'strike', label: '@strike.me' },
  { value: 'custom', label: '직접 입력' },
]

export function buildLightningAddress(form) {
  if (!form) return ''

  const provider = form.provider || 'walletofsatoshi'

  if (provider === 'custom') {
    return (form.customAddress || '').trim()
  }

  const handle = (form.handle || '').trim()
  const domain = LIGHTNING_PROVIDER_DOMAINS[provider]
  if (!handle || !domain) {
    return ''
  }

  return `${handle}@${domain}`
}

export function parseLightningAddress(address) {
  const normalized = (address || '').trim()
  if (!normalized || !normalized.includes('@')) {
    return {
      provider: 'walletofsatoshi',
      handle: '',
      customAddress: normalized,
    }
  }

  const [handle, domainRaw] = normalized.split('@', 2)
  const domain = (domainRaw || '').toLowerCase()

  const matchedProvider = Object.entries(LIGHTNING_PROVIDER_DOMAINS).find(([, value]) => value === domain)
  if (matchedProvider) {
    return {
      provider: matchedProvider[0],
      handle,
      customAddress: '',
    }
  }

  return {
    provider: 'custom',
    handle: '',
    customAddress: normalized,
  }
}

export function buildLightningQrImageUrl(value) {
  const normalized = (value || '').trim()
  if (!normalized) {
    return ''
  }

  return `https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=${encodeURIComponent(normalized)}`
}
