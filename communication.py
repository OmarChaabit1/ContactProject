"""
Partie 7 — Module de communication : Email (SMTP) et WhatsApp (wa.me).
"""

import smtplib
import webbrowser
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:
    """
    Envoi d'email via SMTP.
    Configurez SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS
    dans les paramètres ou via les variables d'environnement.
    """

    def __init__(self,
                 smtp_server="smtp.gmail.com",
                 smtp_port=587,
                 smtp_user="dalaoui679@gmail.com",
                 smtp_pass="utjs uwux ueih ryfb"):

        self.smtp_server = smtp_server
        self.smtp_port   = smtp_port
        self.smtp_user   = smtp_user
        self.smtp_pass   = smtp_pass

    def send(self, to_email, subject, body):
        """
        Envoie un email en texte brut.
        Retourne (True, message_succes) ou (False, message_erreur).
        """
        if not self.smtp_user or not self.smtp_pass:
            return False, ("Configuration SMTP manquante.\n"
                           "Renseignez smtp_user et smtp_pass dans EmailSender.")

        msg = MIMEMultipart()
        msg["From"]    = self.smtp_user
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.smtp_user, to_email, msg.as_string())
            return True, f"Email envoyé à {to_email}."
        except smtplib.SMTPAuthenticationError:
            return False, "Erreur d'authentification SMTP. Vérifiez vos identifiants."
        except smtplib.SMTPConnectError:
            return False, "Impossible de se connecter au serveur SMTP."
        except Exception as e:
            return False, f"Erreur d'envoi : {e}"


class WhatsAppSender:
    """
    Ouvre WhatsApp Web avec un message pré-rempli via l'URL wa.me.
    Ne nécessite aucune bibliothèque externe.
    """

    def send(self, phone_international, message):
        """
        phone_international : numéro E.164 sans '+' ni espaces, ex. "212612345678"
        message             : texte à pré-remplir
        Retourne (True, info) ou (False, erreur).
        """
        # Nettoyer le numéro : garder uniquement les chiffres
        digits = "".join(c for c in phone_international if c.isdigit())
        if not digits:
            return False, "Numéro de téléphone invalide pour WhatsApp."

        encoded_msg = urllib.parse.quote(message)
        url = f"https://wa.me/{digits}?text={encoded_msg}"

        try:
            webbrowser.open(url)
            return True, f"WhatsApp ouvert pour {digits}."
        except Exception as e:
            return False, f"Impossible d'ouvrir le navigateur : {e}"
