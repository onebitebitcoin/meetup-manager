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
