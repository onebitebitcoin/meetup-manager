<template>
  <div class="l-state">
    확인 중
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { takeHash } from '../format'
import { useLiteStore } from '../store'

const router = useRouter()
const store = useLiteStore()
const key = takeHash()

// 이름이 없으면 자동 닉네임으로 가입해 member가 생긴 뒤에 claim을 호출한다
const claim = async () => {
  await store.claimHost(key)
  router.replace('/lite')
}

onMounted(async () => {
  if (!key) router.replace('/lite')
  else if (await store.ensureMember()) claim()
})
</script>
