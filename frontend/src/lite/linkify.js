const URL_PATTERN = /(?:https?:\/\/|www\.)[^\s<]+/gi
const TRAILING = /[.,)!?;:]+$/

// 본문을 텍스트/링크 조각으로 나눈다. 끝의 문장부호는 링크에서 빼서 텍스트로 돌려준다.
export const splitLinks = (text) => {
  const parts = []
  let last = 0
  const push = (part) => { if (part.text) parts.push(part) }
  for (const match of text.matchAll(URL_PATTERN)) {
    const link = match[0].replace(TRAILING, '')
    if (!link) continue
    push({ type: 'text', text: text.slice(last, match.index) })
    const href = /^www\./i.test(link) ? `https://${link}` : link
    parts.push({ type: 'link', text: link, href })
    last = match.index + link.length
  }
  push({ type: 'text', text: text.slice(last) })
  return parts
}

export const firstLink = (text) => splitLinks(text).find((p) => p.type === 'link')?.href ?? null
