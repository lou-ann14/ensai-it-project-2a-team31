import streamlit as st

import api
import commun

st.title("Trains")
commun.afficher_flash()

rechercher, creer, capacite = st.tabs(["Rechercher", "Créer", "Modifier la capacité"])


def afficher_train(train: dict):
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Numéro", train["num_train"])
        c2.metric("Type", train["type_train"] or "—")
        c3.metric("Places 1re", train["places_premieres"])
        c4.metric("Places 2de", train["places_secondes"])
        st.caption(f"Identifiant interne (à utiliser pour les trajets) : #{train['id_train']}")


with rechercher, st.form("chercher_train"):
    num = st.number_input("Numéro du train", min_value=0, step=1, key="cherche_num")
    if st.form_submit_button("Rechercher", icon=":material/search:"):
        try:
            afficher_train(api.trouver_train(commun.token(), int(num)))
        except api.ErreurAPI as e:
            commun.afficher_erreur(e)

with creer, st.form("creer_train"):
    c1, c2 = st.columns(2)
    num = c1.number_input("Numéro du train", min_value=0, step=1, key="creer_num")
    type_train = c2.selectbox("Type", ["TGV", "TER", "Intercités", "Ouigo", "Autre"])
    c3, c4 = st.columns(2)
    premieres = c3.number_input("Places en 1re classe", min_value=0, step=1, value=50)
    secondes = c4.number_input("Places en 2de classe", min_value=0, step=1, value=300)
    if st.form_submit_button("Créer le train", type="primary"):
        try:
            train = api.creer_train(commun.token(), type_train, int(premieres), int(secondes), int(num))
            st.success(f"Train n°{train['num_train']} créé.")
            afficher_train(train)
        except api.ErreurAPI as e:
            commun.afficher_erreur(e)

with capacite:
    with st.form("charger_train"):
        num = st.number_input("Numéro du train", min_value=0, step=1, key="cap_num")
        if st.form_submit_button("Charger"):
            try:
                st.session_state.train_a_modifier = api.trouver_train(commun.token(), int(num))
            except api.ErreurAPI as e:
                st.session_state.pop("train_a_modifier", None)
                commun.afficher_erreur(e)

    train = st.session_state.get("train_a_modifier")
    if train:
        afficher_train(train)
        with st.form("modifier_capacite"):
            c1, c2 = st.columns(2)
            premieres = c1.number_input("Nouvelles places en 1re", min_value=0, step=1,
                                        value=train["places_premieres"])
            secondes = c2.number_input("Nouvelles places en 2de", min_value=0, step=1,
                                       value=train["places_secondes"])
            if st.form_submit_button("Enregistrer", type="primary"):
                try:
                    st.session_state.train_a_modifier = api.modifier_capacite(
                        commun.token(), train, int(premieres), int(secondes)
                    )
                    commun.flash(f"Capacité du train n°{train['num_train']} mise à jour.")
                    st.rerun()
                except api.ErreurAPI as e:
                    commun.afficher_erreur(e)
