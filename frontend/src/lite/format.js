import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

const TZ = 'Asia/Seoul'
const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토']

export const STATUS_LABEL = { going: '참석', maybe: '미정', no: '불참' }
export const PERIOD_LABEL = { this_month: '이번 달', next_month: '다음 달', any: '상관없음' }
export const SEMINAR_STATUS_LABEL = { guide: '안내 중', received: '접수됨', confirmed: '확정' }
export const MODE_LABEL = { online: '온라인', offline: '오프라인' }

export const dateParts = (iso) => {
  const d = dayjs(iso).tz(TZ)
  return { month: d.month() + 1, day: d.date(), weekday: WEEKDAYS[d.day()], time: d.format('HH:mm') }
}

export const toSeoulIso = (date, time) => dayjs.tz(`${date} ${time}`, TZ).toISOString()

export const toSeoulParts = (iso) => {
  const d = dayjs(iso).tz(TZ)
  return { date: d.format('YYYY-MM-DD'), time: d.format('HH:mm') }
}

export const todaySeoul = () => dayjs().tz(TZ).format('YYYY-MM-DD')

// 서울 날짜 기준으로 모임까지 남은 날: 오늘 / 내일 / N일 후 (지난 모임은 빈 문자열)
export const daysUntilLabel = (iso, now = dayjs()) => {
  const start = dayjs(iso).tz(TZ).startOf('day')
  const today = dayjs(now).tz(TZ).startOf('day')
  const diff = Math.round(start.diff(today, 'day', true))
  if (diff < 0) return ''
  if (diff === 0) return '오늘'
  if (diff === 1) return '내일'
  return `${diff}일 후`
}

// location.hash 값을 읽고 즉시 주소에서 지운다(토큰과 운영자 키가 방문 기록에 남지 않게 한다)
export const takeHash = () => {
  const value = decodeURIComponent(window.location.hash.slice(1))
  window.history.replaceState(window.history.state, '', window.location.pathname + window.location.search)
  return value
}

const senderKey = (m) => (m.kind === 'user' ? `user:${m.member?.id}` : m.kind)
const minuteKey = (iso) => dayjs(iso).tz(TZ).format('YYYY-MM-DD HH:mm')
const sameGroup = (a, b) => !!a && !!b && a.kind !== 'system' && senderKey(a) === senderKey(b) && minuteKey(a.created_at) === minuteKey(b.created_at)

// 채팅방처럼 보이도록 같은 사람이 같은 분에 보낸 메시지를 묶는다.
// head: 묶음의 첫 메시지라 이름·아바타를 보인다 / time: 묶음의 마지막 메시지라 시각을 붙인다 / day: 날짜가 바뀌는 자리에 넣을 구분 문구
export const layoutMessages = (messages) => messages.map((message, i) => {
  const prev = messages[i - 1]
  const next = messages[i + 1]
  const d = dayjs(message.created_at).tz(TZ)
  const newDay = !prev || dayjs(prev.created_at).tz(TZ).format('YYYY-MM-DD') !== d.format('YYYY-MM-DD')
  return {
    message,
    day: newDay ? `${d.month() + 1}월 ${d.date()}일 ${WEEKDAYS[d.day()]}요일` : '',
    head: newDay || !sameGroup(prev, message),
    time: sameGroup(message, next) ? '' : d.format('HH:mm'),
  }
})
