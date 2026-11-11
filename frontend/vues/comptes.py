import streamlit as st

import api
import commun

GRADES = ["CLIENT", "COLLABORATEUR", "ADMIN"]

st.title("Gestion des comptes")
commun.afficher_flash()

with st.form("chercher_compte"):
    mode = st.radio("Rechercher par", ["Nom d'utilisateur", "Identifiant"], horizontal=True)
    c1, c2 = st.columns(2)
    nom = c1.text_input("Nom d'utilisateur")
    identifiant = c2.number_input("Identifiant", min_value=1, step=1)
    if st.form_submit_button("Rechercher", type="primary", icon=":material/search:"):
        try:
            if mode == "Identifiant":
                compte = api.rechercher_compte(commun.token(), id_utilisateur=int(identifiant))
            elif not nom.strip():
                compte = None
                st.warning("Saisissez un nom d'utilisateur.")
            else:
                compte = api.rechercher_compte(commun.token(), nom_utilisateur=nom.strip())
            st.session_state.compte_trouve = compte
        except api.ErreurAPI as e:
            st.session_state.pop("compte_trouve", None)
            commun.afficher_erreur(e)

compte = st.session_state.get("compte_trouve")
if not compte:
    st.stop()

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric("Identifiant", f"#{compte['id']}")
    c2.metric("Nom d'utilisateur", compte["nom_utilisateur"])
    c3.metric("Grade", compte["grade"])

if compte["grade"] == "ADMIN":
    st.info("Les droits d'un administrateur ne peuvent pas être modifiés.")
    st.stop()

with st.form("modifier_grade"):
    nouveau = st.selectbox("Nouveau grade", GRADES, index=GRADES.index(compte["grade"]))
    if nouveau == "ADMIN":
        st.caption(":warning: Un administrateur ne peut plus être rétrogradé ensuite.")
    if st.form_submit_button("Enregistrer", type="primary"):
        if nouveau == compte["grade"]:
            st.info("Le grade est inchangé.")
        else:
            try:
                st.session_state.compte_trouve = api.modifier_grade(commun.token(), compte["id"], nouveau)
                commun.flash(f"{compte['nom_utilisateur']} est maintenant {nouveau}.")
                st.rerun()
            except api.ErreurAPI as e:
                commun.afficher_erreur(e)
