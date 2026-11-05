<template>
  <LiteTopbar
    title="관리"
    back
  >
    <span />
  </LiteTopbar>
  <form
    v-if="!store.isHost"
    class="l-body"
    @submit.prevent="submitLogin"
  >
    <input
      v-model="password"
      class="l-big-input"
      type="password"
      autocomplete="current-password"
      placeholder="비밀번호"
      aria-label="운영자 비밀번호"
    >
    <button
      class="l-btn p"
      type="submit"
      :disabled="busy"
    >
      들어가기
    </button>
  </form>
  <div
    v-else
    class="l-body"
  >
    <button
      class="l-btn s"
      @click="router.push('/admin/settings')"
    >
      <Settings :size="18" />설정
    </button>
    <div class="l-seg two">
      <label
        v-for="item in MAIN_TABS"
        :key="item.value"
      >
        <input
          type="radio"
          name="tab"
          :value="item.value"
          :checked="tab === item.value"
          @change="selectTab(item.value)"
        >
        <span>{{ item.label }}</span>
      </label>
    </div>
    <LiteAdminChats v-if="tab === 'chat'" />
    <template v-else>
      <div class="l-seg two">
        <label
          v-for="item in TABS"
          :key="item.value"
        >
          <input
            v-model="scope"
            type="radio"
            name="scope"
            :value="item.value"
          >
          <span>{{ item.label }}</span>
        </label>
      </div>
      <button
        class="l-btn s"
        @click="router.push('/new-meetup')"
      >
        <Plus :size="18" />모임 만들기
      </button>
      <p
        v-if="error"
        class="l-state"
      >
        {{ error }}
      </p>
      <p
        v-else-if="!loaded"
        class="l-state"
      >
        불러오는 중
      </p>
      <p
        v-else-if="!meetups.length"
        class="l-state"
      >
        모임이 없어요
      </p>
      <button
        v-for="meetup in meetups"
        :key="meetup.id"
        class="l-row-btn"
        @click="router.push(`/admin/m/${meetup.id}`)"
      >
        <div class="l-date">
          <span>{{ partsOf(meetup).month }}월</span>
          <b>{{ partsOf(meetup).day }}</b>
          <span>{{ partsOf(meetup).weekday }}</span>
        </div>
        <div class="l-grow">
          <div class="l-title">
            {{ meetup.title }}
          </div>
          <div class="l-sub">
            <span
              v-if="meetup.cancelled"
              class="l-chip no"
            >취소됨</span>
            <span class="l-counts">
              <Users :size="13" />{{ meetup.going_count }}/{{ meetup.capacity }}
            </span>
          </div>
        </div>
      </button>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Settings, Users } from 'lucide-vue-next'
import { liteApi } from '../api'
import { dateParts } from '../format'
import { useLiteStore } from '../store'
import LiteAdminChats from '../components/LiteAdminChats.vue'
import LiteTopbar from '../components/LiteTopbar.vue'

const TABS = [{ value: 'upcoming', label: '다가오는' }, { value: 'past', label: '지난' }]

const MAIN_TABS = [{ value: 'meetup', label: '모임' }, { value: 'chat', label: '채팅' }]

const route = useRoute()
const router = useRouter()
const store = useLiteStore()
// 탭은 ?tab= 쿼리로 유지한다. 채팅방의 뒤로 버튼은 ?from=admin이 있을 때 /admin?tab=chat으로 돌아온다
const tab = ref(route.query.tab === 'chat' ? 'chat' : 'meetup')
const scope = ref('upcoming')
const meetups = ref([])
const error = ref('')
const loaded = ref(false)
const password = ref('')
const busy = ref(false)

const selectTab = (value) => {
  tab.value = value
  router.replace({ query: value === 'chat' ? { tab: 'chat' } : {} })
}

const partsOf = (meetup) => dateParts(meetup.starts_at)

const load = async () => {
  if (!store.isHost || tab.value !== 'meetup') return
  loaded.value = false
  try {
    meetups.value = (await liteApi.adminMeetups(scope.value)).meetups
    error.value = ''
  } catch (e) {
    meetups.value = []
    error.value = e.message
    store.notify(e.message, 'error')
  }
  loaded.value = true
}

const submitLogin = async () => {
  if (!password.value) {
    store.notify('비밀번호를 입력해 주세요', 'error')
    return
  }
  busy.value = true
  const ok = await store.adminLogin(password.value)
  busy.value = false
  password.value = ''
  if (ok) load()
}

// store.ready는 LiteLayout이 기다린 뒤에 이 화면을 그리므로, 여기서 isHost는 이미 확정된 값이다
onMounted(load)
watch([scope, tab], load)
</script>
