"""Prompt: make tic tac toe game with a UI in python """

import tkinter as tk
from tkinter import messagebox

# --- Game logic ---
current_player = "X"
board = [["" for _ in range(3)] for _ in range(3)]
buttons = []  # will hold button widgets


def check_winner():
    # Rows
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] != "":
            return board[row][0]
    # Columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != "":
            return board[0][col]
    # Diagonals
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]

    # Check draw (no empty cells)
    for row in board:
        for cell in row:
            if cell == "":
                return None  # game not over yet
    return "Draw"


def on_button_click(row, col):
    global current_player

    # If cell already taken or game over, ignore
    if board[row][col] != "":
        return

    board[row][col] = current_player
    buttons[row][col]["text"] = current_player

    winner = check_winner()
    if winner:
        if winner == "Draw":
            status_label.config(text="It's a draw!")
            messagebox.showinfo("Game Over", "It's a draw!")
        else:
            status_label.config(text=f"Player {winner} wins!")
            messagebox.showinfo("Game Over", f"Player {winner} wins!")
        disable_all_buttons()
        return

    # Switch player
    current_player = "O" if current_player == "X" else "X"
    status_label.config(text=f"Player {current_player}'s turn")


def disable_all_buttons():
    for row in buttons:
        for btn in row:
            btn.config(state="disabled")


def enable_all_buttons():
    for row in buttons:
        for btn in row:
            btn.config(state="normal")


def reset_game():
    global current_player, board
    current_player = "X"
    board = [["" for _ in range(3)] for _ in range(3)]
    for row in buttons:
        for btn in row:
            btn.config(text="", state="normal")
    status_label.config(text="Player X's turn")


# --- UI setup ---
root = tk.Tk()
root.title("Tic Tac Toe")

status_label = tk.Label(root, text="Player X's turn", font=("Arial", 16))
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
