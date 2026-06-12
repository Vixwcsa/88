import tkinter as tk
import random

LETTERS = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
WORDS = ["КОТ", "ДОМ", "ЛЕС", "СОЛНЦЕ", "МОРЕ"]

class WordSearchGame:
    def __init__(self, root):
        self.root = root
        self.root.title("ФИЛВОРДЫ")
        self.root.geometry("900x700")
        self.size = 8
        self.field = []
        self.words = WORDS
        self.canvas = tk.Canvas(root, bg="#ffffff")
        self.canvas.pack(fill="both", expand=True)
        self.generate_field()
        self.draw_field()

    def generate_field(self):
        self.field = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        for word in self.words:
            row = random.randint(0, self.size-1)
            col = random.randint(0, self.size-len(word))
            for i, ch in enumerate(word):
                self.field[row][col+i] = ch
        for i in range(self.size):
            for j in range(self.size):
                if self.field[i][j] == ' ':
                    self.field[i][j] = random.choice(LETTERS)

    def draw_field(self):
        self.canvas.delete("all")
        cell_size = 60
        for i in range(self.size):
            for j in range(self.size):
                x1 = j * cell_size + 50
                y1 = i * cell_size + 50
                self.canvas.create_rectangle(x1, y1, x1+cell_size, y1+cell_size, outline="#333")
                self.canvas.create_text(x1+30, y1+30, text=self.field[i][j], font=("Arial", 20, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    game = WordSearchGame(root)
    root.mainloop()
