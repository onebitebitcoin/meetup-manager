import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import 'dayjs/locale/ko'

dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.locale('ko')

// 기본 타임존 (클라이언트 타임존 사용)
const getLocalTimezone = () => dayjs.tz.guess()

/**
 * 로컬 datetime-local 값을 UTC ISO 문자열로 변환
 * @param {string} localStr - "YYYY-MM-DDTHH:mm" 형식의 로컬 시간
 * @returns {string} UTC ISO 문자열
 */
export const toUTC = (localStr) => {
  if (!localStr) return null
  return dayjs.tz(localStr, getLocalTimezone()).utc().toISOString()
}

/**
 * UTC 문자열을 클라이언트 타임존 dayjs 객체로 변환
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {dayjs.Dayjs} 로컬 타임존 dayjs 객체
 */
export const toLocal = (utcStr) => {
  if (!utcStr) return null
  return dayjs.utc(utcStr).tz(getLocalTimezone())
}

/**
 * UTC를 "2025년 1월 25일 14:00" 형식으로 포맷
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {string} 포맷된 날짜시간 문자열
 */
export const formatDateTime = (utcStr) => {
  if (!utcStr) return ''
  return toLocal(utcStr).format('YYYY년 M월 D일 HH:mm')
}

/**
 * UTC를 "2025년 1월 25일" 형식으로 포맷
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {string} 포맷된 날짜 문자열
 */
export const formatDate = (utcStr) => {
  if (!utcStr) return ''
  return toLocal(utcStr).format('YYYY년 M월 D일')
}

/**
 * UTC를 "14:00" 형식으로 포맷
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {string} 포맷된 시간 문자열
 */
export const formatTime = (utcStr) => {
  if (!utcStr) return ''
  return toLocal(utcStr).format('HH:mm')
}

/**
 * UTC를 datetime-local input 값으로 변환
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {string} "YYYY-MM-DDTHH:mm" 형식
 */
export const toDateTimeLocal = (utcStr) => {
  if (!utcStr) return ''
  return toLocal(utcStr).format('YYYY-MM-DDTHH:mm')
}

/**
 * UTC를 date input 값으로 변환
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {string} "YYYY-MM-DD" 형식
 */
export const toDateInput = (utcStr) => {
  if (!utcStr) return ''
  return toLocal(utcStr).format('YYYY-MM-DD')
}

/**
 * UTC를 time input 값으로 변환
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {string} "HH:mm" 형식
 */
export const toTimeInput = (utcStr) => {
  if (!utcStr) return ''
  return toLocal(utcStr).format('HH:mm')
}

/**
 * 오늘 날짜 (로컬 타임존)
 * @returns {dayjs.Dayjs} 오늘 날짜 dayjs 객체
 */
export const today = () => {
  return dayjs().tz(getLocalTimezone()).startOf('day')
}

/**
 * 미래 시점 여부 확인
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {boolean}
 */
export const isFuture = (utcStr) => {
  if (!utcStr) return false
  return toLocal(utcStr).isAfter(dayjs())
}

/**
 * 과거 시점 여부 확인
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {boolean}
 */
export const isPast = (utcStr) => {
  if (!utcStr) return false
  return toLocal(utcStr).isBefore(dayjs())
}

/**
 * 로컬 시간에 기간 추가 후 UTC 반환
 * @param {string} localStr - "YYYY-MM-DDTHH:mm" 형식의 로컬 시간
 * @param {number} amount - 추가할 양
 * @param {string} unit - 단위 ('hour', 'minute', 'day' 등)
 * @returns {string} UTC ISO 문자열
 */
export const addDurationToLocal = (localStr, amount, unit) => {
  if (!localStr) return null
  return dayjs.tz(localStr, getLocalTimezone()).add(amount, unit).utc().toISOString()
}

/**
 * "M/D (요일)" 형식으로 포맷 (캘린더용)
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {string}
 */
export const formatShortDate = (utcStr) => {
  if (!utcStr) return ''
  const local = toLocal(utcStr)
  const weekdays = ['일', '월', '화', '수', '목', '금', '토']
  return `${local.format('M/D')} (${weekdays[local.day()]})`
}

/**
 * 상대 시간 표시 ("3일 후", "2시간 전" 등)
 * @param {string} utcStr - UTC ISO 문자열
 * @returns {string}
 */
export const formatRelative = (utcStr) => {
  if (!utcStr) return ''
  const local = toLocal(utcStr)
  const now = dayjs()
  const diffMinutes = local.diff(now, 'minute')
  const diffHours = local.diff(now, 'hour')
  const diffDays = local.diff(now, 'day')

  if (Math.abs(diffMinutes) < 60) {
    return diffMinutes >= 0 ? `${diffMinutes}분 후` : `${Math.abs(diffMinutes)}분 전`
  }
  if (Math.abs(diffHours) < 24) {
    return diffHours >= 0 ? `${diffHours}시간 후` : `${Math.abs(diffHours)}시간 전`
  }
  return diffDays >= 0 ? `${diffDays}일 후` : `${Math.abs(diffDays)}일 전`
}

export default dayjs
