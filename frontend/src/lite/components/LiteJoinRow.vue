<template>
  <div :class="compact ? 'l-join-compact' : 'l-btn-row'">
    <button
      :class="compact ? 'l-pill-btn go' : 'l-btn go'"
      :disabled="busy"
      @click.stop="join"
    >
      참석하기
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { liteApi } from '../api'
import { useLiteStore } from '../store'

const props = defineProps({
  meetup: { type: Object, required: true },
  // 다음 모임 카드의 세션 줄 오른쪽에 들어가는 작은 버튼으로 그린다
  compact: { type: Boolean, default: false },
})
const emit = defineEmits(['done'])

const store = useLiteStore()
const busy = ref(false)

// 처음 온 방문자는 자동 닉네임으로 가입한 뒤 바로 신청한다
const join = async () => {
  if (busy.value) return
  busy.value = true
  if (!(await store.ensureMember())) {
    busy.value = false
    return
  }
  const data = await store.act(() => liteApi.rsvp(props.meetup.id, 'going'), '참석 신청했어요', 'going')
  busy.value = false
  if (data) emit('done', { status: 'going', meetup: data.meetup })
}
</script>
