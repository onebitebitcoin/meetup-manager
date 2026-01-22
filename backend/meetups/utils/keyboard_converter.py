"""
Korean to English keyboard converter utility
Converts Korean characters typed on English keyboard layout to their English equivalents
"""

def korean_to_english(text):
    """
    Convert Korean characters to English based on keyboard layout mapping.
    
    This handles both individual Korean characters (jamo) and complete syllables.
    Korean QWERTY keyboard layout maps directly to English QWERTY keys.
    """

    # Direct Korean keyboard to English keyboard mapping
    # This is based on the physical key positions on a QWERTY keyboard
    korean_to_english_map = {
        # Row 1 (numbers and special chars)
        '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
        '6': '6', '7': '7', '8': '8', '9': '9', '0': '0',
        '!': '!', '@': '@', '#': '#', '$': '$', '%': '%',
        '^': '^', '&': '&', '*': '*', '(': '(', ')': ')',

        # Row 2 - QWERTY row
        'ㅂ': 'q', 'ㅈ': 'w', 'ㄷ': 'e', 'ㄱ': 'r', 'ㅅ': 't',
        'ㅛ': 'y', 'ㅕ': 'u', 'ㅑ': 'i', 'ㅐ': 'o', 'ㅔ': 'p',
        'ㅃ': 'Q', 'ㅉ': 'W', 'ㄸ': 'E', 'ㄲ': 'R', 'ㅆ': 'T',
        '': 'Y', '': 'U', '': 'I', 'ㅒ': 'O', 'ㅖ': 'P',

        # Row 3 - ASDF row
        'ㅁ': 'a', 'ㄴ': 's', 'ㅇ': 'd', 'ㄹ': 'f', 'ㅎ': 'g',
        'ㅗ': 'h', 'ㅓ': 'j', 'ㅏ': 'k', 'ㅣ': 'l',
        '': 'A', '': 'S', '': 'D', '': 'F', '': 'G',
        '': 'H', '': 'J', '': 'K', '': 'L',

        # Row 4 - ZXCV row
        'ㅋ': 'z', 'ㅌ': 'x', 'ㅊ': 'c', 'ㅍ': 'v',
        'ㅠ': 'b', 'ㅜ': 'n', 'ㅡ': 'm',
        '': 'Z', '': 'X', '': 'C', '': 'V',
        '': 'B', '': 'N', '': 'M',

        # Special characters and punctuation
        '-': '-', '=': '=', '[': '[', ']': ']', '\\': '\\',
        ';': ';', "'": "'", ',': ',', '.': '.', '/': '/',
        '_': '_', '+': '+', '{': '{', '}': '}', '|': '|',
        ':': ':', '"': '"', '<': '<', '>': '>', '?': '?',
        '`': '`', '~': '~',

        # Space and common chars
        ' ': ' ', '\t': '\t', '\n': '\n'
    }

    # Convert each character
    converted = ''
    for char in text:
        if char in korean_to_english_map:
            converted += korean_to_english_map[char]
        elif char.isascii():
            # If it's already ASCII (English), keep it as-is
            converted += char
        else:
            # For complex Korean characters (complete syllables), decompose them
            converted += decompose_korean_char(char)

    return converted


def decompose_korean_char(char):
    """
    Decompose a complete Korean character into its constituent parts
    and convert to English equivalents.
    """
    # Unicode ranges for Korean characters
    if 0xAC00 <= ord(char) <= 0xD7A3:  # Complete Korean syllables
        # Decompose Korean syllable
        code = ord(char) - 0xAC00

        # Korean syllable structure: initial + medial + final
        initial = code // (21 * 28)
        medial = (code % (21 * 28)) // 28
        final = code % 28

        # Initial consonants (초성)
        initials = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
                   'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

        # Medial vowels (중성)
        medials = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
                  'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']

        # Final consonants (종성)
        finals = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ',
                 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ',
                 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

        # Convert each component
        result = ''
        if initial < len(initials):
            result += korean_to_english(initials[initial])
        if medial < len(medials):
            result += korean_to_english(medials[medial])
        if final > 0 and final < len(finals):
            result += korean_to_english(finals[final])

        return result

    # If not a Korean character, return as-is
    return char


def has_korean_characters(text):
    """Check if the text contains any Korean characters."""
    for char in text:
        # Check for Korean character ranges
        if (0x1100 <= ord(char) <= 0x11FF or  # Hangul Jamo
            0x3130 <= ord(char) <= 0x318F or  # Hangul Compatibility Jamo
            0xAC00 <= ord(char) <= 0xD7AF):   # Hangul Syllables
            return True
    return False


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_cases = [
        "ㅂㅏㅅㅅㅇㅝㄱㄷ123",  # "password123" typed in Korean
        "ㅁㅠㅂㅏㅅㅅ456",      # "mypass456" typed in Korean
        "ㅂㅏㅅㅅ!@#",         # "pass!@#" typed in Korean
        "password123",          # Already English
        "한글mixed영어",        # Mixed Korean/English
    ]

    print("Korean to English Password Conversion Test:")
    print("=" * 50)

    for test in test_cases:
        converted = korean_to_english(test)
        has_korean = has_korean_characters(test)
        print(f"Original: {test}")
        print(f"Has Korean: {has_korean}")
        print(f"Converted: {converted}")
        print("-" * 30)
