import customtkinter as ctk
import json
import os
import random
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DATA_FILE = "flashter_data.json"

class FlashterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FLASHTER")
        self.geometry("800x600")

        self.study_sets = {}
        self.quiz_scores = {}
        self.load_data()

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.title_label = ctk.CTkLabel(self.main_frame, text="FLASHTER", font=("Impact", 36))
        self.title_label.pack(pady=20)


        self.mode_toggle = ctk.CTkSwitch(self.main_frame, text="Dark Mode", command=self.toggle_mode)
        self.mode_toggle.pack(pady=10)

        self.content_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.content_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.back_button = ctk.CTkButton(self.main_frame, text="Back", command=self.create_main_menu)
        self.create_main_menu()

    def toggle_mode(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
                self.study_sets = data.get("study_sets", {})
                self.quiz_scores = data.get("quiz_scores", {})

    def save_data(self):
        with open(DATA_FILE, "w") as file:
            json.dump({"study_sets": self.study_sets, "quiz_scores": self.quiz_scores}, file, indent=4)

    def create_main_menu(self):
        self.clear_frame(self.content_frame)
        self.back_button.pack_forget()

        buttons = [
            ("Create Flashcard Set", self.create_flashcard_set),
            ("Access Flashcard Sets", self.access_flashcard_sets),
            ("Take Quiz", self.show_choose_quiz_set),
            ("View Progress", self.show_progress),
            ("Exit", self.quit)
        ]

        for text, command in buttons:
            button = ctk.CTkButton(self.content_frame, text=text, command=command)
            button.pack(pady=10)

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def create_flashcard_set(self):
        self.clear_frame(self.content_frame)
        self.back_button.pack(side="top")

        set_name_label = ctk.CTkLabel(self.content_frame, text="Set Name:")
        set_name_label.pack()
        set_name_entry = ctk.CTkEntry(self.content_frame)
        set_name_entry.pack()

        flashcards = []
        flashcard_list = ctk.CTkTextbox(self.content_frame, height=200, width=300, state="disabled")
        flashcard_list.pack()

        def add_flashcard():
            question, answer = question_entry.get(), answer_entry.get()
            if question and answer:
                flashcards.append({"question": question, "answer": answer})
                question_entry.delete(0, 'end')
                answer_entry.delete(0, 'end')
                flashcard_list.configure(state="normal")
                flashcard_list.insert("end", f"Q: {question}\nA: {answer}\n\n")
                flashcard_list.configure(state="disabled")

        question_label = ctk.CTkLabel(self.content_frame, text="Question:")
        question_label.pack()
        question_entry = ctk.CTkEntry(self.content_frame)
        question_entry.pack()

        answer_label = ctk.CTkLabel(self.content_frame, text="Answer:")
        answer_label.pack()
        answer_entry = ctk.CTkEntry(self.content_frame)
        answer_entry.pack()

        ctk.CTkButton(self.content_frame, text="Add Flashcard", command=add_flashcard).pack()
        ctk.CTkButton(self.content_frame, text="Save Set", command=lambda: self.save_flashcard_set(set_name_entry.get(), flashcards)).pack()

    def save_flashcard_set(self, set_name, flashcards):
        if set_name and flashcards:
            self.study_sets[set_name] = flashcards
            self.save_data()
            self.create_main_menu()

    def access_flashcard_sets(self):
        self.clear_frame(self.content_frame)
        self.back_button.pack(side="top")

        for set_name in self.study_sets:
            ctk.CTkButton(self.content_frame, text=set_name, command=lambda name=set_name: self.view_flashcard_set(name)).pack(pady=5)

    def view_flashcard_set(self, set_name):
        self.clear_frame(self.content_frame)
        self.back_button.pack(side="top")

        flashcards = self.study_sets[set_name]
        current_card = 0

        card_text = ctk.CTkLabel(self.content_frame, text="", font=("Arial", 18))
        card_text.pack()

        def show_card(index, show_answer=False):
            card = flashcards[index]
            card_text.configure(text=f"A: {card['answer']}" if show_answer else f"Q: {card['question']}")

        ctk.CTkButton(self.content_frame, text="Flip", command=lambda: show_card(current_card, True)).pack()
        show_card(current_card)

    def show_choose_quiz_set(self):
        self.clear_frame(self.content_frame)
        self.back_button.pack(side="top")

        for set_name in self.study_sets:
            ctk.CTkButton(self.content_frame, text=f"Quiz: {set_name}",
                          command=lambda name=set_name: self.take_quiz(name)).pack(pady=5)

    def take_quiz(self, set_name):
        self.clear_frame(self.content_frame)
        self.back_button.pack(side="top")

        flashcards = self.study_sets[set_name]
        random.shuffle(flashcards)
        total_questions = len(flashcards)
        current_question, score = 0, 0

        question_label = ctk.CTkLabel(self.content_frame, text="", font=("Arial", 16))
        question_label.pack()
        answer_entry = ctk.CTkEntry(self.content_frame)
        answer_entry.pack()

        def check_answer():
            nonlocal current_question, score
            if answer_entry.get().strip().lower() == flashcards[current_question]["answer"].lower():
                score += 1
            current_question += 1
            if current_question < total_questions:
                question_label.configure(text=flashcards[current_question]["question"])
            else:
                messagebox.showinfo("Quiz Completed", f"Score: {score}/{total_questions}")
                self.quiz_scores[set_name] = score
                self.save_data()
                self.create_main_menu()

        ctk.CTkButton(self.content_frame, text="Submit", command=check_answer).pack()
        question_label.configure(text=flashcards[current_question]["question"])

    def show_progress(self):
        self.clear_frame(self.content_frame)
        self.back_button.pack(side="top")

        if not self.quiz_scores:
            ctk.CTkLabel(self.content_frame, text="No progress data available").pack()
            return

        fig, ax = plt.subplots(figsize=(5, 3))
        sets = list(self.quiz_scores.keys())
        scores = list(self.quiz_scores.values())

        ax.bar(sets, scores, color="blue")
        ax.set_xlabel("Flashcard Sets")
        ax.set_ylabel("Score")
        ax.set_title("Quiz Scores")

        canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    app = FlashterApp()
    app.mainloop()
