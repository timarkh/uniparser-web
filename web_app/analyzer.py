import re
import os

from uniparser_albanian import AlbanianAnalyzer
from uniparser_beserman_lat import BesermanLatAnalyzer
from uniparser_buryat import BuryatAnalyzer
from uniparser_eastern_armenian import EasternArmenianAnalyzer
from uniparser_erzya import ErzyaAnalyzer
from uniparser_komi_zyrian import KomiZyrianAnalyzer
from uniparser_meadow_mari import MeadowMariAnalyzer
from uniparser_moksha import MokshaAnalyzer
from uniparser_udmurt import UdmurtAnalyzer
from uniparser_urmi import UrmiAnalyzer


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
                'analyzer': BesermanLatAnalyzer()
            },
            'buryat': {
                'name': 'Buryat',
                'analyzer': BuryatAnalyzer()
            },
            'eastern_armenian': {
                'name': 'Eastern Armenian',
                'analyzer': EasternArmenianAnalyzer()
            },
            'erzya': {
                'name': 'Erzya',
                'analyzer': ErzyaAnalyzer()
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
                'analyzer': MeadowMariAnalyzer()
            },
            'udmurt': {
                'name': 'Udmurt',
                'analyzer': UdmurtAnalyzer()
            },
            'urmi': {
                'name': 'Urmi (Neo-Aramaic)',
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
        return result
