import tkinter as tk
from tkinter import messagebox
import random
import string
import math


class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("480x660")
        self.root.configure(bg="#0f0f1a")
        self.root.resizable(False, False)

        self.length_var = tk.IntVar(value=16)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)
        self.password_var = tk.StringVar(value="Click Generate to create a password")
        self.strength_var = tk.StringVar(value="")
        self.history = []

        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#0f0f1a", pady=20)
        header.pack(fill="x")

        tk.Label(header, text="Password Generator",
                 font=("Helvetica", 22, "bold"),
                 fg="#ffffff", bg="#0f0f1a").pack()
        tk.Label(header, text="Generate strong, random passwords instantly",
                 font=("Helvetica", 11),
                 fg="#666888", bg="#0f0f1a").pack(pady=(4, 0))

        card = tk.Frame(self.root, bg="#1a1a2e", padx=24, pady=20)
        card.pack(fill="x", padx=24)

        tk.Label(card, text="PASSWORD LENGTH",
                 font=("Helvetica", 10, "bold"),
                 fg="#888aaa", bg="#1a1a2e").pack(anchor="w")

        length_row = tk.Frame(card, bg="#1a1a2e")
        length_row.pack(fill="x", pady=(6, 14))

        self.length_label = tk.Label(length_row,
                                     text=str(self.length_var.get()),
                                     font=("Helvetica", 22, "bold"),
                                     fg="#6c63ff", bg="#1a1a2e", width=3)
        self.length_label.pack(side="right")

        tk.Scale(
            length_row, from_=6, to=64,
            orient="horizontal", variable=self.length_var,
            bg="#1a1a2e", fg="#ffffff",
            troughcolor="#2e2e4e", activebackground="#6c63ff",
            highlightthickness=0, bd=0,
            showvalue=False,
            command=self._on_length_change
        ).pack(fill="x", side="left", expand=True, padx=(0, 12))

        tk.Frame(card, bg="#2a2a4a", height=1).pack(fill="x", pady=(0, 14))

        tk.Label(card, text="CHARACTER TYPES",
                 font=("Helvetica", 10, "bold"),
                 fg="#888aaa", bg="#1a1a2e").pack(anchor="w", pady=(0, 8))

        options = [
            (self.use_upper,         "Uppercase letters",      "A - Z"),
            (self.use_lower,         "Lowercase letters",      "a - z"),
            (self.use_digits,        "Numbers",                "0 - 9"),
            (self.use_symbols,       "Symbols",                "! @ # $ % ..."),
            (self.exclude_ambiguous, "Exclude ambiguous chars", "0 O 1 l I"),
        ]

        for var, label, hint in options:
            row = tk.Frame(card, bg="#1a1a2e")
            row.pack(fill="x", pady=2)
            tk.Checkbutton(
                row, variable=var,
                bg="#1a1a2e", activebackground="#1a1a2e",
                selectcolor="#2a2a4e", fg="#ffffff",
                cursor="hand2"
            ).pack(side="left")
            tk.Label(row, text=label,
                     font=("Helvetica", 12), fg="#ddddff",
                     bg="#1a1a2e").pack(side="left")
            tk.Label(row, text=hint,
                     font=("Helvetica", 10), fg="#555577",
                     bg="#1a1a2e").pack(side="right")

        tk.Button(
            self.root, text="Generate Password",
            font=("Helvetica", 14, "bold"),
            fg="#ffffff", bg="#6c63ff",
            activebackground="#574fd6",
            activeforeground="#ffffff",
            relief="flat", cursor="hand2", pady=12,
            command=self.generate
        ).pack(fill="x", padx=24, pady=16)

        out_card = tk.Frame(self.root, bg="#1a1a2e", padx=20, pady=14)
        out_card.pack(fill="x", padx=24)

        tk.Label(out_card, text="GENERATED PASSWORD",
                 font=("Helvetica", 10, "bold"),
                 fg="#888aaa", bg="#1a1a2e").pack(anchor="w", pady=(0, 8))

        pw_row = tk.Frame(out_card, bg="#0f0f1a", bd=1, relief="solid")
        pw_row.pack(fill="x")

        self.pw_label = tk.Label(
            pw_row, textvariable=self.password_var,
            font=("Courier", 13, "bold"),
            fg="#00ffaa", bg="#0f0f1a",
            wraplength=310, justify="left",
            padx=12, pady=10, anchor="w"
        )
        self.pw_label.pack(side="left", fill="x", expand=True)

        tk.Button(
            pw_row, text="Copy",
            font=("Helvetica", 11),
            fg="#6c63ff", bg="#0f0f1a",
            activebackground="#1a1a2e",
            activeforeground="#ffffff",
            relief="flat", cursor="hand2",
            padx=10, pady=10,
            command=self._copy
        ).pack(side="right")

        strength_row = tk.Frame(out_card, bg="#1a1a2e")
        strength_row.pack(fill="x", pady=(10, 4))

        tk.Label(strength_row, text="Strength:",
                 font=("Helvetica", 11),
                 fg="#666888", bg="#1a1a2e").pack(side="left")

        self.strength_label = tk.Label(
            strength_row, textvariable=self.strength_var,
            font=("Helvetica", 11, "bold"),
            fg="#00ffaa", bg="#1a1a2e"
        )
        self.strength_label.pack(side="left", padx=(6, 0))

        self.bar_canvas = tk.Canvas(
            out_card, bg="#1a1a2e", height=8,
            highlightthickness=0
        )
        self.bar_canvas.pack(fill="x", pady=(4, 0))

        hist_outer = tk.Frame(self.root, bg="#0f0f1a", padx=24, pady=8)
        hist_outer.pack(fill="x")

        hist_top = tk.Frame(hist_outer, bg="#0f0f1a")
        hist_top.pack(fill="x")

        tk.Label(hist_top, text="RECENT PASSWORDS",
                 font=("Helvetica", 10, "bold"),
                 fg="#444466", bg="#0f0f1a").pack(side="left")

        tk.Button(hist_top, text="Clear history",
                  font=("Helvetica", 10),
                  fg="#555577", bg="#0f0f1a",
                  activebackground="#0f0f1a",
                  relief="flat", cursor="hand2",
                  command=self._clear_history).pack(side="right")

        self.hist_inner = tk.Frame(hist_outer, bg="#0f0f1a")
        self.hist_inner.pack(fill="x", pady=(6, 0))

    def _on_length_change(self, val):
        self.length_label.config(text=str(int(float(val))))

    def _build_charset(self):
        charset = ""
        if self.use_upper.get():
            charset += string.ascii_uppercase
        if self.use_lower.get():
            charset += string.ascii_lowercase
        if self.use_digits.get():
            charset += string.digits
        if self.use_symbols.get():
            charset += string.punctuation
        if self.exclude_ambiguous.get():
            for ch in "0O1lI|`'\"":
                charset = charset.replace(ch, "")
        return charset

    def generate(self):
        charset = self._build_charset()
        if not charset:
            messagebox.showwarning(
                "No character types",
                "Please select at least one character type."
            )
            return

        length = self.length_var.get()
        guaranteed = []

        if self.use_upper.get():
            pool = string.ascii_uppercase
            if self.exclude_ambiguous.get():
                pool = "".join(c for c in pool if c not in "OI")
            if pool:
                guaranteed.append(random.choice(pool))

        if self.use_lower.get():
            pool = string.ascii_lowercase
            if self.exclude_ambiguous.get():
                pool = "".join(c for c in pool if c not in "l")
            if pool:
                guaranteed.append(random.choice(pool))

        if self.use_digits.get():
            pool = string.digits
            if self.exclude_ambiguous.get():
                pool = "".join(c for c in pool if c not in "01")
            if pool:
                guaranteed.append(random.choice(pool))

        if self.use_symbols.get():
            pool = string.punctuation
            if self.exclude_ambiguous.get():
                pool = "".join(c for c in pool if c not in "|`'\"")
            if pool:
                guaranteed.append(random.choice(pool))

        guaranteed = guaranteed[:length]
        remaining_count = length - len(guaranteed)
        remaining = [random.choice(charset) for _ in range(remaining_count)]

        password_list = guaranteed + remaining
        random.shuffle(password_list)
        password = "".join(password_list)

        self.password_var.set(password)
        self._update_strength(password)
        self._add_to_history(password)

    def _update_strength(self, password):
        charset_size = 0
        if any(c in string.ascii_uppercase for c in password):
            charset_size += 26
        if any(c in string.ascii_lowercase for c in password):
            charset_size += 26
        if any(c in string.digits for c in password):
            charset_size += 10
        if any(c in string.punctuation for c in password):
            charset_size += 32

        if charset_size > 0:
            entropy = len(password) * math.log2(charset_size)
        else:
            entropy = 0

        if entropy < 40:
            label, color, pct = "Weak", "#ff4d6d", 0.25
        elif entropy < 60:
            label, color, pct = "Fair", "#ffaa00", 0.50
        elif entropy < 80:
            label, color, pct = "Strong", "#00ccff", 0.75
        else:
            label, color, pct = "Very Strong", "#00ffaa", 1.0

        self.strength_var.set("{} ({} bits)".format(label, int(entropy)))
        self.strength_label.config(fg=color)
        self._draw_bar(pct, color)

    def _draw_bar(self, pct, color):
        self.bar_canvas.update_idletasks()
        w = self.bar_canvas.winfo_width()
        if w <= 1:
            w = 400
        self.bar_canvas.delete("all")
        self.bar_canvas.create_rectangle(0, 0, w, 8, fill="#2a2a4a", outline="")
        self.bar_canvas.create_rectangle(0, 0, int(w * pct), 8, fill=color, outline="")

    def _copy(self):
        pw = self.password_var.get()
        if not pw or pw == "Click Generate to create a password":
            messagebox.showinfo("Nothing to copy", "Generate a password first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(pw)
        self.root.update()
        messagebox.showinfo("Copied!", "Password copied to clipboard.")

    def _copy_text(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        messagebox.showinfo("Copied!", "Password copied to clipboard.")

    def _add_to_history(self, password):
        self.history.insert(0, password)
        self.history = self.history[:5]
        self._refresh_history()

    def _refresh_history(self):
        for widget in self.hist_inner.winfo_children():
            widget.destroy()
        for pw in self.history:
            row = tk.Frame(self.hist_inner, bg="#0f0f1a")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=pw,
                     font=("Courier", 10), fg="#444466",
                     bg="#0f0f1a", anchor="w").pack(side="left", fill="x", expand=True)
            tk.Button(row, text="Copy",
                      font=("Helvetica", 9),
                      fg="#555577", bg="#0f0f1a",
                      activebackground="#1a1a2e",
                      relief="flat", cursor="hand2",
                      command=lambda p=pw: self._copy_text(p)).pack(side="right")

    def _clear_history(self):
        self.history = []
        self._refresh_history()


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
