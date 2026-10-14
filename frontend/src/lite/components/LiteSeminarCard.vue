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
          {{ host ? `1:1 · ${seminar.member.name}` : '1:1 세미나' }}
        </div>
        <div class="l-sub">
          <span
            v-if="!seminar"
            class="l-chip plum"
          >
            <Pin :size="12" />언제든
          </span>
          <template v-else>
            <span
              v-if="seminar.mode"
              class="l-chip plum"
            >
              {{ MODE_LABEL[seminar.mode] }}
            </span>
            <span
              class="l-chip"
              :class="STATUS_CLASS[seminar.status]"
            >
              {{ SEMINAR_STATUS_LABEL[seminar.status] }}
            </span>
          </template>
        </div>
      </div>
      <ChevronRight :size="18" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronRight, GraduationCap, Pin } from 'lucide-vue-next'
import { MODE_LABEL, SEMINAR_STATUS_LABEL } from '../format'

// seminar가 없으면 아직 시작하지 않은 내 1:1 세미나 진입 카드다. 운영자는 대화별 카드를 쓴다.
const props = defineProps({
  seminar: { type: Object, default: null },
  host: { type: Boolean, default: false },
})

const STATUS_CLASS = { guide: 'none', received: 'maybe', confirmed: 'going' }
const router = useRouter()

const path = computed(() => (props.host ? `/lite/seminar/${props.seminar.id}` : '/lite/seminar'))
const open = () => router.push(path.value)
</script>
