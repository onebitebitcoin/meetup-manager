import { describe, it, expect } from 'vitest'
import { layoutMessages } from '@/lite/format'

const user = (id, memberId, at) => ({ id, kind: 'user', member: { id: memberId, name: `회원${memberId}` }, body: 'hi', created_at: at })

describe('layoutMessages', () => {
  it('같은 사람이 같은 분에 보낸 메시지는 묶고 시각은 마지막에만 붙인다', () => {
    const rows = layoutMessages([
      user(1, 7, '2026-10-19T05:03:10Z'),
      user(2, 7, '2026-10-19T05:03:40Z'),
      user(3, 8, '2026-10-19T05:03:50Z'),
    ])
    expect(rows.map((r) => r.head)).toEqual([true, false, true])
    expect(rows.map((r) => r.time)).toEqual(['', '14:03', '14:03'])
  })

  it('분이 바뀌면 같은 사람이어도 새 묶음으로 시작한다', () => {
    const rows = layoutMessages([user(1, 7, '2026-10-19T05:03:10Z'), user(2, 7, '2026-10-19T05:04:00Z')])
    expect(rows.map((r) => r.head)).toEqual([true, true])
  })

  it('서울 날짜가 바뀌는 자리에 날짜 구분 문구를 넣는다', () => {
    const rows = layoutMessages([user(1, 7, '2026-10-18T14:59:00Z'), user(2, 7, '2026-10-18T15:00:00Z')])
    expect(rows.map((r) => r.day)).toEqual(['10월 18일 일요일', '10월 19일 월요일'])
    expect(rows[1].head).toBe(true)
  })

  it('시스템 메시지는 앞뒤 메시지와 묶지 않는다', () => {
    const sys = { id: 2, kind: 'system', body: '입장', created_at: '2026-10-19T05:03:20Z' }
    const rows = layoutMessages([user(1, 7, '2026-10-19T05:03:10Z'), sys, user(3, 7, '2026-10-19T05:03:30Z')])
    expect(rows.map((r) => r.head)).toEqual([true, true, true])
  })
})
