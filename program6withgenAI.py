import tkinter as tk
from tkinter import messagebox
import os
import random
import json

from openai import OpenAI

# Create OpenAI client (uses OPENAI_API_KEY from environment)
client = OpenAI()

HUMAN = "X"
AI = "O"

current_player = HUMAN
board = [["" for _ in range(3)] for _ in range(3)]
buttons = []


def board_to_text(b):
    """
    Represent the board as text for the model.
    Empty cells become '.' so they are easy to see.
    """
    lines = []
    for row in b:
        lines.append(" ".join(cell if cell != "" else "." for cell in row))
    return "\n".join(lines)


def check_winner(b):
    """Return 'X', 'O', 'Draw', or None."""
    # Rows
    for r in range(3):
        if b[r][0] == b[r][1] == b[r][2] != "":
            return b[r][0]
    # Columns
    for c in range(3):
        if b[0][c] == b[1][c] == b[2][c] != "":
            return b[0][c]
    # Diagonals
    if b[0][0] == b[1][1] == b[2][2] != "":
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != "":
        return b[0][2]
    # Draw?
    for row in b:
        for cell in row:
            if cell == "":
                return None
    return "Draw"


def random_valid_move():
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    return random.choice(empty_cells) if empty_cells else None


def get_ai_move_from_chatgpt():
    """
    Call the OpenAI Responses API to get the AI move and commentary.

    We ask for JSON of the form:
      {
        "move": [row, col],
        "commentary": "some text"
      }
    """
    board_str = board_to_text(board)

    prompt = f"""
You are playing tic tac toe as O against a human who is X.

Board format:
- 3 rows, 3 columns
- Each row is shown on its own line
- Cells contain X, O, or . (for empty)
- Rows and columns are indexed 0, 1, 2.

Current board:
{board_str}

Rules:
- It is your turn as O.
- Choose exactly one empty cell (marked with .).
- You must always choose a valid move.

Respond ONLY with a single JSON object in this format:
{{
  "move": [row, col],
  "commentary": "Explain in 1 to 3 sentences why you chose this move."
}}
"""

    try:
        response = client.responses.create(
            model="gpt-5.1",
            instructions=(
                "You are a tic tac toe AI. "
                "Always reply with a valid JSON object containing 'move' and 'commentary'."
            ),
            input=prompt,
        )
        ai_text = response.output_text.strip()

        # Try to parse JSON
        data = json.loads(ai_text)

        # Extract move
        move = None
        commentary = ""

        if isinstance(data, dict) and "move" in data:
            mv = data["move"]
            if (
                isinstance(mv, list)
                and len(mv) == 2
                and isinstance(mv[0], int)
                and isinstance(mv[1], int)
            ):
                r, c = mv
                if 0 <= r < 3 and 0 <= c < 3:
                    move = (r, c)

        commentary = data.get("commentary", "").strip() if isinstance(data, dict) else ""

        # Validate move and cell
        if move is None or board[move[0]][move[1]] != "":
            print("AI returned invalid or occupied move from JSON:", ai_text)
            move = random_valid_move()
            if not commentary:
                commentary = "I had trouble choosing, so I picked a random valid move."

        if not commentary:
            commentary = f"I chose cell {move[0]},{move[1]} based on the current board position."

        return move, commentary

    except Exception as e:
        print("Error calling OpenAI or parsing JSON:", e)
        move = random_valid_move()
        commentary = "There was an error getting my planned move, so I picked a random valid move."
        return move, commentary


def end_game(winner):
    if winner == "Draw":
        status_label.config(text="It is a draw.")
        messagebox.showinfo("Game Over", "It is a draw.")
        commentary_label.config(text="That was close. Neither of us could force a win.")
    elif winner == HUMAN:
        status_label.config(text="You win!")
        messagebox.showinfo("Game Over", "You win!")
        commentary_label.config(
            text="Nice job. You found a winning line before I could block it."
        )
    else:
        status_label.config(text="Computer wins.")
        messagebox.showinfo("Game Over", "Computer wins.")
        commentary_label.config(
            text="I managed to create a line of three. Try to watch for forks and block earlier."
        )
    disable_all_buttons()


def computer_move():
    global current_player

    if check_winner(board) is not None:
        return

    move, commentary = get_ai_move_from_chatgpt()
    if move is None:
        return

    r, c = move
    board[r][c] = AI
    buttons[r][c]["text"] = AI
    buttons[r][c]["state"] = "disabled"

    # Update commentary section
    commentary_label.config(text=commentary)

    winner = check_winner(board)
    if winner:
        end_game(winner)
        return

    current_player = HUMAN
    status_label.config(text="Your turn (X)")


def on_button_click(row, col):
    global current_player

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

    # Computer turn
    current_player = AI
    status_label.config(text="Computer thinking...")
    commentary_label.config(
        text="I am considering the best move based on the current board."
    )
    # Let the label update, then call the AI
    root.after(200, computer_move)


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
    commentary_label.config(
        text="Welcome back. Make your first move and I will respond."
    )


# Tkinter UI setup
root = tk.Tk()
root.title("Tic Tac Toe vs ChatGPT")

status_label = tk.Label(root, text="Your turn (X)", font=("Arial", 16))
status_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

# 3x3 board buttons
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

# Commentary label (AI explanation area)
commentary_label = tk.Label(
    root,
    text="Welcome. You are X. Make your move and I will explain my responses here.",
    font=("Arial", 11),
    justify="left",
    wraplength=360,
    anchor="w",
)
commentary_label.grid(row=4, column=0, columnspan=3, padx=10, pady=(5, 5), sticky="w")

# Reset button
reset_button = tk.Button(root, text="Reset", font=("Arial", 14), command=reset_game)
reset_button.grid(row=5, column=0, columnspan=3, pady=(5, 10))

root.mainloop()
