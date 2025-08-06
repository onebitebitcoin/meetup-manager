let csrfToken = null

export async function getCSRFToken(force = false) {
  if (!csrfToken || force) {
    console.log('Getting CSRF token, force:', force)
    
    // First try to get from cookie
    csrfToken = getCookie('csrftoken')
    console.log('CSRF token from cookie:', csrfToken ? csrfToken.substring(0, 10) + '...' : 'null')
    
    // If not in cookie, fetch from API
    if (!csrfToken) {
      try {
        console.log('Fetching CSRF token from API...')
        const response = await fetch('/api/csrf/', {
          credentials: 'include',
          headers: {
            'Origin': window.location.origin,
            'Referer': window.location.href
          }
        })
        console.log('CSRF API response status:', response.status)
        
        if (response.ok) {
          const data = await response.json()
          csrfToken = data.csrfToken
          console.log('CSRF token from API:', csrfToken ? csrfToken.substring(0, 10) + '...' : 'null')
        } else {
          console.error('Failed to get CSRF token, status:', response.status)
        }
      } catch (error) {
        console.error('Failed to get CSRF token:', error)
      }
    }
  }
  return csrfToken
}

export function resetCSRFToken() {
  csrfToken = null
}

export function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

export async function fetchWithCSRF(url, options = {}) {
  // Force fresh token for auth endpoints and modifying requests
  const isAuthEndpoint = url.includes('/auth/')
  const isModifyingRequest = ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method)
  const forceRefresh = isAuthEndpoint || isModifyingRequest
  
  const token = await getCSRFToken(forceRefresh)
  
  const headers = {
    'Content-Type': 'application/json',
    'Origin': window.location.origin,
    'Referer': window.location.href,
    ...options.headers
  }
  
  if (token) {
    headers['X-CSRFToken'] = token
    console.log('CSRF token added to request:', token.substring(0, 10) + '...')
  } else {
    console.warn('No CSRF token available for request to:', url)
  }
  
  console.log('Request headers:', headers)
  
  return fetch(url, {
    credentials: 'include',
    ...options,
    headers
  })
}