import shlex
import IPython.core.magic as magic  # type: ignore  # noqa: F401
import pysmagic
from IPython import get_ipython  # type: ignore  # noqa: F401


# magic commandを登録する関数
def register_phasermagic():
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

    # Phaser用追加スクリプト
    precode = """
import js

Phaser = js.Phaser

try:
    from pyodide.ffi import create_proxy
    is_piodide = True
except ImportError:
    is_piodide = False


class PhaserScene:
    def __init__(self, name):
        self.scene = Phaser.Scene.new(name)
        if is_piodide:
            self.preload_proxy = create_proxy(self._pyodide_preload)
            self.create_proxy = create_proxy(self._pyodide_create)
            self.update_proxy = create_proxy(self._pyodide_update)
            self.scene.preload = self.preload_proxy
            self.scene.create = self.create_proxy
            self.scene.update = self.update_proxy
        else:
            self.scene.preload = self._micropython_preload
            self.scene.create = self._micropython_create
            self.scene.update = self._micropython_update

    def __del__(self):
        if is_piodide:
            self.update_proxy.destroy()

    def _pyodide_preload(self):
        self.preload_proxy.destroy()
        self.preload(self.scene)

    def _pyodide_create(self, data):
        self.create_proxy.destroy()
        self.create(self.scene, data)

    def _pyodide_update(self, time, delta):
        self.update(self.scene, time, delta)

    def _micropython_preload(self):
        self.preload(self.scene)

    def _micropython_create(self, data):
        self.create(self.scene, data)

    def _micropython_update(self, time, delta):
        self.update(self.scene, time, delta)

    def preload(self, this):
        pass

    def create(self, this, data):
        pass

    def update(self, this, time, delta):
        pass


class PhaserGame:
    def __init__(self, config):
        self.game = Phaser.Game.new(PhaserGame.config(config))

    setPropFromPy = js.Function.new("obj", "key", "value", "obj[key] = value")

    @classmethod
    def scenes(cls, *scenes):
        result = []
        for scene in scenes:
            if isinstance(scene, PhaserScene):
                result.append(scene.scene)
            else:
                result.append(scene)
        return result

    @classmethod
    def _deep_dict_to_jsobj(cls, data):
        if not isinstance(data, dict):
            return data
        object = js.Object.new()
        for key, value in data.items():
            if isinstance(value, dict):
                PhaserGame.setPropFromPy(object, key, PhaserGame._deep_dict_to_jsobj(value))
            elif isinstance(value, list):
                PhaserGame.setPropFromPy(object, key, PhaserGame._deep_list_to_jsarray(value))
            else:
                PhaserGame.setPropFromPy(object, key, value)
        return object

    @classmethod
    def _deep_list_to_jsarray(cls, data):
        if not isinstance(data, list):
            return data
        array = js.Array.new()
        for value in data:
            if isinstance(value, dict):
                array.push(PhaserGame._deep_dict_to_jsobj(value))
            elif isinstance(value, list):
                array.push(PhaserGame._deep_list_to_jsarray(value))
            else:
                array.push(value)
        return array

    @classmethod
    def config(cls, config):
        return PhaserGame._deep_dict_to_jsobj(config)

    @classmethod
    def start(cls, config):
        game = PhaserGame(config)
        return game.game


scenes = PhaserGame.scenes

gameconfig = PhaserGame.config

gamestart = PhaserGame.start

"""

    # セル内のPythonコードとPhaser用追加スクリプトを結合
    args["py_script"] = precode + py_script

    return args


def default_phaser_args():
    return {
        "width": "500",
        "height": "500",
        "background": "white",
        "py_type": "mpy",
        "py_val": None,
        "py_conf": None,
        "js_src": None,
        "py_ver": "none",
        "py_script": "",
    }

def parse_phaser_args(line, cell):
    # 引数のパース
    line_args = shlex.split(line)
    def_args = default_phaser_args()
    ipython_user_ns = get_ipython().user_ns

    if len(line_args) == 0:
        if 'pys_args' in ipython_user_ns.keys() and isinstance(ipython_user_ns['pys_args'], dict):
            args = pysmagic.merge_dict(def_args, ipython_user_ns['pys_args'])
        else:
            args = def_args
    else:
        args = {}
        args["width"] = line_args[0] if len(line_args) > 0 else def_args["width"]
        args["height"] = line_args[1] if len(line_args) > 1 else def_args["height"]
        args["background"] = line_args[2] if len(line_args) > 2 else def_args["background"]
        args["py_type"] = line_args[3] if len(line_args) > 3 else def_args["py_type"]
        args["py_val"] = line_args[4] if len(line_args) > 4 and line_args[4] != "{}" else def_args["py_val"]
        args["py_conf"] = line_args[5] if len(line_args) > 5 and line_args[5] != "{}" else def_args["py_conf"]
        args["js_src"] = line_args[6] if len(line_args) > 6 and line_args[6] != "[]" else def_args["js_src"]
        args["py_ver"] = line_args[7] if len(line_args) > 7 else def_args["py_ver"]

    args["py_script"] = cell

    return args
