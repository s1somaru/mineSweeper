# consts.py
# --- サイズ設定 ---
CELL_SIZE = 30         # 1マスのピクセルサイズ
HEADER_HEIGHT = 50     # 上部のメッセージエリアの高さ
FONT_SIZE_HEADER = 24  # 結果表示用の大きなフォントサイズ

# --- 状態を表す定数（logicとviewで共有） ---
MINE = -1       # 地雷がある（または踏んだ）
UNOPENED = -2   # まだ開いていない
FLAGGED = -3    # 旗が立っている

# --- 色の設定 ---
COLOR_UNOPENED = "lightgray" # 未開封マスの色
COLOR_MINE = "red"           # 地雷の色
COLOR_OPENED = "white"       # 開いたマスの色
COLOR_TEXT = "blue"          # 数字の色
COLOR_FLAG = "orange"        # 旗の文字色
COLOR_BTN_OPEN = "lightblue" # 「開くモード」ボタンの色
COLOR_BTN_FLAG = "orange"    # 「旗モード」ボタンの色
COLOR_BG = "gray"            # ウィンドウの背景色