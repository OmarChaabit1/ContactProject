# Carnet d'Adresses International — Parties 4 à 9

## Structure du projet

```
mini projet/
├── models/
│   ├── contact.py           # Modèle Contact (+ catégories — Partie 8)
│   └── address_book.py      # SQLite CRUD + AuthManager (Parties 4 & 5)
├── views/
│   ├── login_view.py        # Fenêtre de connexion Tkinter (Partie 4)
│   ├── contact_gui_view.py  # Interface principale Tkinter (Parties 4-9)
│   └── agenda_view.py       # Agenda / RDV Tkinter (Partie 9)
├── controllers/
│   └── contact_gui_controller.py  # Contrôleur MVC enrichi
├── flask_app/
│   ├── app.py               # Application Flask (Partie 6)
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── index.html
│       ├── form.html
│       └── agenda.html
├── communication.py         # Email SMTP + WhatsApp wa.me (Partie 7)
├── main_gui.py              # Lancement Tkinter (avec login)
└── requirements.txt
```

## Installation

```bash
pip install bcrypt flask
```

## Lancement

### Interface Tkinter (Parties 4-9)
```bash
python main_gui.py
```
- Connexion admin par défaut : `admin` / `admin123`

### Interface Web Flask (Partie 6)
```bash
cd flask_app
python app.py
```
- Accès : http://localhost:5000
- Connexion : `admin` / `admin123`

---

## Fonctionnalités par partie

### Partie 4 — Authentification
- Fenêtre de connexion Tkinter (`views/login_view.py`)
- Hachage des mots de passe avec **bcrypt**
- Table `admins` en SQLite
- Blocage après 5 tentatives échouées

### Partie 5 — SQLite
- Base `carnet.db` créée automatiquement
- Tables : `contacts`, `admins`, `rendezvous`
- Export CSV depuis la base
- Recherche fulltext (nom, prénom, email)

### Partie 6 — Flask
- CRUD complet via navigateur
- Authentification session Flask
- Filtre par catégorie et recherche
- Export CSV depuis la liste

### Partie 7 — Communication
- **Email** : envoi via SMTP (`smtplib`)
  - Configurer `smtp_user` et `smtp_pass` dans `communication.py`
- **WhatsApp** : ouverture `wa.me/?text=...` dans le navigateur

### Partie 8 — Catégories & champs enrichis
- Catégories : Patient, Fournisseur, Laboratoire, Client, Entreprise, Autre
- Champs : adresse, fonction, entreprise
- Filtre par catégorie dans la liste et sur Flask

### Partie 9 — Agenda RDV
- Calendrier mensuel interactif (Tkinter)
- Créneaux de 30 min de 08h00 à 18h00
- Créneaux réservés désactivés (visuellement)
- Association contact ↔ RDV
- Suppression de RDV
- Disponible aussi dans Flask (`/agenda`)

---

## Configuration Email (Partie 7)

Dans `communication.py`, modifier `EmailSender` :

```python
EmailSender(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    smtp_user="votre@gmail.com",
    smtp_pass="votre_mot_de_passe_app"
)
```

Pour Gmail, activer la validation 2FA et générer un "mot de passe d'application".
