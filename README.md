# Phaser Magic Command

## 概要

Jypyter(notebook/lab)・VSCodeまたはGoogle ColabでPhaser.jsを使ったコードセルのPythonコードをPyScriptを使ってiframe(ブラウザ)上で実行するマジックコマンドです。

## 使い方

### マジックコマンドの追加

コードセルに以下のコードを貼り付けて実行しマジックコマンドを登録してください。カーネルやランタイムを再起動する度に再実行する必要があります。

```python
%pip install -q -U pysmagic phasermagic
from phasermagic import register_phasermagic

register_phasermagic()
```

### マジックコマンドの使い方

コードセルの冒頭に以下のようにマジックコマンドを記述してください。実行するとアウトプットにiframeが表示されてその中でコードセルのコードがPyScriptで実行されます。

### グローバル変数

PyScriptから以下の変数にアクセスできます。

- 別のセルで設定したグローバル変数(_で始まる変数名やJSONに変換できないものは除く)
- マジックコマンドの引数py_valで設定した変数
- width: iframeの幅(マジックコマンドの引数で指定した幅)
- height: iframeの高さ(マジックコマンドの引数で指定した高さ)

この変数はjs.pysオブジェクトを介してアクセスできます。
変数名が衝突した場合は上記リストの順に上書きされて適用されます。

### マジックコマンド

#### %%runphaser

コードセルのコードをPyScriptを使ってiframe内で実行します。

```jupyter
%%runphaser [width] [height] [background] [py_type] [py_val] [py_conf] [js_src] [py_ver]
```

- width: iframeの幅を指定します。デフォルトは500です。
- height: iframeの高さを指定します。デフォルトは500です。
- background: iframeの背景色を指定します。デフォルトはwhiteです。
- py_type: 実行するPythonの種類。pyまたはmpyを指定します。pyは CPython互換のPyodide、mpyはMicroPytonで実行します。デフォルトはmpyです。
- py_val: PyScriptに渡すデータを''で囲んだJSON文字列形式で設定します。デフォルトは'{}'です
- py_conf: PyScriptの設定を''で囲んだJSON文字列形式で指定します。デフォルトは'{}'です。
- js_src: 外部JavaScriptのURLを''で囲んだ文字列のJSON配列形式で指定します。デフォルトは'[]'です。
- py_ver: PyScriptのバージョンを指定します、Noneを指定するとモジュール内部で設定したデフォルトのバージョンを使用します。デフォルトはNoneです。

#### %%genphaser

セル内のPythonコードをPyScriptを用いてiframe内で実行するために生成したHTMLを表示するマジックコマンド

引数は%%runphaserと同じです。
