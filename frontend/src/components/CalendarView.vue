<template>
  <div class="bg-white dark:bg-neutral-800 rounded-lg shadow p-3 sm:p-6">
    <div class="flex items-center justify-between mb-3 sm:mb-6">
      <h2 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">
        달력
      </h2>
    </div>
    
    <!-- Centered year/month navigation -->
    <div class="flex items-center justify-center mb-3 sm:mb-6">
      <div class="flex items-center space-x-3 sm:space-x-6">
        <button
          class="p-1 sm:p-2 hover:bg-gray-100 dark:hover:bg-neutral-700 rounded-full text-gray-900 dark:text-white transition-colors"
          @click="previousMonth"
        >
          <svg
            class="w-4 h-4 sm:w-5 sm:h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
        <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white min-w-[140px] sm:min-w-[200px] text-center">
          {{ currentMonth.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' }) }}
        </h3>
        <button
          class="p-1 sm:p-2 hover:bg-gray-100 dark:hover:bg-neutral-700 rounded-full text-gray-900 dark:text-white transition-colors"
          @click="nextMonth"
        >
          <svg
            class="w-4 h-4 sm:w-5 sm:h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      </div>
    </div>

    <div class="overflow-x-auto">
      <div class="grid grid-cols-7 gap-px sm:gap-1 mb-2 sm:mb-4 min-w-[280px]">
        <div v-for="day in weekDays" :key="day" class="p-1 sm:p-2 text-center text-xs sm:text-sm font-medium text-gray-700 dark:text-neutral-300">
          {{ day }}
        </div>
      </div>
    </div>

    <div class="overflow-x-auto">
      <div class="grid grid-cols-7 gap-px sm:gap-1 min-w-[280px]">
        <div
          v-for="date in calendarDates"
          :key="date.date"
          class="relative p-1 sm:p-2 min-h-[80px] sm:min-h-[110px] border border-gray-200 dark:border-neutral-600 hover:bg-gray-50 dark:hover:bg-neutral-700"
          :class="{
            'bg-gray-100 dark:bg-neutral-700': !date.isCurrentMonth,
            'bg-blue-50 dark:bg-neutral-600': date.isToday
          }"
        >
          <div class="text-xs sm:text-sm font-medium" :class="{ 'text-gray-400 dark:text-neutral-400': !date.isCurrentMonth, 'text-gray-900 dark:text-white': date.isCurrentMonth }">
            {{ date.date.getDate() }}
          </div>
        
          <div v-if="date.meetups.length > 0" class="mt-0.5 sm:mt-1 space-y-0.5 sm:space-y-1">
            <div
              v-for="meetup in date.meetups.slice(0, 1)"
              :key="meetup.id"
              class="text-xs bg-indigo-100 dark:bg-neutral-600 text-indigo-800 dark:text-neutral-100 px-1 sm:px-2 py-0.5 sm:py-1 rounded cursor-pointer hover:bg-indigo-200 dark:hover:bg-neutral-500 truncate block sm:hidden"
              @click="$router.push(`/meetup/${meetup.id}`)"
            >
              {{ meetup.name.length > 6 ? meetup.name.substring(0, 6) + '...' : meetup.name }}
            </div>
            <div
              v-for="meetup in date.meetups.slice(0, 2)"
              :key="meetup.id"
              class="text-xs bg-indigo-100 dark:bg-neutral-600 text-indigo-800 dark:text-neutral-100 px-1 sm:px-2 py-0.5 sm:py-1 rounded cursor-pointer hover:bg-indigo-200 dark:hover:bg-neutral-500 truncate hidden sm:block"
              @click="$router.push(`/meetup/${meetup.id}`)"
            >
              {{ meetup.name }}
            </div>
            <div 
              v-if="date.meetups.length > 1" 
              class="text-xs text-gray-500 dark:text-neutral-400 cursor-pointer hover:text-gray-700 dark:hover:text-neutral-300 px-1 sm:px-2 py-0.5 sm:py-1 rounded hover:bg-gray-100 dark:hover:bg-neutral-600 sm:hidden"
              @click="showDateMeetups(date)"
            >
              +{{ date.meetups.length - 1 }}개
            </div>
            <div 
              v-if="date.meetups.length > 2" 
              class="text-xs text-gray-500 dark:text-neutral-400 cursor-pointer hover:text-gray-700 dark:hover:text-neutral-300 px-1 sm:px-2 py-0.5 sm:py-1 rounded hover:bg-gray-100 dark:hover:bg-neutral-600 hidden sm:block"
              @click="showDateMeetups(date)"
            >
              +{{ date.meetups.length - 2 }}개 더
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 날짜별 모임 목록 모달 -->
    <div v-if="selectedDateMeetups" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click="selectedDateMeetups = null">
      <div class="bg-beige-50 dark:bg-neutral-800 rounded-2xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-hidden" @click.stop>
        <div class="relative p-6 border-b border-neutral-200 dark:border-neutral-600 bg-beige-200 dark:bg-neutral-700">
          <button class="absolute top-4 right-4 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 transition-colors" @click="selectedDateMeetups = null">
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
          <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 pr-8">
            {{ selectedDateMeetups.date.toLocaleDateString('ko-KR', { month: 'long', day: 'numeric' }) }} 모임 목록
          </h3>
        </div>
        <div class="px-6 py-4 overflow-y-auto max-h-[calc(90vh-12rem)]">
          <div class="space-y-3">
            <div 
              v-for="meetup in selectedDateMeetups.meetups" 
              :key="meetup.id"
              class="p-4 border border-neutral-200 dark:border-neutral-600 rounded-lg cursor-pointer hover:bg-beige-100 dark:hover:bg-neutral-700 transition-colors"
              @click="selectMeetupFromDate(meetup)"
            >
              <div class="flex justify-between items-start gap-3 mb-2">
                <h4 class="font-medium text-neutral-900 dark:text-neutral-100 min-w-0 flex-1 truncate">
                  {{ meetup.name }}
                </h4>
                <span 
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full whitespace-nowrap flex-shrink-0"
                  :class="getStatusClass(meetup)"
                >
                  {{ getStatus(meetup) }}
                </span>
              </div>
              <div class="text-sm text-neutral-600 dark:text-neutral-400 space-y-1">
                <div>
                  <span class="font-medium">시간:</span> 
                  {{ formatTime(meetup.date_time) }}
                  <span v-if="meetup.end_time"> - {{ formatTime(meetup.end_time) }}</span>
                </div>
                <div><span class="font-medium">장소:</span> {{ meetup.location }}</div>
                <div><span class="font-medium">참여:</span> {{ meetup.current_participants }} / {{ meetup.max_participants }}명</div>
                <div class="text-xs text-neutral-500 dark:text-neutral-400 truncate">
                  {{ meetup.description }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'CalendarView',
  props: {
    meetups: {
      type: Array,
      default: () => [],
    },
  },
  setup(props) {
    const router = useRouter()
    const currentMonth = ref(new Date())
    const selectedDateMeetups = ref(null)

    const weekDays = ['일', '월', '화', '수', '목', '금', '토']

    const calendarDates = computed(() => {
      const year = currentMonth.value.getFullYear()
      const month = currentMonth.value.getMonth()
      
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      const startDate = new Date(firstDay)
      startDate.setDate(startDate.getDate() - firstDay.getDay())
      
      const dates = []
      const current = new Date(startDate)
      
      for (let i = 0; i < 42; i++) {
        const dateObj = new Date(current)
        const isCurrentMonth = dateObj.getMonth() === month
        const isToday = dateObj.toDateString() === new Date().toDateString()
        
        const dayMeetups = props.meetups.filter(meetup => {
          const meetupDate = new Date(meetup.date_time)
          return meetupDate.toDateString() === dateObj.toDateString()
        })

        dates.push({
          date: dateObj,
          isCurrentMonth,
          isToday,
          meetups: dayMeetups,
        })
        
        current.setDate(current.getDate() + 1)
      }
      
      return dates
    })

    const previousMonth = () => {
      currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() - 1, 1)
    }

    const nextMonth = () => {
      currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1)
    }

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString('ko-KR')
    }

    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
      })
    }

    const showDateMeetups = (dateData) => {
      selectedDateMeetups.value = dateData
    }

    const selectMeetupFromDate = (meetup) => {
      selectedDateMeetups.value = null
      router.push(`/meetup/${meetup.id}`)
    }

    const getStatus = (meetup) => {
      const meetupDate = new Date(meetup.date_time)
      const now = new Date()
      const diffHours = (meetupDate - now) / (1000 * 60 * 60)

      if (diffHours < 0) {
        return '종료'
      } else if (meetup.current_participants >= meetup.max_participants) {
        return '마감'
      } else if (diffHours < 24) {
        return '임박'
      } else if (diffHours < 72) {
        return '예정'
      } else {
        return '모집중'
      }
    }

    const getStatusClass = (meetup) => {
      const status = getStatus(meetup)
      const classes = {
        '종료': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
        '마감': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        '임박': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
        '예정': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        '모집중': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      }
      return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    }

    return {
      currentMonth,
      selectedDateMeetups,
      weekDays,
      calendarDates,
      previousMonth,
      nextMonth,
      formatDateTime,
      formatTime,
      showDateMeetups,
      selectMeetupFromDate,
      getStatus,
      getStatusClass,
    }
  },
}
</script>
