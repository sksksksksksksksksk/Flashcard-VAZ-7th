import sys
import json
import random
import tkinter as tk
from tkinter import filedialog, messagebox

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcard Study App")
        self.root.geometry("600x400")
        
        self.flashcards = []
        self.current_index = 0
        self.showing_question = True
        
        self.card = tk.Button(root, text="Click to Flip", font=("Arial", 20), bg="lightblue", command=self.flip_card)
        self.card.pack(expand=True, fill=tk.BOTH)
        
        self.quiz_input = tk.Entry(root)
        self.quiz_input.pack()
        
        self.quiz_button = tk.Button(root, text="Submit Answer", command=self.check_answer)
        self.quiz_button.pack()
        
        self.result_label = tk.Label(root, text="")
        self.result_label.pack()
        
        self.load_button = tk.Button(root, text="Load Study Set", command=self.load_study_set)
        self.load_button.pack()
        
        self.create_button = tk.Button(root, text="Create Study Set", command=self.create_study_set)
        self.create_button.pack()
        
        self.dark_mode = tk.BooleanVar()
        self.dark_mode_toggle = tk.Checkbutton(root, text="Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode)
        self.dark_mode_toggle.pack()
 

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
