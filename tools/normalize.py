import re
import unicodedata

CONFUSABLE = str.maketrans({'а':'a','А':'A','е':'e','Е':'E','о':'o','О':'O','р':'p','Р':'P','с':'c','С':'C','х':'x','Х':'X','у':'y','У':'Y','і':'i','І':'I','ј':'j','Ј':'J','ѕ':'s','Ѕ':'S','Β':'B','Ε':'E','Ζ':'Z','Η':'H','Ι':'I','Κ':'K','Μ':'M','Ν':'N','Ο':'O','Ρ':'P','Τ':'T','Υ':'Y','Χ':'X'})
LEADS = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
VOWELS = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
TAILS = '\0ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'
INVISIBLE = re.compile('[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]')


def compose_compat(text):
    out = []; i = 0
    while i < len(text):
        if i+1 < len(text) and text[i] in LEADS and text[i+1] in VOWELS:
            lead, vowel = LEADS.index(text[i]), VOWELS.index(text[i+1]); i += 2; tail = 0
            if i < len(text) and text[i] in TAILS[1:]:
                if not (i+1 < len(text) and text[i] in LEADS and text[i+1] in VOWELS):
                    tail = TAILS.index(text[i]); i += 1
            out.append(chr(0xAC00 + (lead * 21 + vowel) * 28 + tail))
        else:
            out.append(text[i]); i += 1
    return ''.join(out)


def fold_digit_tokens(text):
    table = str.maketrans({'0':'o','1':'i','3':'e','4':'a','5':'s','7':'t','8':'b','@':'a','$':'s'})
    known = {'casino','slot','slots','bet','bonus','porn','sex'}
    def convert(match):
        token = match.group(0)
        folded = token.translate(table)
        return folded if any(c.isdigit() or c in '@$' for c in token) and folded in known else token
    return re.sub(r'[a-z0-9@$]{3,}', convert, text)


def normalize(text, zero_width=False):
    value = INVISIBLE.sub('', text) if zero_width else text
    value = compose_compat(re.sub(r'(?<=[ㄱ-ㅎㅏ-ㅣ])\s+(?=[ㄱ-ㅎㅏ-ㅣ])', '', value))
    return fold_digit_tokens(unicodedata.normalize('NFC', unicodedata.normalize('NFKC', value)).translate(CONFUSABLE).lower())


def text_techniques(text):
    found = []
    if re.search('[\u3131-\u3163\u1100-\u11ff\ua960-\ua97f\ud7b0-\ud7ff]', text):
        found.append('JAMO')
    if any(unicodedata.east_asian_width(c) == 'F' or ord(c) in CONFUSABLE for c in text) or fold_digit_tokens(text.lower()) != text.lower():
        found.append('HOMOGLYPH')
    if INVISIBLE.search(text):
        found.append('ZERO_WIDTH')
    return found


def ad_signal(text, rules):
    value = normalize(text, zero_width=rules.get('zero_width', False))
    compact = re.sub(r'[\s._·|*\-/]+', '', value)
    terms = [x for x in rules['ad_terms'] if x in value or x in compact]
    intent = [x for x in rules['intent_terms'] if x in value or x in compact]
    negative = [x for x in rules['negative_terms'] if x in value]
    score = bool(terms and intent and not negative)
    return {'violation': score, 'terms': terms, 'intent': intent, 'negative': negative, 'normalized': value}
