# main.py
import logic
import view
import consts as c

def main():
    # 1. スタート画面
    settings = view.show_start_screen()
    if settings is None: return
    
    board_size, num_mines = settings
    
    # 2. 初期化 (LogicとViewの準備)
    game_view = view.MinesweeperView(board_size, num_mines)
    init_flag = True
    is_open_mode = True
    while  init_flag:
        click_point = game_view.get_click()
        if click_point is None: break # ウィンドウが閉じられた
        
        # ボタンクリック判定
        if game_view.is_button_clicked(click_point):
            is_open_mode = not is_open_mode
            game_view.update_mode_button(is_open_mode)
            continue
            
        # 盤面クリック判定
        cell = game_view.get_cell_from_click(click_point)
        if cell:
            r, col = cell
            
            if is_open_mode:
                # 開くモード
                board_data, display_state = logic.initialize_board(board_size, num_mines,r,col)
                init_flag = False
                continue
            
            # 画面更新
            game_view.refresh_board(display_state)

    
    game_over = False
    
    # 3. ゲームループ
    while not game_over:
        click_point = game_view.get_click()
        if click_point is None: break # ウィンドウが閉じられた
        
        # ボタンクリック判定
        if game_view.is_button_clicked(click_point):
            is_open_mode = not is_open_mode
            game_view.update_mode_button(is_open_mode)
            continue
            
        # 盤面クリック判定
        cell = game_view.get_cell_from_click(click_point)
        if cell:
            r, col = cell
            
            if is_open_mode:
                # 開くモード
                if display_state[r][col] != c.FLAGGED:
                    result = logic.open_cell(board_data, display_state, r, col, board_size)
                    if result == "GAME_OVER":
                        game_over = True
                        game_view.show_message("GAME OVER...", "red")
                        # 全地雷オープン
                        for rr in range(board_size):
                            for cc in range(board_size):
                                if board_data[rr][cc] == c.MINE:
                                    display_state[rr][cc] = c.MINE
            else:
                # フラグモード
                logic.toggle_flag(display_state, r, col)
            
            # 画面更新
            game_view.refresh_board(display_state)
            
            # 勝利判定
            if not game_over and logic.check_win(display_state, board_size, num_mines):
                game_over = True
                game_view.show_message("YOU WIN!", "green")

    # 終了待機
    if not game_view.win.isClosed():
        if game_over:
            game_view.show_message("Click to Close", "black")
            game_view.wait_click()
        game_view.close()

if __name__ == "__main__":
    main()