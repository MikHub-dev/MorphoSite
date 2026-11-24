#!/usr/bin/env python3
"""Générateur de MorphoSite.

Lit les parcours dans _source/projets/p*.py (listes PROJETS), et écrit :
  ../index.html                 accueil (liste des 32 projets)
  ../projets/NN-slug.html       une page par projet
Usage : python3 build.py
"""
import html, math, importlib.util, pathlib, re

SRC = pathlib.Path(__file__).resolve().parent
OUT = SRC.parent

COL = {"cyan": "#5fd4f0", "violet": "#a78bfa", "violet2": "#c4b5fd", "teal": "#5fd1b3", "orange": "#f5a65b",
       "pink": "#f0719a", "gold": "#f3cf7a", "blue": "#6ea8ff", "muted": "#7c85ab", "ink": "#eef1fb"}

PARTS = {
    1: ("Partie I", "Fondations : fonctions, réseaux, logique", "blue"),
    2: ("Partie II", "Espace et symétries", "cyan"),
    3: ("Partie III", "Temps, calcul, optimisation", "teal"),
    4: ("Partie IV", "Probabilités, décision, information", "orange"),
    5: ("Partie V", "Ondes, signaux, matière", "gold"),
    6: ("Partie VI", "Le monde quantique", "pink"),
    7: ("Partie VII", "Horizons du XXIe siècle", "violet"),
}

CHAPTERS = {  # numéro : (titre, page de début, page du cas concret)
    1: ("Pourquoi transformer ?", 10, 20), 2: ("Des relations aux réseaux", 24, 31), 3: ("Preuves et programmes", 34, 41),
    4: ("Ensembles, logique et circuits", 43, 50), 5: ("Déplacer sans déformer", 54, 60), 6: ("Tourner, symétriser", 62, 69),
    7: ("Déformer sans déchirer", 71, 78), 8: ("Courber l'espace et le temps", 80, 86), 9: ("Modéliser le temps", 89, 95),
    10: ("Calculer sans résoudre", 97, 104), 11: ("Trouver le meilleur chemin", 106, 112), 12: ("Comment apprend une IA ?", 114, 120),
    13: ("Piloter un système", 122, 128), 14: ("Mesurer le hasard", 132, 138), 15: ("Le hasard qui évolue", 140, 146),
    16: ("Apprendre du hasard", 148, 154), 17: ("Décider à plusieurs", 156, 162), 18: ("Coder l'information", 165, 171),
    19: ("Le secret et la confiance", 173, 179), 20: ("Décomposer un signal", 182, 188), 21: ("Mouvement et conservation", 190, 196),
    22: ("Chaleur, ondes et champs", 198, 204), 23: ("Remonter de l'effet à la cause", 206, 212), 24: ("Du bit au qubit", 216, 222),
    25: ("Portes et circuits quantiques", 224, 230), 26: ("Du qubit à l'ordinateur", 234, 240),
    27: ("Après RSA : la cryptographie post-quantique", 242, 248), 28: ("Prouver sans révéler", 250, 256),
    29: ("Les mathématiques de la finance", 258, 264), 30: ("Le cerveau qui calcule", 266, 272),
    31: ("Voyager entre les mondes", 274, 280), 32: ("Les frontières de l'intelligence artificielle", 283, 289),
}


def part_of(ch):
    return 1 if ch <= 4 else 2 if ch <= 8 else 3 if ch <= 13 else 4 if ch <= 19 else 5 if ch <= 23 else 6 if ch <= 25 else 7


def esc(s):
    return html.escape(str(s), quote=True)


def c(name):
    return COL.get(name, name)


# ---------------------------------------------------------------- schémas SVG
FONT = 'font-family="Jost,sans-serif"'


def _wrap(label, n=12):
    words, lines, cur = str(label).split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= n:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def _text_lines(x, y, lines, size=12, color="#eef1fb", anchor="middle", lh=None):
    lh = lh or size * 1.2
    y0 = y - (len(lines) - 1) * lh / 2
    return "".join(f'<text x="{x:.1f}" y="{y0 + i * lh + size * .35:.1f}" fill="{color}" font-size="{size}" {FONT} text-anchor="{anchor}">{esc(t)}</text>'
                   for i, t in enumerate(lines))


def art_chain(a):
    """Boîtes reliées par des flèches, verticalement. edges: liste 'ok'/'no'/'' ; labels d'arêtes optionnels."""
    nodes = a["nodes"]
    edges = a.get("edges", [""] * (len(nodes) - 1))
    elab = a.get("elabels", [""] * (len(nodes) - 1))
    n = len(nodes)
    bh, gap = 34, 30
    H = n * bh + (n - 1) * gap + 10
    out = [f'<svg viewBox="0 0 220 {H}" role="img" aria-label="{esc(a.get("alt", "schéma"))}">']
    for i, lab in enumerate(nodes):
        y = 5 + i * (bh + gap)
        col = c(a.get("colors", {}).get(str(i), "cyan")) if isinstance(a.get("colors"), dict) else c("cyan")
        out.append(f'<rect x="30" y="{y}" width="160" height="{bh}" rx="9" fill="#121839" stroke="{col}" stroke-width="1.6"/>')
        out.append(_text_lines(110, y + bh / 2, _wrap(lab, 24), 12.5))
        if i < n - 1:
            ec = c("teal") if edges[i] == "ok" else c("orange") if edges[i] == "no" else c("muted")
            y1, y2 = y + bh + 3, y + bh + gap - 3
            out.append(f'<line x1="110" y1="{y1}" x2="110" y2="{y2 - 6}" stroke="{ec}" stroke-width="2.2"/>')
            out.append(f'<path d="M104 {y2 - 8} L110 {y2} L116 {y2 - 8}Z" fill="{ec}"/>')
            if elab[i]:
                out.append(f'<text x="120" y="{(y1 + y2) / 2 + 4}" fill="{ec}" font-size="11.5" {FONT}>{esc(elab[i])}</text>')
    out.append("</svg>")
    return "".join(out)


def art_hchain(a):
    """2 ou 3 boîtes horizontales."""
    nodes = a["nodes"]
    n = len(nodes)
    W, bw = 220, (220 - (n - 1) * 22 - 8) / n
    edges = a.get("edges", [""] * (n - 1))
    elab = a.get("elabels", [""] * (n - 1))
    out = [f'<svg viewBox="0 0 {W} 120" role="img" aria-label="{esc(a.get("alt", "schéma"))}">']
    for i, lab in enumerate(nodes):
        x = 4 + i * (bw + 22)
        out.append(f'<rect x="{x:.1f}" y="38" width="{bw:.1f}" height="44" rx="9" fill="#121839" stroke="{c("cyan")}" stroke-width="1.6"/>')
        out.append(_text_lines(x + bw / 2, 60, _wrap(lab, int(bw / 6.6)), 11.5))
        if i < n - 1:
            ec = c("teal") if edges[i] == "ok" else c("orange") if edges[i] == "no" else c("muted")
            xa = x + bw + 3
            out.append(f'<path d="M{xa:.1f} 60 L{xa + 12:.1f} 60" stroke="{ec}" stroke-width="2.2"/><path d="M{xa + 10:.1f} 55 L{xa + 17:.1f} 60 L{xa + 10:.1f} 65Z" fill="{ec}"/>')
            if elab[i]:
                out.append(_text_lines(xa + 8, 100, _wrap(elab[i], 12), 11, ec))
    out.append("</svg>")
    return "".join(out)


def art_graph(a):
    """nodes: [[label,x,y,color?]], edges: [[i,j,color?,label?]], directed: bool. Repère 0-200 x 0-170."""
    out = [f'<svg viewBox="0 0 220 180" role="img" aria-label="{esc(a.get("alt", "graphe"))}">']
    if a.get("directed"):
        out.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#a78bfa"/></marker></defs>')
    N = a["nodes"]
    r = a.get("r", 17)
    for e in a.get("edges", []):
        i, j = e[0], e[1]
        col = c(e[2]) if len(e) > 2 and e[2] else c("violet")
        x1, y1, x2, y2 = N[i][1], N[i][2], N[j][1], N[j][2]
        d = math.hypot(x2 - x1, y2 - y1) or 1
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        sx, sy, ex, ey = x1 + ux * r, y1 + uy * r, x2 - ux * (r + 2), y2 - uy * (r + 2)
        mk = ' marker-end="url(#ah)"' if a.get("directed") else ""
        dash = ' stroke-dasharray="5 4"' if len(e) > 4 and e[4] == "dash" else ""
        out.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{col}" stroke-width="2"{mk}{dash}/>')
        if len(e) > 3 and e[3]:
            out.append(f'<text x="{(x1 + x2) / 2 + 4:.1f}" y="{(y1 + y2) / 2 - 4:.1f}" fill="{col}" font-size="11" {FONT}>{esc(e[3])}</text>')
    for nd in N:
        col = c(nd[3]) if len(nd) > 3 and nd[3] else c("cyan")
        out.append(f'<circle cx="{nd[1]}" cy="{nd[2]}" r="{r}" fill="#121839" stroke="{col}" stroke-width="2"/>')
        out.append(_text_lines(nd[1], nd[2], [nd[0]], 11.5 if len(nd[0]) > 2 else 13, "#eef1fb"))
    out.append("</svg>")
    return "".join(out)


def art_plot(a):
    """curves: [{f:'expr en x', color, label, dash}], x:[a,b], y:[a,b], points:[[x,y,label]], hlines:[[y,label]], xlabel, ylabel."""
    X0, X1 = a["x"]
    Y0, Y1 = a["y"]
    L, R, T, B = 30, 210, 12, 150
    sx = lambda x: L + (x - X0) / (X1 - X0) * (R - L)
    sy = lambda y: B - (y - Y0) / (Y1 - Y0) * (B - T)
    out = [f'<svg viewBox="0 0 220 180" role="img" aria-label="{esc(a.get("alt", "courbe"))}">',
           f'<line x1="{L}" y1="{B}" x2="{R}" y2="{B}" stroke="#7c85ab" stroke-width="1.3"/><line x1="{L}" y1="{T}" x2="{L}" y2="{B}" stroke="#7c85ab" stroke-width="1.3"/>']
    env = {k: getattr(math, k) for k in ("exp", "log", "sin", "cos", "sqrt", "pi", "tanh", "atan", "floor")}
    env.update(abs=abs, round=round, min=min, max=max)
    for hl in a.get("hlines", []):
        out.append(f'<line x1="{L}" y1="{sy(hl[0]):.1f}" x2="{R}" y2="{sy(hl[0]):.1f}" stroke="#7c85ab" stroke-dasharray="4 4"/>')
        if len(hl) > 1:
            out.append(f'<text x="{R - 2}" y="{sy(hl[0]) - 4:.1f}" fill="#aab2d3" font-size="10.5" {FONT} text-anchor="end">{esc(hl[1])}</text>')
    for cv in a.get("curves", []):
        pts = []
        steps = cv.get("n", 120)
        if "pts" in cv:  # courbe donnée point par point
            pts = [f"{sx(x):.1f},{sy(y):.1f}" for x, y in cv["pts"]]
            steps = -1
        for k in range(steps + 1):
            x = X0 + (X1 - X0) * k / steps
            try:
                y = eval(cv["f"], {"__builtins__": {}}, dict(env, x=x))
            except (ZeroDivisionError, ValueError, OverflowError):
                continue
            y = max(min(y, Y1 + (Y1 - Y0)), Y0 - (Y1 - Y0))
            pts.append(f"{sx(x):.1f},{sy(y):.1f}")
        dash = ' stroke-dasharray="6 5"' if cv.get("dash") else ""
        out.append(f'<clipPath id="cp"><rect x="{L}" y="{T - 4}" width="{R - L + 4}" height="{B - T + 4}"/></clipPath>')
        out.append(f'<polyline clip-path="url(#cp)" points="{" ".join(pts)}" fill="none" stroke="{c(cv.get("color", "cyan"))}" stroke-width="{cv.get("w", 2.6)}"{dash}/>')
        if cv.get("label"):
            lx, ly = cv.get("lpos", [X1, None])
            if ly is None and "pts" in cv:
                ly = min(cv["pts"], key=lambda q: abs(q[0] - lx))[1]
            if ly is None:
                ly = eval(cv["f"], {"__builtins__": {}}, dict(env, x=lx))
            out.append(f'<text x="{sx(lx):.1f}" y="{sy(ly) - 6:.1f}" fill="{c(cv.get("color", "cyan"))}" font-size="11" {FONT} text-anchor="{cv.get("anchor", "end")}">{esc(cv["label"])}</text>')
    for p in a.get("points", []):
        p = list(p)
        if p[1] is None:  # point posé sur la première courbe
            p[1] = eval(a["curves"][0]["f"], {"__builtins__": {}}, dict(env, x=p[0]))
        col = c(p[3] if len(p) > 3 else "gold")
        out.append(f'<circle cx="{sx(p[0]):.1f}" cy="{sy(p[1]):.1f}" r="4" fill="{col}"/>')
        if len(p) > 2 and p[2]:
            right = sx(p[0]) > 160
            tx = sx(p[0]) - 6 if right else sx(p[0]) + 6
            ty = sy(p[1]) - 6 if sy(p[1]) > T + 14 else sy(p[1]) + 15
            out.append(f'<text x="{tx:.1f}" y="{ty:.1f}" fill="{col}" font-size="11" {FONT} text-anchor="{"end" if right else "start"}">{esc(p[2])}</text>')
    if a.get("xlabel"):
        out.append(f'<text x="{R}" y="{B + 16}" fill="#aab2d3" font-size="11" {FONT} text-anchor="end">{esc(a["xlabel"])}</text>')
    if a.get("ylabel"):
        out.append(f'<text x="{L + 4}" y="{T + 2}" fill="#aab2d3" font-size="11" {FONT}>{esc(a["ylabel"])}</text>')
    out.append("</svg>")
    return "".join(out)


def _fr(v):
    """Nombre à la française : virgule décimale, espace des milliers."""
    if isinstance(v, float) and not v.is_integer():
        return str(v).replace(".", ",")
    v = int(v)
    return f"{v:,}".replace(",", "\u202f") if abs(v) >= 10000 else str(v)


def art_bars(a):
    """items: [[label, valeur, couleur?]], max, unit."""
    it = a["items"]
    m = a.get("max") or max(v[1] for v in it)
    n = len(it)
    bw = min(40, (180 - (n - 1) * 10) / n)
    tot = n * bw + (n - 1) * 10
    x0 = 20 + (180 - tot) / 2
    out = [f'<svg viewBox="0 0 220 180" role="img" aria-label="{esc(a.get("alt", "diagramme"))}"><line x1="14" y1="140" x2="206" y2="140" stroke="#7c85ab"/>']
    for i, (lab, v, *rest) in enumerate(it):
        col = c(rest[0]) if rest else c("cyan")
        h = 112 * v / m
        x = x0 + i * (bw + 10)
        out.append(f'<rect x="{x:.1f}" y="{140 - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="4" fill="{col}" opacity=".85"/>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{134 - h:.1f}" fill="{col}" font-size="11" {FONT} text-anchor="middle">{esc(a.get("fmt", "{}").format(_fr(v)))}</text>')
        out.append(_text_lines(x + bw / 2, 156, _wrap(lab, max(6, int(bw / 5))), 10.5, "#aab2d3"))
    out.append("</svg>")
    return "".join(out)


def art_grid(a):
    """Tableau de valeurs : rows (liste de listes), head (en-têtes de colonnes), side (en-têtes de lignes), hl: [[i,j]]."""
    rows = a["rows"]
    head = a.get("head")
    side = a.get("side")
    nr, nc = len(rows), len(rows[0])
    off_x = 30 if side else 4
    off_y = 22 if head else 4
    cw = (214 - off_x) / nc
    ch = min(30, (170 - off_y) / nr)
    H = off_y + nr * ch + 6
    hl = {tuple(x) for x in a.get("hl", [])}
    out = [f'<svg viewBox="0 0 220 {H:.0f}" role="img" aria-label="{esc(a.get("alt", "tableau"))}">']
    if head:
        for j, hd in enumerate(head):
            out.append(f'<text x="{off_x + cw * j + cw / 2:.1f}" y="15" fill="#aab2d3" font-size="11" {FONT} text-anchor="middle">{esc(hd)}</text>')
    for i, r in enumerate(rows):
        y = off_y + i * ch
        if side:
            out.append(f'<text x="{off_x - 6}" y="{y + ch / 2 + 4:.1f}" fill="#aab2d3" font-size="11" {FONT} text-anchor="end">{esc(side[i])}</text>')
        for j, v in enumerate(r):
            x = off_x + j * cw
            on = (i, j) in hl
            out.append(f'<rect x="{x + 1:.1f}" y="{y + 1:.1f}" width="{cw - 2:.1f}" height="{ch - 2:.1f}" rx="4" fill="{"rgba(95,212,240,.22)" if on else "#121839"}" stroke="{c("cyan") if on else "rgba(140,155,220,.25)"}"/>')
            out.append(f'<text x="{x + cw / 2:.1f}" y="{y + ch / 2 + 4.5:.1f}" fill="{"#fff" if on else "#d6daf0"}" font-size="{12.5 if len(str(v)) < 5 else 10.5}" {FONT} text-anchor="middle">{esc(v)}</text>')
    out.append("</svg>")
    return "".join(out)


def art_icons(a):
    """items: liste d'emoji ou de textes, séparés par des flèches ; labels sous chaque élément."""
    it = a["items"]
    labs = a.get("labels", [""] * len(it))
    n = len(it)
    w = 220 / n
    out = [f'<svg viewBox="0 0 220 130" role="img" aria-label="{esc(a.get("alt", "illustration"))}">']
    for i, e in enumerate(it):
        x = w * i + w / 2
        if e in ("→", "↔", "⟶", "+", "=", "×", "≠", "⇒"):
            out.append(f'<text x="{x:.1f}" y="66" fill="{c("violet2")}" font-size="26" {FONT} text-anchor="middle">{esc(e)}</text>')
        else:
            size = 40 if len(e) <= 2 else 16
            out.append(f'<text x="{x:.1f}" y="{70 if len(e) <= 2 else 64}" font-size="{size}" text-anchor="middle" fill="#eef1fb" {FONT}>{esc(e)}</text>')
        if labs[i]:
            out.append(_text_lines(x, 104, _wrap(labs[i], max(7, int(w / 6.5))), 11, "#aab2d3"))
    out.append("</svg>")
    return "".join(out)


def art_big(a):
    """Formule ou nombre mis en valeur."""
    lines = a["lines"]
    out = [f'<svg viewBox="0 0 220 140" role="img" aria-label="{esc(a.get("alt", "formule"))}">',
           '<rect x="6" y="6" width="208" height="128" rx="16" fill="rgba(167,139,250,.08)" stroke="rgba(167,139,250,.45)"/>']
    n = len(lines)
    for i, ln in enumerate(lines):
        txt, size, col = (ln + [None, None])[:3] if isinstance(ln, list) else (ln, None, None)
        size = size or (30 if i == 0 else 13)
        y = 70 - (n - 1) * 17 + i * 34
        out.append(f'<text x="110" y="{y + size * .35:.0f}" fill="{c(col or ("#fff" if i == 0 else "muted2"))}" font-size="{size}" font-family="{"Cormorant Garamond,serif" if i == 0 else "Jost,sans-serif"}" text-anchor="middle">{esc(txt)}</text>')
    out.append("</svg>")
    return "".join(out).replace("muted2", "#aab2d3")


ARTS = {"chain": art_chain, "hchain": art_hchain, "graph": art_graph, "plot": art_plot, "bars": art_bars,
        "grid": art_grid, "icons": art_icons, "big": art_big, "svg": lambda a: a["svg"]}


def render_art(a):
    if not a:
        return ""
    return ARTS[a["type"]](a)


# ---------------------------------------------------------------- gabarit
HEAD = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<script src="https://mikhub-dev.github.io/RoutineSite/famzak-verrou.js?v=3" onerror="document.documentElement.hidden=true"></script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600;700&family=Cormorant+Garamond:ital,wght@0,500;1,400;1,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='29' fill='%23070b1f' stroke='%23a78bfa' stroke-width='3'/%3E%3Ctext x='32' y='44' font-size='34' text-anchor='middle' fill='%23c4b5fd' font-style='italic' font-family='Georgia'%3E%CF%86%3C/text%3E%3C/svg%3E">
</head>
<body{bodyattr}>
<header class="nav"><div class="wrap">
  <a class="brand" href="{root}index.html"><span class="dot">φ</span><span>Morpho<b>Site</b></span></a>
  <nav class="menu"><a href="{root}index.html"{cur_home}>Projets</a><a href="{root}index.html#comment">Comment lire</a><a href="{root}livre/Les_Mathematiques_des_Transformations_v8.0.pdf" target="_blank" rel="noopener">Le livre (PDF)</a><a href="https://famzak.github.io/">FamZakSites</a></nav>
</div></header>
"""

FOOT = """<footer class="footer"><div class="wrap"><span>MorphoSite · complément du livre <i>Les Mathématiques des Transformations</i></span><span>Un site de la famille <a href="https://famzak.github.io/" style="color:var(--muted);font-weight:600">FamZakSites</a></span></div></footer>
"""

SCRIPT = """<script>
/* Parcours : étape courante, étapes atteintes gardées sur l'appareil, « Devine d'abord » et bilan.
   Stockage : localStorage « famzak:morpho:<page> » = {vues:[n°], devine:{q1:true|false}, fini:bool}.
   Sans JavaScript, les réponses restent visibles (et la recherche de l'accueil les lit toujours). */
(function(){
const PAGE=location.pathname.split('/').pop().replace(/[.]html$/,'');
const CLE='famzak:morpho:'+PAGE,CLE_MODE='famzak:morpho:mode-devine';
function lire(){try{return Object.assign({vues:[],devine:{},fini:false},JSON.parse(localStorage.getItem(CLE))||{})}catch(e){return{vues:[],devine:{},fini:false}}}
function ecrire(){try{localStorage.setItem(CLE,JSON.stringify(etat))}catch(e){}}
let etat=lire();
let mode=true;try{mode=localStorage.getItem(CLE_MODE)!=='non'}catch(e){}
const steps=[...document.querySelectorAll('.step,#bilan')];
const qs=[...document.querySelectorAll('article.step')];
const links=[...document.querySelectorAll('#rail a')];
const bar=document.getElementById('progbar'),txt=document.getElementById('progtxt');
const N=steps.length-1;
/* Devine d'abord */
const score=document.createElement('div');score.className='devine-score';
document.querySelector('.rail .prog').after(score);
const bascule=document.createElement('label');bascule.className='devine-mode';
bascule.innerHTML='<input type="checkbox"'+(mode?' checked':'')+'> Mode « devine d’abord »';
score.after(bascule);
function majScore(){const v=Object.values(etat.devine),ok=v.filter(Boolean).length;
score.innerHTML=v.length?'<b>'+ok+' / '+v.length+'</b> trouvées en devinant'+(v.length===qs.length&&ok===qs.length?' · sans faute 🏆':''):'';}
qs.forEach(a=>{
  const id=a.id,box=document.createElement('div');box.className='devine';
  box.innerHTML='<p>🤔 <b>Devine d’abord</b> : réfléchis à ta réponse, puis découvre la nôtre.</p><button type="button" class="dv-voir">Voir la réponse</button>';
  const juge=document.createElement('div');juge.className='devine-juge';
  juge.innerHTML='<span>Ta réponse ressemblait-elle à la nôtre ?</span><button type="button" data-v="1">✓ Oui, j’avais trouvé</button><button type="button" data-v="0">✗ Non, pas trouvé</button>';
  const q=a.querySelector('.qhead');q.after(box);
  const ans=a.querySelector('.answer');ans.after(juge);
  function cacher(on){a.classList.toggle('cache',on);box.hidden=!on;}
  function majJuge(){const v=etat.devine[id];juge.hidden=!mode||a.classList.contains('cache');
    juge.querySelectorAll('button').forEach(b=>b.classList.toggle('sel',v!==undefined&&String(+v)===b.dataset.v));}
  box.querySelector('.dv-voir').addEventListener('click',()=>{cacher(false);majJuge();juge.querySelector('button').focus({preventScroll:true});});
  juge.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;etat.devine[id]=b.dataset.v==='1';ecrire();majJuge();majScore();});
  a._maj=()=>{cacher(mode&&etat.devine[id]===undefined);majJuge();};a._maj();
});
bascule.querySelector('input').addEventListener('change',e=>{mode=e.target.checked;try{localStorage.setItem(CLE_MODE,mode?'oui':'non')}catch(_){};qs.forEach(a=>a._maj());});
majScore();
/* Étape courante et étapes atteintes */
function upd(){
  const y=window.scrollY+window.innerHeight*0.35;let cur=0;
  steps.forEach((s,i)=>{if(s.offsetTop<=y)cur=i});
  let change=false;
  for(let i=0;i<=cur;i++)if(!etat.vues.includes(i+1)){etat.vues.push(i+1);change=true}
  if(cur>=N&&!etat.fini){etat.fini=true;change=true;fete();}
  if(change)ecrire();
  links.forEach((a,i)=>{a.classList.toggle('cur',i===cur);a.classList.toggle('done',i!==cur&&etat.vues.includes(i+1))});
  const nv=etat.vues.filter(n=>n<=N).length;
  bar.style.width=(etat.fini?100:nv/N*100)+'%';
  txt.textContent=etat.fini?'Parcours terminé ✓':'Étape '+(cur+1)+' sur '+N;
}
function fete(){const b=document.getElementById('bilan');if(!b||b.querySelector('.bravo'))return;
  const d=document.createElement('div');d.className='bravo';d.textContent='🎉 Parcours terminé : il compte maintenant dans « Mes projets terminés » sur l’accueil.';b.prepend(d);}
if(etat.fini)fete();
window.addEventListener('scroll',upd,{passive:true});upd();
})();
</script>
"""


def slug_file(p):
    return f'{p["ch"]:02d}-{p["slug"]}.html'


_PAGES = None


def find_page(phrase):
    """Page imprimée du livre où apparaît la phrase (page PDF − 1)."""
    global _PAGES
    if _PAGES is None:
        import subprocess
        pdf = OUT / "livre" / "Les_Mathematiques_des_Transformations_v8.0.pdf"
        if not pdf.exists():
            pdf = OUT.parent / "Les_Mathematiques_des_Transformations_v8.0.pdf"
        txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
        _PAGES = [" ".join(p.split()) for p in txt.split("\f")]
    ph = " ".join(phrase.split())
    for i, p in enumerate(_PAGES):
        if ph in p:
            return i  # index 0-based = numéro de page PDF − 1 = page imprimée
    print("  !! phrase introuvable :", phrase)
    return None


def book_chip(b, ch_default):
    if b is None:
        return ""
    if isinstance(b, int):
        b = {"ch": b}
    ch = b.get("ch", ch_default)
    title, p0, pc = CHAPTERS[ch]
    page = b.get("p") or (find_page(b["find"]) if b.get("find") else None) or (pc if b.get("cas") else p0)
    label = b.get("label") or title
    return f'<span class="book">📖 Dans le livre : <b>ch. {ch}</b>, {esc(label) if not b.get("raw") else label}, p. {page}</span>'


def render_project(p, prev, nxt, all_projects):
    ch = p["ch"]
    part = part_of(ch)
    acc = c(p.get("color", PARTS[part][2]))
    steps = p["steps"]
    rail = "".join(f'<li><a href="#q{i + 1}"><span class="n">{i + 1}</span>{esc(s.get("short", s["q"]))}</a></li>' for i, s in enumerate(steps))
    rail += '<li><a href="#bilan"><span class="n">✓</span>Bilan</a></li>'
    chapters_used = sorted({ch} | {(s.get("book") if isinstance(s.get("book"), int) else (s.get("book") or {}).get("ch", ch)) for s in steps if s.get("book") is not None})
    body = []
    for i, s in enumerate(steps):
        art = render_art(s.get("art"))
        math_html = ""
        if s.get("mt"):
            math_html = f'<div class="math"><span class="t">Les maths derrière : {esc(s["mt"])}</span>'
            if s.get("f"):
                math_html += f'<span class="f">{s["f"]}</span>'
            math_html += f'<p>{s.get("mp", "")}</p></div>'
        morph = f'<span class="morph">φ Morphisme : {s["morph"]}</span>' if s.get("morph") else ""
        more = ""
        if s.get("more"):
            t, h = s["more"]
            more = f'<details><summary>{esc(t)}</summary>{h if h.lstrip().startswith("<") else "<p>" + h + "</p>"}</details>'
        body.append(f'''<article class="step{'' if art else ' noart'}" id="q{i + 1}">
<div>
<div class="qhead"><div class="qnum">{i + 1}</div><div><div class="qlab">Question {i + 1}</div><h2>{esc(s["q"])}</h2></div></div>
<p class="answer">{s["a"]}</p>
{math_html}
{morph}
{book_chip(s.get("book", ch), ch)}
{more}
</div>
{f'<div class="art">{art}<div class="cap">{esc(s.get("cap", ""))}</div></div>' if art else ''}
</article>''')
    bl = p["bilan"]
    chain = "".join((f"<span>{esc(x)}</span>" if k % 2 == 0 else "") for k, x in enumerate(sum([[n, "→"] for n in bl["chain"]], [])[:-1]))
    chain = '<em>→</em>'.join(f"<span>{esc(n)}</span>" for n in bl["chain"])
    if bl.get("loop"):
        chain += "<em>↺</em>"
    rows = "".join(f"<tr><td>{esc(r[0])}</td><td>{esc(r[1])}</td><td>{esc(r[2])}</td></tr>" for r in bl["rows"])
    play = p.get("play")
    play_html = ""
    if play:
        play_html = f'''<section class="play"><div class="qlab">À toi de jouer</div><h2>{esc(play["t"])}</h2>
<p class="answer" style="font-size:16px">{play["q"]}</p>
<details><summary>Voir la réponse</summary><p>{play["r"]}</p></details></section>'''
    nexts = []
    if nxt:
        nexts.append(f'<a href="{slug_file(nxt)}"><small>Projet suivant · ch. {nxt["ch"]}</small>{nxt["emoji"]} {esc(nxt["card"])} →</a>')
    if prev:
        nexts.append(f'<a href="{slug_file(prev)}"><small>Projet précédent · ch. {prev["ch"]}</small>← {prev["emoji"]} {esc(prev["card"])}</a>')
    link = p.get("link")
    if link:
        lp = next((q for q in all_projects if q["ch"] == link[0]), None)
        if lp:
            nexts.append(f'<a href="{slug_file(lp)}"><small>{esc(link[1])}</small>{lp["emoji"]} {esc(lp["card"])} →</a>')
    nexts.append('<a href="../index.html"><small>Tous les projets</small>Revenir aux 32 projets →</a>')
    hero_art = render_art(p.get("hero")) if p.get("hero") else f'<div class="hero-emoji">{p["emoji"]}</div>'
    title_html = esc(p["title"])
    if p.get("em"):
        title_html = title_html.replace(esc(p["em"]), f'<em>{esc(p["em"])}</em>', 1)
    doc = HEAD.format(title=esc(p["card"]) + " · MorphoSite", desc=esc(p["desc"]), root="../", bodyattr=f' style="--acc:{acc}"', cur_home="")
    doc += f'''<section class="sky"><div class="wrap hero">
<div class="crumb"><a href="../index.html">Projets</a> › {esc(PARTS[part][0])} › Chapitre {ch}</div>
<div class="hero-grid"><div>
<div class="kicker">Projet {ch} · parcours de construction</div>
<h1>{title_html}</h1>
<p class="lead">{p["lead"]}</p>
<div class="facts"><div><b>{len(steps)}</b>questions</div><div><b>{len(chapters_used)}</b>chapitre{"s" if len(chapters_used) > 1 else ""} du livre</div><div><b>≈ {max(10, len(steps) * 3)} min</b>de lecture</div></div>
</div><div class="hero-art">{hero_art}</div></div>
</div></section>
<div class="wrap"><div class="layout">
<aside class="rail"><h4>Le parcours</h4><ol id="rail">{rail}</ol>
<div class="prog"><span id="progtxt"></span><div class="bar"><i id="progbar"></i></div></div></aside>
<main>
{"".join(body)}
<section class="recap" id="bilan"><div class="qlab">Bilan</div><h2>{esc(bl["title"])}</h2>
<div class="chain">{chain}</div>
<table><thead><tr><th>Transformation</th><th>Ce qui est conservé</th><th>Ce qui change</th></tr></thead><tbody>{rows}</tbody></table>
</section>
{play_html}
<div class="next">{"".join(nexts[:3])}</div>
</main></div></div>
'''
    doc += FOOT + SCRIPT + '<script src="../famzak-progres.js" data-site="morphosite"></script>\n' + "</body>\n</html>\n"
    return doc


def render_index(projects):
    cards = []
    for part in range(1, 8):
        ps = [p for p in projects if part_of(p["ch"]) == part]
        if not ps:
            continue
        pc = c(PARTS[part][2])
        items = []
        for p in ps:
            tags = " · ".join(p.get("tags", []))
            items.append(f'''<a class="pcard" href="projets/{slug_file(p)}" data-part="{part}" data-search="{esc((p["card"] + " " + p["desc"] + " " + tags + " " + CHAPTERS[p["ch"]][0]).lower())}">
<div class="top"><div class="ic">{p["emoji"]}</div><div class="ch">Chapitre {p["ch"]} · {len(p["steps"])} questions</div></div>
<h4>{esc(p["card"])}</h4><p>{esc(p["desc"])}</p>
<div class="math-tags">{esc(tags)}</div>
<div class="go">Suivre le parcours →</div></a>''')
        cards.append(f'''<section class="part-block" data-part="{part}" style="--pc:{pc}"><h2>{PARTS[part][0]}</h2><h3>{esc(PARTS[part][1])}</h3>
<div class="pgrid">{"".join(items)}</div></section>''')
    filt = '<button aria-pressed="true" data-f="0">Tous</button>' + "".join(f'<button aria-pressed="false" data-f="{k}">{v[0].replace("Partie ", "")} · {esc(v[1].split(" :")[0].split(",")[0])}</button>' for k, v in PARTS.items())
    doc = HEAD.format(title="MorphoSite · les mathématiques des transformations", desc="32 projets concrets, du thermomètre connecté au voyage vers Mars, et les mathématiques qui les font marcher.", root="", bodyattr="", cur_home=' class="cur"')
    total_q = sum(len(p["steps"]) for p in projects)
    doc += f'''<section class="sky"><div class="wrap home-hero">
<div class="kicker" style="color:var(--violet2)">L'Atlas des transformations · complément du livre</div>
<h1>Construire le monde, <em>une transformation à la fois</em></h1>
<div class="td-row">
<figure class="td-scene td-g"><svg data-3d="choco" viewBox="0 0 240 240" role="img" aria-label="Un donut au chocolat en 3D qui se déforme lentement en tasse couleur chocolat, puis redevient donut"></svg>
<figcaption class="td-phrase">Pour un topologue, une tasse et un donut sont le même objet.</figcaption></figure>
<div class="td-mid">
<p class="quote">« Les mathématiques ne sont pas seulement l'étude des nombres. Elles sont l'étude des transformations qui permettent de comprendre le monde. »</p>
<p class="lead">{len(projects)} projets concrets, un par chapitre du livre. Pour chacun, les questions à se poser dans l'ordre, des réponses simples, puis les mathématiques qui se cachent derrière.</p>
</div>
<figure class="td-scene td-d"><svg data-3d="fraise" viewBox="0 0 240 240" role="img" aria-label="Une tasse rose en 3D qui se déforme lentement en donut à la fraise, puis redevient tasse"></svg>
<figcaption class="td-vign"><div class="td-eq"><div><span class="td-emo">☕</span><small>un trou</small></div><span class="td-cong">≅</span><div><span class="td-emo">🍩</span><small>un trou</small></div></div>
<p class="td-sous">Même nombre de trous, même forme</p></figcaption></figure>
</div>
<div class="facts"><div><b>{len(projects)}</b>projets</div><div><b>{total_q}</b>questions</div><div><b>7</b>parties</div></div>
<div class="how" id="comment">
<div><b>1 · Une question</b>Chaque étape part d'une question qu'un ingénieur se poserait vraiment, dans l'ordre de construction.</div>
<div><b>2 · Une réponse simple</b>D'abord l'idée, en mots de tous les jours et avec un schéma. Les détails sont repliés.</div>
<div><b>3 · Les maths derrière</b>La notion, la formule clé, le morphisme en jeu, et la page du livre où tout est expliqué.</div>
</div>
</div></section>
<div class="wrap" style="padding-top:36px">
<input class="search" type="search" placeholder="Chercher un projet : drone, GPS, vaccin, Mars…" aria-label="Chercher un projet">
<div class="hits" hidden aria-live="polite"></div>
<div class="mesprojets" id="mesprojets" hidden></div>
<div class="filters">{filt}</div>
{"".join(cards)}
</div>
'''
    doc += FOOT + r"""<script>
const q=document.querySelector('.search'),btns=[...document.querySelectorAll('.filters button')];let part='0';
function apply(){const s=q.value.trim().toLowerCase();
document.querySelectorAll('.pcard').forEach(c=>{const ok=(part==='0'||c.dataset.part===part)&&(!s||c.dataset.search.includes(s));c.classList.toggle('hidden',!ok)});
document.querySelectorAll('.part-block').forEach(b=>b.classList.toggle('hidden',!b.querySelector('.pcard:not(.hidden)')));}
q.addEventListener('input',apply);
/* Recherche dans les parcours : chaque question (et le bilan) des 32 pages projets/,
   lues à la première frappe ; un résultat ouvre la page sur la bonne question. */
const hits=document.querySelector('.hits'),norm=t=>t.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const escH=t=>t.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let idx=null,charge=null;
function charger(){if(charge)return charge;
const urls=[...new Set([...document.querySelectorAll('.pcard')].map(c=>c.getAttribute('href')))];
charge=Promise.all(urls.map(u=>fetch(u).then(r=>r.ok?r.text():'').catch(()=>'').then(h=>{if(!h)return[];
const d=new DOMParser().parseFromString(h,'text/html'),proj=(d.title||'').split(' · ')[0];
d.querySelectorAll('svg,script,style').forEach(n=>n.remove());
d.querySelectorAll('p,div,h2,li,td,th,span,em').forEach(n=>n.after(' '));
return[...d.querySelectorAll('article.step[id],section.recap[id]')].map(b=>{const h=b.querySelector('h2'),lab=b.querySelector('.qlab'),
x=b.textContent.replace(/\s+/g,' ').trim(),t=h?h.textContent.trim():proj;
return{u:u+'#'+b.id,t,p:proj,l:lab?lab.textContent.trim():'',x,nt:norm(t),nx:norm(x)}})}))).then(l=>{idx=l.flat();return idx});
return charge}
function extrait(e,mots){let i=-1;for(const m of mots){i=e.nx.indexOf(m);if(i>=0)break}
if(i<0||e.nx.length!==e.x.length)return escH(e.x.slice(0,150))+'…';
let a=Math.max(0,i-60);const b=Math.min(e.x.length,i+120);if(a>0){const sp=e.x.indexOf(' ',a);if(sp>-1&&sp<i)a=sp+1}
const brut=e.x.slice(a,b),n=norm(brut),r=[];mots.forEach(m=>{let k=0;while((k=n.indexOf(m,k))>-1){r.push([k,k+m.length]);k+=m.length}});
r.sort((x,y)=>x[0]-y[0]);let out='',pos=0;r.forEach(([d,f])=>{if(d<pos)return;out+=escH(brut.slice(pos,d))+'<mark>'+escH(brut.slice(d,f))+'</mark>';pos=f});out+=escH(brut.slice(pos));
return(a>0?'…':'')+out+(b<e.x.length?'…':'')}
async function chercherParcours(){const brut=q.value.trim(),mots=norm(brut).split(/\s+/).filter(m=>m.length>1);
if(!mots.length){hits.hidden=true;hits.innerHTML='';return}
const l=await charger();if(q.value.trim()!==brut)return;
const res=l.map(e=>{let s=0;for(const m of mots){const t=e.nt.includes(m),x=e.nx.includes(m);if(!t&&!x)return null;s+=t?10:1}return{e,s}}).filter(Boolean).sort((a,b)=>b.s-a.s);
if(!res.length){hits.hidden=true;hits.innerHTML='';return}
const vus=res.slice(0,12);
hits.innerHTML='<div class="hits-tete">Dans les parcours · '+res.length+(res.length>1?' passages':' passage')+(res.length>vus.length?' (les '+vus.length+' premiers)':'')+'</div>'+
vus.map(({e})=>'<a class="hit" href="'+escH(e.u)+'"><span class="hit-t">'+escH(e.t)+'</span><span class="hit-p">'+escH(e.p)+(e.l?' · '+escH(e.l):'')+'</span><span class="hit-x">'+extrait(e,mots)+'</span></a>').join('');
hits.hidden=false}
q.addEventListener('input',chercherParcours);
q.addEventListener('focus',charger,{once:true});
btns.forEach(b=>b.addEventListener('click',()=>{part=b.dataset.f;btns.forEach(x=>x.setAttribute('aria-pressed',x===b));apply()}));
/* Mes projets : état de chaque parcours, lu dans localStorage (« famzak:morpho:<page> »). */
(function(){const cartes=[...document.querySelectorAll('.pcard')];let fin=0,cours=0,devOk=0,devN=0;
const lire=k=>{try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}};
cartes.forEach(c=>{const page=c.getAttribute('href').split('/').pop().replace(/[.]html$/,''),e=lire('famzak:morpho:'+page);
const nq=+(c.querySelector('.ch').textContent.match(/(\d+) questions/)||[0,0])[1];
if(!e)return;const v=Object.values(e.devine||{});devN+=v.length;devOk+=v.filter(Boolean).length;
const et=document.createElement('div');et.className='etat'+(e.fini?' fini':'');
const vues=(e.vues||[]).filter(n=>n<=nq).length;
et.textContent=e.fini?'✓ Terminé'+(v.length?' · '+v.filter(Boolean).length+'/'+v.length+' devinées':''):'En cours · '+vues+'/'+nq;
c.querySelector('.top').appendChild(et);if(e.fini)fin++;else if(vues)cours++;});
const box=document.getElementById('mesprojets');if(!fin&&!cours)return;
const paliers=[[1,'🌱','Premier projet'],[8,'🥉','8 projets'],[16,'🥈','16 projets'],[32,'🏆','Les 32 projets']];
box.innerHTML='<div class="mp-tete"><b>Mes projets terminés : '+fin+' / '+cartes.length+'</b>'+(cours?'<span>'+cours+' en cours</span>':'')+(devN?'<span>'+devOk+' / '+devN+' questions trouvées en devinant</span>':'')+'</div>'+
'<div class="mp-barre"><i style="width:'+(fin/cartes.length*100)+'%"></i></div>'+
'<div class="mp-grille">'+cartes.map(c=>{const p=c.getAttribute('href').split('/').pop().replace(/[.]html$/,''),e=lire('famzak:morpho:'+p);
return '<a href="'+c.getAttribute('href')+'" title="'+escH(c.querySelector('h4').textContent)+'" class="'+(e&&e.fini?'ok':e?'encours':'')+'">'+c.querySelector('.ic').textContent+'</a>'}).join('')+'</div>'+
'<div class="mp-badges">'+paliers.map(([n,i,t])=>'<span class="'+(fin>=n?'ok':'')+'">'+i+' '+t+'</span>').join('')+'</div><p class="mp-note">Gardé sur cet appareil.</p>';
box.hidden=false})();
</script>
<script src="assets/tasse-donut-3d.js" defer></script>
<script src="famzak-progres.js" data-site="morphosite"></script>
</body>
</html>
"""
    return doc


def load_projects():
    projects = []
    for f in sorted((SRC / "projets").glob("p*.py")):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        projects.extend(m.PROJETS)
    projects.sort(key=lambda p: p["ch"])
    return projects


def main():
    projects = load_projects()
    (OUT / "projets").mkdir(exist_ok=True)
    for i, p in enumerate(projects):
        prev = projects[i - 1] if i > 0 else None
        nxt = projects[i + 1] if i + 1 < len(projects) else None
        (OUT / "projets" / slug_file(p)).write_text(render_project(p, prev, nxt, projects), encoding="utf-8")
    (OUT / "index.html").write_text(render_index(projects), encoding="utf-8")
    print(f"{len(projects)} projets générés, {sum(len(p['steps']) for p in projects)} questions.")


if __name__ == "__main__":
    main()
