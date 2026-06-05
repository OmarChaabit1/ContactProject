from models.contact import Contact, INDICATIFS
from models.address_book import AddressBook
from views.contact_gui_view import ContactGUIView
from views.agenda_view import AgendaView
from communication import EmailSender, WhatsAppSender
import tkinter.filedialog as fd
import tkinter.messagebox as mb


class ContactGUIController:
    """CONTROLLER GUI — relie Model, View et modules auxiliaires (Parties 4-9)."""

    def __init__(self, root, username="admin"):
        self.root     = root
        self.username = username
        self.model    = AddressBook()
        self.view     = ContactGUIView(root, username)
        self._bind_events()
        self._refresh_list()

    # ── Liaison événements ────────────────────────────────────────────────────

    def _bind_events(self):
        v = self.view

        v.btn_add.config(command=self._focus_form)
        v.btn_del.config(command=self._supprimer)
        v.btn_show.config(command=self._afficher)
        v.btn_agenda.config(command=self._open_agenda)
        v.btn_export.config(command=self._export_csv)
        v.btn_clear.config(command=self._effacer_form)
        v.btn_submit.config(command=self._ajouter)
        v.btn_send.config(command=self._envoyer_message)

        v.listbox.bind("<<ListboxSelect>>", self._on_select)
        v.combo_pays.bind("<<ComboboxSelected>>", self._on_pays_change)

        # Recherche en temps réel
        v.entry_search.bind("<FocusIn>", self._on_search_focus_in)
        v.entry_search.bind("<FocusOut>", self._on_search_focus_out)
        v.entry_search.bind("<KeyRelease>", self._on_search)

        # Filtre catégorie
        v.combo_cat_filter.bind("<<ComboboxSelected>>", self._on_filter_cat)

    # ── Actions CRUD ──────────────────────────────────────────────────────────

    def _ajouter(self):
        data = self.view.get_form_data()
        pays = self.view.get_pays()
        cat  = self.view.get_categorie()

        if not all([data["nom"], data["prenom"], data["email"], data["numero"]]):
            self.view.set_message("Champs obligatoires (*) non remplis.", succes=False)
            return
        if not pays:
            self.view.set_message("Veuillez sélectionner un pays.", succes=False)
            return

        try:
            contact = Contact(
                nom=data["nom"], prenom=data["prenom"],
                email=data["email"], pays=pays,
                numero_local=data["numero"],
                adresse=data["adresse"],
                fonction=data["fonction"],
                entreprise=data["entreprise"],
                categorie=cat,
            )
            succes, message = self.model.add(contact)
            self.view.set_message(message, succes=succes)
            if succes:
                self._refresh_list()
                self.view.clear_form()
                self.view.set_status(f"Contact '{contact.nom} {contact.prenom}' ajouté.")
        except AssertionError as e:
            self.view.set_message(str(e), succes=False)

    def _supprimer(self):
        nom = self.view.get_selected_nom()
        if not nom:
            self.view.set_status("Sélectionnez un contact dans la liste.")
            return
        contact   = self.model.find(nom)
        nom_exact = contact.nom if contact else nom
        if self.view.confirm_delete(nom_exact):
            succes, message = self.model.remove(nom_exact)
            self.view.set_status(message)
            if succes:
                self._refresh_list()
                self.view.clear_detail()

    def _afficher(self):
        nom = self.view.get_selected_nom()
        if not nom:
            self.view.set_status("Sélectionnez un contact dans la liste.")
            return
        contact = self.model.find(nom)
        if contact:
            self.view.show_detail(contact)
            self.view.set_status(f"Affichage : {contact.nom} {contact.prenom}")

    # ── Agenda (Partie 9) ─────────────────────────────────────────────────────

    def _open_agenda(self):
        contacts = self.model.all()
        AgendaView(self.root, self.model, contacts, self.username)

    # ── Export CSV (Partie 5) ─────────────────────────────────────────────────

    def _export_csv(self):
        filepath = fd.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Tous", "*.*")],
            initialfile="contacts_export.csv",
            title="Exporter les contacts"
        )
        if filepath:
            n = self.model.export_csv(filepath)
            self.view.set_status(f"{n} contact(s) exporté(s) → {filepath}")
            mb.showinfo("Export CSV", f"{n} contact(s) exporté(s) avec succès.")

    # ── Communication (Partie 7) ──────────────────────────────────────────────

    def _envoyer_message(self):
        nom = self.view.get_selected_nom()
        if not nom:
            self.view.set_comm_message("Sélectionnez d'abord un contact dans la liste.",
                                       succes=False)
            return

        contact = self.model.find(nom)
        if not contact:
            self.view.set_comm_message("Contact introuvable.", succes=False)
            return

        data  = self.view.get_comm_data()
        canal = data["canal"]
        msg   = data["message"]

        if not msg:
            self.view.set_comm_message("Le message est vide.", succes=False)
            return

        if canal == "email":
            sender = EmailSender()  # Configurer SMTP dans communication.py
            sujet  = data["sujet"] or f"Message de {self.username}"
            ok, info = sender.send(contact.email, sujet, msg)
        else:
            # WhatsApp : numéro sans +, ex. "212612345678"
            phone = contact.indicatif.replace("+", "") + contact.numero_local
            sender = WhatsAppSender()
            ok, info = sender.send(phone, msg)

        self.view.set_comm_message(info, succes=ok)
        self.view.set_status(info)

    # ── Formulaire ────────────────────────────────────────────────────────────

    def _effacer_form(self):
        self.view.clear_form()
        self.view.set_message("")
        self.view.set_status("Formulaire effacé.")

    def _focus_form(self):
        self.view.notebook.select(0)
        self.view.entries["nom"].focus_set()

    # ── Événements ────────────────────────────────────────────────────────────

    def _on_select(self, event):
        nom = self.view.get_selected_nom()
        if nom:
            contact = self.model.find(nom)
            if contact:
                self.view.show_detail(contact)

    def _on_pays_change(self, event):
        pays = self.view.get_pays()
        if pays in INDICATIFS:
            self.view.set_indicatif(INDICATIFS[pays])

    def _on_search_focus_in(self, event):
        if self.view.entry_search.get() == "🔍 Rechercher…":
            self.view.entry_search.delete(0, "end")
            from views.contact_gui_view import TEXT_MAIN
            self.view.entry_search.config(fg=TEXT_MAIN)

    def _on_search_focus_out(self, event):
        if not self.view.entry_search.get():
            from views.contact_gui_view import TEXT_MUTED
            self.view.entry_search.insert(0, "🔍 Rechercher…")
            self.view.entry_search.config(fg=TEXT_MUTED)

    def _on_search(self, event):
        query = self.view.get_search_query()
        if query:
            contacts = self.model.search(query)
        else:
            cat = self.view.get_cat_filter()
            contacts = self.model.filter_by_category(cat) if cat else self.model.all()
        self.view.update_listbox(contacts)
        self.view.set_status(f"{len(contacts)} résultat(s).")

    def _on_filter_cat(self, event):
        cat = self.view.get_cat_filter()
        contacts = self.model.filter_by_category(cat) if cat else self.model.all()
        self.view.update_listbox(contacts)
        self.view.set_status(f"Filtre : {cat or 'Tous'} — {len(contacts)} contact(s).")

    # ── Rafraîchissement ──────────────────────────────────────────────────────

    def _refresh_list(self):
        cat      = self.view.get_cat_filter()
        contacts = self.model.filter_by_category(cat) if cat else self.model.all()
        self.view.update_listbox(contacts)
        self.view.set_status(f"{len(contacts)} contact(s) chargé(s).")
