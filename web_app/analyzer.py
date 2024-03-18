import re
import os
import copy
import jinja2
from flask import render_template

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
            # 'albanian': {
            #     'name': 'Albanian',
            #     'analyzer': AlbanianAnalyzer()
            # },
            'beserman': {
                'name': 'Beserman (Latin-based)',
                'analyzer': BesermanLatAnalyzer(),
                'translit': {
                    'UPA': beserman_translit_upa,
                    'IPA': beserman_translit_upa,
                    'Cyrillic': beserman_translit_cyrillic
                }
            },
            # 'buryat': {
            #     'name': 'Buryat',
            #     'analyzer': BuryatAnalyzer()
            # },
            # 'eastern_armenian': {
            #     'name': 'Eastern Armenian',
            #     'analyzer': EasternArmenianAnalyzer(),
            #     'translit': {
            #         'Quasi-Meillet': armenian_translit_meillet
            #     }
            # },
            # 'erzya': {
            #     'name': 'Erzya',
            #     'analyzer': ErzyaAnalyzer(),
            #     'translit': {
            #         'UPA': erzya_translit_upa
            #     }
            # },
            # 'komi_zyrian': {
            #     'name': 'Komi Zyrian',
            #     'analyzer': KomiZyrianAnalyzer()
            # },
            # 'meadow_mari': {
            #     'name': 'Meadow Mari',
            #     'analyzer': MeadowMariAnalyzer()
            # },
            # 'moksha': {
            #     'name': 'Moksha',
            #     'analyzer': MokshaAnalyzer()
            # },
            # 'ossetic': {
            #     'name': 'Ossetic (Iron)',
            #     'analyzer': OsseticAnalyzer()
            # },
            # 'turoyo': {
            #     'name': 'Ṭuroyo',
            #     'analyzer': TuroyoAnalyzer()
            # },
            # 'udmurt': {
            #     'name': 'Udmurt',
            #     'analyzer': UdmurtAnalyzer(),
            #     'translit': {
            #         'UPA': udmurt_translit_upa
            #     }
            # },
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


class PaperParser:
    rxPuncR = re.compile('^[.,?!:;)"/-]+$')
    rxPuncL = re.compile('^[*(]+$')
    rxExamples = re.compile('(?<=\n) *\\((x[x0-9]+?)\\)[ \t]*([^\r\n]+?)[ \t]*\n'
                            '(?: *([^ \r\n][^\r\n]*?) *\n)?|(?<=\n)([^\n]*\n)',
                            flags=re.DOTALL)
    rxStemGloss = re.compile('[ ,;:()]+')
    rxWordLang = {
        'beserman': re.compile('(?<= )-[\\w()]*[əɤʼčšžǯɨ][\\w()-]*|'
                               '\\w*[əɤʼčšžǯɨ]\\w*|'
                               '\\b(ta|[mt]on|ben|uk|mare?|(ta|so)os(len)?|nu|soje|'
                               'pe|val|palaz|u[gmzd]|na|tak|odig|se?re|ma|ik|mh|vot|tare|'
                               'ke|ja|bere|pun[eoi]?[mdz]?|gine|(so|ta)iz[^ \r\n]*|gord|marke|'
                               'e[jzmd]|(ta|so)len|(ta|so)in|tros|bur|luoz|naverno|'
                               'pi|dore|vaj[eo]?|med|da|wa|olo|abi(len)?|jun|'
                               'korka[^ \r\n]*|aslam|poti[zdm]?|kule|lue|murt[^ \r\n]*)\\b',
                               flags=re.DOTALL)
    }

    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.templates = {}  # Jinja2 template cache

    def render_jinja_html(self, templateDir, templateFilename, **context):
        """
        Render a flask template without flask context (needed if
        this file is imported from outside the package).
        """
        try:
            template = self.templates[(templateDir, templateFilename)]
        except KeyError:
            template = jinja2.Environment(
                loader=jinja2.FileSystemLoader(templateDir + '/')
            ).get_template(templateFilename)
            self.templates[(templateDir, templateFilename)] = template
        return template.render(context)

    def process_example(self, lang, num, text, trans):
        result = self.analyzer.analyze(lang, text)
        if 'IPA' in result:
            result = result['IPA']
        else:
            result = result['default']
        words = []
        glosses = []
        hangingPuncL = ''
        for w in result:
            if len(w) <= 0:
                continue
            wf = w[0]['wf']
            if self.rxPuncR.search(wf) is not None:
                if len(words) > 0:
                    words[-1] += wf
                else:
                    hangingPuncL += wf
                continue
            elif self.rxPuncL.search(wf) is not None:
                hangingPuncL += wf
                continue
            wf = hangingPuncL + wf
            gloss = 'STEM'
            curGlosses = set()
            curWfParts = set()
            curTrans = set()
            for ana in w:
                curWfParts.add(ana['wfGlossed'])
                curGlosses.add(ana['gloss'])
                if 'trans_ru' in ana:
                    curTrans.add(ana['trans_ru'])
            curGlosses = [g for g in sorted(curGlosses, key=lambda x: (x.count('-'), x))]
            curWfParts = [p for p in sorted(curWfParts, key=lambda x: (x.count('-'), x))]
            curTrans = [t for t in sorted(curTrans, key=lambda x: (-len(x), x))]
            if len(curGlosses) > 0 and len(curWfParts) > 0:
                wf = hangingPuncL + curWfParts[0]
                gloss = curGlosses[0]
                if len(curTrans) > 0:
                    gloss = gloss.replace('STEM', self.rxStemGloss.sub('.', curTrans[0]))
            hangingPuncL = ''
            words.append(wf)
            glosses.append(gloss)
        return self.render_jinja_html('web_app/templates',
                                      'analysis_paper.html',
                                      num=num,
                                      words=words,
                                      glosses=glosses,
                                      translation=trans).strip()

    def analyze(self, lang, text):
        if lang not in self.analyzer.langs:
            return text
        text = '\n' + text.strip() + '\n'
        segments = self.rxExamples.findall(text)
        textProcessed = ''
        for seg in segments:
            if len(seg[1]) == 0 and len(seg[3]) == 0:
                textProcessed += '<br>'
            elif len(seg[3]) > 0 and len(seg[1]) <= 0:
                para = seg[3]
                if lang in self.rxWordLang:
                    if 'IPA' in self.analyzer.langs[lang]['translit']:
                        transliterator = self.analyzer.langs[lang]['translit']['IPA']
                    else:
                        transliterator = lambda s: s
                    para = self.rxWordLang[lang].sub(lambda m: '<i>' + transliterator(m.group(0)) + '</i>', para)
                textProcessed += '<p>' + para.replace('\n', '</p>\n<p>')[:-3]
            else:
                print(seg)
                textProcessed += self.process_example(lang, seg[0], seg[1], seg[2])
        return textProcessed

