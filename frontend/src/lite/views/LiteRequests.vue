<template>
  <LiteTopbar
    title="모임 요청"
    back
  >
    <span />
  </LiteTopbar>
  <div class="lite-scroll">
    <LiteRequestList />
  </div>
</template>

<script setup>
import LiteRequestList from '../components/LiteRequestList.vue'
import LiteTopbar from '../components/LiteTopbar.vue'
</script>
