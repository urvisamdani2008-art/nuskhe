"""
Nuskhe — Ayurveda Home Remedies (Desktop App)
-----------------------------------------------
A pure Python desktop application built with Tkinter (Python's built-in
GUI toolkit — no browser, no Flask, no internet needed to run it).

Beginner notes (read these!):
- Tkinter apps are built from "widgets" — Labels, Buttons, Entry boxes,
  Listboxes, etc. — arranged inside Frames using layout managers
  (we use .pack() and .grid() here).
- We store the remedies and your favorites in a local SQLite database
  file (nuskhe_desktop.db) that lives right next to this script.
- Everything runs in ONE window; different "views" (All remedies,
  Favorites, Glossary) are just different tabs using ttk.Notebook.

To run:
    python nuskhe_desktop.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
import os

# ---------------------------------------------------------------------
# Colors & fonts (kept in one place so the whole app stays consistent)
# ---------------------------------------------------------------------

COLOR_BG = "#FBF6EC"          # ivory background
COLOR_CARD = "#FFFFFF"
COLOR_SANDALWOOD = "#EFE3CC"
COLOR_TURMERIC = "#C98A2C"
COLOR_TULSI = "#3F5D3A"
COLOR_CLAY = "#2E2018"
COLOR_RUST = "#A64B3A"
COLOR_LINE = "#DDD0B0"

FONT_TITLE = ("Georgia", 20, "bold")
FONT_HEADING = ("Georgia", 13, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)

CATEGORY_COLORS = {
    "Cold & Cough": "#C98A2C",
    "Digestion": "#3F5D3A",
    "Skin & Hair": "#A64B3A",
    "Sleep & Stress": "#6B5B95",
    "Aches & Pains": "#4A6670",
    "Immunity": "#8C7A3C",
}

GLOSSARY = [
    ("Turmeric", "An anti-inflammatory root used in cooking and remedies alike; the compound curcumin is behind most of its benefits."),
    ("Tulsi (Holy Basil)", "A staple in almost every Indian household courtyard, used for colds, stress, and general immunity."),
    ("Ashwagandha", "A calming root often called an 'adaptogen' — traditionally used to help the body handle stress."),
    ("Ajwain (Carom Seeds)", "Small, strong-smelling seeds that are a go-to for bloating and indigestion after meals."),
    ("Triphala", "A blend of three dried fruits, commonly used to support gentle, regular digestion."),
    ("Amla (Indian Gooseberry)", "A sour fruit rich in Vitamin C, used for immunity and as a base for hair oils."),
    ("Brahmi", "A herb traditionally associated with calming the mind and supporting focus."),
    ("Clove", "A strong, numbing spice — a classic quick fix for tooth and gum discomfort."),
]

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nuskhe_desktop.db")


# ---------------------------------------------------------------------
# Seed data — same 24 remedies as the web version
# ---------------------------------------------------------------------

SEED_REMEDIES = [
    {"name": "Ginger-Tulsi Kadha", "category": "Cold & Cough",
     "symptoms": ["cold", "cough", "sore throat", "congestion"],
     "ingredients": ["ginger", "tulsi", "black pepper", "honey"],
     "method": "Boil crushed ginger, 5-6 tulsi leaves and a pinch of crushed black pepper in a cup of water for 5-7 minutes. Strain, cool slightly, and stir in a teaspoon of honey.",
     "when": "Twice a day, morning and night, while symptoms last.",
     "caution": "Skip honey for children under 1 year. Reduce pepper if you have acidity."},
    {"name": "Turmeric Milk (Haldi Doodh)", "category": "Immunity",
     "symptoms": ["cold", "body ache", "immunity", "cough"],
     "ingredients": ["turmeric", "milk", "black pepper"],
     "method": "Warm a cup of milk, stir in half a teaspoon of turmeric and a pinch of black pepper. Simmer for 2 minutes.",
     "when": "Once at night before sleeping.",
     "caution": "Avoid if lactose intolerant — can be made with warm water instead."},
    {"name": "Ajwain Water for Bloating", "category": "Digestion",
     "symptoms": ["indigestion", "bloating", "gas", "stomach ache"],
     "ingredients": ["ajwain"],
     "method": "Boil a teaspoon of ajwain (carom seeds) in a cup of water for 5 minutes until it turns light brown. Strain and sip warm.",
     "when": "After a heavy meal, or when bloated.",
     "caution": "Avoid large amounts during pregnancy without checking with a doctor."},
    {"name": "Fennel-Honey for Acidity", "category": "Digestion",
     "symptoms": ["acidity", "heartburn", "indigestion"],
     "ingredients": ["fennel", "honey"],
     "method": "Chew a teaspoon of fennel seeds slowly after meals, or steep them in hot water for 5 minutes and drink with honey.",
     "when": "After meals, especially heavy or spicy ones.",
     "caution": "Generally safe, but skip honey for infants."},
    {"name": "Jeera Water for Digestion", "category": "Digestion",
     "symptoms": ["indigestion", "bloating", "gas"],
     "ingredients": ["jeera"],
     "method": "Soak a teaspoon of jeera (cumin) in a glass of water overnight. Boil the same water in the morning for 5 minutes, strain, and drink warm.",
     "when": "First thing in the morning, on an empty stomach.",
     "caution": "Safe for most people; reduce quantity if you have very low blood pressure."},
    {"name": "Warm Turmeric-Salt Gargle", "category": "Cold & Cough",
     "symptoms": ["sore throat", "cough"],
     "ingredients": ["turmeric", "salt"],
     "method": "Mix half a teaspoon each of turmeric and salt in a glass of warm water. Gargle for 30 seconds.",
     "when": "2-3 times a day.",
     "caution": "Do not swallow the gargle. Not for children too young to gargle safely."},
    {"name": "Ashwagandha Warm Milk", "category": "Sleep & Stress",
     "symptoms": ["sleep", "stress", "anxiety", "insomnia"],
     "ingredients": ["ashwagandha", "milk"],
     "method": "Stir half a teaspoon of ashwagandha powder into a warm cup of milk. Sweeten lightly if needed.",
     "when": "30-45 minutes before bed.",
     "caution": "Avoid during pregnancy or if on thyroid medication without medical advice."},
    {"name": "Brahmi-Tulsi Calming Tea", "category": "Sleep & Stress",
     "symptoms": ["stress", "anxiety", "headache"],
     "ingredients": ["tulsi", "brahmi"],
     "method": "Steep tulsi leaves and a small amount of brahmi powder in hot water for 5-7 minutes. Strain and sip slowly.",
     "when": "In the evening, when winding down.",
     "caution": "Introduce brahmi gradually — start with a small amount."},
    {"name": "Ginger-Peppermint for Headache", "category": "Aches & Pains",
     "symptoms": ["headache", "nausea"],
     "ingredients": ["ginger", "peppermint"],
     "method": "Steep crushed ginger and a few peppermint leaves in hot water for 5 minutes. Drink warm, and inhale the steam before drinking.",
     "when": "At the onset of a headache.",
     "caution": "Avoid strong peppermint oil directly on skin for young children."},
    {"name": "Warm Mustard Oil Massage", "category": "Aches & Pains",
     "symptoms": ["joint pain", "body ache", "muscle pain"],
     "ingredients": ["mustard oil", "garlic"],
     "method": "Warm mustard oil with a crushed garlic clove until fragrant. Cool to a comfortable temperature and massage into the sore area.",
     "when": "Once daily, or before sleeping on a painful day.",
     "caution": "Test on a small skin patch first to check for irritation."},
    {"name": "Aloe Vera Gel for Sunburn", "category": "Skin & Hair",
     "symptoms": ["sunburn", "skin irritation", "rash"],
     "ingredients": ["aloe vera"],
     "method": "Apply fresh aloe vera gel directly to the affected skin. Leave it on until absorbed, no need to rinse.",
     "when": "2-3 times a day until redness settles.",
     "caution": "Do a patch test first if using aloe vera on skin for the first time."},
    {"name": "Besan-Turmeric Face Pack", "category": "Skin & Hair",
     "symptoms": ["dull skin", "acne", "skin glow"],
     "ingredients": ["besan", "turmeric", "milk"],
     "method": "Mix two tablespoons of besan (gram flour) with a pinch of turmeric and enough milk or water to form a paste. Apply, leave for 15 minutes, then rinse.",
     "when": "2 times a week.",
     "caution": "Turmeric can temporarily stain skin yellow — this fades within a day."},
    {"name": "Amla-Honey Immunity Mix", "category": "Immunity",
     "symptoms": ["immunity", "weakness", "cold"],
     "ingredients": ["amla", "honey"],
     "method": "Mix a teaspoon of amla (Indian gooseberry) powder with honey to form a thick paste.",
     "when": "Once daily, in the morning.",
     "caution": "Skip honey for children under 1 year."},
    {"name": "Clove for Toothache", "category": "Aches & Pains",
     "symptoms": ["toothache", "gum pain"],
     "ingredients": ["clove"],
     "method": "Place a whole clove near the painful tooth and gently bite to release the oil, or dab a drop of clove oil on a cotton swab and apply.",
     "when": "As needed for temporary relief.",
     "caution": "This eases pain temporarily — see a dentist for the underlying issue."},
    {"name": "Coconut Oil-Camphor for Cough at Night", "category": "Cold & Cough",
     "symptoms": ["cough", "congestion", "cold"],
     "ingredients": ["coconut oil", "camphor"],
     "method": "Warm coconut oil with a small piece of camphor until it dissolves. Massage gently onto the chest and back before bed.",
     "when": "At night before sleeping.",
     "caution": "Keep away from the nose and eyes. Not for infants."},
    {"name": "Curd-Turmeric for Hiccups", "category": "Digestion",
     "symptoms": ["hiccups"],
     "ingredients": ["curd"],
     "method": "Eat a spoonful of plain curd slowly, or sip on buttermilk.",
     "when": "As soon as hiccups start.",
     "caution": "Generally safe for most people."},
    {"name": "Tulsi-Ginger Steam Inhalation", "category": "Cold & Cough",
     "symptoms": ["congestion", "cold", "blocked nose"],
     "ingredients": ["tulsi", "ginger"],
     "method": "Boil water with crushed ginger and a handful of tulsi leaves. Inhale the steam under a towel for 5-8 minutes.",
     "when": "Once or twice a day.",
     "caution": "Keep a safe distance from boiling water to avoid burns; not for young children unsupervised."},
    {"name": "Triphala Water for Constipation", "category": "Digestion",
     "symptoms": ["constipation", "bloating"],
     "ingredients": ["triphala"],
     "method": "Soak half a teaspoon of triphala powder in warm water overnight. Strain if needed and drink in the morning.",
     "when": "Once daily, preferably before bed or first thing in the morning.",
     "caution": "Start with a small amount — too much can cause loose motion. Avoid during pregnancy without medical advice."},
    {"name": "Coconut Oil for Dry, Cracked Heels", "category": "Skin & Hair",
     "symptoms": ["dry skin", "cracked heels"],
     "ingredients": ["coconut oil"],
     "method": "Massage warm coconut oil into clean feet, focusing on heels. Wear cotton socks overnight to lock in moisture.",
     "when": "Every night until skin softens.",
     "caution": "Generally safe; discontinue if irritation occurs."},
    {"name": "Amla-Coconut Hair Oil for Hair Fall", "category": "Skin & Hair",
     "symptoms": ["hair fall", "dandruff", "dry scalp"],
     "ingredients": ["amla", "coconut oil"],
     "method": "Warm coconut oil with a spoon of amla powder for a few minutes. Cool slightly and massage into the scalp. Leave for an hour before washing.",
     "when": "2 times a week.",
     "caution": "Patch test if you have a sensitive scalp."},
    {"name": "Clove-Salt Rinse for Mouth Ulcers", "category": "Aches & Pains",
     "symptoms": ["mouth ulcer", "gum pain"],
     "ingredients": ["clove", "salt"],
     "method": "Dissolve a pinch of salt in warm water and rinse the mouth. Alternatively, dab a little clove oil directly on the ulcer.",
     "when": "2-3 times a day.",
     "caution": "Avoid clove oil directly on very young children's gums."},
    {"name": "Warm Garlic Oil for Ear Ache", "category": "Aches & Pains",
     "symptoms": ["ear ache", "ear pain"],
     "ingredients": ["garlic", "mustard oil"],
     "method": "Warm mustard oil with a crushed garlic clove until fragrant, then strain and cool until just warm. Place 2-3 drops in the affected ear.",
     "when": "Once, when the ache starts.",
     "caution": "Never use if there is discharge from the ear or a suspected eardrum injury — see a doctor instead."},
    {"name": "Rose Water Eye Compress", "category": "Sleep & Stress",
     "symptoms": ["eye strain", "tired eyes"],
     "ingredients": ["rose water"],
     "method": "Soak two cotton pads in chilled rose water and place over closed eyes for 10 minutes.",
     "when": "In the evening, after screen-heavy days.",
     "caution": "Use pure, food/cosmetic-grade rose water only."},
    {"name": "Ashwagandha for Study Fatigue", "category": "Sleep & Stress",
     "symptoms": ["fatigue", "stress", "exam stress", "weakness"],
     "ingredients": ["ashwagandha", "milk"],
     "method": "Mix a small amount of ashwagandha powder into warm milk, taken as a steady daily habit rather than only during exams.",
     "when": "Once daily, ideally at the same time each day.",
     "caution": "Avoid during pregnancy or with thyroid conditions without medical advice; not a substitute for sleep or rest."},
]


# ---------------------------------------------------------------------
# Database layer
# ---------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS remedies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            method TEXT NOT NULL,
            when_to_take TEXT NOT NULL,
            caution TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            remedy_id INTEGER PRIMARY KEY,
            FOREIGN KEY(remedy_id) REFERENCES remedies(id)
        )
    """)
    conn.commit()

    count = cur.execute("SELECT COUNT(*) FROM remedies").fetchone()[0]
    if count == 0:
        for r in SEED_REMEDIES:
            cur.execute(
                """INSERT INTO remedies
                   (name, category, symptoms, ingredients, method, when_to_take, caution)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (r["name"], r["category"], json.dumps(r["symptoms"]),
                 json.dumps(r["ingredients"]), r["method"], r["when"], r["caution"]),
            )
        conn.commit()
    conn.close()


def fetch_all_remedies():
    conn = get_db()
    rows = conn.execute("SELECT * FROM remedies").fetchall()
    fav_ids = {row["remedy_id"] for row in conn.execute("SELECT remedy_id FROM favorites")}
    conn.close()

    remedies = []
    for row in rows:
        remedies.append({
            "id": row["id"], "name": row["name"], "category": row["category"],
            "symptoms": json.loads(row["symptoms"]),
            "ingredients": json.loads(row["ingredients"]),
            "method": row["method"], "when": row["when_to_take"], "caution": row["caution"],
            "is_favorite": row["id"] in fav_ids,
        })
    return remedies


def toggle_favorite_db(remedy_id, make_favorite):
    conn = get_db()
    if make_favorite:
        conn.execute("INSERT OR IGNORE INTO favorites (remedy_id) VALUES (?)", (remedy_id,))
    else:
        conn.execute("DELETE FROM favorites WHERE remedy_id = ?", (remedy_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------

class NuskheApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nuskhe — Home Remedies, The Ayurvedic Way")
        self.geometry("980x640")
        self.configure(bg=COLOR_BG)
        self.minsize(800, 560)

        self.remedies = fetch_all_remedies()
        self.symptom_query = tk.StringVar()
        self.active_category = None
        self.active_ingredients = set()
        self.show_favorites_only = False

        self._build_style()
        self._build_layout()
        self._refresh_remedy_list()

    # -- styling -------------------------------------------------------

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Card.TFrame", background=COLOR_CARD)
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_CLAY, font=FONT_BODY)
        style.configure("Heading.TLabel", background=COLOR_BG, foreground=COLOR_CLAY, font=FONT_HEADING)
        style.configure("Title.TLabel", background=COLOR_BG, foreground=COLOR_TULSI, font=FONT_TITLE)
        style.configure("Small.TLabel", background=COLOR_BG, foreground="#6b5c47", font=FONT_SMALL)
        style.configure("TButton", font=FONT_BODY, padding=6)
        style.configure("Accent.TButton", background=COLOR_TULSI, foreground="white")
        style.map("Accent.TButton", background=[("active", "#324a2e")])
        style.configure("Treeview", font=FONT_BODY, rowheight=26, background=COLOR_CARD, fieldbackground=COLOR_CARD)
        style.configure("Treeview.Heading", font=FONT_BODY_BOLD)

    # -- layout ----------------------------------------------------------

    def _build_layout(self):
        # Header
        header = ttk.Frame(self, padding=(20, 14))
        header.pack(fill="x")
        ttk.Label(header, text="Nuskhe", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="   Home remedies passed down, kept in one place", style="Small.TLabel").pack(side="left", pady=(8, 0))

        # Disclaimer banner
        banner = tk.Frame(self, bg="#F4E7DE")
        banner.pack(fill="x")
        tk.Label(
            banner,
            text="Please note: these remedies are for everyday, mild discomfort only. "
                 "See a doctor if a symptom is severe, persistent, or keeps returning.",
            bg="#F4E7DE", fg="#5c2c1e", font=FONT_SMALL, wraplength=920, justify="left", padx=16, pady=8,
        ).pack(fill="x")

        # Main body: left filters, center list, right detail
        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_center_panel(body)
        self._build_right_panel(body)

    def _build_left_panel(self, parent):
        panel = ttk.Frame(parent, width=220)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 14))

        ttk.Label(panel, text="Search by symptom", style="Heading.TLabel").pack(anchor="w", pady=(0, 4))
        entry = ttk.Entry(panel, textvariable=self.symptom_query, width=26)
        entry.pack(fill="x", pady=(0, 4))
        self.symptom_query.trace_add("write", lambda *a: self._on_symptom_change())
        ttk.Label(panel, text="e.g. cold, headache, acidity", style="Small.TLabel").pack(anchor="w", pady=(0, 16))

        ttk.Label(panel, text="Browse by category", style="Heading.TLabel").pack(anchor="w", pady=(0, 6))
        self.category_buttons = {}
        for cat, color in CATEGORY_COLORS.items():
            btn = tk.Button(
                panel, text=cat, bg=color, fg="white", relief="flat", anchor="w",
                font=FONT_BODY_BOLD, padx=10, pady=6,
                command=lambda c=cat: self._on_category_click(c),
            )
            btn.pack(fill="x", pady=2)
            self.category_buttons[cat] = btn

        ttk.Label(panel, text="What's in your kitchen?", style="Heading.TLabel").pack(anchor="w", pady=(16, 6))
        ingr_frame = ttk.Frame(panel)
        ingr_frame.pack(fill="both", expand=False)

        canvas = tk.Canvas(ingr_frame, bg=COLOR_BG, height=160, highlightthickness=0)
        scrollbar = ttk.Scrollbar(ingr_frame, orient="vertical", command=canvas.yview)
        self.ingr_inner = ttk.Frame(canvas)
        self.ingr_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.ingr_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.ingredient_vars = {}
        for ing in self._all_ingredients():
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                self.ingr_inner, text=ing, variable=var, bg=COLOR_BG, anchor="w",
                font=FONT_SMALL, command=self._on_ingredient_toggle,
            )
            cb.pack(fill="x")
            self.ingredient_vars[ing] = var

        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=14)
        self.fav_toggle_btn = ttk.Button(panel, text="Show favorites only", command=self._toggle_favorites_view)
        self.fav_toggle_btn.pack(fill="x")

        ttk.Button(panel, text="Clear all filters", command=self._clear_filters).pack(fill="x", pady=(6, 0))

    def _build_center_panel(self, parent):
        panel = ttk.Frame(parent)
        panel.grid(row=0, column=1, sticky="nsew", padx=(0, 14))
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)

        top_row = ttk.Frame(panel)
        top_row.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.results_title = ttk.Label(top_row, text="All remedies", style="Heading.TLabel")
        self.results_title.pack(side="left")
        self.results_count = ttk.Label(top_row, text="", style="Small.TLabel")
        self.results_count.pack(side="right")

        columns = ("name", "category")
        self.tree = ttk.Treeview(panel, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Remedy")
        self.tree.heading("category", text="Category")
        self.tree.column("name", width=260)
        self.tree.column("category", width=140)
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_select_remedy)

        vsb = ttk.Scrollbar(panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        # Tag colors per category for a little visual flair in the list
        for cat, color in CATEGORY_COLORS.items():
            self.tree.tag_configure(cat, background=COLOR_CARD)

    def _build_right_panel(self, parent):
        panel = tk.Frame(parent, bg=COLOR_SANDALWOOD, width=320)
        panel.grid(row=0, column=2, sticky="ns")
        panel.pack_propagate(False)

        self.detail_name = tk.Label(panel, text="Select a remedy", bg=COLOR_SANDALWOOD, fg=COLOR_CLAY,
                                     font=FONT_HEADING, wraplength=290, justify="left")
        self.detail_name.pack(anchor="w", padx=16, pady=(16, 4))

        self.detail_cat = tk.Label(panel, text="", bg=COLOR_SANDALWOOD, fg="white", font=FONT_SMALL)
        self.detail_cat.pack(anchor="w", padx=16, pady=(0, 10))

        self.fav_btn = tk.Button(panel, text="♡ Add to favorites", command=self._on_toggle_favorite,
                                  relief="flat", bg=COLOR_CARD, fg=COLOR_RUST, font=FONT_BODY_BOLD)
        self.fav_btn.pack(anchor="w", padx=16, pady=(0, 14))

        self.detail_text = tk.Text(panel, wrap="word", bg=COLOR_SANDALWOOD, fg=COLOR_CLAY,
                                    font=FONT_BODY, relief="flat", height=22, borderwidth=0)
        self.detail_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.detail_text.configure(state="disabled")

        self.selected_remedy_id = None

    # -- data helpers ------------------------------------------------------

    def _all_ingredients(self):
        s = set()
        for r in self.remedies:
            s.update(r["ingredients"])
        return sorted(s)

    def _matches_filters(self, r):
        if self.show_favorites_only:
            return r["is_favorite"]
        if self.active_category:
            return r["category"] == self.active_category
        if self.active_ingredients:
            return any(ing in r["ingredients"] for ing in self.active_ingredients)
        q = self.symptom_query.get().strip().lower()
        if q:
            return any(q in s for s in r["symptoms"]) or q in r["name"].lower()
        return True

    # -- event handlers ------------------------------------------------------

    def _on_symptom_change(self):
        if self.symptom_query.get().strip():
            self.active_category = None
            self.active_ingredients.clear()
            self.show_favorites_only = False
            self._reset_ingredient_checks()
        self._refresh_remedy_list()

    def _on_category_click(self, cat):
        self.active_category = None if self.active_category == cat else cat
        self.active_ingredients.clear()
        self.show_favorites_only = False
        self.symptom_query.set("")
        self._reset_ingredient_checks()
        self._refresh_remedy_list()

    def _on_ingredient_toggle(self):
        self.active_ingredients = {ing for ing, var in self.ingredient_vars.items() if var.get()}
        if self.active_ingredients:
            self.active_category = None
            self.show_favorites_only = False
            self.symptom_query.set("")
        self._refresh_remedy_list()

    def _toggle_favorites_view(self):
        self.show_favorites_only = not self.show_favorites_only
        if self.show_favorites_only:
            self.active_category = None
            self.active_ingredients.clear()
            self.symptom_query.set("")
            self._reset_ingredient_checks()
            self.fav_toggle_btn.configure(text="Show all remedies")
        else:
            self.fav_toggle_btn.configure(text="Show favorites only")
        self._refresh_remedy_list()

    def _clear_filters(self):
        self.active_category = None
        self.active_ingredients.clear()
        self.show_favorites_only = False
        self.symptom_query.set("")
        self._reset_ingredient_checks()
        self.fav_toggle_btn.configure(text="Show favorites only")
        self._refresh_remedy_list()

    def _reset_ingredient_checks(self):
        for var in self.ingredient_vars.values():
            var.set(False)

    def _on_select_remedy(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        remedy_id = int(selection[0])
        self._show_detail(remedy_id)

    def _on_toggle_favorite(self):
        if self.selected_remedy_id is None:
            return
        remedy = next(r for r in self.remedies if r["id"] == self.selected_remedy_id)
        remedy["is_favorite"] = not remedy["is_favorite"]
        toggle_favorite_db(remedy["id"], remedy["is_favorite"])
        self._show_detail(remedy["id"])
        self._refresh_remedy_list(keep_selection=True)

    # -- rendering ------------------------------------------------------

    def _refresh_remedy_list(self, keep_selection=False):
        prev_selection = self.selected_remedy_id if keep_selection else None

        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered = [r for r in self.remedies if self._matches_filters(r)]

        if self.show_favorites_only:
            self.results_title.configure(text="My favorites")
        elif self.active_category:
            self.results_title.configure(text=self.active_category)
        elif self.active_ingredients:
            self.results_title.configure(text="Made with what you have")
        elif self.symptom_query.get().strip():
            self.results_title.configure(text=f'Remedies for "{self.symptom_query.get().strip()}"')
        else:
            self.results_title.configure(text="All remedies")

        noun = "remedy" if len(filtered) == 1 else "remedies"
        self.results_count.configure(text=f"{len(filtered)} {noun}")

        for r in filtered:
            star = "★ " if r["is_favorite"] else ""
            self.tree.insert("", "end", iid=str(r["id"]), values=(star + r["name"], r["category"]))

        if not filtered:
            self.detail_name.configure(text="No remedies match")
            self.detail_cat.configure(text="")
            self._set_detail_text("Try a different symptom, ingredient, or category.")
            self.selected_remedy_id = None
        elif prev_selection and any(r["id"] == prev_selection for r in filtered):
            self.tree.selection_set(str(prev_selection))
            self._show_detail(prev_selection)

    def _show_detail(self, remedy_id):
        remedy = next(r for r in self.remedies if r["id"] == remedy_id)
        self.selected_remedy_id = remedy_id

        self.detail_name.configure(text=remedy["name"])
        color = CATEGORY_COLORS.get(remedy["category"], "#999")
        self.detail_cat.configure(text="  " + remedy["category"] + "  ", bg=color)

        self.fav_btn.configure(
            text="♥ Saved to favorites" if remedy["is_favorite"] else "♡ Add to favorites",
            fg=COLOR_RUST if remedy["is_favorite"] else COLOR_CLAY,
        )

        text = (
            f"INGREDIENTS\n{', '.join(remedy['ingredients'])}\n\n"
            f"METHOD\n{remedy['method']}\n\n"
            f"WHEN TO TAKE\n{remedy['when']}\n\n"
            f"CAUTION\n{remedy['caution']}"
        )
        self._set_detail_text(text)

    def _set_detail_text(self, text):
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.configure(state="disabled")


if __name__ == "__main__":
    init_db()
    app = NuskheApp()
    app.mainloop()
