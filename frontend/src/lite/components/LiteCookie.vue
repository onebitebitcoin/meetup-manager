<template>
  <svg
    viewBox="0 0 48 48"
    width="24"
    height="24"
    aria-hidden="true"
  >
    <template v-if="filled">
      <circle
        cx="24"
        cy="24"
        r="20"
        fill="#E2A55A"
        stroke="var(--lite-line)"
        stroke-width="3"
      />
      <circle
        v-for="[x, y, r] in CHIPS"
        :key="`${x}-${y}`"
        :cx="x"
        :cy="y"
        :r="r"
        fill="#2B1A17"
      />
    </template>
    <circle
      v-else
      cx="24"
      cy="24"
      r="19"
      fill="none"
      stroke="var(--lite-hair)"
      stroke-width="3"
      stroke-dasharray="5 4"
    />
  </svg>
</template>

<script setup>
defineProps({ filled: { type: Boolean, default: false } })

const CHIPS = [[15, 20, 2.6], [22, 34, 2.6], [32, 28, 2.6], [13, 31, 2], [27, 16, 2]]
</script>
