<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-950">
    <nav class="bg-beige-200 dark:bg-neutral-900 border-b border-beige-300 dark:border-neutral-800 safe-area-top">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center space-x-3">
            <img 
              src="/icons/logo.png" 
              alt="한입 모임 로고" 
              class="h-8 w-8 rounded-lg"
            />
            <h1
              class="text-lg sm:text-xl font-semibold text-neutral-900 dark:text-neutral-100"
            >
              한입 모임
            </h1>
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
              to="/help"
              class="text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-300 px-2 sm:px-3 py-2 rounded-md text-sm font-medium hidden sm:block"
            >
              사용 가이드
            </router-link>
            <router-link
              v-if="!authStore.isGuest"
              to="/settings"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 px-2 sm:px-3 py-2 rounded-md text-sm font-medium hidden sm:block"
            >
              내 모임
            </router-link>
            <!-- Mobile: Admin navigation -->
            <router-link
              v-if="authStore.isAdmin"
              to="/admin"
              class="sm:hidden p-1 text-purple-500 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 rounded-md"
              title="관리자 패널"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                ></path>
              </svg>
            </router-link>
            <!-- Mobile: Help navigation -->
            <router-link
              to="/help"
              class="sm:hidden p-1 text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-300 rounded-md"
              title="사용 가이드"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
            </router-link>
            <!-- Mobile: Only show essential navigation -->
            <router-link
              v-if="!authStore.isGuest"
              to="/settings"
              class="sm:hidden p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-md"
              title="내 모임"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                ></path>
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                ></path>
              </svg>
            </router-link>
            <div class="sm:hidden">
              <ThemeToggle />
            </div>
            <div class="hidden sm:block">
              <ThemeToggle />
            </div>
            <span class="text-gray-700 dark:text-gray-300 hidden sm:inline"
              >{{ authStore.user?.name }}님</span
            >
            <span
              v-if="authStore.isGuest"
              class="text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded-full hidden sm:inline"
              >게스트 모드</span
            >
            <button
              @click="logout"
              class="bg-red-600 hover:bg-red-700 text-white px-1 sm:px-4 py-1 sm:py-2 rounded-md text-sm font-medium"
            >
              <span class="hidden sm:inline">로그아웃</span>
              <svg
                class="w-4 h-4 sm:hidden"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                ></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Guest Mode Banner -->
    <div
      v-if="authStore.isGuest"
      class="bg-yellow-50 dark:bg-yellow-900 border-b border-yellow-200 dark:border-yellow-800"
    >
      <div class="max-w-7xl mx-auto py-3 px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <svg
              class="h-5 w-5 text-yellow-400 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clip-rule="evenodd"
              ></path>
            </svg>
            <span
              class="text-sm font-medium text-yellow-800 dark:text-yellow-200"
            >
              게스트 모드로 접속중입니다. 모임 조회만 가능하며, 참가 신청 및
              모임 생성은 할 수 없습니다.
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto py-4 sm:py-6 px-4 sm:px-6 lg:px-8">
      <div class="sm:px-0">
        <!-- Ads Banner (replacing statistics cards) -->
        <div class="mb-6 sm:mb-8">
          <AdsBanner :meetups="bannerMeetups" @banner-click="handleBannerClick" />
        </div>

        <!-- 필터 섹션 -->
        <div
          class="bg-white dark:bg-gray-800 overflow-hidden shadow-lg rounded-xl border border-gray-200 dark:border-gray-700 mb-6"
        >
          <div class="p-4 sm:p-6">
            <div
              class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2 sm:mb-4"
            >
              <!-- Mobile: Collapsible header -->
              <div class="sm:hidden w-full">
                <button
                  @click="showMobileFilters = !showMobileFilters"
                  class="flex items-center justify-between w-full text-base sm:text-lg font-medium text-gray-900 dark:text-white py-1.5 sm:py-2"
                >
                  <span>필터</span>
                  <svg
                    :class="[
                      'w-5 h-5 transform transition-transform',
                      showMobileFilters ? 'rotate-180' : '',
                    ]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
              </div>

              <!-- Desktop: Regular header -->
              <div
                class="hidden sm:flex sm:items-center sm:justify-between w-full"
              >
                <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                  필터
                </h3>
              </div>
            </div>
            <!-- Filter content - collapsible on mobile -->
            <div v-show="showMobileFilters" class="sm:!block">

              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 sm:gap-4">
                <!-- 년도 필터 -->
                <div>
                  <label
                    class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                    >년도</label
                  >
                  <CustomSelect
                    v-model="filters.year"
                    :options="yearOptions"
                    placeholder="모든 년도"
                  />
                </div>

                <!-- 월 필터 -->
                <div>
                  <label
                    class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                    >월</label
                  >
                  <CustomSelect
                    v-model="filters.month"
                    :options="monthOptions"
                    placeholder="모든 월"
                  />
                </div>

                <!-- 상태 필터 -->
                <div>
                  <label
                    class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                    >상태</label
                  >
                  <CustomSelect
                    v-model="filters.status"
                    :options="statusOptions"
                    placeholder="모든 상태"
                  />
                </div>

                <!-- 해시태그 필터 -->
                <div>
                  <label
                    class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                    >해시태그</label
                  >
                  <CustomSelect
                    v-model="filters.hashtag"
                    :options="hashtagOptions"
                    placeholder="모든 해시태그"
                  />
                </div>

                <!-- 검색 -->
                <div>
                  <label
                    class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                    >검색</label
                  >
                  <input
                    v-model="filters.search"
                    type="text"
                    placeholder="모임명 또는 장소 검색"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-gray-700 dark:text-gray-100 dark:placeholder-gray-400"
                  />
                </div>

                <!-- 필터 액션 버튼들 -->
                <div class="flex items-end gap-2">
                  <button
                    @click="applyFilters"
                    class="flex-1 px-3 py-2 text-primary-700 bg-primary-100 hover:bg-primary-200 dark:bg-primary-900 dark:text-primary-300 dark:hover:bg-primary-800 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v18" />
                    </svg>
                    적용
                  </button>
                  <button
                    @click="clearFilters"
                    class="flex-1 px-3 py-2 text-red-700 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    초기화
                  </button>
                </div>
              </div>

              <!-- 필터 결과 표시 -->
              <div class="mt-6 border-t border-gray-200 dark:border-gray-700 pt-4">
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div class="flex items-center gap-2">
                    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 px-3 py-2 rounded-lg border border-blue-200 dark:border-blue-800">
                      <span class="text-sm font-medium text-blue-700 dark:text-blue-300">
                        {{ filteredMeetups.length }}개 모임 발견
                      </span>
                      <span class="text-xs text-blue-600 dark:text-blue-400 ml-1">
                        (전체 {{ totalMeetups }}개 중)
                      </span>
                    </div>
                  </div>

                  <!-- 적용된 필터 태그들 -->
                  <div v-if="hasActiveFilters" class="flex flex-wrap gap-1.5">
                      <!-- 년도 필터 -->
                      <div
                        v-if="appliedFilters.year"
                        class="inline-flex items-center bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/30 border border-amber-200 dark:border-amber-800 rounded-md px-2 py-1 shadow-sm hover:shadow transition-all duration-200"
                      >
                        <svg
                          class="w-2.5 h-2.5 text-amber-600 dark:text-amber-400 mr-1"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                          ></path>
                        </svg>
                        <span
                          class="text-xs font-medium text-amber-700 dark:text-amber-300"
                          >{{ appliedFilters.year }}년</span
                        >
                        <button
                          @click="
                            appliedFilters.year = '';
                            filters.year = '';
                          "
                          class="ml-1 w-4 h-4 flex items-center justify-center rounded-full hover:bg-amber-200 dark:hover:bg-amber-800 text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-200 transition-colors"
                        >
                          <svg
                            class="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M6 18L18 6M6 6l12 12"
                            ></path>
                          </svg>
                        </button>
                      </div>

                      <!-- 월 필터 -->
                      <div
                        v-if="appliedFilters.month"
                        class="inline-flex items-center bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/30 dark:to-teal-900/30 border border-emerald-200 dark:border-emerald-800 rounded-md px-2 py-1 shadow-sm hover:shadow transition-all duration-200"
                      >
                        <svg
                          class="w-2.5 h-2.5 text-emerald-600 dark:text-emerald-400 mr-1"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                          ></path>
                        </svg>
                        <span
                          class="text-xs font-medium text-emerald-700 dark:text-emerald-300"
                          >{{ getMonthLabel(appliedFilters.month) }}</span
                        >
                        <button
                          @click="
                            appliedFilters.month = '';
                            filters.month = '';
                          "
                          class="ml-1 w-4 h-4 flex items-center justify-center rounded-full hover:bg-emerald-200 dark:hover:bg-emerald-800 text-emerald-600 dark:text-emerald-400 hover:text-emerald-800 dark:hover:text-emerald-200 transition-colors"
                        >
                          <svg
                            class="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M6 18L18 6M6 6l12 12"
                            ></path>
                          </svg>
                        </button>
                      </div>

                      <!-- 상태 필터 -->
                      <div
                        v-if="appliedFilters.status"
                        class="inline-flex items-center bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/30 dark:to-purple-900/30 border border-violet-200 dark:border-violet-800 rounded-md px-2 py-1 shadow-sm hover:shadow transition-all duration-200"
                      >
                        <svg
                          class="w-2.5 h-2.5 text-violet-600 dark:text-violet-400 mr-1"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
                          ></path>
                        </svg>
                        <span
                          class="text-xs font-medium text-violet-700 dark:text-violet-300"
                          >{{ getStatusLabel(appliedFilters.status) }}</span
                        >
                        <button
                          @click="
                            appliedFilters.status = '';
                            filters.status = '';
                          "
                          class="ml-1 w-4 h-4 flex items-center justify-center rounded-full hover:bg-violet-200 dark:hover:bg-violet-800 text-violet-600 dark:text-violet-400 hover:text-violet-800 dark:hover:text-violet-200 transition-colors"
                        >
                          <svg
                            class="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M6 18L18 6M6 6l12 12"
                            ></path>
                          </svg>
                        </button>
                      </div>

                      <!-- 검색 필터 -->
                      <div
                        v-if="appliedFilters.search"
                        class="inline-flex items-center bg-gradient-to-r from-rose-50 to-pink-50 dark:from-rose-900/30 dark:to-pink-900/30 border border-rose-200 dark:border-rose-800 rounded-md px-2 py-1 shadow-sm hover:shadow transition-all duration-200"
                      >
                        <svg
                          class="w-2.5 h-2.5 text-rose-600 dark:text-rose-400 mr-1"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                          ></path>
                        </svg>
                        <span
                          class="text-xs font-medium text-rose-700 dark:text-rose-300"
                          >"{{ appliedFilters.search }}"</span
                        >
                        <button
                          @click="
                            appliedFilters.search = '';
                            filters.search = '';
                          "
                          class="ml-1 w-4 h-4 flex items-center justify-center rounded-full hover:bg-rose-200 dark:hover:bg-rose-800 text-rose-600 dark:text-rose-400 hover:text-rose-800 dark:hover:text-rose-200 transition-colors"
                        >
                          <svg
                            class="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M6 18L18 6M6 6l12 12"
                            ></path>
                          </svg>
                        </button>
                      </div>

                      <!-- 해시태그 필터 -->
                      <div
                        v-if="appliedFilters.hashtag"
                        class="inline-flex items-center bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-900/30 dark:to-blue-900/30 border border-indigo-200 dark:border-indigo-800 rounded-md px-2 py-1 shadow-sm hover:shadow transition-all duration-200"
                      >
                        <svg
                          class="w-2.5 h-2.5 text-indigo-600 dark:text-indigo-400 mr-1"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                          ></path>
                        </svg>
                        <span
                          class="text-xs font-medium text-indigo-700 dark:text-indigo-300"
                          >{{ appliedFilters.hashtag }}</span
                        >
                        <button
                          @click="
                            appliedFilters.hashtag = '';
                            filters.hashtag = '';
                          "
                          class="ml-1 w-4 h-4 flex items-center justify-center rounded-full hover:bg-indigo-200 dark:hover:bg-indigo-800 text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200 transition-colors"
                        >
                          <svg
                            class="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M6 18L18 6M6 6l12 12"
                            ></path>
                          </svg>
                        </button>
                      </div>

                      <!-- 모든 필터 초기화 버튼 -->
                      <button
                        @click="clearFilters"
                        class="inline-flex items-center bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 text-xs font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 shadow-sm hover:shadow transition-all duration-200"
                      >
                        <svg
                          class="w-2.5 h-2.5 mr-1"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          ></path>
                        </svg>
                        모두 지우기
                      </button>
                    </div>
                  </div>
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
                    : 'text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700',
                ]"
                title="캘린더 보기"
              >
                <svg
                  class="h-5 w-5"
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
              </button>
              <button
                @click="activeView = 'table'"
                :class="[
                  'p-2 rounded-md transition-colors',
                  activeView === 'table'
                    ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300'
                    : 'text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700',
                ]"
                title="테이블 보기"
              >
                <svg
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M3 10h18M3 14h18m-9-4v8m-7 0V4a1 1 0 011-1h14a1 1 0 011 1v16a1 1 0 01-1 1H4a1 1 0 01-1-1z"
                  />
                </svg>
              </button>
            </div>

            <!-- 실제 뷰 컴포넌트 -->
            <div :class="{ '-mx-4 sm:mx-0': activeView === 'calendar' }">
              <CalendarView
                v-if="activeView === 'calendar'"
                :meetups="filteredMeetups"
              />
              <MeetupTable
                v-if="activeView === 'table'"
                :meetups="filteredMeetups"
                tableCentered
              />
            </div>
        </div>
      </div>
    </div>
    
    <!-- Meetup Detail Modal -->
    <MeetupDetailModal
      v-if="showMeetupModal"
      :selectedMeetup="selectedMeetup"
      @close="closeMeetupModal"
      @meetupUpdated="handleMeetupUpdated"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useMeetupsStore } from "@/stores/meetups";
import CalendarView from "@/components/CalendarView.vue";
import MeetupTable from "@/components/MeetupTable.vue";
import ThemeToggle from "@/components/ThemeToggle.vue";
import AdsBanner from "@/components/AdsBanner.vue";
import MeetupDetailModal from "@/components/MeetupDetailModal.vue";
import CustomSelect from "@/components/CustomSelect.vue";

export default {
  name: "DashboardView",
  components: {
    CalendarView,
    MeetupTable,
    ThemeToggle,
    AdsBanner,
    MeetupDetailModal,
    CustomSelect,
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const meetupsStore = useMeetupsStore();
    const activeView = ref("calendar");
    const showMobileFilters = ref(false); // Collapsed by default on mobile
    
    // Modal state
    const selectedMeetup = ref(null)
    const showMeetupModal = ref(false)

    // 필터 상태 - 사용자가 입력하는 값
    const filters = ref({
      year: "",
      month: "",
      status: "",
      search: "",
      hashtag: "",
    });

    // 실제로 적용된 필터 - 버튼을 눌렀을 때만 업데이트
    const appliedFilters = ref({
      year: "",
      month: "",
      status: "",
      search: "",
      hashtag: "",
    });

    // 월 데이터
    const months = [
      { value: "1", label: "1월" },
      { value: "2", label: "2월" },
      { value: "3", label: "3월" },
      { value: "4", label: "4월" },
      { value: "5", label: "5월" },
      { value: "6", label: "6월" },
      { value: "7", label: "7월" },
      { value: "8", label: "8월" },
      { value: "9", label: "9월" },
      { value: "10", label: "10월" },
      { value: "11", label: "11월" },
      { value: "12", label: "12월" },
    ];

    // 사용 가능한 년도 목록
    const availableYears = computed(() => {
      const years = new Set();
      meetupsStore.meetups.forEach((meetup) => {
        const year = new Date(meetup.date_time).getFullYear();
        years.add(year);
      });
      return Array.from(years).sort((a, b) => b - a);
    });

    // 사용 가능한 해시태그 목록
    const availableHashtags = computed(() => {
      const hashtags = new Set();
      meetupsStore.meetups.forEach((meetup) => {
        if (meetup.hashtags_list && Array.isArray(meetup.hashtags_list)) {
          meetup.hashtags_list.forEach((hashtag) => {
            hashtags.add(hashtag);
          });
        }
      });
      return Array.from(hashtags).sort();
    });

    // CustomSelect용 포맷된 옵션들
    const yearOptions = computed(() => [
      { value: "", label: "모든 년도" },
      ...availableYears.value.map(year => ({
        value: year.toString(),
        label: `${year}년`
      }))
    ]);

    const monthOptions = computed(() => [
      { value: "", label: "모든 월" },
      ...months
    ]);

    const statusOptions = computed(() => [
      { value: "", label: "모든 상태" },
      { value: "upcoming", label: "예정된 모임" },
      { value: "ongoing", label: "진행 중" },
      { value: "completed", label: "완료된 모임" },
      { value: "available", label: "참가 가능" },
      { value: "full", label: "정원 마감" }
    ]);

    const hashtagOptions = computed(() => [
      { value: "", label: "모든 해시태그" },
      ...availableHashtags.value.map(hashtag => ({
        value: hashtag,
        label: hashtag
      }))
    ]);

    // 필터링된 모임 목록
    const filteredMeetups = computed(() => {
      let filtered = [...sortedMeetups.value];

      console.log("Original meetups count:", filtered.length);
      console.log("Applied filters:", appliedFilters.value);

      // 년도 필터
      if (appliedFilters.value.year) {
        const beforeCount = filtered.length;
        console.log("Year filter debug:");
        console.log(
          "- Applied year filter:",
          appliedFilters.value.year,
          "type:",
          typeof appliedFilters.value.year
        );

        filtered = filtered.filter((meetup) => {
          const meetupYear = new Date(meetup.date_time)
            .getFullYear()
            .toString();
          const matches = meetupYear === appliedFilters.value.year;
          console.log(
            `- Meetup: ${meetup.name}, date_time: ${
              meetup.date_time
            }, parsed year: ${meetupYear} (type: ${typeof meetupYear}), matches: ${matches}`
          );
          return matches;
        });
        console.log(
          `Year filter (${appliedFilters.value.year}): ${beforeCount} -> ${filtered.length}`
        );
      }

      // 월 필터
      if (appliedFilters.value.month) {
        const beforeCount = filtered.length;
        filtered = filtered.filter((meetup) => {
          const meetupMonth = (
            new Date(meetup.date_time).getMonth() + 1
          ).toString();
          return meetupMonth === appliedFilters.value.month;
        });
        console.log(
          `Month filter (${appliedFilters.value.month}): ${beforeCount} -> ${filtered.length}`
        );
      }

      // 상태 필터
      if (appliedFilters.value.status) {
        const beforeCount = filtered.length;
        const now = new Date();
        filtered = filtered.filter((meetup) => {
          const meetupDate = new Date(meetup.date_time);
          const meetupEndDate = meetup.end_time
            ? new Date(meetup.end_time)
            : new Date(meetup.date_time);

          switch (appliedFilters.value.status) {
            case "upcoming":
              return meetupDate > now;
            case "ongoing":
              return meetupDate <= now && meetupEndDate > now;
            case "completed":
              return meetupEndDate <= now;
            case "available":
              return (
                (meetup.current_participants || 0) <
                (meetup.max_participants || 0)
              );
            case "full":
              return (
                (meetup.current_participants || 0) >=
                (meetup.max_participants || 0)
              );
            default:
              return true;
          }
        });
        console.log(
          `Status filter (${appliedFilters.value.status}): ${beforeCount} -> ${filtered.length}`
        );
      }

      // 검색 필터
      if (appliedFilters.value.search) {
        const beforeCount = filtered.length;
        const searchTerm = appliedFilters.value.search.toLowerCase().trim();
        if (searchTerm) {
          filtered = filtered.filter(
            (meetup) =>
              (meetup.name && meetup.name.toLowerCase().includes(searchTerm)) ||
              (meetup.location &&
                meetup.location.toLowerCase().includes(searchTerm)) ||
              (meetup.description &&
                meetup.description.toLowerCase().includes(searchTerm))
          );
        }
        console.log(
          `Search filter (${appliedFilters.value.search}): ${beforeCount} -> ${filtered.length}`
        );
      }

      // 해시태그 필터
      if (appliedFilters.value.hashtag) {
        const beforeCount = filtered.length;
        filtered = filtered.filter((meetup) => {
          if (meetup.hashtags_list && Array.isArray(meetup.hashtags_list)) {
            return meetup.hashtags_list.includes(appliedFilters.value.hashtag);
          }
          return false;
        });
        console.log(
          `Hashtag filter (${appliedFilters.value.hashtag}): ${beforeCount} -> ${filtered.length}`
        );
      }

      console.log("Final filtered count:", filtered.length);
      return filtered;
    });

    // 필터 적용
    const applyFilters = () => {
      appliedFilters.value = {
        year: filters.value.year,
        month: filters.value.month,
        status: filters.value.status,
        search: filters.value.search,
        hashtag: filters.value.hashtag,
      };
      console.log("Filters applied:", appliedFilters.value);
      // Collapse on mobile after applying to reduce header height
      showMobileFilters.value = false;
    };

    // 필터 초기화
    const clearFilters = () => {
      filters.value = {
        year: "",
        month: "",
        status: "",
        search: "",
        hashtag: "",
      };
      appliedFilters.value = {
        year: "",
        month: "",
        status: "",
        search: "",
        hashtag: "",
      };
    };

    // 활성 필터가 있는지 확인
    const hasActiveFilters = computed(() => {
      return !!(
        appliedFilters.value.year ||
        appliedFilters.value.month ||
        appliedFilters.value.status ||
        appliedFilters.value.search ||
        appliedFilters.value.hashtag
      );
    });

    // 라벨 헬퍼 함수들
    const getMonthLabel = (monthValue) => {
      const month = months.find((m) => m.value === monthValue);
      return month ? month.label : monthValue;
    };

    const getStatusLabel = (status) => {
      const statusLabels = {
        upcoming: "예정된 모임",
        ongoing: "진행 중",
        completed: "완료된 모임",
        available: "참가 가능",
        full: "정원 마감",
      };
      return statusLabels[status] || status;
    };

    // 전체 모임 수 (for filter display)
    const totalMeetups = computed(() => meetupsStore.meetups.length);

    // 배너용: 종료되지 않은(미종료) 모임만 선택, 시작일 오름차순으로 최대 5개
    const bannerMeetups = computed(() => {
      const now = new Date()
      const open = meetupsStore.meetups.filter((m) => {
        const end = m.end_time ? new Date(m.end_time) : new Date(m.date_time)
        return end > now
      })
      open.sort((a, b) => new Date(a.date_time) - new Date(b.date_time))
      return open.slice(0, 5)
    })

    // 정렬된 모임 목록: 모집중(시작 임박순) -> 종료된 모임(종료일 오름차순)
    const sortedMeetups = computed(() => {
      const now = new Date();
      // 모집중(아직 끝나지 않은) 모임
      const ongoing = meetupsStore.meetups.filter((m) => {
        const end = m.end_time ? new Date(m.end_time) : new Date(m.date_time);
        return end > now;
      });
      // 종료된 모임
      const ended = meetupsStore.meetups.filter((m) => {
        const end = m.end_time ? new Date(m.end_time) : new Date(m.date_time);
        return end <= now;
      });
      // 모집중 모임은 시작일 오름차순, 종료된 모임은 종료일 오름차순
      ongoing.sort((a, b) => new Date(a.date_time) - new Date(b.date_time));
      ended.sort((a, b) => {
        const aEnd = a.end_time ? new Date(a.end_time) : new Date(a.date_time);
        const bEnd = b.end_time ? new Date(b.end_time) : new Date(b.date_time);
        return aEnd - bEnd;
      });
      return [...ongoing, ...ended];
    });

    const upcomingMeetups = computed(() => {
      const now = new Date();
      return meetupsStore.meetups.filter((meetup) => {
        const meetupDate = new Date(meetup.date_time);
        return meetupDate > now;
      }).length;
    });

    const totalCapacity = computed(() => {
      return meetupsStore.meetups.reduce(
        (sum, meetup) => sum + meetup.max_participants,
        0
      );
    });

    const totalRegistered = computed(() => {
      return meetupsStore.meetups.reduce(
        (sum, meetup) => sum + meetupsStore.getRegistrationCount(meetup.id),
        0
      );
    });

    const availableSeats = computed(() => {
      return totalCapacity.value - totalRegistered.value;
    });

    const fullMeetups = computed(() => {
      return meetupsStore.meetups.filter((meetup) =>
        meetupsStore.isMeetupFull(meetup.id)
      ).length;
    });

    const averageAttendance = computed(() => {
      if (totalCapacity.value === 0) return 0;
      return Math.round((totalRegistered.value / totalCapacity.value) * 100);
    });

    const formatDateTime = (dateTimeString) => {
      const date = new Date(dateTimeString);
      return date.toLocaleDateString("ko-KR", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    const logout = async () => {
      await authStore.logout();
      router.push("/login");
    };
    
    // Handle ads banner click
    const handleBannerClick = (adData) => {
      // Prefer full meetup data from store to include image, etc.
      const storeMeetup = meetupsStore.meetups.find(m => m.id === adData.id)
      if (storeMeetup) {
        selectedMeetup.value = storeMeetup
      } else {
        // Fallback to minimal object from banner
        selectedMeetup.value = {
          id: adData.id,
          name: adData.title,
          description: adData.description,
          date_time: adData.dateTime,
          location: adData.location,
          current_participants: adData.currentParticipants,
          max_participants: adData.maxParticipants,
          creator_name: "한입 모임",
          creator_email: "contact@hangbeon.com",
          hashtags_list: adData.hashtags || [],
          image_display_url: null,
          end_time: null
        }
      }
      showMeetupModal.value = true
    }
    
    // Handle modal close
    const closeMeetupModal = () => {
      showMeetupModal.value = false
      selectedMeetup.value = null
    }
    
    // Handle meetup updates from modal
    const handleMeetupUpdated = () => {
      // Refresh meetups data if needed
      meetupsStore.fetchMeetups()
    }

    onMounted(async () => {
      authStore.checkAuth();
      // Small delay to ensure session is fully established after login
      await new Promise((resolve) => setTimeout(resolve, 100));
      await meetupsStore.fetchMeetups();
    });

    return {
      authStore,
      meetupsStore,
      activeView,
      totalMeetups,
      bannerMeetups,
      formatDateTime,
      logout,
      sortedMeetups,
      // 필터 관련
      filters,
      appliedFilters,
      filteredMeetups,
      availableYears,
      availableHashtags,
      months,
      // CustomSelect용 옵션들
      yearOptions,
      monthOptions,
      statusOptions,
      hashtagOptions,
      applyFilters,
      clearFilters,
      getMonthLabel,
      getStatusLabel,
      hasActiveFilters,
      showMobileFilters,
      // Modal
      selectedMeetup,
      showMeetupModal,
      handleBannerClick,
      closeMeetupModal,
      handleMeetupUpdated,
    };
  },
};
</script>
