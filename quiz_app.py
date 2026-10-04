import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import random
import csv
import os
import sys

from pathlib import Path
from datetime import datetime


def resource_path(filename):
    """หาไฟล์ที่มากับโปรแกรม เช่น questions.json"""
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / filename


def get_app_data_folder():
    """สร้างโฟลเดอร์สำหรับเก็บข้อมูลคะแนนของผู้ใช้"""
    appdata = os.getenv("APPDATA")

    if appdata:
        folder = Path(appdata) / "QuizGame"
    else:
        folder = Path.home() / ".quizgame"

    folder.mkdir(parents=True, exist_ok=True)

    return folder


QUESTIONS_FILE = resource_path("questions.json")
SCORES_FILE = get_app_data_folder() / "scores.csv"


def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_score(name, score, total):
    with open(SCORES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name,
            score,
            total
        ])


def load_scores():
    if not SCORES_FILE.exists():
        return []

    with open(SCORES_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)


class QuizGame:
    def __init__(self, master):
        self.master = master

        self.master.title("🎮 Quiz Game")
        self.master.geometry("700x500")
        self.master.configure(bg="#f0f8ff")

        self.show_main_menu()

    def show_main_menu(self):
        self.clear_window()

        self.master.configure(bg="#e6f7ff")

        tk.Label(
            self.master,
            text="🧠 QUIZ GAME",
            font=("Arial Black", 28),
            bg="#e6f7ff",
            fg="#1c4e80"
        ).pack(pady=40)

        tk.Button(
            self.master,
            text="▶️ เริ่มเกม",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2,
            command=self.start_game
        ).pack(pady=10)

        tk.Button(
            self.master,
            text="❌ ออก",
            font=("Arial", 14),
            bg="#f44336",
            fg="white",
            width=20,
            command=self.master.quit
        ).pack(pady=10)

    def start_game(self):
        self.score = 0
        self.q_index = 0

        try:
            self.questions = load_questions()
        except FileNotFoundError:
            messagebox.showerror(
                "Error",
                "ไม่พบไฟล์ questions.json"
            )
            return

        except json.JSONDecodeError:
            messagebox.showerror(
                "Error",
                "ข้อมูลใน questions.json ไม่ถูกต้อง"
            )
            return

        if not self.questions:
            messagebox.showerror(
                "Error",
                "ไม่มีคำถามใน questions.json"
            )
            return

        random.shuffle(self.questions)

        self.show_question()

    def show_question(self):
        self.clear_window()

        self.master.configure(bg="#fffbe6")

        if self.q_index < len(self.questions):
            self.current_q = self.questions[self.q_index]

            tk.Label(
                self.master,
                text=f"ข้อที่ {self.q_index + 1}:",
                font=("Arial", 18, "bold"),
                bg="#fffbe6",
                fg="#ff8c00"
            ).pack(pady=10)

            tk.Label(
                self.master,
                text=self.current_q["question"],
                font=("Arial", 16),
                wraplength=600,
                bg="#fffbe6"
            ).pack(pady=10)

            for i, option in enumerate(self.current_q["options"]):
                tk.Button(
                    self.master,
                    text=option,
                    font=("Arial", 14),
                    bg="#2196F3",
                    fg="white",
                    width=50,
                    command=lambda i=i: self.check_answer(i)
                ).pack(pady=5)

        else:
            self.end_game()

    def check_answer(self, selected):
        correct_answer = self.current_q["answer"] - 1

        if selected == correct_answer:
            self.score += 1

        self.q_index += 1

        self.show_question()

    def end_game(self):
        name = simpledialog.askstring(
            "ชื่อผู้เล่น",
            f"คุณได้ {self.score}/{len(self.questions)} คะแนน\n"
            "กรุณาใส่ชื่อ:"
        )

        if name:
            save_score(
                name,
                self.score,
                len(self.questions)
            )

        self.show_scoreboard()

    def show_scoreboard(self):
        self.clear_window()

        self.master.configure(bg="#f0fff0")

        tk.Label(
            self.master,
            text="📊 สรุปคะแนน",
            font=("Arial Black", 22),
            bg="#f0fff0",
            fg="#2e7d32"
        ).pack(pady=10)

        scores = load_scores()

        if not scores:
            tk.Label(
                self.master,
                text="ยังไม่มีคะแนน",
                font=("Arial", 14),
                bg="#f0fff0"
            ).pack(pady=10)

        else:
            frame = tk.Frame(
                self.master,
                bg="#f0fff0"
            )

            frame.pack()

            for row in scores[-10:]:
                if len(row) >= 4:
                    text = (
                        f"{row[1]} ได้ {row[2]}/{row[3]} คะแนน "
                        f"เมื่อ {row[0]}"
                    )

                    tk.Label(
                        frame,
                        text=text,
                        font=("Arial", 12),
                        bg="#f0fff0",
                        anchor="w"
                    ).pack(pady=2)

        tk.Button(
            self.master,
            text="เล่นใหม่",
            font=("Arial", 13),
            bg="#03a9f4",
            fg="white",
            width=20,
            command=self.start_game
        ).pack(pady=8)

        tk.Button(
            self.master,
            text="กลับเมนูหลัก",
            font=("Arial", 13),
            bg="#8e44ad",
            fg="white",
            width=20,
            command=self.show_main_menu
        ).pack(pady=8)

        tk.Button(
            self.master,
            text="ลบคะแนนทั้งหมด",
            font=("Arial", 13),
            bg="#e53935",
            fg="white",
            width=20,
            command=self.clear_scores
        ).pack(pady=10)

    def clear_scores(self):
        confirm = messagebox.askyesno(
            "ยืนยัน",
            "คุณต้องการลบคะแนนทั้งหมดจริงหรือ?"
        )

        if confirm:
            with open(
                SCORES_FILE,
                "w",
                newline="",
                encoding="utf-8"
            ):
                pass

            messagebox.showinfo(
                "สำเร็จ",
                "ลบคะแนนทั้งหมดแล้ว"
            )

            self.show_scoreboard()

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()

    app = QuizGame(root)

    root.mainloop()