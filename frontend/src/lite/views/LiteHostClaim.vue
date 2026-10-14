<template>
  <LiteOnboard v-if="!store.member" />
  <div
    v-else
    class="l-state"
  >
    확인 중
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { takeHash } from '../format'
import { useLiteStore } from '../store'
import LiteOnboard from '../components/LiteOnboard.vue'

const router = useRouter()
const store = useLiteStore()
const key = takeHash()

// 이름이 없으면 온보딩을 거쳐 member가 생긴 뒤에 claim을 호출한다
let claiming = false
const claim = async () => {
  if (claiming) return
  claiming = true
  await store.claimHost(key)
  router.replace('/lite')
}

onMounted(() => {
  if (!key) router.replace('/lite')
  else if (store.member) claim()
})
watch(() => store.member, (member) => {
  if (member && key) claim()
})
</script>
