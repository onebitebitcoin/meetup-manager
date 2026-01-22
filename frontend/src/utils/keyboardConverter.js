/**
 * Korean to English keyboard converter utility
 * Converts Korean characters typed on English keyboard layout to their English equivalents
 */

/**
 * Convert Korean characters to English based on keyboard layout mapping.
 * 
 * Korean QWERTY layout maps to English QWERTY as follows:
 * ㅂ->q, ㅈ->w, ㄷ->e, ㄱ->r, ㅅ->t, ㅛ->y, ㅕ->u, ㅑ->i, ㅐ->o, ㅔ->p
 * ㅁ->a, ㄴ->s, ㅇ->d, ㄹ->f, ㅎ->g, ㅗ->h, ㅓ->j, ㅏ->k, ㅣ->l
 * ㅋ->z, ㅌ->x, ㅊ->c, ㅍ->v, ㅠ->b, ㅜ->n, ㅡ->m
 */
export function koreanToEnglish(text) {
  if (!text) return text

  // Korean to English character mapping
  const koreanToEnglishMap = {
    // Basic consonants and vowels
    'ㅂ': 'q', 'ㅈ': 'w', 'ㄷ': 'e', 'ㄱ': 'r', 'ㅅ': 't',
    'ㅛ': 'y', 'ㅕ': 'u', 'ㅑ': 'i', 'ㅐ': 'o', 'ㅔ': 'p',
    'ㅁ': 'a', 'ㄴ': 's', 'ㅇ': 'd', 'ㄹ': 'f', 'ㅎ': 'g',
    'ㅗ': 'h', 'ㅓ': 'j', 'ㅏ': 'k', 'ㅣ': 'l',
    'ㅋ': 'z', 'ㅌ': 'x', 'ㅊ': 'c', 'ㅍ': 'v',
    'ㅠ': 'b', 'ㅜ': 'n', 'ㅡ': 'm',
    
    // Shifted consonants/vowels
    'ㅃ': 'Q', 'ㅉ': 'W', 'ㄸ': 'E', 'ㄲ': 'R', 'ㅆ': 'T',
    'ㅒ': 'O', 'ㅖ': 'P',
    'ㅢ': 'L',
    
    // Special characters that might be used in passwords
    '·': '`', '~': '~',
    '!': '!', '@': '@', '#': '#', '$': '$', '%': '%',
    '^': '^', '&': '&', '*': '*', '(': '(', ')': ')',
    '-': '-', '_': '_', '=': '=', '+': '+',
    '[': '[', ']': ']', '{': '{', '}': '}',
    '\\': '\\', '|': '|',
    ';': ';', ':': ':', '\'': '\'', '"': '"',
    ',': ',', '.': '.', '/': '/', '?': '?',
  }

  // Convert each character
  let converted = ''
  for (const char of text) {
    if (char in koreanToEnglishMap) {
      converted += koreanToEnglishMap[char]
    } else {
      // For complex Korean characters (complete syllables), decompose them
      converted += decomposeKoreanChar(char)
    }
  }

  return converted
}

/**
 * Decompose a complete Korean character into its constituent parts
 * and convert to English equivalents.
 */
function decomposeKoreanChar(char) {
  const charCode = char.charCodeAt(0)
  
  // Check if it's a Korean syllable (가-힣)
  if (charCode >= 0xAC00 && charCode <= 0xD7A3) {
    // Decompose Korean syllable
    const code = charCode - 0xAC00
    
    // Korean syllable structure: initial + medial + final
    const initial = Math.floor(code / (21 * 28))
    const medial = Math.floor((code % (21 * 28)) / 28)
    const final = code % 28
    
    // Initial consonants (초성)
    const initials = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 
      'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    
    // Medial vowels (중성)
    const medials = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 
      'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    
    // Final consonants (종성)
    const finals = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 
      'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 
      'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    
    // Convert each component
    let result = ''
    if (initial < initials.length) {
      result += koreanToEnglish(initials[initial])
    }
    if (medial < medials.length) {
      result += koreanToEnglish(medials[medial])
    }
    if (final > 0 && final < finals.length) {
      result += koreanToEnglish(finals[final])
    }
    
    return result
  }
  
  // If not a Korean character, return as-is
  return char
}

/**
 * Check if the text contains any Korean characters.
 */
export function hasKoreanCharacters(text) {
  if (!text) return false
  
  for (const char of text) {
    const charCode = char.charCodeAt(0)
    // Check for Korean character ranges
    if ((charCode >= 0x1100 && charCode <= 0x11FF) ||  // Hangul Jamo
        (charCode >= 0x3130 && charCode <= 0x318F) ||  // Hangul Compatibility Jamo
        (charCode >= 0xAC00 && charCode <= 0xD7AF)) {   // Hangul Syllables
      return true
    }
  }
  return false
}

/**
 * Utility function to convert password input in real-time
 * Can be used with input event listeners
 */
export function convertPasswordInput(password) {
  // Security: Never log the actual password content
  if (hasKoreanCharacters(password)) {
    // Only log that conversion occurred, not the password itself
    if (process.env.NODE_ENV === 'development') {
      console.log('Korean keyboard input detected and converted')
    }
    return koreanToEnglish(password)
  }
  return password
}

// Example usage and testing
export function testKoreanConversion() {
  const testCases = [
    'ㅂㅏㅅㅅㅇㅝㄱㄷ123',  // "password123" typed in Korean
    'ㅁㅠㅂㅏㅅㅅ456',      // "mypass456" typed in Korean  
    'ㅂㅏㅅㅅ!@#',         // "pass!@#" typed in Korean
    'password123',          // Already English
    '한글mixed영어',        // Mixed Korean/English
  ]
  
  console.log('Korean to English Password Conversion Test:')
  console.log('='.repeat(50))
  
  testCases.forEach(test => {
    const converted = koreanToEnglish(test)
    const hasKorean = hasKoreanCharacters(test)
    console.log(`Original: ${test}`)
    console.log(`Has Korean: ${hasKorean}`)
    console.log(`Converted: ${converted}`)
    console.log('-'.repeat(30))
  })
}