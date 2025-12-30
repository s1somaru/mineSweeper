# view.py
from graphics import *
import consts as c

class MinesweeperView:
    def __init__(self, size, num_mines):
        self.size = size
        self.num_mines = num_mines
        self.control_height = 60  # 下のボタンエリアの高さ
        
        # ウィンドウの幅を計算（盤面が小さすぎるときは最低幅350にする）
        board_pixel_width = size * c.CELL_SIZE
        self.window_width = max(board_pixel_width, 350)
        
        # ★ウィンドウの高さ計算
        # ヘッダー(上) + 盤面(真ん中) + コントロールエリア(下)
        self.window_height = c.HEADER_HEIGHT + size * c.CELL_SIZE + self.control_height
        
        # 盤面を左右中央に寄せるための隙間（オフセット）を計算
        self.offset_x = (self.window_width - board_pixel_width) / 2
        
        # ウィンドウ作成
        self.win = GraphWin("Minesweeper", self.window_width, self.window_height)
        self.win.setBackground(c.COLOR_BG)
        
        # 描画オブジェクトを管理するリストや辞書
        self.rects = []       # マスの四角形
        self.flag_icons = {}  # 旗の文字("F")
        self.text_objects = {} # 数字の文字
        
        # UIパーツの変数を初期化
        self.btn_area = None
        self.btn_label = None
        self.msg_text = None     # 下部のメッセージ用（Click to Closeなど）
        self.header_text = None  # 上部のデカ文字用（GAME OVERなど）
        
        self.remain_bg = None
        self.remain_text = None
        
        # 画面の初期描画を実行
        self._init_gui()
        # 残り地雷数を表示
        self.display_remaining_mines([], self.num_mines)

    def _init_gui(self):
        """画面の基本パーツ（ヘッダー、盤面、ボタン）を描画するメソッド"""
        
        # 1. 上部のヘッダーエリア（結果表示用）を描画
        header_bg = Rectangle(Point(0, 0), Point(self.window_width, c.HEADER_HEIGHT))
        header_bg.setFill("white")
        header_bg.setOutline("gray")
        header_bg.draw(self.win)
        
        # ヘッダーのテキスト（最初は空っぽにしておく）
        self.header_text = Text(Point(self.window_width/2, c.HEADER_HEIGHT/2), "")
        self.header_text.setSize(c.FONT_SIZE_HEADER)
        self.header_text.setStyle("bold")
        self.header_text.draw(self.win)

        # 2. 盤面の描画（グリッド作成）
        for r in range(self.size):
            row_rects = []
            for col in range(self.size):
                # X座標: 中央寄せのオフセットを足す
                x1 = self.offset_x + col * c.CELL_SIZE
                # ★Y座標: ヘッダーの高さ分だけ下にずらす！
                y1 = c.HEADER_HEIGHT + r * c.CELL_SIZE
                
                x2 = self.offset_x + (col + 1) * c.CELL_SIZE
                y2 = c.HEADER_HEIGHT + (r + 1) * c.CELL_SIZE
                
                rect = Rectangle(Point(x1, y1), Point(x2, y2))
                rect.setFill(c.COLOR_UNOPENED)
                rect.setOutline("gray")
                rect.draw(self.win)
                row_rects.append(rect)
            self.rects.append(row_rects)
            
        # 3. 下部のコントロールエリアを描画
        # 開始位置は「ヘッダー高さ + 盤面の高さ」の場所から
        y_start = c.HEADER_HEIGHT + self.size * c.CELL_SIZE
        bg = Rectangle(Point(0, y_start), Point(self.window_width, self.window_height))
        bg.setFill("white")
        bg.draw(self.win)
        
        # モード切替ボタンの描画
        self.btn_area = Rectangle(Point(5, y_start+10), Point(140, y_start+50))
        self.btn_area.setFill(c.COLOR_BTN_OPEN)
        self.btn_area.setOutline("black")
        self.btn_area.draw(self.win)
        
        self.btn_label = Text(Point(72.5, y_start+30), "⛏️ MODE: OPEN")
        self.btn_label.setStyle("bold")
        self.btn_label.draw(self.win)
        
        # 下部のメッセージエリア（操作説明用）
        space_center_x = (140 + (self.window_width - 110)) / 2
        self.msg_text = Text(Point(space_center_x, y_start+30), "")
        self.msg_text.setSize(10)
        self.msg_text.draw(self.win)

    def update_mode_button(self, is_open_mode):
        """ボタンの色と文字をモードに合わせて切り替える"""
        if is_open_mode:
            self.btn_area.setFill(c.COLOR_BTN_OPEN)
            self.btn_label.setText("⛏️ MODE: OPEN")
        else:
            self.btn_area.setFill(c.COLOR_BTN_FLAG)
            self.btn_label.setText("🚩 MODE: FLAG")

    def show_message(self, text, color="black"):
        """
        メッセージを表示するメソッド。
        内容によって表示場所（上か下か）を自動で振り分けるよ！
        """
        if "Click" in text:
            # 「クリックして終了」などの案内は、下側の小さいエリアに表示
            self.msg_text.setText(text)
            self.msg_text.setTextColor(color)
        else:
            # 「GAME OVER」や「YOU WIN」などの結果は、上側のヘッダーに大きく表示
            self.header_text.setText(text)
            self.header_text.setTextColor(color)

    def display_remaining_mines(self, display, num_mines):
        """右下に残り地雷数（地雷数 - フラグ数）を表示する"""
        if not display:
            remain = num_mines
        else:
            remain = self._remainMines(display, num_mines)
        
        text_str = f"Mines: {remain}"
        
        # 表示位置の計算（盤面の下）
        y_start = c.HEADER_HEIGHT + self.size * c.CELL_SIZE
        
        bg_p1 = Point(self.window_width - 110, y_start + 15)
        bg_p2 = Point(self.window_width - 10, y_start + 45)
        text_center = Point(self.window_width - 60, y_start + 30)

        # 初回作成時と更新時で処理を分ける
        if self.remain_text is None:
            self.remain_bg = Rectangle(bg_p1, bg_p2)
            self.remain_bg.setFill("black") 
            self.remain_bg.setOutline("gray")
            self.remain_bg.draw(self.win)
            
            self.remain_text = Text(text_center, text_str)
            self.remain_text.setSize(14)
            self.remain_text.setStyle("bold")
            self.remain_text.setTextColor("red")
            self.remain_text.draw(self.win)
        else:
            self.remain_text.setText(text_str)

    def _remainMines(self, display, num_mines):
        """盤面にあるフラグの数を数えて、残り地雷数を計算する"""
        flagged_count = sum(row.count(c.FLAGGED) for row in display)
        return num_mines - flagged_count

    def refresh_board(self, display):
        """盤面の状態（数字、開いた、フラグなど）を見て画面を更新する"""
        for r in range(self.size):
            for col in range(self.size):
                val = display[r][col]
                rect = self.rects[r][col]
                key = (r, col)
                
                # マスの中心座標を取得
                cx, cy = rect.p1.getX() + c.CELL_SIZE/2, rect.p1.getY() + c.CELL_SIZE/2

                # --- フラグの描画 ---
                if val == c.FLAGGED:
                    if key not in self.flag_icons:
                        ft = Text(Point(cx, cy), "F")
                        ft.setFill(c.COLOR_FLAG)
                        ft.setStyle("bold")
                        ft.draw(self.win)
                        self.flag_icons[key] = ft
                    continue

                # もしフラグじゃなくなっていたら、フラグのアイコンを消す
                if key in self.flag_icons:
                    self.flag_icons[key].undraw()
                    del self.flag_icons[key]
                
                # --- 開いたマスの描画 ---
                if val != c.UNOPENED:
                    rect.setFill(c.COLOR_OPENED)
                    if val == c.MINE:
                        rect.setFill(c.COLOR_MINE)
                    elif val > 0:
                        # 数字を描画（まだ描画してない場合のみ）
                        if key not in self.text_objects:
                            t = Text(Point(cx, cy), str(val))
                            t.setFill(c.COLOR_TEXT)
                            t.draw(self.win)
                            self.text_objects[key] = t
        
        # 残り地雷数表示も更新
        self.display_remaining_mines(display, self.num_mines)

    def get_click(self):
        """マウスクリックを待機して座標を返す（エラー処理付き）"""
        try:
            return self.win.getMouse()
        except GraphicsError:
            return None

    def is_button_clicked(self, p):
        """クリックされた場所がボタンの中かどうか判定"""
        x, y = p.getX(), p.getY()
        p1, p2 = self.btn_area.getP1(), self.btn_area.getP2()
        return p1.getX() <= x <= p2.getX() and p1.getY() <= y <= p2.getY()

    def get_cell_from_click(self, p):
        """クリックされた座標から、盤面の何行何列目かを計算する"""
        x, y = p.getX(), p.getY()
        
        # 盤面の範囲（Y座標はヘッダー分ずれていることに注意！）
        board_top = c.HEADER_HEIGHT
        board_bottom = c.HEADER_HEIGHT + self.size * c.CELL_SIZE
        board_w = self.size * c.CELL_SIZE

        # クリック位置が盤面の中にあるかチェック
        if (board_top <= y < board_bottom) and (self.offset_x <= x < self.offset_x + board_w):
            # 座標からインデックスへの変換
            # (Y座標 - ヘッダー高さ) ÷ 1マスのサイズ = 行番号
            row = int((y - board_top) // c.CELL_SIZE)
            col = int((x - self.offset_x) // c.CELL_SIZE)
            return row, col
        return None

    def close(self):
        self.win.close()
    
    def wait_click(self):
        self.win.getMouse()

# --- スタート画面（メニュー） ---
def show_start_screen():
    """難易度選択画面を表示して、選択された設定を返す"""
    win = GraphWin("Minesweeper Menu", 400, 400)
    win.setBackground("lightblue")
    
    Text(Point(200, 80), "Minesweeper").draw(win).setSize(24)
    Text(Point(200, 120), "Select your difficulty").draw(win)
    
    # ボタンの定義リスト
    buttons = [
        {"rect": [100, 160, 300, 200], "text": "Beginner (9x9, 10 mines)", "val": (9, 10), "col": "lightgreen"},
        {"rect": [100, 220, 300, 260], "text": "Advanced (16x16, 40 mines)", "val": (16, 40), "col": "yellow"},
        {"rect": [100, 280, 300, 320], "text": "Expert (20x20, 70 mines)", "val": (20, 70), "col": "orange"}
    ]
    
    # ボタンを描画
    for b in buttons:
        r = Rectangle(Point(b["rect"][0], b["rect"][1]), Point(b["rect"][2], b["rect"][3]))
        r.setFill(b["col"])
        r.draw(win)
        Text(Point(200, (b["rect"][1]+b["rect"][3])/2), b["text"]).draw(win)

    choice = None
    # 選択されるまでループ
    while choice is None:
        try:
            p = win.getMouse()
            x, y = p.getX(), p.getY()
            for b in buttons:
                if b["rect"][0] <= x <= b["rect"][2] and b["rect"][1] <= y <= b["rect"][3]:
                    choice = b["val"]
        except GraphicsError:
            return None
    win.close()
    return choice