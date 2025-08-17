<template>
  <button
    @click="toggleTheme"
    :class="[
      'relative inline-flex items-center justify-center w-11 h-11 rounded-lg bg-beige-200 dark:bg-neutral-900 border border-beige-300 dark:border-neutral-800 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-neutral-950 group',
      variant === 'amber'
        ? 'hover:border-amber-300 dark:hover:border-amber-600 focus:ring-amber-500'
        : variant === 'neutral'
          ? 'hover:border-neutral-400 dark:hover:border-neutral-600 focus:ring-neutral-500'
          : 'hover:border-primary-300 dark:hover:border-primary-700 focus:ring-primary-500'
    ]"
    :title="themeStore.isDarkMode ? '라이트 모드로 전환' : '다크 모드로 전환'"
  >
    <!-- Subtle background hover effect -->
    <div :class="[
      'absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200',
      variant === 'amber'
        ? 'bg-amber-50 dark:bg-amber-900/10'
        : variant === 'neutral'
          ? 'bg-neutral-100 dark:bg-neutral-800/20'
          : 'bg-primary-50 dark:bg-primary-900/10'
    ]"></div>
    
    <!-- Icon container with smooth transitions -->
    <div class="relative z-10 flex items-center justify-center">
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        leave-active-class="transition-all duration-300 ease-out"
        enter-from-class="scale-0 rotate-180 opacity-0"
        leave-to-class="scale-0 rotate-180 opacity-0"
        mode="out-in"
      >
        <!-- Moon icon (shown in light mode) -->
        <svg
          v-if="!themeStore.isDarkMode"
          key="moon"
          :class="[
            'w-5 h-5 text-neutral-600 dark:text-neutral-400 transition-colors duration-200',
            variant === 'amber'
              ? 'group-hover:text-amber-600 dark:group-hover:text-amber-400'
              : variant === 'neutral'
                ? 'group-hover:text-neutral-700 dark:group-hover:text-neutral-300'
                : 'group-hover:text-primary-600 dark:group-hover:text-primary-400'
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>

        <!-- Sun icon (shown in dark mode) -->
        <svg
          v-else
          key="sun"
          :class="[
            'w-5 h-5 text-neutral-600 dark:text-neutral-400 transition-colors duration-200',
            variant === 'amber'
              ? 'group-hover:text-amber-600 dark:group-hover:text-amber-400'
              : variant === 'neutral'
                ? 'group-hover:text-neutral-700 dark:group-hover:text-neutral-300'
                : 'group-hover:text-primary-600 dark:group-hover:text-primary-400'
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
      </Transition>
    </div>
    
    <!-- Subtle indicator dot -->
    <div :class="[
      'absolute -top-1 -right-1 w-3 h-3 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300',
      variant === 'amber'
        ? 'bg-amber-500 dark:bg-amber-400'
        : variant === 'neutral'
          ? 'bg-neutral-500 dark:bg-neutral-400'
          : 'bg-primary-500 dark:bg-primary-400'
    ]"></div>
  </button>
</template>

<script>
import { useThemeStore } from '@/stores/theme'

export default {
  name: 'ThemeToggle',
  props: {
    variant: {
      type: String,
      default: 'neutral'
    }
  },
  setup() {
    const themeStore = useThemeStore()

    const toggleTheme = () => {
      // Add haptic feedback for mobile devices
      if (navigator.vibrate) {
        navigator.vibrate(10)
      }
      
      // Smooth theme transition
      document.documentElement.style.transition = 'background-color 0.3s ease, color 0.3s ease'
      themeStore.toggleTheme()
      
      // Remove transition after animation completes to avoid affecting other transitions
      setTimeout(() => {
        document.documentElement.style.transition = ''
      }, 300)
    }

    return {
      themeStore,
      toggleTheme
    }
  }
}
</script>
