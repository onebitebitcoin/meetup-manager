<template>
  <span
    class="l-progress"
    role="img"
    :aria-label="`${total}명 중 ${Math.min(count, total)}명`"
  >
    <i
      v-for="n in total"
      :key="n"
      :class="{ on: n <= count }"
    />
  </span>
</template>

<script setup>
defineProps({
  count: { type: Number, required: true },
  total: { type: Number, required: true },
})
</script>
