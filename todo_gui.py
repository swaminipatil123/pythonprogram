import tkinter as tk
from tkinter import messagebox, font
import json
import os
from datetime import datetime

DATA_FILE = "todos.json"


def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")
        self.root.geometry("620x680")
        self.root.configure(bg="#f5f5f0")
        self.root.resizable(True, True)

        self.tasks = load_tasks()
        self.filter_mode = "all"

        self._build_ui()
        self._refresh_list()

    # ── UI CONSTRUCTION ──────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1a1a2e", pady=18)
        header.pack(fill="x")

        tk.Label(header, text="✅  My To-Do List", font=("Helvetica Neue", 20, "bold"),
                 fg="#ffffff", bg="#1a1a2e").pack()
        self.subtitle_var = tk.StringVar()
        tk.Label(header, textvariable=self.subtitle_var, font=("Helvetica Neue", 11),
                 fg="#aaaacc", bg="#1a1a2e").pack(pady=(2, 0))

        # Input area
        input_frame = tk.Frame(self.root, bg="#f5f5f0", pady=14, padx=20)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="Task", font=("Helvetica Neue", 11, "bold"),
                 bg="#f5f5f0", fg="#444").grid(row=0, column=0, sticky="w")
        tk.Label(input_frame, text="Priority", font=("Helvetica Neue", 11, "bold"),
                 bg="#f5f5f0", fg="#444").grid(row=0, column=1, sticky="w", padx=(14, 0))
        tk.Label(input_frame, text="Due Date (optional)", font=("Helvetica Neue", 11, "bold"),
                 bg="#f5f5f0", fg="#444").grid(row=0, column=2, sticky="w", padx=(14, 0))

        self.task_entry = tk.Entry(input_frame, font=("Helvetica Neue", 13),
                                   relief="flat", bd=0, highlightthickness=1,
                                   highlightbackground="#cccccc", highlightcolor="#6c63ff",
                                   bg="white", width=24)
        self.task_entry.grid(row=1, column=0, ipady=8, sticky="ew")
        self.task_entry.bind("<Return>", lambda e: self._add_task())

        self.priority_var = tk.StringVar(value="Medium")
        priority_menu = tk.OptionMenu(input_frame, self.priority_var, "High", "Medium", "Low")
        priority_menu.config(font=("Helvetica Neue", 12), relief="flat", bg="white",
                             highlightthickness=1, highlightbackground="#cccccc", width=8)
        priority_menu.grid(row=1, column=1, padx=(14, 0), ipady=4, sticky="w")

        self.due_entry = tk.Entry(input_frame, font=("Helvetica Neue", 12),
                                  relief="flat", bd=0, highlightthickness=1,
                                  highlightbackground="#cccccc", highlightcolor="#6c63ff",
                                  bg="white", width=14)
        self.due_entry.insert(0, "YYYY-MM-DD")
        self.due_entry.config(fg="#aaa")
        self.due_entry.bind("<FocusIn>", self._clear_placeholder)
        self.due_entry.bind("<FocusOut>", self._restore_placeholder)
        self.due_entry.grid(row=1, column=2, ipady=8, padx=(14, 0), sticky="ew")

        add_btn = tk.Button(input_frame, text="+ Add Task", font=("Helvetica Neue", 12, "bold"),
                            bg="#6c63ff", fg="white", relief="flat", padx=18, pady=6,
                            cursor="hand2", command=self._add_task,
                            activebackground="#574fd6", activeforeground="white")
        add_btn.grid(row=1, column=3, padx=(14, 0), sticky="ew")

        input_frame.columnconfigure(0, weight=3)

        # Divider
        tk.Frame(self.root, bg="#e0e0e0", height=1).pack(fill="x", padx=20)

        # Filter bar
        filter_frame = tk.Frame(self.root, bg="#f5f5f0", pady=10, padx=20)
        filter_frame.pack(fill="x")

        tk.Label(filter_frame, text="Show:", font=("Helvetica Neue", 11),
                 bg="#f5f5f0", fg="#666").pack(side="left")

        self.filter_btns = {}
        for mode in ("all", "active", "done"):
            btn = tk.Button(filter_frame, text=mode.capitalize(),
                            font=("Helvetica Neue", 11), relief="flat", padx=12, pady=4,
                            cursor="hand2", bg="#e8e8f0", fg="#555",
                            command=lambda m=mode: self._set_filter(m))
            btn.pack(side="left", padx=4)
            self.filter_btns[mode] = btn

        # Search
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._refresh_list())
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var,
                                font=("Helvetica Neue", 11), relief="flat", bd=0,
                                highlightthickness=1, highlightbackground="#cccccc",
                                bg="white", width=18)
        search_entry.pack(side="right", ipady=5, padx=(0, 0))
        tk.Label(filter_frame, text="🔍", bg="#f5f5f0", font=("Helvetica Neue", 12)
                 ).pack(side="right", padx=(8, 2))

        # Task list with scrollbar
        list_frame = tk.Frame(self.root, bg="#f5f5f0", padx=20)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(list_frame, font=("Helvetica Neue", 13),
                                  selectbackground="#6c63ff", selectforeground="white",
                                  activestyle="none", relief="flat", bd=0,
                                  highlightthickness=0, bg="white",
                                  yscrollcommand=scrollbar.set,
                                  selectmode="single", cursor="hand2")
        self.listbox.pack(fill="both", expand=True, pady=(0, 8))
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<Double-Button-1>", lambda e: self._toggle_done())

        # Bottom action bar
        action_frame = tk.Frame(self.root, bg="#f5f5f0", pady=12, padx=20)
        action_frame.pack(fill="x")

        btn_style = dict(font=("Helvetica Neue", 12), relief="flat",
                         padx=16, pady=6, cursor="hand2")

        tk.Button(action_frame, text="✔ Mark Done", bg="#28a745", fg="white",
                  activebackground="#1e7e34", activeforeground="white",
                  command=self._toggle_done, **btn_style).pack(side="left", padx=(0, 8))

        tk.Button(action_frame, text="✏ Edit", bg="#fd7e14", fg="white",
                  activebackground="#dc6502", activeforeground="white",
                  command=self._edit_task, **btn_style).pack(side="left", padx=(0, 8))

        tk.Button(action_frame, text="🗑 Delete", bg="#dc3545", fg="white",
                  activebackground="#bd2130", activeforeground="white",
                  command=self._delete_task, **btn_style).pack(side="left")

        tk.Button(action_frame, text="Clear Done", bg="#aaaaaa", fg="white",
                  activebackground="#888888", activeforeground="white",
                  command=self._clear_done, **btn_style).pack(side="right")

        self._set_filter("all")

    # ── HELPERS ──────────────────────────────────────────────────────────────

    def _priority_color(self, priority):
        return {"High": "#e74c3c", "Medium": "#f39c12", "Low": "#27ae60"}.get(priority, "#999")

    def _priority_tag(self, priority):
        return {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(priority, "⚪")

    def _clear_placeholder(self, e):
        if self.due_entry.get() == "YYYY-MM-DD":
            self.due_entry.delete(0, "end")
            self.due_entry.config(fg="#333")

    def _restore_placeholder(self, e):
        if not self.due_entry.get():
            self.due_entry.insert(0, "YYYY-MM-DD")
            self.due_entry.config(fg="#aaa")

    def _get_selected_index(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        listbox_idx = sel[0]
        return self.visible_indices[listbox_idx]

    # ── FILTER ───────────────────────────────────────────────────────────────

    def _set_filter(self, mode):
        self.filter_mode = mode
        for m, btn in self.filter_btns.items():
            if m == mode:
                btn.config(bg="#6c63ff", fg="white")
            else:
                btn.config(bg="#e8e8f0", fg="#555")
        self._refresh_list()

    # ── REFRESH LIST ─────────────────────────────────────────────────────────

    def _refresh_list(self):
        self.listbox.delete(0, "end")
        self.visible_indices = []
        query = self.search_var.get().lower() if hasattr(self, "search_var") else ""

        for i, task in enumerate(self.tasks):
            if self.filter_mode == "active" and task["done"]:
                continue
            if self.filter_mode == "done" and not task["done"]:
                continue
            if query and query not in task["name"].lower():
                continue

            done_mark = "✓" if task["done"] else " "
            tag = self._priority_tag(task.get("priority", "Medium"))
            due = f"  📅 {task['due']}" if task.get("due") else ""
            added = f"  · added {task.get('added', '')}"
            label = f"  [{done_mark}] {tag} {task['name']}{due}{added}"

            self.listbox.insert("end", label)
            if task["done"]:
                self.listbox.itemconfig("end", fg="#aaaaaa")
            self.visible_indices.append(i)

        done_count = sum(1 for t in self.tasks if t["done"])
        total = len(self.tasks)
        self.subtitle_var.set(f"{total} tasks · {done_count} completed · {total - done_count} remaining")

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def _add_task(self):
        name = self.task_entry.get().strip()
        if not name:
            messagebox.showwarning("Empty task", "Please enter a task name.")
            return

        due = self.due_entry.get().strip()
        if due == "YYYY-MM-DD":
            due = ""

        self.tasks.append({
            "name": name,
            "done": False,
            "priority": self.priority_var.get(),
            "due": due,
            "added": datetime.now().strftime("%b %d")
        })
        save_tasks(self.tasks)
        self.task_entry.delete(0, "end")
        self.due_entry.delete(0, "end")
        self.due_entry.insert(0, "YYYY-MM-DD")
        self.due_entry.config(fg="#aaa")
        self.priority_var.set("Medium")
        self._refresh_list()

    def _toggle_done(self):
        idx = self._get_selected_index()
        if idx is None:
            messagebox.showinfo("Select a task", "Please click a task first.")
            return
        self.tasks[idx]["done"] = not self.tasks[idx]["done"]
        save_tasks(self.tasks)
        self._refresh_list()

    def _delete_task(self):
        idx = self._get_selected_index()
        if idx is None:
            messagebox.showinfo("Select a task", "Please click a task first.")
            return
        name = self.tasks[idx]["name"]
        if messagebox.askyesno("Delete task", f"Delete '{name}'?"):
            self.tasks.pop(idx)
            save_tasks(self.tasks)
            self._refresh_list()

    def _edit_task(self):
        idx = self._get_selected_index()
        if idx is None:
            messagebox.showinfo("Select a task", "Please click a task to edit.")
            return

        task = self.tasks[idx]
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Task")
        edit_win.geometry("400x220")
        edit_win.configure(bg="#f5f5f0")
        edit_win.grab_set()

        tk.Label(edit_win, text="Edit Task", font=("Helvetica Neue", 15, "bold"),
                 bg="#f5f5f0").pack(pady=(16, 10))

        tk.Label(edit_win, text="Task name:", font=("Helvetica Neue", 11), bg="#f5f5f0").pack()
        name_entry = tk.Entry(edit_win, font=("Helvetica Neue", 13), width=36,
                              relief="flat", highlightthickness=1,
                              highlightbackground="#cccccc", bg="white")
        name_entry.insert(0, task["name"])
        name_entry.pack(ipady=6, pady=4)

        tk.Label(edit_win, text="Due date:", font=("Helvetica Neue", 11), bg="#f5f5f0").pack()
        due_entry = tk.Entry(edit_win, font=("Helvetica Neue", 13), width=36,
                             relief="flat", highlightthickness=1,
                             highlightbackground="#cccccc", bg="white")
        due_entry.insert(0, task.get("due", ""))
        due_entry.pack(ipady=6, pady=4)

        def save_edit():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Empty", "Task name cannot be empty.")
                return
            self.tasks[idx]["name"] = new_name
            self.tasks[idx]["due"] = due_entry.get().strip()
            save_tasks(self.tasks)
            self._refresh_list()
            edit_win.destroy()

        tk.Button(edit_win, text="Save", font=("Helvetica Neue", 12, "bold"),
                  bg="#6c63ff", fg="white", relief="flat", padx=20, pady=6,
                  cursor="hand2", command=save_edit).pack(pady=10)

    def _clear_done(self):
        count = sum(1 for t in self.tasks if t["done"])
        if count == 0:
            messagebox.showinfo("Nothing to clear", "No completed tasks.")
            return
        if messagebox.askyesno("Clear done", f"Remove {count} completed task(s)?"):
            self.tasks = [t for t in self.tasks if not t["done"]]
            save_tasks(self.tasks)
            self._refresh_list()


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
