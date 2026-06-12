import tkinter as tk
from tkinter import messagebox
import random
import time

LETTERS = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
WORD_COLORS = ["#e15881", "#83e8dc", "#8800ff", "#95c2f4", "#7836e9", "#6071ad", "#4dc696", "#0ea463"]

WORDS = [
    "КОТ", "ДОМ", "ЛЕС", "СОЛНЦЕ", "ЛУНА", "ЗВЕЗДА", "МОРЕ", "ГОРА", "РЕКА", "ПОЛЕ", "КОЛЕСО", "РАСХОД", "СНЕГИРЬ",
    "ПИТОН", "АЛГОРИТМ", "ПРОГРАММА", "КОМПЬЮТЕР", "РАЗРАБОТЧИК", "ИНТЕРФЕЙС", "МЕСЯЦ", "БАСКЕТБОЛ", "ФУТБОЛ", "ФАКЕЛ", "РАКУШКА",
    "СОБАКА", "КОШКА", "ЗАЯЦ", "ЛИСА", "ВОЛК", "МЕДВЕДЬ", "ТИГР", "ЛЕВ", "ЙОГУРТ", "ПЛАСТИЛИН", "ТОПОТ", "РАЗУМ", "СУФЛЕ", "ПОЧВА",
    "МАШИНА", "САМОЛЕТ", "ПОЕЗД", "КОРАБЛЬ", "ВЕЛОСИПЕД", "АВТОБУС", "ПИТОМЕЦ", "МЫЛО", "УЮТ", "КЛЮКВА", "УЗЕЛ", "ГОСТЬ", "КУСТ",
    "ВЕСНА", "ЛЕТО", "ОСЕНЬ", "ЗИМА", "МАМА", "ПАПА", "БРАТ", "СЕСТРА", "ХОККЕЙ", "ЗВЕЗДА", "КАМЕРА", "МОРЯК", "ВОКЗАЛ", "ЛИМОНАД",
    "СЧАСТЬЕ", "ЛЮБОВЬ", "КИТ", "ЛЕД", "ФИГУРА", "ЗОЛА", "САПФИР", "ГРАМОТА", "ДРУЖБА", "МИР", "ХЛЕБ", "МОЛОКО", "УЧИТЕЛЬ", "КНИГА", "РУЧКА", "ТЕТРАДЬ", "СТУЛ", "СТОЛ", "ОКНО", "ДВЕРЬ", "БЕЛКА", "ОПЫТ", "ТЕЛЕФОН", "РОБОТ", "ФУТБОЛ", "ХОККЕЙ", "МУЗЫКА", "ПЕСНЯ", "ДЕРЕВО"
]

DIRECTIONS = [(0, 1), (1, 0), (-1, 0)]

LEVEL_CONFIG = {}
for i in range(1, 101):
    if i <= 20:
        size = 6
        count = 5 + (i // 4)
    elif i <= 40:
        size = 7
        count = 6 + (i // 5)
    elif i <= 60:
        size = 8
        count = 7 + (i // 6)
    elif i <= 80:
        size = 9
        count = 8 + (i // 7)
    else:
        size = 10
        count = 9 + (i // 8)
    LEVEL_CONFIG[i] = {"size": size, "count": min(count, 12)}


class WordSearchGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Филворды - Поиск слов")
        self.root.geometry("1100x820")
        self.root.configure(bg="#f8f9fa")

        self.level = 1
        self.size = 6
        self.words = []
        self.field = []
        self.placed = []
        self.found = {}
        self.word_colors = {}
        self.selected_cells = []
        self.current_highlight_color = "#a8e6cf"
        self.cell_rects = {}
        self.cell_size = 50
        self.start_time = None
        self.timer_id = None
        self.hints_left = 10
        self.menu_frame = None
        self.game_frame = None
        self.word_labels = {}  

        self.show_main_menu()

    def show_main_menu(self):
        if self.game_frame: self.game_frame.destroy()
        if self.menu_frame: self.menu_frame.destroy()

        self.menu_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.menu_frame.pack(fill="both", expand=True)

        tk.Button(self.menu_frame, text="⚙ Настройки", font=("Arial", 10),
                  bg="#ecf0f1", fg="#2c3e50", relief="flat",
                  command=self.open_settings).pack(anchor="ne", padx=20, pady=10)

        title = tk.Label(self.menu_frame, text="ГОЛОВОЛОМКА:\nПОИСК СЛОВ",
                         font=("Arial", 36, "bold"), bg="#f8f9fa", fg="#2c3e50", justify="center")
        title.pack(pady=80)

        level_text = tk.Label(self.menu_frame, text=f"ТЕКУЩИЙ УРОВЕНЬ\n{self.level}",
                              font=("Arial", 20, "bold"), bg="#f8f9fa", fg="#34495e")
        level_text.pack(pady=30)

        play_btn = tk.Button(self.menu_frame, text="ИГРАТЬ (PLAY) ▶",
                             font=("Arial", 18, "bold"), bg="#2c3e50", fg="white",
                             width=22, height=2, relief="flat", command=self.start_game)
        play_btn.pack(pady=40)

    def open_settings(self):
        messagebox.showinfo("Настройки", "Настройки пока в разработке")

    def start_game(self):
        if self.menu_frame:
            self.menu_frame.destroy()
        self.create_game_ui()
        self.new_game()

    def back_to_menu(self):
        if messagebox.askyesno("Меню", "Вернуться в главное меню?"):
            self.stop_timer()
            if self.game_frame:
                self.game_frame.destroy()
            self.show_main_menu()

    def create_game_ui(self):
        self.game_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.game_frame.pack(fill="both", expand=True)

        tk.Label(self.game_frame, text="ФИЛВОРДЫ", font=("Arial", 28, "bold"),
                 bg="#f8f9fa", fg="#2c3e50").pack(pady=8)

        game_area = tk.Frame(self.game_frame, bg="#f8f9fa")
        game_area.pack(fill="both", expand=True, padx=30, pady=10)

        self.canvas = tk.Canvas(game_area, bg="#ffffff", highlightthickness=4,
                                highlightbackground="#2c3e50", relief="solid")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Configure>", self.on_resize)

        words_panel = tk.Frame(game_area, bg="#ffffff", relief="solid", bd=2)
        words_panel.pack(fill="x", pady=(15, 0))

        tk.Label(words_panel, text="НАЙДИ ЭТИ СЛОВА", font=("Arial", 16, "bold"),
                 bg="#ffffff", fg="#2c3e50").pack(pady=12)

        self.words_container = tk.Frame(words_panel, bg="#ffffff")
        self.words_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        side_panel = tk.Frame(game_area, bg="#f8f9fa", width=260)
        side_panel.pack(side="right", fill="y", padx=(20, 0))
        side_panel.pack_propagate(False)

        self.timer_label = tk.Label(side_panel, text="Время: 00:00",
                                    font=("Arial", 16, "bold"), bg="#f8f9fa", fg="#e74c3c")
        self.timer_label.pack(pady=12)

        self.hints_label = tk.Label(side_panel, text=f"Подсказки: {self.hints_left}",
                                    font=("Arial", 13, "bold"), bg="#f8f9fa", fg="#e67e22")
        self.hints_label.pack(pady=8)

        btn_frame = tk.Frame(side_panel, bg="#f8f9fa")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Заново", font=("Arial", 11), bg="#3498db",
                  fg="white", width=14, command=self.reset_level).pack(pady=5)
        tk.Button(btn_frame, text="Подсказка", font=("Arial", 11), bg="#f39c12",
                  fg="white", width=14, command=self.hint).pack(pady=5)

        bottom_bar = tk.Frame(self.game_frame, bg="#f8f9fa")
        bottom_bar.pack(fill="x", pady=12)

        self.level_label = tk.Label(bottom_bar, text="Уровень 1 / 100", 
                                    font=("Arial", 13), bg="#f8f9fa", fg="#2c3e50")
        self.level_label.pack(side="left", padx=30)

        self.found_label = tk.Label(bottom_bar, text="Найдено: 0/0", 
                                    font=("Arial", 13), bg="#f8f9fa", fg="#2c3e50")
        self.found_label.pack(side="left", padx=30)

        tk.Button(bottom_bar, text="ГЛАВНОЕ МЕНЮ", font=("Arial", 12, "bold"),
                  bg="#95a5a6", fg="white", command=self.back_to_menu).pack(side="right", padx=30)

    def update_word_list(self):
        for widget in self.words_container.winfo_children():
            widget.destroy()
        
        self.word_labels = {}
        for idx, word in enumerate(self.words):
            frame = tk.Frame(self.words_container, bg="#ffffff")
            frame.pack(fill="x", pady=4, padx=10)
            
            check = tk.Label(frame, text="✓" if self.found.get(word, False) else "  ",
                             font=("Arial", 14, "bold"), bg="#ffffff", fg="#2ecc71", width=2)
            check.pack(side="left")
            
            lbl = tk.Label(frame, text=word, font=("Arial", 14),
                           bg="#ffffff", fg="#2c3e50", anchor="w")
            lbl.pack(side="left", padx=5)
            
            self.word_labels[word] = (check, lbl)

    def update_ui(self):
        self.level_label.config(text=f"Уровень {self.level} / 100")
        found_cnt = sum(self.found.values())
        self.found_label.config(text=f"Найдено: {found_cnt}/{len(self.words)}")
        self.update_word_list()

    def start_timer(self):
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Время: {elapsed//60:02d}:{elapsed%60:02d}")
            self.timer_id = self.root.after(1000, self.update_timer)

    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def get_random_words(self):
        available = [w for w in WORDS if len(w) <= self.size]   # ← ИСПРАВЛЕНО
        random.shuffle(available)
        count = LEVEL_CONFIG.get(self.level, {"count": 6})["count"]
        return available[:count]

    def update_size_by_level(self):
        self.size = LEVEL_CONFIG.get(self.level, {"size": 6})["size"]

    def generate_field(self):
        max_attempts = 5000
        self.field = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        self.placed = []
        used_positions = set()

        for word in self.words:
            placed_ok = False
            for _ in range(max_attempts):
                dr, dc = random.choice(DIRECTIONS)
                if dr == 0 and dc == 1:
                    row = random.randint(0, self.size - 1)
                    col = random.randint(0, self.size - len(word))
                elif dr == 1 and dc == 0:
                    row = random.randint(0, self.size - len(word))
                    col = random.randint(0, self.size - 1)
                else:
                    row = random.randint(len(word) - 1, self.size - 1)
                    col = random.randint(0, self.size - 1)

                can_place = True
                positions = []
                for i in range(len(word)):
                    r = row + i * dr
                    c = col + i * dc
                    positions.append((r, c))
                    if (r, c) in used_positions or (self.field[r][c] != ' ' and self.field[r][c] != word[i]):
                        can_place = False
                        break

                if can_place:
                    for i, ch in enumerate(word):
                        r, c = positions[i]
                        self.field[r][c] = ch
                        used_positions.add((r, c))
                    color = random.choice(WORD_COLORS)
                    self.placed.append((word, row, col, dr, dc, color))
                    self.word_colors[word] = color
                    placed_ok = True
                    break
            if not placed_ok:
                return self.generate_field()

        for i in range(self.size):
            for j in range(self.size):
                if self.field[i][j] == ' ':
                    self.field[i][j] = random.choice(LETTERS)

    def new_game(self):
        self.stop_timer()
        self.update_size_by_level()
        self.words = self.get_random_words()
        self.found = {w: False for w in self.words}
        self.word_colors = {}
        self.selected_cells = []
        self.generate_field()
        self.update_ui()
        self.draw_field()
        self.start_timer()

    def reset_level(self):
        self.stop_timer()
        self.selected_cells = []
        self.found = {w: False for w in self.words}
        self.word_colors = {}
        self.generate_field()
        self.update_ui()
        self.draw_field()
        self.start_timer()

    def update_hints_label(self):
        self.hints_label.config(text=f"Подсказки: {self.hints_left}")

    def draw_field(self):
        self.canvas.delete("all")
        if not self.field: return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.cell_size = max(38, min(72, min(w, h) // self.size - 10))

        total_w = self.cell_size * self.size
        total_h = self.cell_size * self.size
        offset_x = (w - total_w) // 2
        offset_y = (h - total_h) // 2

        self.cell_rects = {}
        for i in range(self.size):
            for j in range(self.size):
                x1 = offset_x + j * self.cell_size
                y1 = offset_y + i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if (i, j) in self.selected_cells:
                    color = self.current_highlight_color
                else:
                    color = None
                    for word, r0, c0, dr, dc, word_clr in self.placed:
                        if self.found.get(word, False):
                            for k in range(len(word)):
                                if r0 + k * dr == i and c0 + k * dc == j:
                                    color = word_clr
                                    break
                        if color: break
                    color = color or "#ecf0f1"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#2c3e50", width=2)
                self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                        text=self.field[i][j],
                                        font=("Arial", self.cell_size//2 + 3, "bold"),
                                        fill="#2c3e50")
                self.cell_rects[(i, j)] = (x1, y1, x2, y2)

    def get_word_from_cells(self, cells):
        if len(cells) < 2: return None
        rows = [p[0] for p in cells]
        cols = [p[1] for p in cells]

        if len(set(rows)) == 1:
            r = rows[0]
            sorted_cells = sorted(cells, key=lambda x: x[1])
            word = ''.join(self.field[r][c] for (r, c) in sorted_cells)
            if word in self.found: return word
            if word[::-1] in self.found: return word[::-1]

        if len(set(cols)) == 1:
            c = cols[0]
            sorted_cells = sorted(cells, key=lambda x: x[0])
            word = ''.join(self.field[r][c] for (r, c) in sorted_cells)
            if word in self.found: return word
            if word[::-1] in self.found: return word[::-1]
        return None

    def on_mouse_down(self, e):
        self.selected_cells = []
        self.current_highlight_color = random.choice(WORD_COLORS)
        self.mouse_select(e)

    def on_mouse_drag(self, e):
        self.mouse_select(e)

    def on_mouse_up(self, e):
        if len(self.selected_cells) >= 2:
            word = self.get_word_from_cells(self.selected_cells)
            if word and word in self.found and not self.found[word]:
                self.found[word] = True
                self.word_colors[word] = self.current_highlight_color
                for i, item in enumerate(self.placed):
                    if item[0] == word:
                        self.placed[i] = (*item[:5], self.current_highlight_color)
                        break
                self.update_ui()
                self.draw_field()

                if all(self.found.values()):
                    self.stop_timer()
                    self.hints_left += 1
                    self.update_hints_label()
                    self.root.after(600, self.next_level_auto)

        self.selected_cells = []
        self.draw_field()

    def mouse_select(self, e):
        x, y = e.x, e.y
        for (r, c), (x1, y1, x2, y2) in self.cell_rects.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                if self.is_cell_used_in_found_word(r, c):
                    return
                if not self.selected_cells:
                    self.selected_cells = [(r, c)]
                else:
                    last = self.selected_cells[-1]
                    if ((r == last[0] and abs(c - last[1]) == 1) or
                        (c == last[1] and abs(r - last[0]) == 1)):
                        if (r, c) not in self.selected_cells:
                            self.selected_cells.append((r, c))
                self.draw_field()
                return

    def is_cell_used_in_found_word(self, r, c):
        for word, r0, c0, dr, dc, _ in self.placed:
            if self.found.get(word, False):
                for k in range(len(word)):
                    if r0 + k * dr == r and c0 + k * dc == c:
                        return True
        return False

    def clear_hint(self):
        self.selected_cells = []
        self.draw_field()

    def hint(self):
        if self.hints_left <= 0:
            messagebox.showinfo("Подсказки", "Подсказки закончились!")
            return
        for word in self.words:
            if not self.found[word]:
                for r in range(self.size):
                    for c in range(self.size):
                        if self.field[r][c] == word[0] and not self.is_cell_used_in_found_word(r, c):
                            self.selected_cells = [(r, c)]
                            self.current_highlight_color = "#3e3479"
                            self.draw_field()
                            self.root.after(1600, self.clear_hint)
                            self.hints_left -= 1
                            self.update_hints_label()
                            return

    def next_level_auto(self):
        if self.level < 100:
            self.level += 1
            self.new_game()
        else:
            if messagebox.askyesno("Победа!", "Вы прошли все 100 уровней!\nНачать сначала?"):
                self.level = 1
                self.hints_left = 10
                self.new_game()

    def on_resize(self, e):
        self.draw_field()


if __name__ == "__main__":
    root = tk.Tk()
    game = WordSearchGame(root)
    root.mainloop()