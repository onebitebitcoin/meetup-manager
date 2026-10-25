export const MAX_UPLOAD_BYTES = 10 * 1024 * 1024

export const formatSize = (bytes) => {
  if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)}MB`
  return `${Math.max(1, Math.round(bytes / 1024))}KB`
}

// 공지 바처럼 한 줄로 줄여 보일 때 쓰는 첨부 요약
export const attachmentLabel = (attachment) => (
  attachment.kind === 'image' ? '사진' : `파일 · ${attachment.name}`
)
