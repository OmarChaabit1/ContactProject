import sqlite3
import csv
import bcrypt
from models.contact import Contact

DB_PATH = "carnet.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée les tables si elles n'existent pas encore (Parties 4 & 5)."""
    conn = get_connection()
    cur = conn.cursor()

    # Table contacts
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nom         TEXT NOT NULL,
            prenom      TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            pays        TEXT NOT NULL,
            numero_local TEXT NOT NULL,
            adresse     TEXT DEFAULT '',
            fonction    TEXT DEFAULT '',
            entreprise  TEXT DEFAULT '',
            categorie   TEXT DEFAULT 'Autre'
        )
    """)

    # Table admins (Partie 4 — mots de passe hachés avec bcrypt)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Table rendez-vous (Partie 9)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rendezvous (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            date       TEXT NOT NULL,
            heure      TEXT NOT NULL,
            notes      TEXT DEFAULT '',
            FOREIGN KEY(contact_id) REFERENCES contacts(id)
        )
    """)

    conn.commit()

    # Créer un admin par défaut si la table est vide
    cur.execute("SELECT COUNT(*) FROM admins")
    if cur.fetchone()[0] == 0:
        _create_admin(cur, "admin", "admin123")
        conn.commit()

    conn.close()


def _create_admin(cur, username, password):
    """Hache le mot de passe avec bcrypt et insère l'admin."""
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cur.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                (username, hashed))


# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTIFICATION (Partie 4)
# ─────────────────────────────────────────────────────────────────────────────

class AuthManager:
    """Gestion de l'authentification des administrateurs."""

    def verify(self, username, password):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM admins WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        if row is None:
            return False
        return bcrypt.checkpw(password.encode(), row["password"].encode())

    def create_admin(self, username, password):
        conn = get_connection()
        cur = conn.cursor()
        try:
            _create_admin(cur, username, password)
            conn.commit()
            return True, "Admin créé avec succès."
        except sqlite3.IntegrityError:
            return False, "Ce nom d'utilisateur existe déjà."
        finally:
            conn.close()

    def list_admins(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM admins")
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete_admin(self, username):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM admins WHERE username = ?", (username,))
        deleted = cur.rowcount
        conn.commit()
        conn.close()
        return deleted > 0


# ─────────────────────────────────────────────────────────────────────────────
# CONTACTS (Partie 5 — SQLite)
# ─────────────────────────────────────────────────────────────────────────────

class AddressBook:
    """Gestion des contacts via SQLite."""

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def add(self, contact):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO contacts
                    (nom, prenom, email, pays, numero_local, adresse, fonction, entreprise, categorie)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (contact.nom, contact.prenom, contact.email, contact.pays,
                  contact.numero_local, contact.adresse, contact.fonction,
                  contact.entreprise, contact.categorie))
            conn.commit()
            return True, "Contact ajouté avec succès."
        except sqlite3.IntegrityError:
            return False, "Email déjà existant."
        finally:
            conn.close()

    def remove(self, nom):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM contacts WHERE LOWER(nom) = LOWER(?)", (nom,))
        deleted = cur.rowcount
        conn.commit()
        conn.close()
        if deleted == 0:
            return False, f"Aucun contact trouvé avec le nom '{nom}'."
        return True, f"Contact '{nom}' supprimé."

    def find(self, nom):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts WHERE LOWER(nom) = LOWER(?)", (nom,))
        row = cur.fetchone()
        conn.close()
        return self._row_to_contact(row) if row else None

    def find_by_id(self, contact_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cur.fetchone()
        conn.close()
        return self._row_to_contact(row) if row else None

    def all(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts ORDER BY LOWER(nom)")
        rows = cur.fetchall()
        conn.close()
        return [self._row_to_contact(r) for r in rows]

    def search(self, query):
        """Recherche par nom, prénom ou email."""
        conn = get_connection()
        cur = conn.cursor()
        q = f"%{query.lower()}%"
        cur.execute("""
            SELECT * FROM contacts
            WHERE LOWER(nom) LIKE ? OR LOWER(prenom) LIKE ? OR LOWER(email) LIKE ?
            ORDER BY LOWER(nom)
        """, (q, q, q))
        rows = cur.fetchall()
        conn.close()
        return [self._row_to_contact(r) for r in rows]

    def filter_by_category(self, categorie):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM contacts WHERE categorie = ? ORDER BY LOWER(nom)", (categorie,))
        rows = cur.fetchall()
        conn.close()
        return [self._row_to_contact(r) for r in rows]

    def update(self, nom_original, contact):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE contacts SET
                    nom=?, prenom=?, email=?, pays=?, numero_local=?,
                    adresse=?, fonction=?, entreprise=?, categorie=?
                WHERE LOWER(nom) = LOWER(?)
            """, (contact.nom, contact.prenom, contact.email, contact.pays,
                  contact.numero_local, contact.adresse, contact.fonction,
                  contact.entreprise, contact.categorie, nom_original))
            conn.commit()
            return True, "Contact mis à jour."
        except sqlite3.IntegrityError:
            return False, "Email déjà utilisé par un autre contact."
        finally:
            conn.close()

    # ── Export CSV (Partie 5 — synchronisation) ────────────────────────────

    def export_csv(self, filepath="export_contacts.csv"):
        contacts = self.all()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Nom", "Prénom", "Email", "Pays", "Téléphone",
                             "Adresse", "Fonction", "Entreprise", "Catégorie"])
            for c in contacts:
                writer.writerow([c.nom, c.prenom, c.email, c.pays,
                                 c.telephone, c.adresse, c.fonction,
                                 c.entreprise, c.categorie])
        return len(contacts)

    def import_csv(self, filepath):
        imported, errors = 0, 0
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Reconstituer le numero_local depuis le téléphone si besoin
                    numero = row.get("Numéro", row.get("Téléphone", "")).strip()
                    # Extraire uniquement les 10 derniers chiffres
                    digits = "".join(c for c in numero if c.isdigit())[-10:]
                    c = Contact(
                        nom=row["Nom"], prenom=row["Prénom"],
                        email=row["Email"], pays=row["Pays"],
                        numero_local=digits,
                        adresse=row.get("Adresse", ""),
                        fonction=row.get("Fonction", ""),
                        entreprise=row.get("Entreprise", ""),
                        categorie=row.get("Catégorie", "Autre"),
                    )
                    ok, _ = self.add(c)
                    if ok:
                        imported += 1
                    else:
                        errors += 1
                except Exception:
                    errors += 1
        return imported, errors

    # ── Rendez-vous (Partie 9) ─────────────────────────────────────────────

    def add_rdv(self, contact_id, date, heure, notes=""):
        conn = get_connection()
        cur = conn.cursor()
        # Vérifier si le créneau est déjà pris
        cur.execute("SELECT id FROM rendezvous WHERE date=? AND heure=?", (date, heure))
        if cur.fetchone():
            conn.close()
            return False, "Ce créneau est déjà réservé."
        cur.execute("""
            INSERT INTO rendezvous (contact_id, date, heure, notes)
            VALUES (?, ?, ?, ?)
        """, (contact_id, date, heure, notes))
        conn.commit()
        conn.close()
        return True, "Rendez-vous enregistré."

    def get_rdv_by_date(self, date):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT r.*, c.nom, c.prenom FROM rendezvous r
            LEFT JOIN contacts c ON c.id = r.contact_id
            WHERE r.date = ?
            ORDER BY r.heure
        """, (date,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_rdv(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT r.*, c.nom, c.prenom FROM rendezvous r
            LEFT JOIN contacts c ON c.id = r.contact_id
            ORDER BY r.date, r.heure
        """)
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete_rdv(self, rdv_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM rendezvous WHERE id=?", (rdv_id,))
        deleted = cur.rowcount
        conn.commit()
        conn.close()
        return deleted > 0

    def get_occupied_slots(self, date):
        """Retourne les créneaux occupés pour une date donnée."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT heure FROM rendezvous WHERE date=?", (date,))
        rows = cur.fetchall()
        conn.close()
        return {r["heure"] for r in rows}

    # ── Helper ────────────────────────────────────────────────────────────────

    def _row_to_contact(self, row):
        if row is None:
            return None
        keys = row.keys()
        c = Contact(
            nom=row["nom"], prenom=row["prenom"],
            email=row["email"], pays=row["pays"],
            numero_local=row["numero_local"],
            adresse=row["adresse"] if "adresse" in keys else "",
            fonction=row["fonction"] if "fonction" in keys else "",
            entreprise=row["entreprise"] if "entreprise" in keys else "",
            categorie=row["categorie"] if "categorie" in keys else "Autre",
        )
        c._id = row["id"]
        return c
