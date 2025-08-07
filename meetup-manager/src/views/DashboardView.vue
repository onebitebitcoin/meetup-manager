
<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <nav class="bg-gray-50 dark:bg-gray-800 shadow safe-area-top">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">오프라인 모임</h1>
          </div>
          <div class="flex items-center space-x-1 sm:space-x-4">
            <router-link
              v-if="authStore.isAdmin"
              to="/admin"
              class="text-purple-500 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 px-2 sm:px-3 py-2 rounded-md text-sm font-medium hidden sm:block"
            >
              관리자
            </router-link>
            <router-link
              v-if="!authStore.isGuest"
              to="/settings"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 px-2 sm:px-3 py-2 rounded-md text-sm font-medium hidden sm:block"
            >
              내 모임
            </router-link>
            <!-- Mobile: Only show essential navigation -->
            <router-link
              v-if="!authStore.isGuest"
              to="/settings"
              class="sm:hidden p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-md"
              title="내 모임"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
            </router-link>
            <div class="sm:hidden">
              <ThemeToggle />
            </div>
            <div class="hidden sm:block">
              <ThemeToggle />
            </div>
            <span class="text-gray-700 dark:text-gray-300 hidden sm:inline">{{ authStore.user?.name }}님</span>
            <span v-if="authStore.isGuest" class="text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded-full hidden sm:inline">게스트 모드</span>
            <button
              @click="logout"
              class="bg-red-600 hover:bg-red-700 text-white px-1 sm:px-4 py-1 sm:py-2 rounded-md text-sm font-medium"
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

    <!-- Guest Mode Banner -->
    <div v-if="authStore.isGuest" class="bg-yellow-50 dark:bg-yellow-900 border-b border-yellow-200 dark:border-yellow-800">
      <div class="max-w-7xl mx-auto py-3 px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <svg class="h-5 w-5 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
            </svg>
            <span class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
              게스트 모드로 접속중입니다. 모임 조회만 가능하며, 참가 신청 및 모임 생성은 할 수 없습니다.
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto py-4 sm:py-6 px-4 sm:px-6 lg:px-8">
      <div class="sm:px-0">
        <!-- 통계 카드 -->
        <div class="grid grid-cols-1 gap-3 sm:gap-5 sm:grid-cols-2 lg:grid-cols-2 mb-6 sm:mb-8">
          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-lg rounded-xl border border-gray-200 dark:border-gray-700">
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

          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-lg rounded-xl border border-gray-200 dark:border-gray-700">
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
          </div>


        <!-- 메인 컨텐츠 -->
        <div class="space-y-6">
          <!-- 뷰 컨테이너 with toggle buttons -->
          <div class="relative">
            <!-- 뷰 토글 버튼 (오른쪽 상단) -->
            <div class="absolute top-2 sm:top-4 right-2 sm:right-4 z-10 flex space-x-1 bg-gray-50 dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-1">
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
            <div :class="{ '-mx-4 sm:mx-0': activeView === 'calendar' }">
              <CalendarView v-if="activeView === 'calendar'" :meetups="sortedMeetups" />
              <MeetupTable v-if="activeView === 'table'" :meetups="sortedMeetups" tableCentered />
            </div>
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


    // 전체 모임 수
    const totalMeetups = computed(() => meetupsStore.meetups.length)

    // 이번 주 모임 수
    const thisWeekMeetups = computed(() => {
      const now = new Date()
      const weekStart = new Date(now)
      weekStart.setDate(now.getDate() - now.getDay())
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      return meetupsStore.meetups.filter(meetup => {
        const meetupDate = new Date(meetup.date_time)
        return meetupDate >= weekStart && meetupDate <= weekEnd
      }).length
    })

    // 정렬된 모임 목록: 모집중(시작 임박순) -> 종료된 모임(종료일 오름차순)
    const sortedMeetups = computed(() => {
      const now = new Date()
      // 모집중(아직 끝나지 않은) 모임
      const ongoing = meetupsStore.meetups.filter(m => {
        const end = m.end_time ? new Date(m.end_time) : new Date(m.date_time)
        return end > now
      })
      // 종료된 모임
      const ended = meetupsStore.meetups.filter(m => {
        const end = m.end_time ? new Date(m.end_time) : new Date(m.date_time)
        return end <= now
      })
      // 모집중 모임은 시작일 오름차순, 종료된 모임은 종료일 오름차순
      ongoing.sort((a, b) => new Date(a.date_time) - new Date(b.date_time))
      ended.sort((a, b) => {
        const aEnd = a.end_time ? new Date(a.end_time) : new Date(a.date_time)
        const bEnd = b.end_time ? new Date(b.end_time) : new Date(b.date_time)
        return aEnd - bEnd
      })
      return [...ongoing, ...ended]
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
      // Small delay to ensure session is fully established after login
      await new Promise(resolve => setTimeout(resolve, 100))
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
      logout,
      sortedMeetups
    }
  }
}
</script>