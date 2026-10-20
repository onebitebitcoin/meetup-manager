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
    :class="{ cont: !head }"
  >
    <span
      class="l-av bot"
      :class="{ ghost: !head }"
    ><Megaphone :size="15" /></span>
    <div class="l-bub-row">
      <div class="l-bub">
        {{ message.body }}
      </div>
      <span
        v-if="time"
        class="l-time"
      >{{ time }}</span>
    </div>
  </div>
  <div
    v-else
    class="l-msg"
    :class="{ mine, cont: !head }"
  >
    <span
      v-if="!mine"
      class="l-av"
      :class="{ ghost: !head }"
    >{{ message.member?.name?.slice(0, 1) }}</span>
    <div>
      <div
        v-if="!mine && head"
        class="l-who"
      >
        {{ message.member?.name }}
      </div>
      <div class="l-bub-row">
        <div class="l-bub">
          {{ message.body }}
        </div>
        <span
          v-if="time"
          class="l-time"
        >{{ time }}</span>
      </div>
      <div
        v-if="showMenu && menuOpen"
        class="l-msg-menu"
      >
        <template v-if="!confirming">
          <button
            type="button"
            @click="emit('pin')"
          >
            공지로 고정
          </button>
          <button
            type="button"
            class="danger"
            @click="confirming = true"
          >
            <Trash2 :size="16" />삭제
          </button>
        </template>
        <template v-else>
          <span>삭제할까요?</span>
          <button
            type="button"
            class="danger"
            @click="emit('delete')"
          >
            <Trash2 :size="16" />삭제
          </button>
          <button
            type="button"
            @click="confirming = false"
          >
            그만두기
          </button>
        </template>
      </div>
    </div>
    <button
      v-if="showMenu"
      type="button"
      class="l-msg-more"
      aria-label="메시지 관리"
      :aria-expanded="menuOpen"
      @click="emit('toggle-menu')"
    >
      <MoreHorizontal :size="18" />
    </button>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Megaphone, MoreHorizontal, Trash2 } from 'lucide-vue-next'
import { useLiteStore } from '../store'

const props = defineProps({
  message: { type: Object, required: true },
  mine: { type: Boolean, default: false },
  head: { type: Boolean, default: true },
  time: { type: String, default: '' },
  menuOpen: { type: Boolean, default: false },
})
const emit = defineEmits(['toggle-menu', 'pin', 'delete'])

const store = useLiteStore()
const confirming = ref(false)
const showMenu = computed(() => store.isHost && props.message.kind === 'user')

// 메뉴가 닫히면 삭제 확인 단계도 처음으로 돌린다
watch(() => props.menuOpen, (open) => { if (!open) confirming.value = false })
</script>
