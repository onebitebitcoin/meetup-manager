<template>
  <LiteOnboard v-if="!store.member" />
  <template v-else>
    <LiteTopbar :title="tab === 'requests' ? '모임 요청' : '모임'" />
    <div class="lite-scroll">
      <LiteRequestList v-if="tab === 'requests'" />
      <div
        v-else
        class="l-body"
      >
        <LiteSeminarCard
          v-if="!store.isHost"
          :seminar="home.my_seminar"
        />
        <LiteSeminarCard
          v-for="seminar in sortedSeminars"
          :key="seminar.id"
          :seminar="seminar"
          host
        />
        <button
          v-if="store.isHost"
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
          v-if="loaded && !home.meetups.length"
          class="l-state"
        >
          예정된 모임이 없어요
        </p>
        <LiteMeetupCard
          v-for="meetup in home.meetups"
          :key="meetup.id"
          :meetup="meetup"
          @changed="load"
        />
      </div>
    </div>
    <nav class="l-nav">
      <button
        :aria-current="tab === 'meetups' ? 'page' : 'false'"
        @click="setTab('meetups')"
      >
        <CalendarDays :size="22" />모임
      </button>
      <button
        :aria-current="tab === 'requests' ? 'page' : 'false'"
        @click="setTab('requests')"
      >
        <Hand :size="22" />요청
        <span
          v-if="store.isHost && home.ready_request_count"
          class="l-dot"
        >{{ home.ready_request_count }}</span>
      </button>
    </nav>
  </template>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CalendarDays, Hand, Plus } from 'lucide-vue-next'
import { liteApi } from '../api'
import { useLiteStore } from '../store'
import LiteMeetupCard from '../components/LiteMeetupCard.vue'
import LiteOnboard from '../components/LiteOnboard.vue'
import LiteRequestList from '../components/LiteRequestList.vue'
import LiteSeminarCard from '../components/LiteSeminarCard.vue'
import LiteTopbar from '../components/LiteTopbar.vue'

const route = useRoute()
const router = useRouter()
const store = useLiteStore()
const home = ref({ meetups: [], my_seminar: null, seminars: [], ready_request_count: 0 })
const error = ref('')
const loaded = ref(false)

const tab = computed(() => (route.query.tab === 'requests' ? 'requests' : 'meetups'))
const SEMINAR_ORDER = { received: 0, guide: 1, confirmed: 2 }
const sortedSeminars = computed(() => [...home.value.seminars].sort((a, b) => SEMINAR_ORDER[a.status] - SEMINAR_ORDER[b.status]))

const setTab = (next) => router.replace({ path: '/lite', query: next === 'requests' ? { tab: next } : {} })

const load = async () => {
  if (!store.member) return
  try {
    home.value = await liteApi.home()
    error.value = ''
    loaded.value = true
  } catch (e) {
    error.value = e.message
    store.notify(e.message, 'error')
  }
}

onMounted(load)
watch(() => store.member, load)
</script>
