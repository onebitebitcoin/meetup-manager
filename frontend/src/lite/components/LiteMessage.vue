<template>
  <div
    v-if="message.kind === 'system'"
    class="l-sys"
  >
    {{ message.body }}
  </div>
  <div
    v-else-if="message.kind === 'guide'"
    class="l-msg bot"
  >
    <span class="l-av bot"><Megaphone :size="15" /></span>
    <div class="l-bub">
      {{ message.body }}
    </div>
  </div>
  <div
    v-else
    class="l-msg"
    :class="{ mine }"
  >
    <span
      v-if="!mine"
      class="l-av"
    >{{ message.member?.name?.slice(0, 1) }}</span>
    <div>
      <div
        v-if="!mine"
        class="l-who"
      >
        {{ message.member?.name }}
      </div>
      <div class="l-bub">
        {{ message.body }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { Megaphone } from 'lucide-vue-next'

defineProps({
  message: { type: Object, required: true },
  mine: { type: Boolean, default: false },
})
</script>
