import tkinter as tk
from tkinter import ttk, messagebox
from models.contact import INDICATIFS, CATEGORIES

# ── Palette ──────────────────────────────────────────────────────────────────
BG_DARK    = "#0d1117"
BG_CARD    = "#161b22"
BG_INPUT   = "#0d1117"
NEON       = "#00ff9f"
NEON2      = "#00cfff"
ACCENT     = "#ff4e6a"
TEXT_MAIN  = "#c9d1d9"
TEXT_MUTED = "#8b949e"
BORDER     = "#30363d"
BTN_ADD    = "#1a7f4b"
BTN_DEL    = "#8b1a2e"
BTN_SHOW   = "#1a4f7f"
BTN_AGENDA = "#4f2d7f"
BTN_EXPORT = "#2d4a7f"

FONT_TITLE  = ("Consolas", 16, "bold")
FONT_SUB    = ("Consolas", 10)
FONT_LABEL  = ("Consolas", 10, "bold")
FONT_ENTRY  = ("Consolas", 10)
FONT_LIST   = ("Consolas", 11)
FONT_BTN    = ("Consolas", 10, "bold")
FONT_DETAIL = ("Consolas", 10)


class ContactGUIView:
    """VIEW Tkinter enrichie (Parties 4-9)."""

    def __init__(self, root, username="admin"):
        self.root     = root
        self.username = username
        self._setup_window()
        self._build_ui()

    # ── Fenêtre ──────────────────────────────────────────────────────────────

    def _setup_window(self):
        self.root.title(f"Carnet d'Adresses International — {self.username}")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1150x750")
        self.root.minsize(950, 620)
        self.root.resizable(True, True)

    # ── Construction UI ──────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_top_frame()
        self._build_main_frame()
        self._build_status_bar()

    def _build_top_frame(self):
        top = tk.Frame(self.root, bg=BG_DARK, pady=12)
        top.pack(fill=tk.X)

        tk.Label(top, text="[ CARNET D'ADRESSES INTERNATIONAL ]",
                 font=("Consolas", 17, "bold"),
                 fg=NEON, bg=BG_DARK).pack()
        tk.Label(top, text=f"MVC · SQLite · Tkinter · Flask · Python  |  Admin : {self.username}",
                 font=FONT_SUB, fg=TEXT_MUTED, bg=BG_DARK).pack()

        tk.Frame(self.root, bg=NEON, height=2).pack(fill=tk.X)

    def _build_main_frame(self):
        main = tk.Frame(self.root, bg=BG_DARK)
        main.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=4)
        main.rowconfigure(0, weight=1)

        self._build_list_panel(main)
        self._build_form_panel(main)

    # ── Panel gauche ─────────────────────────────────────────────────────────

    def _build_list_panel(self, parent):
        panel = tk.Frame(parent, bg=BG_CARD, bd=0,
                         highlightbackground=BORDER, highlightthickness=1)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        panel.rowconfigure(2, weight=1)
        panel.columnconfigure(0, weight=1)

        # En-tête
        hdr = tk.Frame(panel, bg=BG_CARD, pady=8)
        hdr.grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(hdr, text="▸ CONTACTS", font=FONT_LABEL,
                 fg=NEON2, bg=BG_CARD).pack(side=tk.LEFT)
        self.lbl_count = tk.Label(hdr, text="(0)", font=FONT_SUB,
                                  fg=TEXT_MUTED, bg=BG_CARD)
        self.lbl_count.pack(side=tk.LEFT, padx=6)

        # Recherche + filtre catégorie
        search_row = tk.Frame(panel, bg=BG_CARD)
        search_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 4))
        search_row.columnconfigure(0, weight=1)

        self.entry_search = tk.Entry(search_row, font=FONT_ENTRY,
                                     bg=BG_INPUT, fg=TEXT_MAIN,
                                     insertbackground=NEON,
                                     relief="flat", bd=5,
                                     highlightbackground=BORDER,
                                     highlightcolor=NEON2,
                                     highlightthickness=1)
        self.entry_search.insert(0, "🔍 Rechercher…")
        self.entry_search.config(fg=TEXT_MUTED)
        self.entry_search.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.combo_cat_filter = ttk.Combobox(
            search_row, font=FONT_ENTRY,
            values=["Tous"] + CATEGORIES, state="readonly")
        self.combo_cat_filter.current(0)
        self.combo_cat_filter.grid(row=1, column=0, sticky="ew")

        # Listbox
        list_frame = tk.Frame(panel, bg=BG_CARD)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(4, 4))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        scrollbar = tk.Scrollbar(list_frame, bg=BG_CARD,
                                 troughcolor=BG_DARK, activebackground=NEON)
        self.listbox = tk.Listbox(
            list_frame, font=FONT_LIST,
            bg=BG_INPUT, fg=TEXT_MAIN,
            selectbackground=NEON, selectforeground=BG_DARK,
            activestyle="none", bd=0, highlightthickness=0,
            yscrollcommand=scrollbar.set, cursor="hand2"
        )
        scrollbar.config(command=self.listbox.yview)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Boutons
        btn_frame = tk.Frame(panel, bg=BG_CARD, pady=8)
        btn_frame.grid(row=3, column=0, sticky="ew", padx=10)

        self.btn_add    = self._make_btn(btn_frame, "＋  Ajouter",    BTN_ADD,    None)
        self.btn_del    = self._make_btn(btn_frame, "－  Supprimer",  BTN_DEL,    None)
        self.btn_show   = self._make_btn(btn_frame, "◎  Afficher",   BTN_SHOW,   None)
        self.btn_agenda = self._make_btn(btn_frame, "📅  Agenda",     BTN_AGENDA, None)
        self.btn_export = self._make_btn(btn_frame, "⬇  Export CSV", BTN_EXPORT, None)
        self.btn_clear  = self._make_btn(btn_frame, "⟳  Effacer",    "#2d333b",  None)

        for b in (self.btn_add, self.btn_del, self.btn_show,
                  self.btn_agenda, self.btn_export, self.btn_clear):
            b.pack(fill=tk.X, pady=2)

    # ── Panel droit ───────────────────────────────────────────────────────────

    def _build_form_panel(self, parent):
        panel = tk.Frame(parent, bg=BG_CARD, bd=0,
                         highlightbackground=BORDER, highlightthickness=1)
        panel.grid(row=0, column=1, sticky="nsew")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TNotebook", background=BG_CARD, borderwidth=0)
        style.configure("Dark.TNotebook.Tab",
                        background=BG_DARK, foreground=TEXT_MUTED,
                        font=FONT_LABEL, padding=[12, 6])
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", BG_CARD)],
                  foreground=[("selected", NEON)])

        self.notebook = ttk.Notebook(panel, style="Dark.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Onglet Formulaire
        tab_form = tk.Frame(self.notebook, bg=BG_CARD)
        self.notebook.add(tab_form, text=" ✎  Formulaire ")
        self._build_form_fields(tab_form)

        # Onglet Détail
        tab_detail = tk.Frame(self.notebook, bg=BG_CARD)
        self.notebook.add(tab_detail, text=" ◎  Détail ")
        self._build_detail_tab(tab_detail)

        # Onglet Communication (Partie 7)
        tab_comm = tk.Frame(self.notebook, bg=BG_CARD)
        self.notebook.add(tab_comm, text=" ✉  Communication ")
        self._build_comm_tab(tab_comm)

    def _build_form_fields(self, parent):
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(3, weight=1)

        champs_g = [
            ("Nom *",                "nom"),
            ("Prénom *",             "prenom"),
            ("Email *",              "email"),
            ("Numéro * (10 chiffres)","numero"),
        ]
        champs_d = [
            ("Adresse",   "adresse"),
            ("Fonction",  "fonction"),
            ("Entreprise","entreprise"),
        ]

        self.entries = {}
        for i, (label, key) in enumerate(champs_g):
            color = NEON if "*" in label else TEXT_MUTED
            tk.Label(parent, text=label, font=FONT_LABEL,
                     fg=color, bg=BG_CARD, anchor="w"
                     ).grid(row=i, column=0, sticky="w", padx=(12, 4), pady=4)
            e = self._make_entry(parent)
            e.grid(row=i, column=1, sticky="ew", padx=(0, 12), pady=4)
            self.entries[key] = e

        for i, (label, key) in enumerate(champs_d):
            tk.Label(parent, text=label, font=FONT_LABEL,
                     fg=TEXT_MUTED, bg=BG_CARD, anchor="w"
                     ).grid(row=i, column=2, sticky="w", padx=(8, 4), pady=4)
            e = self._make_entry(parent)
            e.grid(row=i, column=3, sticky="ew", padx=(0, 12), pady=4)
            self.entries[key] = e

        # Ligne pays
        row_pays = max(len(champs_g), len(champs_d))
        tk.Label(parent, text="Pays *", font=FONT_LABEL,
                 fg=NEON, bg=BG_CARD, anchor="w"
                 ).grid(row=row_pays, column=0, sticky="w", padx=(12, 4), pady=4)

        style = ttk.Style()
        style.configure("Dark.TCombobox",
                        fieldbackground=BG_INPUT, background=BG_CARD,
                        foreground=TEXT_MAIN, selectbackground=NEON,
                        selectforeground=BG_DARK, arrowcolor=NEON)

        self.combo_pays = ttk.Combobox(parent, values=sorted(INDICATIFS.keys()),
                                       font=FONT_ENTRY, style="Dark.TCombobox",
                                       state="readonly")
        self.combo_pays.grid(row=row_pays, column=1, sticky="ew", padx=(0, 12), pady=4)

        # Indicatif
        tk.Label(parent, text="Indicatif", font=FONT_LABEL,
                 fg=TEXT_MUTED, bg=BG_CARD, anchor="w"
                 ).grid(row=row_pays, column=2, sticky="w", padx=(8, 4), pady=4)
        self.lbl_indicatif = tk.Label(parent, text="—", font=FONT_ENTRY,
                                      fg=NEON2, bg=BG_CARD, anchor="w")
        self.lbl_indicatif.grid(row=row_pays, column=3, sticky="w", padx=(4, 12), pady=4)

        # Catégorie (Partie 8)
        row_cat = row_pays + 1
        tk.Label(parent, text="Catégorie", font=FONT_LABEL,
                 fg=NEON2, bg=BG_CARD, anchor="w"
                 ).grid(row=row_cat, column=0, sticky="w", padx=(12, 4), pady=4)

        self.combo_categorie = ttk.Combobox(parent, values=CATEGORIES,
                                            font=FONT_ENTRY, style="Dark.TCombobox",
                                            state="readonly")
        self.combo_categorie.current(CATEGORIES.index("Autre"))
        self.combo_categorie.grid(row=row_cat, column=1, sticky="ew", padx=(0, 12), pady=4)

        # Bouton enregistrer
        row_btn = row_cat + 1
        self.btn_submit = self._make_btn(parent, "＋  ENREGISTRER LE CONTACT", BTN_ADD, None)
        self.btn_submit.grid(row=row_btn, column=0, columnspan=4,
                             sticky="ew", padx=12, pady=(12, 4))

        self.lbl_msg = tk.Label(parent, text="", font=FONT_SUB,
                                fg=ACCENT, bg=BG_CARD, wraplength=500, justify="left")
        self.lbl_msg.grid(row=row_btn+1, column=0, columnspan=4,
                          sticky="w", padx=12, pady=4)

    def _build_detail_tab(self, parent):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        self.detail_text = tk.Text(
            parent, font=FONT_DETAIL,
            bg=BG_INPUT, fg=TEXT_MAIN,
            insertbackground=NEON,
            relief="flat", bd=8,
            state="disabled", cursor="arrow", wrap=tk.WORD
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.detail_text.tag_config("key",   foreground=NEON2)
        self.detail_text.tag_config("value", foreground=TEXT_MAIN)
        self.detail_text.tag_config("title", foreground=NEON,
                                    font=("Consolas", 12, "bold"))
        self.detail_text.tag_config("cat",   foreground=ACCENT)
        self.detail_text.tag_config("sep",   foreground=BORDER)

    def _build_comm_tab(self, parent):
        """Partie 7 — Module de communication (Email / WhatsApp)."""
        parent.columnconfigure(0, weight=1)

        tk.Label(parent, text="✉  ENVOYER UN MESSAGE AU CONTACT",
                 font=FONT_LABEL, fg=NEON, bg=BG_CARD
                 ).pack(pady=(14, 4), padx=12, anchor="w")

        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=12)

        # Sélection du canal
        canal_frame = tk.Frame(parent, bg=BG_CARD)
        canal_frame.pack(fill=tk.X, padx=12, pady=8)

        tk.Label(canal_frame, text="Canal :", font=FONT_LABEL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(side=tk.LEFT)

        self.var_canal = tk.StringVar(value="email")
        for val, lbl in [("email", "📧  Email"), ("whatsapp", "💬  WhatsApp")]:
            tk.Radiobutton(canal_frame, text=lbl, variable=self.var_canal,
                           value=val, font=FONT_ENTRY,
                           bg=BG_CARD, fg=TEXT_MAIN,
                           selectcolor=BG_DARK,
                           activebackground=BG_CARD,
                           activeforeground=NEON).pack(side=tk.LEFT, padx=12)

        # Sujet (email seulement)
        self.frame_sujet = tk.Frame(parent, bg=BG_CARD)
        self.frame_sujet.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(self.frame_sujet, text="Sujet :", font=FONT_LABEL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(side=tk.LEFT)
        self.entry_sujet = self._make_entry_raw(self.frame_sujet)
        self.entry_sujet.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        # Corps du message
        tk.Label(parent, text="Message :", font=FONT_LABEL,
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=12, pady=(8, 2))

        self.text_msg_body = tk.Text(
            parent, font=FONT_ENTRY, height=7,
            bg=BG_INPUT, fg=TEXT_MAIN,
            insertbackground=NEON, relief="flat", bd=6,
            highlightbackground=BORDER, highlightcolor=NEON, highlightthickness=1
        )
        self.text_msg_body.pack(fill=tk.X, padx=12, pady=(0, 8))

        # Bouton envoyer
        self.btn_send = self._make_btn(parent, "✉  ENVOYER", BTN_ADD, None)
        self.btn_send.pack(fill=tk.X, padx=12, pady=(0, 6))

        self.lbl_comm_msg = tk.Label(parent, text="", font=FONT_SUB,
                                     fg=NEON, bg=BG_CARD, wraplength=500)
        self.lbl_comm_msg.pack(padx=12, pady=(0, 6), anchor="w")

        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=12)

        info = ("Note : l'envoi d'email utilise smtplib (SMTP).\n"
                "L'envoi WhatsApp utilise l'URL wa.me avec le navigateur.")
        tk.Label(parent, text=info, font=FONT_SUB,
                 fg=TEXT_MUTED, bg=BG_CARD, justify="left"
                 ).pack(anchor="w", padx=12, pady=8)

    # ── Barre de statut ───────────────────────────────────────────────────────

    def _build_status_bar(self):
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)
        bar = tk.Frame(self.root, bg=BG_DARK, pady=5)
        bar.pack(fill=tk.X, padx=16)

        self.lbl_status = tk.Label(bar, text="Prêt.",
                                   font=FONT_SUB, fg=TEXT_MUTED, bg=BG_DARK)
        self.lbl_status.pack(side=tk.LEFT)

        tk.Label(bar, text="MVC · SQLite · Tkinter · Flask · Python",
                 font=FONT_SUB, fg=BORDER, bg=BG_DARK).pack(side=tk.RIGHT)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_btn(self, parent, text, color, cmd):
        return tk.Button(parent, text=text, font=FONT_BTN,
                         bg=color, fg="white",
                         activebackground=color, activeforeground=NEON,
                         relief="flat", bd=0, pady=7,
                         cursor="hand2", command=cmd)

    def _make_entry(self, parent):
        return tk.Entry(parent, font=FONT_ENTRY,
                        bg=BG_INPUT, fg=TEXT_MAIN,
                        insertbackground=NEON, relief="flat", bd=6,
                        highlightbackground=BORDER, highlightcolor=NEON,
                        highlightthickness=1)

    def _make_entry_raw(self, parent):
        return tk.Entry(parent, font=FONT_ENTRY,
                        bg=BG_INPUT, fg=TEXT_MAIN,
                        insertbackground=NEON, relief="flat", bd=6,
                        highlightbackground=BORDER, highlightcolor=NEON,
                        highlightthickness=1)

    # ── API publique ──────────────────────────────────────────────────────────

    def get_form_data(self):
        return {k: e.get().strip() for k, e in self.entries.items()}

    def get_pays(self):
        return self.combo_pays.get()

    def get_categorie(self):
        return self.combo_categorie.get()

    def get_search_query(self):
        val = self.entry_search.get()
        if val == "🔍 Rechercher…":
            return ""
        return val.strip()

    def get_cat_filter(self):
        val = self.combo_cat_filter.get()
        return "" if val == "Tous" else val

    def clear_form(self):
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.combo_pays.set("")
        self.lbl_indicatif.config(text="—")
        self.lbl_msg.config(text="", fg=ACCENT)
        self.combo_categorie.current(CATEGORIES.index("Autre"))

    def set_indicatif(self, indicatif):
        self.lbl_indicatif.config(text=indicatif)

    def set_message(self, msg, succes=True):
        self.lbl_msg.config(text=msg, fg=NEON if succes else ACCENT)

    def set_status(self, msg):
        self.lbl_status.config(text=msg)

    def set_comm_message(self, msg, succes=True):
        self.lbl_comm_msg.config(text=msg, fg=NEON if succes else ACCENT)

    def update_listbox(self, contacts):
        self.listbox.delete(0, tk.END)
        for c in contacts:
            cat_badge = f"[{c.categorie[:3].upper()}]"
            self.listbox.insert(tk.END, f"  {cat_badge} {c.nom.upper()}, {c.prenom}")
        self.lbl_count.config(text=f"({len(contacts)})")

    def get_selected_nom(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        item = self.listbox.get(sel[0]).strip()
        # Supprimer le badge catégorie ex: "[PAT] NOM, Prenom"
        if item.startswith("["):
            item = item.split("] ", 1)[-1]
        return item.split(",")[0].strip().capitalize()

    def show_detail(self, contact):
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", tk.END)

        self.detail_text.insert(tk.END, "── FICHE CONTACT ──\n\n", "title")

        champs = [
            ("Nom",        contact.nom),
            ("Prénom",     contact.prenom),
            ("Email",      contact.email),
            ("Pays",       contact.pays),
            ("Téléphone",  contact.telephone),
            ("Catégorie",  contact.categorie),
        ]
        for label, valeur in champs:
            self.detail_text.insert(tk.END, f"{label:<12}: ", "key")
            tag = "cat" if label == "Catégorie" else "value"
            self.detail_text.insert(tk.END, f"{valeur}\n", tag)

        for label, valeur in [("Adresse", contact.adresse),
                               ("Fonction", contact.fonction),
                               ("Entreprise", contact.entreprise)]:
            if valeur:
                self.detail_text.insert(tk.END, f"{label:<12}: ", "key")
                self.detail_text.insert(tk.END, f"{valeur}\n", "value")

        self.detail_text.config(state="disabled")
        self.notebook.select(1)

    def clear_detail(self):
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.config(state="disabled")

    def confirm_delete(self, nom):
        return messagebox.askyesno("Confirmer la suppression",
                                   f"Supprimer le contact '{nom}' ?",
                                   parent=self.root)

    def get_comm_data(self):
        return {
            "canal":   self.var_canal.get(),
            "sujet":   self.entry_sujet.get().strip(),
            "message": self.text_msg_body.get("1.0", tk.END).strip(),
        }
