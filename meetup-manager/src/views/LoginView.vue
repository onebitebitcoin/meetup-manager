<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 py-6 sm:py-12 px-4 sm:px-6 lg:px-8 safe-area-top safe-area-bottom"
  >
    <div class="max-w-md w-full space-y-6 sm:space-y-8">
      <!-- 테마 토글 버튼 -->
      <div class="flex justify-end">
        <ThemeToggle />
      </div>

      <div>
        <div class="text-center mb-6 tablet:mb-8">
          <h1
            class="text-2xl xs:text-3xl tablet:text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2"
          >
            한번 모임
          </h1>
          <p class="text-sm xs:text-base text-gray-600 dark:text-gray-400">
            환영합니다! 계속하려면 로그인해주세요
          </p>
          <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          또는
          <router-link
            to="/register"
            class="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
          >
            새 계정 만들기
          </router-link>
        </p>
        </div>

        
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm space-y-3">
          <div>
            <label for="email" class="sr-only">이메일</label>
            <input
              id="email"
              v-model="form.email"
              name="email"
              type="email"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-800 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="이메일 주소"
            />
          </div>
          <div>
            <label for="password" class="sr-only">비밀번호</label>
            <input
              id="password"
              v-model="form.password"
              name="password"
              type="password"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-800 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="비밀번호"
            />
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="form.remember"
              name="remember-me"
              type="checkbox"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label
              for="remember-me"
              class="ml-2 block text-sm text-gray-900 dark:text-gray-300"
            >
              로그인 상태 유지
            </label>
          </div>
        </div>

        <div class="space-y-3">
          <button
            type="submit"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            로그인
          </button>

          <button
            type="button"
            @click="handleGuestLogin"
            class="group relative w-full flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            게스트로 입장
          </button>
        </div>

        <div class="text-center space-y-2">
          <p class="text-xs text-gray-500 dark:text-gray-400">
            게스트 모드: 모임 조회만 가능, 생성/참가 불가
          </p>
          <div>
            <router-link
              to="/help"
              class="text-xs text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 underline"
            >
              📚 사용 가이드 보기
            </router-link>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import ThemeToggle from "@/components/ThemeToggle.vue";
import { fetchWithCSRF } from "@/utils/csrf";

export default {
  name: "LoginView",
  components: {
    ThemeToggle,
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    const form = reactive({
      email: "",
      password: "",
      remember: false,
    });

    const handleLogin = async () => {
      try {
        console.log("Starting login process...");

        const response = await fetchWithCSRF("/api/auth/login/", {
          method: "POST",
          body: JSON.stringify({
            username: form.email,
            password: form.password,
          }),
        });

        console.log("Login response status:", response.status);

        if (response.ok) {
          const data = await response.json();
          const userData = {
            id: data.user.id,
            name: data.user.name,
            email: data.user.email,
            username: data.user.username,
            is_admin: data.user.is_admin,
            is_guest: false,
          };

          await authStore.login(userData);

          // Small delay to ensure authentication state is fully established
          await new Promise((resolve) => setTimeout(resolve, 100));

          if (userData.is_admin) {
            router.push("/admin");
          } else {
            router.push("/dashboard");
          }
        } else {
          const errorData = await response.json();
          alert(errorData.error || "로그인에 실패했습니다");
        }
      } catch (error) {
        alert("네트워크 오류가 발생했습니다. 다시 시도해주세요.");
      }
    };

    const handleGuestLogin = async () => {
      try {
        const guestUserData = {
          id: "guest",
          name: "게스트 사용자",
          email: "guest@example.com",
          username: "guest",
          is_admin: false,
          is_guest: true,
        };

        await authStore.login(guestUserData);
        router.push("/dashboard");
      } catch (error) {
        alert("게스트 로그인에 실패했습니다.");
      }
    };

    return {
      form,
      handleLogin,
      handleGuestLogin,
    };
  },
};
</script>
