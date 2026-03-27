import tkinter as tk

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("360x580")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        self.expression = ""
        self.display_var = tk.StringVar(value="0")
        self.sub_display_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        # ── Display ──────────────────────────────────────────────
        display_frame = tk.Frame(self.root, bg="#1e1e2e", pady=20, padx=20)
        display_frame.pack(fill="x")

        tk.Label(display_frame, textvariable=self.sub_display_var,
                 font=("Helvetica Neue", 13), fg="#888aaa", bg="#1e1e2e",
                 anchor="e").pack(fill="x")

        tk.Label(display_frame, textvariable=self.display_var,
                 font=("Helvetica Neue", 42, "bold"), fg="#ffffff", bg="#1e1e2e",
                 anchor="e", wraplength=320, justify="right").pack(fill="x")

        # ── Divider ───────────────────────────────────────────────
        tk.Frame(self.root, bg="#333355", height=1).pack(fill="x", padx=20)

        # ── Buttons ───────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg="#1e1e2e", padx=16, pady=16)
        btn_frame.pack(fill="both", expand=True)

        # Button layout: (label, row, col, colspan, style)
        buttons = [
            # Row 0 — utility row
            ("AC",  0, 0, 1, "util"),
            ("+/-", 0, 1, 1, "util"),
            ("%",   0, 2, 1, "util"),
            ("÷",   0, 3, 1, "op"),
            # Row 1
            ("7", 1, 0, 1, "num"),
            ("8", 1, 1, 1, "num"),
            ("9", 1, 2, 1, "num"),
            ("×", 1, 3, 1, "op"),
            # Row 2
            ("4", 2, 0, 1, "num"),
            ("5", 2, 1, 1, "num"),
            ("6", 2, 2, 1, "num"),
            ("−", 2, 3, 1, "op"),
            # Row 3
            ("1", 3, 0, 1, "num"),
            ("2", 3, 1, 1, "num"),
            ("3", 3, 2, 1, "num"),
            ("+", 3, 3, 1, "op"),
            # Row 4
            ("0", 4, 0, 2, "num"),   # wide zero
            (".", 4, 2, 1, "num"),
            ("=", 4, 3, 1, "eq"),
        ]

        # Color palette
        colors = {
            "num":  {"bg": "#2e2e4e", "fg": "#ffffff", "active": "#3e3e6e"},
            "op":   {"bg": "#6c63ff", "fg": "#ffffff", "active": "#574fd6"},
            "util": {"bg": "#3a3a5c", "fg": "#ffffff", "active": "#4a4a7c"},
            "eq":   {"bg": "#ff6584", "fg": "#ffffff", "active": "#e0506e"},
        }

        for (label, row, col, colspan, style) in buttons:
            c = colors[style]
            btn = tk.Button(
                btn_frame,
                text=label,
                font=("Helvetica Neue", 20, "bold"),
                fg=c["fg"], bg=c["bg"],
                activebackground=c["active"], activeforeground=c["fg"],
                relief="flat", bd=0, cursor="hand2",
                command=lambda l=label: self._on_press(l)
            )
            btn.grid(
                row=row, column=col,
                columnspan=colspan,
                padx=6, pady=6,
                sticky="nsew",
                ipadx=0, ipady=18
            )

        # Make grid cells expand evenly
        for i in range(4):
            btn_frame.columnconfigure(i, weight=1)
        for i in range(5):
            btn_frame.rowconfigure(i, weight=1)

        # Keyboard support
        self.root.bind("<Key>", self._on_key)

    # ── INPUT HANDLER ────────────────────────────────────────────────────────

    def _on_press(self, label):
        if label == "AC":
            self.expression = ""
            self.display_var.set("0")
            self.sub_display_var.set("")

        elif label == "+/-":
            if self.expression and self.expression != "0":
                if self.expression.startswith("-"):
                    self.expression = self.expression[1:]
                else:
                    self.expression = "-" + self.expression
                self.display_var.set(self.expression)

        elif label == "%":
            try:
                val = float(self.expression) / 100
                self.expression = self._format(val)
                self.display_var.set(self.expression)
            except:
                self.display_var.set("Error")

        elif label == "=":
            self._calculate()

        elif label in ("÷", "×", "−", "+"):
            op_map = {"÷": "/", "×": "*", "−": "-", "+": "+"}
            # Avoid double operator
            if self.expression and self.expression[-1] in "+-*/":
                self.expression = self.expression[:-1]
            self.expression += op_map[label]
            self.sub_display_var.set(
                self.expression.replace("/","÷").replace("*","×").replace("-","−")
            )
            self.display_var.set(op_map[label])

        elif label == ".":
            # Only add dot if current number doesn't already have one
            parts = self.expression.replace("+","|").replace("-","|") \
                                   .replace("*","|").replace("/","|").split("|")
            if "." not in (parts[-1] if parts else ""):
                if not self.expression or self.expression[-1] in "+-*/":
                    self.expression += "0"
                self.expression += "."
                self.display_var.set(self.expression)

        else:
            # Digit
            if self.display_var.get() == "0" and label != ".":
                self.expression = label if not self.expression or self.expression[-1] in "+-*/" else self.expression + label
            else:
                self.expression += label
            # Show only the current number being typed
            parts = self.expression.replace("+","|").replace("*","|") \
                                   .replace("/","|")
            # split on operators but keep negative at start
            import re
            tokens = re.split(r'(?<=[0-9)])([\+\-\*\/])', self.expression)
            self.display_var.set(tokens[-1] if tokens else self.expression)

    def _calculate(self):
        try:
            expr = self.expression
            self.sub_display_var.set(
                expr.replace("/","÷").replace("*","×").replace("-","−") + " ="
            )
            result = eval(expr)
            formatted = self._format(result)
            self.display_var.set(formatted)
            self.expression = formatted
        except ZeroDivisionError:
            self.display_var.set("÷ 0 Error")
            self.sub_display_var.set("")
            self.expression = ""
        except:
            self.display_var.set("Error")
            self.expression = ""

    def _format(self, val):
        """Return int string if whole number, else float string."""
        if val == int(val):
            return str(int(val))
        return str(round(val, 10)).rstrip("0")

    # ── KEYBOARD SUPPORT ─────────────────────────────────────────────────────

    def _on_key(self, event):
        key = event.char
        keysym = event.keysym
        mapping = {
            "/": "÷", "*": "×", "-": "−",
            "+": "+", ".": ".", "=": "=",
            "\r": "=", "\x08": "AC"   # Enter, Backspace
        }
        if key in "0123456789":
            self._on_press(key)
        elif key in mapping:
            self._on_press(mapping[key])
        elif keysym == "Return":
            self._on_press("=")
        elif keysym == "BackSpace":
            # Delete last character
            if self.expression:
                self.expression = self.expression[:-1]
                self.display_var.set(self.expression if self.expression else "0")
        elif keysym == "Escape":
            self._on_press("AC")


if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()
