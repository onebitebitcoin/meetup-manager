<template>
  <button
    type="button"
    role="switch"
    class="l-switch"
    :class="going ? 'going' : 'no'"
    :aria-checked="going"
    :aria-label="`${meetup.title} 참석`"
    :disabled="busy"
    @click="toggle"
  >
    <span class="l-switch-track"><span class="l-switch-thumb" /></span>
    <span class="l-switch-label">{{ going ? '참석' : '불참' }}</span>
  </button>
</template>

<script setup>
import { computed, ref } from 'vue'
import { liteApi } from '../api'
import { useLiteStore } from '../store'

// 홈의 참석 스위치. 아직 응답하지 않은 모임도 꺼진 불참 상태로 보이고, 켜면 참석으로 신청한다.
// 이름이 없는 방문자는 켜는 순간 자동 닉네임으로 가입한다.
const props = defineProps({ meetup: { type: Object, required: true } })
// 응답을 바꾸면 홈이 목록을 다시 불러오도록 알린다
const emit = defineEmits(['changed'])

const store = useLiteStore()
const busy = ref(false)
const going = computed(() => props.meetup.my_status === 'going')

const toggle = async () => {
  if (busy.value) return
  const next = going.value ? 'no' : 'going'
  busy.value = true
  if (!(await store.ensureMember())) {
    busy.value = false
    return
  }
  const data = await store.act(() => liteApi.rsvp(props.meetup.id, next), next === 'going' ? '참석으로 바꿨어요' : '불참으로 바꿨어요')
  busy.value = false
  if (data) emit('changed')
}
</script>
