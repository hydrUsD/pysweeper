"""Texte für hint() und explain(). Stufe 1 = Denkanstoß, 2 = Prinzip, 3 = konkreter Schritt."""

TITLES = {
    "l0": "Lektion 0 – Paketstruktur",
    "l1": "Lektion 1 – GameState & DifficultyConfig",
    "l2": "Lektion 2 – Cell",
    "l3": "Lektion 3 – Board Aufbau",
    "l4": "Lektion 4 – Board Verhalten",
    "l4_extra": "Lektion 4+ – Chording & Abfragen",
    "l5": "Lektion 5 – Game",
    "l5_extra": "Lektion 5+ – Timer & Minen-Zähler",
    "l6": "Lektion 6 – UserInterface & TerminalUI",
    "l7": "Lektion 7 – TkinterUI (Bonus)",
    "l8": "Lektion 8 – StartMenu",
    "l8_extra": "Lektion 8+ – Zurück ins Startmenü",
    "l9": "Lektion 9 – Offene und geschlossene Zellen",
    "l9_extra": "Lektion 9+ – Falsche Flaggen nach der Niederlage",
}

HINTS = {
    "l0": [
        "Woran erkennt Python, dass ein Ordner ein Paket ist und nicht nur ein Ordner voller Dateien?",
        "Jeder Paketordner braucht eine Datei __init__.py, auch wenn sie leer ist. Das gilt auch für "
        "Unterordner wie ui/. Dateinamen in Python sind snake_case: aus der Klasse DifficultyConfig wird "
        "difficulty_config.py.",
        "Im Terminal (Projekt-Root):\n"
        "    mkdir -p pysweeper/ui\n"
        "    touch pysweeper/__init__.py pysweeper/ui/__init__.py\n"
        "Danach die sieben Moduldateien aus der Aufgabe genauso mit touch anlegen "
        "(oder in PyCharm: Rechtsklick → New → Python Package / Python File).",
    ],
    "l1": [
        "Welche Java-Konstrukte entsprechen „feste Menge benannter Werte“ und „unveränderlicher "
        "Datenträger mit equals/hashCode“? Python hat für beides etwas in der Standardbibliothek.",
        "enum.Enum ist Javas enum. @dataclass(frozen=True) aus dem Modul dataclasses ist Javas record: "
        "Die Felder stehen als annotierte Klassenattribute im Rumpf, und __init__, __eq__, __repr__ "
        "werden generiert. Die Reihenfolge der Felder bestimmt die Reihenfolge der Konstruktor-Parameter.",
        "Gerüst (Werte selbst eintragen):\n"
        "    from dataclasses import dataclass\n\n"
        "    @dataclass(frozen=True)\n"
        "    class DifficultyConfig:\n"
        "        name: str\n"
        "        amount: int\n"
        "        size: tuple[int, int]   # (width, height)\n\n"
        "    EASY = DifficultyConfig(...)\n"
        "Achtung bei HARD: main.py speichert (rows, cols) = (16, 30), du brauchst (width, height).",
    ],
    "l2": [
        "Wo entstehen in Python die Attribute eines Objekts, wenn es keine Felddeklarationen wie in Java gibt?",
        "Attribute entstehen in __init__ durch Zuweisung an self (self ist Javas this, nur explizit als "
        "erster Parameter). Was direkt im Klassenrumpf steht, gehört der Klasse, also wie static in Java.",
        "Gerüst:\n"
        "    class Cell:\n"
        "        def __init__(self, x: int, y: int):\n"
        "            self.x = x\n"
        "            ...           # vier weitere Attribute mit Startwerten\n\n"
        "        def toggle_flag(self) -> None:\n"
        "            if ...:       # aufgedeckte Zellen nicht markieren\n"
        "                return\n"
        "            self.is_flagged = not self.is_flagged",
    ],
    "l3": [
        "Das Board besteht aus Zellen (Komposition, schwarze Raute im Diagramm). Wer erzeugt die Zellen, "
        "und in welcher Verschachtelung: erst Zeilen oder erst Spalten?",
        "grid[y][x]: Die äußere Liste hat height Einträge (Zeilen), jede innere width Zellen. Eine "
        "verschachtelte List Comprehension erzeugt jede Zelle einzeln. Für die Nachbarn lohnt sich ein "
        "privater Generator _neighbors(x, y), der mit yield alle gültigen (nx, ny) liefert. Den brauchst du "
        "in _plant_mines, _calculate_neighbors und später in der Cascade. random.sample(liste, k) zieht k "
        "verschiedene Elemente.",
        "Bausteine:\n"
        "    self.grid = [[Cell(x, y) for x in range(...)] for y in range(...)]\n\n"
        "    def _neighbors(self, x, y):\n"
        "        for dx in (-1, 0, 1):\n"
        "            for dy in (-1, 0, 1):\n"
        "                ...  # (0, 0) überspringen, Rand prüfen, dann yield nx, ny\n\n"
        "_plant_mines: safe = {(safe_x, safe_y), *self._neighbors(safe_x, safe_y)}, Kandidaten ohne safe "
        "(zu wenige? → nur die Startzelle ausschließen), random.sample, is_mine setzen, mines_planted = True.\n"
        "_calculate_neighbors: für jede Nicht-Mine neighbor_mines = sum(...) über _neighbors.",
    ],
    "l4": [
        "Geh deinen eigenen Ablauf durch: markiert? → aufdecken → Mine? Was muss zusätzlich passieren, "
        "wenn die aufgedeckte Zelle eine 0 ist, und warum darf das nicht rekursiv sein?",
        "Reihenfolge in reveal_cell: (1) Zelle markiert oder schon offen → False. (2) Noch keine Minen → "
        "_plant_mines + _calculate_neighbors. (3) _cascade_reveal(x, y) aufrufen. Die Cascade deckt die "
        "Startzelle selbst auf und läuft nur bei einer Nicht-Mine mit neighbor_mines == 0 weiter. (4) True.\n"
        "Die Cascade arbeitet mit einer Liste als Stack (append/pop) statt mit Rekursion: Python bricht nach "
        "ca. 1000 verschachtelten Aufrufen mit RecursionError ab. check_win zählt nur, verändert nichts.",
        "Cascade-Gerüst (vgl. main.py, reveal):\n"
        "    def _cascade_reveal(self, x, y):\n"
        "        stack = [(x, y)]               # die Startzelle selbst kommt zuerst dran\n"
        "        while stack:\n"
        "            cx, cy = stack.pop()\n"
        "            cell = self.grid[cy][cx]\n"
        "            if ...:                    # schon offen oder markiert → überspringen\n"
        "                continue\n"
        "            cell.is_revealed = True\n"
        "            if ...:                    # wann geht es bei den Nachbarn weiter?\n"
        "                stack.extend(...)\n"
        "Wichtig: reveal_cell deckt nicht selbst auf, das macht die Cascade. Sonst überspringt sie die "
        "Startzelle als „schon offen“, und es passiert nichts weiter.",
    ],
    "l4_extra": [
        "Chording ist ein Sonderfall von „Zelle ist schon offen“. Welche Bedingung muss gelten, bevor die "
        "Nachbarn aufgedeckt werden dürfen?",
        "Bedingung: Die Zelle ist eine offene Zahl (> 0, keine Mine), und die Anzahl markierter Nachbarn "
        "ist gleich neighbor_mines. Dann jeden verdeckten, unmarkierten Nachbarn aufdecken, inklusive "
        "Cascade. Lagere die Cascade in eine eigene Methode aus (_cascade_reveal steht im Diagramm!), dann "
        "kannst du sie wiederverwenden. flags_placed und mine_revealed() sind reine Abfragen mit sum()/any().",
        "Gerüst:\n"
        "    if cell.is_revealed:\n"
        "        return self._chord(x, y)          # gibt True zurück, wenn etwas aufging\n\n"
        "    def mine_revealed(self) -> bool:\n"
        "        return any(... for row in self.grid for c in row)   # welche Bedingung pro Zelle?\n\n"
        "    @property\n"
        "    def flags_placed(self) -> int: ...",
    ],
    "l5": [
        "Game ist der Controller: Es entscheidet über den Spielzustand, das Board macht die Arbeit. "
        "Welche Information braucht Game vom Board, um nach einem Zug LOST oder WON zu setzen?",
        "Game.__init__ baut aus difficulty.size = (width, height) und difficulty.amount ein Board. Lege das "
        "Erzeugen in reset_board(), dann nutzen __init__ und set_difficulty es mit. reveal/toggle_flag "
        "machen nur im Zustand PLAYING etwas (früher return, sog. Guard Clause).",
        "Gerüst für reveal (dein Entwurf):\n"
        "    def reveal(self, x, y):\n"
        "        if self.state is not GameState.PLAYING:\n"
        "            return\n"
        "        if self.board.reveal_cell(x, y):\n"
        "            if ...:            # Mine erwischt?\n"
        "                ...\n"
        "            elif ...:          # gewonnen?\n"
        "                ...",
    ],
    "l5_extra": [
        "Der Timer braucht zwei Zeitpunkte. Wann wird welcher gesetzt, und was liefert elapsed davor, "
        "währenddessen und danach?",
        "Merke start_time (anfangs None) beim ersten reveal, der etwas aufdeckt, und end_time beim Wechsel "
        "zu WON/LOST, beides mit time.monotonic() (einer Uhr, die nie rückwärts springt; aufrufen als "
        "time.monotonic() nach `import time`). elapsed: 0, solange start_time None ist, sonst "
        "int((end_time oder jetzt) - start_time). Für den Verlust per Chording ersetzt "
        "board.mine_revealed() die Prüfung der angeklickten Zelle.",
        "Gerüst:\n"
        "    @property\n"
        "    def elapsed(self) -> int:\n"
        "        if self.start_time is None:\n"
        "            return 0\n"
        "        end = ...       # Spiel vorbei? Dann end_time, sonst jetzt\n"
        "        return int(...)  # int() rundet ab\n"
        "Eine kleine Hilfsmethode _finish(state) setzt state und end_time zusammen. reset_board setzt beides "
        "auf None.",
    ],
    "l6": [
        "Was haben TerminalUI und TkinterUI gemeinsam, und was muss jede selbst können? Genau das gehört "
        "in die abstrakte Basisklasse.",
        "from abc import ABC, abstractmethod. UserInterface erbt von ABC, run und draw_board bekommen "
        "@abstractmethod und als Rumpf nur `...`. TerminalUI.__init__ speichert stdscr und setzt den Cursor. "
        "run(game) merkt sich self.game, ruft _setup_curses() auf und enthält die Schleife aus main.py "
        "(play). draw_board ist main.py:draw: die Zellen aus board.grid[y][x] statt aus numpy-Arrays, Titel, "
        "Minen-Zähler, Timer und Sieg/Verlust-Meldung aus self.game (difficulty.name, mines_left, elapsed, state).",
        "Port-Fahrplan aus main.py:\n"
        "  init_colors, curs_set, keypad  → _setup_curses()\n"
        "  play()-Schleife                → run(game)   (stdscr.getch() → _get_input())\n"
        "  game.move(dr, dc)              → self._move_cursor(dx, dy)   (Achtung: dx = Spalte!)\n"
        "  draw(), cell_look()            → draw_board(board) + private Helfer\n"
        "  game.reveal(*game.cursor)      → self.game.reveal(self.cursor_x, self.cursor_y)\n"
        "Optionales M-Menü: menu() setzt stdscr.timeout(-1); danach wieder timeout(250), sonst steht der Timer. "
        "Nach set_difficulty den Cursor neu setzen, sonst liegt er auf kleineren Brettern außerhalb (IndexError).\n"
        "__main__.py:\n"
        "    def main(stdscr):\n"
        "        TerminalUI(stdscr).run(Game(EASY))\n\n"
        "    if __name__ == \"__main__\":\n"
        "        curses.wrapper(main)",
    ],
    "l7": [
        "Ein Button pro Zelle, und jeder Klick soll game.reveal(x, y) mit seinen eigenen x und y aufrufen. "
        "Was ist an `command=lambda: self._on_left_click(x, y)` in einer Schleife gefährlich?",
        "Lambdas merken sich die Variable, nicht ihren Wert (late binding). Nach der Schleife zeigen alle auf "
        "das letzte x, y. Lösung: den Wert als Default-Argument einfrieren (lambda x=x, y=y: ...). Rechtsklick: "
        "Tk 8.6 (in Python 3.12) meldet ihn auf macOS als \"<Button-2>\", unter Windows/Linux als \"<Button-3>\". "
        "Binde beide, dann läuft es auf dem Mac und auf dem Arbeitsrechner. Nach jedem Klick "
        "draw_board aufrufen.",
        "Gerüst:\n"
        "    for y in range(height):\n"
        "        row = []\n"
        "        for x in range(width):\n"
        "            b = tk.Button(self.root, width=2, command=lambda x=x, y=y: self._on_left_click(x, y))\n"
        "            for event in (\"<Button-2>\", \"<Button-3>\"):   # Rechtsklick: macOS / Windows+Linux\n"
        "                b.bind(event, lambda e, x=x, y=y: self._on_right_click(x, y))\n"
        "            b.grid(row=y, column=x)\n"
        "            row.append(b)\n"
        "        self.buttons.append(row)\n"
        "Start z. B. in einem eigenen Skript: root = tk.Tk(); TkinterUI(root).run(Game(EASY)); run endet mit "
        "root.mainloop().",
    ],
    "l8": [
        "StartMenu IST ein Frame (Vererbung), TkinterUI HAT ein Fenster (Komposition). Was muss ein "
        "Konstruktor tun, bevor die geerbten Teile benutzbar sind? Und woher weiß das Menü, welche "
        "Oberflächen es anbieten soll, ohne „Terminal“ selbst hinzuschreiben?",
        "Erst super().__init__(master), danach Variablen und Widgets. Radiobuttons, die sich eine StringVar "
        "teilen, bilden eine Gruppe: Beim Klick schreibt Tk den value des Buttons in die Variable. Die "
        "Variable hält deshalb nur Namen; das passende DifficultyConfig suchst du erst beim Start heraus. "
        "Für __main__.py: Jeder Eintrag in LAUNCHERS ist eine Funktion, die eine Schwierigkeit bekommt und "
        "„ihre“ Oberfläche startet. Zwei davon hast du schon fast.",
        "Gerüst StartMenu (Widgets und run() selbst ergänzen):\n"
        "    class StartMenu(tk.Frame):\n"
        "        def __init__(self, master, ui_names, difficulties):\n"
        "            super().__init__(master)\n"
        "            self.ui_names = ui_names\n"
        "            self.difficulties = difficulties\n"
        "            self.ui_choice = tk.StringVar(master=self, value=ui_names[0])\n"
        "            self.difficulty_choice = ...\n"
        "            self.selection = None\n"
        "            self._create_widgets()      # Radiobuttons + self.start_button\n\n"
        "        def _on_start(self):\n"
        "            difficulty = next(d for d in self.difficulties if d.name == ...)\n"
        "            self.selection = ...\n"
        "            self.master.destroy()\n\n"
        "Gerüst __main__.py:\n"
        "    LAUNCHERS = {\"Terminal\": ..., \"Tkinter\": run_tkinter}\n\n"
        "    if __name__ == \"__main__\":\n"
        "        _use_base_tcl(tk)               # vor dem ersten tk.Tk()!\n"
        "        selection = StartMenu(tk.Tk(), list(LAUNCHERS), DIFFICULTIES).run()\n"
        "        if selection is not None:\n"
        "            ...",
    ],
    "l8_extra": [
        "Das Programm soll erst enden, wenn das Menü ohne Start geschlossen wird. Welche Schleife hört genau "
        "dann auf, und warum braucht jeder Durchlauf ein neues tk.Tk()?",
        "Eine Schleife, die so lange läuft, bis run() None liefert. Das Menü schließt sein Fenster mit "
        "destroy(), deshalb gehören tk.Tk() und StartMenu(...) in die Schleife, nicht davor.",
        "Gerüst:\n"
        "    while True:\n"
        "        selection = ...        # neues Fenster, neues StartMenu, run()\n"
        "        if selection is None:\n"
        "            break\n"
        "        ...                    # gewählte Oberfläche starten\n"
        "Kürzer geht es mit dem Walross-Operator :=, der in einem Ausdruck zuweist (seit Python 3.8).",
    ],
    "l9": [
        "Zwei Fragen trennen: „Wie soll diese Zelle aussehen?“ (hängt nur vom Zustand der Zelle ab) und „Wie "
        "bringe ich das auf den Bildschirm?“ (Tk). Welche der beiden lässt sich ohne Fenster beantworten und testen?",
        "_cell_style ist eine Abfrage: Sie bekommt eine Cell und gibt ein dict mit text, relief, bg und fg zurück, "
        "ohne irgendein Widget anzufassen. Lege zwei Grund-Stile als Konstanten an (geschlossen, offen) und baue "
        "die Sonderfälle mit {**GRUNDSTIL, \"text\": …} daraus. Die Reihenfolge der Prüfungen zählt: Eine Flagge "
        "liegt immer auf einer geschlossenen Zelle.",
        "Gerüst (Farben und Sonderfälle selbst ergänzen):\n"
        "    CLOSED = {\"relief\": \"raised\", \"bg\": ..., \"fg\": \"black\", \"text\": \"\"}\n"
        "    OPEN = {\"relief\": \"flat\", \"bg\": ..., \"fg\": \"black\", \"text\": \"\"}\n\n"
        "    def _cell_style(self, cell):\n"
        "        if cell.is_flagged:\n"
        "            return {**CLOSED, \"text\": \"F\"}\n"
        "        if not cell.is_revealed:\n"
        "            return CLOSED\n"
        "        ...                      # Mine, Zahl, leer\n\n"
        "In _create_widgets wird aus tk.Button ein tk.Label. Ein Label kennt kein command=, der Klick hängt per "
        "bind dran, und bind übergibt ein Event-Objekt:\n"
        "    label = tk.Label(self.root, width=2)\n"
        "    label.bind(\"<Button-1>\", lambda e, x=x, y=y: self._on_left_click(x, y))\n"
        "In draw_board: self.cells[c.y][c.x].config(**self._cell_style(c))",
    ],
    "l9_extra": [
        "Ob eine Flagge falsch war, darf man erst nach dem Spiel sehen. Welche zwei Informationen braucht "
        "_cell_style dafür, und woher bekommt es die zweite?",
        "Die Zelle weiß, ob sie eine Mine ist. Ob das Spiel verloren ist, weiß nur self.game.state. Falsch ist eine "
        "Flagge, wenn das Spiel LOST ist und die Zelle keine Mine.",
        "Gerüst:\n"
        "    if cell.is_flagged:\n"
        "        wrong = ... and not cell.is_mine\n"
        "        return {**CLOSED, \"text\": \"X\" if wrong else \"F\"}",
    ],
}

ANSWERS = {
    "l0": """Musterantworten L0
• *-- (gefüllte Raute) = Komposition: Das Ganze besitzt die Teile und erzeugt sie; ohne Board keine Cells.
• --> = Assoziation („kennt/benutzt dauerhaft“), z. B. Game → DifficultyConfig.
• <|-- = Vererbung (TerminalUI ist ein UserInterface).
• ..> = Abhängigkeit („benutzt kurz“, z. B. als Parameter): UserInterface ruft Game-Methoden auf.
• + öffentlich, - privat (in Python: führender Unterstrich), * hinter einer Methode = abstrakt.
1. „Game hält dauerhaft eine TerminalUI“ wäre eine Assoziation: Game --> TerminalUI. Gehörte die UI dem Game
   und lebte nur mit ihm, wäre es Komposition: Game *-- TerminalUI. (Beides wollen wir NICHT, siehe Frage 2.)
2. Die UI kennt das Spiel, das Spiel kennt die UI nicht. Der Pfeil zeigt in Richtung der Abhängigkeit. So kann
   man die Oberfläche austauschen (Terminal, Tkinter), ohne die Spiellogik anzufassen.
3. _initialize_board, _plant_mines, _calculate_neighbors und _cascade_reveal: Im Diagramm stehen sie mit
   „-“, in Python beginnen sie mit einem Unterstrich.
• Warum eine Klasse pro Datei? In Python ist das keine Pflicht (anders als Java). Hier hilft es, Abhängigkeiten
  sichtbar zu machen: An den Imports jeder Datei siehst du sofort, wen sie kennt.""",
    "l1": """Musterantworten L1
• Warum Enum statt Strings wie 'won'? Tippfehler ('wonn') fallen bei Strings erst zur Laufzeit oder gar nicht
  auf; GameState.WONN wirft sofort AttributeError, und die IDE kann vervollständigen. Außerdem ist die Menge
  der Zustände an einer Stelle definiert.
• Warum frozen=True? Eine Schwierigkeitsstufe ist ein Wert, keine Entität. Wäre EASY veränderbar, könnte ein
  Spiel EASY.amount = 50 setzen und damit jedes andere Spiel mit EASY verändern (geteilte Referenz). Frozen
  dataclasses sind zudem hashbar (als dict-Key oder in sets nutzbar), wie Java-Records.""",
    "l2": """Musterantworten L2
• Warum muss self explizit dastehen? Python übergibt das Objekt beim Methodenaufruf als erstes Argument:
  cell.toggle_flag() ist Cell.toggle_flag(cell). Java macht dasselbe versteckt mit this.
• Warum gehört toggle_flag in Cell und nicht nur ins Board? Die Regel „aufgedeckte Zellen lassen sich nicht
  markieren“ betrifft nur den Zustand der Zelle. Liegt sie in Cell, kann niemand sie umgehen, egal ob Board,
  Game oder ein Test die Methode aufruft (Kapselung: Daten und die Regeln dazu an einem Ort).""",
    "l3": """Musterantworten L3
• Warum [[Cell(...)] * w] * h nicht funktioniert: * vervielfacht Referenzen, nicht Objekte. Alle Zeilen sind
  dieselbe Liste, alle Einträge dieselbe Cell. Ändert man eine, ändern sich „alle“. Java würde das mit
  Arrays.fill(row, cell) genauso falsch machen.
• Warum die Minen erst beim ersten Klick legen? Nur so kann die Startzelle (samt Nachbarn) garantiert sicher
  sein. Dafür braucht das Board den Zustand mines_planted.
• Warum ein Generator für die Nachbarn? Die Rand-Logik steht dann an genau einer Stelle (DRY). yield liefert die
  Nachbarn bei Bedarf einzeln, ohne eine Liste aufzubauen; das ähnelt einem Java-Iterator/Stream.""",
    "l4": """Musterantworten L4
• Warum Stack statt Rekursion? Python hat keine Tail-Call-Optimierung und ein Rekursionslimit (~1000). Die
  Rekursionstiefe kann bis zur Anzahl der Felder wachsen. HARD (480 Felder) liegt knapp darunter, aber schon
  zwei Aufrufebenen pro Feld (z. B. reveal_cell ↔ _cascade_reveal) oder ein größeres Brett (der Test nimmt
  60x60, und Board akzeptiert beliebige Größen) sprengen das Limit → RecursionError. Ein expliziter Stack
  wächst auf dem Heap und hat diese Grenze nicht.
• Warum ist check_win eine reine Abfrage? Command-Query-Separation: Methoden ändern entweder Zustand (Command)
  oder liefern eine Antwort (Query), nicht beides. Dann kann man check_win beliebig oft aufrufen, z. B. für die
  Anzeige, ohne Überraschungen. Das automatische Markieren aller Minen bei Sieg (main.py: check_win) ist ein
  Command. Wer es möchte, macht es dort, wo der Zustandswechsel passiert (Game beim Wechsel zu WON) oder nur in
  der Anzeige (die UI zeigt bei WON alle Minen als Flagge).
• Warum gibt reveal_cell bei Flaggen False zurück, statt eine Exception zu werfen? Ein Klick auf eine Flagge ist
  ein normaler Spielzug ohne Wirkung, kein Fehler. Exceptions sind für unerwartete Situationen.""",
    "l5": """Musterantworten L5
• Warum entscheidet Game über LOST/WON und nicht das Board? Das Board kennt Zellen, nicht Spielregeln wie „nach
  dem Verlieren keine Züge mehr“. So bleibt das Board wiederverwendbar (z. B. für einen Solver), und der
  Spielablauf steht an einer Stelle (Controller).
• Warum lässt sich game.board in den Tests einfach ersetzen? Weil das Attribut öffentlich ist und Game bei jedem
  Zug frisch über self.board mit dem Board redet (Duck Typing: jedes Objekt mit denselben Methoden passt).
  Echte Dependency Injection ist das aber nicht: Game erzeugt sein Board selbst (Komposition), und
  reset_board() würde ein eingesetztes Board wieder überschreiben. Echtes DI wäre z. B.
  Game(difficulty, board_factory=Board): Der Aufrufer bestimmt, womit das Board gebaut wird, so wie Spring
  einem Service seine Abhängigkeiten per Konstruktor übergibt.""",
    "l6": """Musterantworten L6
• Warum eine abstrakte Basisklasse, wenn Python Duck Typing kann? Die ABC dokumentiert den Vertrag und
  erzwingt ihn früh: Eine UI ohne draw_board lässt sich gar nicht erst instanziieren, statt mitten im Spiel mit
  AttributeError abzustürzen. (Alternative ohne Vererbung: typing.Protocol, ähnlich wie ein Java-Interface,
  das nur strukturell geprüft wird.)
• Warum darf game.py nichts von curses wissen? Abhängigkeiten sollen von außen (UI) nach innen (Logik) zeigen.
  Dann kannst du die Logik testen, ohne Terminal, und eine zweite UI (Tkinter) bauen, ohne Game anzufassen.
  Das ist dieselbe Schichtung wie Controller → Service in Spring.
• Warum der Cursor in TerminalUI statt in Game? Ein Cursor ist ein Konzept der Tastatur-Oberfläche. Tkinter
  braucht keinen, dort klickt man direkt.""",
    "l7": """Musterantworten L7
• Late Binding: Eine Closure speichert die Variable, nicht den Wert. Java verbietet genau diesen Fehler, indem
  Lambdas nur auf (effectively) final Variablen zugreifen dürfen. Python erlaubt es, deshalb x=x als
  Default-Argument.
• Was zeigt die zweite UI? Wenn Game, Board und Cell unverändert bleiben und trotzdem eine komplett andere
  Oberfläche funktioniert, ist die Trennung gelungen (Open/Closed: offen für Erweiterung, geschlossen für
  Änderung).
• Diagramm-Reflexion: Das sollte dein ergänztes Diagramm (mindestens) enthalten:
    Board:       -_neighbors(x, y) Iterator, +flags_placed: int (Property), +mine_revealed() bool,
                 -_chord(x, y) bool (falls ausgelagert)
    Game:        +mines_left: int, +elapsed: int (Properties), +start_time / +end_time (oder privat),
                 ggf. -_finish(state)
    TerminalUI:  +game: Game  →  aus der gestrichelten Abhängigkeit UserInterface ..> Game wird bei TerminalUI
                 eine echte Assoziation (TerminalUI --> Game), weil sie das Spiel dauerhaft hält.
    reveal_cell: Rückgabe dokumentieren („True = Zelle wurde aufgedeckt“), z. B. als note.
  Vergleiche: Was war im ursprünglichen Diagramm unterspezifiziert? (Rückgabewert, Ort des Cursors,
  Timer, Chording)""",
    "l8": """Musterantworten L8
• Warum bekommt StartMenu die UI-Namen und Schwierigkeiten übergeben, statt sie selbst zu importieren?
  So kennt das Menü weder TerminalUI noch TkinterUI. Es zeigt einfach an, was __main__.py ihm gibt. Eine
  dritte Oberfläche ist eine neue Zeile in LAUNCHERS, StartMenu bleibt unverändert. Das ist Dependency
  Injection per Konstruktor, wie in L5 beschrieben (in Spring: Konstruktor-Injection), und es macht das
  Menü testbar: Die Checks geben ihm erfundene Namen wie „Alpha“ und „Beta“.
• Warum ist StartMenu keine UserInterface? UserInterface verspricht run(game) und draw_board(board), also
  eine Oberfläche, die ein laufendes Spiel zeigt. Das Menü spielt kein Spiel, es wählt nur aus. Würde es
  trotzdem erben, müsste es Methoden haben, die nichts Sinnvolles tun. Vererbung heißt „ist ein“, und ein
  Startmenü ist kein Spielfeld (Liskov: überall, wo eine UserInterface erwartet wird, müsste es passen).
• Was passiert ohne super().__init__(master)? Der Frame-Teil des Objekts wird nie eingerichtet: Es fehlen
  self.tk, self.master und das echte Tk-Widget. Der Fehler kommt erst beim ersten Kind-Widget oder bei
  StringVar(master=self) als AttributeError, weit weg von der eigentlichen Ursache. In Java ergänzt der
  Compiler super() automatisch. In Python läuft das geerbte __init__ nur dann von selbst, wenn die
  Unterklasse gar kein eigenes __init__ hat; schreibst du eines, musst du super().__init__ selbst aufrufen.
• Warum LAUNCHERS statt if/else? Die Liste der Oberflächen steht an genau einer Stelle, und das Menü liest
  sie von dort. Mit if/else müsstest du für eine neue UI das Menü und die Verzweigung ändern und darauf
  achten, dass die Namen gleich geschrieben sind.""",
    "l9": """Musterantworten L9
• Warum gibt _cell_style ein dict zurück, statt das Label selbst zu ändern? So ist „wie sieht eine Zelle aus“
  eine reine Abfrage ohne Seiteneffekt (Command-Query-Trennung wie in L4). Sie lässt sich ohne Fenster testen,
  und draw_board bleibt eine einzige Zeile pro Zelle. Die TerminalUI macht es mit _cell_look genauso, nur mit
  curses-Attributen statt Tk-Optionen.
• Warum Labels statt Buttons? Auf macOS zeichnet Tk Buttons mit dem System-Look (Aqua) und ignoriert bg und
  relief. Ein Label zeichnet Tk selbst, deshalb wirken die Optionen dort auf jedem System gleich. Der Preis:
  Ein Label hat kein command=, der Klick kommt über bind.
• Was ist der Unterschied zwischen command= und bind? command= gibt es nur bei Widgets mit einer
  „Hauptaktion“; bei Button und Checkbutton ruft Tk die Funktion ohne Argumente auf (andere Widgets wie
  Scale übergeben einen Wert). bind hängt an ein beliebiges Ereignis (Maustaste, Taste, Fokus …) und übergibt
  immer ein Event-Objekt, deshalb lambda e, …. In Java entspricht command= etwa addActionListener, bind etwa
  addMouseListener; anders als bei Tks command= bekommt aber auch der ActionListener ein Event.
• Was macht {**CLOSED, "text": "F"}? Es baut ein neues dict: erst alle Einträge aus CLOSED, dann wird text
  überschrieben. CLOSED selbst bleibt unverändert. Darum dürfen die Grund-Stile Konstanten sein, die sich
  alle Zellen teilen. (Gefährlich wäre CLOSED["text"] = "F": Das änderte den Stil für jede geschlossene Zelle.)""",
    "quiz": """Musterantworten Abschluss-Quiz
1. __init__, __repr__, __eq__ (und mehr). frozen=True verbietet Zuweisungen nach dem Erzeugen und macht die
   Objekte hashbar.
2. In __init__ durch self.name = …; eine Liste im Klassenrumpf ist ein Klassenattribut und wird von allen
   Instanzen geteilt.
3. Sie wird zur Generator-Funktion: Der Aufruf liefert einen Iterator, der Werte einzeln bei Bedarf erzeugt.
4. Die äußere Liste sind die Zeilen (y), jede Zeile enthält die Spalten (x). So entspricht grid[y] einer
   Bildschirmzeile, wie beim Zeichnen von oben nach unten.
5. Command: reveal_cell / toggle_flag. Query: check_win / mine_revealed / flags_placed.
6. TypeError, weil abstrakte Methoden fehlen. Gut, weil der Fehler beim Erzeugen auffällt und nicht erst,
   wenn mitten im Spiel draw_board aufgerufen wird.
7. pysweeper/__main__.py. Ohne den Guard würde schon ein bloßer Import (z. B. durch Tests oder Tools) das
   Spiel starten.""",
}
