<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900">
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
              대시보드
            </router-link>
            
            <!-- Mobile: Dashboard icon -->
            <router-link
              to="/dashboard"
              class="sm:hidden p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-md"
              title="대시보드"
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
            class="bg-gray-50 dark:bg-gray-800 overflow-hidden shadow rounded-lg"
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
            class="bg-gray-50 dark:bg-gray-800 overflow-hidden shadow rounded-lg"
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

          <div
            class="bg-gray-50 dark:bg-gray-800 overflow-hidden shadow rounded-lg"
          >
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg
                    class="h-8 w-8 text-yellow-400"
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
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt
                      class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate"
                    >
                      예정된 모임
                    </dt>
                    <dd
                      class="text-lg font-medium text-gray-900 dark:text-white"
                    >
                      {{ upcomingMeetups }}개
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div
            class="bg-gray-50 dark:bg-gray-800 overflow-hidden shadow rounded-lg"
          >
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg
                    class="h-8 w-8 text-indigo-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt
                      class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate"
                    >
                      평균 참여율
                    </dt>
                    <dd
                      class="text-lg font-medium text-gray-900 dark:text-white"
                    >
                      {{ averageParticipation }}%
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="bg-gray-50 dark:bg-gray-800 shadow rounded-lg">
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
          class="bg-gray-50 dark:bg-gray-800 shadow rounded-lg"
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
            class="bg-gray-50 dark:bg-gray-800 shadow rounded-lg overflow-hidden"
          >
            <div
              class="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-700"
            >
              <h3
                class="text-lg leading-6 font-medium text-gray-900 dark:text-white"
              >
                내 모임 목록
              </h3>
              <p
                class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400"
              >
                {{ meetups.length }}개의 모임을 관리하고 있습니다.
              </p>
            </div>
            <!-- Desktop view -->
            <div class="hidden sm:block divide-y divide-gray-200 dark:divide-gray-700">
              <div
                v-for="meetup in meetups"
                :key="meetup.id"
                class="px-4 py-6 sm:px-6"
              >
                <div class="flex items-center justify-between">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center space-x-3">
                      <div class="flex-shrink-0">
                        <div
                          class="w-10 h-10 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center"
                        >
                          <svg
                            class="w-6 h-6 text-indigo-600 dark:text-indigo-400"
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
                        <p
                          class="text-sm text-gray-500 dark:text-gray-400 mt-1"
                        >
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
                            <span class="ml-1 text-xs text-gray-400">
                              ({{ meetup.available_spots }}석 남음)
                            </span>
                          </div>
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
                    <div class="flex items-center space-x-1">
                      <button
                        @click="editMeetup(meetup)"
                        class="p-2 text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900 rounded-md"
                        title="수정"
                      >
                        <svg
                          class="h-4 w-4"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                          />
                        </svg>
                      </button>
                      <button
                        @click="deleteMeetup(meetup.id)"
                        class="p-2 text-red-600 hover:text-red-900 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900 rounded-md"
                        title="삭제"
                      >
                        <svg
                          class="h-4 w-4"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
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
                class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-3"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1 min-w-0">
                    <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {{ meetup.name }}
                    </h3>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                      {{ meetup.description }}
                    </p>
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
                
                <div class="flex space-x-2 pt-2">
                  <button
                    @click="editMeetup(meetup)"
                    class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs flex-1"
                  >
                    수정
                  </button>
                  <button
                    @click="deleteMeetup(meetup.id)"
                    class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs flex-1"
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
          class="bg-gray-50 dark:bg-gray-800 shadow rounded-lg overflow-hidden mt-6"
        >
          <div
            class="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-700"
          >
            <h3
              class="text-lg leading-6 font-medium text-gray-900 dark:text-white"
            >
              참가 신청한 모임
            </h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
              {{ registeredMeetups.length }}개의 모임에 참가 신청했습니다.
            </p>
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
              참가 신청한 모임이 없습니다
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
          <div v-if="!loadingRegistered && registeredMeetups.length > 0" class="hidden sm:block divide-y divide-gray-200 dark:divide-gray-700">
            <div
              v-for="meetup in registeredMeetups"
              :key="meetup.id"
              class="px-4 py-6 sm:px-6"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-3">
                    <div class="flex-shrink-0">
                      <div
                        class="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center"
                      >
                        <svg
                          class="w-6 h-6 text-green-600 dark:text-green-400"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
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
                    class="p-2 text-red-600 hover:text-red-900 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900 rounded-md"
                    title="참가 취소"
                  >
                    <svg
                      class="h-4 w-4"
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
              </div>
            </div>
          </div>
          
          <!-- Mobile view for registered meetups -->
          <div v-if="!loadingRegistered && registeredMeetups.length > 0" class="sm:hidden space-y-4 p-4">
            <div
              v-for="meetup in registeredMeetups"
              :key="meetup.id"
              class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-3"
            >
              <div class="flex justify-between items-start">
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {{ meetup.name }}
                  </h3>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                    {{ meetup.description }}
                  </p>
                </div>
                <span class="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 flex-shrink-0">
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
        localDateTime = date.toISOString().slice(0, 16);
      }

      editForm.value = {
        name: meetup.name,
        description: meetup.description,
        location: meetup.location,
        date_time: localDateTime,
        duration: duration,
        max_participants: meetup.max_participants,
      };
      currentEditId.value = meetup.id;
      showEditModal.value = true;
    };

    const closeEditModal = () => {
      showEditModal.value = false;
      editForm.value = {};
      currentEditId.value = null;
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
        };

        const response = await fetchWithCSRF(
          `/api/meetups/${currentEditId.value}/`,
          {
            method: "PUT",
            body: JSON.stringify(updateData),
          }
        );

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
    };
  },
};
</script>
