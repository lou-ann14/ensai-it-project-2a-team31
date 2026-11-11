from datetime import date, datetime, time, timedelta

import streamlit as st

import api
import commun

st.title("Trajets")
st.caption(
    "L'heure d'arrivée et le temps de trajet sont calculés automatiquement par l'API SNCF. "
    "Le train est désigné par son numéro."
)


def champs_trajet(prefixe: str):
    """Champs communs à la création et à la modification. Renvoie les valeurs saisies."""
    c1, c2 = st.columns(2)
    id_ligne = c1.number_input("Identifiant de la ligne", min_value=1, step=1, key=f"{prefixe}_ligne")
    num_train = c2.number_input("Numéro du train", min_value=0, step=1, key=f"{prefixe}_train")
    c3, c4, c5 = st.columns(3)
    jour = c3.date_input("Date de départ", value=date.today() + timedelta(days=1),
                         format="DD/MM/YYYY", key=f"{prefixe}_jour")
    heure = c4.time_input("Heure de départ", value=time(8, 0), step=300, key=f"{prefixe}_heure")
    tarif = c5.number_input("Tarif de base (€)", min_value=0.0, step=1.0, value=40.0,
                            format="%.2f", key=f"{prefixe}_tarif")
    return int(id_ligne), int(num_train), datetime.combine(jour, heure), float(tarif)


def id_train_depuis_num(num_train: int) -> int:
    return api.trouver_train(commun.token(), num_train)["id_train"]


def afficher_resultat(reponse: dict):
    st.success(
        f"{reponse['message']} : trajet #{reponse['id_trajet']}, arrivée "
        f"{commun.date_heure(reponse['heure_arrivee'])} ({commun.duree(reponse['temps_trajet'])})."
    )


creer, modifier, supprimer = st.tabs(["Créer", "Modifier", "Supprimer"])

with creer, st.form("creer_trajet"):
    id_ligne, num_train, depart, tarif = champs_trajet("creer")
    if st.form_submit_button("Créer le trajet", type="primary"):
        if depart <= datetime.now():
            st.warning("L'heure de départ est déjà passée.")
        else:
            try:
                with st.spinner("Calcul du temps de trajet avec l'API SNCF…"):
                    reponse = api.creer_trajet(commun.token(), id_ligne, id_train_depuis_num(num_train),
                                               depart, tarif)
                afficher_resultat(reponse)
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)

with modifier, st.form("modifier_trajet"):
    id_trajet = st.number_input("Identifiant du trajet à modifier", min_value=1, step=1, key="mod_trajet")
    id_ligne, num_train, depart, tarif = champs_trajet("mod")
    if st.form_submit_button("Modifier le trajet", type="primary"):
        try:
            with st.spinner("Calcul du temps de trajet avec l'API SNCF…"):
                reponse = api.modifier_trajet(commun.token(), int(id_trajet), id_ligne,
                                              id_train_depuis_num(num_train), depart, tarif)
            afficher_resultat(reponse)
        except api.ErreurAPI as e:
            commun.afficher_erreur(e)

with supprimer, st.form("supprimer_trajet"):
    id_trajet = st.number_input("Identifiant du trajet", min_value=1, step=1, key="sup_trajet")
    confirme = st.checkbox("Je confirme la suppression")
    st.caption("Impossible si des réservations existent encore sur ce trajet.")
    if st.form_submit_button("Supprimer le trajet"):
        if not confirme:
            st.warning("Cochez la case de confirmation.")
        else:
            try:
                st.success(api.supprimer_trajet(commun.token(), int(id_trajet))["message"])
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)
