<template>
  <div
    class="l-card link pinned"
    role="button"
    tabindex="0"
    @click="open"
    @keydown.enter="open"
  >
    <div class="l-row center">
      <div class="l-date always">
        <GraduationCap :size="24" />
      </div>
      <div class="l-grow">
        <div class="l-title">
          1:1 · {{ seminar.member.name }}
        </div>
        <div class="l-sub">
          <span
            v-if="seminar.mode"
            class="l-chip plum"
          >
            {{ MODE_LABEL[seminar.mode] }}
          </span>
          <span
            v-if="seminar.status !== 'guide'"
            class="l-chip"
            :class="STATUS_CLASS[seminar.status]"
          >
            {{ SEMINAR_STATUS_LABEL[seminar.status] }}
          </span>
        </div>
      </div>
      <ChevronRight :size="18" />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ChevronRight, GraduationCap } from 'lucide-vue-next'
import { MODE_LABEL, SEMINAR_STATUS_LABEL } from '../format'

// 운영자 홈에 세미나 대화별로 놓는 카드. 일반 회원은 플로팅 버튼(LiteFab)으로 들어간다.
const props = defineProps({ seminar: { type: Object, required: true } })

const STATUS_CLASS = { guide: 'none', received: 'maybe', confirmed: 'going' }
const router = useRouter()

const open = () => router.push(`/lite/seminar/${props.seminar.id}`)
</script>
