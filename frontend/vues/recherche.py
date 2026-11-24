import streamlit as st

import api
import commun
import style

utilisateur = commun.utilisateur()
# Tous les grades peuvent réserver (un collaborateur ou un administrateur a aussi les droits d'un client)
est_client = utilisateur["grade"] in ("CLIENT", "COLLABORATEUR", "ADMIN")

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
    c1, c2, c3 = st.columns([2, 2, 1.5])
    with c1:
        depart = commun.choisir_gare("Gare de départ", gares, "rech_depart")
    with c2:
        arrivee = commun.choisir_gare("Gare d'arrivée", gares, "rech_arrivee")
    with c3:
        jour = st.date_input(
            "Date (facultatif)", value=None, format="DD/MM/YYYY",
            help="Sans date, tous les trajets à venir sont affichés.",
        )
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
# Sans date choisie, les trajets peuvent être de jours différents : le jour est alors affiché
sans_date = resultats["jour"] is None


def duree_panneau(minutes: int | None) -> str:
    """
    Écrit une durée pour le panneau.

    Param:
    ------
    minutes: int | None
        la durée en minutes, ou None si elle est inconnue

    Return:
    ------
    str
        la durée, ou des tirets si elle est inconnue
    """
    if minutes is None:
        return "--"
    h, m = divmod(minutes, 60)
    return f"{h}H{m:02d}"


def places_panneau(places: int | None) -> str:
    """
    F5 : écrit le nombre de places restantes dans une classe.

    Param:
    ------
    places: int | None
        le nombre de places, ou None s'il est inconnu

    Return:
    ------
    str
        le nombre de places, COMPLET s'il n'y en a plus, ou des tirets s'il est inconnu
    """
    if places is None:
        return "--"
    return "COMPLET" if places == 0 else str(places)


style.panneau_departs(
    f"{resultats['depart']['nom']} → {resultats['arrivee']['nom']}",
    colonnes=([("DATE", 5, False)] if sans_date else [])
           + [("DÉPART", 5, False), ("ARRIVÉE", 5, False), ("DURÉE", 5, False),
              ("TRAIN", 5, False), ("2DE CL.", 8, True), ("1RE CL.", 8, True),
              ("PL. 2DE", 7, True), ("PL. 1RE", 7, True)],
    lignes=[
        ([commun.date_heure(t["heure_depart"])[:5]] if sans_date else [])
        + [
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
    message_vide="AUCUN TRAIN À VENIR" if sans_date else "AUCUN TRAIN CE JOUR",
)
periode = "Tous les trajets à venir" if sans_date else commun.jour(resultats["jour"]).capitalize()
st.caption(f"{periode} · {len(trajets)} trajet(s)")


def libelle_trajet(t: dict) -> str:
    """
    Texte d'un trajet dans le choix du train (le jour est ajouté si la recherche est sans date).

    Param:
    ------
    t: dict
        le trajet

    Return:
    ------
    str
        les horaires et le numéro du train
    """
    depart = commun.date_heure(t["heure_depart"]) if sans_date else commun.heure(t["heure_depart"])
    return (
        f"{depart} → {commun.heure(t['heure_arrivee'])}"
        + (f" · train {t['num_train']}" if t.get("num_train") else "")
    )


# --- F5 : tarification transparente -------------------------------------------------
POSTES_PRIX = [
    ("cout_exploitation", "Coût d'exploitation (personnel, énergie, entretien)"),
    ("peage_reseau", "Péage réseau (versé à SNCF Réseau)"),
    ("marge", "Marge de la compagnie"),
    ("tva", "TVA (10 %)"),
    ("prix_total", "Prix payé"),
]
avec_detail = [t for t in trajets if t.get("detail_prix_seconde") and t.get("detail_prix_premiere")]
if avec_detail:
    with st.expander("Tarification transparente : où va votre argent ?", icon=":material/euro:"):
        for t in avec_detail:
            st.markdown(f"**{libelle_trajet(t)}**")
            st.dataframe(
                [
                    {
                        "Poste": libelle,
                        "2de classe": commun.euros(t["detail_prix_seconde"][cle]),
                        "1re classe": commun.euros(t["detail_prix_premiere"][cle]),
                    }
                    for cle, libelle in POSTES_PRIX
                ],
                hide_index=True,
                width="stretch",
            )

if not trajets or not est_client:
    st.stop()

# --- Réservation (FO1) : la place est attribuée automatiquement ou choisie parmi les libres ---
st.subheader("Réserver une place")

billet = st.session_state.pop("dernier_billet", None)
if billet:
    st.success(
        f"Réservation confirmée (place {billet['place']}), voici votre billet :",
        icon=":material/check_circle:",
    )
    commun.afficher_billet(billet)

AUTO = "Attribution automatique"
par_id = {t["id_trajet"]: t for t in trajets}
id_trajet = st.selectbox("Train", list(par_id), format_func=lambda i: libelle_trajet(par_id[i]), key="resa_trajet")
f1, f2 = st.columns(2)
classe = f1.radio("Classe", [2, 1], format_func=commun.libelle_classe, horizontal=True, key="resa_classe")

try:
    places = api.places_libres(commun.token(), id_trajet)
except api.ErreurAPI as e:
    commun.afficher_erreur(e)
    st.stop()

libres = places["libres_premiere"] if classe == 1 else places["libres_seconde"]
capacite = places["capacite_premiere"] if classe == 1 else places["capacite_seconde"]
if not libres:
    f2.warning(f"Complet en {commun.libelle_classe(classe)}.", icon=":material/block:")
    st.stop()

choix = f2.selectbox(
    f"Place ({len(libres)} libre(s) sur {capacite})",
    [AUTO, *libres],
    help="Par défaut, la première place libre vous est attribuée. Vous pouvez aussi choisir votre place.",
    key=f"resa_place_{id_trajet}_{classe}",
)
st.caption(f"Prix : {commun.euros(commun.prix_classe(par_id[id_trajet]['tarif_base'], classe))}")

if st.button("Confirmer la réservation", type="primary", icon=":material/confirmation_number:"):
    try:
        reservation = api.reserver(commun.token(), id_trajet, None if choix == AUTO else str(choix), classe)
    except api.ErreurAPI as e:
        commun.afficher_erreur(e)
        st.stop()
    # Met à jour les places restantes affichées dans le panneau
    try:
        resultats["trajets"] = api.rechercher_trajets(
            commun.token(), resultats["depart"]["nom"], resultats["arrivee"]["nom"], resultats["jour"]
        )
    except api.ErreurAPI:
        pass
    st.session_state.dernier_billet = reservation
    st.rerun()
