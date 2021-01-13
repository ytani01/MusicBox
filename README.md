# Music Box

【未完成】

音楽データ(MIDI, 独自のPaperTape)を読み込み演奏する。

Music Box 本体で演奏するモードと、
スピーカーから擬似的な音を鳴らずモードがある。

* 二種類のサーバで構成されている。

  - メイン・サーバ: 本体を制御するサーバ

    Websocketで、JSON形式のコマンドを受取り、
    本体を制御する。
    
    本体を制御する代わりに、
    擬似的な音をスピーカーから再生するモードもあり、
    本体では再生できない音階も再生可能。(... 後述)
    
    ポート番号を変えて、複数のモードを同時に立ち上げることが可能。
    
  - Webサーバ: ユーザインタフェース用: ``http://IPorHOST:10080/musicbox/``
  
    ユーザからの入力を受け、メインサーバとWebsocket通信する。
    (メイン・サーバからみるとクライアントとして動作する。)

    ファイルのアップロード、
    アップロードされたファイルの管理・保存、
    パージングは、
    Webサーバで行い、
    パージングした結果のデータをメイン・サーバに送信して、演奏する。

    (パージング結果をWebサーバ側で適切に管理すれば、
    毎回パージングする必要は無い。)

* 全ての機能(上記2種類のサーバ、パージングなど)は、
  一つのコマンド「``MusicBox``」で実行する。

  (``git``コマンドなどと同様)


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


### 全サービスの起動(再起動)

メインサーバとWebサーバを起動する。
既に起動している場合は、全て終了(kill)してから、再起動する。

```bash
$ boot-musicbox.sh
```

全サービスを終了(kill)する場合は、
```bash
$ boot-musicbox.sh -k
```

### サーボの調整

ブラウザからアクセスして、サーボモータの調整を行う。

```
URL: http://IPaddress:10080/musicbox/
```


## マニュアル

### API Manual
```bash
(env1)$ python3 -m pydoc musicbox.クラス名
```


### Command line manual
```bash
$ MusicBox サブコマンド名 -h
```


## 1. 少し解説

### 1.0 インストール後のディレクトリ構造

```bash
$ install.sh help
````

```
[インストール後のディレクトリ構造]

 $HOME/ ... ホームディレクトリ
    |
    +- bin/ ... シェルスクリプトなど
    |   |
    |   +- MusicBox ... メイン・コマンド・スクリプト (wrapper script)
    |   +- boot-musicbox.sh ... 起動スクリプト
    |
    +- musicbox-env ... 環境変数設定ファイル【インストール時に作成】
    |    【環境変数】
    |    MUSICBOX_DIR ... git clone されたディレクトリ
    |    MUSICBOX_WORK ... 作業用ディレクトリ ($HOME/msucibox_work/)
    |    VENVDIR ... python3 Virtualenv ディレクトリ ($HOME/env1/ など)
    |    (etc.)
    |
    +- musicbox-servo.conf ... サーボ調整パラメータ保存ファイル
    |
    +- musicbox_work/ ... 作業用ディレクトリ
    |   |
    |   +- upload/ ... アップロードされたファイル(MIDIなど)
    |   +- music_data/ ... パーズ後の音楽データ
    |   +- log/ ... ログディレクトリ
    |
    +- env1/  ... python3 Virtualenv(venv) 【ユーザが作成する】
        |
        +- musicbox/ ... musicboxプロジェクトの gitリポジトリ
        |
        | 【以下、インストールに必要なライブラリなど】
        |
        +- ServoPCA9685/
        +- StepperMotor/
        +- MIDI-lib/
        :

```

### 1.1 Music Box メイン・サーバ

Music Box 本体を直接制御するサーバ

Websocketで通信して、
Webインタフェースなどから、コマンドを受取り、
曲を演奏したり、単発で音を鳴らしたりする。

以下は、基本的な使い方のみ。
オプションの詳細については、下記、リファレンスを参照
```bash
$ MusicBox server -h
```

#### 1.1.1 通常の起動

```bash
$ MusicBox server &
```

#### 1.1.2 Music Boxを鳴らす代わりに、スピーカーから音を鳴らす場合

``-w N``オプションをつける。
(N = 1, 2, 3)

Music Boxをシミュレートする
```bash
$ ./MusicBox server -w 1 &
```

ピアノをシミュレートする (88音階)
```bash
$ ./MusicBox server -w 2 &
```

sin波のサンプル音でシミュレートする (128音階)
```bash
$ ./MusicBox server -w 3 &
```


### 1.2 Client side

以下、いくつかの例を示す。

詳細は、下記のマニュアル参照。

```bash
$ MusicBox -h
$ MusicBox サブコマンド名 -h
$ python3 -m pydoc musicbox.WsServer
```

#### 1.2.1 1回音を鳴らす (下記の例では、和音)
```bash
$ MusicBox send single_play 0 2 4
```


#### 1.2.2 ``Paper Tape Text``形式(独自)の曲を再生
```bash
$ MusicBox ptt kaeruno-uta.txt ws://localhost:8880/
```


#### 1.2.3 MIDI形式の曲を再生
```bash
$ MusicBox midi joy.mid ws://localhost:8880/
```


#### 1.2.4  再生をストップ/再開/シーク

```bash
$ MusicBox send music_stop
$ MusicBox send music_start
$ MusicBox send music_seek 30
```


#### パージング結果をファイルに保存し、それをサーバに送信

この方法だと、パージング処理を毎回しないで済む。
```bash
$ MusicBox midi midi_file  music_data.json
$ MusicBox send music_load  music_data.json
```


## 2. Command Message Format for MusicBoxWebsockServer.py

サーバが受付けるコマンド・メッセージの形式などについては、
下記を参照。

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



## 9 MIDIに関するメモ

### 9.1 トラック、チャンネル

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


### 9.2 (note_on + velocity=0) == note_off !!

参考：[g200kg:Note Off ノートオフ](https://www.g200kg.com/jp/docs/dic/noteoff.html)


### 9.9 その他

* [情報処理学会:ピアノをMIDIで駆動する際のノート・オン・タイミングの補正について](https://ipsj.ixsq.nii.ac.jp/ej/index.php?active_action=repository_view_main_item_detail&page_id=13&block_id=8&item_id=55958&item_no=1)



## 10. Module Architecture

![Module Architecture](module-architecture.png)
