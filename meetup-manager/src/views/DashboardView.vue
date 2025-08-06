<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <nav class="bg-white dark:bg-gray-800 shadow safe-area-top">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">모임 대시보드</h1>
          </div>
          <div class="flex items-center space-x-2 sm:space-x-4">
            <!-- <router-link
              to="/create-meetup"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              모임 만들기
            </router-link> -->
            <router-link
              v-if="authStore.isAdmin"
              to="/admin"
              class="text-purple-500 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 px-2 sm:px-3 py-2 rounded-md text-sm font-medium hidden sm:block"
            >
              관리자
            </router-link>
            <router-link
              to="/settings"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 px-2 sm:px-3 py-2 rounded-md text-sm font-medium hidden sm:block"
            >
              내 모임
            </router-link>
            <router-link
              v-if="authStore.isAdmin"
              to="/admin"
              class="sm:hidden p-2 text-purple-500 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 rounded-md"
              title="관리자"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
              </svg>
            </router-link>
            <router-link
              to="/settings"
              class="sm:hidden p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-md"
              title="내 모임"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
            </router-link>
            <ThemeToggle />
            <span class="text-gray-700 dark:text-gray-300 hidden sm:inline">{{ authStore.user?.name }}님</span>
            <span class="text-gray-700 dark:text-gray-300 sm:hidden text-xs">{{ authStore.user?.name?.slice(0, 3) }}</span>
            <button
              @click="logout"
              class="bg-red-600 hover:bg-red-700 text-white px-2 sm:px-4 py-2 rounded-md text-sm font-medium"
            >
              <span class="hidden sm:inline">로그아웃</span>
              <svg class="w-4 h-4 sm:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto py-4 sm:py-6 px-4 sm:px-6 lg:px-8">
      <div class="sm:px-0">
        <!-- 통계 카드 -->
        <div class="grid grid-cols-2 gap-3 sm:gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6 sm:mb-8">
          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">전체 모임</dt>
                    <dd class="text-lg font-medium text-gray-900 dark:text-white">{{ totalMeetups }}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">이번 주 모임</dt>
                    <dd class="text-lg font-medium text-gray-900 dark:text-white">{{ thisWeekMeetups }}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-8 w-8 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">다가오는 모임</dt>
                    <dd class="text-lg font-medium text-gray-900 dark:text-white">{{ upcomingMeetups }}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-8 w-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">등록된 참여자</dt>
                    <dd class="text-lg font-medium text-gray-900 dark:text-white">{{ totalRegistered }}명</dd>
                    <dd class="text-xs text-gray-500 dark:text-gray-400">/ {{ totalCapacity }}명 (총 정원)</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 메인 컨텐츠 -->
        <div class="space-y-6">
          <!-- 뷰 컨테이너 with toggle buttons -->
          <div class="relative">
            <!-- 뷰 토글 버튼 (오른쪽 상단) -->
            <div class="absolute top-2 sm:top-4 right-2 sm:right-4 z-10 flex space-x-1 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-1">
              <button
                @click="activeView = 'calendar'"
                :class="[
                  'p-2 rounded-md transition-colors',
                  activeView === 'calendar' 
                    ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300' 
                    : 'text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                ]"
                title="캘린더 보기"
              >
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </button>
              <button
                @click="activeView = 'table'"
                :class="[
                  'p-2 rounded-md transition-colors',
                  activeView === 'table' 
                    ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300' 
                    : 'text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                ]"
                title="테이블 보기"
              >
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0V4a1 1 0 011-1h14a1 1 0 011 1v16a1 1 0 01-1 1H4a1 1 0 01-1-1z" />
                </svg>
              </button>
            </div>
            
            <!-- 실제 뷰 컴포넌트 -->
            <CalendarView v-if="activeView === 'calendar'" />
            <MeetupTable v-if="activeView === 'table'" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMeetupsStore } from '@/stores/meetups'
import CalendarView from '@/components/CalendarView.vue'
import MeetupTable from '@/components/MeetupTable.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

export default {
  name: 'DashboardView',
  components: {
    CalendarView,
    MeetupTable,
    ThemeToggle
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const meetupsStore = useMeetupsStore()
    const activeView = ref('calendar')

    const totalMeetups = computed(() => meetupsStore.meetups.length)

    const thisWeekMeetups = computed(() => {
      const now = new Date()
      const weekStart = new Date(now.setDate(now.getDate() - now.getDay()))
      const weekEnd = new Date(now.setDate(now.getDate() - now.getDay() + 6))
      
      return meetupsStore.meetups.filter(meetup => {
        const meetupDate = new Date(meetup.date_time)
        return meetupDate >= weekStart && meetupDate <= weekEnd
      }).length
    })

    const upcomingMeetups = computed(() => {
      const now = new Date()
      return meetupsStore.meetups.filter(meetup => {
        const meetupDate = new Date(meetup.date_time)
        return meetupDate > now
      }).length
    })

    const totalCapacity = computed(() => {
      return meetupsStore.meetups.reduce((sum, meetup) => sum + meetup.max_participants, 0)
    })

    const totalRegistered = computed(() => {
      return meetupsStore.meetups.reduce((sum, meetup) => 
        sum + meetupsStore.getRegistrationCount(meetup.id), 0)
    })

    const availableSeats = computed(() => {
      return totalCapacity.value - totalRegistered.value
    })

    const fullMeetups = computed(() => {
      return meetupsStore.meetups.filter(meetup => 
        meetupsStore.isMeetupFull(meetup.id)).length
    })

    const averageAttendance = computed(() => {
      if (totalCapacity.value === 0) return 0
      return Math.round((totalRegistered.value / totalCapacity.value) * 100)
    })

    const formatDateTime = (dateTimeString) => {
      const date = new Date(dateTimeString)
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const logout = () => {
      authStore.logout()
      router.push('/login')
    }

    onMounted(async () => {
      authStore.checkAuth()
      await meetupsStore.fetchMeetups()
    })

    return {
      authStore,
      meetupsStore,
      activeView,
      totalMeetups,
      thisWeekMeetups,
      upcomingMeetups,
      totalCapacity,
      totalRegistered,
      availableSeats,
      fullMeetups,
      averageAttendance,
      formatDateTime,
      logout
    }
  }
}
</script>