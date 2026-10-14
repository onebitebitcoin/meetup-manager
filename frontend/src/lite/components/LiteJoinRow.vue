<template>
  <div class="l-btn-row">
    <button
      class="l-btn p"
      :disabled="busy"
      @click.stop="choose('going')"
    >
      {{ meetup.my_status === 'no' ? '다시 신청하기' : '신청하기' }}
    </button>
    <button
      v-if="meetup.my_status !== 'no'"
      class="l-btn s fit"
      :disabled="busy"
      @click.stop="choose('no')"
    >
      못 가요
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { liteApi } from '../api'
import { useLiteStore } from '../store'

const props = defineProps({ meetup: { type: Object, required: true } })
const emit = defineEmits(['done'])

const store = useLiteStore()
const busy = ref(false)

const choose = async (status) => {
  if (busy.value) return
  busy.value = true
  const data = await store.act(
    () => liteApi.rsvp(props.meetup.id, status),
    status === 'going' ? '신청했어요' : '불참으로 표시했어요',
  )
  busy.value = false
  if (data) emit('done', { status, meetup: data.meetup })
}
</script>
