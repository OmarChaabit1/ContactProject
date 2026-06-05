import re

# Dictionnaire pays -> indicatif
INDICATIFS = {
    "Afghanistan": "+93", "Afrique du Sud": "+27", "Albanie": "+355",
    "Algérie": "+213", "Allemagne": "+49", "Arabie Saoudite": "+966",
    "Argentine": "+54", "Australie": "+61", "Autriche": "+43",
    "Belgique": "+32", "Brésil": "+55", "Canada": "+1",
    "Chine": "+86", "Côte d'Ivoire": "+225", "Danemark": "+45",
    "Egypte": "+20", "Emirats Arabes Unis": "+971", "Espagne": "+34",
    "Etats-Unis": "+1", "Finlande": "+358", "France": "+33",
    "Ghana": "+233", "Grèce": "+30", "Inde": "+91",
    "Indonésie": "+62", "Irak": "+964", "Iran": "+98",
    "Irlande": "+353", "Israël": "+972", "Italie": "+39",
    "Japon": "+81", "Jordanie": "+962", "Kenya": "+254",
    "Liban": "+961", "Libye": "+218", "Luxembourg": "+352",
    "Malaisie": "+60", "Mali": "+223", "Maroc": "+212",
    "Mauritanie": "+222", "Mexique": "+52", "Niger": "+227",
    "Nigeria": "+234", "Norvège": "+47", "Nouvelle-Zélande": "+64",
    "Pakistan": "+92", "Pays-Bas": "+31", "Philippines": "+63",
    "Pologne": "+48", "Portugal": "+351", "Qatar": "+974",
    "Roumanie": "+40", "Royaume-Uni": "+44", "Russie": "+7",
    "Sénégal": "+221", "Singapour": "+65", "Suède": "+46",
    "Suisse": "+41", "Syrie": "+963", "Tchad": "+235",
    "Thaïlande": "+66", "Tunisie": "+216", "Turquie": "+90",
    "Ukraine": "+380", "Uruguay": "+598", "Venezuela": "+58",
}

# Catégories disponibles (Partie 8)
CATEGORIES = ["Patient", "Fournisseur", "Laboratoire", "Client", "Entreprise", "Autre"]

# Champs CSV dans l'ordre
CHAMPS = ["nom", "prenom", "email", "pays", "numero_local",
          "adresse", "fonction", "entreprise", "categorie"]


class Contact:
    """MODEL : représente un contact avec ses données (Partie 8 : catégories)."""

    def __init__(self, nom, prenom, email, pays, numero_local,
                 adresse="", fonction="", entreprise="", categorie="Autre"):
        assert nom.strip(), "Le nom ne peut pas être vide."
        assert prenom.strip(), "Le prénom ne peut pas être vide."
        assert self._valider_email(email), f"Email invalide : {email}"
        assert pays in INDICATIFS, f"Pays inconnu : '{pays}'"
        assert self._valider_numero(numero_local), \
            "Numéro invalide : doit contenir exactement 10 chiffres."

        self.nom          = nom.strip()
        self.prenom       = prenom.strip()
        self.email        = email.strip()
        self.pays         = pays.strip()
        self.indicatif    = INDICATIFS[pays]
        self.numero_local = re.sub(r'\s', '', numero_local.strip())
        self.telephone    = f"{self.indicatif} {self.numero_local}"
        self.adresse      = adresse.strip()
        self.fonction     = fonction.strip()
        self.entreprise   = entreprise.strip()
        self.categorie    = categorie.strip() if categorie.strip() in CATEGORIES else "Autre"

    # ── Validation ──────────────────────────────────────────────────────────

    def _valider_email(self, email):
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email.strip()))

    def _valider_numero(self, numero):
        chiffres = re.sub(r'\s', '', numero.strip())
        return chiffres.isdigit() and len(chiffres) == 10

    # ── Sérialisation ────────────────────────────────────────────────────────

    def to_line(self):
        return (f"{self.nom},{self.prenom},{self.email},{self.pays},"
                f"{self.numero_local},{self.adresse},{self.fonction},"
                f"{self.entreprise},{self.categorie}\n")

    @classmethod
    def from_line(cls, line):
        parts = line.strip().split(',')
        if len(parts) == 5:
            parts += ["", "", "", "Autre"]
        elif len(parts) == 8:
            parts += ["Autre"]
        if len(parts) != 9:
            raise ValueError(f"Ligne invalide : {line}")
        return cls(*parts)

    # ── Affichage ────────────────────────────────────────────────────────────

    def __str__(self):
        lignes = [
            f"Nom        : {self.nom}",
            f"Prénom     : {self.prenom}",
            f"Email      : {self.email}",
            f"Pays       : {self.pays}",
            f"Téléphone  : {self.telephone}",
            f"Catégorie  : {self.categorie}",
        ]
        if self.adresse:
            lignes.append(f"Adresse    : {self.adresse}")
        if self.fonction:
            lignes.append(f"Fonction   : {self.fonction}")
        if self.entreprise:
            lignes.append(f"Entreprise : {self.entreprise}")
        return "\n".join(lignes)

    def __repr__(self):
        return (f"Contact(nom='{self.nom}', prenom='{self.prenom}', "
                f"email='{self.email}', pays='{self.pays}', "
                f"numero='{self.numero_local}', categorie='{self.categorie}')")
