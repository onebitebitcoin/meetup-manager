import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDarkMode = ref(false) // 라이트 모드를 기본값으로 설정
  const systemPreference = ref('dark')
  const isAutoMode = ref(false)

  // 시스템 테마 감지
  const detectSystemTheme = () => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      systemPreference.value = mediaQuery.matches ? 'dark' : 'light'
      
      // 시스템 테마 변경 감지
      mediaQuery.addEventListener('change', (e) => {
        systemPreference.value = e.matches ? 'dark' : 'light'
        if (isAutoMode.value) {
          isDarkMode.value = e.matches
        }
      })
    }
  }

  // 로컬 스토리지에서 테마 설정 불러오기
  const loadTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    const savedAutoMode = localStorage.getItem('theme-auto') === 'true'
    
    isAutoMode.value = savedAutoMode
    
    if (savedAutoMode) {
      // 자동 모드일 때는 시스템 설정 따라감
      detectSystemTheme()
      isDarkMode.value = systemPreference.value === 'dark'
    } else if (savedTheme !== null) {
      isDarkMode.value = savedTheme === 'dark'
    } else {
      // 저장된 테마가 없으면 라이트 모드를 기본값으로 설정
      detectSystemTheme()
      isDarkMode.value = false
    }
    
    applyTheme()
  }

  // 테마 적용 (향상된 애니메이션 포함)
  const applyTheme = () => {
    const root = document.documentElement
    
    // 부드러운 전환을 위한 클래스 추가
    root.style.transition = 'background-color 0.3s ease, color 0.3s ease'
    
    if (isDarkMode.value) {
      root.classList.add('dark')
      // PWA 테마 색상 업데이트 - 다크 모드용 녹색
      updateMetaThemeColor('#052e16') // primary-950
    } else {
      root.classList.remove('dark')
      // PWA 테마 색상 업데이트 - 라이트 모드용 녹색
      updateMetaThemeColor('#22c55e') // primary-500
    }
    
    // 전환 애니메이션 후 transition 제거
    setTimeout(() => {
      root.style.transition = ''
    }, 300)
  }

  // PWA 메타 테마 색상 업데이트
  const updateMetaThemeColor = (color) => {
    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', color)
    }
  }

  // 테마 토글 (수동 모드)
  const toggleTheme = () => {
    isAutoMode.value = false
    isDarkMode.value = !isDarkMode.value
    localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
    localStorage.setItem('theme-auto', 'false')
    applyTheme()
  }

  // 자동 테마 설정
  const setAutoTheme = () => {
    isAutoMode.value = true
    detectSystemTheme()
    isDarkMode.value = systemPreference.value === 'dark'
    localStorage.setItem('theme-auto', 'true')
    localStorage.removeItem('theme')
    applyTheme()
  }

  // 수동 테마 설정
  const setManualTheme = (theme) => {
    isAutoMode.value = false
    isDarkMode.value = theme === 'dark'
    localStorage.setItem('theme', theme)
    localStorage.setItem('theme-auto', 'false')
    applyTheme()
  }

  // 현재 테마 상태 반환
  const currentTheme = () => {
    if (isAutoMode.value) {
      return 'auto'
    }
    return isDarkMode.value ? 'dark' : 'light'
  }

  // 다크 모드 감시 및 자동 적용
  watch(isDarkMode, () => {
    if (!isAutoMode.value) {
      localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
    }
    applyTheme()
  }, { immediate: false })

  // 초기 시스템 테마 감지
  detectSystemTheme()

  return {
    isDarkMode,
    isAutoMode,
    systemPreference,
    toggleTheme,
    loadTheme,
    setAutoTheme,
    setManualTheme,
    currentTheme
  }
})