<template>
  <div class="min-h-screen bg-gray-200 dark:bg-gray-900">
    <!-- Navigation -->
    <nav class="bg-gray-50 dark:bg-gray-800 shadow safe-area-top">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">
              내 모임 관리
            </h1>
          </div>
          <div class="flex items-center space-x-1 sm:space-x-4">
            <!-- Desktop navigation -->
            <router-link
              to="/dashboard"
              class="hidden sm:block text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium"
            >
              한번 모임
            </router-link>
            
            <!-- Mobile: Dashboard icon -->
            <router-link
              to="/dashboard"
              class="sm:hidden p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-md"
              title="한번 모임"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2V7z"></path>
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
            <span class="hidden sm:inline text-gray-700 dark:text-gray-300">{{ authStore.user?.name }}님</span>
            
            <!-- Logout button - compact on mobile -->
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

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Success Message -->
        <div
          v-if="message"
          class="mb-6 rounded-md bg-green-100 dark:bg-green-900 p-4"
        >
          <div class="flex">
            <div class="flex-shrink-0">
              <svg
                class="h-5 w-5 text-green-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-green-700 dark:text-green-200">
                {{ message }}
              </p>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div
            class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg"
          >
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg
                    class="h-8 w-8 text-blue-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt
                      class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate"
                    >
                      내가 만든 모임
                    </dt>
                    <dd
                      class="text-lg font-medium text-gray-900 dark:text-white"
                    >
                      {{ meetups.length }}개
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div
            class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg"
          >
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg
                    class="h-8 w-8 text-green-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt
                      class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate"
                    >
                      총 참여자
                    </dt>
                    <dd
                      class="text-lg font-medium text-gray-900 dark:text-white"
                    >
                      {{ totalParticipants }}명
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6 text-center">
            <svg
              class="animate-spin -ml-1 mr-3 h-8 w-8 text-indigo-500 mx-auto"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <p class="mt-2 text-gray-600 dark:text-gray-400">
              모임 목록을 불러오는 중...
            </p>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-else-if="meetups.length === 0"
          class="bg-white dark:bg-gray-800 shadow rounded-lg"
        >
          <div class="px-4 py-5 sm:p-6 text-center">
            <svg
              class="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M34 40h10v-4a6 6 0 00-10.712-3.714M34 40H14m20 0v-4a9.971 9.971 0 00-.712-3.714M14 40H4v-4a6 6 0 0110.713-3.714M14 40v-4c0-1.313.253-2.566.713-3.714m0 0A10.003 10.003 0 0124 26c4.21 0 7.813 2.602 9.288 6.286M30 14a6 6 0 11-12 0 6 6 0 0112 0zm12 6a4 4 0 11-8 0 4 4 0 018 0zm-28 0a4 4 0 11-8 0 4 4 0 018 0z"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              아직 만든 모임이 없습니다
            </h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              첫 번째 모임을 만들어 사람들과 함께하는 시간을 가져보세요.
            </p>
            <div class="mt-6">
              <router-link
                to="/create-meetup"
                class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg
                  class="-ml-1 mr-2 h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                    clip-rule="evenodd"
                  />
                </svg>
                첫 모임 만들기
              </router-link>
            </div>
          </div>
        </div>

        <!-- Meetup Cards -->
        <div v-else class="space-y-6">
          <div
            class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 shadow rounded-lg overflow-hidden border border-blue-200 dark:border-blue-800"
          >
            <div
              class="px-4 py-5 sm:px-6 border-b border-blue-200 dark:border-blue-700 bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-800/30 dark:to-indigo-800/30"
            >
              <div class="flex justify-between items-center">
                <div class="flex items-center space-x-2">
                  <div class="p-2 bg-blue-200 dark:bg-blue-800 rounded-full">
                    <svg class="w-5 h-5 text-blue-600 dark:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                    </svg>
                  </div>
                  <div>
                    <h3
                      class="text-lg leading-6 font-medium text-blue-900 dark:text-blue-100"
                    >
                      내가 개설한 모임
                    </h3>
                    <p
                      class="mt-1 max-w-2xl text-sm text-blue-700 dark:text-blue-300"
                    >
                      {{ meetups.length }}개의 모임을 관리하고 있습니다.
                    </p>
                  </div>
                </div>
                <router-link
                  to="/create-meetup"
                  class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <svg class="-ml-0.5 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                  </svg>
                  <span class="hidden sm:inline">새 모임 만들기</span>
                  <span class="sm:hidden">새 모임</span>
                </router-link>
              </div>
            </div>
            <!-- Desktop view -->
            <div class="hidden sm:block divide-y divide-blue-200 dark:divide-blue-700">
              <div
                v-for="meetup in meetups"
                :key="meetup.id"
                class="px-4 py-6 sm:px-6 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors duration-150"
              >
                <div class="space-y-4">
                  <!-- Main content row -->
                  <div class="flex items-start justify-between">
                    <div class="flex items-center space-x-3 flex-1 min-w-0">
                      <div class="flex-shrink-0">
                        <div v-if="meetup.image_display_url" class="w-12 h-12 rounded-lg overflow-hidden">
                          <img 
                            :src="meetup.image_display_url" 
                            :alt="meetup.name"
                            class="w-12 h-12 object-cover"
                            @error="handleImageError"
                          />
                        </div>
                        <div
                          v-else
                          class="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center"
                        >
                          <svg
                            class="w-7 h-7 text-blue-600 dark:text-blue-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                            />
                          </svg>
                        </div>
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between">
                          <div class="flex-1 min-w-0">
                            <h4 class="text-lg font-medium text-gray-900 dark:text-white truncate">
                              {{ meetup.name }}
                            </h4>
                            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                              {{ meetup.description }}
                            </p>
                          </div>
                          <div class="flex items-center space-x-2 ml-4">
                            <span
                              :class="[
                                'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                                meetup.is_full
                                  ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                                  : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
                              ]"
                            >
                              {{ meetup.is_full ? "마감" : "모집중" }}
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
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {{ formatDateTime(meetup.date_time) }}
                      </div>
                      <div class="flex items-center">
                        <svg class="mr-1.5 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {{ meetup.location }}
                      </div>
                      <div class="flex items-center">
                        <svg class="mr-1.5 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        {{ meetup.current_participants }}/{{ meetup.max_participants }}명
                        <span class="ml-1 text-xs text-gray-400">({{ meetup.available_spots }}석 남음)</span>
                      </div>
                    </div>

                    <!-- Hashtags and Actions row -->
                    <div class="flex items-center justify-between">
                      <!-- Hashtags -->
                      <div class="flex-1">
                        <div v-if="meetup.hashtags_list && meetup.hashtags_list.length > 0" class="flex flex-wrap gap-1">
                          <span v-for="hashtag in meetup.hashtags_list" :key="hashtag" 
                                class="inline-flex px-2 py-0.5 text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full">
                            {{ hashtag }}
                          </span>
                        </div>
                      </div>
                      
                      <!-- Action buttons -->
                      <div class="flex items-center space-x-1 ml-4">
                        <button
                          @click="editMeetup(meetup)"
                          class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-indigo-700 bg-indigo-100 hover:bg-indigo-200 dark:bg-indigo-900 dark:text-indigo-300 dark:hover:bg-indigo-800 rounded-md transition-colors"
                          title="수정"
                        >
                          <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                          수정
                        </button>
                        <button
                          @click="openManageParticipants(meetup)"
                          class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-green-700 bg-green-100 hover:bg-green-200 dark:bg-green-900 dark:text-green-300 dark:hover:bg-green-800 rounded-md transition-colors"
                          title="참가자 관리"
                        >
                          <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                          </svg>
                          참가자
                        </button>
                        <button
                          @click="deleteMeetup(meetup.id)"
                          class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-red-700 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800 rounded-md transition-colors"
                          title="삭제"
                        >
                          <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
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
              <div
                v-for="meetup in meetups"
                :key="meetup.id"
                class="bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-800/40 dark:to-indigo-800/40 rounded-lg p-4 space-y-3 border border-blue-200 dark:border-blue-700"
              >
                <div class="flex justify-between items-start">
                  <div class="flex items-start space-x-3 flex-1 min-w-0">
                    <div v-if="meetup.image_display_url" class="flex-shrink-0">
                      <img 
                        :src="meetup.image_display_url" 
                        :alt="meetup.name"
                        class="w-12 h-12 object-cover rounded-lg"
                        @error="handleImageError"
                      />
                    </div>
                    <div class="flex-1 min-w-0">
                      <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {{ meetup.name }}
                      </h3>
                      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                        {{ meetup.description }}
                      </p>
                    </div>
                  </div>
                  <span 
                    class="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full flex-shrink-0"
                    :class="[
                      meetup.is_full
                        ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
                    ]"
                  >
                    {{ meetup.is_full ? "마감" : "모집중" }}
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
                
                <div class="grid grid-cols-3 gap-2 pt-2 border-t border-blue-200 dark:border-blue-700">
                  <button
                    @click="editMeetup(meetup)"
                    class="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
                  >
                    수정
                  </button>
                  <button
                    @click="openManageParticipants(meetup)"
                    class="bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
                  >
                    참가자
                  </button>
                  <button
                    @click="deleteMeetup(meetup.id)"
                    class="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
                  >
                    삭제
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 등록한 모임 목록 -->
        <div
          class="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 shadow rounded-lg overflow-hidden mt-6 border border-green-200 dark:border-green-800"
        >
          <div
            class="px-4 py-5 sm:px-6 border-b border-green-200 dark:border-green-700 bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-800/30 dark:to-emerald-800/30"
          >
            <div class="flex items-center space-x-2">
              <div class="p-2 bg-green-200 dark:bg-green-800 rounded-full">
                <svg class="w-5 h-5 text-green-600 dark:text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div>
                <h3
                  class="text-lg leading-6 font-medium text-green-900 dark:text-green-100"
                >
                  내가 신청한 모임
                </h3>
                <p class="mt-1 max-w-2xl text-sm text-green-700 dark:text-green-300">
                  {{ registeredMeetups.length }}개의 모임에 참가 신청했습니다.
                </p>
              </div>
            </div>
          </div>

          <!-- 등록한 모임 로딩 상태 -->
          <div v-if="loadingRegistered" class="px-4 py-5 sm:px-6 text-center">
            <svg
              class="animate-spin -ml-1 mr-3 h-8 w-8 text-indigo-500 mx-auto"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <p class="mt-2 text-gray-600 dark:text-gray-400">
              등록한 모임 목록을 불러오는 중...
            </p>
          </div>

          <!-- 등록한 모임이 없는 경우 -->
          <div
            v-else-if="registeredMeetups.length === 0"
            class="px-4 py-5 sm:px-6 text-center"
          >
            <svg
              class="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M34 40h10v-4a6 6 0 00-10.712-3.714M34 40H14m20 0v-4a9.971 9.971 0 00-.712-3.714M14 40H4v-4a6 6 0 0110.713-3.714M14 40v-4c0-1.313.253-2.566.713-3.714m0 0A10.003 10.003 0 0124 26c4.21 0 7.813 2.602 9.288 6.286M30 14a6 6 0 11-12 0 6 6 0 0112 0zm12 6a4 4 0 11-8 0 4 4 0 018 0zm-28 0a4 4 0 11-8 0 4 4 0 018 0z"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              내가 신청한 모임이 없습니다
            </h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              관심 있는 모임에 참가 신청해보세요.
            </p>
            <div class="mt-6">
              <router-link
                to="/dashboard"
                class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg
                  class="-ml-1 mr-2 h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"
                  />
                </svg>
                모임 둘러보기
              </router-link>
            </div>
          </div>

          <!-- Desktop view for registered meetups -->
          <div v-if="!loadingRegistered && registeredMeetups.length > 0" class="hidden sm:block divide-y divide-green-200 dark:divide-green-700">
            <div
              v-for="meetup in registeredMeetups"
              :key="meetup.id"
              class="px-4 py-6 sm:px-6 hover:bg-green-50 dark:hover:bg-green-900/30 transition-colors duration-150"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-3">
                    <div class="flex-shrink-0">
                      <div v-if="meetup.image_display_url" class="w-12 h-12 rounded-lg overflow-hidden">
                        <img 
                          :src="meetup.image_display_url" 
                          :alt="meetup.name"
                          class="w-12 h-12 object-cover"
                          @error="handleImageError"
                        />
                      </div>
                      <div
                        v-else
                        class="w-12 h-12 bg-emerald-100 dark:bg-emerald-900 rounded-lg flex items-center justify-center"
                      >
                        <svg
                          class="w-7 h-7 text-emerald-600 dark:text-emerald-400"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <h4
                        class="text-lg font-medium text-gray-900 dark:text-white truncate"
                      >
                        {{ meetup.name }}
                      </h4>
                      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {{ meetup.description }}
                      </p>
                      <div
                        class="mt-2 flex items-center text-sm text-gray-500 dark:text-gray-400 space-x-4"
                      >
                        <div class="flex items-center">
                          <svg
                            class="mr-1.5 h-4 w-4 text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                          </svg>
                          {{ formatDateTime(meetup.date_time) }}
                        </div>
                        <div class="flex items-center">
                          <svg
                            class="mr-1.5 h-4 w-4 text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                            />
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                            />
                          </svg>
                          {{ meetup.location }}
                        </div>
                        <div class="flex items-center">
                          <svg
                            class="mr-1.5 h-4 w-4 text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                            />
                          </svg>
                          {{ meetup.current_participants }} /
                          {{ meetup.max_participants }}명
                        </div>
                      </div>
                      <div class="mt-2 text-xs text-gray-400">
                        {{
                          new Date(meetup.registration_date).toLocaleDateString(
                            "ko-KR"
                          )
                        }}에 신청
                      </div>
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <span
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      meetup.is_full
                        ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
                    ]"
                  >
                    {{ meetup.is_full ? "마감" : "모집중" }}
                  </span>
                  <button
                    @click="
                      unregisterFromMeetup(meetup.id, meetup.registration_id)
                    "
                    class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-red-700 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800 rounded-md transition-colors"
                    title="참가 취소"
                  >
                    <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    취소
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Mobile view for registered meetups -->
          <div v-if="!loadingRegistered && registeredMeetups.length > 0" class="sm:hidden space-y-4 p-4">
            <div
              v-for="meetup in registeredMeetups"
              :key="meetup.id"
              class="bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-800/40 dark:to-emerald-800/40 rounded-lg p-4 space-y-3 border border-green-200 dark:border-green-700"
            >
              <div class="flex justify-between items-start">
                <div class="flex items-start space-x-3 flex-1 min-w-0">
                  <div v-if="meetup.image_display_url" class="flex-shrink-0">
                    <img 
                      :src="meetup.image_display_url" 
                      :alt="meetup.name"
                      class="w-12 h-12 object-cover rounded-lg"
                      @error="handleImageError"
                    />
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {{ meetup.name }}
                    </h3>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                      {{ meetup.description }}
                    </p>
                  </div>
                </div>
                <span class="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200 flex-shrink-0">
                  참가중
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
                  <div class="text-gray-500 dark:text-gray-400">장소</div>
                  <div class="text-gray-900 dark:text-white font-medium truncate">
                    {{ meetup.location }}
                  </div>
                </div>
                
                <div>
                  <div class="text-gray-500 dark:text-gray-400">생성자</div>
                  <div class="text-gray-900 dark:text-white font-medium">
                    {{ meetup.creator_name }}
                  </div>
                </div>
                
                <div>
                  <div class="text-gray-500 dark:text-gray-400">참여자</div>
                  <div class="text-gray-900 dark:text-white font-medium">
                    {{ meetup.current_participants }}/{{ meetup.max_participants }}명
                  </div>
                </div>
              </div>
              
              <div class="flex space-x-2 pt-2">
                <button
                  @click="unregisterFromMeetup(meetup.id, meetup.registration_id)"
                  :disabled="loadingRegistered"
                  class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs flex-1 disabled:opacity-50"
                >
                  취소
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div
      v-if="showEditModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click.self="closeEditModal"
    >
      <div
        class="relative top-20 mx-auto p-5 border max-w-md shadow-lg rounded-lg bg-gray-50 dark:bg-gray-800"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            모임 수정
          </h3>
          <button
            @click="closeEditModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
        <form @submit.prevent="updateMeetup" class="space-y-4">
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >모임 이름</label
            >
            <input
              v-model="editForm.name"
              type="text"
              required
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-sm"
            />
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >설명</label
            >
            <textarea
              v-model="editForm.description"
              rows="3"
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-sm"
            ></textarea>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >장소</label
            >
            <input
              v-model="editForm.location"
              type="text"
              required
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-sm"
            />
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >시작 시간</label
            >
            <input
              v-model="editForm.date_time"
              type="datetime-local"
              required
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-sm"
            />
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >모임 진행 시간 (시간)</label
            >
            <input
              v-model.number="editForm.duration"
              type="number"
              min="0.5"
              step="0.5"
              placeholder="예: 2 (2시간)"
              required
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-sm"
            />
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >최대 참여 인원</label
            >
            <input
              v-model.number="editForm.max_participants"
              type="number"
              min="1"
              required
              class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-sm"
            />
          </div>

          <!-- Hashtags Section -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              해시태그
            </label>
            <input
              v-model="editForm.hashtags"
              type="text"
              placeholder="#개발,#네트워킹,#스타트업 (쉼표로 구분)"
              class="block w-full px-3 py-2 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 sm:text-sm"
            />
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
                <img 
                  :src="editForm.currentImageUrl" 
                  alt="현재 이미지" 
                  class="h-20 w-32 object-cover rounded-lg border border-gray-300 dark:border-gray-600"
                  @error="handleImageError"
                />
                <span class="absolute top-0 left-0 bg-blue-500 text-white text-xs px-1 rounded">현재</span>
              </div>

              <!-- New Image Options -->
              <div class="flex flex-col space-y-2">
                <!-- File Upload -->
                <div>
                  <label for="edit-image-upload" class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                    새 이미지 파일 업로드
                  </label>
                  <input
                    type="file"
                    id="edit-image-upload"
                    ref="editImageInput"
                    @change="handleEditImageUpload"
                    accept="image/*"
                    class="block w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 dark:file:bg-indigo-900 dark:file:text-indigo-300"
                  />
                </div>
                
                <!-- URL Input -->
                <div>
                  <label for="edit-image-url" class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                    또는 새 이미지 URL
                  </label>
                  <input
                    type="url"
                    id="edit-image-url"
                    v-model="editForm.imageUrl"
                    placeholder="https://example.com/image.jpg"
                    class="block w-full px-2 py-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 text-sm"
                  />
                </div>
              </div>

              <!-- New Image Preview -->
              <div v-if="editImagePreview" class="relative inline-block">
                <img 
                  :src="editImagePreview" 
                  alt="새 이미지 미리보기" 
                  class="h-20 w-32 object-cover rounded-lg border border-gray-300 dark:border-gray-600"
                  @error="handleImageError"
                />
                <span class="absolute top-0 left-0 bg-green-500 text-white text-xs px-1 rounded">새 이미지</span>
                <button
                  type="button"
                  @click="removeEditImage"
                  class="absolute -top-1 -right-1 bg-red-500 hover:bg-red-600 text-white rounded-full p-1"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div
            class="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700"
          >
            <button
              type="button"
              @click="closeEditModal"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
            >
              취소
            </button>
            <button
              type="submit"
              :disabled="updating"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg
                v-if="updating"
                class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              {{ updating ? "수정 중..." : "수정 완료" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Manage Participants Modal -->
    <div
      v-if="showParticipantsModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click.self="closeParticipantsModal"
    >
      <div
        class="relative top-10 mx-auto p-5 border max-w-2xl shadow-lg rounded-lg bg-gray-50 dark:bg-gray-800"
      >
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">
              참가자 관리: {{ selectedMeetup?.name }}
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ selectedMeetup?.current_participants }} / {{ selectedMeetup?.max_participants }}명 등록
            </p>
          </div>
          <button
            @click="closeParticipantsModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Manual Registration Form -->
        <div class="bg-white dark:bg-gray-700 rounded-lg p-4 mb-4">
          <h4 class="text-md font-medium text-gray-900 dark:text-white mb-3">
            수동 참가자 등록
          </h4>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
            다른 채널을 통해 등록한 참가자를 수동으로 추가할 수 있습니다.
          </p>
          <form @submit.prevent="addParticipantManually" class="space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  이름 *
                </label>
                <input
                  v-model="manualRegistrationForm.name"
                  type="text"
                  required
                  placeholder="참가자 이름"
                  class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white sm:text-sm"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  이메일 *
                </label>
                <input
                  v-model="manualRegistrationForm.email"
                  type="email"
                  required
                  placeholder="참가자 이메일"
                  class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white sm:text-sm"
                />
              </div>
            </div>
            <div class="flex justify-end">
              <button
                type="submit"
                :disabled="addingParticipant"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="addingParticipant" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ addingParticipant ? "추가 중..." : "참가자 추가" }}
              </button>
            </div>
          </form>
        </div>

        <!-- Participants List -->
        <div class="bg-white dark:bg-gray-700 rounded-lg p-4">
          <h4 class="text-md font-medium text-gray-900 dark:text-white mb-3">
            등록된 참가자
          </h4>
          
          <!-- Loading State -->
          <div v-if="loadingParticipants" class="text-center py-4">
            <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-indigo-500 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="mt-2 text-gray-600 dark:text-gray-400">참가자 목록을 불러오는 중...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="participants.length === 0" class="text-center py-4">
            <p class="text-gray-500 dark:text-gray-400">등록된 참가자가 없습니다.</p>
          </div>

          <!-- Participants List -->
          <div v-else class="space-y-2 max-h-60 overflow-y-auto">
            <div
              v-for="participant in participants"
              :key="participant.id"
              class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-600 rounded-lg"
            >
              <div class="flex-1">
                <div class="flex items-center space-x-3">
                  <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center">
                      <svg class="w-4 h-4 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
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
              <button
                @click="removeParticipant(participant.id)"
                :disabled="removingParticipant"
                class="p-2 text-red-600 hover:text-red-900 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900 rounded-md disabled:opacity-50"
                title="참가자 제거"
              >
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div class="flex justify-end mt-4">
          <button
            @click="closeParticipantsModal"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-gray-600 dark:text-gray-300 dark:border-gray-500 dark:hover:bg-gray-500"
          >
            닫기
          </button>
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
    const loading = ref(false);
    const loadingRegistered = ref(false);
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

    onMounted(() => {
      if (route.query.message) {
        message.value = route.query.message;
        setTimeout(() => {
          message.value = "";
        }, 5000);
      }
      loadMeetups();
      loadRegisteredMeetups();
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
        console.error("모임 수정에 실패했습니다:", error);
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

    const logout = () => {
      authStore.logout();
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

    return {
      authStore,
      meetups,
      registeredMeetups,
      loading,
      loadingRegistered,
      message,
      showEditModal,
      editForm,
      updating,
      totalParticipants,
      upcomingMeetups,
      averageParticipation,
      formatDateTime,
      editMeetup,
      closeEditModal,
      updateMeetup,
      deleteMeetup,
      unregisterFromMeetup,
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
      handleImageError,
      editImageInput,
      editImagePreview,
      handleEditImageUpload,
      removeEditImage,
    };
  },
};
</script>
