import streamlit as st

import api
import commun

st.title("Gares")

st.subheader("Importer des gares depuis l'API SNCF")
with st.form("importer"):
    texte = st.text_input("Nom de gare ou de ville", placeholder="ex. Rennes")
    lancer = st.form_submit_button("Importer", type="primary", icon=":material/download:")

if lancer:
    if len(texte.strip()) < 2:
        st.warning("Saisissez au moins 2 caractères.")
    else:
        try:
            with st.spinner("Interrogation de l'API SNCF…"):
                importees = api.importer_gares(commun.token(), texte.strip())
            commun.liste_gares.clear()
            if importees:
                st.success(f"{len(importees)} gare(s) importée(s) ou mise(s) à jour.")
                st.dataframe(importees, hide_index=True, width="stretch",
                             column_order=["id_gare", "nom", "ville", "id_sncf"])
            else:
                st.info("L'API SNCF n'a trouvé aucune gare pour ce texte.")
        except api.ErreurAPI as e:
            commun.afficher_erreur(e)

st.divider()
st.subheader("Gares enregistrées")
try:
    gares = commun.liste_gares(commun.token())
except api.ErreurAPI as e:
    commun.afficher_erreur(e)
    st.stop()

filtre = st.text_input("Filtrer", placeholder="Nom ou ville…", label_visibility="collapsed")
if filtre:
    f = filtre.casefold()
    gares = [g for g in gares if f in g["nom"].casefold() or f in (g.get("ville") or "").casefold()]
st.caption(f"{len(gares)} gare(s)")
st.dataframe(gares, hide_index=True, width="stretch",
             column_order=["id_gare", "nom", "ville", "id_sncf"])
