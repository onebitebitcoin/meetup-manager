<template>
  <LiteTopbar title="한입 모임">
    <button
      v-if="store.isHost"
      class="l-icon-btn"
      aria-label="관리"
      @click="router.push('/admin')"
    >
      <Settings :size="20" />
    </button>
  </LiteTopbar>
  <div class="lite-scroll">
    <div
      class="l-body l-home"
      :class="{ 'l-body-fab': !store.isHost && store.isOpen }"
    >
      <div
        v-if="store.isHost && loaded"
        class="l-bar"
      >
        <component
          :is="store.isOpen ? LockOpen : Lock"
          :size="18"
        />
        <span class="l-grow">{{ store.isOpen ? '오픈 중이에요' : '오픈 전이에요 · 운영자만 써요' }}</span>
        <button
          class="l-btn"
          :class="store.isOpen ? 's' : 'p'"
          :disabled="toggling"
          @click="toggleOpen"
        >
          {{ store.isOpen ? '닫기' : '오픈하기' }}
        </button>
      </div>
      <p
        v-if="!store.canJoin && loaded"
        class="l-state"
      >
        오픈 준비 중이에요
      </p>
      <template v-if="store.isHost">
        <LiteSeminarCard
          v-for="seminar in sortedSeminars"
          :key="seminar.id"
          :seminar="seminar"
        />
        <LiteRequestEntry :ready-count="home.ready_request_count" />
      </template>
      <button
        v-if="store.isHost"
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
        v-if="loaded && !home.meetups.length"
        class="l-state"
      >
        예정된 모임이 없어요
      </p>
      <LiteNextCard
        v-if="split.next.length"
        :meetups="split.next"
        @changed="load"
      />
      <template v-if="split.rest.length">
        <h3 class="l-section">
          다가오는 모임
        </h3>
        <div class="l-mlist">
          <LiteMeetupRow
            v-for="meetup in split.rest"
            :key="meetup.id"
            :meetup="meetup"
            @changed="load"
          />
        </div>
      </template>
    </div>
  </div>
  <LiteFab
    v-if="!store.isHost && store.isOpen"
    :seminar="home.my_seminar"
  />
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Lock, LockOpen, Plus, Settings } from 'lucide-vue-next'
import { liteApi } from '../api'
import { splitNextMeetups } from '../format'
import { useLiteStore } from '../store'
import LiteFab from '../components/LiteFab.vue'
import LiteMeetupRow from '../components/LiteMeetupRow.vue'
import LiteNextCard from '../components/LiteNextCard.vue'
import LiteRequestEntry from '../components/LiteRequestEntry.vue'
import LiteSeminarCard from '../components/LiteSeminarCard.vue'
import LiteTopbar from '../components/LiteTopbar.vue'

const router = useRouter()
const store = useLiteStore()
const home = ref({ meetups: [], my_seminar: null, seminars: [], ready_request_count: 0 })
const error = ref('')
const loaded = ref(false)
const toggling = ref(false)

const SEMINAR_ORDER = { received: 0, guide: 1, confirmed: 2 }
const split = computed(() => splitNextMeetups(home.value.meetups))
const sortedSeminars = computed(() => [...home.value.seminars].sort((a, b) => SEMINAR_ORDER[a.status] - SEMINAR_ORDER[b.status]))

const load = async () => {
  try {
    home.value = await liteApi.home()
    store.isOpen = home.value.is_open
    error.value = ''
    loaded.value = true
  } catch (e) {
    error.value = e.message
    store.notify(e.message, 'error')
  }
}

const toggleOpen = async () => {
  toggling.value = true
  const next = !store.isOpen
  const data = await store.act(() => liteApi.setOpen(next), next ? '오픈했어요' : '오픈 전으로 닫았어요')
  toggling.value = false
  if (data) store.isOpen = data.is_open
}

onMounted(load)
watch(() => store.member, load)
</script>
