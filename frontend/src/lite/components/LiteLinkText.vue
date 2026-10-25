<template>
  <template
    v-for="(part, i) in parts"
    :key="i"
  >
    <a
      v-if="part.type === 'link'"
      class="l-link"
      :href="part.href"
      target="_blank"
      rel="noopener noreferrer"
    >{{ part.text }}</a>
    <template v-else>
      {{ part.text }}
    </template>
  </template>
</template>

<script setup>
import { computed } from 'vue'
import { splitLinks } from '../linkify'

const props = defineProps({ text: { type: String, required: true } })
const parts = computed(() => splitLinks(props.text))
</script>
