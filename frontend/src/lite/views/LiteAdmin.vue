<template>
  <LiteTopbar
    title="관리"
    back
  >
    <span />
  </LiteTopbar>
  <div class="l-body">
    <div class="l-seg two">
      <label
        v-for="tab in TABS"
        :key="tab.value"
      >
        <input
          v-model="scope"
          type="radio"
          name="scope"
          :value="tab.value"
        >
        <span>{{ tab.label }}</span>
      </label>
    </div>
    <button
      class="l-btn s"
      @click="router.push('/lite/new-meetup')"
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
      @click="router.push(`/lite/admin/m/${meetup.id}`)"
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
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Users } from 'lucide-vue-next'
import { liteApi } from '../api'
import { dateParts } from '../format'
import { useLiteStore } from '../store'
import LiteTopbar from '../components/LiteTopbar.vue'

const TABS = [{ value: 'upcoming', label: '다가오는' }, { value: 'past', label: '지난' }]

const router = useRouter()
const store = useLiteStore()
const scope = ref('upcoming')
const meetups = ref([])
const error = ref('')
const loaded = ref(false)

const partsOf = (meetup) => dateParts(meetup.starts_at)

const load = async () => {
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

onMounted(() => {
  if (!store.isHost) {
    router.replace('/lite')
    return
  }
  load()
})
watch(scope, load)
</script>
