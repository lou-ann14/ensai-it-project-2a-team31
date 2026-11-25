import api
import commun
import streamlit as st

st.title("Lignes")
commun.afficher_flash()

try:
    gares = commun.liste_gares(commun.token())
    lignes = {ligne["id_ligne"]: ligne for ligne in api.lister_lignes(commun.token())}
except api.ErreurAPI as e:
    commun.afficher_erreur(e)
    st.stop()

if len(gares) < 2:
    st.info("Il faut au moins deux gares enregistrées : importez-en depuis la page « Gares ».")
    st.stop()


def libelle(id_ligne: int) -> str:
    """
    Texte d'une ligne dans les listes déroulantes.

    Param:
    ------
    id_ligne: int
        l'id de la ligne

    Return:
    ------
    str
        les gares de départ et d'arrivée
    """
    return commun.libelle_ligne(lignes[id_ligne])


liste, creer, modifier, supprimer = st.tabs([f"Liste ({len(lignes)})", "Créer", "Modifier", "Supprimer"])

with liste:
    if not lignes:
        st.caption("Aucune ligne n'est encore enregistrée.")
    else:
        st.dataframe(
            [
                {
                    "Id": ligne["id_ligne"],
                    "Gare de départ": ligne["gare_depart"]["nom"],
                    "Gare d'arrivée": ligne["gare_arrivee"]["nom"],
                }
                for ligne in lignes.values()
            ],
            hide_index=True,
            width="stretch",
        )

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
                commun.flash(f"{reponse['message']} : ligne #{reponse['id_ligne']}.")
                st.rerun()
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)

with modifier, st.form("modifier_ligne"):
    id_ligne = st.selectbox("Ligne à modifier", list(lignes), index=None, format_func=libelle,
                            placeholder="Choisissez une ligne", key="mod_id_ligne")
    c1, c2 = st.columns(2)
    with c1:
        depart = commun.choisir_gare("Nouvelle gare de départ", gares, "mod_ligne_depart")
    with c2:
        arrivee = commun.choisir_gare("Nouvelle gare d'arrivée", gares, "mod_ligne_arrivee")
    st.caption("Impossible si des trajets existent déjà sur cette ligne.")
    if st.form_submit_button("Modifier la ligne", type="primary"):
        if id_ligne is None:
            st.warning("Choisissez la ligne à modifier.")
        elif depart is None or arrivee is None:
            st.warning("Choisissez les deux gares.")
        else:
            try:
                reponse = api.modifier_ligne(commun.token(), id_ligne, depart["nom"], arrivee["nom"])
                commun.flash(f"{reponse['message']} (ligne #{reponse['id_ligne']}).")
                st.rerun()
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)

with supprimer, st.form("supprimer_ligne"):
    id_ligne = st.selectbox("Ligne à supprimer", list(lignes), index=None, format_func=libelle,
                            placeholder="Choisissez une ligne", key="sup_id_ligne")
    confirme = st.checkbox("Je confirme la suppression")
    st.caption("Impossible si des trajets existent encore sur cette ligne.")
    if st.form_submit_button("Supprimer la ligne"):
        if id_ligne is None:
            st.warning("Choisissez la ligne à supprimer.")
        elif not confirme:
            st.warning("Cochez la case de confirmation.")
        else:
            try:
                reponse = api.supprimer_ligne(commun.token(), id_ligne)
                commun.flash(reponse["message"])
                st.rerun()
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)
