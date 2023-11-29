import re
import os
import copy

from uniparser_albanian import AlbanianAnalyzer
from uniparser_beserman_lat import BesermanLatAnalyzer
from uniparser_buryat import BuryatAnalyzer
from uniparser_eastern_armenian import EasternArmenianAnalyzer
from uniparser_erzya import ErzyaAnalyzer
from uniparser_komi_zyrian import KomiZyrianAnalyzer
from uniparser_meadow_mari import MeadowMariAnalyzer
from uniparser_moksha import MokshaAnalyzer
from uniparser_ossetic import OsseticAnalyzer
from uniparser_turoyo import TuroyoAnalyzer
from uniparser_udmurt import UdmurtAnalyzer
from uniparser_urmi import UrmiAnalyzer

from .translit_armenian import armenian_translit_meillet
from .translit_beserman import beserman_translit_cyrillic, beserman_translit_upa
from .translit_erzya import erzya_translit_upa
from .translit_udmurt import udmurt_translit_upa


class Analyzer:
    rxWords = re.compile('\\w+|\\w[\\w\'-]+\\w|[^\\w]+')
    rxWord = re.compile('\\w+|\\w[\\w\'-]+\\w')
    rxSpace = re.compile('^[ \r\n\t]+$')
    rxBadChars = re.compile('[<>&]')

    def __init__(self):
        self.langs = {
            'albanian': {
                'name': 'Albanian',
                'analyzer': AlbanianAnalyzer()
            },
            'beserman': {
                'name': 'Beserman (Latin-based)',
                'analyzer': BesermanLatAnalyzer(),
                'translit': {
                    'UPA': beserman_translit_upa,
                    'Cyrillic': beserman_translit_cyrillic
                }
            },
            'buryat': {
                'name': 'Buryat',
                'analyzer': BuryatAnalyzer()
            },
            'eastern_armenian': {
                'name': 'Eastern Armenian',
                'analyzer': EasternArmenianAnalyzer(),
                'translit': {
                    'Quasi-Meillet': armenian_translit_meillet
                }
            },
            'erzya': {
                'name': 'Erzya',
                'analyzer': ErzyaAnalyzer(),
                'translit': {
                    'UPA': erzya_translit_upa
                }
            },
            'komi_zyrian': {
                'name': 'Komi Zyrian',
                'analyzer': KomiZyrianAnalyzer()
            },
            'meadow_mari': {
                'name': 'Meadow Mari',
                'analyzer': MeadowMariAnalyzer()
            },
            'moksha': {
                'name': 'Moksha',
                'analyzer': MokshaAnalyzer()
            },
            'ossetic': {
                'name': 'Ossetic (Iron)',
                'analyzer': OsseticAnalyzer()
            },
            'turoyo': {
                'name': 'Ṭuroyo',
                'analyzer': TuroyoAnalyzer()
            },
            'udmurt': {
                'name': 'Udmurt',
                'analyzer': UdmurtAnalyzer(),
                'translit': {
                    'UPA': udmurt_translit_upa
                }
            },
            'urmi': {
                'name': 'Christian Urmi (Assyrian Neo-Aramaic), Latin-based',
                'analyzer': UrmiAnalyzer()
            }
        }
        self.disamb_langs = ['albanian', 'udmurt', 'beserman', 'eastern_armenian']

    def analyze(self, lang, sentence):
        if lang not in self.langs:
            return ''
        sentence = self.rxBadChars.sub('', sentence)[:2048]
        tokens = [t.strip() for t in self.rxWords.findall(sentence.strip())
                  if self.rxSpace.search(t) is None]
        result = []
        if lang in self.disamb_langs:
            result = self.langs[lang]['analyzer'].analyze_words(tokens, disambiguate=True, format='json')
        else:
            result = self.langs[lang]['analyzer'].analyze_words(tokens, format='json')
        result = {'default': result}
        if 'translit' in self.langs[lang]:
            for translit, f in self.langs[lang]['translit'].items():
                resultTranslit = []
                for w in result['default']:
                    wTranslit = copy.deepcopy(w)
                    for ana in wTranslit:
                        ana['wf'] = f(ana['wf'])
                        if 'lemma' in ana:
                            ana['lemma'] = f(ana['lemma'])
                        if 'wfGlossed' in ana:
                            ana['wfGlossed'] = f(ana['wfGlossed'])
                    resultTranslit.append(wTranslit)
                result[translit] = resultTranslit
        return result
