import streamlit as st

import api
import commun


st.title("Lignes")
st.caption(
    "L'API ne permet pas encore de lister les lignes : notez l'identifiant affiché "
    "à la création, il sert à créer des trajets. Les lignes créées pendant cette session "
    "sont rappelées en bas de page."
)

try:
    gares = commun.liste_gares(commun.token())
except api.ErreurAPI as e:
    commun.afficher_erreur(e)
    st.stop()

if len(gares) < 2:
    st.info("Il faut au moins deux gares enregistrées : importez-en depuis la page « Gares ».")
    st.stop()

memo = st.session_state.setdefault("lignes_session", {})

creer, modifier, supprimer = st.tabs(["Créer", "Modifier", "Supprimer"])

with creer, st.form("creer_ligne"):
    c1, c2 = st.columns(2)
    with c1:
        depart = commun.choisir_gare("Gare de départ", gares, "ligne_depart")
    with c2:
        arrivee = commun.choisir_gare("Gare d'arrivée (terminus)", gares, "ligne_arrivee")
    st.caption("Le sens compte : Paris → Rennes et Rennes → Paris sont deux lignes différentes.")
    if st.form_submit_button("Créer la ligne", type="primary"):
        if depart is None or arrivee is None:
            st.warning("Choisissez les deux gares.")
        else:
            try:
                reponse = api.creer_ligne(commun.token(), depart["nom"], arrivee["nom"])
                memo[reponse["id_ligne"]] = f"{depart['nom']} → {arrivee['nom']}"
                st.success(f"{reponse['message']} : ligne #{reponse['id_ligne']}.")
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)

with modifier, st.form("modifier_ligne"):
    id_ligne = st.number_input("Identifiant de la ligne", min_value=1, step=1, key="mod_id_ligne")
    c1, c2 = st.columns(2)
    with c1:
        depart = commun.choisir_gare("Nouvelle gare de départ", gares, "mod_ligne_depart")
    with c2:
        arrivee = commun.choisir_gare("Nouvelle gare d'arrivée", gares, "mod_ligne_arrivee")
    st.caption("Impossible si des trajets existent déjà sur cette ligne.")
    if st.form_submit_button("Modifier la ligne", type="primary"):
        if depart is None or arrivee is None:
            st.warning("Choisissez les deux gares.")
        else:
            try:
                reponse = api.modifier_ligne(commun.token(), int(id_ligne), depart["nom"], arrivee["nom"])
                memo[int(id_ligne)] = f"{depart['nom']} → {arrivee['nom']}"
                st.success(f"{reponse['message']} (ligne #{reponse['id_ligne']}).")
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)

with supprimer, st.form("supprimer_ligne"):
    id_ligne = st.number_input("Identifiant de la ligne", min_value=1, step=1, key="sup_id_ligne")
    confirme = st.checkbox("Je confirme la suppression")
    st.caption("Impossible si des trajets existent encore sur cette ligne.")
    if st.form_submit_button("Supprimer la ligne"):
        if not confirme:
            st.warning("Cochez la case de confirmation.")
        else:
            try:
                reponse = api.supprimer_ligne(commun.token(), int(id_ligne))
                memo.pop(int(id_ligne), None)
                st.success(reponse["message"])
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)

if memo:
    st.divider()
    st.subheader("Lignes de cette session")
    st.dataframe(
        [{"id_ligne": i, "ligne": libelle} for i, libelle in sorted(memo.items())],
        hide_index=True, width="stretch",
    )
