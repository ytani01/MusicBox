# Music Box

【未完成・内容が古い】

音楽データを読み込み演奏する。
または、直接、チャンネル番号を指定して演奏することもできる。

Music Box 本体で演奏するモードと、
スピーカーから擬似的な音(wav形式)を鳴らずモードがある。


## TL;DR

### 0.1 Install

```bash
$ cd ~
$ python3 -m venv env1
$ cd ~/env1
$ git clone https://github.com/ytani01/MusicBox.git
$ cd ~/env1/MusicBox
$ pip install -r requirements.txt
```

### 0.2 Execute

クライアント・サーバ構成になっている。

サーバーを起動してから、クライアントで制御する。

#### 0.2.1 Common

クライアントもサーバーも、まずは以下を実行する。

```bash
$ . ~/env1/bin/activate
(env1)$ cd ~/env1/MusicBox
```

#### 0.2.2 Server side

```
(env1)$ ./MusicBoxWebsockServer.py
```

#### 0.2.3 Client side (play paper tape file)

一つのコマンドを実行する

```bash
(env1)$ ./MusicBoxWebsockclinet.py ws://localhost:8881/ paper_tape
```
#### 0.2.3 Client side (interactive mode)

インタラクティブ(対話)モード

```bash
(env1) ~/env1/MusicBox$ ./MusicBoxWebsockclinet.py paper_tape
> 0 2 3
:
> [Ctrl]-[D] to end
```

### Client API

```
```bash
$ . ~/env1/bin/activate
(env1)$ cd ~/env1/MusicBox
(env1)$ python3 -m pydoc MusicBoxWebsockClient.MusicBoxWebsockClient
```


## 2. Paper Tape Format

紙テープをテキストで擬した形式


### 2.1 例

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


### 2.2 詳細

* 紙テープと同様にどの音を鳴らすか、記号で指定する。

* '-o-O- 600'のように、文字列のあとに delayを記述できる。

* データに記述された delayをどう扱うか
  (以降のデフォルト値を変更 or 一時的なdelay)
  は、上位のアプリに依存。

* '---------------'は、スリープ
  ('-'のように一文字でも同様)

* '#'以降は、コメント


## A. References

