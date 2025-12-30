# main.py
import logic
import view
import consts as c

def main():
    # 1. スタート画面で難易度を選択してもらう
    settings = view.show_start_screen()
    if settings is None: return # 閉じられたら終了
    
    board_size, num_mines = settings
    
    # 2. ゲーム画面の作成 (Viewの準備)
    game_view = view.MinesweeperView(board_size, num_mines)
    
    # --- 初回クリック待機ループ ---
    # 最初の1クリック目で地雷配置を決めるため（初手ゲームオーバー防止）
    init_flag = True
    is_open_mode = True # Trueなら「開く」、Falseなら「旗」モード
    
    while init_flag:
        click_point = game_view.get_click()
        if click_point is None: break # ウィンドウが閉じられた
        
        # ボタンクリック判定（モード切替）
        if game_view.is_button_clicked(click_point):
            is_open_mode = not is_open_mode
            game_view.update_mode_button(is_open_mode)
            continue
            
        # 盤面クリック判定
        cell = game_view.get_cell_from_click(click_point)
        if cell:
            r, col = cell
            
            if is_open_mode:
                # 開くモードなら、ここを起点に盤面を初期化してループを抜ける
                board_data, display_state = logic.initialize_board(board_size, num_mines, r, col)
                init_flag = False
                continue
            
            # まだ初期化前なので旗を立てても意味ないけど、画面更新だけしておく
            game_view.refresh_board(display_state)

    
    game_over = False
    
    # 3. メインゲームループ
    while not game_over:
        click_point = game_view.get_click()
        if click_point is None: break # 閉じるボタンが押されたら終了
        
        # ボタンクリック判定（モード切替）
        if game_view.is_button_clicked(click_point):
            is_open_mode = not is_open_mode
            game_view.update_mode_button(is_open_mode)
            continue
            
        # 盤面クリック判定
        cell = game_view.get_cell_from_click(click_point)
        if cell:
            r, col = cell
            
            if is_open_mode:
                # --- 開くモード ---
                # 旗が立ってる場所はガードして開かないようにする
                if display_state[r][col] != c.FLAGGED:
                    result = logic.open_cell(board_data, display_state, r, col, board_size)
                    
                    # 地雷を踏んだ場合
                    if result == "GAME_OVER":
                        game_over = True
                        game_view.show_message("GAME OVER...", "red")
                        # 答え合わせのために全地雷を表示する
                        for rr in range(board_size):
                            for cc in range(board_size):
                                if board_data[rr][cc] == c.MINE:
                                    display_state[rr][cc] = c.MINE
            else:
                # --- 旗モード ---
                logic.toggle_flag(display_state, r, col)
            
            # 変更を画面に反映
            game_view.refresh_board(display_state)
            
            # 勝利判定
            if not game_over and logic.check_win(display_state, board_size, num_mines):
                game_over = True
                game_view.show_message("YOU WIN!", "green")

    # 4. ゲーム終了後の待機
    # ウィンドウが開いていて、勝敗がついた状態ならクリック待ちをする
    if not game_view.win.isClosed():
        if game_over:
            game_view.show_message("Click to Close", "black")
            game_view.wait_click()
        game_view.close()

if __name__ == "__main__":
    main()