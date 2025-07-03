import re

dic2cyr = {'a': 'а', 'b': 'б', 'β': 'в',
           'g': 'г', 'd': 'д', 'e': 'е',
           'ž': 'ж', 'š': 'ш', 'š́': 'щ', 'ö': 'ӧ',
           'č́': 'ч', 'ŋ': 'ҥ',
           'z': 'з', 'i': 'ӥ', 'j': 'й', 'k': 'к',
           'l': 'л', 'm': 'м', 'n': 'н',
           'o': 'о', 'p': 'п', 'r': 'р',
           's': 'с', 't': 'т', 'u': 'у',
           'c': 'ц', 'ü': 'ӱ', 'χ': 'х',
           'f': 'ф', 'ə̑': 'ы'}
cyr2dic = {v: k for k, v in dic2cyr.items()}
cyr2dic.update({'я': 'ʼa', 'е': 'ʼe', 'и': 'ʼi', 'э': 'e',
                'ё': 'ʼo', 'ю': 'ʼu', 'ь': 'ʼ'})
cyrHard2Soft = {'а': 'я', 'э': 'е', 'е': 'е', 'ӥ': 'и', 'о': 'ё', 'у': 'ю'}
rxSoften = re.compile('(?<!ч)ʼ([аэӥоу])', flags=re.I)
rxCyrSoften = re.compile('(č)(?!ʼ)', flags=re.I)
rxCyrMultSoften = re.compile('ʼ{2,}')
rxNeutral1 = re.compile('(?<=[бвгджзкмҥпрстфхцчшщйʼ])([э])', re.I)
rxNeutral2 = re.compile('([бвгджзкмҥпрстфхцчшщйʼаоэуўяёеиюӧӱ]|\\b)(ӥ)', re.I)
rxCyrNeutral = re.compile('(?<=[bvgzkmprfxcwj])ʼ', re.I)
rxCJV = re.compile('(?<=[бвгджзӟклмнпрстўфхцчшщ])й([аяэеоёую])', re.I)
rxSh = re.compile('ш(?=[ʼяёюиеЯЁЮИЕ])')
rxZh = re.compile('ж(?=[ʼяёюиеЯЁЮИЕ])')
rxShCapital = re.compile('Ш(?=[ʼяёюиеЯЁЮИЕ])')
rxZhCapital = re.compile('Ж(?=[ʼяёюиеЯЁЮИЕ])')
rxVJV = re.compile('(?<=[аеёиӥоӧуӱыэюяʼ])й([аэоу])', flags=re.I)
rxJV = re.compile('\\bй([аэоу])')
rxJVCapital = re.compile('\\bЙ([аэоуАЭОУ])')
rxCyrVJV = re.compile('([aeouöüə])ʼ([aeouöüə])')
rxCyrVSoft = re.compile('([aeouöüə]|\\b)ʼ')
rxCyrJV = re.compile('(?<![^ aeouöüə̑][ʼ́-])\\bʼ([aeouöüə])')
rxExtraSoft = re.compile('([лн])ь\\1(?=[лн])')
rxCyrExtraSoft = re.compile('([ln])\\1(?=ʼ)')
rxCyrSingleSoft = re.compile('(?<!ʼ)ʼ(?=[ei])')


cyrReplacements = {}
srcReplacements = {}


def meadow_mari_translit_upa(text):
    """
    Transliterate Meadow Mari text from Cyrillic script to Latin UPA.
    """
    letters = []
    for letter in text:
        if letter.lower() in cyr2dic:
            if letter.islower():
                letters.append(cyr2dic[letter.lower()])
            else:
                letters.append(cyr2dic[letter.lower()].upper())
        else:
            letters.append(letter)
    res = ''.join(letters)
    res = rxCyrVJV.sub('\\1j\\2', res)
    res = rxCyrJV.sub('j\\1', res)
    res = res.replace('ъʼ', 'j')
    res = rxCyrNeutral.sub('', res)
    res = rxCyrExtraSoft.sub('\\1ʼ\\1', res)
    res = rxCyrSingleSoft.sub('', res)
    res = rxCyrMultSoften.sub('ʼ', res)
    res = rxCyrVSoft.sub('\\1', res)
    res = res.replace('nʼ', 'ń')
    res = res.replace('Nʼ', 'Ń')
    return res
