<template>
  <div class="l-state">
    복구 중
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { takeHash } from '../format'
import { useLiteStore } from '../store'

const router = useRouter()
const store = useLiteStore()

onMounted(async () => {
  const token = takeHash()
  if (!token) store.notify('복구 링크가 올바르지 않아요', 'error')
  else if (await store.recover(token)) store.notify(`${store.member.name}님, 반가워요`)
  router.replace('/lite')
})
</script>
