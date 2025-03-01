# Phaser Magic Command

## 概要

Jypyter(notebook/lab)・VSCodeまたはGoogle ColabでPhaserを使ったコードセルのPythonコードをPyScriptを使ってiframe(ブラウザ)上で実行するマジックコマンドです。

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

以下は、Phaserライブラリを使って描画した赤い円を矢印キーで動かす例です。

Phaser関連クラスに辞書形式のオプションを渡す場合は、gameconfig関数を通じて渡す必要があります。(gamestart関数に渡すconfig変数は内部でgameconfig関数を使っているので使う必要はありません)

また、PyodideでPhaser関連クラスにコールバック関数を渡す場合は、Pyodide.ffi.create_proxy関数を通じて渡す必要があります。(MicroPythonではそのまま関数を渡しても大丈夫です)

```python
%%runphaser 500 500 white

# from pyodide.ffi import create_proxy

scene = None
cursor = None
graphics = None
x = 100
y = 100

def create(data):
  global cursor, graphics
  cursor = scene.input.keyboard.createCursorKeys()
  graphics = scene.add.graphics(gameconfig({'fillStyle': {'color': 0xff0000}}))


def update(time, delta):
  global x, y
  graphics.clear()
  if cursor.left.isDown:
    x -= 5
  if cursor.right.isDown:
    x += 5
  if cursor.up.isDown:
    y -= 5
  if cursor.down.isDown:
    y += 5
  graphics.fillCircle(x, y, 30)


scene = Phaser.Scene.new('SampleScene')
scene.create = create  # scene.create = create_proxy(create)
scene.update = update  # scene.update = create_proxy(update)

config = {
  'type': Phaser.AUTO,
  'width': 300,
  'height': 300,
  'scene': [scene]
}

game = gamestart(config)
```

Phaser.SceneクラスをPyScript用にラップしたPhaserSceneクラスを継承して独自のシーンクラスを作成する形でも記述できます。

PhaserSceneクラス内でcreate_proxy関数を通じたコールバックの設定をしているので、PyodideでもPhaserSceneクラスを継承する場合はcreate_proxy関数を使う必要はありません。

PhaserSceneクラスのインスタンスをconfigのsceneに設定する場合はインスタンスのsceneプロパティを渡す必要がありますが(例:`scene: [Scene1().scene]`)、

scenes関数を使ってPhaserSceneインスタンスを直接設定することもできます(例:`'scene': scenes(Scene1())`)。`,`で区切って複数渡すこともできます(例:`'scene': scenes(Scene1(), Scene2())`)。

```python
%%runphaser 500 500 white

class SampleScene(PhaserScene):
    def __init__(self):
        super().__init__('SampleScene')
        self.cursor = None
        self.graphics = None
        self.x = 100
        self.y = 100

    def create(self, this, data):
        self.cursor = this.input.keyboard.createCursorKeys()
        self.graphics = this.add.graphics(gameconfig({'fillStyle': {'color': 0xff0000}}))

    def update(self, this, time, delta):
        self.graphics.clear()
        if self.cursor.left.isDown:
            self.x -= 5
        if self.cursor.right.isDown:
            self.x += 5
        if self.cursor.up.isDown:
            self.y -= 5
        if self.cursor.down.isDown:
            self.y += 5
        self.graphics.fillCircle(self.x, self.y, 30)


config = {
    'type': Phaser.AUTO,
    'width': 300,
    'height': 300,
    'scene': scenes(SampleScene())
}

game = gamestart(config)
```

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

コードセルのコードをPyScriptを使ってiframe内で実行します。別のセルでpys_args変数を設定して実行している場合はその値がマジックコマンドの引数として使用されます。

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
