# logic.py
import random
import consts as c

def initialize_board(size, num_mines, y, x):
    """
    盤面の初期化を行う関数。
    最初のクリック位置(y, x)を受け取って、その周囲には地雷を置かないようにするよ（初手安全策）。
    """
    # 盤面データ（地雷や数字）を格納する2次元リスト
    board = [[0] * size for _ in range(size)]
    # プレイヤーに見せる状態（開いた、閉じた、旗）を管理するリスト
    display = [[c.UNOPENED] * size for _ in range(size)]
    
    mines_placed = 0
    
    # 最初のクリック位置と、その周囲8マスの座標リストを作る
    directions = [
        (x-1,y-1),(x,y-1),(x+1,y-1),
        (x-1,y),(x,y),(x+1,y),
        (x-1,y+1),(x,y+1),(x+1,y+1)
    ]
    # 安全地帯として一時的にフラグ扱いにしておく（後で戻すわけじゃないけど、地雷配置スキップ用）
    for dx, dy in directions:
        if not (0 <= dx < size and 0 <= dy < size):
            continue
        board[dy][dx] = c.FLAGGED
    
    # 地雷をランダムに配置
    while mines_placed < num_mines:
        r, c_idx = random.randint(0, size - 1), random.randint(0, size - 1)
        # すでに地雷がある場所や、さっき確保した安全地帯には置かない
        if board[r][c_idx] != c.MINE and board[r][c_idx] != c.FLAGGED:
            board[r][c_idx] = c.MINE
            mines_placed += 1

    # 各マスの数字（周囲の地雷数）を計算
    for r in range(size):
        for col in range(size):
            # 地雷マスは計算不要
            if board[r][col] == c.MINE:
                continue
            
            # 周囲8マスをチェックして地雷を数える
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, col + dc
                    if (0 <= nr < size) and (0 <= nc < size) and (board[nr][nc] == c.MINE):
                        count += 1
            board[r][col] = count # 計算した数字をセット
            
    # 安全地帯用のマーク(FLAGGED)が入ってしまっている場合は、数字や空(0)に戻す処理が必要だけど、
    # この実装だと数字計算で上書きされるから大丈夫！
    
    return board, display

def open_cell(board, display, r, col, size):
    """マスを開く処理。0（空白）なら周囲も連鎖して開く（再帰処理）"""
    # 盤面外なら何もしない
    if not (0 <= r < size and 0 <= col < size): return
    # すでに開いてるマスなら何もしない
    if display[r][col] != c.UNOPENED: return
    
    # 地雷を踏んだらゲームオーバーの合図を返す
    if board[r][col] == c.MINE:
        display[r][col] = c.MINE
        return "GAME_OVER"
    
    # 盤面の情報を表示用にコピー（これでマスが開いたことになる）
    display[r][col] = board[r][col]
    
    # もし開いた場所が「0（周囲に地雷なし）」なら、隣も自動で開く
    if board[r][col] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                open_cell(board, display, r + dr, col + dc, size)

def toggle_flag(display, r, c_idx):
    """旗を立てたり消したりする切り替え処理"""
    if display[r][c_idx] == c.UNOPENED:
        display[r][c_idx] = c.FLAGGED
    elif display[r][c_idx] == c.FLAGGED:
        display[r][c_idx] = c.UNOPENED

def check_win(display, size, num_mines):
    """勝利判定：開いてないマス＋旗のマスの数が、地雷の数とぴったり同じなら勝ち！"""
    unopened_or_flagged = 0
    for r in range(size):
        for col in range(size):
            if display[r][col] == c.UNOPENED or display[r][col] == c.FLAGGED:
                unopened_or_flagged += 1
    return unopened_or_flagged == num_mines