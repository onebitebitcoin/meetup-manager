<template>
  <a
    v-if="preview"
    class="l-lp"
    :href="preview.url"
    target="_blank"
    rel="noopener noreferrer"
  >
    <img
      v-if="preview.image"
      class="l-lp-img"
      :src="preview.image"
      alt=""
      loading="lazy"
      @load="emit('loaded')"
    >
    <span class="l-lp-text">
      <span
        v-if="preview.site_name"
        class="l-lp-site"
      >{{ preview.site_name }}</span>
      <span
        v-if="preview.title"
        class="l-lp-title"
      >{{ preview.title }}</span>
      <span
        v-if="preview.description"
        class="l-lp-desc"
      >{{ preview.description }}</span>
    </span>
  </a>
</template>

<script>
// URL별 결과 캐시. null(미리보기 없음)도 저장해 같은 링크를 다시 조회하지 않는다.
const cache = new Map()
</script>

<script setup>
import { onMounted, ref } from 'vue'
import { liteApi } from '../api'

const props = defineProps({ url: { type: String, required: true } })
const emit = defineEmits(['loaded'])
const preview = ref(null)

// 부가 기능이므로 실패해도 카드만 그리지 않고 토스트는 띄우지 않는다
const load = () => {
  if (!cache.has(props.url)) {
    cache.set(props.url, liteApi.linkPreview(props.url).then((data) => data?.preview ?? null, () => null))
  }
  return cache.get(props.url)
}

onMounted(async () => {
  preview.value = await load()
  if (preview.value) emit('loaded')
})
</script>
