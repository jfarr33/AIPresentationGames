"""Prompt: make tic tac toe game with a UI in python.  I want a version where I only play against the computer. """


import tkinter as tk
from tkinter import messagebox
import copy

# --- Game state ---
HUMAN = "X"
AI = "O"

current_player = HUMAN
board = [["" for _ in range(3)] for _ in range(3)]
buttons = []  # will hold button widgets


# --- Game logic ---

def check_winner(b):
    """Return 'X', 'O', 'Draw', or None."""
    # Rows
    for row in range(3):
        if b[row][0] == b[row][1] == b[row][2] != "":
            return b[row][0]

    # Columns
    for col in range(3):
        if b[0][col] == b[1][col] == b[2][col] != "":
            return b[0][col]

    # Diagonals
    if b[0][0] == b[1][1] == b[2][2] != "":
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != "":
        return b[0][2]

    # Draw?
    for row in b:
        for cell in row:
            if cell == "":
                return None  # not over yet

    return "Draw"


def minimax(b, is_maximizing):
    """
    Minimax algorithm:
    - AI (O) is maximizing player
    - Human (X) is minimizing player
    Returns (score, move) where move is (row, col)
    """
    winner = check_winner(b)
    if winner == AI:
        return 1, None
    elif winner == HUMAN:
        return -1, None
    elif winner == "Draw":
        return 0, None

    if is_maximizing:
        best_score = -999
        best_move = None
        for r in range(3):
            for c in range(3):
                if b[r][c] == "":
                    b[r][c] = AI
                    score, _ = minimax(b, False)
                    b[r][c] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        return best_score, best_move
    else:
        best_score = 999
        best_move = None
        for r in range(3):
            for c in range(3):
                if b[r][c] == "":
                    b[r][c] = HUMAN
                    score, _ = minimax(b, True)
                    b[r][c] = ""
                    if score < best_score:
                        best_score = score
                        best_move = (r, c)
        return best_score, best_move


def ai_move():
    global board, current_player

    if check_winner(board) is not None:
        return  # game already over

    # Copy board for minimax (not strictly necessary but safer)
    board_copy = copy.deepcopy(board)
    _, move = minimax(board_copy, True)
    if move is None:
        return
    r, c = move

    board[r][c] = AI
    buttons[r][c]["text"] = AI
    buttons[r][c]["state"] = "disabled"

    winner = check_winner(board)
    if winner:
        end_game(winner)
        return

    current_player = HUMAN
    status_label.config(text="Your turn (X)")


def end_game(winner):
    if winner == "Draw":
        status_label.config(text="It's a draw!")
        messagebox.showinfo("Game Over", "It's a draw!")
    else:
        if winner == HUMAN:
            status_label.config(text="You win!")
            messagebox.showinfo("Game Over", "You win! 🎉")
        else:
            status_label.config(text="Computer wins!")
            messagebox.showinfo("Game Over", "Computer wins 🤖")
    disable_all_buttons()


def on_button_click(row, col):
    global current_player, board

    # Ignore clicks if not human's turn or cell already taken
    if current_player != HUMAN:
        return
    if board[row][col] != "":
        return

    # Human move
    board[row][col] = HUMAN
    buttons[row][col]["text"] = HUMAN
    buttons[row][col]["state"] = "disabled"

    winner = check_winner(board)
    if winner:
        end_game(winner)
        return

    # Switch to AI
    current_player = AI
    status_label.config(text="Computer thinking...")

    # Let the UI update, then call ai_move
    root.after(300, ai_move)  # 300ms delay just for a nicer feel


def disable_all_buttons():
    for row in buttons:
        for btn in row:
            btn.config(state="disabled")


def reset_game():
    global current_player, board
    current_player = HUMAN
    board = [["" for _ in range(3)] for _ in range(3)]
    for row in buttons:
        for btn in row:
            btn.config(text="", state="normal")
    status_label.config(text="Your turn (X)")


# --- UI setup ---
root = tk.Tk()
root.title("Tic Tac Toe vs Computer")

status_label = tk.Label(root, text="Your turn (X)", font=("Arial", 16))
status_label.grid(row=0, column=0, columnspan=3, pady=(10, 10))

# Create 3x3 grid of buttons
for r in range(3):
    row_buttons = []
    for c in range(3):
        btn = tk.Button(
            root,
            text="",
            font=("Arial", 32),
            width=3,
            height=1,
            command=lambda r=r, c=c: on_button_click(r, c),
        )
        btn.grid(row=r + 1, column=c, padx=5, pady=5)
        row_buttons.append(btn)
    buttons.append(row_buttons)

reset_button = tk.Button(root, text="Reset", font=("Arial", 14), command=reset_game)
reset_button.grid(row=4, column=0, columnspan=3, pady=(10, 10))

root.mainloop()
