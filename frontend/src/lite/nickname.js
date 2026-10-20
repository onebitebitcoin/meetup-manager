// 처음 온 방문자에게 이름을 묻지 않고 "친근한 형용사 + 동물/곤충" 닉네임을 붙여 준다
const ADJECTIVES = [
  '느긋한', '다정한', '씩씩한', '수줍은', '용감한', '졸린', '배고픈', '반짝이는',
  '포근한', '명랑한', '꼼꼼한', '엉뚱한', '날쌘', '상냥한', '든든한', '호기심 많은',
  '부지런한', '해맑은', '말랑한', '느릿한', '깜찍한', '유쾌한', '차분한', '설레는',
]

const CREATURES = [
  '수달', '고양이', '강아지', '판다', '다람쥐', '토끼', '고슴도치', '펭귄',
  '부엉이', '너구리', '햄스터', '코알라', '알파카', '돌고래', '여우', '오리',
  '꿀벌', '무당벌레', '나비', '반딧불이', '개미', '잠자리', '달팽이', '사슴벌레',
]

const pick = (list, random) => list[Math.floor(random() * list.length)]

// suffix: 이름이 겹쳐 여러 번 실패했을 때 뒤에 붙이는 두 자리 숫자
export const randomNickname = ({ suffix = false, random = Math.random } = {}) => {
  const base = `${pick(ADJECTIVES, random)} ${pick(CREATURES, random)}`
  return suffix ? `${base}${10 + Math.floor(random() * 90)}` : base
}
