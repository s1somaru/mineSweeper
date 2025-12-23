# view.py
from graphics import *
import consts as c

class MinesweeperView:
    def __init__(self, size, num_mines):
        self.size = size
        self.num_mines = num_mines
        self.control_height = 60
        
        # ウィンドウ幅計算
        board_pixel_width = size * c.CELL_SIZE
        self.window_width = max(board_pixel_width, 350) # 最低幅350
        self.window_height = size * c.CELL_SIZE + self.control_height
        
        # ★追加: 中央寄せのためのオフセット(左側の余白)を計算
        # (ウィンドウ幅 - 盤面幅) ÷ 2
        self.offset_x = (self.window_width - board_pixel_width) / 2
        
        self.win = GraphWin("Minesweeper", self.window_width, self.window_height)
        self.win.setBackground(c.COLOR_BG)
        
        self.rects = []
        self.flag_icons = {}
        self.text_objects = {}
        
        self.btn_area = None
        self.btn_label = None
        self.msg_text = None
        self.remain_bg = None
        self.remain_text = None
        
        self._init_gui()
        self.display_remaining_mines([], self.num_mines)

    def _init_gui(self):
        # 盤面の描画
        for r in range(self.size):
            row_rects = []
            for col in range(self.size):
                # ★修正: X座標に self.offset_x を足して描画位置をずらす
                x1 = self.offset_x + col * c.CELL_SIZE
                y1 = r * c.CELL_SIZE
                x2 = self.offset_x + (col + 1) * c.CELL_SIZE
                y2 = (r + 1) * c.CELL_SIZE
                
                rect = Rectangle(Point(x1, y1), Point(x2, y2))
                rect.setFill(c.COLOR_UNOPENED)
                rect.setOutline("gray")
                rect.draw(self.win)
                row_rects.append(rect)
            self.rects.append(row_rects)
            
        # コントロールエリア背景
        y_start = self.size * c.CELL_SIZE
        bg = Rectangle(Point(0, y_start), Point(self.window_width, self.window_height))
        bg.setFill("white")
        bg.draw(self.win)
        
        # モード切替ボタン
        self.btn_area = Rectangle(Point(5, y_start+10), Point(140, y_start+50))
        self.btn_area.setFill(c.COLOR_BTN_OPEN)
        self.btn_area.setOutline("black")
        self.btn_area.draw(self.win)
        
        self.btn_label = Text(Point(72.5, y_start+30), "⛏️ MODE: OPEN")
        self.btn_label.setStyle("bold")
        self.btn_label.draw(self.win)
        
        # メッセージエリア
        space_center_x = (140 + (self.window_width - 110)) / 2
        self.msg_text = Text(Point(space_center_x, y_start+30), "")
        self.msg_text.setSize(10)
        self.msg_text.draw(self.win)

    def update_mode_button(self, is_open_mode):
        if is_open_mode:
            self.btn_area.setFill(c.COLOR_BTN_OPEN)
            self.btn_label.setText("⛏️ MODE: OPEN")
        else:
            self.btn_area.setFill(c.COLOR_BTN_FLAG)
            self.btn_label.setText("🚩 MODE: FLAG")

    def show_message(self, text, color="black"):
        self.msg_text.setText(text)
        self.msg_text.setTextColor(color)

    def display_remaining_mines(self, display, num_mines):
        if not display:
            remain = num_mines
        else:
            remain = self._remainMines(display, num_mines)
        
        text_str = f"Mines: {remain}"
        y_start = self.size * c.CELL_SIZE
        
        bg_p1 = Point(self.window_width - 110, y_start + 15)
        bg_p2 = Point(self.window_width - 10, y_start + 45)
        text_center = Point(self.window_width - 60, y_start + 30)

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
        flagged_count = sum(row.count(c.FLAGGED) for row in display)
        return num_mines - flagged_count

    def refresh_board(self, display):
        for r in range(self.size):
            for col in range(self.size):
                val = display[r][col]
                rect = self.rects[r][col]
                key = (r, col)
                cx, cy = rect.p1.getX() + c.CELL_SIZE/2, rect.p1.getY() + c.CELL_SIZE/2

                if val == c.FLAGGED:
                    if key not in self.flag_icons:
                        ft = Text(Point(cx, cy), "F")
                        ft.setFill(c.COLOR_FLAG)
                        ft.setStyle("bold")
                        ft.draw(self.win)
                        self.flag_icons[key] = ft
                    continue

                if key in self.flag_icons:
                    self.flag_icons[key].undraw()
                    del self.flag_icons[key]
                
                if val != c.UNOPENED:
                    rect.setFill(c.COLOR_OPENED)
                    if val == c.MINE:
                        rect.setFill(c.COLOR_MINE)
                    elif val > 0:
                        if key not in self.text_objects:
                            t = Text(Point(cx, cy), str(val))
                            t.setFill(c.COLOR_TEXT)
                            t.draw(self.win)
                            self.text_objects[key] = t
        
        self.display_remaining_mines(display, self.num_mines)

    def get_click(self):
        try:
            return self.win.getMouse()
        except GraphicsError:
            return None

    def is_button_clicked(self, p):
        x, y = p.getX(), p.getY()
        p1, p2 = self.btn_area.getP1(), self.btn_area.getP2()
        return p1.getX() <= x <= p2.getX() and p1.getY() <= y <= p2.getY()

    def get_cell_from_click(self, p):
        x, y = p.getX(), p.getY()
        
        # ★修正: 盤面の範囲内かチェック (X座標は offset_x を考慮)
        board_w = self.size * c.CELL_SIZE
        if (0 <= y < board_w) and (self.offset_x <= x < self.offset_x + board_w):
            # ずらした分(offset_x)を引いてから計算する
            return int(y // c.CELL_SIZE), int((x - self.offset_x) // c.CELL_SIZE)
        return None

    def close(self):
        self.win.close()
    
    def wait_click(self):
        self.win.getMouse()

# スタート画面 (変更なし)
def show_start_screen():
    win = GraphWin("Minesweeper Menu", 400, 400)
    win.setBackground("lightblue")
    
    Text(Point(200, 80), "Minesweeper").draw(win).setSize(24)
    Text(Point(200, 120), "難易度を選んでください").draw(win)
    
    buttons = [
        {"rect": [100, 160, 300, 200], "text": "初級 (9x9, 10個)", "val": (9, 10), "col": "lightgreen"},
        {"rect": [100, 220, 300, 260], "text": "中級 (16x16, 40個)", "val": (16, 40), "col": "yellow"},
        {"rect": [100, 280, 300, 320], "text": "上級 (20x20, 70個)", "val": (20, 70), "col": "orange"}
    ]
    
    for b in buttons:
        r = Rectangle(Point(b["rect"][0], b["rect"][1]), Point(b["rect"][2], b["rect"][3]))
        r.setFill(b["col"])
        r.draw(win)
        Text(Point(200, (b["rect"][1]+b["rect"][3])/2), b["text"]).draw(win)

    choice = None
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