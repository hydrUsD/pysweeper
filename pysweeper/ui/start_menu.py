import tkinter as tk

from pysweeper.difficulty_config import DifficultyConfig


class StartMenu(tk.Frame):
    def __init__(self, master, ui_names: list[str], difficulties: list[DifficultyConfig]):
        super().__init__(master, padx=16, pady=12)
        self.ui_names = ui_names
        self.difficulties = difficulties
        self.ui_choice = tk.StringVar(master=self, value=ui_names[0])
        self.difficulty_choice = tk.StringVar(master=self, value=difficulties[0].name)
        self.selection = None
        self._create_widgets()

    def _create_widgets(self) -> None:
        uis = tk.LabelFrame(self, text="Oberfläche")
        uis.pack(fill="x")
        for name in self.ui_names:
            tk.Radiobutton(uis, text=name, value=name, variable=self.ui_choice).pack(anchor="w")
        levels = tk.LabelFrame(self, text="Schwierigkeit")
        levels.pack(fill="x", pady=8)
        for d in self.difficulties:
            label = f"{d.name}  {d.size[0]}x{d.size[1]}, {d.amount} Minen"
            tk.Radiobutton(levels, text=label, value=d.name, variable=self.difficulty_choice).pack(anchor="w")
        self.start_button = tk.Button(self, text="Start", command=self._on_start)
        self.start_button.pack()

    def _on_start(self) -> None:
        difficulty = next(d for d in self.difficulties if d.name == self.difficulty_choice.get())
        self.selection = (self.ui_choice.get(), difficulty)
        self.master.destroy()

    def run(self):
        self.pack()
        self.master.mainloop()
        return self.selection
