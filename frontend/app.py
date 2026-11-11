"""Point d'entrée de l'interface Streamlit.

Lancement (depuis la racine du dépôt) :
    uv run --project frontend streamlit run frontend/app.py
"""

from html import escape

import streamlit as st

import api
import commun
import style

st.set_page_config(page_title="Concurrent SNCF", page_icon=":material/train:", layout="wide")
style.appliquer()


def page_connexion():
    style.titre_panneau("CONCURRENT SNCF", "PROCHAIN DÉPART · VOTRE VOYAGE")

    colonne, texte = st.columns([1, 1], gap="large")
    with texte:
        style.etapes([
            ("Recherchez", "un trajet entre deux gares, à la date de votre choix"),
            ("Réservez", "votre place en 1re ou en 2de classe"),
            ("Voyagez", "avec tous vos billets réunis au même endroit"),
        ])

    with colonne, st.container(key="guichet"):
        st.html('<div class="guichet-entete"><span>GUICHET</span><span class="ouvert">● OUVERT</span></div>')
        mode = st.segmented_control("Action", ["Connexion", "Inscription"], default="Connexion",
                                    required=True, key="mode_guichet", label_visibility="collapsed",
                                    width="stretch")

        if mode == "Connexion":
            with st.form("connexion", border=False):
                nom = st.text_input("Nom d'utilisateur")
                mdp = st.text_input("Mot de passe", type="password")
                if st.form_submit_button("Se connecter", type="primary", width="stretch"):
                    if not nom.strip() or not mdp:
                        st.error("Renseignez le nom d'utilisateur et le mot de passe.")
                    else:
                        try:
                            st.session_state.utilisateur = api.login(nom.strip(), mdp)
                            st.rerun()
                        except api.ErreurAPI as e:
                            if e.statut == 401:
                                st.error("Nom d'utilisateur ou mot de passe incorrect.")
                            else:
                                st.error(e.message)
        else:
            with st.form("inscription", border=False):
                nom = st.text_input("Nom d'utilisateur", max_chars=15, help="15 caractères maximum")
                mdp = st.text_input("Mot de passe", type="password")
                mdp2 = st.text_input("Confirmer le mot de passe", type="password")
                if st.form_submit_button("Créer mon compte", type="primary", width="stretch"):
                    if not nom.strip() or not mdp:
                        st.error("Renseignez le nom d'utilisateur et le mot de passe.")
                    elif mdp != mdp2:
                        st.error("Les deux mots de passe ne correspondent pas.")
                    else:
                        try:
                            api.creer_compte(nom.strip(), mdp)
                            st.success("Compte client créé ! Vous pouvez maintenant vous connecter.")
                        except api.ErreurAPI as e:
                            st.error(e.message)


def entete(utilisateur: dict) -> None:
    """Bandeau de gare : marque à gauche, carte du voyageur et déconnexion à droite."""
    grade = (utilisateur.get("grade") or "").capitalize()
    with st.container(key="entete"):
        gauche, droite, bouton = st.columns([5, 3, 1.4], vertical_alignment="center")
        gauche.html(style.marque())
        droite.html(
            f'<div class="voyageur"><label>Voyageur</label>'
            f'<strong>{escape(utilisateur["nom"])}</strong>'
            f'<span>{escape(grade)} · N° {utilisateur["id"]}</span></div>'
        )
        if bouton.button("Quitter", key="deconnexion", icon=":material/logout:", width="stretch"):
            commun.deconnecter()
            st.rerun()


def ligne_navigation(arrets: list[tuple[str, st.Page]], courante) -> None:
    """Menu dessiné comme une ligne de train : chaque page est un arrêt."""
    with st.container(key="ligne"):
        colonnes = st.columns(len(arrets), gap=None)
        for i, (colonne, (groupe, page)) in enumerate(zip(colonnes, arrets)):
            actif = page.url_path == courante.url_path
            with colonne, st.container(key=f"arret{'_actif' if actif else ''}_{i}"):
                st.page_link(page, label=page.title)
                st.html(f'<div class="arret-groupe">{"VOUS ÊTES ICI" if actif else escape(groupe)}</div>')


utilisateur = commun.utilisateur()

if utilisateur is None:
    navigation = st.navigation([st.Page(page_connexion, title="Connexion", icon=":material/login:")],
                               position="hidden")
else:
    grade = utilisateur.get("grade")
    arrets = [("Voyager", st.Page("vues/recherche.py", title="Rechercher", icon=":material/search:",
                                  default=True))]
    if grade == "CLIENT":
        arrets.append(("Voyager", st.Page("vues/reservations.py", title="Mes réservations",
                                          icon=":material/confirmation_number:")))
    if grade == "COLLABORATEUR":
        arrets += [
            ("Exploitation", st.Page("vues/gares.py", title="Gares", icon=":material/location_on:")),
            ("Exploitation", st.Page("vues/lignes.py", title="Lignes", icon=":material/route:")),
            ("Exploitation", st.Page("vues/trains.py", title="Trains", icon=":material/train:")),
            ("Exploitation", st.Page("vues/trajets.py", title="Trajets", icon=":material/schedule:")),
        ]
    if grade == "ADMIN":
        arrets.append(("Administration", st.Page("vues/comptes.py", title="Comptes",
                                                 icon=":material/manage_accounts:")))
    navigation = st.navigation([page for _, page in arrets], position="hidden")

    entete(utilisateur)
    ligne_navigation(arrets, navigation)

navigation.run()
