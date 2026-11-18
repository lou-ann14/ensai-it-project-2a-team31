from datetime import datetime

import streamlit as st

import api
import commun


st.title("Mes réservations")

try:
    reservations = api.historique_reservations(commun.token())
except api.ErreurAPI as e:
    commun.afficher_erreur(e)
    st.stop()

if not reservations:
    st.info("Vous n'avez encore aucune réservation. Rendez-vous dans « Rechercher un trajet ».")
    st.stop()

maintenant = datetime.now()
a_venir = [r for r in reservations if commun.lire_date(r["trajet"]["heure_depart"]) > maintenant]
passees = [r for r in reservations if r not in a_venir]


@st.dialog("Annuler la réservation ?")
def confirmer_annulation(id_reservation: int):
    st.write(f"La réservation #{id_reservation} sera définitivement annulée.")
    c1, c2 = st.columns(2)
    if c1.button("Oui, annuler", type="primary", width="stretch"):
        try:
            api.annuler_reservation(commun.token(), id_reservation)
            st.rerun()
        except api.ErreurAPI as e:
            st.error(e.message)
    if c2.button("Non", width="stretch"):
        st.rerun()


def carte(reservation: dict, annulable: bool):
    commun.afficher_billet(reservation)
    if annulable and st.button("Annuler ce billet", key=f"annuler_{reservation['id_reservation']}",
                               icon=":material/cancel:", type="tertiary"):
        confirmer_annulation(reservation["id_reservation"])


onglet_venir, onglet_passees = st.tabs([f"À venir ({len(a_venir)})", f"Passées ({len(passees)})"])
with onglet_venir:
    if not a_venir:
        st.caption("Aucune réservation à venir.")
    for r in a_venir:
        carte(r, annulable=True)
with onglet_passees:
    if not passees:
        st.caption("Aucune réservation passée.")
    for r in passees:
        carte(r, annulable=False)
