import os
import random
import tkinter as tk
from tkinter import font as tkfont
from tkinter import scrolledtext
from typing import List, Optional

from openai import OpenAI


# ------------- OpenAI setup and Gen Alpha smack talk ----------------

client = OpenAI()  # Uses OPENAI_API_KEY from environment


def build_commentary_prompt(context: str) -> str:
    """
    Creates a short one liner of Gen Alpha smack talk with controlled slang variety.
    Prevents overusing 'no cap' or repeating the same slang back to back.
    """
    return f"""
You are a playful Gen Alpha commentator for a tic tac toe game.

Requirements:
- Return ONE short one liner only.
- Tone: playful, light roast, energetic, never mean, never NSFW.
- Use Gen Alpha slang SPARINGLY and with variety.
- Avoid repeating the same slang twice in a row.
- 'no cap' can appear occasionally but NOT frequently.
- Acceptable slang pool to choose from:
  rizz, bussin', slay, gyat, sigma, sus, bet, ate, drip, sheesh,
  brain rot, mogging, fanum tax, POV, ratio'd, delulu, "it's giving"
- DO NOT overuse any single term.
- Throw in a 6 7 every now and then too

Context of gameplay:
{context}

Return only one short line, maximum 12 words.
""".strip()


def get_smack_talk(context: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "Sheesh that move wild no cap."

    try:
        system_prompt = build_commentary_prompt(context)

        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "One line only."},
            ],
            max_tokens=30,
            temperature=0.95,
        )

        return completion.choices[0].message.content.strip()
    except Exception:
        return "Lag spike but that was sus no cap."


# ------------- Game logic ----------------

Board = List[str]

WINNING_LINES = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


def create_board() -> Board:
    return [" "] * 9


def check_winner(board: Board) -> Optional[str]:
    for a, b, c in WINNING_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    if " " not in board:
        return "draw"
    return None


def available_moves(board: Board):
    return [i for i, v in enumerate(board) if v == " "]


def find_winning_move(board: Board, player: str) -> Optional[int]:
    for idx in available_moves(board):
        copy = board.copy()
        copy[idx] = player
        if check_winner(copy) == player:
            return idx
    return None


def computer_pick_move(board: Board) -> Optional[int]:
    win_spot = find_winning_move(board, "O")
    if win_spot is not None:
        return win_spot

    block_spot = find_winning_move(board, "X")
    if block_spot is not None:
        return block_spot

    if board[4] == " ":
        return 4

    corners = [i for i in [0, 2, 6, 8] if board[i] == " "]
    if corners:
        return random.choice(corners)

    sides = [i for i in [1, 3, 5, 7] if board[i] == " "]
    if sides:
        return random.choice(sides)

    return None


# ------------- Tkinter UI ----------------

class TicTacToeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gen Alpha Tic Tac Toe")

        self.board: Board = create_board()
        self.current_player = "X"
        self.game_over = False

        self.cell_font = tkfont.Font(family="Helvetica", size=36, weight="bold")
        self.status_font = tkfont.Font(family="Helvetica", size=16, weight="bold")

        # *** Commentary font now 2x size ***
        self.comment_font = tkfont.Font(family="Helvetica", size=24)

        # Main horizontal layout
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=20)

        # Board pane
        board_panel = tk.Frame(main_frame)
        board_panel.grid(row=0, column=0, sticky="n", padx=(0, 20))

        board_frame = tk.Frame(board_panel)
        board_frame.pack()

        self.buttons = []
        for r in range(3):
            for c in range(3):
                idx = r * 3 + c
                btn = tk.Button(
                    board_frame,
                    text=" ",
                    width=3,
                    height=1,
                    font=self.cell_font,
                    command=lambda i=idx: self.on_cell_click(i),
                )
                btn.grid(row=r, column=c, padx=5, pady=5)
                self.buttons.append(btn)

        self.status_label = tk.Label(
            board_panel,
            text="You are X. Tap a square to start.",
            font=self.status_font,
        )
        self.status_label.pack(pady=(10, 10))

        reset_btn = tk.Button(
            board_panel,
            text="Reset Game",
            font=self.status_font,
            command=self.reset_game,
        )
        reset_btn.pack(pady=(0, 10))

        # Commentary pane
        right_panel = tk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky="n")

        commentary_title = tk.Label(
            right_panel,
            text="Smack Talk Feed",
            font=self.status_font,
        )
        commentary_title.pack(pady=(0, 5))

        # *** Commentary box is now 2x bigger ***
        self.comment_text = scrolledtext.ScrolledText(
            right_panel,
            width=60,    # was 40
            height=28,   # was 18
            font=self.comment_font,
            wrap="word",
            state="disabled",
        )
        self.comment_text.pack()

        self.append_comment("POV: Code warming up no cap.")

    def append_comment(self, text: str):
        self.comment_text.config(state="normal")
        self.comment_text.insert("end", text + "\n\n")
        self.comment_text.see("end")
        self.comment_text.config(state="disabled")

    def reset_game(self):
        self.board = create_board()
        self.current_player = "X"
        self.game_over = False
        for btn in self.buttons:
            btn.config(text=" ", state=tk.NORMAL)
        self.status_label.config(text="New game. You are X. Lock in.")

        self.comment_text.config(state="normal")
        self.comment_text.delete("1.0", "end")
        self.comment_text.config(state="disabled")
        self.append_comment("Fresh game vibes no cap.")

    def on_cell_click(self, idx: int):
        if self.game_over:
            return
        if self.board[idx] != " ":
            self.append_comment("Bro that's taken. Brain rot moment.")
            return

        self.board[idx] = "X"
        self.buttons[idx].config(text="X")
        self.status_label.config(text="You placed X. Computer thinking...")

        self.append_comment(get_smack_talk("Human placed X."))

        winner = check_winner(self.board)
        if winner is not None:
            self.end_game(winner)
            return

        self.root.after(450, self.computer_turn)

    def computer_turn(self):
        if self.game_over:
            return

        move = computer_pick_move(self.board)
        if move is None:
            self.end_game(check_winner(self.board) or "draw")
            return

        self.board[move] = "O"
        self.buttons[move].config(text="O")
        self.status_label.config(text="Computer placed O. Your turn.")

        #self.append_comment(get_smack_talk("Computer placed O."))

        winner = check_winner(self.board)
        if winner is not None:
            self.end_game(winner)

    def end_game(self, result: str):
        self.game_over = True
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)

        if result == "draw":
            self.status_label.config(text="Draw game.")
            ctx = "Game ended in draw."
        elif result == "X":
            self.status_label.config(text="You win!")
            ctx = "Human won."
        else:
            self.status_label.config(text="Computer wins.")
            ctx = "Computer won."

        self.append_comment(get_smack_talk(ctx))


def main():
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
