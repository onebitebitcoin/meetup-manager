<template>
  <div class="l-state">
    확인 중
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLiteStore } from '../store'

const route = useRoute()
const router = useRouter()
const store = useLiteStore()

onMounted(async () => {
  if (!store.member) store.notify('이름을 먼저 입력해 주세요', 'error')
  else await store.claimHost(route.params.key)
  router.replace('/lite')
})
</script>
