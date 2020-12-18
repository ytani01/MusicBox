# Music Box

【未完成】

音楽データを読み込み演奏する。
または、直接、チャンネル番号を指定して演奏することもできる。

Music Box 本体で演奏するモードと、
スピーカーから擬似的な音を鳴らずモードがある。

* クライアント・サーバ間の通信は、Websocket

* サーバが受付けるメッセージは、独自のJSON形式
  (後述)

* Client API(後述)を使えば、Websocketやメッセージ形式を意識する必要はない

* ファイルのパージングは、クライアント側で行う


## TL;DR

```bash
      $ sudo pigpiod
      $ cd ~
      $ python3 -m venv env1
      $ cd ~/env1
      $ git clone https://github.com/ytani01/MusicBox.git
      $ source ./bin/activate
(env1)$ cd ~/env1/MusicBox
(env1)$ pip install -r requirements.txt
(env1)$ ./MusicBoxWebsockServer.py &
(env1)$ ./MusicBoxWebsockClient.py ws://localhost:8881/ papaer_tape/kaeruno-uta.txt
(env1)$ ./MusicBoxWebsockClient.py ws://localhost:8881/
      > 0 2 4
      > stop
      > [Ctrl]-[D]
(env1)$
```

### Client API: Simple Usage

内部では、Websocket通信を行っているが、
この Client APIを使えば、
ほとんど意識する必要は無い。

```python
from MusicBoxWebsockClient import MusicBoxWebsockClient

cl = MusicBoxWebsockClient('ws://ipaddr:port/')

cl.single_play([0,1, ..])
cl.midi(filename)           # TBD
cl.paper_tape(filename)
cl.music_start()
cl.music_pause()
cl.music_rewind()
cl.music_stop()

cl.end()     # Call at the end of program
```

APIのマニュアルは、以下で見ることができます。

```bash
$ . ~/env1/bin/activate
(env1)$ cd ~/env1/MusicBox
(env1)$ python3 -m pydoc MusicBoxWebsockClient.MusicBoxWebsockClient
```

## 1. Install

```bash
$ cd ~
$ python3 -m venv env1
$ cd ~/env1
$ git clone https://github.com/ytani01/MusicBox.git
$ cd ~/env1/MusicBox
$ pip install -r requirements.txt
```

## 2. Execute

クライアント・サーバ構成になっている。

サーバーを起動してから、クライアントで制御する。

クライアントのサンプルは、
コマンドを単発で実行するモードと、
対話的に実行するモードがある。

### 2.1 Common

クライアントもサーバーも、まずは以下を実行する。

```bash
      $ sudo pigpiod
      $ source ~/env1/bin/activate
(env1)$ cd ~/env1/MusicBox
```

### 2.2 Server side

```
(env1)$ ./MusicBoxWebsockServer.py &
```

Music Boxを鳴らす代わりに、スピーカーから音を鳴らす場合は、
``-w``オプションをつける。

```
(env1)$ ./MusicBoxWebsockServer.py -w &
```

## 2.3 Client side (one time): サンプル実装

一つずつコマンドを実行 (サーバーに送信) する方法

```bash
(env1)$ ./MusicBoxWebsockClinet.py ws://localhost:8881/ paper_tape paper_tape/kaeruno-uta.txt
(env1)$ ./MusicBoxWebsockClinet.py ws://localhost:8881/ midi midi/joy-4-62.midi -c 4
(env1)$ ./MusicBoxWebsockClinet.py ws://localhost:8881/ stop
```
## 2.3 Client side (interactive mode): サンプル実装

インタラクティブ(対話)モード

```bash
(env1)$ ./MusicBoxWebsockClinet.py ws://localhost:8881/
> help
 :
> 0 2 4
> [Ctrl]-[D] to end
```


## 2.4 Message Format for Music Box Server

```
{"cmd": "single_play", "ch": [0,2,4]}  # single play

{"cmd": "music_load",                  # load music and play
 "music_data": [
  {"ch": null,"delay": 500},
  {"ch": [0,2,4], "delay": null},
  {"ch": [], "delay": null}
]}

{"cmd": "music_start"}                 # (re)start music
{"cmd": "music_pause"}
{"cmd": "music_rewind"}
{"cmd": "music_stop"
```


## 3. Paper Tape Format

紙テープをテキストで擬した形式


### 3.1 例

```
# '#'以降はコメント
600 # delayを600msecとする
o-o-o----------
-o--o----------
--o-----o------
___o___o_____o_
-o-o-o---------
--o---o-------- 400  # delayを指定することも可能(どう扱うかはアプリ依存)
--*-O-o--------      # 'o', 'O', '*'は、どれも紙テープの穴とみなす
```


### 3.2 詳細

* 紙テープと同様にどの音を鳴らすか、記号で指定する。

* '-o-O- 600'のように、文字列のあとに delayを記述できる。

* データに記述された delayをどう扱うか
  (以降のデフォルト値を変更 or 一時的なdelay)
  は、上位のアプリに依存。

* '---------------'は、スリープ
  ('-'のように一文字でも同様)

* '#'以降は、コメント


## 4. MIDIパーサー: MusicBoxMidi.py

MIDIファイルを解析し、
以下の ``Data Format`` でオルゴールのデータに変換する。

* トラック、チャンネルを選択することができる。

  (``parse``メソッドの ``track``, ``channel``パラメータ)

* キー(音程)を調整して、
  なるべく多くの音が Music Box で再生できるよう自動調整する。
  
  (``parse``メソッドの ``base``パラメータ)
  
### 4.0 Simple Usaege

```python
from MusicBoxMidi import MusicBoxMidi

parser = MusicBoxMidi()

music_data = parser.parse(midi_file)

  :

parser.end()   # end of program
```

  
### 4.1 Output Data Format

```
music_data := list of ``data_ent``

data_ent := {'ch': ``ch_list``, 'delay': ``delay_msec``}

ch_list := list of int
    Music Box のチャンネル(サーボ番号)のリスト
    
delay_msec := int
    音を鳴らした後の遅延 [msec]
```

例
```
(Python形式)
[
  {'ch': [0, 2, 4]: 'delay': 500},
  {'ch': [1, 3]: 'delay': 5},
  {'ch': [0], 'delay': 200},
    :
]
```

### 4.2 MIDIパーサー API

```bash
$ python3 -m pydoc MusicBoxMidi.MusicBoxMidi
```


## memo

### MIDIに関するメモ

#### トラック、チャンネル

* トラック: 楽譜に相当
* チャンネル: 楽器に相当

* 1つのトラックに、複数のチャンネルが存在可能
* トラック、チャンネルは、「直列的に」結合されている。

```
MIDIデータ: [トラック1:チャンネル1]-[トラック1:チャンネル2]- --->
```

再生するには、
トラック・チャンネンルに分割して、
「並列に」再生する必要がある。

```
演奏 -+--> [トラック1:チャンネル1]  -->
      |
      +--> [トラック1:チャンネル2]  -->
```

どれが主旋律かわからないので、自動選択は不可能。

## A. References
