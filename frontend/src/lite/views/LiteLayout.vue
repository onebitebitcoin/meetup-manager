<template>
  <div class="lite-root">
    <div class="lite-shell">
      <div
        v-if="!store.ready"
        class="l-state"
      >
        불러오는 중
      </div>
      <router-view v-else />
      <LiteToast />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useLiteStore } from '../store'
import LiteToast from '../components/LiteToast.vue'
import '../lite.css'

const store = useLiteStore()

onMounted(() => store.init())
</script>
