import tkinter as tk
from tkinter import messagebox
import random
import json

from openai import OpenAI

# Uses OPENAI_API_KEY from your environment
client = OpenAI()

HUMAN = "X"
AI = "O"

current_player = HUMAN
board = [["" for _ in range(3)] for _ in range(3)]
buttons = []


def board_to_text(b):
    """Represent the board as text for the model. Empty cells are '.'."""
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
    # Draw
    for row in b:
        for cell in row:
            if cell == "":
                return None
    return "Draw"


def random_valid_move():
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    return random.choice(empty_cells) if empty_cells else None


# ------------- AI 1: proposer ------------- #

def get_ai1_suggestion():
    """
    First AI: suggests a move and commentary.
    Returns (move, commentary)
    move is (row, col)
    """
    board_str = board_to_text(board)

    prompt = f"""
You are AI 1 playing tic tac toe as O against a human who is X.

Board format:
- 3 rows, 3 columns
- Each row is on its own line
- Cells contain X, O, or . (empty)
- Rows and columns are indexed 0, 1, 2.

Current board:
{board_str}

It is your turn as O.
You must choose exactly one empty cell (with .).

Respond ONLY with a single JSON object in this exact format:
{{
  "move": [row, col],
  "commentary": "Explain in 1 to 2 sentences why you chose this move."
}}
"""

    try:
        response = client.responses.create(
            model="gpt-5.1",
            instructions=(
                "You are AI 1 playing tic tac toe. "
                "Always reply with valid JSON that has 'move' and 'commentary'. "
                "Do not include any extra text outside the JSON."
            ),
            input=prompt,
        )

        ai_text = response.output_text.strip()
        data = json.loads(ai_text)

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

        # Validate move
        if move is None or board[move[0]][move[1]] != "":
            print("AI 1 returned invalid or occupied move:", ai_text)
            move = random_valid_move()
            if not commentary:
                commentary = "I had trouble choosing, so I picked a random valid move."

        if not commentary:
            commentary = f"I chose cell {move[0]},{move[1]} based on simple tactical considerations."

        return move, commentary

    except Exception as e:
        print("Error in AI 1:", e)
        move = random_valid_move()
        commentary = "There was an error, so I made a safe random move."
        return move, commentary


# ------------- AI 2: reviewer ------------- #

def get_ai2_review(proposed_move, ai1_commentary):
    """
    Second AI persona: reviewer / coach.
    It sees the board, the proposed move, and AI 1's commentary.
    It can keep the move or change it.

    Returns (final_move, review_commentary)
    """
    board_str = board_to_text(board)
    r1, c1 = proposed_move

    prompt = f"""
You are AI 2, a tic tac toe coach reviewing AI 1's suggestion.

Board format:
- 3 rows, 3 columns
- Each row is on its own line
- Cells contain X, O, or . (empty)
- Rows and columns are indexed 0, 1, 2.

Current board:
{board_str}

Situation:
- Human is X.
- AI plays as O.
- It is O's turn.

AI 1 suggested this move: [ {r1}, {c1} ]
AI 1's commentary: "{ai1_commentary}"

Your job:
- Evaluate whether AI 1's move is good.
- You can either keep that move or choose a different empty cell if you think there is a clearly better move.
- You must always end with a legal empty cell for O.

Respond ONLY with a single JSON object in this exact format:
{{
  "final_move": [row, col],
  "analysis": "In 1 to 3 sentences, explain whether you kept or changed the move and why."
}}
"""

    try:
        response = client.responses.create(
            model="gpt-5.1",
            instructions=(
                "You are AI 2, a reviewer of tic tac toe moves. "
                "Always reply with valid JSON that has 'final_move' and 'analysis'. "
                "Do not include any extra text outside the JSON."
            ),
            input=prompt,
        )

        ai_text = response.output_text.strip()
        data = json.loads(ai_text)

        final_move = None
        analysis = ""

        if isinstance(data, dict) and "final_move" in data:
            mv = data["final_move"]
            if (
                isinstance(mv, list)
                and len(mv) == 2
                and isinstance(mv[0], int)
                and isinstance(mv[1], int)
            ):
                r, c = mv
                if 0 <= r < 3 and 0 <= c < 3:
                    final_move = (r, c)

        analysis = data.get("analysis", "").strip() if isinstance(data, dict) else ""

        # Validate final move
        if final_move is None or board[final_move[0]][final_move[1]] != "":
            print("AI 2 returned invalid or occupied move:", ai_text)
            # If invalid, fall back to original AI 1 move if it is legal
            if board[proposed_move[0]][proposed_move[1]] == "":
                final_move = proposed_move
                if not analysis:
                    analysis = "I tried to change the move but the result was invalid, so I kept the original move."
            else:
                final_move = random_valid_move()
                if not analysis:
                    analysis = "Both my suggestion and AI 1's move were invalid, so I picked a random valid move."

        if not analysis:
            if final_move == proposed_move:
                analysis = "I agreed with AI 1's choice and kept the same move."
            else:
                analysis = "I found an alternative that I believe is tactically stronger in this position."

        return final_move, analysis

    except Exception as e:
        print("Error in AI 2:", e)
        # Fall back to AI 1 move if possible
        if board[proposed_move[0]][proposed_move[1]] == "":
            final_move = proposed_move
            analysis = "There was an error in my review, so I kept AI 1's original move."
        else:
            final_move = random_valid_move()
            analysis = "There was an error in my review, so I chose a random legal move."
        return final_move, analysis


# ------------- Game flow ------------- #

def end_game(winner):
    if winner == "Draw":
        status_label.config(text="It is a draw.")
        messagebox.showinfo("Game Over", "It is a draw.")
        commentary_label.config(
            text="AI 1 and AI 2 agree that neither side could force a win in this game."
        )
    elif winner == HUMAN:
        status_label.config(text="You win!")
        messagebox.showinfo("Game Over", "You win!")
        commentary_label.config(
            text="Nice work. Both AI 1 and AI 2 would say that you found a line that they failed to stop."
        )
    else:
        status_label.config(text="Computer wins.")
        messagebox.showinfo("Game Over", "Computer wins.")
        commentary_label.config(
            text="AI 1 and AI 2 combined to find a winning sequence. Try to watch for double threats next time."
        )
    disable_all_buttons()


def computer_move():
    global current_player

    if check_winner(board) is not None:
        return

    # First AI proposes
    ai1_move, ai1_commentary = get_ai1_suggestion()

    # Second AI reviews
    final_move, ai2_analysis = get_ai2_review(ai1_move, ai1_commentary)

    r, c = final_move
    board[r][c] = AI
    buttons[r][c]["text"] = AI
    buttons[r][c]["state"] = "disabled"

    # Show both commentaries
    combined_text = (
        f"AI 1: {ai1_commentary}\n"
        f"AI 2: {ai2_analysis} (final move: {r},{c})"
    )
    commentary_label.config(text=combined_text)

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
    status_label.config(text="AI 1 and AI 2 are thinking...")
    commentary_label.config(
        text="AI 1 will propose a move and AI 2 will review it to decide on the final choice."
    )
    # Let UI update then call the AI
    root.after(300, computer_move)


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
        text="Welcome. You are X. Make a move and watch how AI 1 and AI 2 discuss the reply."
    )


# ------------- Tkinter UI ------------- #

root = tk.Tk()
root.title("Tic Tac Toe with Two AI Personas")

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

# Commentary label for both AIs
commentary_label = tk.Label(
    root,
    text="Welcome. You are X. Make a move and the two AIs will discuss the response here.",
    font=("Arial", 11),
    justify="left",
    wraplength=380,
    anchor="w",
)
commentary_label.grid(row=4, column=0, columnspan=3, padx=10, pady=(5, 5), sticky="w")

# Reset button
reset_button = tk.Button(root, text="Reset", font=("Arial", 14), command=reset_game)
reset_button.grid(row=5, column=0, columnspan=3, pady=(5, 10))

root.mainloop()
