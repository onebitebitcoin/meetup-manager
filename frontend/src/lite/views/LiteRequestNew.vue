<template>
  <LiteTopbar
    title="이런 모임 열어주세요"
    back
    :back-to="backTo"
  >
    <span />
  </LiteTopbar>
  <form
    class="l-body"
    @submit.prevent="submit"
  >
    <input
      v-model="title"
      class="l-big-input"
      maxlength="60"
      placeholder="어떤 모임?"
      aria-label="모임 주제"
    >
    <div
      class="l-seg"
      role="radiogroup"
      aria-label="원하는 시기"
    >
      <label
        v-for="(label, value) in PERIOD_LABEL"
        :key="value"
      >
        <input
          v-model="period"
          type="radio"
          name="period"
          :value="value"
        >
        <span>{{ label }}</span>
      </label>
    </div>
    <button
      class="l-btn p"
      type="submit"
      :disabled="busy"
    >
      올리기
    </button>
  </form>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { liteApi } from '../api'
import { PERIOD_LABEL } from '../format'
import { useLiteStore } from '../store'
import LiteTopbar from '../components/LiteTopbar.vue'

const router = useRouter()
const store = useLiteStore()
const title = ref('')
const period = ref('next_month')
const busy = ref(false)
// 방문자는 홈의 문의 메뉴에서 바로 오고, 운영자는 요청 목록에서 온다
const backTo = computed(() => (store.isHost ? '/requests' : '/'))

const submit = async () => {
  const trimmed = title.value.trim()
  if (!trimmed) {
    store.notify('모임 주제를 입력해 주세요', 'error')
    return
  }
  busy.value = true
  // 이름 없이 들어온 방문자는 올리는 순간 자동 닉네임으로 가입한다
  if (!(await store.ensureMember())) {
    busy.value = false
    return
  }
  const data = await store.act(() => liteApi.createRequest(trimmed, period.value), '요청을 올렸어요')
  busy.value = false
  if (data) router.push(backTo.value)
}
</script>
