from datetime import date, datetime, time, timedelta

import streamlit as st

import api
import commun

st.title("Trajets")
st.caption("L'heure d'arrivée et le temps de trajet sont calculés automatiquement par l'API SNCF.")
commun.afficher_flash()

try:
    lignes = {ligne["id_ligne"]: ligne for ligne in api.lister_lignes(commun.token())}
    trains = {train["id_train"]: train for train in api.lister_trains(commun.token())}
    trajets = {trajet["id_trajet"]: trajet for trajet in api.lister_trajets(commun.token())}
except api.ErreurAPI as e:
    commun.afficher_erreur(e)
    st.stop()


def libelle_trajet(id_trajet: int) -> str:
    """
    Texte d'un trajet dans les listes déroulantes.

    Param:
    ------
    id_trajet: int
        l'id du trajet

    Return:
    ------
    str
        la date de départ, les gares et le numéro du train
    """
    t = trajets[id_trajet]
    train = f" · train {t['num_train']}" if t["num_train"] is not None else ""
    return f"{commun.date_heure(t['heure_depart'])} · {commun.libelle_ligne(t['ligne'])}{train}"


def champs_trajet(prefixe: str, trajet: dict | None = None) -> tuple[int | None, int | None, datetime, float]:
    """
    Champs communs à la création et à la modification.

    Param:
    ------
    prefixe: str
        le début des clés Streamlit des champs
    trajet: dict | None
        le trajet à modifier, dont les valeurs sont proposées (None pour une création)

    Return:
    ------
    tuple[int | None, int | None, datetime, float]
        l'id de la ligne, l'id du train, la date de départ et le tarif
    """
    depart = commun.lire_date(trajet["heure_depart"]) if trajet else datetime.combine(
        date.today() + timedelta(days=1), time(8, 0)
    )
    ids_lignes, ids_trains = list(lignes), list(trains)
    position_ligne = ids_lignes.index(trajet["ligne"]["id_ligne"]) if trajet else None
    position_train = next(
        (i for i, id_train in enumerate(ids_trains) if trajet and trains[id_train]["num_train"] == trajet["num_train"]),
        None,
    )

    c1, c2 = st.columns(2)
    id_ligne = c1.selectbox("Ligne", ids_lignes, index=position_ligne, key=f"{prefixe}_ligne",
                            format_func=lambda i: commun.libelle_ligne(lignes[i]), placeholder="Choisissez une ligne")
    id_train = c2.selectbox("Train", ids_trains, index=position_train, key=f"{prefixe}_train",
                            format_func=lambda i: commun.libelle_train(trains[i]), placeholder="Choisissez un train")
    c3, c4, c5 = st.columns(3)
    jour = c3.date_input("Date de départ", value=depart.date(), format="DD/MM/YYYY", key=f"{prefixe}_jour")
    heure = c4.time_input("Heure de départ", value=depart.time(), step=300, key=f"{prefixe}_heure")
    tarif = c5.number_input("Tarif de base (€)", min_value=0.0, step=1.0, format="%.2f", key=f"{prefixe}_tarif",
                            value=float(trajet["tarif_base"]) if trajet else 40.0)
    return id_ligne, id_train, datetime.combine(jour, heure), float(tarif)


def message_resultat(reponse: dict) -> str:
    """
    Prépare le message affiché après la création ou la modification d'un trajet.

    Param:
    ------
    reponse: dict
        la réponse de l'API

    Return:
    ------
    str
        le message, avec l'heure d'arrivée et la durée du trajet
    """
    return (
        f"{reponse['message']} : trajet #{reponse['id_trajet']}, arrivée "
        f"{commun.date_heure(reponse['heure_arrivee'])} ({commun.duree(reponse['temps_trajet'])})."
    )


liste, creer, modifier, supprimer = st.tabs([f"À venir ({len(trajets)})", "Créer", "Modifier", "Supprimer"])

with liste:
    if not trajets:
        st.caption("Aucun trajet à venir.")
    else:
        st.dataframe(
            [
                {
                    "Id": t["id_trajet"],
                    "Ligne": commun.libelle_ligne(t["ligne"]),
                    "Départ": commun.date_heure(t["heure_depart"]),
                    "Arrivée": commun.date_heure(t["heure_arrivee"]),
                    "Durée": commun.duree(t["temps_trajet"]),
                    "Train": t["num_train"],
                    "Tarif": commun.euros(t["tarif_base"]),
                    "Places 1re": t["places_restantes_premiere"],
                    "Places 2de": t["places_restantes_seconde"],
                }
                for t in trajets.values()
            ],
            hide_index=True,
            width="stretch",
        )

with creer, st.form("creer_trajet"):
    id_ligne, id_train, depart, tarif = champs_trajet("creer")
    if st.form_submit_button("Créer le trajet", type="primary"):
        if id_ligne is None or id_train is None:
            st.warning("Choisissez une ligne et un train.")
        elif depart <= datetime.now():
            st.warning("L'heure de départ est déjà passée.")
        else:
            try:
                with st.spinner("Calcul du temps de trajet avec l'API SNCF…"):
                    reponse = api.creer_trajet(commun.token(), id_ligne, id_train, depart, tarif)
                commun.flash(message_resultat(reponse))
                st.rerun()
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)

with modifier:
    id_trajet = st.selectbox("Trajet à modifier", list(trajets), index=None, format_func=libelle_trajet,
                             placeholder="Choisissez un trajet", key="mod_trajet")
    if id_trajet is not None:
        with st.form("modifier_trajet"):
            id_ligne, id_train, depart, tarif = champs_trajet(f"mod_{id_trajet}", trajets[id_trajet])
            if st.form_submit_button("Modifier le trajet", type="primary"):
                if id_ligne is None or id_train is None:
                    st.warning("Choisissez une ligne et un train.")
                else:
                    try:
                        with st.spinner("Calcul du temps de trajet avec l'API SNCF…"):
                            reponse = api.modifier_trajet(commun.token(), id_trajet, id_ligne, id_train, depart, tarif)
                        commun.flash(message_resultat(reponse))
                        st.rerun()
                    except api.ErreurAPI as e:
                        commun.afficher_erreur(e)

with supprimer, st.form("supprimer_trajet"):
    id_trajet = st.selectbox("Trajet à supprimer", list(trajets), index=None, format_func=libelle_trajet,
                             placeholder="Choisissez un trajet", key="sup_trajet")
    confirme = st.checkbox("Je confirme la suppression")
    st.caption("Impossible si des réservations existent encore sur ce trajet.")
    if st.form_submit_button("Supprimer le trajet"):
        if id_trajet is None:
            st.warning("Choisissez le trajet à supprimer.")
        elif not confirme:
            st.warning("Cochez la case de confirmation.")
        else:
            try:
                commun.flash(api.supprimer_trajet(commun.token(), id_trajet)["message"])
                st.rerun()
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)
