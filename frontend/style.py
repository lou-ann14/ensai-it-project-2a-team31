"""Identité visuelle : panneau d'affichage à lettres défilantes et billets de train.

Tout est en HTML/CSS (st.html), sans JavaScript. Les animations sont désactivées
pour les personnes qui ont demandé à réduire les animations dans leur système.
"""

import random
from datetime import datetime
from html import escape

import streamlit as st

NUIT = "#0b1d33"
NUIT_2 = "#13294a"
AMBRE = "#ffb000"
PAPIER = "#f6f3ec"
ENCRE = "#14213d"

# Caractères qui défilent avant d'afficher le bon (comme sur un afficheur à palettes)
_DEFILEMENT = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

_CSS = f"""
<style>
/* --- Interface générale -------------------------------------------------- */
[data-testid="stMainMenu"], [data-testid="stAppDeployButton"], footer {{ display: none !important; }}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}
[data-testid="stMainBlockContainer"] {{ padding-top: 1.6rem; }}

/* Titres de page : plaque émaillée de quai */
[data-testid="stMain"] h1 {{ display: inline-block; text-transform: uppercase; letter-spacing: .04em;
    background: {NUIT}; color: {PAPIER} !important; padding: .25rem 1rem .15rem;
    border-radius: 6px; border-left: 7px solid {AMBRE}; font-size: 1.9rem; margin-bottom: .6rem;
    box-shadow: 0 4px 0 rgba(11,29,51,.15); }}
[data-testid="stMain"] h1 a {{ display: none !important; }}

/* --- Bandeau de gare (haut de page) -------------------------------------- */
.st-key-entete {{ background: {NUIT}; border-radius: 12px; padding: .7rem 1.2rem;
    border-bottom: 4px solid {AMBRE}; box-shadow: 0 8px 22px rgba(11,29,51,.18); }}
.marque {{ display: flex; align-items: center; gap: .8rem; }}
.marque-logo {{ width: 2.4rem; height: 2.4rem; border-radius: 50%; background: {AMBRE}; color: {NUIT};
    display: grid; place-items: center; font: 700 1.05rem 'Barlow Condensed', sans-serif; }}
.marque-texte {{ font-family: 'Barlow Condensed', sans-serif; font-weight: 700; font-size: 1.5rem;
    letter-spacing: .08em; color: {PAPIER}; line-height: 1; }}
.marque-texte small {{ display: block; font-size: .72rem; letter-spacing: .2em; color: {AMBRE}; margin-top: .2rem; }}
.voyageur {{ border-left: 2px dashed rgba(246,243,236,.35); padding-left: 1rem; color: {PAPIER}; line-height: 1.2; }}
.voyageur label {{ display: block; font: 600 .62rem 'IBM Plex Sans', sans-serif; letter-spacing: .2em;
    color: {AMBRE}; text-transform: uppercase; }}
.voyageur strong {{ display: block; font: 600 1.05rem 'IBM Plex Mono', monospace; }}
.voyageur span {{ font-size: .78rem; opacity: .7; }}
.st-key-deconnexion button {{ background: transparent !important; color: {PAPIER} !important;
    border: 1px solid rgba(246,243,236,.35) !important; }}
.st-key-deconnexion button:hover {{ border-color: {AMBRE} !important; color: {AMBRE} !important; }}

/* --- Menu : une ligne de train dont chaque page est un arrêt ------------- */
.st-key-ligne {{ margin: .4rem 0 1.4rem; }}
.st-key-ligne [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; overflow-x: auto;
    gap: 0 !important; padding-bottom: .2rem; }}
.st-key-ligne [data-testid="stColumn"] {{ position: relative; min-width: 7.5rem !important;
    flex: 1 1 0 !important; width: auto !important; }}
/* le rail : deux demi-segments par arrêt, coupés aux extrémités de la ligne */
.st-key-ligne [data-testid="stColumn"]::before {{ content: ""; position: absolute; top: 8px; height: 6px;
    left: 0; right: 0; background: {NUIT}; }}
.st-key-ligne [data-testid="stColumn"]:first-child::before {{ left: 50%; }}
.st-key-ligne [data-testid="stColumn"]:last-child::before {{ right: 50%; }}
.st-key-ligne [data-testid="stColumn"]:only-child::before {{ display: none; }}
[class*="st-key-arret"] {{ position: relative; align-items: center; text-align: center;
    padding-top: 1.75rem; gap: 0 !important; }}
/* le point d'arrêt */
[class*="st-key-arret"]::before {{ content: ""; position: absolute; top: 2px; left: 50%; z-index: 1;
    width: 18px; height: 18px; transform: translateX(-50%); border-radius: 50%;
    background: {PAPIER}; border: 4px solid {NUIT}; box-sizing: border-box; transition: transform .15s; }}
[class*="st-key-arret"]:hover::before {{ transform: translateX(-50%) scale(1.2); }}
[class*="st-key-arret_actif"]::before {{ width: 26px; height: 26px; top: -2px; background: {AMBRE};
    box-shadow: 0 0 0 4px rgba(255,176,0,.25); }}
[class*="st-key-arret"] [data-testid="stPageLink"] a {{ justify-content: center; background: transparent !important;
    padding: .1rem .4rem; }}
[class*="st-key-arret"] [data-testid="stPageLink"] p {{ font: 700 1.02rem 'Barlow Condensed', sans-serif;
    letter-spacing: .06em; text-transform: uppercase; white-space: nowrap; }}
[class*="st-key-arret_actif"] [data-testid="stPageLink"] p {{ text-decoration: underline 3px {AMBRE};
    text-underline-offset: 5px; }}
.arret-groupe {{ font: 600 .62rem 'IBM Plex Sans', sans-serif; letter-spacing: .18em; color: #7a7f8c; }}
[class*="st-key-arret_actif"] .arret-groupe {{ color: #a36f00; }}

/* --- Guichet (page de connexion) ----------------------------------------- */
.st-key-guichet {{ background: #fbf7ec; border: 1px solid #d9d1bf; border-radius: 14px 14px 10px 10px;
    padding: 0 1.3rem 1.2rem; overflow: hidden; box-shadow: 0 10px 26px rgba(20,33,61,.10); }}
.guichet-entete {{ display: flex; justify-content: space-between; margin: 0 -1.3rem .3rem;
    padding: .55rem 1.3rem; background: {NUIT}; color: {PAPIER};
    font: 700 1rem 'Barlow Condensed', sans-serif; letter-spacing: .25em;
    border-bottom: 4px solid {AMBRE}; }}
.guichet-entete .ouvert {{ color: #7fd18b; font-size: .8rem; letter-spacing: .15em; }}

/* Étapes du voyage, dessinées comme une ligne verticale */
.etapes {{ list-style: none; margin: .6rem 0 0; padding: 0; }}
.etapes li {{ position: relative; padding: 0 0 1.6rem 2.6rem; }}
.etapes li::before {{ content: ""; position: absolute; left: 6px; top: 6px; width: 18px; height: 18px;
    border-radius: 50%; background: {PAPIER}; border: 4px solid {NUIT}; box-sizing: border-box; z-index: 1; }}
.etapes li::after {{ content: ""; position: absolute; left: 12px; top: 14px; bottom: -6px; width: 6px;
    background: {NUIT}; }}
.etapes li:last-child::after {{ display: none; }}
.etapes li:last-child::before {{ background: {AMBRE}; }}
.etapes b {{ display: block; font: 700 1.5rem 'Barlow Condensed', sans-serif; text-transform: uppercase;
    letter-spacing: .05em; line-height: 1.1; }}
.etapes span {{ color: #5b6478; }}

/* --- Palettes de l'afficheur -------------------------------------------- */
.pa {{ --h: 1.55em; font-family: 'IBM Plex Mono', ui-monospace, monospace; font-weight: 600; }}
.pa-car {{ display: inline-block; position: relative; width: .78em; height: var(--h);
          margin: 0 1px; overflow: hidden; vertical-align: middle; text-align: center;
          background: linear-gradient({NUIT_2} 0 50%, #0f2440 50% 100%);
          border-radius: 2px; color: {AMBRE}; line-height: var(--h);
          box-shadow: inset 0 1px 0 rgba(255,255,255,.06); }}
.pa-car::after {{ content: ""; position: absolute; left: 0; right: 0; top: 50%;
                 height: 1px; background: rgba(0,0,0,.6); }}
.pa-car.vide {{ background: #0e2240; }}
.pa-bande {{ display: block; animation: pa-defile var(--d) steps(var(--k), end) var(--r) both; }}
.pa-bande > span {{ display: block; height: var(--h); }}
@keyframes pa-defile {{ to {{ transform: translateY(calc(var(--k) * var(--h) * -1)); }} }}
@media (prefers-reduced-motion: reduce) {{
  .pa-bande {{ animation: none; transform: translateY(calc(var(--k) * var(--h) * -1)); }}
}}

/* --- Panneau des départs ------------------------------------------------- */
.panneau {{ background: {NUIT}; border-radius: 12px; padding: 1.1rem 1.2rem 1.3rem;
           box-shadow: 0 10px 30px rgba(11,29,51,.25); overflow-x: auto; margin-bottom: 1rem; }}
.panneau-haut {{ display: flex; justify-content: space-between; align-items: center; gap: 1rem;
                color: {PAPIER}; font-family: 'Barlow Condensed', sans-serif; font-weight: 700;
                letter-spacing: .14em; font-size: .95rem; margin-bottom: .8rem; }}
.panneau-haut .horloge {{ color: {AMBRE}; font-family: 'IBM Plex Mono', monospace; letter-spacing: .05em; }}
.panneau-titre {{ font-size: 1.25rem; margin-bottom: 1rem; line-height: 1.9; }}
.panneau table {{ border-collapse: collapse; width: max-content; min-width: 100%; }}
.panneau th {{ color: rgba(246,243,236,.55); font: 600 .72rem 'IBM Plex Sans', sans-serif;
              letter-spacing: .14em; text-align: left; padding: 0 1.1rem .35rem 0; }}
.panneau td {{ padding: .3rem 1.1rem .3rem 0; border-top: 1px solid rgba(246,243,236,.07);
              font-size: 1.02rem; white-space: nowrap; }}
.panneau td.num {{ text-align: right; }}

/* --- Billet --------------------------------------------------------------- */
.billet {{ position: relative; display: flex; background: #fbf7ec; color: {ENCRE};
          border-radius: 10px; margin: .2rem 0 .6rem; overflow: hidden;
          box-shadow: 0 1px 0 #e6dcc6, 0 6px 18px rgba(20,33,61,.10); }}
.billet-corps {{ flex: 1; min-width: 0; }}
.billet-entete {{ display: flex; justify-content: space-between; gap: 1rem; padding: .45rem 1.1rem;
                 background: {NUIT}; color: {PAPIER}; font: 700 .8rem 'Barlow Condensed', sans-serif;
                 letter-spacing: .16em; }}
.billet.premiere .billet-entete {{ background: linear-gradient(90deg, {NUIT} 70%, #6b5310); }}
.billet-entete .classe {{ color: {AMBRE}; }}
.billet-trajet {{ display: grid; grid-template-columns: auto 1fr auto; align-items: center;
                 gap: 1rem; padding: .9rem 1.1rem .5rem; }}
.b-heure {{ font: 600 1.75rem 'IBM Plex Mono', monospace; line-height: 1; }}
.b-gare {{ font-weight: 600; font-size: .95rem; margin-top: .2rem; }}
.b-droite {{ text-align: right; }}
.b-voie {{ position: relative; height: 2px; background: repeating-linear-gradient(90deg, {ENCRE} 0 8px, transparent 8px 12px); }}
.b-voie::before, .b-voie::after {{ content: ""; position: absolute; top: -4px; width: 10px; height: 10px;
                                  border-radius: 50%; background: {ENCRE}; }}
.b-voie::before {{ left: -2px; }} .b-voie::after {{ right: -2px; }}
.b-duree {{ text-align: center; font-size: .78rem; color: #5b6478; margin-top: .45rem; }}
.billet-pied {{ display: flex; flex-wrap: wrap; gap: .4rem 1.6rem; padding: .5rem 1.1rem .85rem;
               font-size: .9rem; }}
.billet label, .billet-talon label {{ display: block; font: 600 .66rem 'IBM Plex Sans', sans-serif;
                                     letter-spacing: .14em; color: #7a7f8c; text-transform: uppercase; }}
.billet-talon {{ position: relative; width: 9.5rem; flex-shrink: 0; padding: .8rem 1rem;
                border-left: 2px dashed #cdbf9f; text-align: center; background: #f4eedd; }}
.billet-talon::before, .billet-talon::after {{ content: ""; position: absolute; left: -11px; width: 20px;
                                              height: 20px; border-radius: 50%; background: {PAPIER}; }}
.billet-talon::before {{ top: -10px; }} .billet-talon::after {{ bottom: -10px; }}
.b-place {{ font: 600 2.1rem 'IBM Plex Mono', monospace; line-height: 1.1; margin-bottom: .35rem; }}
.code-barre {{ height: 34px; margin-top: .6rem; }}
.tampon {{ position: absolute; right: 11.5rem; top: 50%; transform: translateY(-50%) rotate(-12deg);
          border: 3px solid #b3261e; color: #b3261e; border-radius: 6px; padding: .15rem .6rem;
          font: 700 1rem 'Barlow Condensed', sans-serif; letter-spacing: .14em; opacity: .75;
          pointer-events: none; }}
.billet.passe .billet-corps, .billet.passe .billet-talon {{ opacity: .62; }}
@media (max-width: 640px) {{
  .billet {{ flex-direction: column; }}
  .billet-talon {{ width: auto; border-left: none; border-top: 2px dashed #cdbf9f;
                  display: flex; justify-content: space-around; align-items: center; }}
  .billet-talon::before, .billet-talon::after {{ display: none; }}
  .code-barre {{ display: none; }}
  .tampon {{ right: 1rem; top: 3.2rem; transform: rotate(-12deg); }}
}}
</style>
"""


def appliquer():
    """Injecte la feuille de style (à appeler une fois par exécution, dans app.py)."""
    st.html(_CSS)


def marque() -> str:
    """Logo et nom du service (HTML), pour le bandeau du haut."""
    return ('<div class="marque"><div class="marque-logo">CS</div>'
            '<div class="marque-texte">CONCURRENT SNCF<small>RÉSEAU FERROVIAIRE</small></div></div>')


def etapes(liste: list[tuple[str, str]]) -> None:
    """Liste d'étapes reliées par un rail vertical (page de connexion)."""
    items = "".join(f"<li><b>{escape(t)}</b><span>{escape(d)}</span></li>" for t, d in liste)
    st.html(f'<ol class="etapes">{items}</ol>')


# --- Afficheur à palettes ------------------------------------------------------------

def _palettes(texte: str, rang: int = 0, sel: str = "") -> str:
    """Transforme un texte en palettes qui défilent puis s'arrêtent sur le bon caractère.
    Le tirage est déterminé par le texte : la même valeur ne se ré-anime pas à chaque rerun."""
    morceaux = []
    for i, car in enumerate(texte.upper()):
        if car == " ":
            morceaux.append('<span class="pa-car vide"></span>')
            continue
        hasard = random.Random(f"{sel}|{texte}|{i}")
        k = hasard.randint(4, 9)
        bande = "".join(f"<span>{c}</span>" for c in hasard.choices(_DEFILEMENT, k=k))
        style = f"--k:{k};--d:{0.35 + k * 0.07:.2f}s;--r:{rang * 0.12 + i * 0.035:.2f}s"
        morceaux.append(
            f'<span class="pa-car"><span class="pa-bande" style="{style}">'
            f"{bande}<span>{escape(car)}</span></span></span>"
        )
    return f'<span class="pa" aria-label="{escape(texte)}">{"".join(morceaux)}</span>'


def titre_panneau(texte: str, sous_titre: str = "") -> None:
    """Grand titre façon afficheur (page de connexion)."""
    st.html(
        f'<div class="panneau"><div class="panneau-haut"><span>{escape(sous_titre)}</span>'
        f'<span class="horloge">{datetime.now():%H:%M}</span></div>'
        f'<div class="panneau-titre" style="font-size:1.7rem">{_palettes(texte, sel="titre")}</div></div>'
    )


def panneau_departs(titre: str, colonnes: list[tuple[str, int, bool]], lignes: list[list[str]],
                    message_vide: str = "AUCUN TRAIN") -> None:
    """Panneau des départs.

    colonnes : (intitulé, largeur en caractères, aligné à droite)
    lignes   : valeurs texte, dans l'ordre des colonnes
    """
    entete = "".join(f"<th>{escape(nom)}</th>" for nom, _, _ in colonnes)
    corps = []
    for rang, ligne in enumerate(lignes):
        cellules = []
        for (_, largeur, droite), valeur in zip(colonnes, ligne, strict=True):
            valeur = valeur[:largeur]
            valeur = valeur.rjust(largeur) if droite else valeur.ljust(largeur)
            cellules.append(f'<td class="{"num" if droite else ""}">{_palettes(valeur, rang + 1)}</td>')
        corps.append(f"<tr>{''.join(cellules)}</tr>")
    if not lignes:
        corps.append(f'<tr><td colspan="{len(colonnes)}">{_palettes(message_vide, 1)}</td></tr>')

    st.html(
        f'<div class="panneau"><div class="panneau-haut"><span>DÉPARTS</span>'
        f'<span class="horloge">{datetime.now():%H:%M}</span></div>'
        f'<div class="panneau-titre">{_palettes(titre, sel="titre")}</div>'
        f"<table><thead><tr>{entete}</tr></thead><tbody>{''.join(corps)}</tbody></table></div>"
    )


# --- Billet ----------------------------------------------------------------------------

def _code_barre(graine: str) -> str:
    """Faux code-barres déterministe (dégradé CSS)."""
    hasard = random.Random(graine)
    arrets, x = [], 0
    while x < 100:
        noir, blanc = hasard.choice([1, 1, 2, 3]), hasard.choice([1, 2, 2, 3])
        arrets.append(f"{ENCRE} {x}% {min(x + noir, 100)}%")
        x += noir
        arrets.append(f"transparent {min(x, 100)}% {min(x + blanc, 100)}%")
        x += blanc
    return f'<div class="code-barre" style="background:linear-gradient(90deg,{",".join(arrets)})"></div>'


def billet(*, id_reservation: int, gare_depart: str, gare_arrivee: str, depart: str, arrivee: str,
           date: str, duree: str, num_train: str, place: str, classe: int, prix: str, passe: bool) -> None:
    """Affiche une réservation sous forme de billet de train."""
    e = escape
    classes = "billet" + (" premiere" if classe == 1 else "") + (" passe" if passe else "")
    libelle_classe = "1RE CLASSE" if classe == 1 else "2DE CLASSE"
    tampon = '<div class="tampon">VOYAGE EFFECTUÉ</div>' if passe else ""
    st.html(f"""
<div class="{classes}">
  <div class="billet-corps">
    <div class="billet-entete"><span>CONCURRENT SNCF · BILLET</span>
      <span class="classe">{libelle_classe}</span></div>
    <div class="billet-trajet">
      <div><div class="b-heure">{e(depart)}</div><div class="b-gare">{e(gare_depart)}</div></div>
      <div><div class="b-voie"></div><div class="b-duree">{e(duree)}</div></div>
      <div class="b-droite"><div class="b-heure">{e(arrivee)}</div><div class="b-gare">{e(gare_arrivee)}</div></div>
    </div>
    <div class="billet-pied">
      <div><label>Date</label>{e(date)}</div>
      <div><label>Train</label>{e(num_train)}</div>
      <div><label>Réservation</label>#{id_reservation}</div>
      <div><label>Prix</label>{e(prix)}</div>
    </div>
  </div>
  <div class="billet-talon">
    <div><label>Place</label><div class="b-place">{e(place)}</div></div>
    <div><label>Classe</label><strong>{classe}</strong></div>
    {_code_barre(f"billet-{id_reservation}")}
  </div>
  {tampon}
</div>""")
