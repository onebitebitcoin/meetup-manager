<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-950">
    <!-- Navigation -->
    <nav class="bg-beige-200 dark:bg-neutral-900 border-b border-beige-300 dark:border-neutral-800 safe-area-top">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center space-x-3">
            <img src="/icons/logo.png" alt="한입 모임 로고" class="h-8 w-8 rounded-lg" />
            <h1 class="text-lg sm:text-xl font-semibold text-black dark:text-neutral-100">
              내 모임 관리
            </h1>
          </div>
          <div class="flex items-center space-x-1 sm:space-x-4">
            <!-- Desktop navigation -->
            <router-link to="/dashboard"
              class="hidden sm:block text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-300 px-3 py-2 rounded-md text-sm font-medium">
              한입 모임
            </router-link>

            <!-- Mobile: Dashboard icon -->
            <router-link to="/dashboard"
              class="sm:hidden p-1 text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-300 rounded-md"
              title="한입 모임">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2V7z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5h8"></path>
              </svg>
            </router-link>

            <!-- Theme toggle - compact on mobile -->
            <div class="sm:hidden">
              <ThemeToggle />
            </div>
            <div class="hidden sm:block">
              <ThemeToggle />
            </div>

            <!-- User name - hidden on mobile -->
            <span class="hidden sm:inline text-neutral-700 dark:text-neutral-300">{{ authStore.user?.name }}님</span>

            <!-- Logout button - compact on mobile -->
            <button @click="logout" class="btn-danger px-1 sm:px-4 py-1 sm:py-2 text-sm">
              <span class="hidden sm:inline">로그아웃</span>
              <svg class="w-4 h-4 sm:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Success Message -->
        <div v-if="message"
          class="mb-6 rounded-lg bg-beige-100 dark:bg-neutral-900 p-4 border border-beige-300 dark:border-neutral-800">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-neutral-700 dark:text-neutral-300" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-neutral-700 dark:text-neutral-300">
                {{ message }}
              </p>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-8 w-8 text-neutral-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      총 참여자
                    </dt>
                    <dd class="text-lg font-medium text-gray-900 dark:text-white">
                      {{ totalParticipants }}명
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <!-- Notifications Card -->
          <button @click="openNotificationsModal"
            class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow cursor-pointer focus:outline-none focus:ring-2 focus:ring-purple-500">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0 relative">
                  <svg class="h-8 w-8 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M15 17h5l-5 5v-5zM15 17H9a2 2 0 01-2-2V5a2 2 0 012-2h6a2 2 0 012 2v10z" />
                  </svg>
                  <!-- Unread notification badge -->
                  <span v-if="unreadNotificationCount > 0"
                    class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {{ unreadNotificationCount > 9 ? '9+' : unreadNotificationCount }}
                  </span>
                </div>
                <div class="ml-5 w-0 flex-1 text-left">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      알림
                    </dt>
                    <dd class="text-lg font-medium text-gray-900 dark:text-white">
                      {{ notifications.length }}개
                      <span v-if="unreadNotificationCount > 0" class="text-sm text-purple-600 dark:text-purple-400">
                        ({{ unreadNotificationCount }}개 읽지 않음)
                      </span>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6 text-center">
            <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-neutral-500 mx-auto" xmlns="http://www.w3.org/2000/svg"
              fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
              </path>
            </svg>
            <p class="mt-2 text-gray-600 dark:text-gray-400">
              모임 목록을 불러오는 중...
            </p>
          </div>
        </div>

        <!-- Empty State for Created Meetups (keep card layout) -->
        <div v-else-if="meetups.length === 0" class="space-y-6">
          <div
            class="bg-white dark:bg-neutral-900 shadow-sm rounded-xl overflow-hidden border border-neutral-200 dark:border-neutral-800">
            <div
              class="px-4 py-5 sm:px-6 border-b border-beige-300 dark:border-neutral-800 bg-beige-200 dark:bg-neutral-800">
              <div class="flex justify-between items-center">
                <div class="flex items-center space-x-2">
                  <div class="p-2 bg-beige-200 dark:bg-neutral-800 rounded-full">
                    <svg class="w-5 h-5 text-neutral-700 dark:text-neutral-300" fill="none" stroke="currentColor"
                      viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-lg leading-6 font-medium text-black dark:text-neutral-100">
                      내가 개설한 모임
                    </h3>
                    <p class="mt-1 max-w-2xl text-sm text-neutral-700 dark:text-neutral-300">
                      아직 만든 모임이 없습니다
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div class="px-4 py-8 sm:px-6 text-center">
              <svg class="mx-auto h-12 w-12 text-neutral-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"
                fill="currentColor">
                <path
                  d="M31.2 14.4a7.2 7.2 0 11-14.4 0 7.2 7.2 0 0114.4 0zM43.2 19.2a4.8 4.8 0 11-9.6 0 4.8 4.8 0 019.6 0zM33.6 36a9.6 9.6 0 00-19.2 0v7.2h19.2V36zM14.4 19.2a4.8 4.8 0 11-9.6 0 4.8 4.8 0 019.6 0zM38.4 43.2V36a14.333 14.333 0 00-1.8-6.973A7.212 7.212 0 0145.6 36v7.2h-7.2zM11.4 29.027A14.353 14.353 0 009.6 36v7.2H2.4V36a7.2 7.2 0 019-6.973z" />
              </svg>
              <p class="mt-2 text-sm text-neutral-500 dark:text-neutral-400">
                첫 번째 모임을 만들어 사람들과 함께하는 시간을 가져보세요.
              </p>
              <div class="mt-6">
                <router-link to="/create-meetup"
                  class="inline-flex items-center justify-center text-primary-700 bg-primary-100 hover:bg-primary-200 dark:bg-primary-900 dark:text-primary-300 dark:hover:bg-primary-800 px-3 py-1.5 rounded-md text-xs font-medium transition-colors">
                  <svg class="h-5 w-5 sm:-ml-1 sm:mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"
                    fill="currentColor">
                    <path fill-rule="evenodd"
                      d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                      clip-rule="evenodd" />
                  </svg>
                  <span class="hidden sm:inline">새 모임 만들기</span>
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Meetup Cards -->
        <div v-else class="space-y-6">
          <div
            class="bg-white dark:bg-neutral-900 shadow-sm rounded-xl overflow-hidden border border-neutral-200 dark:border-neutral-800">
            <div
              class="px-4 py-5 sm:px-6 border-b border-beige-300 dark:border-neutral-800 bg-beige-200 dark:bg-neutral-800">
              <div class="flex justify-between items-center">
                <div class="flex items-center space-x-2">
                  <div class="p-2 bg-beige-200 dark:bg-neutral-800 rounded-full">
                    <svg class="w-5 h-5 text-neutral-700 dark:text-neutral-300" fill="none" stroke="currentColor"
                      viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-lg leading-6 font-medium text-black dark:text-neutral-100">
                      내가 개설한 모임
                    </h3>
                    <p class="mt-1 max-w-2xl text-sm text-neutral-700 dark:text-neutral-300">
                      {{ meetups.length }}개의 모임을 관리하고 있습니다.
                    </p>
                  </div>
                </div>
                <!-- <router-link
                  to="/create-meetup"
                  class="btn-primary text-sm leading-4"
                >
                  <svg class="-ml-0.5 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                  </svg>
                  <span class="hidden sm:inline">새 모임 만들기</span>
                  <span class="sm:hidden">새 모임</span>
                </router-link> -->
                <router-link to="/create-meetup"
                  class="inline-flex items-center justify-center text-primary-700 bg-primary-100 hover:bg-primary-200 dark:bg-primary-900 dark:text-primary-300 dark:hover:bg-primary-800 px-3 py-1.5 rounded-md text-xs font-medium transition-colors">
                  <svg class="h-5 w-5 sm:-ml-1 sm:mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"
                    fill="currentColor">
                    <path fill-rule="evenodd"
                      d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                      clip-rule="evenodd" />
                  </svg>
                  <span class="hidden sm:inline">새 모임 만들기</span>
                </router-link>
              </div>
            </div>
            <!-- Desktop view -->
            <div class="hidden sm:block divide-y divide-neutral-200 dark:divide-neutral-700">
              <div v-for="meetup in meetups" :key="meetup.id" class="px-4 py-6 sm:px-6 transition-colors duration-150">
                <div class="space-y-4">
                  <!-- Main content row -->
                  <div class="flex items-start justify-between">
                    <div class="flex items-center space-x-3 flex-1 min-w-0">
                      <div class="flex-shrink-0">
                        <div v-if="meetup.image_display_url" class="w-12 h-12 rounded-lg overflow-hidden">
                          <img :src="meetup.image_display_url" :alt="meetup.name" class="w-12 h-12 object-cover"
                            @error="handleImageError" />
                        </div>
                        <div v-else
                          class="w-12 h-12 bg-beige-200 dark:bg-neutral-800 rounded-lg flex items-center justify-center">
                          <svg class="w-7 h-7 text-neutral-600 dark:text-neutral-300" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between">
                          <div class="flex-1 min-w-0">
                            <h4 class="text-lg font-medium text-black dark:text-white truncate">
                              {{ meetup.name }}
                            </h4>
                            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                              {{ meetup.description }}
                            </p>
                          </div>
                          <div class="flex items-center space-x-2 ml-4">
                            <span :class="[
                              'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                              getMeetupStatusClass(meetup)
                            ]">
                              {{ getMeetupStatus(meetup) }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Details and hashtags row -->
                  <div class="pl-15 space-y-3">
                    <!-- Meeting details -->
                    <div class="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                      <div class="flex items-center">
                        <svg class="mr-1.5 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {{ formatDateTime(meetup.date_time) }}
                      </div>
                      <div class="flex items-center">
                        <svg class="mr-1.5 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {{ meetup.location }}
                      </div>
                      <div class="flex items-center">
                        <svg class="mr-1.5 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        {{ meetup.current_participants }}/{{ meetup.max_participants }}명
                        <span class="ml-1 text-xs text-gray-400">({{ meetup.available_spots }}석 남음)</span>
                      </div>
                    </div>

                    <!-- Hashtags and Actions row -->
                    <div class="flex items-center justify-between">
                      <!-- Hashtags -->
                      <div class="flex-1">
                        <div v-if="meetup.hashtags_list && meetup.hashtags_list.length > 0"
                          class="flex flex-wrap gap-1">
                          <span v-for="hashtag in meetup.hashtags_list" :key="hashtag"
                            class="inline-flex px-2 py-0.5 text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full">
                            {{ hashtag }}
                          </span>
                        </div>
                      </div>

                      <!-- Action buttons -->
                      <div class="flex items-center space-x-1 ml-4">
                        <button @click="editMeetup(meetup)"
                          class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md transition-colors text-blue-700 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-300 dark:hover:bg-blue-800"
                          title="수정">
                          <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                          수정
                        </button>
                        <button @click="openManageParticipants(meetup)"
                          class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md transition-colors text-orange-700 bg-orange-200 hover:bg-orange-300 dark:bg-orange-900 dark:text-orange-300 dark:hover:bg-orange-800"
                          title="참가자 관리">
                          <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                          </svg>
                          참가자 추가
                        </button>
                        <button @click="deleteMeetup(meetup.id)"
                          class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md transition-colors text-red-700 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800"
                          title="삭제">
                          <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          삭제
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Mobile view for created meetups -->
            <div class="sm:hidden space-y-4 p-4">
              <div v-for="meetup in meetups" :key="meetup.id"
                class="bg-gradient-to-r from-beige-100 to-beige-50 dark:from-neutral-800/30 dark:to-neutral-800/10 rounded-lg p-4 space-y-3 border border-beige-300 dark:border-neutral-700">
                <div class="flex justify-between items-start">
                  <div class="flex items-start space-x-3 flex-1 min-w-0">
                    <div v-if="meetup.image_display_url" class="flex-shrink-0">
                      <img :src="meetup.image_display_url" :alt="meetup.name" class="w-12 h-12 object-cover rounded-lg"
                        @error="handleImageError" />
                    </div>
                    <div class="flex-1 min-w-0">
                      <h3 class="text-sm font-medium text-black dark:text-white truncate">
                        {{ meetup.name }}
                      </h3>
                      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                        {{ meetup.description }}
                      </p>
                    </div>
                  </div>
                  <span class="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full flex-shrink-0" :class="getMeetupStatusClass(meetup)">
                    {{ getMeetupStatus(meetup) }}
                  </span>
                </div>

                <div class="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <div class="text-gray-500 dark:text-gray-400">시간</div>
                    <div class="text-gray-900 dark:text-white font-medium">
                      {{ formatDateTime(meetup.date_time) }}
                    </div>
                  </div>

                  <div>
                    <div class="text-gray-500 dark:text-gray-400">참여자</div>
                    <div class="text-gray-900 dark:text-white font-medium">
                      {{ meetup.current_participants }}/{{ meetup.max_participants }}명
                    </div>
                  </div>
                </div>

                <!-- Hashtags display for mobile -->
                <div v-if="meetup.hashtags_list && meetup.hashtags_list.length > 0" class="flex flex-wrap gap-1 mb-2">
                  <span v-for="hashtag in meetup.hashtags_list" :key="hashtag"
                    class="inline-flex px-2 py-0.5 text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full">
                    {{ hashtag }}
                  </span>
                </div>

                <div class="grid grid-cols-3 gap-2 pt-2 border-t border-beige-300 dark:border-neutral-700">
                  <button @click="editMeetup(meetup)"
                    class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors text-blue-700 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-300 dark:hover:bg-blue-800">
                    수정
                  </button>
                  <button @click="openManageParticipants(meetup)"
                    class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors text-orange-700 bg-orange-100 hover:bg-orange-200 dark:bg-orange-900 dark:text-orange-300 dark:hover:bg-orange-800">
                    참가자
                  </button>
                  <button @click="deleteMeetup(meetup.id)"
                    class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex-1 text-red-700 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800">
                    삭제
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 내 모임 목록 (등록 + 대기열) -->
        <div
          class="bg-white dark:bg-neutral-900 shadow-sm rounded-xl overflow-hidden mt-6 border border-neutral-200 dark:border-neutral-800">
          <div
            class="px-4 py-5 sm:px-6 border-b border-beige-300 dark:border-neutral-800 bg-beige-200 dark:bg-neutral-800">
            <div class="flex items-center space-x-2">
              <div class="p-2 bg-beige-200 dark:bg-neutral-800 rounded-full">
                <svg class="w-5 h-5 text-neutral-700 dark:text-neutral-300" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg leading-6 font-medium text-black dark:text-neutral-100">
                  내 모임 현황
                </h3>
                <p class="mt-1 max-w-2xl text-sm text-neutral-700 dark:text-neutral-300">
                  참가 확정 {{ registeredMeetups.length }}개, 대기 중 {{ waitlistMeetups.length }}개 총 {{ allMyMeetups.length
                  }}개의 모임
                </p>
              </div>
            </div>
          </div>

          <!-- 모임 로딩 상태 -->
          <div v-if="loadingRegistered || loadingWaitlist" class="px-4 py-5 sm:px-6 text-center">
            <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-neutral-500 mx-auto" xmlns="http://www.w3.org/2000/svg"
              fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
              </path>
            </svg>
            <p class="mt-2 text-gray-600 dark:text-gray-400">
              모임 목록을 불러오는 중...
            </p>
          </div>

          <!-- Empty State for Registered Meetups -->
          <div v-else-if="allMyMeetups.length === 0" class="px-4 py-5 sm:px-6 text-center">
            <svg class="mx-auto h-12 w-12 text-neutral-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path
                d="M34 40h10v-4a6 6 0 00-10.712-3.714M34 40H14m20 0v-4a9.971 9.971 0 00-.712-3.714M14 40H4v-4a6 6 0 0110.713-3.714M14 40v-4c0-1.313.253-2.566.713-3.714m0 0A10.003 10.003 0 0124 26c4.21 0 7.813 2.602 9.288 6.286M30 14a6 6 0 11-12 0 6 6 0 0112 0zm12 6a4 4 0 11-8 0 4 4 0 018 0zm-28 0a4 4 0 11-8 0 4 4 0 018 0z"
                stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-black dark:text-neutral-100">
              참가한 모임이 없습니다
            </h3>
            <p class="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
              관심 있는 모임에 참가 신청하거나 대기열에 등록해보세요.
            </p>
            <div class="mt-6">
              <router-link to="/dashboard" class="inline-flex items-center justify-center text-primary-700 bg-primary-100 hover:bg-primary-200 dark:bg-primary-900 dark:text-primary-300 dark:hover:bg-primary-800 px-4 py-2 rounded-md text-sm font-medium transition-colors">
                <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"
                  fill="currentColor">
                  <path
                    d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                </svg>
                모임 둘러보기
              </router-link>
            </div>
          </div>

          <!-- Desktop view for all meetups -->
          <div v-if="!loadingRegistered && !loadingWaitlist && allMyMeetups.length > 0"
            class="hidden sm:block divide-y divide-neutral-200 dark:divide-neutral-700">
            <div v-for="meetup in allMyMeetups" :key="meetup.id + '-' + meetup.status"
              class="px-4 py-6 sm:px-6 transition-colors duration-150">
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-3">
                    <div class="flex-shrink-0">
                      <div v-if="meetup.image_display_url" class="w-12 h-12 rounded-lg overflow-hidden">
                        <img :src="meetup.image_display_url" :alt="meetup.name" class="w-12 h-12 object-cover"
                          @error="handleImageError" />
                      </div>
                      <div v-else
                        :class="meetup.status === 'registered' ? 'w-12 h-12 bg-emerald-100 dark:bg-emerald-900 rounded-lg flex items-center justify-center' : 'w-12 h-12 bg-yellow-100 dark:bg-yellow-900 rounded-lg flex items-center justify-center'">
                        <svg
                          :class="meetup.status === 'registered' ? 'w-7 h-7 text-emerald-600 dark:text-emerald-400' : 'w-7 h-7 text-yellow-600 dark:text-yellow-400'"
                          fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            :d="meetup.status === 'registered' ? 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' : 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'" />
                        </svg>
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center space-x-2">
                        <h4 class="text-lg font-medium text-gray-900 dark:text-white truncate">
                          {{ meetup.name }}
                        </h4>
                        <span v-if="meetup.status === 'registered'"
                          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-beige-200 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-200">
                          참가 확정
                        </span>
                        <span v-else
                          class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                          대기 {{ meetup.position }}번째
                        </span>
                      </div>
                      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {{ meetup.description }}
                      </p>
                      <div class="mt-2 flex items-center text-sm text-gray-500 dark:text-gray-400 space-x-4">
                        <div class="flex items-center">
                          <svg class="mr-1.5 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {{ formatDateTime(meetup.date_time || meetup.meetup_date_time) }}
                        </div>
                        <div class="flex items-center">
                          <svg class="mr-1.5 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          {{ meetup.location }}
                        </div>
                        <div v-if="meetup.status === 'registered'" class="flex items-center">
                          <svg class="mr-1.5 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                          </svg>
                          {{ meetup.current_participants }} /
                          {{ meetup.max_participants }}명
                        </div>
                      </div>
                      <div class="mt-2 text-xs text-gray-400">
                        <span v-if="meetup.status === 'registered'">
                          {{ new Date(meetup.registration_date).toLocaleDateString("ko-KR") }}에 신청
                        </span>
                        <span v-else>
                          {{ new Date(meetup.waitlisted_at).toLocaleDateString("ko-KR") }}에 대기열 등록
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <span v-if="meetup.status === 'registered'" :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    meetup.is_full
                      ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                      : 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200',
                  ]">
                    {{ meetup.is_full ? "마감" : "모집중" }}
                  </span>
                  <button v-if="meetup.status === 'registered'"
                    @click="unregisterFromMeetup(meetup.id, meetup.registration_id)"
                    class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-red-700 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800 rounded-md transition-colors"
                    title="참가 취소">
                    <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    취소
                  </button>
                  <button v-else @click="removeFromWaitlist(meetup.meetup, meetup.id)"
                    class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-orange-700 bg-orange-100 hover:bg-orange-200 dark:bg-orange-900 dark:text-orange-300 dark:hover:bg-orange-800 rounded-md transition-colors"
                    title="대기열 취소">
                    <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    대기 취소
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Mobile view for all meetups -->
          <div v-if="!loadingRegistered && !loadingWaitlist && allMyMeetups.length > 0" class="sm:hidden space-y-4 p-4">
            <div v-for="meetup in allMyMeetups" :key="meetup.id + '-' + meetup.status"
              :class="meetup.status === 'registered' ? 'bg-gradient-to-r from-beige-100 to-beige-50 dark:from-neutral-800/30 dark:to-neutral-800/10 rounded-lg p-4 space-y-3 border border-beige-300 dark:border-neutral-700' : 'bg-gradient-to-r from-beige-100 to-beige-50 dark:from-neutral-800/30 dark:to-neutral-800/10 rounded-lg p-4 space-y-3 border border-beige-300 dark:border-neutral-700'">
              <div class="flex justify-between items-start">
                <div class="flex items-start space-x-3 flex-1 min-w-0">
                  <div v-if="meetup.image_display_url" class="flex-shrink-0">
                    <img :src="meetup.image_display_url" :alt="meetup.name" class="w-12 h-12 object-cover rounded-lg"
                      @error="handleImageError" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center space-x-2">
                      <h3 class="text-sm font-medium text-black dark:text-white truncate">
                        {{ meetup.name }}
                      </h3>
                      <span v-if="meetup.status === 'registered'"
                        class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-beige-200 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-200 flex-shrink-0">
                        참가 확정
                      </span>
                      <span v-else
                        class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 flex-shrink-0">
                        대기 {{ meetup.position }}번째
                      </span>
                    </div>
                    <p v-if="meetup.description" class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                      {{ meetup.description }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <div class="text-gray-500 dark:text-gray-400">시간</div>
                  <div class="text-gray-900 dark:text-white font-medium">
                    {{ formatDateTime(meetup.date_time || meetup.meetup_date_time) }}
                  </div>
                </div>

                <div v-if="meetup.location">
                  <div class="text-gray-500 dark:text-gray-400">장소</div>
                  <div class="text-gray-900 dark:text-white font-medium truncate">
                    {{ meetup.location }}
                  </div>
                </div>

                <div v-if="meetup.creator_name">
                  <div class="text-gray-500 dark:text-gray-400">생성자</div>
                  <div class="text-gray-900 dark:text-white font-medium">
                    {{ meetup.creator_name }}
                  </div>
                </div>

                <div v-if="meetup.status === 'registered'">
                  <div class="text-gray-500 dark:text-gray-400">참여자</div>
                  <div class="text-gray-900 dark:text-white font-medium">
                    {{ meetup.current_participants }}/{{ meetup.max_participants }}명
                  </div>
                </div>

                <div v-if="meetup.status === 'waitlisted'">
                  <div class="text-gray-500 dark:text-gray-400">대기 등록일</div>
                  <div class="text-gray-900 dark:text-white font-medium">
                    {{ new Date(meetup.waitlisted_at).toLocaleDateString("ko-KR") }}
                  </div>
                </div>
              </div>

              <div class="flex space-x-2 pt-2">
                <button v-if="meetup.status === 'registered'"
                  @click="unregisterFromMeetup(meetup.id, meetup.registration_id)" :disabled="loadingRegistered"
                  class="text-red-700 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800 px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex-1 disabled:opacity-50 disabled:cursor-not-allowed">
                  참가 취소
                </button>
                <button v-else @click="removeFromWaitlist(meetup.meetup, meetup.id)" :disabled="loadingWaitlist"
                  class="text-orange-700 bg-orange-100 hover:bg-orange-200 dark:bg-orange-900 dark:text-orange-300 dark:hover:bg-orange-800 px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex-1 disabled:opacity-50 disabled:cursor-not-allowed">
                  대기 취소
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeEditModal">
      <div class="bg-beige-50 dark:bg-neutral-800 rounded-2xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-hidden">
        <!-- Modal Header -->
        <div class="relative p-6 border-b border-neutral-200 dark:border-neutral-600 bg-beige-200 dark:bg-neutral-700">
          <!-- Close Button -->
          <button @click="closeEditModal" class="absolute top-4 right-4 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
          
          <!-- Title -->
          <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 pr-8">모임 수정</h3>
        </div>

        <!-- Modal Content with Scroll -->
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
        <form @submit.prevent="updateMeetup" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">모임 이름</label>
            <input v-model="editForm.name" type="text" required
              class="block w-full px-4 py-3 border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white text-base" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">설명</label>
            <textarea v-model="editForm.description" rows="4"
              class="block w-full px-4 py-3 border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white text-base"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">장소</label>
            <input v-model="editForm.location" type="text" required
              class="block w-full px-4 py-3 border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white text-base" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">시작 시간</label>
            <input v-model="editForm.date_time" type="datetime-local" required
              class="block w-full px-4 py-3 border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white text-base" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">모임 진행 시간 (시간)</label>
            <input v-model.number="editForm.duration" type="number" min="0.5" step="0.5" placeholder="예: 2 (2시간)"
              required
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">최대 참여 인원</label>
            <input v-model.number="editForm.max_participants" type="number" min="1" required
              class="block w-full px-4 py-3 border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white text-base" />
          </div>

          <!-- Hashtags Section -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              해시태그
            </label>
            <input v-model="editForm.hashtags" type="text" placeholder="#개발,#네트워킹,#스타트업 (쉼표로 구분)"
              class="block w-full px-4 py-3 border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 text-base" />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              해시태그를 쉼표로 구분하여 입력하세요. 예: #개발,#네트워킹,#스타트업
            </p>
          </div>

          <!-- Image Upload Section -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              모임 이미지
            </label>
            <div class="space-y-3">
              <!-- Current Image Display -->
              <div v-if="editForm.currentImageUrl" class="relative inline-block">
                <img :src="editForm.currentImageUrl" alt="현재 이미지"
                  class="h-20 w-32 object-cover rounded-lg border border-gray-300 dark:border-gray-600"
                  @error="handleImageError" />
                <span class="absolute top-0 left-0 bg-neutral-700 text-white text-xs px-1 rounded">현재</span>
              </div>

              <!-- New Image Options -->
              <div class="flex flex-col space-y-2">
                <!-- File Upload -->
                <div>
                  <label for="edit-image-upload"
                    class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                    새 이미지 파일 업로드
                  </label>
                  <input type="file" id="edit-image-upload" ref="editImageInput" @change="handleEditImageUpload"
                    accept="image/*"
                    class="block w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:font-medium file:bg-neutral-100 file:text-neutral-700 hover:file:bg-neutral-200 dark:file:bg-neutral-800 dark:file:text-neutral-300" />
                </div>

                <!-- URL Input -->
                <div>
                  <label for="edit-image-url" class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                    또는 새 이미지 URL
                  </label>
                  <input type="url" id="edit-image-url" v-model="editForm.imageUrl"
                    placeholder="https://example.com/image.jpg"
                    class="block w-full px-2 py-1 border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 text-sm" />
                </div>
              </div>

              <!-- New Image Preview -->
              <div v-if="editImagePreview" class="relative inline-block">
                <img :src="editImagePreview" alt="새 이미지 미리보기"
                  class="h-20 w-32 object-cover rounded-lg border border-gray-300 dark:border-gray-600"
                  @error="handleImageError" />
                <span class="absolute top-0 left-0 bg-neutral-700 text-white text-xs px-1 rounded">새 이미지</span>
                <button type="button" @click="removeEditImage"
                  class="absolute -top-1 -right-1 bg-red-500 hover:bg-red-600 text-white rounded-full p-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button type="button" @click="closeEditModal"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600">
              취소
            </button>
            <button type="submit" :disabled="updating"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-neutral-400 hover:bg-neutral-500 dark:bg-neutral-700 dark:hover:bg-neutral-600 disabled:opacity-50 disabled:cursor-not-allowed">
              <svg v-if="updating" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg"
                fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              {{ updating ? "수정 중..." : "수정 완료" }}
            </button>
          </div>
        </form>
        </div>
      </div>
    </div>

    <!-- Manage Participants Modal -->
    <div v-if="showParticipantsModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeParticipantsModal">
      <div class="bg-beige-50 dark:bg-neutral-800 rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <!-- Modal Header -->
        <div class="relative p-6 border-b border-neutral-200 dark:border-neutral-600 bg-beige-200 dark:bg-neutral-700">
          <!-- Close Button -->
          <button @click="closeParticipantsModal"
            class="absolute top-4 right-4 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>

          <!-- Title -->
          <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 pr-8">참가자 관리: {{ selectedMeetup?.name
            }}</h3>
          <p class="text-sm text-neutral-500 dark:text-neutral-400 mt-1">
            {{ selectedMeetup?.current_participants }} / {{ selectedMeetup?.max_participants }}명 등록
          </p>
        </div>

        <!-- Modal Content with Scroll -->
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">

          <!-- Manual Registration Form -->
          <div class="mb-6">
            <h4 class="text-md font-medium text-neutral-900 dark:text-neutral-100 mb-3">
              수동 참가자 등록
            </h4>
            <p class="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
              다른 채널을 통해 등록한 참가자를 수동으로 추가할 수 있습니다.
            </p>
            <form @submit.prevent="addParticipantManually" class="space-y-3">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    이름 *
                  </label>
                  <input v-model="manualRegistrationForm.name" type="text" required placeholder="참가자 이름"
                    class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white sm:text-sm" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    이메일 *
                  </label>
                  <input v-model="manualRegistrationForm.email" type="email" required placeholder="참가자 이메일"
                    class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white sm:text-sm" />
                </div>
              </div>
              <div class="flex justify-end">
                <button type="submit" :disabled="addingParticipant"
                  class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-neutral-700 hover:bg-neutral-800 dark:bg-neutral-700 dark:hover:bg-neutral-600 disabled:opacity-50 disabled:cursor-not-allowed">
                  <svg v-if="addingParticipant" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                    xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                  </svg>
                  {{ addingParticipant ? "추가 중..." : "참가자 추가" }}
                </button>
              </div>
            </form>
          </div>


          <!-- Participants List -->
          <div class="mb-6">
            <h4 class="text-md font-medium text-neutral-900 dark:text-neutral-100 mb-3">
              등록된 참가자
            </h4>

            <!-- Loading State -->
            <div v-if="loadingParticipants" class="text-center py-4">
              <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-neutral-500 mx-auto" xmlns="http://www.w3.org/2000/svg"
                fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              <p class="mt-2 text-gray-600 dark:text-gray-400">참가자 목록을 불러오는 중...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="participants.length === 0" class="text-center py-4">
              <p class="text-gray-500 dark:text-gray-400">등록된 참가자가 없습니다.</p>
            </div>

            <!-- Participants List -->
            <div v-else class="space-y-2 max-h-60 overflow-y-auto">
              <div v-for="participant in participants" :key="participant.id"
                class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-600 rounded-lg">
                <div class="flex-1">
                  <div class="flex items-center space-x-3">
                    <div class="flex-shrink-0">
                      <div
                        class="w-8 h-8 bg-beige-200 dark:bg-neutral-800 rounded-full flex items-center justify-center">
                        <svg class="w-4 h-4 text-neutral-700 dark:text-neutral-300" fill="none" viewBox="0 0 24 24"
                          stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {{ participant.user_name }}
                      </p>
                      <p class="text-sm text-gray-500 dark:text-gray-400 truncate">
                        {{ participant.user_email }}
                      </p>
                    </div>
                  </div>
                </div>
                <button @click="removeParticipant(participant.id)" :disabled="removingParticipant"
                  class="p-2 text-red-600 hover:text-red-900 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900 rounded-md disabled:opacity-50"
                  title="참가자 제거">
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Send Notification Section -->
          <div class="bg-white dark:bg-gray-700 rounded-lg p-4 mt-4">
            <h4 class="text-md font-medium text-black dark:text-white mb-3">
              참가자에게 알림 보내기
            </h4>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              모든 참가자에게 알림을 보냅니다.
            </p>
            <form @submit.prevent="sendNotificationToParticipants" class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  제목 *
                </label>
                <input v-model="notificationForm.title" type="text" required placeholder="알림 제목"
                  class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white sm:text-sm" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  메시지 *
                </label>
                <textarea v-model="notificationForm.message" required rows="3" placeholder="알림 내용"
                  class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-neutral-500 focus:border-neutral-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white sm:text-sm"></textarea>
              </div>
              <div class="flex justify-end">
                <button type="submit" :disabled="sendingNotification || participants.length === 0"
                  class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-neutral-700 hover:bg-neutral-800 dark:bg-neutral-700 dark:hover:bg-neutral-600 disabled:opacity-50 disabled:cursor-not-allowed">
                  <svg v-if="sendingNotification" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                    xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                  </svg>
                  {{ sendingNotification ? "전송 중..." : `알림 보내기 (${participants.length}명)` }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Notifications Modal - Table Style with Detail View -->
    <div v-if="showNotificationsModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click.self="closeNotificationsModal">
      <div
        class="relative top-4 mx-auto p-0 max-w-6xl bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 max-h-[90vh] flex flex-col">
        <!-- Modal Header -->
        <div
          class="bg-beige-100 dark:bg-neutral-900 px-6 py-4 rounded-t-lg border-b border-beige-300 dark:border-neutral-800">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-xl font-semibold text-black dark:text-white">알림 관리</h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                총 {{ notificationPagination.total }}개 알림 ({{ unreadNotificationCount }}개 읽지 않음)
              </p>
            </div>
            <div class="flex items-center space-x-2">
              <button v-if="unreadNotificationCount > 0" @click="markAllNotificationsRead"
                :disabled="loadingNotifications"
                class="bg-beige-200 hover:bg-beige-300 dark:bg-neutral-800 dark:hover:bg-neutral-700 text-neutral-800 dark:text-neutral-200 px-3 py-1.5 rounded-md text-sm font-medium transition-colors disabled:opacity-50 flex items-center space-x-1">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>모두 읽음</span>
              </button>
              <button @click="closeNotificationsModal"
                class="w-6 h-6 flex items-center justify-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 focus:outline-none rounded-full hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Modal Body -->
        <div class="flex-1 overflow-y-auto">
          <!-- Selected Notification Detail View -->
          <div v-if="selectedNotification"
            class="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-full flex items-center justify-center"
                  :class="'bg-beige-200 dark:bg-neutral-800'">
                  <svg v-if="selectedNotification.notification_type === 'waitlist_promotion'"
                    class="w-5 h-5 text-neutral-700 dark:text-neutral-300" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <svg v-else class="w-5 h-5 text-neutral-700 dark:text-neutral-300" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h4 class="text-lg font-semibold text-black dark:text-white">{{ selectedNotification.title }}</h4>
                  <div class="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400 mt-1">
                    <span>{{ selectedNotification.time_ago }}</span>
                    <span v-if="selectedNotification.meetup_name"
                      class="text-neutral-800 dark:text-neutral-300 font-medium">
                      {{ selectedNotification.meetup_name }}
                    </span>
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                      :class="'bg-beige-200 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-300'">
                      {{ selectedNotification.notification_type === 'waitlist_promotion' ? '대기열 승격' : '일반 알림' }}
                    </span>
                  </div>
                </div>
              </div>
              <button @click="closeNotificationDetail"
                class="w-5 h-5 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
              <p class="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">{{
                selectedNotification.message }}</p>
            </div>
          </div>

          <div class="p-6">
            <!-- Loading state -->
            <div v-if="loadingNotifications" class="py-12 text-center">
              <svg class="animate-spin -ml-1 mr-3 h-12 w-12 text-neutral-500 mx-auto" xmlns="http://www.w3.org/2000/svg"
                fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              <p class="mt-4 text-gray-600 dark:text-gray-400">알림을 불러오는 중...</p>
            </div>

            <!-- Empty state -->
            <div v-else-if="paginatedNotifications.length === 0" class="py-12 text-center">
              <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M15 17h5l-5 5v-5zM15 17H9a2 2 0 01-2-2V5a2 2 0 012-2h6a2 2 0 012 2v10z" />
              </svg>
              <h3 class="mt-4 text-lg font-medium text-black dark:text-white">알림이 없습니다</h3>
              <p class="mt-2 text-gray-500 dark:text-gray-400">
                대기열에서 승격되거나 모임 관련 알림이 있을 때 여기에 표시됩니다.
              </p>
            </div>

            <!-- Notifications Table -->
            <div v-else class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table class="min-w-full divide-y divide-gray-300 dark:divide-gray-600">
                <!-- Table Header -->
                <thead class="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th scope="col"
                      class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 dark:text-white sm:pl-6">상태
                    </th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-white">유형
                    </th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-white">제목
                    </th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-white">모임
                    </th>
                    <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-white">시간
                    </th>
                    <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                      <span class="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <!-- Table Body -->
                <tbody class="divide-y divide-gray-200 dark:divide-gray-600 bg-white dark:bg-gray-800">
                  <tr v-for="notification in paginatedNotifications" :key="notification.id"
                    class="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                    :class="{ 'bg-beige-100 dark:bg-neutral-900': !notification.is_read }"
                    @click="selectNotification(notification)">
                    <!-- Status -->
                    <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm sm:pl-6">
                      <div class="flex items-center">
                        <div v-if="!notification.is_read" class="w-2 h-2 bg-neutral-500 rounded-full mr-3"></div>
                        <div v-else class="w-2 h-2 bg-gray-300 dark:bg-gray-600 rounded-full mr-3"></div>
                        <span class="text-xs font-medium px-2 py-1 rounded-full" :class="!notification.is_read
                          ? 'bg-beige-200 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-300'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-300'">
                          {{ !notification.is_read ? '읽지 않음' : '읽음' }}
                        </span>
                      </div>
                    </td>
                    <!-- Type -->
                    <td class="whitespace-nowrap px-3 py-4 text-sm">
                      <div class="flex items-center">
                        <div class="w-8 h-8 rounded-full flex items-center justify-center mr-3"
                          :class="'bg-beige-200 dark:bg-neutral-800'">
                          <svg v-if="notification.notification_type === 'waitlist_promotion'"
                            class="w-4 h-4 text-neutral-700 dark:text-neutral-300" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <svg v-else class="w-4 h-4 text-neutral-700 dark:text-neutral-300" fill="none"
                            viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <span class="text-sm text-gray-900 dark:text-white">
                          {{ notification.notification_type === 'waitlist_promotion' ? '대기열 승격' : '일반 알림' }}
                        </span>
                      </div>
                    </td>
                    <!-- Title -->
                    <td class="px-3 py-4 text-sm text-gray-900 dark:text-white">
                      <div class="font-medium truncate max-w-xs" :title="notification.title">{{ notification.title }}
                      </div>
                    </td>
                    <!-- Meetup -->
                    <td class="px-3 py-4 text-sm text-gray-500 dark:text-gray-400">
                      <span v-if="notification.meetup_name"
                        class="truncate max-w-xs text-neutral-800 dark:text-neutral-300"
                        :title="notification.meetup_name">
                        {{ notification.meetup_name }}
                      </span>
                      <span v-else>-</span>
                    </td>
                    <!-- Time -->
                    <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {{ notification.time_ago }}
                    </td>
                    <!-- Actions -->
                    <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <button v-if="!notification.is_read" @click.stop="markNotificationRead(notification.id)"
                        class="text-neutral-800 hover:text-neutral-900 dark:text-neutral-300 dark:hover:text-neutral-100">
                        읽음 표시
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <div v-if="notificationPagination.total > notificationPagination.per_page"
              class="mt-6 flex items-center justify-between border-t border-gray-200 dark:border-gray-700 pt-6">
              <div class="flex-1 flex justify-between sm:hidden">
                <!-- Mobile pagination buttons -->
                <button @click="goToPage(notificationPagination.current_page - 1)"
                  :disabled="notificationPagination.current_page <= 1"
                  class="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                  이전
                </button>
                <button @click="goToPage(notificationPagination.current_page + 1)"
                  :disabled="notificationPagination.current_page >= notificationPagination.total_pages"
                  class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                  다음
                </button>
              </div>

              <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p class="text-sm text-gray-700 dark:text-gray-300">
                    총 <span class="font-medium">{{ notificationPagination.total }}</span>개 중
                    <span class="font-medium">{{ (notificationPagination.current_page - 1) *
                      notificationPagination.per_page + 1 }}</span> -
                    <span class="font-medium">{{ Math.min(notificationPagination.current_page *
                      notificationPagination.per_page, notificationPagination.total) }}</span>개 표시
                  </p>
                </div>
                <div>
                  <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <!-- Previous button -->
                    <button @click="goToPage(notificationPagination.current_page - 1)"
                      :disabled="notificationPagination.current_page <= 1"
                      class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                      <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd"
                          d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                          clip-rule="evenodd" />
                      </svg>
                    </button>

                    <!-- Page numbers -->
                    <button v-for="page in getVisiblePages()" :key="page" @click="goToPage(page)" :class="[
                      'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                      page === notificationPagination.current_page
                        ? 'z-10 bg-beige-100 dark:bg-neutral-900 border-beige-300 text-neutral-800 dark:text-neutral-300'
                        : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600'
                    ]">
                      {{ page }}
                    </button>

                    <!-- Next button -->
                    <button @click="goToPage(notificationPagination.current_page + 1)"
                      :disabled="notificationPagination.current_page >= notificationPagination.total_pages"
                      class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                      <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd"
                          d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                          clip-rule="evenodd" />
                      </svg>
                    </button>
                  </nav>
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
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { fetchWithCSRF } from "@/utils/csrf";
import ThemeToggle from "@/components/ThemeToggle.vue";

export default {
  name: "SettingsView",
  components: {
    ThemeToggle,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();
    const meetups = ref([]);
    const registeredMeetups = ref([]);
    const waitlistMeetups = ref([]);
    const loading = ref(false);
    const loadingRegistered = ref(false);
    const loadingWaitlist = ref(false);
    const message = ref("");
    const showEditModal = ref(false);
    const editForm = ref({});
    const updating = ref(false);
    const currentEditId = ref(null);
    const editImageInput = ref(null);
    const editImagePreview = ref('');

    // Participants management
    const showParticipantsModal = ref(false);
    const selectedMeetup = ref(null);
    const participants = ref([]);
    const loadingParticipants = ref(false);
    const addingParticipant = ref(false);
    const removingParticipant = ref(false);
    const manualRegistrationForm = ref({
      name: '',
      email: ''
    });

    // Notification sending
    const notificationForm = ref({
      title: '',
      message: ''
    });
    const sendingNotification = ref(false);

    // Notifications
    const notifications = ref([]);
    const loadingNotifications = ref(false);
    const showNotificationsModal = ref(false);
    const selectedNotification = ref(null);

    // Pagination for notifications
    const notificationPagination = ref({
      current_page: 1,
      per_page: 10, // Table rows per page
      total: 0,
      total_pages: 0
    });

    const unreadNotificationCount = computed(() => {
      return notifications.value.filter(n => !n.is_read).length;
    });

    const paginatedNotifications = computed(() => {
      const start = (notificationPagination.value.current_page - 1) * notificationPagination.value.per_page;
      const end = start + notificationPagination.value.per_page;
      return notifications.value.slice(start, end);
    });

    // Computed values for stats
    const totalParticipants = computed(() => {
      return meetups.value.reduce(
        (sum, meetup) => sum + meetup.current_participants,
        0
      );
    });

    const upcomingMeetups = computed(() => {
      const now = new Date();
      return meetups.value.filter((meetup) => {
        const meetupDate = new Date(meetup.date_time);
        return meetupDate > now;
      }).length;
    });

    const averageParticipation = computed(() => {
      if (meetups.value.length === 0) return 0;
      const totalCapacity = meetups.value.reduce(
        (sum, meetup) => sum + meetup.max_participants,
        0
      );
      if (totalCapacity === 0) return 0;
      return Math.round((totalParticipants.value / totalCapacity) * 100);
    });

    const allMyMeetups = computed(() => {
      const registered = registeredMeetups.value.map(meetup => ({
        ...meetup,
        status: 'registered'
      }));

      const waitlisted = waitlistMeetups.value.map(waitlist => ({
        ...waitlist,
        id: waitlist.meetup,
        name: waitlist.meetup_name,
        date_time: waitlist.meetup_date_time,
        description: '', // Waitlist doesn't include description
        location: '', // Waitlist doesn't include location  
        status: 'waitlisted',
        position: waitlist.position
      }));

      return [...registered, ...waitlisted].sort((a, b) =>
        new Date(a.date_time || a.meetup_date_time) - new Date(b.date_time || b.meetup_date_time)
      );
    });

    // Helper function to check if meetup is in the past
    const isMeetupPast = (meetup) => {
      const now = new Date()
      const meetupDate = new Date(meetup.date_time)
      const endDate = meetup.end_time ? new Date(meetup.end_time) : meetupDate
      return endDate < now
    }

    // Helper function to get meetup status
    const getMeetupStatus = (meetup) => {
      if (isMeetupPast(meetup)) {
        return '종료'
      } else if (meetup.is_full) {
        return '마감'
      } else {
        return '모집중'
      }
    }

    // Helper function to get status class
    const getMeetupStatusClass = (meetup) => {
      const status = getMeetupStatus(meetup)
      if (status === '종료') {
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
      } else if (status === '마감') {
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      } else {
        return 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
      }
    }

    onMounted(() => {
      if (route.query.message) {
        message.value = route.query.message;
        setTimeout(() => {
          message.value = "";
        }, 5000);
      }
      loadMeetups();
      loadRegisteredMeetups();
      loadWaitlistMeetups();
      loadNotifications();
    });

    const loadMeetups = async () => {
      loading.value = true;
      try {
        const response = await fetch("/api/my-meetups/", {
          credentials: "include",
        });
        if (response.ok) {
          meetups.value = await response.json();
        }
      } catch (error) {
        console.error("모임 목록을 불러오는데 실패했습니다:", error);
      } finally {
        loading.value = false;
      }
    };

    const loadRegisteredMeetups = async () => {
      loadingRegistered.value = true;
      try {
        const response = await fetch("/api/registrations/", {
          credentials: "include",
        });
        if (response.ok) {
          const allRegistrations = await response.json();
          // Filter registrations for current user and get meetup details
          const userRegistrations = allRegistrations.filter(
            (reg) => reg.user === authStore.user?.id
          );

          // Get meetup details for each registration
          const meetupPromises = userRegistrations.map(async (reg) => {
            const meetupResponse = await fetch(`/api/meetups/${reg.meetup}/`, {
              credentials: "include",
            });
            if (meetupResponse.ok) {
              const meetupData = await meetupResponse.json();
              return {
                ...meetupData,
                registration_date: reg.registered_at,
                registration_id: reg.id,
              };
            }
            return null;
          });

          const meetupsData = await Promise.all(meetupPromises);
          registeredMeetups.value = meetupsData.filter(
            (meetup) => meetup !== null
          );
        }
      } catch (error) {
        console.error("등록한 모임 목록을 불러오는데 실패했습니다:", error);
      } finally {
        loadingRegistered.value = false;
      }
    };

    const loadWaitlistMeetups = async () => {
      loadingWaitlist.value = true;
      try {
        const response = await fetchWithCSRF("/api/my-waitlists/", {
          credentials: "include",
        });
        if (response.ok) {
          const waitlistData = await response.json();
          waitlistMeetups.value = waitlistData;
        }
      } catch (error) {
        console.error("대기열 목록을 불러오는데 실패했습니다:", error);
      } finally {
        loadingWaitlist.value = false;
      }
    };

    // Notification functions
    const loadNotifications = async () => {
      loadingNotifications.value = true;
      try {
        const response = await fetchWithCSRF("/api/notifications/", {
          credentials: "include",
        });
        if (response.ok) {
          const data = await response.json();
          notifications.value = data.notifications || [];

          // Update pagination data
          notificationPagination.value.total = notifications.value.length;
          notificationPagination.value.total_pages = Math.ceil(notifications.value.length / notificationPagination.value.per_page);

          // Reset to first page if current page is beyond total pages
          if (notificationPagination.value.current_page > notificationPagination.value.total_pages) {
            notificationPagination.value.current_page = 1;
          }
        }
      } catch (error) {
        console.error("알림 목록을 불러오는데 실패했습니다:", error);
      } finally {
        loadingNotifications.value = false;
      }
    };

    const markNotificationRead = async (notificationId) => {
      try {
        const response = await fetchWithCSRF(`/api/notifications/${notificationId}/read/`, {
          method: 'POST',
          credentials: "include",
        });
        if (response.ok) {
          // Update local state
          const notification = notifications.value.find(n => n.id === notificationId);
          if (notification) {
            notification.is_read = true;
          }
        }
      } catch (error) {
        console.error("알림 읽음 처리에 실패했습니다:", error);
      }
    };

    const markAllNotificationsRead = async () => {
      try {
        const response = await fetchWithCSRF("/api/notifications/mark-all-read/", {
          method: 'POST',
          credentials: "include",
        });
        if (response.ok) {
          // Update local state
          notifications.value.forEach(notification => {
            notification.is_read = true;
          });
        }
      } catch (error) {
        console.error("모든 알림 읽음 처리에 실패했습니다:", error);
      }
    };

    const deleteNotification = async (notificationId) => {
      if (confirm("이 알림을 삭제하시겠습니까?")) {
        try {
          const response = await fetchWithCSRF(`/api/notifications/${notificationId}/delete/`, {
            method: 'DELETE',
            credentials: "include",
          });
          if (response.ok) {
            // Remove from local state
            notifications.value = notifications.value.filter(n => n.id !== notificationId);
          }
        } catch (error) {
          console.error("알림 삭제에 실패했습니다:", error);
        }
      }
    };

    const openNotificationsModal = () => {
      showNotificationsModal.value = true;
    };

    const closeNotificationsModal = () => {
      showNotificationsModal.value = false;
      selectedNotification.value = null; // Clear selection when modal closes
    };

    const selectNotification = (notification) => {
      selectedNotification.value = notification;
      // Mark as read when selected
      if (!notification.is_read) {
        markNotificationRead(notification.id);
      }
    };

    const closeNotificationDetail = () => {
      selectedNotification.value = null;
    };

    // Pagination functions
    const goToPage = (page) => {
      if (page >= 1 && page <= notificationPagination.value.total_pages) {
        notificationPagination.value.current_page = page;
      }
    };

    const getVisiblePages = () => {
      const current = notificationPagination.value.current_page;
      const total = notificationPagination.value.total_pages;
      const visible = [];

      if (total <= 7) {
        // Show all pages if total is 7 or less
        for (let i = 1; i <= total; i++) {
          visible.push(i);
        }
      } else {
        // Show smart pagination
        if (current <= 4) {
          // Show first 5 pages + last page
          for (let i = 1; i <= 5; i++) {
            visible.push(i);
          }
          if (total > 6) {
            visible.push('...');
            visible.push(total);
          }
        } else if (current >= total - 3) {
          // Show first page + last 5 pages
          visible.push(1);
          if (total > 6) {
            visible.push('...');
          }
          for (let i = total - 4; i <= total; i++) {
            visible.push(i);
          }
        } else {
          // Show first page + current-1, current, current+1 + last page
          visible.push(1);
          visible.push('...');
          for (let i = current - 1; i <= current + 1; i++) {
            visible.push(i);
          }
          visible.push('...');
          visible.push(total);
        }
      }

      return visible.filter(page => page !== '...' || visible.indexOf(page) === visible.lastIndexOf(page));
    };

    const removeFromWaitlist = async (meetupId, waitlistId) => {
      if (confirm("정말로 이 모임 대기열에서 나가시겠습니까?")) {
        try {
          const response = await fetchWithCSRF(
            `/api/meetups/${meetupId}/waitlist/remove/`,
            {
              method: "DELETE",
            }
          );
          if (response.ok) {
            message.value = "대기열에서 성공적으로 제거되었습니다.";
            setTimeout(() => {
              message.value = "";
            }, 3000);
            await loadWaitlistMeetups(); // Refresh waitlist
          }
        } catch (error) {
          console.error("대기열 제거 실패:", error);
          alert("대기열 제거에 실패했습니다.");
        }
      }
    };

    const unregisterFromMeetup = async (meetupId, registrationId) => {
      if (confirm("정말로 이 모임 참가를 취소하시겠습니까?")) {
        try {
          const response = await fetchWithCSRF(
            `/api/meetups/${meetupId}/unregister/`,
            {
              method: "DELETE",
            }
          );

          if (response.ok) {
            await loadRegisteredMeetups();
            message.value = "모임 참가가 성공적으로 취소되었습니다";
            setTimeout(() => {
              message.value = "";
            }, 3000);
          }
        } catch (error) {
          console.error("모임 참가 취소에 실패했습니다:", error);
        }
      }
    };

    const formatDateTime = (dateTimeStr) => {
      const date = new Date(dateTimeStr);
      return date.toLocaleString("ko-KR", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    const editMeetup = (meetup) => {
      
      // Calculate duration from start and end time
      let duration = 2; // default 2 hours
      if (meetup.date_time && meetup.end_time) {
        const startTime = new Date(meetup.date_time);
        const endTime = new Date(meetup.end_time);
        duration = (endTime - startTime) / (1000 * 60 * 60); // convert to hours
      }

      // Convert date_time to local datetime-local format
      let localDateTime = "";
      if (meetup.date_time) {
        const date = new Date(meetup.date_time);
        // Convert to local time for datetime-local input
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        localDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
      }

      editForm.value = {
        name: meetup.name,
        description: meetup.description,
        location: meetup.location,
        date_time: localDateTime,
        duration: duration,
        max_participants: meetup.max_participants,
        hashtags: meetup.hashtags || '',
        currentImageUrl: meetup.image_display_url,
        imageUrl: '',
        imageFile: null,
      };
      currentEditId.value = meetup.id;
      showEditModal.value = true;
    };

    const closeEditModal = () => {
      showEditModal.value = false;
      editForm.value = {};
      currentEditId.value = null;
      editImagePreview.value = '';
      if (editImageInput.value) {
        editImageInput.value.value = '';
      }
    };

    const updateMeetup = async () => {
      updating.value = true;
      try {
        // Calculate end time from start time and duration
        const startTime = new Date(editForm.value.date_time);
        const endTime = new Date(
          startTime.getTime() + editForm.value.duration * 60 * 60 * 1000
        );

        // Prepare the data to send to the backend
        const updateData = {
          name: editForm.value.name,
          description: editForm.value.description,
          location: editForm.value.location,
          date_time: startTime.toISOString(),
          end_time: endTime.toISOString(),
          max_participants: editForm.value.max_participants,
          hashtags: editForm.value.hashtags,
        };

        // Add image URL if provided and no file is selected
        if (editForm.value.imageUrl && !editForm.value.imageFile) {
          updateData.image_url = editForm.value.imageUrl;
        }

        // Use FormData if there's an image file, otherwise JSON
        let response;
        if (editForm.value.imageFile) {
          const formData = new FormData();

          // Add all meetup data to FormData
          Object.keys(updateData).forEach(key => {
            formData.append(key, updateData[key]);
          });

          // Add image file
          formData.append('image', editForm.value.imageFile);

          response = await fetchWithCSRF(
            `/api/meetups/${currentEditId.value}/`,
            {
              method: "PUT",
              body: formData
            }
          );
        } else {
          response = await fetchWithCSRF(
            `/api/meetups/${currentEditId.value}/`,
            {
              method: "PUT",
              body: JSON.stringify(updateData),
            }
          );
        }

        if (response.ok) {
          await loadMeetups();
          closeEditModal();
          message.value = "모임이 성공적으로 수정되었습니다";
          setTimeout(() => {
            message.value = "";
          }, 3000);
        }
      } catch (error) {
        console.error("수정에 실패했습니다:", error);
      } finally {
        updating.value = false;
      }
    };

    const deleteMeetup = async (meetupId) => {
      
      if (
        confirm(
          "정말로 이 모임을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."
        )
      ) {
        try {
          const response = await fetchWithCSRF(`/api/meetups/${meetupId}/`, {
            method: "DELETE",
          });

          if (response.ok) {
            await loadMeetups();
            message.value = "모임이 성공적으로 삭제되었습니다";
            setTimeout(() => {
              message.value = "";
            }, 3000);
          }
        } catch (error) {
          console.error("모임 삭제에 실패했습니다:", error);
          message.value = "모임 삭제에 실패했습니다. 다시 시도해주세요.";
          setTimeout(() => {
            message.value = "";
          }, 3000);
        }
      }
    };

    const logout = async () => {
      await authStore.logout();
      router.push("/login");
    };

    const handleImageError = (event) => {
      event.target.style.display = 'none';
    };

    const handleEditImageUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
        // Check file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
          alert('이미지 파일 크기가 너무 큽니다. 5MB 이하의 파일을 선택해주세요.');
          return;
        }

        // Check file type
        if (!file.type.startsWith('image/')) {
          alert('이미지 파일만 업로드 가능합니다.');
          return;
        }

        editForm.value.imageFile = file;
        editForm.value.imageUrl = ''; // Clear URL when file is selected

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
          editImagePreview.value = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    };

    const removeEditImage = () => {
      editForm.value.imageFile = null;
      editForm.value.imageUrl = '';
      editImagePreview.value = '';
      if (editImageInput.value) {
        editImageInput.value.value = '';
      }
    };

    const openManageParticipants = async (meetup) => {
      // For past meetups, still allow viewing but disable adding participants
      selectedMeetup.value = meetup;
      showParticipantsModal.value = true;
      await loadParticipants(meetup.id);
    };

    const closeParticipantsModal = () => {
      showParticipantsModal.value = false;
      selectedMeetup.value = null;
      participants.value = [];
      manualRegistrationForm.value = { name: '', email: '' };
    };

    const loadParticipants = async (meetupId) => {
      loadingParticipants.value = true;
      try {
        const response = await fetch(`/api/meetups/${meetupId}/registrations/`, {
          credentials: "include",
        });
        if (response.ok) {
          const data = await response.json();
          participants.value = data.registrations || [];
        }
      } catch (error) {
        console.error("참가자 목록을 불러오는데 실패했습니다:", error);
        participants.value = [];
      } finally {
        loadingParticipants.value = false;
      }
    };

    const addParticipantManually = async () => {
      if (!selectedMeetup.value) return;

      addingParticipant.value = true;
      try {
        const response = await fetchWithCSRF(
          `/api/meetups/${selectedMeetup.value.id}/add-participant/`,
          {
            method: "POST",
            body: JSON.stringify({
              name: manualRegistrationForm.value.name,
              email: manualRegistrationForm.value.email
            }),
          }
        );

        if (response.ok) {
          await loadParticipants(selectedMeetup.value.id);
          await loadMeetups(); // Refresh meetup data to update participant count

          // Update selected meetup with latest data
          const updatedMeetup = meetups.value.find(m => m.id === selectedMeetup.value.id);
          if (updatedMeetup) {
            selectedMeetup.value = updatedMeetup;
          }

          manualRegistrationForm.value = { name: '', email: '' };
          message.value = "참가자가 성공적으로 추가되었습니다";
          setTimeout(() => {
            message.value = "";
          }, 3000);
        } else {
          const errorData = await response.json();
          throw new Error(errorData.error || '참가자 추가에 실패했습니다');
        }
      } catch (error) {
        console.error("참가자 추가 실패:", error);
        alert(error.message || '참가자 추가에 실패했습니다. 다시 시도해주세요.');
      } finally {
        addingParticipant.value = false;
      }
    };

    const removeParticipant = async (registrationId) => {
      if (!selectedMeetup.value) return;
      

      if (confirm("정말로 이 참가자를 제거하시겠습니까?")) {
        removingParticipant.value = true;
        try {
          const response = await fetchWithCSRF(
            `/api/meetups/${selectedMeetup.value.id}/remove-participant/${registrationId}/`,
            {
              method: "DELETE",
            }
          );

          if (response.ok) {
            await loadParticipants(selectedMeetup.value.id);
            await loadMeetups(); // Refresh meetup data to update participant count

            // Update selected meetup with latest data
            const updatedMeetup = meetups.value.find(m => m.id === selectedMeetup.value.id);
            if (updatedMeetup) {
              selectedMeetup.value = updatedMeetup;
            }

            message.value = "참가자가 성공적으로 제거되었습니다";
            setTimeout(() => {
              message.value = "";
            }, 3000);
          }
        } catch (error) {
          console.error("참가자 제거 실패:", error);
          alert('참가자 제거에 실패했습니다. 다시 시도해주세요.');
        } finally {
          removingParticipant.value = false;
        }
      }
    };

    const sendNotificationToParticipants = async () => {
      if (!selectedMeetup.value || participants.value.length === 0) return;

      sendingNotification.value = true;
      try {
        const response = await fetchWithCSRF(
          `/api/meetups/${selectedMeetup.value.id}/send-notification/`,
          {
            method: "POST",
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              title: notificationForm.value.title,
              message: notificationForm.value.message,
            }),
          }
        );

        if (response.ok) {
          const result = await response.json();
          alert(`${result.sent_count}명의 참가자에게 알림을 보냈습니다.`);

          // Clear form
          notificationForm.value.title = '';
          notificationForm.value.message = '';
        } else {
          const errorData = await response.json();
          throw new Error(errorData.error || '알림 전송에 실패했습니다');
        }
      } catch (error) {
        console.error("알림 전송 실패:", error);
        alert(error.message || '알림 전송에 실패했습니다. 다시 시도해주세요.');
      } finally {
        sendingNotification.value = false;
      }
    };

    return {
      authStore,
      meetups,
      registeredMeetups,
      waitlistMeetups,
      loading,
      loadingRegistered,
      loadingWaitlist,
      message,
      showEditModal,
      editForm,
      updating,
      totalParticipants,
      upcomingMeetups,
      averageParticipation,
      allMyMeetups,
      formatDateTime,
      // Helper functions for meetup status
      isMeetupPast,
      getMeetupStatus,
      getMeetupStatusClass,
      editMeetup,
      closeEditModal,
      updateMeetup,
      deleteMeetup,
      unregisterFromMeetup,
      removeFromWaitlist,
      logout,
      // Participants management
      showParticipantsModal,
      selectedMeetup,
      participants,
      loadingParticipants,
      addingParticipant,
      removingParticipant,
      manualRegistrationForm,
      openManageParticipants,
      closeParticipantsModal,
      loadParticipants,
      addParticipantManually,
      removeParticipant,
      // Notification sending
      notificationForm,
      sendingNotification,
      sendNotificationToParticipants,
      handleImageError,
      editImageInput,
      editImagePreview,
      handleEditImageUpload,
      removeEditImage,
      // Notifications
      notifications,
      loadingNotifications,
      showNotificationsModal,
      selectedNotification,
      unreadNotificationCount,
      loadNotifications,
      markNotificationRead,
      markAllNotificationsRead,
      openNotificationsModal,
      closeNotificationsModal,
      selectNotification,
      closeNotificationDetail,
      // Notification pagination
      notificationPagination,
      paginatedNotifications,
      goToPage,
      getVisiblePages,
    };
  },
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
