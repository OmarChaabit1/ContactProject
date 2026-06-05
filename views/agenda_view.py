import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import date, datetime

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
SLOT_FREE  = "#1c2b1c"
SLOT_TAKEN = "#3b1a1a"

FONT_TITLE  = ("Consolas", 13, "bold")
FONT_LABEL  = ("Consolas", 10, "bold")
FONT_ENTRY  = ("Consolas", 10)
FONT_BTN    = ("Consolas", 9, "bold")
FONT_SLOT   = ("Consolas", 9)
FONT_SUB    = ("Consolas", 9)

# Créneaux de 30 min de 08:00 à 18:00
CRENEAUX = []
for h in range(8, 18):
    CRENEAUX.append(f"{h:02d}:00")
    CRENEAUX.append(f"{h:02d}:30")


class AgendaView(tk.Toplevel):
    """
    Partie 9 — Agenda avec créneaux de 30 min.
    Les créneaux déjà réservés sont désactivés.
    """

    def __init__(self, parent, model, contacts, username="admin"):
        super().__init__(parent)
        self.model    = model
        self.contacts = contacts
        self.username = username

        self._sel_date  = date.today()
        self._sel_year  = self._sel_date.year
        self._sel_month = self._sel_date.month

        self.title("📅  Agenda — Gestion des RDV")
        self.configure(bg=BG_DARK)
        self.geometry("900x640")
        self.resizable(True, True)
        self.grab_set()

        self._build_ui()
        self._refresh()

    # ── Construction UI ──────────────────────────────────────────────────────

    def _build_ui(self):
        tk.Frame(self, bg=NEON, height=2).pack(fill=tk.X)

        top = tk.Frame(self, bg=BG_DARK, pady=10)
        top.pack(fill=tk.X, padx=16)
        tk.Label(top, text="[ AGENDA — GESTION DES RDV ]",
                 font=FONT_TITLE, fg=NEON, bg=BG_DARK).pack(side=tk.LEFT)

        tk.Frame(self, bg=BORDER, height=1).pack(fill=tk.X)

        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        self._build_calendar(main)
        self._build_slots(main)

    # ── Calendrier ────────────────────────────────────────────────────────────

    def _build_calendar(self, parent):
        cal_frame = tk.Frame(parent, bg=BG_CARD,
                             highlightbackground=BORDER, highlightthickness=1)
        cal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Navigation mois
        nav = tk.Frame(cal_frame, bg=BG_CARD)
        nav.pack(fill=tk.X, padx=8, pady=(10, 4))

        tk.Button(nav, text="◀", font=FONT_BTN, bg=BG_INPUT, fg=NEON2,
                  relief="flat", cursor="hand2",
                  command=self._prev_month).pack(side=tk.LEFT)

        self.lbl_month = tk.Label(nav, text="", font=FONT_LABEL,
                                  fg=NEON, bg=BG_CARD)
        self.lbl_month.pack(side=tk.LEFT, expand=True)

        tk.Button(nav, text="▶", font=FONT_BTN, bg=BG_INPUT, fg=NEON2,
                  relief="flat", cursor="hand2",
                  command=self._next_month).pack(side=tk.RIGHT)

        # Jours de la semaine
        days_fr = ["Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"]
        day_hdr = tk.Frame(cal_frame, bg=BG_CARD)
        day_hdr.pack(fill=tk.X, padx=8)
        for d in days_fr:
            tk.Label(day_hdr, text=d, font=FONT_SLOT, fg=TEXT_MUTED,
                     bg=BG_CARD, width=4).pack(side=tk.LEFT)

        # Grille des jours
        self.cal_grid = tk.Frame(cal_frame, bg=BG_CARD)
        self.cal_grid.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        # Bouton "Aujourd'hui"
        tk.Button(cal_frame, text="Aujourd'hui", font=FONT_BTN,
                  bg=BTN_ADD, fg="white", relief="flat", cursor="hand2",
                  command=self._go_today).pack(pady=(0, 10))

    def _build_slots(self, parent):
        right = tk.Frame(parent, bg=BG_CARD,
                         highlightbackground=BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        # En-tête
        hdr = tk.Frame(right, bg=BG_CARD, pady=8)
        hdr.pack(fill=tk.X, padx=12)
        self.lbl_sel_date = tk.Label(hdr, text="", font=FONT_LABEL,
                                     fg=NEON2, bg=BG_CARD)
        self.lbl_sel_date.pack(side=tk.LEFT)

        # Canvas scrollable pour les créneaux
        canvas = tk.Canvas(right, bg=BG_CARD, highlightthickness=0)
        scrollbar = tk.Scrollbar(right, orient="vertical", command=canvas.yview)
        self.slots_frame = tk.Frame(canvas, bg=BG_CARD)

        self.slots_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.slots_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0), pady=(0, 8))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 8), padx=(0, 8))

        # Formulaire rapide en bas
        form = tk.Frame(right, bg=BG_CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill=tk.X, padx=12, pady=(0, 12))

        tk.Label(form, text="Contact :", font=FONT_LABEL,
                 fg=TEXT_MUTED, bg=BG_CARD).grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.combo_contact = ttk.Combobox(form, font=FONT_ENTRY, state="readonly", width=25)
        self.combo_contact.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=4)

        tk.Label(form, text="Notes :", font=FONT_LABEL,
                 fg=TEXT_MUTED, bg=BG_CARD).grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.entry_notes = tk.Entry(form, font=FONT_ENTRY,
                                    bg=BG_INPUT, fg=TEXT_MAIN,
                                    insertbackground=NEON, relief="flat", bd=6,
                                    highlightbackground=BORDER, highlightcolor=NEON,
                                    highlightthickness=1)
        self.entry_notes.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=4)

        self.lbl_sel_slot = tk.Label(form, text="Créneau : aucun sélectionné",
                                     font=FONT_SUB, fg=NEON2, bg=BG_CARD)
        self.lbl_sel_slot.grid(row=2, column=0, columnspan=2, sticky="w", padx=8)

        tk.Button(form, text="✔  RÉSERVER", font=FONT_BTN,
                  bg=BTN_ADD, fg="white", relief="flat", cursor="hand2",
                  command=self._reserver).grid(row=3, column=0, columnspan=2,
                                               sticky="ew", padx=8, pady=6)

        self.lbl_msg = tk.Label(right, text="", font=FONT_SUB,
                                fg=ACCENT, bg=BG_CARD)
        self.lbl_msg.pack(pady=(0, 6))

        form.columnconfigure(1, weight=1)
        self._sel_slot = None

    # ── Logique calendrier ────────────────────────────────────────────────────

    def _prev_month(self):
        if self._sel_month == 1:
            self._sel_month = 12
            self._sel_year -= 1
        else:
            self._sel_month -= 1
        self._refresh_calendar()

    def _next_month(self):
        if self._sel_month == 12:
            self._sel_month = 1
            self._sel_year += 1
        else:
            self._sel_month += 1
        self._refresh_calendar()

    def _go_today(self):
        today = date.today()
        self._sel_year  = today.year
        self._sel_month = today.month
        self._sel_date  = today
        self._refresh()

    def _select_date(self, d):
        self._sel_date = d
        self._refresh_slots()
        self._refresh_calendar()

    def _refresh_calendar(self):
        MOIS_FR = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                   "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.lbl_month.config(
            text=f"{MOIS_FR[self._sel_month-1]} {self._sel_year}")

        for w in self.cal_grid.winfo_children():
            w.destroy()

        cal = calendar.monthcalendar(self._sel_year, self._sel_month)
        today = date.today()

        for week in cal:
            row_frame = tk.Frame(self.cal_grid, bg=BG_CARD)
            row_frame.pack(fill=tk.X)
            for day_num in week:
                if day_num == 0:
                    tk.Label(row_frame, text="  ", font=FONT_SLOT,
                             bg=BG_CARD, width=4).pack(side=tk.LEFT)
                else:
                    d = date(self._sel_year, self._sel_month, day_num)
                    is_sel   = (d == self._sel_date)
                    is_today = (d == today)
                    fg = BG_DARK if is_sel else (NEON if is_today else TEXT_MAIN)
                    bg = NEON if is_sel else (BG_CARD if not is_today else "#1a2a1a")

                    btn = tk.Button(
                        row_frame, text=str(day_num),
                        font=FONT_SLOT, fg=fg, bg=bg,
                        width=3, relief="flat", cursor="hand2",
                        command=lambda dd=d: self._select_date(dd)
                    )
                    btn.pack(side=tk.LEFT, padx=1, pady=1)

    def _refresh_slots(self):
        for w in self.slots_frame.winfo_children():
            w.destroy()

        date_str = self._sel_date.strftime("%Y-%m-%d")
        self.lbl_sel_date.config(
            text=f"📅  {self._sel_date.strftime('%d/%m/%Y')}")

        occupied = self.model.get_occupied_slots(date_str)
        rdv_list = self.model.get_rdv_by_date(date_str)
        rdv_by_hour = {r["heure"]: r for r in rdv_list}

        self._sel_slot = None
        self.lbl_sel_slot.config(text="Créneau : aucun sélectionné")
        self._slot_btns = {}

        for slot in CRENEAUX:
            is_taken = slot in occupied
            row = tk.Frame(self.slots_frame, bg=SLOT_TAKEN if is_taken else SLOT_FREE,
                           highlightbackground=BORDER, highlightthickness=1)
            row.pack(fill=tk.X, padx=4, pady=2)

            time_lbl = tk.Label(row, text=slot, font=FONT_SLOT,
                                fg=ACCENT if is_taken else NEON,
                                bg=SLOT_TAKEN if is_taken else SLOT_FREE,
                                width=7, anchor="w")
            time_lbl.pack(side=tk.LEFT, padx=(8, 0))

            if is_taken and slot in rdv_by_hour:
                rdv = rdv_by_hour[slot]
                info = f"{rdv.get('nom','?')} {rdv.get('prenom','')}"
                if rdv.get("notes"):
                    info += f"  — {rdv['notes']}"
                tk.Label(row, text=info, font=FONT_SLOT,
                         fg=TEXT_MUTED, bg=SLOT_TAKEN).pack(side=tk.LEFT, padx=8)

                # Bouton supprimer RDV
                tk.Button(row, text="✕", font=FONT_SLOT,
                          bg=BTN_DEL, fg="white", relief="flat", cursor="hand2",
                          command=lambda rid=rdv["id"]: self._delete_rdv(rid)
                          ).pack(side=tk.RIGHT, padx=4)
            else:
                btn = tk.Button(row, text="Réserver",
                                font=FONT_SLOT, bg=BTN_ADD, fg="white",
                                relief="flat", cursor="hand2",
                                command=lambda s=slot: self._quick_reserve(s))
                btn.pack(side=tk.RIGHT, padx=4)
                self._slot_btns[slot] = btn

    def _refresh(self):
        # Mettre à jour combobox contacts
        self.contacts = self.model.all()
        self.combo_contact["values"] = [
            f"{c.nom} {c.prenom}" for c in self.contacts]
        self._refresh_calendar()
        self._refresh_slots()

    # ── Actions ───────────────────────────────────────────────────────────────

    def _quick_reserve(self, slot):
        self._sel_slot = slot
        self.lbl_sel_slot.config(text=f"Créneau sélectionné : {slot}")
        self.lbl_msg.config(text="")

    def _reserver(self):
        if not self._sel_slot:
            self.lbl_msg.config(text="Sélectionnez un créneau en cliquant sur 'Réserver'.")
            return

        idx = self.combo_contact.current()
        contact_id = self.contacts[idx]._id if idx >= 0 else None

        notes   = self.entry_notes.get().strip()
        date_str = self._sel_date.strftime("%Y-%m-%d")

        ok, msg = self.model.add_rdv(contact_id, date_str, self._sel_slot, notes)
        self.lbl_msg.config(text=msg, fg=NEON if ok else ACCENT)
        if ok:
            self._sel_slot = None
            self.lbl_sel_slot.config(text="Créneau : aucun sélectionné")
            self.entry_notes.delete(0, tk.END)
            self._refresh_slots()

    def _delete_rdv(self, rdv_id):
        if messagebox.askyesno("Supprimer RDV", "Annuler ce rendez-vous ?", parent=self):
            self.model.delete_rdv(rdv_id)
            self._refresh_slots()
