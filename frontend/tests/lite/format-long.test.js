import { describe, it, expect } from 'vitest'
import { koreanTime, longDate } from '@/lite/format'

describe('풀어 쓴 날짜·시각 (서울 기준)', () => {
  it('날짜를 "N월 N일 O요일"로 쓴다', () => {
    expect(longDate('2026-11-08T05:00:00Z')).toBe('11월 8일 일요일')
  })

  it('시각을 오전/오후 12시간제로 쓰고, 정각이면 분을 생략한다', () => {
    expect(koreanTime('2026-11-08T05:00:00Z')).toBe('오후 2시') // 서울 14:00
    expect(koreanTime('2026-11-08T05:30:00Z')).toBe('오후 2시 30분')
    expect(koreanTime('2026-11-08T03:00:00Z')).toBe('오후 12시') // 정오
    expect(koreanTime('2026-11-07T15:00:00Z')).toBe('오전 12시') // 자정
    expect(koreanTime('2026-11-07T22:05:00Z')).toBe('오전 7시 5분')
  })
})
