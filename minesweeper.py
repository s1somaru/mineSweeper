import random
import time
from graphics import *

# --- 設定 ---
BOARD_SIZE = 9
NUM_MINES = 10
CELL_SIZE = 30 
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE
# --- 状態定数 ---
MINE = -1
UNOPENED = -2
FLAGGED = -3  # ★ NEW: フラグ状態を追加
# --- 色定義 ---
COLOR_UNOPENED = "lightgray"
COLOR_MINE = "red"
COLOR_OPENED = "white"
COLOR_TEXT = "blue"
COLOR_FLAG = "orange" # ★ NEW: フラグの色

# --- グローバル変数 (GUI管理用) ---
win = None
rects = []
board_data = None
display_state = None
flag_icons = {} # ★ NEW: フラグのアイコン (Textオブジェクト) を保持する辞書

# --- ロジックコア (再掲/修正なし) --------------------------------------------

def initialize_board():
    """ 盤面を初期化し、地雷を配置して周囲の数字を計算する """
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    display = [[UNOPENED] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    
    mines_placed = 0
    while mines_placed < NUM_MINES:
        row, col = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)
        if board[row][col] != MINE:
            board[row][col] = MINE
            mines_placed += 1
            
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == MINE:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < BOARD_SIZE) and (0 <= nc < BOARD_SIZE) and (board[nr][nc] == MINE):
                        count += 1
            board[r][c] = count
            
    return board, display

def open_cell(board, display, r, c):
    """ 指定されたマスを開く (再帰処理あり) """
    
    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
        return
    # ★ 修正: 未開またはフラグが立っているマスは開かない
    if display[r][c] != UNOPENED:
        return
    
    if board[r][c] == MINE:
        display[r][c] = MINE
        return "GAME_OVER"
    
    display[r][c] = board[r][c]
    
    if board[r][c] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                open_cell(board, display, r + dr, c + dc)

def check_win(display):
    """ 勝利条件をチェックする """
    unopened_count = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if display[r][c] == UNOPENED or display[r][c] == FLAGGED:
                unopened_count += 1
    
    return unopened_count == NUM_MINES

# --- フラグ操作ロジック ------------------------------------------------------

def toggle_flag(display, r, c):
    """ マスのフラグ状態を切り替える (右クリック対応) """
    if display[r][c] == UNOPENED:
        display[r][c] = FLAGGED
    elif display[r][c] == FLAGGED:
        display[r][c] = UNOPENED

# --- GUI 描画/更新関数 (要修正) ----------------------------------------------

def draw_grid(win, board):
    """ 盤面のグリッドと初期状態を描画する (修正なし) """
    global rects
    rects = []
    
    for r in range(BOARD_SIZE):
        row_rects = []
        for c in range(BOARD_SIZE):
            x1, y1 = c * CELL_SIZE, r * CELL_SIZE
            x2, y2 = (c + 1) * CELL_SIZE, (r + 1) * CELL_SIZE

            rect = Rectangle(Point(x1, y1), Point(x2, y2))
            rect.setFill(COLOR_UNOPENED)
            rect.setOutline("gray")
            rect.draw(win)
            row_rects.append(rect)
        rects.append(row_rects)
    
    # メッセージエリア（盤面の下）
    msg_area = Rectangle(Point(0, WINDOW_SIZE), Point(WINDOW_SIZE, WINDOW_SIZE + 30))
    msg_area.setFill("white")
    msg_area.draw(win)
    
    message = Text(Point(WINDOW_SIZE / 2, WINDOW_SIZE + 15), "左クリックで開く。右クリックでフラグ。")
    message.setSize(12)
    message.draw(win)
    return message

def update_gui(win, board, display, message_obj):
    """ 盤面（display）の状態に応じてGUIを更新する (フラグ対応) """
    global flag_icons
    
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            cell_val = display[r][c]
            rect = rects[r][c]
            key = (r, c)
            
            # 既存のフラグアイコンをクリア
            if key in flag_icons:
                flag_icons[key].undraw()
                del flag_icons[key]

            if cell_val == FLAGGED:
                # ★ フラグが立っている場合
                center_x = rect.p1.getX() + CELL_SIZE/2
                center_y = rect.p1.getY() + CELL_SIZE/2
                flag_text = Text(Point(center_x, center_y), "F") # Fでフラグを表現
                flag_text.setFill(COLOR_FLAG)
                flag_text.setSize(14)
                flag_text.draw(win)
                flag_icons[key] = flag_text
                
            elif cell_val != UNOPENED:
                # マスが開いている場合
                rect.setFill(COLOR_OPENED)
                center_x = rect.p1.getX() + CELL_SIZE/2
                center_y = rect.p1.getY() + CELL_SIZE/2
                
                if cell_val == MINE:
                    # 地雷の場合
                    rect.setFill(COLOR_MINE)
                    
                elif cell_val > 0:
                    # 数字の場合
                    text_obj = Text(Point(center_x, center_y), str(cell_val))
                    text_obj.setFill(COLOR_TEXT)
                    text_obj.setSize(12)
                    text_obj.draw(win)
                # cell_val == 0 の場合、背景色のみ変更

# --- メイン関数 (マウスクリックイベント処理を修正) -----------------------------

def main_gui():
    global win, board_data, display_state
    
    # 1. ウィンドウの初期化
    win = GraphWin("マインスイーパ", WINDOW_SIZE, WINDOW_SIZE + 30)
    win.setBackground("gray")
    
    # 2. 盤面の初期化と描画
    board_data, display_state = initialize_board()
    message_obj = draw_grid(win, board_data)
    
    game_over = False
    
    # 3. イベントループ
    while not game_over and win.isClosed() == False:
        try:
            # ★ 修正: getMouse() の代わりに checkMouse() を使用
            click_point = win.checkMouse()

            if click_point:
                # マス目をクリックしているか判定
                if click_point.getY() >= WINDOW_SIZE:
                    continue
                
                # クリック座標からマス目 (行 r, 列 c) を計算
                c = int(click_point.getX() // CELL_SIZE)
                r = int(click_point.getY() // CELL_SIZE)
                
                # ★ クリックボタンの判定と処理 ★
                # graphics.pyでは、getMouse()が返すPointオブジェクトに
                # 'button'という属性でクリックされたボタン番号（1:左, 3:右）が格納される
                button_pressed = getattr(click_point, 'button', 1)
                
                if button_pressed == 1: # 左クリック (開く)
                    if display_state[r][c] != FLAGGED:
                        result = open_cell(board_data, display_state, r, c)
                        if result == "GAME_OVER":
                            game_over = True
                
                elif button_pressed == 3: # 右クリック (フラグの設置/解除)
                    if display_state[r][c] == UNOPENED or display_state[r][c] == FLAGGED:
                         toggle_flag(display_state, r, c)

                # GUIを更新
                update_gui(win, board_data, display_state, message_obj)

                # 勝利判定
                if check_win(display_state):
                    message_obj.setText("🎉 勝利! おめでとう!")
                    message_obj.setFill("green")
                    game_over = True
            
        except GraphicsError:
            game_over = True
        except Exception as e:
            # 開発中はエラーを表示すると便利
            print(f"予期せぬエラー: {e}")
            game_over = True
            
    # 4. ゲーム終了後の待機
    if win and win.isClosed() == False:
        # ゲームオーバー時に全ての地雷を公開
        if board_data and game_over:
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if board_data[r][c] == MINE and display_state[r][c] != MINE:
                        display_state[r][c] = MINE
        
        update_gui(win, board_data, display_state, message_obj)
        
        message_obj.setText("ゲーム終了。クリックでウィンドウを閉じます。")
        win.getMouse()
        win.close()
    
# --- 実行部分 ---
if __name__ == "__main__":
    main_gui()