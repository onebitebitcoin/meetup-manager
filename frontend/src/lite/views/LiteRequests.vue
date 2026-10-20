<template>
  <LiteTopbar
    title="모임 요청"
    back
  >
    <span />
  </LiteTopbar>
  <div
    v-if="store.member"
    class="lite-scroll"
  >
    <LiteRequestList />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useLiteStore } from '../store'
import LiteRequestList from '../components/LiteRequestList.vue'
import LiteTopbar from '../components/LiteTopbar.vue'

const store = useLiteStore()

onMounted(() => store.ensureMember())
</script>
