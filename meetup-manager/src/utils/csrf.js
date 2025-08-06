let csrfToken = null

export async function getCSRFToken(force = false) {
  if (!csrfToken || force) {
    console.log('Getting CSRF token, force:', force)
    
    // Always try to fetch fresh token from API for auth requests
    try {
      console.log('Fetching fresh CSRF token from API...')
      const response = await fetch('/api/csrf/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
        }
      })
      console.log('CSRF API response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        csrfToken = data.csrfToken
        console.log('CSRF token from API:', csrfToken ? csrfToken.substring(0, 10) + '...' : 'null')
      } else {
        console.error('Failed to get CSRF token, status:', response.status)
        // Fallback to cookie if API fails
        csrfToken = getCookie('csrftoken')
        console.log('CSRF token from cookie fallback:', csrfToken ? csrfToken.substring(0, 10) + '...' : 'null')
      }
    } catch (error) {
      console.error('Failed to get CSRF token from API:', error)
      // Fallback to cookie if API fails
      csrfToken = getCookie('csrftoken')
      console.log('CSRF token from cookie fallback:', csrfToken ? csrfToken.substring(0, 10) + '...' : 'null')
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
  // Always get fresh token for auth and modifying requests
  const isAuthEndpoint = url.includes('/auth/') || url.includes('/csrf/')
  const isModifyingRequest = ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method)
  const needsCSRF = isAuthEndpoint || isModifyingRequest
  
  console.log('Making request to:', url, 'with method:', options.method || 'GET', 'needsCSRF:', needsCSRF)
  
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...options.headers
  }
  
  // Only add CSRF token for requests that need it
  if (needsCSRF) {
    const token = await getCSRFToken(true) // Always force fresh for auth requests
    if (token) {
      headers['X-CSRFToken'] = token
      console.log('CSRF token added to request:', token.substring(0, 10) + '...')
    } else {
      console.warn('No CSRF token available for request to:', url)
    }
  }
  
  const fetchOptions = {
    credentials: 'include',
    ...options,
    headers
  }
  
  try {
    const response = await fetch(url, fetchOptions)
    console.log('Response status:', response.status, 'for', url)
    
    // If we get a 403 and haven't already retried with fresh token
    if (response.status === 403 && needsCSRF) {
      console.log('Got 403, retrying with fresh CSRF token...')
      const freshToken = await getCSRFToken(true)
      if (freshToken) {
        headers['X-CSRFToken'] = freshToken
        const retryResponse = await fetch(url, {
          credentials: 'include',
          ...options,
          headers
        })
        console.log('Retry response status:', retryResponse.status)
        return retryResponse
      }
    }
    
    return response
  } catch (error) {
    console.error('Fetch error for', url, ':', error)
    throw error
  }
}