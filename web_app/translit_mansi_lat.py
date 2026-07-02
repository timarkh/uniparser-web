import re

dic2cyr = {
    'a': 'а', 'b': 'б', 'v': 'в',
    'g': 'г', 'ɣ': 'г', 'd': 'д', 'e': 'э',
    'ž': 'ж', 'š': 'ш',
    'ə': 'ы', 'č': 'ч',
    'z': 'з', 'i': 'ы', 'j': 'й', 'k': 'к',
    'l': 'л', 'm': 'м', 'n': 'н',
    'o': 'о', 'p': 'п', 'r': 'р',
    's': 'с', 'ɕ': "s'", 't': 'т', 'u': 'у',
    'c': 'ц', 'w': 'в', 'x': 'х',
    'y': 'ы', 'f': 'ф',
    'ā': 'а̄',
    'ō': 'о̄',
    'ē': 'э̄',
    'ī': 'ы̄',
    'ū': 'ӯ',
    'ŋ': 'ӈ'
}

cyrHard2Soft = {
                'а': 'я', 'а̄': 'я̄',
                'э': 'е', 'э̄': 'ē',
                'ы': 'и', 'ы̄': 'ӣ',
                'о': 'ё', 'о̄': 'ё̄',
                'у': 'ю', 'ӯ': 'ю̄'
}

badChars = {
        'ā': 'ā',
        'ō': 'ō',
        'ē': 'ē',
        'ī': 'ī',
        'ū': 'ū'
    }

rxSoften = re.compile('\'([аэыоу])', flags=re.I)
rxCyrMultSoften = re.compile('\'{2,}')
rxNeutral1 = re.compile('(?<=[бвгджзкмпрфхцчшщй\'])([э])', re.I)
rxNeutral2 = re.compile('(\\b)(ы)', re.I)
rxCJV = re.compile('(?<=[бвгджзӟклмнӈпрстфхцчшщ])й([аяэеоёуюыи])', re.I)
rxVJV = re.compile('(?<=[аеёиоуыэюя̄\'])й([аэыоу])', flags=re.I)
rxJV = re.compile('\\bй([аэыоу])')
rxJVCapital = re.compile('\\bЙ([аэыоуАЭЫОУ])')
rxExtraSoft = re.compile('([лнст])ь\\1(?=[ьяеёию])')

rxCyrillic = re.compile('^[а-яёӟӥӧўөА-ЯЁӞӤӦЎӨ.,;:!?\\-()\\[\\]{}<>]*$')

cyrReplacements = {}
srcReplacements = {}


def mansi_clean(s):
    for c in badChars:
        s = s.replace(c, badChars[c])
        s = s.replace(c.upper(), badChars[c].upper())
    return s


def mansi_translit_cyrillic(text):
    """
    Transliterate Mansi text from Dasha's Latin script to Cyrillics.
    """
    if rxCyrillic.search(text) is not None:
        return text

    letters = []
    for letter in text:
        if letter.lower() in dic2cyr:
            if letter.islower():
                letters.append(dic2cyr[letter.lower()])
            else:
                letters.append(dic2cyr[letter.lower()].upper())
        else:
            letters.append(letter)
    res = ''.join(letters)
    res = res.replace('h', 'х')
    res = res.replace('H', 'Х')
    res = rxSoften.sub(lambda m: cyrHard2Soft[m.group(1).lower()], res)
    res = rxVJV.sub(lambda m: cyrHard2Soft[m.group(1).lower()], res)
    res = rxVJV.sub(lambda m: cyrHard2Soft[m.group(1).lower()], res)
    res = rxJV.sub(lambda m: cyrHard2Soft[m.group(1).lower()], res)
    res = rxJVCapital.sub(lambda m: cyrHard2Soft[m.group(1).lower()].upper(), res)
    res = rxNeutral1.sub(lambda m: cyrHard2Soft[m.group(1).lower()], res)
    res = rxNeutral2.sub('\\1и', res)
    res = rxCJV.sub(lambda m: 'ъ' + cyrHard2Soft[m.group(1).lower()], res)
    res = res.replace("'", 'ь')
    res = rxExtraSoft.sub('\\1\\1', res)

    if res in cyrReplacements:
        res = cyrReplacements[res]
    return res


def mansi_translit_ipa(text):
    text = mansi_clean(text)
    text = text.replace('č', 'č')
    text = text.replace('Č', 'Č')
    text = text.replace('š', 'š')
    text = text.replace('Š', 'Š')
    text = text.replace('ž', 'ž')
    text = text.replace('Ž', 'Ž')
    text = text.replace('ǯ', 'ǯ')
    text = text.replace('Ǯ', 'Ǯ')
    text = text.replace("'", 'ʼ')
    text = text.replace('ə', 'ʌ')
    text = text.replace('Ə', 'Ʌ')
    text = text.replace('ɤ', 'ɘ')
    text = text.replace('ü', 'ʉ')
    # text = text.replace('ɨ', 'i̮')
    # text = text.replace('Ɨ', 'I̮')
    text = text.replace('čʼ', 't͡ɕ')
    text = text.replace('Čʼ', 'T͡ɕ')
    text = text.replace('ǯʼ', 'd͡ʑ')
    text = text.replace('Ǯʼ', 'D͡ʑ')
    text = text.replace('šʼ', 'ɕ')
    text = text.replace('Šʼ', 'ɕ')
    text = text.replace('žʼ', 'ʑ')
    text = text.replace('Žʼ', 'ʑ')
    text = text.replace('č', 't͡ʂ')
    text = text.replace('Č', 'T͡ʂ')
    text = text.replace('ǯ', 'd͡ʐ')
    text = text.replace('Ǯ', 'D͡ʐ')
    text = text.replace('š', 'ʂ')
    text = text.replace('Š', 'ʂ')
    text = text.replace('ž', 'ʐ')
    text = text.replace('Ž', 'ʐ')
    text = text.replace('ʼ', 'ʲ')
    text = text.replace('c', 't͡s')
    text = text.replace('C', 'T͡s')
    text = text.replace('ā', 'aː')
    text = text.replace('ā'.upper(), 'aː'.upper())
    text = text.replace('ō', 'oː')
    text = text.replace('ō'.upper(), 'oː'.upper())
    text = text.replace('ū', 'uː')
    text = text.replace('ū'.upper(), 'uː'.upper())
    text = text.replace('ī', 'iː')
    text = text.replace('ī'.upper(), 'iː'.upper())
    text = text.replace('ē', 'eː')
    text = text.replace('ē'.upper(), 'eː'.upper())
    return text


def mansi_translit_upa(text):
    text = mansi_clean(text)
    text = text.replace("'", 'ʼ')
    text = text.replace('ɕ', 'ś')
    text = text.replace('žʼ', 'ź')
    text = text.replace('Žʼ', 'Ź')
    text = text.replace('nʼ', 'ń')
    text = text.replace('Nʼ', 'Ń')
    # text = text.replace('ʼ', '̓')
    return text