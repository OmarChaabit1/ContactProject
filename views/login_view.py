import tkinter as tk
from tkinter import messagebox
from models.address_book import AuthManager

# ── Palette (reprend le thème sombre existant) ───────────────────────────────
BG_DARK   = "#0d1117"
BG_CARD   = "#161b22"
BG_INPUT  = "#0d1117"
NEON      = "#00ff9f"
NEON2     = "#00cfff"
ACCENT    = "#ff4e6a"
TEXT_MAIN = "#c9d1d9"
TEXT_MUTED= "#8b949e"
BORDER    = "#30363d"
BTN_ADD   = "#1a7f4b"

FONT_TITLE = ("Consolas", 14, "bold")
FONT_LABEL = ("Consolas", 10, "bold")
FONT_ENTRY = ("Consolas", 11)
FONT_BTN   = ("Consolas", 10, "bold")
FONT_SUB   = ("Consolas", 9)


class LoginWindow:
    """
    Partie 4 — Fenêtre de connexion administrateur.
    Lance l'application principale si l'authentification réussit.
    """

    def __init__(self, root, on_success):
        self.root       = root
        self.on_success = on_success  # callback appelé après connexion
        self.auth       = AuthManager()
        self._attempts  = 0

        self._build_ui()

    # ── Construction UI ──────────────────────────────────────────────────────

    def _build_ui(self):
        self.root.title("Connexion — Carnet d'Adresses")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("400x420")
        self.root.resizable(False, False)
        self.root.eval("tk::PlaceWindow . center")

        # Titre
        tk.Frame(self.root, bg=NEON, height=3).pack(fill=tk.X)

        header = tk.Frame(self.root, bg=BG_DARK, pady=24)
        header.pack(fill=tk.X)
        tk.Label(header, text="🔐  ACCÈS ADMINISTRATEUR",
                 font=FONT_TITLE, fg=NEON, bg=BG_DARK).pack()
        tk.Label(header, text="Carnet d'Adresses International",
                 font=FONT_SUB, fg=TEXT_MUTED, bg=BG_DARK).pack(pady=(4, 0))

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)

        # Carte formulaire
        card = tk.Frame(self.root, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=30, pady=24)

        # Nom d'utilisateur
        tk.Label(card, text="Nom d'utilisateur", font=FONT_LABEL,
                 fg=NEON2, bg=BG_CARD, anchor="w").pack(fill=tk.X, padx=16, pady=(20, 2))
        self.entry_user = self._make_entry(card)
        self.entry_user.pack(fill=tk.X, padx=16, pady=(0, 10))

        # Mot de passe
        tk.Label(card, text="Mot de passe", font=FONT_LABEL,
                 fg=NEON2, bg=BG_CARD, anchor="w").pack(fill=tk.X, padx=16, pady=(0, 2))
        self.entry_pass = self._make_entry(card, show="●")
        self.entry_pass.pack(fill=tk.X, padx=16, pady=(0, 20))

        # Bouton connexion
        self.btn_login = tk.Button(
            card, text="  SE CONNECTER  ",
            font=FONT_BTN, bg=BTN_ADD, fg="white",
            activebackground="#238956", activeforeground=NEON,
            relief="flat", pady=9, cursor="hand2",
            command=self._login
        )
        self.btn_login.pack(fill=tk.X, padx=16, pady=(0, 10))

        # Message d'erreur
        self.lbl_msg = tk.Label(card, text="", font=FONT_SUB,
                                fg=ACCENT, bg=BG_CARD, wraplength=320)
        self.lbl_msg.pack(pady=(0, 10))

        # Appuyer Entrée = connexion
        self.root.bind("<Return>", lambda e: self._login())
        self.entry_user.focus_set()

        # Footer
        tk.Label(self.root, text="Admin par défaut : admin / admin123",
                 font=FONT_SUB, fg=BORDER, bg=BG_DARK).pack(pady=(0, 8))

    def _make_entry(self, parent, show=None):
        kw = dict(font=FONT_ENTRY, bg=BG_INPUT, fg=TEXT_MAIN,
                  insertbackground=NEON, relief="flat", bd=8,
                  highlightbackground=BORDER, highlightcolor=NEON,
                  highlightthickness=1)
        if show:
            kw["show"] = show
        return tk.Entry(parent, **kw)

    # ── Logique ──────────────────────────────────────────────────────────────

    def _login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()

        if not username or not password:
            self.lbl_msg.config(text="Veuillez remplir tous les champs.")
            return

        if self.auth.verify(username, password):
            self.root.unbind("<Return>")
            self.root.destroy()
            self.on_success(username)
        else:
            self._attempts += 1
            if self._attempts >= 5:
                self.lbl_msg.config(text="Trop de tentatives. Fermeture.")
                self.root.after(1500, self.root.destroy)
            else:
                remaining = 5 - self._attempts
                self.lbl_msg.config(
                    text=f"Identifiants incorrects. ({remaining} essai(s) restant(s))")
            self.entry_pass.delete(0, tk.END)
