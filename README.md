# Music Box

【未完成】

音楽データを読み込み演奏する。
または、直接、番号を指定して演奏することもできる。

Music Box 本体で演奏するモードと、
スピーカーから擬似的な音を鳴らずモードがある。

* クライアント・サーバ間の通信は、Websocket。

* サーバは、JSON形式のコマンドを受取り、本体を制御する。
  
* MIDIなどの楽曲ファイルは、クライアント側でパージングし、
  独自の ``music_data`` 形式に変換して、サーバに送信する。


## 手順まとめ

### Install

```bash
      $ sudo pigpiod
      $ cd ~
      $ python3 -m venv env1
      $ cd ~/env1
      $ source ./bin/activate

(env1)$ git clone https://github.com/ytani01/MusicBox.git
(env1)$ cd ~/env1/MusicBox
(env1)$ ./install.sh
```

### サーボの調整

ブラウザからアクセスして、サーボモータの調整を行う。

```
URL: http://IPaddress:10080/
```


### Command line manual
```bash
(env1)$ MusicBox サブコマンド名 --help
```


### API Manual
```bash
(env1)$ python3 -m pydoc musicbox.クラス名
```

## 1. 少し解説


### 1.1 Music Box Server

Music Box 本体を直接制御するサーバ

Websocketで通信して、
Webインタフェースなどから、コマンドを受取り、
曲を演奏したり、単発で音を鳴らしたりする。

```
(env1)$ MusicBox svr &
```

Music Boxを鳴らす代わりに、スピーカーから音を鳴らす場合は、
``-w N``オプションをつける。
(N = 1, 2, 3)

Music Boxをシミュレートする
```
(env1)$ ./MusicBox svr -w 1 &
```

ピアノをシミュレートする (88音階)
```
(env1)$ ./MusicBox svr -w 2 &
```

sin波のサンプル音でシミュレートする (128音階)
```
(env1)$ ./MusicBox svr -w 3 &
```


### 1.2 Client side

Paper Tape 形式(テキスト・ファイル)の曲を再生
```bash
(env1)$ MusicBox txt kaeruno-uta.txt ws://localhost:8880/
```

MIDI形式の曲を再生
```bash
(env1)$ MusicBox midi joy.mid ws://localhost:8880/
```

再生をストップ
```bash
(env1)$ MusicBox cmd music_stop
```


## 2. Command Message Format for MusicBoxWebsockServer.py

サーバが受付けるコマンド・メッセージの形式

```bash
python3 -m pydoc musicbox.WsServer
```


## 5. Paper Tape Format

紙テープをテキストで擬した形式


### 5.1 例

```
# '#'以降はコメント
600                  # 以降の delay を 600msec とする
o-o-o----------
-o--o----------
--o-----o------
___o___o_____o_
-o-o-o---------
--o---o--------
--*-O-o--------      # 'o', 'O', '*'は、どれも紙テープの穴とみなす
```


### 6.3 MIDIに関するメモ

#### 6.3.1 トラック、チャンネル

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
演奏 -+--> [トラック1:チャンネル0]  -->
      |
      +--> [トラック2:チャンネル1]  -->
      |
      +--> [トラック3:チャンネル2]  -->
       :
       :
```

どれが主旋律かわからないので、自動選択は不可能。


#### 6.3.2 (note_on + velocity=0) == note_off !!

参考：[g200kg:Note Off ノートオフ](https://www.g200kg.com/jp/docs/dic/noteoff.html)


#### 6.3.A その他

* [情報処理学会:ピアノをMIDIで駆動する際のノート・オン・タイミングの補正について](https://ipsj.ixsq.nii.ac.jp/ej/index.php?active_action=repository_view_main_item_detail&page_id=13&block_id=8&item_id=55958&item_no=1)



## 10. Software

### Module Architecture

![Module Architecture](module-architecture.png)
