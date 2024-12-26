import shlex
import IPython.core.magic as magic  # type: ignore  # noqa: F401
import pysmagic


# magic commandを登録する関数
def register_phasermagic():
    from IPython import get_ipython  # type: ignore  # noqa: F401
    ipy = get_ipython()
    ipy.register_magic_function(runphaser)
    ipy.register_magic_function(genphaser)
    print("Registered Phaser magic commands.")


# iframe内でPyScriptを実行するマジックコマンド
@magic.register_cell_magic
def runphaser(line, cell):
    """
    セル内のPhaserを使ったPythonコードをPyScriptを用いてiframe内で実行するマジックコマンド

    Usage:
        %%runpys [width] [height] [background] [py_type] [py_val] [py_conf] [js_src] [py_ver]

    Args:
        width: iframeの幅を指定します。デフォルトは500です。
        height: iframeの高さを指定します。デフォルトは500です。
        background: iframeの背景色を指定します。デフォルトはwhiteです。
        py_type: 実行するPythonの種類。pyまたはmpyを指定します。pyはCPython互換のPyodide、mpyはMicroPytonで実行します。デフォルトはmpyです。
        py_val: PyScriptに渡すデータを''で囲んだJSON文字列形式で設定します。デフォルトは'{}'です
        py_conf: PyScriptの設定を''で囲んだJSON文字列形式で指定します。デフォルトは'{}'です。
        js_src: 外部JavaScriptのURLを''で囲んだ文字列のJSON配列形式で指定します。デフォルトは'[]'です。
        py_ver: PyScriptのバージョンを指定します.
    """
    # 引数のパース
    args = parse_phaser_args(line, cell)
    args = set_phaser_args(args)
    args["htmlmode"] = False

    # PyScriptを実行
    pysmagic.run_pyscript(args)


@magic.register_cell_magic
def genphaser(line, cell):
    """
    セル内のPhaserを使ったPythonコードをPyScriptを用いてiframe内で実行するために生成したHTMLを表示するマジックコマンド
    """
    # 引数のパース
    args = parse_phaser_args(line, cell)
    args = set_phaser_args(args)
    args["htmlmode"] = True

    # PyScriptを実行
    pysmagic.run_pyscript(args)


def run_phaser_script(args):
    args = set_phaser_args(args)
    pysmagic.run_pyscript(args)


def set_phaser_args(args):
    # pythonコードを取得
    py_script = args.get("py_script", "")

    # 外部JavaScriptの追加
    args["add_src"] = ["https://cdn.jsdelivr.net/npm/phaser@v3/dist/phaser.min.js"]

    # phaser用追加スクリプト
    precode = """
import js

Phaser = js.Phaser

def deep_dict_to_jsobj(data):
  if not isinstance(data, dict):
    return data
  object = js.Object.new()
  for key, value in data.items():
    if isinstance(value, dict):
      object[key] = deep_dict_to_jsobj(value)
    elif isinstance(value, list):
      object[key] = deep_list_to_jsarray(value)
    else:
      object[key] = value
  return object


def deep_list_to_jsarray(data):
  if not isinstance(data, list):
    return data
  array = js.Array.new()
  for value in data:
    if isinstance(value, dict):
      array.push(deep_dict_to_jsobj(value))
    elif isinstance(value, list):
      array.push(deep_list_to_jsarray(value))
    else:
      array.push(value)
  return array

def set_config(config):
  return deep_dict_to_jsobj(config)

"""

    aftercode = """
game = Phaser.Game.new(deep_dict_to_jsobj(config))

"""

    # セル内のPythonコードとjspreadsheet実行スクリプトを結合
    args["py_script"] = precode + py_script + aftercode

    return args


def parse_phaser_args(line, cell):
    # 引数のパース
    line_args = shlex.split(line)
    args = {}
    args["width"] = line_args[0] if len(line_args) > 0 else "500"
    args["height"] = line_args[1] if len(line_args) > 1 else "500"
    args["background"] = line_args[2] if len(line_args) > 2 else "white"
    args["py_type"] = line_args[3] if len(line_args) > 3 else "mpy"
    args["py_val"] = line_args[4] if len(line_args) > 4 and line_args[4] != "{}" else None
    args["py_conf"] = line_args[5] if len(line_args) > 5 and line_args[5] != "{}" else None
    args["js_src"] = line_args[6] if len(line_args) > 6 and line_args[6] != "[]" else None
    args["py_ver"] = line_args[7] if len(line_args) > 7 else "none"
    args["py_script"] = cell

    return args
