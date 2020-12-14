# Music Box

【未完成】

Paper Tape Format(後述)に従って書かれた
楽譜データ(テキストファイル)を読み込み
演奏する。

Music Box 本体で演奏するモードと、
スピーカーから擬似的な音(wav形式)を鳴らずモードがある。

## ToDo

* クラスライブラリ化して、Webアプリなどから利用できるようにする。
* 本体での演奏と、スピーカーから音をならすときの delayを共通化する。


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

```bash
$ . ~/env1/bin/activate
(env1)$ cd ~/env1/MusicBox
(env1)$ ./MusicBoxPlayer.py kaeruno-uta.txt
```


## 1. MusicBoxPlayer.py

プログラム本体

### 1.1 Usage

以下のヘルプを参照

```bash
$ ./MusicBoxPlayer.py -h
```

## 2. Paper Tape Format

紙テープをテキストで擬した形式


### 2.0 TBD

Music Box本体で演奏する場合、
サーボの動作に遅延があるが、
スピーカーを鳴らすときとは、遅延がない。

このため、
楽譜データの delayの値を共通にできない。


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

