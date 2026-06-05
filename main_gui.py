"""
Point d'entrée principal — Carnet d'Adresses International
Parties 4 à 9 intégrées.

Lancement interface Tkinter :
    python main_gui.py

Lancement interface Web Flask :
    cd flask_app && python app.py
    → http://localhost:5000
"""

import tkinter as tk
from models.address_book import init_db
from views.login_view import LoginWindow
from controllers.contact_gui_controller import ContactGUIController


def launch_app(username):
    """Lance l'application principale après authentification réussie."""
    main_root = tk.Tk()
    ContactGUIController(main_root, username)
    main_root.mainloop()


if __name__ == "__main__":
    # Initialise la base SQLite (crée tables + admin par défaut si besoin)
    init_db()

    # Fenêtre de connexion (Partie 4)
    login_root = tk.Tk()
    LoginWindow(login_root, on_success=launch_app)
    login_root.mainloop()
