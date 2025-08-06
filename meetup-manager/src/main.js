import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import { initMobileOptimizations } from '@/utils/touch'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 테마 스토어 초기화
import { useThemeStore } from '@/stores/theme'
const themeStore = useThemeStore()
themeStore.loadTheme()

// Initialize mobile optimizations
initMobileOptimizations()

app.mount('#app')