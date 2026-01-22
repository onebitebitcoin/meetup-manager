<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-950 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 헤더 -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          📚 <한입 모임> 사용 가이드
        </h1>
        <p class="text-lg text-gray-600 dark:text-neutral-300">
          모임 관리 플랫폼의 다양한 기능을 알아보세요
        </p>
        <div class="mt-4">
          <router-link
            to="/dashboard"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors duration-200"
          >
            <svg
              class="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            대시보드로 돌아가기
          </router-link>
        </div>
      </div>

      <!-- 목차 -->
      <div class="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-gray-200 dark:border-neutral-700 p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          📋 목차
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <a href="#getting-started" class="text-blue-600 dark:text-blue-400 hover:underline">1. 시작하기</a>
          <a href="#dashboard" class="text-blue-600 dark:text-blue-400 hover:underline">2. 대시보드 사용법</a>
          <a href="#create-meetup" class="text-blue-600 dark:text-blue-400 hover:underline">3. 모임 만들기</a>
          <a href="#join-meetup" class="text-blue-600 dark:text-blue-400 hover:underline">4. 모임 참가하기</a>
          <a href="#waitlist" class="text-blue-600 dark:text-blue-400 hover:underline">5. 대기열 시스템</a>
          <a href="#notifications" class="text-blue-600 dark:text-blue-400 hover:underline">6. 알림 관리</a>
          <a href="#settings" class="text-blue-600 dark:text-blue-400 hover:underline">7. 설정 관리</a>
        </div>
      </div>

      <!-- 섹션들 -->
      <div class="space-y-8">
        <!-- 시작하기 -->
        <section id="getting-started" class="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-gray-200 dark:border-neutral-700 p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            🚀 1. 시작하기
          </h2>
          <div class="space-y-4 text-gray-600 dark:text-neutral-300">
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                회원가입
              </h3>
              <p>• 이름, 이메일, 비밀번호를 입력하여 계정을 생성하세요</p>
              <p>• 이메일은 중복될 수 없으며, 비밀번호는 안전하게 암호화됩니다</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                로그인
              </h3>
              <p>• 등록한 이메일과 비밀번호로 로그인하세요</p>
              <p>• 로그인 후 자동으로 대시보드로 이동합니다</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                게스트 로그인
              </h3>
              <p>• 회원가입 없이 '게스트로 둘러보기'를 클릭하여 기능을 체험할 수 있습니다</p>
              <p>• 게스트는 모임 조회만 가능하며, 참가나 생성은 할 수 없습니다</p>
            </div>
          </div>
        </section>

        <!-- 대시보드 -->
        <section id="dashboard" class="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-gray-200 dark:border-neutral-700 p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            🏠 2. 대시보드 사용법
          </h2>
          <div class="space-y-4 text-gray-600 dark:text-neutral-300">
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                모임 보기 방식
              </h3>
              <p>• <strong>달력 보기:</strong> 월별 캘린더에서 모임 일정을 한눈에 확인</p>
              <p>• <strong>목록 보기:</strong> 모임을 리스트 형태로 상세 정보와 함께 확인</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                검색 및 필터
              </h3>
              <p>• 모임 이름으로 검색하여 원하는 모임을 빠르게 찾기</p>
              <p>• 카테고리별로 필터링하여 관심 있는 주제의 모임만 보기</p>
              <p>• 참가 상태별로 필터링 (참가 중, 대기 중, 전체)</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                모임 정보 확인
              </h3>
              <p>• 각 모임의 제목, 날짜, 시간, 장소, 참가자 수를 확인</p>
              <p>• 모임을 클릭하면 상세 정보 모달이 열립니다</p>
            </div>
          </div>
        </section>

        <!-- 모임 만들기 -->
        <section id="create-meetup" class="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-gray-200 dark:border-neutral-700 p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            ➕ 3. 모임 만들기
          </h2>
          <div class="space-y-4 text-gray-600 dark:text-neutral-300">
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                모임 생성 폼
              </h3>
              <p>• <strong>모임 이름:</strong> 명확하고 매력적인 제목을 작성하세요</p>
              <p>• <strong>설명:</strong> 모임의 목적, 내용, 준비사항 등을 자세히 설명</p>
              <p>• <strong>날짜와 시간:</strong> 정확한 일정을 설정하세요</p>
              <p>• <strong>장소:</strong> 구체적인 위치 정보를 입력</p>
              <p>• <strong>최대 참가자 수:</strong> 적절한 인원수를 설정</p>
              <p>• <strong>카테고리:</strong> 모임 주제에 맞는 카테고리 선택</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                이미지 업로드
              </h3>
              <p>• 모임을 대표하는 이미지를 업로드할 수 있습니다</p>
              <p>• JPG, PNG 형식을 지원하며, 5MB 이하의 파일만 업로드 가능</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                모임 관리
              </h3>
              <p>• 생성한 모임은 자동으로 본인이 참가자로 등록됩니다</p>
              <p>• 모임 생성자는 참가자 관리 권한을 갖습니다</p>
            </div>
          </div>
        </section>

        <!-- 모임 참가하기 -->
        <section id="join-meetup" class="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-gray-200 dark:border-neutral-700 p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            🤝 4. 모임 참가하기
          </h2>
          <div class="space-y-4 text-gray-600 dark:text-neutral-300">
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                참가 신청
              </h3>
              <p>• 관심 있는 모임을 클릭하여 상세 정보를 확인</p>
              <p>• "참가하기" 버튼을 클릭하여 모임에 참가 신청</p>
              <p>• 인원이 가득 찬 경우 자동으로 대기열에 등록됩니다</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                참가 취소
              </h3>
              <p>• 참가 중인 모임에서 "참가 취소" 버튼으로 참가를 취소할 수 있습니다</p>
              <p>• 참가 취소 시 대기열의 다음 사람이 자동으로 승격됩니다</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                모임 정보 확인
              </h3>
              <p>• 참가자 목록에서 다른 참가자들을 확인할 수 있습니다</p>
              <p>• 모임 생성자는 참가자 관리 기능을 사용할 수 있습니다</p>
            </div>
          </div>
        </section>

        <!-- 대기열 시스템 -->
        <section id="waitlist" class="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-gray-200 dark:border-neutral-700 p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            ⏳ 5. 대기열 시스템
          </h2>
          <div class="space-y-4 text-gray-600 dark:text-neutral-300">
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                대기열 등록
              </h3>
              <p>• 모임 정원이 가득 찬 경우 자동으로 대기열에 등록됩니다</p>
              <p>• 대기열에서의 순서는 등록 순서에 따라 결정됩니다</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                자동 승격
              </h3>
              <p>• 기존 참가자가 취소하면 대기열의 첫 번째 사람이 자동으로 참가자가 됩니다</p>
              <p>• 승격 시 알림을 통해 참가 확정을 안내받습니다</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                대기열 취소
              </h3>
              <p>• "대기 취소" 버튼을 클릭하여 언제든지 대기열에서 나올 수 있습니다</p>
              <p>• 대기 순서는 취소 후 자동으로 재조정됩니다</p>
            </div>
          </div>
        </section>

        <!-- 알림 관리 -->
        <section id="notifications" class="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-gray-200 dark:border-neutral-700 p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            🔔 6. 알림 관리
          </h2>
          <div class="space-y-4 text-gray-600 dark:text-neutral-300">
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                알림 유형
              </h3>
              <p>• <strong>대기열 승격:</strong> 대기열에서 참가자로 승격된 경우</p>
              <p>• <strong>모임 알림:</strong> 모임 생성자가 보내는 공지사항</p>
              <p>• <strong>일반 알림:</strong> 시스템에서 보내는 기타 알림</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                알림 확인
              </h3>
              <p>• 설정 페이지에서 알림 카드를 클릭하여 알림 목록을 확인</p>
              <p>• 읽지 않은 알림은 파란색으로 표시됩니다</p>
              <p>• 알림을 클릭하면 자동으로 읽음 처리됩니다</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                알림 관리
              </h3>
              <p>• "모두 읽음" 버튼으로 모든 알림을 한번에 읽음 처리</p>
              <p>• 개별 알림 삭제 또는 전체 알림 삭제 가능</p>
              <p>• 알림은 페이지네이션으로 관리됩니다</p>
            </div>
          </div>
        </section>

        <!-- 설정 관리 -->
        <section id="settings" class="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-gray-200 dark:border-neutral-700 p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            ⚙️ 7. 설정 관리
          </h2>
          <div class="space-y-4 text-gray-600 dark:text-neutral-300">
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                계정 정보
              </h3>
              <p>• 내 계정 정보를 확인하고 필요시 수정할 수 있습니다</p>
              <p>• 이름과 이메일 정보가 표시됩니다</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                참여 통계
              </h3>
              <p>• <strong>총 참여자:</strong> 전체 등록된 사용자 수</p>
              <p>• <strong>활성 모임:</strong> 현재 진행 중인 모임 수</p>
              <p>• <strong>내 참가 모임:</strong> 내가 참가한 모임 수</p>
              <p>• <strong>알림:</strong> 읽지 않은 알림 수</p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2">
                테마 설정
              </h3>
              <p>• 다크 모드와 라이트 모드 간 전환 가능</p>
              <p>• 기본값은 다크 모드로 설정되어 있습니다</p>
              <p>• 테마 설정은 브라우저에 저장됩니다</p>
            </div>
          </div>
        </section>

        <!-- 추가 팁 -->
        <section id="additional-tips" class="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-gray-200 dark:border-neutral-700 p-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            💡 추가 팁
          </h2>
          <div class="space-y-4 text-gray-600 dark:text-neutral-300">
            <p>• <strong>모바일 친화적:</strong> 모든 기능이 모바일에서도 원활하게 작동합니다</p>
            <p>• <strong>실시간 업데이트:</strong> 다른 사용자의 참가/취소가 실시간으로 반영됩니다</p>
            <p>• <strong>검색 활용:</strong> 키워드 검색으로 원하는 모임을 빠르게 찾을 수 있습니다</p>
            <p>• <strong>정확한 정보:</strong> 모임 생성 시 정확한 정보를 입력하면 참가율이 높아집니다</p>
            <p>• <strong>예의:</strong> 참가 확정 후 무단 불참은 다른 참가자에게 피해가 됩니다</p>
          </div>
        </section>

        <!-- 문의 -->
        <section class="bg-gray-50 dark:bg-neutral-800/50 rounded-lg border border-gray-200 dark:border-neutral-700 p-6 text-center">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-3">
            ❓ 더 궁금한 것이 있으신가요?
          </h2>
          <p class="text-gray-600 dark:text-neutral-300 mb-4">
            사용 중 문제가 발생하거나 추가 문의사항이 있으시면 언제든지 연락주세요.
          </p>
          <div class="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4 mb-4">
            <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-2">
              📧 문의하기
            </h3>
            <p class="text-blue-800 dark:text-blue-300 mb-2">
              기술적 문제, 기능 제안, 또는 기타 문의사항이 있으시면 아래 이메일로 연락해주세요:
            </p>
            <p class="text-blue-800 dark:text-blue-300 font-medium">
              📧 <a href="mailto:onebitebitcoin@proton.me" class="text-blue-600 dark:text-blue-400 hover:underline">onebitebitcoin@proton.me</a>
            </p>
          </div>
          <p class="text-sm text-gray-500 dark:text-neutral-400">
            이 가이드는 계속 업데이트되며, 새로운 기능이 추가되면 반영됩니다.
          </p>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HelpView',
  mounted() {
    // 페이지 로드 시 URL 해시로 자동 스크롤
    if (this.$route.hash) {
      this.$nextTick(() => {
        const element = document.querySelector(this.$route.hash)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' })
        }
      })
    }
  },
}
</script>

<style scoped>
/* 부드러운 스크롤 */
html {
  scroll-behavior: smooth;
}

/* 섹션 제목에 앵커 링크 공간 확보 */
section {
  scroll-margin-top: 2rem;
}
</style>
