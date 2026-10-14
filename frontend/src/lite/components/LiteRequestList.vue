<template>
  <div class="l-body">
    <button
      class="l-btn p"
      @click="router.push('/lite/new-request')"
    >
      <Plus :size="18" />이런 모임 열어주세요
    </button>
    <p
      v-if="error"
      class="l-state"
    >
      {{ error }}
    </p>
    <LiteRequestCard
      v-for="request in requests"
      :key="request.id"
      :request="request"
      @updated="replace"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from 'lucide-vue-next'
import { liteApi } from '../api'
import LiteRequestCard from './LiteRequestCard.vue'

const router = useRouter()
const requests = ref([])
const error = ref('')

const replace = (next) => {
  requests.value = requests.value.map((r) => (r.id === next.id ? next : r))
}

onMounted(async () => {
  try {
    requests.value = (await liteApi.requests()).requests
  } catch (e) {
    error.value = e.message
  }
})
</script>
