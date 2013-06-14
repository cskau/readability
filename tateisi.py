#!/usr/bin/env python4
# encoding: utf-8


'''
Implementation of Tateisi et al's Japanese Readability Score.
  Yuka, Tateisi, Ono Yoshihiko, and Yamada Hisao.
    "A computer readability formula of Japanese texts for machine scoring."
    Proceedings of the 12th conference on Computational linguistics-Volume 2.
    Association for Computational Linguistics, 1988.
'''


import sys
import unittest


'''
pa, ph, pc, pk    Percentages of (roman) alphabet runs, hiragana runs,
  kanzi runs, and katakana runs, respectively;
ls    Average numbers of letters per sentence;
la, lh, lc, lk    Average numbers of letters per alphabet run,
  hiragana run, kanzi run, and katakana run, respectively;
cp    Toten to kuten ratio.
'''

'''
Wikipedia:
U+4E00–U+9FBF Kanji
U+3040–U+309F Hiragana
U+30A0–U+30FF Katakana
'''

class Tateisi(object):
  # initial values
  pa, ph, pc, pk = 0, 0, 0, 0
  la, lh, lc, lk = 0, 0, 0, 0
  ls = 0
  cp = 0

  def __init__(self, txt):
    # initial vectors
    a, h, c, k = 0, 0, 0, 0
    ar, hr, cr, kr = 0, 0, 0, 0
    tt, tk = 0, 0
    current_run = ''
    for l in txt:
      ord_l = ord(l)
      # latin, latin fullwidth
      if 0x0041 <= ord_l <= 0x007A or 0xFF21 <= ord_l <= 0xFF5A:
        if current_run != 'a':
          current_run = 'a'
          ar += 1
        a += 1
      # hiragana
      elif 0x3041 <= ord_l <= 0x3096:
        if current_run != 'h':
          current_run = 'h'
          hr += 1
        h += 1
      # katakana
      elif 0x30A1 <= ord_l <= 0x30FA:
        if current_run != 'k':
          current_run = 'k'
          kr += 1
        k += 1
      # kanji
      elif 0x4E00 <= ord_l <= 0x9FBF:
        if current_run != 'c':
          current_run = 'c'
          cr += 1
        c += 1
      # kuten
      elif l == u'。':
        tk += 1
      # tooten
      elif l == u'、':
        tt += 1
      elif 0x0021 <= ord_l <= 0x002F: # !"#$%&'()*+,-./
        continue
      elif 0x0030 <= ord_l <= 0x0039: # 0123456789
        continue
      elif 0x003A <= ord_l <= 0x0040: # :;<=>?@
        continue
      # elif 0x005B <= ord_l <= 0x0060: # [\]^_`
      #   continue
      elif 0x007B <= ord_l <= 0x007E: # {|}~
        continue

    # assume at least 1 (implicit) kuten per sentence
    tk = tk or 1.0
    tr = (ar + hr + cr + kr) / 100.0
    if tr != 0:
      self.pa = (ar / tr)
      self.ph = (hr / tr)
      self.pc = (cr / tr)
      self.pk = (kr / tr)
    if ar != 0:
      self.la = (a / ar)
    if hr != 0:
      self.lh = (h / hr)
    if cr != 0:
      self.lc = (c / cr)
    if kr != 0:
      self.lk = (k / kr)
    self.cp = (tt / tk)
    self.ls = ((a + h + c + k) / tk)

  def calculate_rs_tateisi_a(self):
    return (
      (0.06 * self.pa) + (0.25 * self.ph) -
      (0.19 * self.pc) - (0.61 * self.pk) -
      (1.34 * self.ls) - (1.35 * self.la) +
      (7.52 * self.lh) - (22.1 * self.lc) -
      (5.3 * self.lk) - (3.87 * self.cp) -
      109.1
      )

  def calculate_rs_tateisi_b(self):
    return (
      (-0.12 * self.ls) + (-1.37 * self.la) +
      (7.4 * self.lh) + (-23.18 * self.lc) +
      (-5.4 * self.lk) + (-4.67 * self.cp) +
      115.79
      )


## Unit Tests

class TestScoring(unittest.TestCase):

  def test_near_empty_string(self):
    self.assertEqual(Tateisi(u'').calculate_rs_tateisi_b(), 115.79)
    self.assertEqual(Tateisi(u'。').calculate_rs_tateisi_b(), 115.79)
    self.assertEqual(Tateisi(u'   ').calculate_rs_tateisi_b(), 115.79)
    self.assertEqual(
        Tateisi(
            u'!"#$%&\'()*+,-./0123456789:;<=>?@{|}'
            ).calculate_rs_tateisi_b(),
        115.79,
        )


## Example usage

if __name__ == '__main__':
  import sys

  text = sys.argv[1] if len(sys.argv) >= 2 else u'僕は鰻だ！'
  
  print('## Tateisi et al Readability Score')
  print('Text: "{}"'.format(text))
  
  tateisi = Tateisi(text)

  score_a = tateisi.calculate_rs_tateisi_a()
  score_b = tateisi.calculate_rs_tateisi_b()

  print('Score A: {}'.format(score_a))
  print('Score B: {}'.format(score_b))
