from datetime import date

import streamlit as st

import api
import commun
import style

utilisateur = commun.utilisateur()
est_client = utilisateur["grade"] == "CLIENT"

st.title("Rechercher un trajet")

try:
    gares = commun.liste_gares(commun.token())
except api.ErreurAPI as e:
    commun.afficher_erreur(e)
    st.stop()

if not gares:
    st.info("Aucune gare n'est encore enregistrée. Un collaborateur doit d'abord importer des gares.")
    st.stop()

with st.form("recherche"):
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        depart = commun.choisir_gare("Gare de départ", gares, "rech_depart")
    with c2:
        arrivee = commun.choisir_gare("Gare d'arrivée", gares, "rech_arrivee")
    with c3:
        jour = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
    lancer = st.form_submit_button("Rechercher", type="primary", icon=":material/search:")

if lancer:
    if depart is None or arrivee is None:
        st.warning("Choisissez une gare de départ et une gare d'arrivée.")
    elif depart["id_gare"] == arrivee["id_gare"]:
        st.warning("La gare de départ et la gare d'arrivée doivent être différentes.")
    else:
        try:
            st.session_state.resultats = {
                "depart": depart,
                "arrivee": arrivee,
                "jour": jour,
                "trajets": api.rechercher_trajets(commun.token(), depart["nom"], arrivee["nom"], jour),
            }
        except api.ErreurAPI as e:
            st.session_state.pop("resultats", None)
            commun.afficher_erreur(e)

resultats = st.session_state.get("resultats")
if not resultats:
    st.stop()

trajets = resultats["trajets"]


def duree_panneau(minutes: int | None) -> str:
    if minutes is None:
        return "--"
    h, m = divmod(minutes, 60)
    return f"{h}H{m:02d}"


def places_panneau(places: int | None) -> str:
    """F5 : places restantes dans une classe (COMPLET à 0, -- si inconnues)."""
    if places is None:
        return "--"
    return "COMPLET" if places == 0 else str(places)


style.panneau_departs(
    f"{resultats['depart']['nom']} → {resultats['arrivee']['nom']}",
    colonnes=[("DÉPART", 5, False), ("ARRIVÉE", 5, False), ("DURÉE", 5, False),
              ("TRAIN", 5, False), ("2DE CL.", 8, True), ("1RE CL.", 8, True),
              ("PL. 2DE", 7, True), ("PL. 1RE", 7, True)],
    lignes=[
        [
            commun.heure(t["heure_depart"]),
            commun.heure(t["heure_arrivee"]),
            duree_panneau(t.get("temps_trajet")),
            str(t.get("num_train") or "--"),
            commun.euros(commun.prix_classe(t["tarif_base"], 2)),
            commun.euros(commun.prix_classe(t["tarif_base"], 1)),
            places_panneau(t.get("places_restantes_seconde")),
            places_panneau(t.get("places_restantes_premiere")),
        ]
        for t in trajets
    ],
    message_vide="AUCUN TRAIN CE JOUR",
)
st.caption(f"{commun.jour(resultats['jour']).capitalize()} · {len(trajets)} trajet(s)")

if not trajets or not est_client:
    st.stop()

st.subheader("Réserver une place")
with st.form("reserver"):
    trajet = st.selectbox(
        "Train",
        trajets,
        format_func=lambda t: (
            f"{commun.heure(t['heure_depart'])} → {commun.heure(t['heure_arrivee'])}"
            + (f" · train {t['num_train']}" if t.get("num_train") else "")
        ),
    )
    f1, f2 = st.columns(2)
    classe = f1.radio("Classe", [2, 1], format_func=commun.libelle_classe, horizontal=True)
    place = f2.text_input("Numéro de place", max_chars=10, placeholder="ex. 42")
    if st.form_submit_button("Confirmer la réservation", type="primary", icon=":material/confirmation_number:"):
        if not place.strip():
            st.error("Indiquez un numéro de place.")
        else:
            try:
                reservation = api.reserver(
                    commun.token(), trajet["id_trajet"], place.strip(), classe
                )
                st.success("Réservation confirmée, voici votre billet :", icon=":material/check_circle:")
                commun.afficher_billet(reservation)
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)
