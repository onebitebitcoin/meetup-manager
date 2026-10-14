const BASE = '/api/lite'
export const TOKEN_KEY = 'lite_token'

export const readToken = () => {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export const writeToken = (token) => {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    // 저장소를 쓸 수 없으면 메모리 상태만 유지한다
  }
}

export const request = async (path, { method = 'GET', body, token = readToken() } = {}) => {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['X-Member-Token'] = token

  let response
  try {
    response = await fetch(`${BASE}/${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new Error('네트워크 오류')
  }

  let data = null
  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (!response.ok) {
    const error = new Error(data?.error || `요청에 실패했어요 (${response.status})`)
    error.status = response.status
    throw error
  }
  return data
}

export const liteApi = {
  createMember: (name) => request('members/', { method: 'POST', body: { name } }),
  me: (token) => request('me/', token ? { token } : {}),
  claimHost: (key) => request('host/claim/', { method: 'POST', body: { key } }),
  home: () => request('home/'),
  createMeetup: (payload) => request('meetups/', { method: 'POST', body: payload }),
  meetup: (id) => request(`meetups/${id}/`),
  rsvp: (id, status) => request(`meetups/${id}/rsvp/`, { method: 'PUT', body: { status } }),
  checkin: (id, code) => request(`meetups/${id}/checkin/`, { method: 'POST', body: { code } }),
  messages: (roomId, after) => request(`rooms/${roomId}/messages/${after ? `?after=${after}` : ''}`),
  olderMessages: (roomId, before) => request(`rooms/${roomId}/messages/?before=${before}`),
  sendMessage: (roomId, body) => request(`rooms/${roomId}/messages/`, { method: 'POST', body: { body } }),
  seminar: () => request('seminar/', { method: 'POST' }),
  seminarMode: (mode) => request('seminar/mode/', { method: 'POST', body: { mode } }),
  confirmSeminar: (id) => request(`seminars/${id}/confirm/`, { method: 'POST' }),
  requests: () => request('requests/'),
  createRequest: (title, preferredPeriod) => request('requests/', {
    method: 'POST',
    body: { title, preferred_period: preferredPeriod },
  }),
  vote: (id) => request(`requests/${id}/vote/`, { method: 'POST' }),
}
