# view.py
from graphics import *
import consts as c

class MinesweeperView:
    def __init__(self, size, num_mines):
        self.size = size
        self.control_height = 60
        self.window_width = max(size * c.CELL_SIZE, 250)
        self.window_height = size * c.CELL_SIZE + self.control_height
        
        self.win = GraphWin("Minesweeper", self.window_width, self.window_height)
        self.win.setBackground(c.COLOR_BG)
        
        self.rects = []
        self.flag_icons = {}
        self.text_objects = {}
        
        # モードボタン関連
        self.btn_area = None
        self.btn_label = None
        self.msg_text = None
        
        self._init_gui()

    def _init_gui(self):
        # 盤面の描画
        for r in range(self.size):
            row_rects = []
            for col in range(self.size):
                rect = Rectangle(Point(col*c.CELL_SIZE, r*c.CELL_SIZE), 
                                 Point((col+1)*c.CELL_SIZE, (r+1)*c.CELL_SIZE))
                rect.setFill(c.COLOR_UNOPENED)
                rect.setOutline("gray")
                rect.draw(self.win)
                row_rects.append(rect)
            self.rects.append(row_rects)
            
        # コントロールエリア
        y_start = self.size * c.CELL_SIZE
        bg = Rectangle(Point(0, y_start), Point(self.window_width, self.window_height))
        bg.setFill("white")
        bg.draw(self.win)
        
        # ボタン
        self.btn_area = Rectangle(Point(10, y_start+10), Point(130, y_start+50))
        self.btn_area.setFill(c.COLOR_BTN_OPEN)
        self.btn_area.setOutline("black")
        self.btn_area.draw(self.win)
        
        self.btn_label = Text(Point(70, y_start+30), "⛏️ MODE: OPEN")
        self.btn_label.setStyle("bold")
        self.btn_label.draw(self.win)
        
        # メッセージ
        self.msg_text = Text(Point(self.window_width/2 + 60, y_start+30), "")
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

    def refresh_board(self, display):
        for r in range(self.size):
            for col in range(self.size):
                val = display[r][col]
                rect = self.rects[r][col]
                key = (r, col)
                cx, cy = rect.p1.getX() + c.CELL_SIZE/2, rect.p1.getY() + c.CELL_SIZE/2

                # フラグ処理
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
        if y < self.size * c.CELL_SIZE and x < self.size * c.CELL_SIZE:
            return int(y // c.CELL_SIZE), int(x // c.CELL_SIZE) # row, col
        return None

    def close(self):
        self.win.close()
    
    def wait_click(self):
        self.win.getMouse()

# スタート画面用関数（クラスの外におく）
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