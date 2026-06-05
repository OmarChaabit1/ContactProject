"""
Partie 6 — Application Web Flask de gestion de contacts.
Lancer : python flask_app/app.py
Accès  : http://localhost:5000
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import (Flask, render_template, request,
                   redirect, url_for, flash, session, send_file)
from models.address_book import AddressBook, AuthManager, init_db
from models.contact import Contact, INDICATIFS, CATEGORIES
import io

app = Flask(__name__)
app.secret_key = "carnet_adresses_secret_key_2024"

book = AddressBook()
auth = AuthManager()

# ── Initialisation DB ─────────────────────────────────────────────────────────

@app.before_request
def setup():
    init_db()

# ── Décorateur de protection ─────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            flash("Veuillez vous connecter.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if auth.verify(username, password):
            session["admin"] = username
            flash(f"Bienvenue, {username} !", "success")
            return redirect(url_for("index"))
        flash("Identifiants incorrects.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Déconnecté.", "info")
    return redirect(url_for("login"))

# ── INDEX — liste contacts ────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    q   = request.args.get("q", "").strip()
    cat = request.args.get("cat", "").strip()

    if q:
        contacts = book.search(q)
    elif cat:
        contacts = book.filter_by_category(cat)
    else:
        contacts = book.all()

    return render_template("index.html",
                           contacts=contacts,
                           categories=CATEGORIES,
                           q=q, cat=cat,
                           admin=session.get("admin"))

# ── AJOUTER ───────────────────────────────────────────────────────────────────

@app.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    if request.method == "POST":
        try:
            c = Contact(
                nom=request.form["nom"],
                prenom=request.form["prenom"],
                email=request.form["email"],
                pays=request.form["pays"],
                numero_local=request.form["numero"],
                adresse=request.form.get("adresse", ""),
                fonction=request.form.get("fonction", ""),
                entreprise=request.form.get("entreprise", ""),
                categorie=request.form.get("categorie", "Autre"),
            )
            ok, msg = book.add(c)
            flash(msg, "success" if ok else "error")
            if ok:
                return redirect(url_for("index"))
        except AssertionError as e:
            flash(str(e), "error")

    return render_template("form.html",
                           indicatifs=INDICATIFS,
                           categories=CATEGORIES,
                           contact=None,
                           admin=session.get("admin"))

# ── MODIFIER ──────────────────────────────────────────────────────────────────

@app.route("/modifier/<nom>", methods=["GET", "POST"])
@login_required
def modifier(nom):
    contact = book.find(nom)
    if not contact:
        flash(f"Contact '{nom}' introuvable.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            new_c = Contact(
                nom=request.form["nom"],
                prenom=request.form["prenom"],
                email=request.form["email"],
                pays=request.form["pays"],
                numero_local=request.form["numero"],
                adresse=request.form.get("adresse", ""),
                fonction=request.form.get("fonction", ""),
                entreprise=request.form.get("entreprise", ""),
                categorie=request.form.get("categorie", "Autre"),
            )
            ok, msg = book.update(nom, new_c)
            flash(msg, "success" if ok else "error")
            if ok:
                return redirect(url_for("index"))
        except AssertionError as e:
            flash(str(e), "error")

    return render_template("form.html",
                           indicatifs=INDICATIFS,
                           categories=CATEGORIES,
                           contact=contact,
                           admin=session.get("admin"))

# ── SUPPRIMER ─────────────────────────────────────────────────────────────────

@app.route("/supprimer/<nom>", methods=["POST"])
@login_required
def supprimer(nom):
    ok, msg = book.remove(nom)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("index"))

# ── EXPORT CSV ────────────────────────────────────────────────────────────────

@app.route("/export")
@login_required
def export():
    path = "export_flask.csv"
    n = book.export_csv(path)
    flash(f"{n} contact(s) exporté(s).", "success")
    return send_file(path, as_attachment=True, download_name="contacts.csv")

# ── AGENDA ────────────────────────────────────────────────────────────────────

@app.route("/agenda")
@login_required
def agenda():
    from datetime import date
    sel_date = request.args.get("date", date.today().strftime("%Y-%m-%d"))
    rdv_list = book.get_rdv_by_date(sel_date)
    occupied = book.get_occupied_slots(sel_date)
    contacts = book.all()

    from views.agenda_view import CRENEAUX
    return render_template("agenda.html",
                           creneaux=CRENEAUX,
                           rdv_list=rdv_list,
                           occupied=occupied,
                           sel_date=sel_date,
                           contacts=contacts,
                           admin=session.get("admin"))

@app.route("/agenda/reserver", methods=["POST"])
@login_required
def reserver_rdv():
    contact_id = request.form.get("contact_id")
    date_str   = request.form.get("date")
    heure      = request.form.get("heure")
    notes      = request.form.get("notes", "")

    ok, msg = book.add_rdv(contact_id, date_str, heure, notes)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("agenda", date=date_str))

@app.route("/agenda/supprimer/<int:rdv_id>", methods=["POST"])
@login_required
def supprimer_rdv(rdv_id):
    date_str = request.form.get("date")
    book.delete_rdv(rdv_id)
    flash("RDV annulé.", "success")
    return redirect(url_for("agenda", date=date_str))

# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
