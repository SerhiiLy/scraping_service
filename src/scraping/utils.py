from translitua import translit, UkrainianSimple


def from_cyrillic_to_eng(text: str):
    text = text.replace(' ', '_').lower()
    tmp = translit(text)
    return tmp