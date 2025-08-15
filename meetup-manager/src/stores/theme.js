import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDarkMode = ref(true) // 다크 모드를 기본값으로 설정

  // 로컬 스토리지에서 테마 설정 불러오기
  const loadTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme !== null) {
      isDarkMode.value = savedTheme === 'dark'
    } else {
      // 저장된 테마가 없으면 다크 모드를 기본값으로 설정
      isDarkMode.value = true
    }
    applyTheme()
  }

  // 테마 적용
  const applyTheme = () => {
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // 테마 토글
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
    localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
    applyTheme()
  }

  // 다크 모드 감시 및 자동 적용
  watch(isDarkMode, () => {
    localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
    applyTheme()
  }, { immediate: true })

  return {
    isDarkMode,
    toggleTheme,
    loadTheme
  }
})