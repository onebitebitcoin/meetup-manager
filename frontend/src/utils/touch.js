// Touch gesture utilities for mobile interaction

export function addSwipeListener(element, callback) {
  let startX, startY, startTime
  
  element.addEventListener('touchstart', (e) => {
    const touch = e.touches[0]
    startX = touch.clientX
    startY = touch.clientY
    startTime = Date.now()
  }, { passive: true })
  
  element.addEventListener('touchend', (e) => {
    if (!startX || !startY) return
    
    const touch = e.changedTouches[0]
    const endX = touch.clientX
    const endY = touch.clientY
    const endTime = Date.now()
    
    const deltaX = endX - startX
    const deltaY = endY - startY
    const deltaTime = endTime - startTime
    
    // Minimum swipe distance and maximum time
    const minDistance = 50
    const maxTime = 500
    
    if (deltaTime > maxTime) return
    
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minDistance) {
      // Horizontal swipe
      callback({
        direction: deltaX > 0 ? 'right' : 'left',
        distance: Math.abs(deltaX),
        velocity: Math.abs(deltaX) / deltaTime
      })
    } else if (Math.abs(deltaY) > minDistance) {
      // Vertical swipe
      callback({
        direction: deltaY > 0 ? 'down' : 'up',
        distance: Math.abs(deltaY),
        velocity: Math.abs(deltaY) / deltaTime
      })
    }
    
    startX = startY = null
  }, { passive: true })
}

export function addPullToRefresh(element, callback) {
  let startY, currentY, isRefreshing = false
  
  element.addEventListener('touchstart', (e) => {
    if (element.scrollTop === 0) {
      startY = e.touches[0].clientY
      currentY = startY
    }
  }, { passive: true })
  
  element.addEventListener('touchmove', (e) => {
    if (!startY || isRefreshing) return
    
    currentY = e.touches[0].clientY
    const pullDistance = currentY - startY
    
    if (pullDistance > 0 && element.scrollTop === 0) {
      e.preventDefault()
      
      // Add visual feedback
      const pullThreshold = 80
      if (pullDistance > pullThreshold) {
        element.style.transform = `translateY(${Math.min(pullDistance / 3, 40)}px)`
        element.style.opacity = Math.max(0.7, 1 - (pullDistance / 200))
      }
    }
  })
  
  element.addEventListener('touchend', () => {
    if (!startY || isRefreshing) return
    
    const pullDistance = currentY - startY
    const pullThreshold = 80
    
    if (pullDistance > pullThreshold && element.scrollTop === 0) {
      isRefreshing = true
      callback(() => {
        isRefreshing = false
        element.style.transform = ''
        element.style.opacity = ''
      })
    } else {
      element.style.transform = ''
      element.style.opacity = ''
    }
    
    startY = currentY = null
  }, { passive: true })
}

export function hapticFeedback(type = 'medium') {
  if ('vibrate' in navigator) {
    switch (type) {
      case 'light':
        navigator.vibrate(10)
        break
      case 'medium':
        navigator.vibrate(25)
        break
      case 'heavy':
        navigator.vibrate(50)
        break
      case 'success':
        navigator.vibrate([25, 50, 25])
        break
      case 'error':
        navigator.vibrate([50, 25, 50, 25, 50])
        break
    }
  }
}

export function preventZoom() {
  // Prevent double-tap zoom on iOS
  let lastTouchEnd = 0
  document.addEventListener('touchend', (event) => {
    const now = Date.now()
    if (now - lastTouchEnd <= 300) {
      event.preventDefault()
    }
    lastTouchEnd = now
  }, false)
}

// Initialize mobile optimizations
export function initMobileOptimizations() {
  // Prevent zoom on input focus
  const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea')
  inputs.forEach(input => {
    input.style.fontSize = '16px'
  })
  
  // Prevent zoom on double tap
  preventZoom()
  
  // Add viewport-fit=cover for devices with safe areas
  const viewport = document.querySelector('meta[name="viewport"]')
  if (viewport) {
    viewport.setAttribute('content', viewport.getAttribute('content') + ', viewport-fit=cover')
  }
}