<template>
  <LiteTopbar
    title="설정"
    back
    back-to="/admin"
  >
    <span />
  </LiteTopbar>
  <div class="l-body">
    <p
      v-if="error"
      class="l-state"
    >
      {{ error }}
    </p>
    <p
      v-else-if="!values"
      class="l-state"
    >
      불러오는 중
    </p>
    <form
      v-else
      class="l-body"
      @submit.prevent="save"
    >
      <label
        v-for="field in FIELDS"
        :key="field.key"
        class="l-section"
      >
        <span>{{ field.label }}</span>
        <input
          v-if="field.number"
          v-model.number="values[field.key]"
          class="l-field"
          type="number"
          inputmode="numeric"
          min="1"
        >
        <textarea
          v-else
          v-model="values[field.key]"
          class="l-field"
          rows="4"
          maxlength="1000"
        />
      </label>
      <button
        class="l-btn p"
        type="submit"
        :disabled="busy"
      >
        저장
      </button>
    </form>
    <form
      class="l-body"
      @submit.prevent="changePassword"
    >
      <h3 class="l-section">
        비밀번호 바꾸기
      </h3>
      <input
        v-model="currentPassword"
        class="l-field"
        type="password"
        autocomplete="current-password"
        placeholder="현재 비밀번호"
        aria-label="현재 비밀번호"
      >
      <input
        v-model="newPassword"
        class="l-field"
        type="password"
        autocomplete="new-password"
        placeholder="새 비밀번호 (8자 이상)"
        aria-label="새 비밀번호"
      >
      <button
        class="l-btn s"
        type="submit"
        :disabled="passwordBusy"
      >
        비밀번호 바꾸기
      </button>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { liteApi } from '../api'
import { useLiteStore } from '../store'
import LiteTopbar from '../components/LiteTopbar.vue'

const FIELDS = [
  { key: 'vote_threshold', label: '모임 개설 투표 기준 인원', number: true },
  { key: 'seminar_guide_1', label: '세미나 안내 1' },
  { key: 'seminar_guide_2', label: '세미나 안내 2' },
  { key: 'seminar_guide_3', label: '세미나 안내 3' },
  { key: 'seminar_guide_4', label: '세미나 접수 후 안내' },
  { key: 'join_guide', label: '참석 안내' },
]

const router = useRouter()
const store = useLiteStore()
const values = ref(null)
const error = ref('')
const busy = ref(false)
const currentPassword = ref('')
const newPassword = ref('')
const passwordBusy = ref(false)

const load = async () => {
  try {
    values.value = await liteApi.adminSettings()
    error.value = ''
  } catch (e) {
    values.value = null
    error.value = e.message
    store.notify(e.message, 'error')
  }
}

const save = async () => {
  busy.value = true
  const data = await store.act(() => liteApi.updateAdminSettings(values.value), '저장했어요')
  busy.value = false
  if (data) values.value = data
}

const changePassword = async () => {
  if (!currentPassword.value || !newPassword.value) {
    store.notify('현재 비밀번호와 새 비밀번호를 입력해 주세요', 'error')
    return
  }
  passwordBusy.value = true
  const data = await store.act(
    () => liteApi.changeAdminPassword(currentPassword.value, newPassword.value),
    '비밀번호를 바꿨어요',
  )
  passwordBusy.value = false
  if (data) {
    currentPassword.value = ''
    newPassword.value = ''
  }
}

onMounted(() => {
  if (!store.isHost) {
    router.replace('/admin')
    return
  }
  load()
})
</script>
