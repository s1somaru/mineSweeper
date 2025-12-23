import random
import time
from graphics import *

# --- 設定 ---
CELL_SIZE = 30 
# --- 状態定数 ---
MINE = -1
UNOPENED = -2
FLAGGED = -3 
# --- 色定義 ---
COLOR_UNOPENED = "lightgray"
COLOR_MINE = "red"
COLOR_OPENED = "white"
COLOR_TEXT = "blue"
COLOR_FLAG = "orange"
COLOR_BTN_OPEN = "lightblue"
COLOR_BTN_FLAG = "orange"

# --- グローバル変数 ---
win = None
rects = []
flag_icons = {}
text_objects = {}

# ==========================================
#  ロジックコア (変更なし)
# ==========================================

def initialize_board(size, num_mines):
    board = [[0] * size for _ in range(size)]
    display = [[UNOPENED] * size for _ in range(size)]
    
    mines_placed = 0
    while mines_placed < num_mines:
        r, c = random.randint(0, size - 1), random.randint(0, size - 1)
        if board[r][c] != MINE:
            board[r][c] = MINE
            mines_placed += 1
            
    for r in range(size):
        for c in range(size):
            if board[r][c] == MINE:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < size) and (0 <= nc < size) and (board[nr][nc] == MINE):
                        count += 1
            board[r][c] = count
    return board, display

def open_cell(board, display, r, c, size):
    if not (0 <= r < size and 0 <= c < size): return
    if display[r][c] != UNOPENED: return
    if board[r][c] == MINE:
        display[r][c] = MINE
        return "GAME_OVER"
    display[r][c] = board[r][c]
    if board[r][c] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                open_cell(board, display, r + dr, c + dc, size)

def toggle_flag(display, r, c):
    if display[r][c] == UNOPENED:
        display[r][c] = FLAGGED
    elif display[r][c] == FLAGGED:
        display[r][c] = UNOPENED

def check_win(display, size, num_mines):
    unopened_or_flagged = 0
    for r in range(size):
        for c in range(size):
            if display[r][c] == UNOPENED or display[r][c] == FLAGGED:
                unopened_or_flagged += 1
    return unopened_or_flagged == num_mines

# ==========================================
#  GUI: スタート画面 & 共通パーツ
# ==========================================

def draw_button_obj(win, x1, y1, x2, y2, text, color):
    """ ボタンを描画してRectとTextオブジェクトを返す """
    rect = Rectangle(Point(x1, y1), Point(x2, y2))
    rect.setFill(color)
    rect.setOutline("black")
    rect.draw(win)
    label = Text(Point((x1+x2)/2, (y1+y2)/2), text)
    label.setStyle("bold")
    label.draw(win)
    return rect, label

def show_start_screen():
    menu_win = GraphWin("Minesweeper Menu", 400, 400)
    menu_win.setBackground("lightblue")
    
    Text(Point(200, 80), "Minesweeper").draw(menu_win).setSize(24)
    Text(Point(200, 120), "難易度を選んでください").draw(menu_win)
    
    # ボタン描画 (戻り値は使わず座標のみ管理)
    draw_button_obj(menu_win, 100, 160, 300, 200, "初級 (9x9, 10個)", "lightgreen")
    draw_button_obj(menu_win, 100, 220, 300, 260, "中級 (16x16, 40個)", "yellow")
    draw_button_obj(menu_win, 100, 280, 300, 320, "上級 (20x20, 70個)", "orange")
    
    choice = None
    while choice is None:
        try:
            p = menu_win.getMouse()
            x, y = p.getX(), p.getY()
            if 100 <= x <= 300:
                if 160 <= y <= 200: choice = (9, 10)
                elif 220 <= y <= 260: choice = (16, 40)
                elif 280 <= y <= 320: choice = (20, 70)
        except GraphicsError:
            return None
    menu_win.close()
    return choice

# ==========================================
#  GUI: ゲーム画面更新
# ==========================================

def draw_game_board(win, size):
    global rects
    rects = []
    for r in range(size):
        row_rects = []
        for c in range(size):
            rect = Rectangle(Point(c*CELL_SIZE, r*CELL_SIZE), Point((c+1)*CELL_SIZE, (r+1)*CELL_SIZE))
            rect.setFill(COLOR_UNOPENED)
            rect.setOutline("gray")
            rect.draw(win)
            row_rects.append(rect)
        rects.append(row_rects)

def update_cell_visual(win, r, c, val):
    global flag_icons, text_objects
    rect = rects[r][c]
    key = (r, c)
    cx, cy = rect.p1.getX() + CELL_SIZE/2, rect.p1.getY() + CELL_SIZE/2

    if val == FLAGGED:
        if key not in flag_icons:
            ft = Text(Point(cx, cy), "F")
            ft.setFill(COLOR_FLAG)
            ft.setStyle("bold")
            ft.draw(win)
            flag_icons[key] = ft
        return

    if key in flag_icons:
        flag_icons[key].undraw()
        del flag_icons[key]
        
    if val != UNOPENED:
        rect.setFill(COLOR_OPENED)
        if val == MINE:
            rect.setFill(COLOR_MINE)
        elif val > 0:
            if key not in text_objects:
                t = Text(Point(cx, cy), str(val))
                t.setFill(COLOR_TEXT)
                t.draw(win)
                text_objects[key] = t

def full_gui_refresh(win, display, size):
    for r in range(size):
        for c in range(size):
            update_cell_visual(win, r, c, display[r][c])

# ==========================================
#  メイン処理 (モード切替実装)
# ==========================================

def main():
    global win, rects, flag_icons, text_objects
    
    settings = show_start_screen()
    if settings is None: return
    
    board_size, num_mines = settings
    # ウィンドウ下の操作エリアの高さを確保
    control_height = 60
    window_width = board_size * CELL_SIZE
    # ウィンドウ幅が小さすぎるとボタンが入らないので最低幅を設定
    if window_width < 250: window_width = 250
    
    window_height = board_size * CELL_SIZE + control_height
    
    win = GraphWin("Minesweeper", window_width, window_height)
    win.setBackground("gray")
    
    # 盤面初期化
    board_data, display_state = initialize_board(board_size, num_mines)
    draw_game_board(win, board_size)
    
    # --- コントロールエリア (モード切替ボタン) ---
    control_y_start = board_size * CELL_SIZE
    
    # 背景
    ctrl_bg = Rectangle(Point(0, control_y_start), Point(window_width, window_height))
    ctrl_bg.setFill("white")
    ctrl_bg.draw(win)
    
    # モード切替ボタン
    btn_x1, btn_y1 = 10, control_y_start + 10
    btn_x2, btn_y2 = 130, control_y_start + 50
    mode_btn_rect, mode_btn_label = draw_button_obj(win, btn_x1, btn_y1, btn_x2, btn_y2, "⛏️ MODE: OPEN", COLOR_BTN_OPEN)
    
    # メッセージ表示部
    msg_text = Text(Point(window_width/2 + 60, control_y_start + 30), "")
    msg_text.setSize(10)
    msg_text.draw(win)

    # 現在のモード (True=Open, False=Flag)
    is_open_mode = True 
    game_over = False
    
    while not game_over and not win.isClosed():
        try:
            click = win.getMouse() # 通常のgetMouseを使用
            cx, cy = click.getX(), click.getY()
            
            # --- ボタンクリック判定 ---
            if btn_x1 <= cx <= btn_x2 and btn_y1 <= cy <= btn_y2:
                # モード切替
                is_open_mode = not is_open_mode
                if is_open_mode:
                    mode_btn_rect.setFill(COLOR_BTN_OPEN)
                    mode_btn_label.setText("⛏️ MODE: OPEN")
                else:
                    mode_btn_rect.setFill(COLOR_BTN_FLAG)
                    mode_btn_label.setText("🚩 MODE: FLAG")
                continue # 盤面処理へは行かない
            
            # --- 盤面クリック判定 ---
            if cy < board_size * CELL_SIZE and cx < board_size * CELL_SIZE:
                c = int(cx // CELL_SIZE)
                r = int(cy // CELL_SIZE)
                
                if is_open_mode:
                    # 開くモード
                    if display_state[r][c] != FLAGGED:
                        res = open_cell(board_data, display_state, r, c, board_size)
                        if res == "GAME_OVER":
                            game_over = True
                            msg_text.setText("GAME OVER...")
                            msg_text.setTextColor("red")
                            # 全地雷表示
                            for rr in range(board_size):
                                for cc in range(board_size):
                                    if board_data[rr][cc] == MINE:
                                        display_state[rr][cc] = MINE
                else:
                    # フラグモード
                    toggle_flag(display_state, r, c)
                
                full_gui_refresh(win, display_state, board_size)
                
                if not game_over and check_win(display_state, board_size, num_mines):
                    game_over = True
                    msg_text.setText("YOU WIN!")
                    msg_text.setTextColor("green")
                    
        except GraphicsError:
            break
            
    if not win.isClosed():
        msg_text.setText("Click to Close")
        win.getMouse()
        win.close()

if __name__ == "__main__":
    main()