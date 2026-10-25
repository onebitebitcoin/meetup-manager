import { describe, it, expect } from 'vitest'
import { splitLinks, firstLink } from '@/lite/linkify'

describe('splitLinks', () => {
  it('링크가 없으면 텍스트 조각 하나만 돌려준다', () => {
    expect(splitLinks('안녕하세요')).toEqual([{ type: 'text', text: '안녕하세요' }])
  })

  it('본문 중간의 링크를 앞뒤 텍스트와 분리한다', () => {
    expect(splitLinks('보세요 https://a.com/x 감사')).toEqual([
      { type: 'text', text: '보세요 ' },
      { type: 'link', text: 'https://a.com/x', href: 'https://a.com/x' },
      { type: 'text', text: ' 감사' },
    ])
  })

  it('끝의 문장부호는 링크에서 뺀다', () => {
    expect(splitLinks('(http://a.com/p).')).toEqual([
      { type: 'text', text: '(' },
      { type: 'link', text: 'http://a.com/p', href: 'http://a.com/p' },
      { type: 'text', text: ').' },
    ])
    expect(splitLinks('https://a.com?!')[0]).toMatchObject({ type: 'link', href: 'https://a.com' })
  })

  it('www로 시작하면 href에 https를 붙이고 표시 텍스트는 그대로 둔다', () => {
    expect(splitLinks('www.a.com')).toEqual([{ type: 'link', text: 'www.a.com', href: 'https://www.a.com' }])
  })

  it('링크가 여러 개여도 모두 나눈다', () => {
    const links = splitLinks('https://a.com 와 https://b.com').filter((p) => p.type === 'link')
    expect(links.map((p) => p.href)).toEqual(['https://a.com', 'https://b.com'])
  })

  it('빈 문자열은 빈 배열이다', () => {
    expect(splitLinks('')).toEqual([])
  })
})

describe('firstLink', () => {
  it('첫 링크의 href를 돌려주고 없으면 null이다', () => {
    expect(firstLink('x https://a.com y https://b.com')).toBe('https://a.com')
    expect(firstLink('링크 없음')).toBeNull()
    expect(firstLink('')).toBeNull()
  })
})
