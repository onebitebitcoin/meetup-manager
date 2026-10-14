<template>
  <div class="l-state">
    복구 중
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
  store.setToken(route.params.token)
  await store.init()
  if (store.member) store.notify(`${store.member.name}님, 반가워요`)
  else store.notify('복구 링크가 올바르지 않아요', 'error')
  router.replace('/lite')
})
</script>
