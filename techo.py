# line 461

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# techo  ---  Teto's echo
#
# usage: $ techo [-0~5] [-q] [-f text-file] [message ... ]
#
# example1: $ techo hello world
# example2: $ cat sample.txt | techo
# example3: $ techo -q
#
# copyright of the source code:
#   2024, nwp8861, released under the MIT No Attribution license (MIT-0)
#   MIT-0: https://opensource.org/license/MIT-0
# copyright of Teto:
#   PCL (applied mutatis mutandis)
#   https://kasaneteto.jp/guideline/ctu.html
#
# 補足:
#   PowerShellでパイプラインで日本語を送り込む場合は
#   コマンドラインであらかじめ以下のように実行する必要がある。
#   PS C:\ > $OutputEncoding = [Text.Encoding]::Default
#   PS C:\ > echo あいうえお | python techo.py
#
# Note:
#   To type Japanese to the pipeline in PowerShell,
#   you need to run the following on the command line first:
#   PS C:\ > $OutputEncoding = [Text.Encoding]::Default
#   PS C:\ > echo あいうえお | python techo.py

import signal
import sys
import re
import shutil
import os
import unicodedata

version = '31.0'

#---------------------------------------------
# usage
#---------------------------------------------
def usage(argv0, ver):
  print(f"""{argv0} --- TETO's echo Version {ver}

usage: {argv0} [-0~5|-q|-d|-l|-r|-f text-file] [--] [message ... ]

  -0 ~ -5      ... change face (default: -0)
  -q           ... output no message (show face only)
  -d           ... reduce Teto's vertical width
  -l           ... position face to the left
  -r           ... position face to the right (default)
  -f text-file ... read message from text-file
  --           ... end of command line options
""", file=sys.stderr)
  exit()

#---------------------------------------------
# Ctrl+cが来たら画面設定をリセットして終了
# At Ctrl+c, reset the screen settings and exit
#
def ctrlC(signal, frame):
  print("\033[0m", end='')
  sys.exit(0)
signal.signal(signal.SIGINT, ctrlC)   # SIGINTにctrlC()を紐づける

#---------------------------------------------
# Windowsの端末の場合はエスケープシーケンスを有効にする
# Enable escape sequence for Windows terminal
#
if os.name == 'nt':
  import ctypes
  import io
  ENABLE_PROCESSED_OUTPUT = 0x0001
  ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
  ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
  MODE = ENABLE_PROCESSED_OUTPUT + ENABLE_WRAP_AT_EOL_OUTPUT + ENABLE_VIRTUAL_TERMINAL_PROCESSING
 
  handle = ctypes.windll.kernel32.GetStdHandle(-11)
  ctypes.windll.kernel32.SetConsoleMode(handle, MODE)

  sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
  sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

#--------------------------------------------
# Skin tones taken from Heart Gem palette
# https://lospec.com/palette-list/heart-gem
# 
palette = ['2d272a', # Black

                     # Red
           'ff0026', # Hair
           'cc001e', # Hair Shade
           'b3001a', # Hair Dark

           'ee0e46', # Eyes (Pink-ish Red)

           'f6cdcb', # Skin
           'f79ca1', # Skin Shade

                     # Mauve
           '925b6e', # Dress
           '76445f'] # Dress Shade

#---------------------------------------------
# 顔データ
# Faces
# 
# The numbers in the images refer to the index of the color in palette
# Eg - If palette=['ff0000', '00ff00', '0000ff'],
#      '0' would be ff0000, '1' would be 00ff00, and so on
# 
img = [
  #----------おすまし -0
  [
  '...........112...........',
  '..........12.............',
  '..........2..............',
  '...........2.............',
  '..........12.11113...13..',
  '.....12..1111121113.11133',
  '...1112..12111121113.1113',
  '..112.2.11111121111111113',
  '..12.2.111111111111211113',
  '....111111111111111211113',
  '..12.31112111121111111213',
  '..12.32112211122111122123',
  '..112.3112122112211121213',
  '...12.3121161212211112123',
  '...112.322661166621111213',
  '....12.35540516406213.3..',
  '....1121155555555613..13.',
  '.....12.15555655663..123.',
  '.....11..155555556...113.',
  '......11...500056.....3..',
  '............5556......3..',
  '.............666.........',
  '...........776678........',
  '........57717777188......',
  '.......567717171777856...',
  '......56777718177785556..',
  '.....556777771777785556..',
  '.....55677777777785556...',
  ],

  #----------にっこり smile ^_^ -1
  [
  '...........112...........',
  '..........12.............',
  '..........2..............',
  '...........2.............',
  '..........12.11113...13..',
  '.....12..1111111113.11133',
  '...1112..12111121113.1113',
  '..112.2.11111121111112113',
  '..12.2.111111111111211113',
  '....111111111111111211113',
  '..12.31112111121111111213',
  '..12.32112211112111122123',
  '..112.3112621156211121213',
  '...12.3125562155611112123',
  '...112.325056150552111213',
  '....12.31050550505213.3..',
  '....1121155555555613..13.',
  '.....12.15555555661..123.',
  '.....11..150110566...113.',
  '......11...500556.....3..',
  '............5556......3..',
  '.............666.........',
  '...........776678........',
  '........57717777188......',
  '.......567717171777856...',
  '......56777718177785556..',
  '.....556777771777785556..',
  '.....55677777777785556...',
  ],

  #----------きりっ+笑い？ Sharp + laughter? -2
  [
  '...........112...........',
  '..........12.............',
  '..........2..............',
  '...........2.............',
  '..........12.11113...13..',
  '.....12..1111121113.11133',
  '...1112..12111121113.1113',
  '..112.2.11111121111111113',
  '..12.2.111111111111211113',
  '....111111111111111211113',
  '..12.31112111121111111213',
  '..12.32112211122111122123',
  '..112.3112122112211121213',
  '...12.3121161212211112123',
  '...112.322661166621111213',
  '....12.35540516406213.3..',
  '....1121155555555613..13.',
  '.....12.15555555663..123.',
  '.....11..150110556...113.',
  '......11...500556.....3..',
  '............5556......3..',
  '.............666.........',
  '...........776678........',
  '........57717777188......',
  '.......567717171777856...',
  '......56777718177785556..',
  '.....556777771777785556..',
  '.....55677777777785556...',
  ],
  #----------ぱっちり bright (looks kinda creepy) -3
  [
  '...........112...........',
  '..........12.............',
  '..........2..............',
  '...........2.............',
  '..........12.11113...13..',
  '.....12..1111121113.11133',
  '...1112..12111121113.1113',
  '..112.2.11111121111111113',
  '..12.2.111111111111211113',
  '....111111111111111211113',
  '..12.31112111121111111213',
  '..12.32112211122111122123',
  '..112.3112122112211121213',
  '...12.3121161212211112123',
  '...112.322000160001111213',
  '....12.35504516046213.3..',
  '....1121155555555613..13.',
  '.....12.15555655663..123.',
  '.....11..155555556...113.',
  '......11...501056.....3..',
  '............5556......3..',
  '.............666.........',
  '...........776678........',
  '........57717777188......',
  '.......567717171777856...',
  '......56777718177785556..',
  '.....556777771777785556..',
  '.....55677777777785556...',
  ],

  #----------びっくり Surprised :o omg -4
  [
  '...........112...........',
  '..........12.............',
  '..........2..............',
  '...........2.............',
  '..........12.11113...13..',
  '.....12..1111121113.11133',
  '...1112..12111121113.1113',
  '..112.2.11111121111111113',
  '..12.2.111111111111211113',
  '....111111111111111211113',
  '..12.31112111121111111213',
  '..12.32112211122111122123',
  '..112.3112122112211121213',
  '...12.3121011210211112123',
  '...112.320505105021111213',
  '....12.35050550506213.3..',
  '....1121150555505613..13.',
  '.....12.15555555563..123.',
  '.....11..155000556...113.',
  '......11...501056.....3..',
  '............5556......3..',
  '.............666.........',
  '...........776678........',
  '........57717777188......',
  '.......567717171777856...',
  '......56777718177785556..',
  '.....556777771777785556..',
  '.....55677777777785556...',
  ],

  #----------困った I'm in trouble -5
  [
  '...........112...........',
  '..........12.............',
  '..........2..............',
  '...........2.............',
  '..........12.11113...13..',
  '.....12..1111121113.11133',
  '...1112..12111121113.1113',
  '..112.2.11111121111111113',
  '..12.2.111111111111211113',
  '....111111111111111211113',
  '..12.31112111121111111213',
  '..12.32112211122111122123',
  '..112.3112122112211121213',
  '...12.3121111212211112123',
  '...112.320001100021111213',
  '....12.35545555456213.3..',
  '....1121100055000613..13.',
  '.....12.15655655663..123.',
  '.....11..155555556...113.',
  '......11...501056.....3..',
  '............5556......3..',
  '.............666.........',
  '...........776678........',
  '........57717777188......',
  '.......567717171777856...',
  '......56777718177785556..',
  '.....556777771777785556..',
  '.....55677777777785556...',
  ]
]

def hexToRGB(hex):
  return int(hex[0:2], 16), int(hex[2:4], 16), int(hex[4:6], 16)

#---------------------------------------------
# コマンドライン引数処理
# arg processing
#
inFile = ''              # ファイルからメッセージを読む場合にファイル名を入れる; Enter file name if reading from a file
quiet = False            # True=メッセージを読まず顔出力のみ; True=Ignore message, only output face

showWhole = True         # True=出力文が短くても顔全体を表示する; True=Show whole face even if output sentence is short
imgSeq = 0               # 出力する顔の番号; Face number to output
align = 'R'              # R=右揃え、L=左揃え; R=right justified, L=left justified
argv0 = sys.argv.pop(0)
while (len(sys.argv) > 0 and re.match('^-', sys.argv[0])):
  arg = sys.argv.pop(0)
  if   arg == '--': break
  elif arg == '-l': align = 'L'
  elif arg == '-r': align = 'R'
  elif arg == '-q': quiet = True
  elif arg == '-d': showWhole = False
  elif arg == '-f' and len(sys.argv) > 0: inFile = sys.argv.pop(0)
  elif re.match('^-[0-' + str(len(img)-1) + ']$', arg): imgSeq = abs(int(arg))
  else: usage(argv0, version)

#---------------------------------------------
# 出力文字列を得る
# Get the output string
#
msg = '';
if quiet:
  msg = ''                   # 顔画像だけ出力させる場合はなにもしない; Do nothing if you only want to output the face

elif inFile != '':
  f = open(inFile, 'r')      # -f で指定したファイルを読み込むとき; When reading the file specified with -f
  msg = f.read()             # 改行が\nでないファイルだと問題があるかも。; There may be problems if the file does not have line breaks as \n
  f.close()
elif len(sys.argv) > 0:
  msg = ' '.join(sys.argv)   # コマンドライン引数から文字列を得るとき; When getting a string from cmd line arg
else:
  while True:                # 標準入力から文字列を得るとき; When getting a string from stdin
    try:
      msg += input() + "\n"
    except EOFError:
      break

#---------------------------------------------
# 出力文字列をいったん行毎に配列化し、制御文字を整形したうえで1つの文字列に戻す。
# 改行文字以外の制御文字を処理したいので。
#
# The output string is first arranged line by line, and then the control characters are formatted before being returned as a single string.
# Because I want to process control characters other than newline characters.
#
msg = msg.replace('\t', ' ').rstrip('\n')         # TABを空白にする。末尾の改行を削除する; Convert Tab to space. Remove trailing newline.
msgTmp = ''
for s in msg.splitlines():
  msgTmp += re.sub(r'[\x00-\x1F\x7F]', '', s) + '\n'
msg = msgTmp

#---------------------------------------------
# 出力行数を得る。ただし文字数が多すぎた場合はずれる。
# Gets the number of output lines. If the number of characters is too large, it will be off.
#
lineNum = msg.count('\n')
if lineNum <= 0: lineNum = 1

#---------------------------------------------
# 顔を表示する範囲を決め、配列から出力する要素のみを残す
# Decide the range to display the face and leave only the elements to be output from the array
#
if showWhole == False:
  yStart = 0
  yEnd = len(img[imgSeq])
  if lineNum < 6:                          # 顔は最小でも6行表示させる; Display atleast 6 lines of faces
    yStart = int(len(img[imgSeq]) / 2) - int(6 / 2) + 2
    yEnd = yStart + 6
  elif lineNum + 2 < len(img[imgSeq]):     # 顔サイズよりメッセージ文が短そうなとき; When message seems shorter than the face
    yStart = int(len(img[imgSeq]) / 2) - int(lineNum / 2) + 1
    yEnd = yStart + lineNum + 1
  img[imgSeq] = img[imgSeq][yStart : yEnd] # 配列から出力する要素のみ残す; Keep only the elements to be output from the array

#---------------------------------------------
# 端末の横幅を求め、顔が右端に来るよう左側に余白(.)を挿入する
# Calculate the width of the terminal and insert a margin (.) on the left side so that the face is on the right edge.
#
width = shutil.get_terminal_size().columns
if align == 'R':
  mWidth = width - len(img[imgSeq][0]) * 2;
  if mWidth > 0:
    for i in range(len(img[imgSeq])):
      img[imgSeq][i] = '.' * int(mWidth / 2) + img[imgSeq][i];
  else:
    # 画面が狭すぎるときは、文字列のみ出力して終了する
    # If screen is too narrow, output text only and exit.
    print('warning: too narrow screen', file=sys.stderr)
    exit()

#---------------------------------------------
# 字幅をカウントする。全角文字は2カウント。
# Count the width of the character. Full-width char are counted as 2.
#---------------------------------------------
def countChar(msg):
  N = 0
  for c in list(msg):
    w = unicodedata.east_asian_width(c)     # 出力文字の文字幅を求める; Get width of the output character
    if w in 'FWA': N += 2                   # 全角文字の場合; For full-width characters
    else: N += 1
  return N

#---------------------------------------------
# メッセージの出力開始行msgStartを決める
# Determine the message output start line msgStart
#
if align == 'R':
  msgStart = 0
  outN = countChar(msg)    # 出力したい文字数; Number of char to be output
  N = 0                    # 絵の横に出力できる文字数をカウントする変数; Var to count the number of char that can be printed next to the picture
  for s in range(len(img[imgSeq])):
    l = int(len(img[imgSeq])/2) + int(s/2+0.5) * ((-1)**s)
    for color in list(img[imgSeq][l]):
      if color == '.': N += 2          # 絵の1ドットを2文字分としてカウントする; Count one dot of the picture as two char
      else: break
    if outN < N:
      msgStart = int(len(img[imgSeq])/2) - int(s/2+0.5)
      break
  msgStart2 = int(len(img[imgSeq]) / 2 - lineNum / 2 + 0.5)  # 上下中央ぞろえの場合; Vertically centered
  if msgStart2 < 0: msgStart2 = 0
  if msgStart > msgStart2: msgStart = msgStart2   # より小さい方の行番号を開始位置にする; Start with smaller line number
else:
  for i in range(len(img[imgSeq])):
    img[imgSeq][i] = img[imgSeq][i][::-1]
  msgStart = int(len(img[imgSeq]) - lineNum)
  msgStart2 = int(len(img[imgSeq]) / 2 - lineNum / 2 + 0.5)  # 上下中央ぞろえの場合
  if msgStart2 < 0: msgStart2 = 0
  if msgStart > msgStart2: msgStart = msgStart2   # より小さい方の行番号を開始位置にする

#---------------------------------------------
# 画面出力（顔が左、メッセージが右の場合）
# Screen output (face on the left, message on the right)
#---------------------------------------------
def outLeft(img, imgSeq, width, msg, msgStart):
  msgChars = list(msg)
  print("\033[0m", end='')                                     # 文字設定のリセット; Reset character settings
  for l in range(len(img[imgSeq])):
    # 顔データを1行分出力
    # Output one line of face data
    for color in list(img[imgSeq][l]):
      if color == '.': print("\033[0m  ", end='')              # 背景を描画する; Print background
      else:
          r, g, b = hexToRGB(palette[int(color)])
          print(f"\033[48;2;{r};{g};{b}m  ", end='')             # 顔を描画する; Print face
    print("\033[0m", end='')                                   # 文字設定をリセットする; Reset character settings

    # 出力するメッセージが無いなら次の行へ
    # If there is no message to output, go to next line
    if l < msgStart or len(msgChars) <= 0:
      print('')
      continue

    # メッセージを出力する
    # Output a message
    x = len(img[imgSeq][l]) * 2                         # x...カーソル位置; x...cursor position
    while x < width:
      w = unicodedata.east_asian_width(msgChars[0])     # 出力文字の文字幅を求める; Get the char width of output char
      if w in 'FWA' and x + 1 >= width:                 # 全角文字で行をまたがる場合; When spanning lines with full-width char
        print(' ' * (width - x))
        break
      outc = msgChars.pop(0)                            # メッセージを1文字取り出す; Extract one char from message
      if outc == '\n':                                  # メッセージが改行だった場合; If message is a line break
        print(' ' * (width - x))
        break
      print(outc, end='')                               # メッセージを1文字出力する; Output a single message
      if w in 'FWA': x += 2                             # xの更新。全角なら+2; Update x. If full-width, it's +2.
      else: x += 1
  if len(msgChars) > 0: print(''.join(msgChars) + "\n") # 未出力の文字列があれば出力する; Output any unoutput strings

#---------------------------------------------
# 画面出力（顔が右、メッセージが左の場合）
# Screen output (face on the right, message on the left)

#---------------------------------------------
def outRight(img, imgSeq, width, msg, msgStart):
  msgChars = list(msg)
  print("\033[0m", end='')              # 文字設定のリセット; Reset character settings
  for l in range(len(img[imgSeq])):
    # フラグを初期化
    # Init flags
    msgok = True
    if l < msgStart: msgok = False      # True=メッセージ出力OK; True=Message output OK

    # 顔やメッセージを一文字ずつ出力
    # Output faces and messages one char at a time
    for color in list(img[imgSeq][l]):
      if color != '.': msgok = False    # 顔の右側に文字を表示させない; Don't display text to the right of the face

      # 色設定
      # Color Settings
      if color == '.': print("\033[0m", end='')               # 背景; background
      else:
          r, g, b = hexToRGB(palette[int(color)])
          print(f"\033[48;2;{r};{g};{b}m", end='')          # 顔; Print face

      # メッセージを出力しない場所の場合
      # In case no message is output
      if msgok == False or len(msgChars) <= 0:
        print('  ', end='')          # 空白を出力して次の文字へ; Output a space and move to the next char
        continue

      # 出力文字を1つ取り出す
      # Extract one output char
      outc = msgChars.pop(0)

      # 出力文字が改行コードだった場合
      # If the output char is a line feed code
      if outc == '\n':
        print('  ', end='')
        msgok = False
        continue

      # 出力文字が普通の文字だった場合
      # If the output char is normal char
      w = unicodedata.east_asian_width(outc)  # 文字幅を求める; Find char width
      if not(w in 'FWA'):                     # 1文字目が半角だったら後続文字との連結を試みる; If first char is half-width, try to concatenate it with the following char.
        if len(msgChars) <= 0: outc += ' '    # 後続文字が無い場合; If there are no subsequent char
        else:                                 # 後続文字がある場合; If there is a trailing char
          w = unicodedata.east_asian_width(msgChars[0])
          if not(w in 'FWA'):                 # 後続文字が半角なら取り出して連結; If the following char are half-width, extract and concatenate them
            outc2 = msgChars.pop(0)
            if outc2 == '\n':                 # 後続文字が改行コードだった場合; If the subsequent char is a line feed code
              outc2 = ' '
              msgok = False
            outc += outc2
          else:
            outc += ' '
      print(outc, end='')                     # 1文字出力; 1 char output
    print("\033[0m")                          # 行末の改行出力; Line feed output at the end of a line
  if len(msgChars) > 0: print(''.join(msgChars) + "\n")  # 未出力の文字列があれば出力する; Output any unoutput strings

#---------------------------------------------
# 画面出力
# Screen Output
#
if align == 'L': outLeft (img, imgSeq, width, msg, msgStart)
else:            outRight(img, imgSeq, width, msg, msgStart)

# 文字設定をリセットする
# Reset character settings
print("\033[0m", end='')
