import tkinter as tk
from tkinter import messagebox
import random
import math

# European roulette wheel sequence (single zero)
WHEEL_NUMBERS = [
    0,
    32, 15, 19, 4, 21, 2, 25, 17, 34, 6,
    27, 13, 36, 11, 30, 8, 23, 10, 5, 24,
    16, 33, 1, 20, 14, 31, 9, 22, 18, 29,
    7, 28, 12, 35, 3, 26
]

RED_NUMBERS = {
    1, 3, 5, 7, 9, 12, 14, 16, 18,
    19, 21, 23, 25, 27, 30, 32, 34, 36
}
BLACK_NUMBERS = {
    2, 4, 6, 8, 10, 11, 13, 15, 17,
    20, 22, 24, 26, 28, 29, 31, 33, 35
}


def get_color(num):
    if num == 0:
        return "green"
    elif num in RED_NUMBERS:
        return "red"
    elif num in BLACK_NUMBERS:
        return "black"
    else:
        return "gray"


class RouletteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Roulette App")

        self.balance = 1000  # starting balance
        self.ball_id = None  # canvas item id for the ball

        # Canvas for wheel
        self.canvas_size = 400
        self.canvas = tk.Canvas(
            root,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="darkgreen",
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, rowspan=8, padx=10, pady=10)

        # Right side controls
        controls = tk.Frame(root)
        controls.grid(row=0, column=1, sticky="n", padx=10, pady=10)

        # Balance display
        self.balance_label = tk.Label(controls, text=f"Balance: ${self.balance}")
        self.balance_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        # Bet amount
        tk.Label(controls, text="Bet amount:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.bet_entry = tk.Entry(controls)
        self.bet_entry.grid(row=1, column=1, padx=5, pady=5)
        self.bet_entry.insert(0, "100")

        # Bet type choice
        tk.Label(controls, text="Bet type:").grid(row=2, column=0, sticky="e", padx=5, pady=5)

        self.bet_type = tk.StringVar(value="Red")
        self.bet_type_menu = tk.OptionMenu(
            controls,
            self.bet_type,
            "Red",
            "Black",
            "Even",
            "Odd",
            "Number"
        )
        self.bet_type_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Number entry (only used if bet type is "Number")
        tk.Label(controls, text="Number (0-36):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.number_entry = tk.Entry(controls)
        self.number_entry.grid(row=3, column=1, padx=5, pady=5)

        # Spin button
        self.spin_button = tk.Button(controls, text="Spin", command=self.spin)
        self.spin_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Result label
        self.result_label = tk.Label(controls, text="Result: -", font=("Arial", 14))
        self.result_label.grid(row=5, column=0, columnspan=2, pady=10)

        # Message label
        self.message_label = tk.Label(controls, text="", fg="blue")
        self.message_label.grid(row=6, column=0, columnspan=2, pady=5)

        # Draw the initial wheel
        self.draw_wheel()

    def draw_wheel(self):
        self.canvas.delete("all")

        cx = cy = self.canvas_size // 2
        outer_radius = 180
        inner_radius = 70
        text_radius = 130

        angle_step = 360 / len(WHEEL_NUMBERS)

        # Draw outer circle background
        self.canvas.create_oval(
            cx - outer_radius - 5,
            cy - outer_radius - 5,
            cx + outer_radius + 5,
            cy + outer_radius + 5,
            outline="gold",
            width=4
        )

        # Draw pockets
        for i, num in enumerate(WHEEL_NUMBERS):
            # We go clockwise by decreasing angle, starting at 90 degrees (top)
            start_angle = 90 - i * angle_step
            extent = -angle_step  # negative extent makes the arc go clockwise

            color = get_color(num)

            # Pocket wedge
            self.canvas.create_arc(
                cx - outer_radius, cy - outer_radius,
                cx + outer_radius, cy + outer_radius,
                start=start_angle,
                extent=extent,
                fill=color,
                outline="white",
                width=1
            )

            # Text label for the number
            angle_mid = start_angle + extent / 2
            rad = math.radians(angle_mid)

            tx = cx + math.cos(rad) * text_radius
            ty = cy - math.sin(rad) * text_radius

            text_color = "white" if color != "green" else "black"

            self.canvas.create_text(
                tx, ty,
                text=str(num),
                fill=text_color,
                font=("Arial", 10, "bold")
            )

        # Inner circle to make a ring
        self.canvas.create_oval(
            cx - inner_radius,
            cy - inner_radius,
            cx + inner_radius,
            cy + inner_radius,
            fill="darkgreen",
            outline="gold",
            width=3
        )

        # Center decoration
        self.canvas.create_oval(
            cx - 20, cy - 20,
            cx + 20, cy + 20,
            fill="gold",
            outline="black"
        )

        # Pointer at the top
        pointer_width = 20
        pointer_height = 20
        self.canvas.create_polygon(
            cx, cy - outer_radius - 10,              # tip
            cx - pointer_width // 2, cy - outer_radius + pointer_height,
            cx + pointer_width // 2, cy - outer_radius + pointer_height,
            fill="gold",
            outline="black"
        )

    def draw_ball(self, result_number):
        # Remove old ball
        if self.ball_id is not None:
            self.canvas.delete(self.ball_id)

        # Find index of result_number in wheel
        try:
            idx = WHEEL_NUMBERS.index(result_number)
        except ValueError:
            return

        cx = cy = self.canvas_size // 2
        ball_radius = 8
        ball_distance = 155  # distance from center where ball should sit
        angle_step = 360 / len(WHEEL_NUMBERS)

        start_angle = 90 - idx * angle_step
        extent = -angle_step
        angle_mid = start_angle + extent / 2

        rad = math.radians(angle_mid)

        bx = cx + math.cos(rad) * ball_distance
        by = cy - math.sin(rad) * ball_distance

        self.ball_id = self.canvas.create_oval(
            bx - ball_radius,
            by - ball_radius,
            bx + ball_radius,
            by + ball_radius,
            fill="white",
            outline="black",
            width=2
        )

    def spin(self):
        # Validate bet amount
        try:
            bet_amount = int(self.bet_entry.get())
            if bet_amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Bet amount must be a positive integer.")
            return

        if bet_amount > self.balance:
            messagebox.showerror("Error", "You cannot bet more than your balance.")
            return

        chosen_type = self.bet_type.get()
        chosen_number = None

        if chosen_type == "Number":
            try:
                chosen_number = int(self.number_entry.get())
                if chosen_number < 0 or chosen_number > 36:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number between 0 and 36.")
                return

        # Spin the wheel
        result = random.choice(WHEEL_NUMBERS)
        color = get_color(result).capitalize()

        # Update wheel ball position
        self.draw_ball(result)

        self.result_label.config(text=f"Result: {result} ({color})")

        winnings = self.calculate_winnings(
            bet_amount, chosen_type, chosen_number, result, color
        )

        self.balance += winnings - bet_amount
        self.balance_label.config(text=f"Balance: ${self.balance}")

        if winnings > 0:
            self.message_label.config(
                text=f"You won ${winnings - bet_amount}! Payout: ${winnings}",
                fg="green"
            )
        else:
            self.message_label.config(
                text=f"You lost ${bet_amount}.",
                fg="red"
            )

    def calculate_winnings(self, bet, bet_type, bet_number, result, color):
        """
        Returns total amount returned to player (0 if they lose).

        Payouts:
        Red or Black  1 to 1
        Even or Odd   1 to 1
        Single number 35 to 1
        """
        # Single number
        if bet_type == "Number":
            if result == bet_number:
                return bet * 36  # 35 to 1 plus original
            else:
                return 0

        # Red or Black
        if bet_type == "Red":
            if color.lower() == "red":
                return bet * 2
            else:
                return 0

        if bet_type == "Black":
            if color.lower() == "black":
                return bet * 2
            else:
                return 0

        # Even or Odd (0 is neither)
        if bet_type == "Even":
            if result != 0 and result % 2 == 0:
                return bet * 2
            else:
                return 0

        if bet_type == "Odd":
            if result % 2 == 1:
                return bet * 2
            else:
                return 0

        return 0


if __name__ == "__main__":
    root = tk.Tk()
    app = RouletteApp(root)
    root.mainloop()
