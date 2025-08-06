<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Navigation -->
    <nav class="bg-white dark:bg-gray-800 shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-gray-900 dark:text-white">
              내 모임 관리
            </h1>
          </div>
          <div class="flex items-center space-x-4">
            <router-link
              to="/dashboard"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium"
            >
              대시보드
            </router-link>
            
            <ThemeToggle />
            <span class="text-gray-700 dark:text-gray-300"
              >{{ authStore.user?.name }}님</span
            >
            <button
              @click="logout"
              class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              로그아웃
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
          class="mb-6 rounded-md bg-green-50 dark:bg-green-900 p-4"
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

          <div
            class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg"
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
            class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg"
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
            class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden"
          >
            <div
              class="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-700"
            >
              <h3
                class="text-lg leading-6 font-medium text-gray-900 dark:text-white"
              >
                내가 주최한 모임
              </h3>
              <p
                class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400"
              >
                {{ meetups.length }}개의 모임을 관리하고 있습니다.
              </p>

              <!-- 새 모임 만들기 버튼 (타이틀 오른쪽) -->
              <router-link
                to="/create-meetup"
                class="ml-auto bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium inline-flex items-center"
                style="float: right; margin-top: -2.5rem;"
              >
                새 모임 만들기
              </router-link>

            </div>
            <div class="divide-y divide-gray-200 dark:divide-gray-700">
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
                        @click="manageParticipants(meetup)"
                        class="p-2 text-green-600 hover:text-green-900 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900 rounded-md"
                        title="참가자 관리"
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
                            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                          />
                        </svg>
                      </button>
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
          </div>
        </div>

        <!-- 등록한 모임 목록 -->
        <div
          class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden mt-6"
        >
          <div
            class="px-4 py-5 sm:px-6 border-b border-gray-200 dark:border-gray-700"
          >
            <h3
              class="text-lg leading-6 font-medium text-gray-900 dark:text-white"
            >
              내가 신청한 모임
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

          <!-- 등록한 모임 카드들 -->
          <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
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
        class="relative top-10 mx-auto p-6 border max-w-2xl shadow-lg rounded-lg bg-white dark:bg-gray-800"
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
        <form @submit.prevent="updateMeetup" class="space-y-6">
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >모임 이름</label
            >
            <input
              v-model="editForm.name"
              type="text"
              required
              class="block w-full px-4 py-3 text-base border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-indigo-400"
              placeholder="모임 이름을 입력하세요"
            />
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >설명</label
            >
            <textarea
              v-model="editForm.description"
              rows="5"
              class="block w-full px-4 py-3 text-base border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-indigo-400 resize-y"
              placeholder="모임에 대한 설명을 작성하세요"
            ></textarea>
          </div>
          <div>
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >장소</label
            >
            <input
              v-model="editForm.location"
              type="text"
              required
              class="block w-full px-4 py-3 text-base border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-indigo-400"
              placeholder="모임 장소를 입력하세요"
            />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >날짜</label
              >
              <input
                v-model="editForm.date"
                type="date"
                required
                class="block w-full px-4 py-3 text-base border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-indigo-400"
              />
            </div>
            <div>
              <label
                class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >시작 시간</label
              >
              <input
                v-model="editForm.time"
                type="time"
                required
                class="block w-full px-4 py-3 text-base border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-indigo-400"
              />
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >모임 진행 시간</label
              >
              <select
                v-model.number="editForm.duration"
                required
                class="block w-full px-4 py-3 text-base border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-indigo-400"
              >
                <option value="0.5">30분</option>
                <option value="1">1시간</option>
                <option value="1.5">1시간 30분</option>
                <option value="2">2시간</option>
                <option value="2.5">2시간 30분</option>
                <option value="3">3시간</option>
                <option value="3.5">3시간 30분</option>
                <option value="4">4시간</option>
                <option value="5">5시간</option>
                <option value="6">6시간</option>
                <option value="8">8시간</option>
              </select>
            </div>
            <div>
              <label
                class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >최대 참여 인원</label
              >
              <input
                v-model.number="editForm.max_participants"
                type="number"
                min="1"
                max="100"
                required
                class="block w-full px-4 py-3 text-base border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:ring-indigo-400"
                placeholder="최대 인원"
              />
            </div>
          </div>
          <div
            class="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700"
          >
            <button
              type="button"
              @click="closeEditModal"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
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

    <!-- Participants Management Modal -->
    <div
      v-if="showParticipantsModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click.self="closeParticipantsModal"
    >
      <div
        class="relative top-10 mx-auto p-6 border max-w-4xl shadow-lg rounded-lg bg-white dark:bg-gray-800"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            {{ selectedMeetupForParticipants?.name }} - 참가자 관리
          </h3>
          <button
            @click="closeParticipantsModal"
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

        <div class="space-y-6">
          <!-- Add Participant Section -->
          <div class="border-b border-gray-200 dark:border-gray-700 pb-6">
            <h4 class="text-md font-medium text-gray-900 dark:text-white mb-3">참가자 추가</h4>
            <div class="flex space-x-3">
              <input
                v-model="newParticipantEmail"
                type="email"
                placeholder="참가자 이메일 입력"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                @keyup.enter="addParticipant"
              />
              <button
                @click="addParticipant"
                :disabled="!newParticipantEmail || addingParticipant"
                class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="addingParticipant" class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ addingParticipant ? '추가 중...' : '추가' }}
              </button>
            </div>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
              이메일로 참가자를 직접 추가할 수 있습니다. 기존 사용자가 아닌 경우 게스트로 추가됩니다.
            </p>
          </div>

          <!-- Current Participants List -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-md font-medium text-gray-900 dark:text-white">
                현재 참가자 ({{ participants.length }} / {{ selectedMeetupForParticipants?.max_participants }}명)
              </h4>
              <button
                @click="refreshParticipants"
                :disabled="loadingParticipants"
                class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
                title="참가자 목록 새로고침"
              >
                <svg 
                  :class="['w-4 h-4', { 'animate-spin': loadingParticipants }]" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
              </button>
            </div>

            <div v-if="loadingParticipants" class="text-center py-4">
              <div class="text-gray-600 dark:text-gray-400">참가자 목록을 불러오는 중...</div>
            </div>

            <div v-else-if="participants.length === 0" class="text-center py-8">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">참가자가 없습니다</h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">위에서 이메일로 참가자를 추가해보세요.</p>
            </div>

            <div v-else class="space-y-2 max-h-64 overflow-y-auto">
              <div 
                v-for="participant in participants" 
                :key="participant.id"
                class="flex items-center justify-between bg-gray-50 dark:bg-gray-700 p-3 rounded-lg"
              >
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded-full flex items-center justify-center text-xs font-semibold">
                    {{ participant.user_name.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900 dark:text-white">{{ participant.user_name }}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">{{ participant.user_email }}</div>
                  </div>
                </div>
                <button
                  @click="removeParticipant(participant.id)"
                  class="text-red-600 hover:text-red-900 dark:text-red-400 p-1 hover:bg-red-50 dark:hover:bg-red-900 rounded"
                  title="참가자 제거"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-6 flex justify-end">
          <button
            @click="closeParticipantsModal"
            class="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-md text-sm font-medium"
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

    // Participants management
    const showParticipantsModal = ref(false);
    const selectedMeetupForParticipants = ref(null);
    const participants = ref([]);
    const newParticipantEmail = ref('');
    const addingParticipant = ref(false);
    const loadingParticipants = ref(false);

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

      // Convert date_time to separate date and time fields
      let dateValue = "";
      let timeValue = "";
      if (meetup.date_time) {
        const date = new Date(meetup.date_time);
        dateValue = date.toISOString().split('T')[0]; // YYYY-MM-DD
        timeValue = date.toTimeString().slice(0, 5); // HH:MM
      }

      editForm.value = {
        name: meetup.name,
        description: meetup.description,
        location: meetup.location,
        date: dateValue,
        time: timeValue,
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
        // Combine date and time fields into datetime
        const dateTimeString = `${editForm.value.date}T${editForm.value.time}`;
        const startTime = new Date(dateTimeString);
        
        // Calculate end time from start time and duration
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

    // Participant management functions
    const manageParticipants = async (meetup) => {
      selectedMeetupForParticipants.value = meetup;
      showParticipantsModal.value = true;
      await refreshParticipants();
    };

    const closeParticipantsModal = () => {
      showParticipantsModal.value = false;
      selectedMeetupForParticipants.value = null;
      participants.value = [];
      newParticipantEmail.value = '';
    };

    const refreshParticipants = async () => {
      if (!selectedMeetupForParticipants.value) return;
      
      loadingParticipants.value = true;
      try {
        const response = await fetch(`/api/meetups/${selectedMeetupForParticipants.value.id}/registrations/`, {
          credentials: 'include'
        });
        
        if (response.ok) {
          const data = await response.json();
          participants.value = data.registrations;
        }
      } catch (error) {
        console.error('참가자 목록 불러오기 실패:', error);
      } finally {
        loadingParticipants.value = false;
      }
    };

    const addParticipant = async () => {
      if (!newParticipantEmail.value || !selectedMeetupForParticipants.value) return;
      
      addingParticipant.value = true;
      try {
        const response = await fetchWithCSRF(`/api/meetups/${selectedMeetupForParticipants.value.id}/add-participant/`, {
          method: 'POST',
          body: JSON.stringify({
            email: newParticipantEmail.value
          })
        });

        if (response.ok) {
          newParticipantEmail.value = '';
          await Promise.all([refreshParticipants(), loadMeetups()]);
          message.value = '참가자가 성공적으로 추가되었습니다';
          setTimeout(() => {
            message.value = '';
          }, 3000);
        } else {
          const data = await response.json();
          alert(data.error || '참가자 추가에 실패했습니다');
        }
      } catch (error) {
        console.error('참가자 추가 실패:', error);
        alert('네트워크 오류가 발생했습니다');
      } finally {
        addingParticipant.value = false;
      }
    };

    const removeParticipant = async (registrationId) => {
      if (!confirm('정말로 이 참가자를 제거하시겠습니까?')) return;
      
      try {
        const response = await fetchWithCSRF(`/api/meetups/${selectedMeetupForParticipants.value.id}/remove-participant/${registrationId}/`, {
          method: 'DELETE'
        });

        if (response.ok) {
          await Promise.all([refreshParticipants(), loadMeetups()]);
          message.value = '참가자가 성공적으로 제거되었습니다';
          setTimeout(() => {
            message.value = '';
          }, 3000);
        } else {
          const data = await response.json();
          alert(data.error || '참가자 제거에 실패했습니다');
        }
      } catch (error) {
        console.error('참가자 제거 실패:', error);
        alert('네트워크 오류가 발생했습니다');
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
      // Participant management
      showParticipantsModal,
      selectedMeetupForParticipants,
      participants,
      newParticipantEmail,
      addingParticipant,
      loadingParticipants,
      manageParticipants,
      closeParticipantsModal,
      refreshParticipants,
      addParticipant,
      removeParticipant,
      logout,
    };
  },
};
</script>
