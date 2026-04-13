"""
Dashboard Streamlit — Data Challenge Big Four (version améliorée)
Persona : Candidat (Alexandre, M2 école de commerce)
Auteurs : Joana & Mahélène — Master IMCDS, Paris 1 Panthéon-Sorbonne
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import re
import os
from unidecode import unidecode
import plotly.io as pio

# ── Template Plotly global — fonds transparents, texte blanc (thème sombre) ────
pio.templates["bigfour"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF", family="DM Sans, sans-serif", size=12),
        title=dict(font=dict(color="#FFFFFF", size=14)),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.1)",
            linecolor="rgba(255,255,255,0.2)",
            zerolinecolor="rgba(255,255,255,0.2)",
            tickfont=dict(color="#FFFFFF"),
            title=dict(font=dict(color="#FFFFFF")),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.1)",
            linecolor="rgba(255,255,255,0.2)",
            zerolinecolor="rgba(255,255,255,0.2)",
            tickfont=dict(color="#FFFFFF"),
            title=dict(font=dict(color="#FFFFFF")),
        ),
        legend=dict(font=dict(color="#FFFFFF"), bgcolor="rgba(0,0,0,0)"),
        coloraxis=dict(colorbar=dict(tickfont=dict(color="#FFFFFF"), title=dict(font=dict(color="#FFFFFF")))),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(gridcolor="rgba(255,255,255,0.15)", tickfont=dict(color="#FFFFFF")),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.15)", tickfont=dict(color="#FFFFFF")),
        ),
        annotationdefaults=dict(font=dict(color="#FFFFFF")),
    )
)
pio.templates.default = "plotly+bigfour"

# ── Configuration page ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Big Four — Dashboard Candidat",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette & constantes ───────────────────────────────────────────────────────
# ── Fonction utilitaire globale ────────────────────────────────────────────────
def norm(t):
    """Normalise un texte : minuscules + suppression accents."""
    if pd.isna(t) or t is None:
        return ""
    return unidecode(str(t).lower())


COLORS = {
    "deloitte": "#86BC25",
    "ey":       "#E8A000",
    "kpmg":     "#00338D",
    "pwc":      "#D04A02",
}
LABELS = {"deloitte": "Deloitte", "ey": "EY", "kpmg": "KPMG", "pwc": "PwC"}
FIRM_ORDER = ["deloitte", "ey", "kpmg", "pwc"]

THEMES = {
    "Travail stimulant": (
        "sous_theme_pro: Travail stimulant/ satisfaction dans le travail/ sens du travail / motivation",
        "sous_theme_con: Travail stimulant/ satisfaction dans le travail/ sens du travail / motivation",
    ),
    "Développement pro.": (
        "sous_theme_pro: Opportunité de développement professionnel",
        "sous_theme_con: Opportunité de développement professionnel",
    ),
    "Ambiance & équipe": (
        "sous_theme_pro: Ambiance et collaboration en équipe / appartenance à l\u2019entreprise",
        "sous_theme_con: Ambiance et collaboration en équipe / appartenance à l\u2019entreprise",
    ),
    "Management": (
        "sous_theme_pro: Bienveillance managériale et reconnaissance / qualité de l\u2019encadrement",
        "sous_theme_con: Bienveillance managériale et reconnaissance / qualité de l\u2019encadrement",
    ),
    "Flexibilité": (
        "sous_theme_pro: Flexibilité",
        "sous_theme_con: Flexibilité",
    ),
    "Équilibre vie pro/perso": (
        "sous_theme_pro: Equilibre vie privée - vie professionnelle",
        "sous_theme_con: Equilibre vie privée - vie professionnelle",
    ),
    "Charge de travail": (
        "sous_theme_pro: Charge de travail / travail stressant",
        "sous_theme_con: Charge de travail / travail stressant",
    ),
    "Aspect financier": (
        "sous_theme_pro: Aspect financier",
        "sous_theme_con: Aspect financier",
    ),
    "Autonomie": (
        "sous_theme_pro: Autonomie et liberté d\u2019action / confiance",
        "sous_theme_con: Autonomie et liberté d\u2019action / confiance",
    ),
}

# Poids par défaut pour le profil Alexandre
ALEXANDRE_DEFAULT = {
    "Travail stimulant":    3,
    "Développement pro.":  5,
    "Ambiance & équipe":   3,
    "Management":          3,
    "Flexibilité":         2,
    "Équilibre vie pro/perso": 3,
    "Charge de travail":   2,
    "Aspect financier":    3,
    "Autonomie":           2,
}

STOPWORDS_FR = {
    "de","du","des","le","la","les","un","une","et","en","à","au","aux","est",
    "que","qui","par","pour","sur","dans","avec","ce","se","pas","plus","très",
    "bien","mais","ou","donc","car","il","elle","on","nous","vous","ils","elles",
    "je","tu","ne","si","aussi","son","sa","ses","leur","leurs","tout","tous",
    "même","comme","être","avoir","faire","peu","trop","assez","peut","d","l",
    "the","and","of","is","to","a","in","for","it","an","that","this","with",
    "not","cest","quil","quelle","lequipe","lentreprise","bonne","bon","super",
    "cabinet","experience","collaborateur","aucun","rien","ras","nan","none",
    "travail","poste","emploi","job","stage","consultant","consulting",
}

# Mots positifs / négatifs pour sentiment léger
POSITIVE_WORDS = {
    "excellent","super","top","formidable","génial","bien","bonne","bon","parfait",
    "enrichissant","stimulant","interessant","interessante","développement","apprendre",
    "apprentissage","dynamique","équipe","ambiance","soudée","bienveillant","reconnu",
    "autonomie","confiance","flexible","formation","évoluer","progression","opportunité",
    "passionnant","agréable","qualité","professionnel","compétent","innovant","varié",
    "exciting","great","good","best","amazing","positive","friendly","learn","grow",
}
NEGATIVE_WORDS = {
    "mauvais","mauvaise","horrible","terrible","nul","nulle","pénible","difficile",
    "charge","surcharge","stressant","epuisant","épuisant","burnout","pression",
    "turnover","départ","licenciement","aucun","manque","insuffisant","faible","bas",
    "toxic","toxique","hierarchie","politique","injuste","inégalité","salaire","bas",
    "heures","longues","weekend","nuit","vie","équilibre","absent","inexistant",
    "bad","poor","terrible","awful","worst","negative","stress","overwork","toxic",
}

# ── CSS custom — compatible thème sombre & clair ───────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    /* ── Header ── */
    .main-header {
        background: linear-gradient(135deg, #0D1B3E 0%, #1A3A8F 60%, #2E5BFF 100%);
        padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 1.8rem;
        border: 1px solid rgba(46,91,255,0.3);
        box-shadow: 0 8px 32px rgba(13,27,62,0.3);
    }
    .main-header h1 { color: #ffffff !important; margin: 0; font-size: 2rem; font-weight: 700; }
    .main-header p  { color: #A8C0FF !important; margin: 0.4rem 0 0; font-size: 0.92rem; }
    .main-header .persona-tag {
        display: inline-block; background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3); border-radius: 20px;
        padding: 2px 12px; font-size: 0.82rem; color: #E0EAFF !important; margin-top: 0.6rem;
    }

    /* ── KPI cards — fond semi-transparent, texte adaptatif ── */
    .kpi-card {
        background: rgba(128,128,128,0.12);
        border-radius: 12px; padding: 1.2rem 1.4rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
        border-left: 5px solid; margin-bottom: 0.5rem;
        transition: transform 0.15s;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-value { font-size: 1.8rem; font-weight: 700; margin: 0; line-height: 1.1; }
    .kpi-label { font-size: 0.75rem; color: var(--text-color, inherit); opacity: 0.65;
                 margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-sub   { margin: 6px 0 0; font-size: 0.83rem; opacity: 0.8; }

    /* ── Callouts — fond semi-transparent avec bordure colorée ── */
    .callout {
        padding: 0.9rem 1.1rem; border-radius: 10px; border-left: 4px solid;
        margin: 0.6rem 0; font-size: 0.87rem; line-height: 1.5;
        background: rgba(128,128,128,0.10);
    }
    .callout b { opacity: 1; }
    .callout-blue   { border-color: #5B8DEF; }
    .callout-green  { border-color: #2ECC71; }
    .callout-red    { border-color: #E74C3C; }
    .callout-orange { border-color: #E8A000; }
    .callout-purple { border-color: #A29BFE; }

    /* ── Section title ── */
    .section-title {
        font-size: 1.05rem; font-weight: 700;
        border-bottom: 2.5px solid #5B8DEF;
        padding-bottom: 5px; margin: 1.4rem 0 0.9rem;
        display: flex; align-items: center; gap: 6px;
    }

    /* ── Reco card ── */
    .reco-card {
        border-radius: 12px; padding: 1.1rem 1.3rem; margin: 0.4rem 0;
        border-left: 4px solid; font-size: 0.88rem; line-height: 1.5;
        background: rgba(128,128,128,0.10);
    }
    .reco-card h4 { margin: 0 0 0.4rem; font-size: 1rem; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] .stMarkdown { font-size: 0.88rem; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] { font-size: 0.9rem; font-weight: 500; }
    .stTabs [aria-selected="true"] { color: #5B8DEF !important; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT & PRÉPARATION DES DONNÉES
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data() -> pd.DataFrame:
    # Cherche le CSV dans plusieurs emplacements possibles
    candidates = [
        "dataset_prof.csv",
        "dataset_pro.csv",
        os.path.join(os.path.dirname(__file__), "dataset_prof.csv"),
        os.path.join(os.path.dirname(__file__), "dataset_pro.csv"),
    ]
    df = None
    for path in candidates:
        if os.path.exists(path):
            df = pd.read_csv(path)
            break

    if df is None:
        return None

    df["source"] = df["source"].astype(str).str.strip().str.lower()

    # Date parsing robuste
    date1 = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    mask  = date1.isna()
    date2 = pd.to_datetime(df.loc[mask, "date"], errors="coerce")
    df["date_parsed"] = date1
    df.loc[mask, "date_parsed"] = date2
    df["year"] = df["date_parsed"].dt.year

    # Catégorie employé
    def emp_cat(x):
        if pd.isna(x): return "Autre"
        t = str(x).lower()
        if "stag" in t or "intern" in t: return "Stagiaire"
        if "ancien" in t or "former" in t or "ex-" in t: return "Ancien employé"
        if "employ" in t or "current" in t or "actuel" in t: return "Employé actuel"
        return "Autre"

    df["emp_cat"] = df["employee_type"].apply(emp_cat)

    # Catégorie ancienneté
    def dur_cat(x):
        if pd.isna(x): return None
        if x < 1:   return "< 1 an"
        if x < 3:   return "1–3 ans"
        if x < 6:   return "3–6 ans"
        return "6 ans +"

    df["duration_cat"] = df["employment_duration"].apply(dur_cat)

    # Nettoyage texte pour wordcloud
    df["pros_clean"] = df["pros"].apply(norm)
    df["cons_clean"] = df["cons"].apply(norm)

    # ── Sentiment léger (bag-of-words) ─────────────────────────────────────────
    def sentiment_score(text: str) -> float:
        if not text or len(text.strip()) < 5:
            return 0.0
        words = set(re.findall(r"\b\w+\b", norm(text)))
        pos = len(words & POSITIVE_WORDS)
        neg = len(words & NEGATIVE_WORDS)
        total = pos + neg
        return (pos - neg) / total if total > 0 else 0.0

    df["sentiment_pros"] = df["pros"].apply(sentiment_score)
    df["sentiment_cons"] = df["cons"].apply(sentiment_score)
    df["sentiment_net"]  = df["sentiment_pros"] + df["sentiment_cons"]

    # Longueur des verbatims (proxy engagement)
    df["len_pros"] = df["pros"].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
    df["len_cons"] = df["cons"].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
    df["len_total"] = df["len_pros"] + df["len_cons"]

    # Avis "récents" (2022+) flag
    df["recent"] = df["year"] >= 2022

    return df


# ── Chargement ─────────────────────────────────────────────────────────────────
df_raw = load_data()

if df_raw is None:
    st.error(
        "❌ Fichier CSV introuvable. "
        "Placez `dataset_prof.csv` (ou `dataset_pro.csv`) dans le même répertoire que `app.py` et relancez."
    )
    st.info("💡 Conseil : assurez-vous que le CSV est dans le même dossier que ce fichier Python.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTRES
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🎛️ Filtres")
    st.markdown("---")

    st.markdown("**Cabinets**")
    firms_selected = []
    for f in FIRM_ORDER:
        checked = st.checkbox(LABELS[f], value=True, key=f"chk_{f}")
        if checked:
            firms_selected.append(f)

    if not firms_selected:
        st.warning("Sélectionnez au moins un cabinet.")
        st.stop()

    st.markdown("---")
    st.markdown("**Période**")
    years_avail = sorted(df_raw["year"].dropna().unique().astype(int))
    year_min, year_max = int(min(years_avail)), int(max(years_avail))
    year_range = st.slider("Années d'avis", year_min, year_max, (year_min, year_max), step=1)

    st.markdown("---")
    st.markdown("**Profil employé**")
    emp_cats_all = ["Stagiaire", "Employé actuel", "Ancien employé", "Autre"]
    emp_selected = st.multiselect(
        "Type d'employé", emp_cats_all,
        default=["Stagiaire", "Employé actuel", "Ancien employé"],
    )
    if not emp_selected:
        emp_selected = emp_cats_all

    st.markdown("---")
    st.markdown("**Niveau hiérarchique**")
    hier_all = ["Junior", "Intermédiaire", "Senior", "Direction", "Unknown"]
    hier_selected = st.multiselect("Grade", hier_all, default=hier_all)
    if not hier_selected:
        hier_selected = hier_all

    st.markdown("---")
    recent_only = st.toggle("🔍 Avis récents uniquement (2022–2024)", value=False)

    st.markdown("---")
    st.markdown(
        "<small>📊 Source : Glassdoor FR<br>"
        "Joana & Mahélène — Master IMCDS 2026</small>",
        unsafe_allow_html=True,
    )


# ── Application des filtres ────────────────────────────────────────────────────
mask_base = (
    df_raw["source"].isin(firms_selected)
    & (df_raw["year"].between(year_range[0], year_range[1], inclusive="both") | df_raw["year"].isna())
    & (df_raw["emp_cat"].isin(emp_selected))
    & (df_raw["grade_hierarchical"].isin(hier_selected))
)
if recent_only:
    mask_base &= df_raw["recent"]

dff = df_raw[mask_base].copy()
firms_present = [f for f in FIRM_ORDER if f in dff["source"].unique()]


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <h1>🏢 Big Four — Dashboard Candidat</h1>
    <p>Quel cabinet choisir pour son premier emploi dans le conseil ? — Analyse de 2 135 avis employés (2008–2024)</p>
    <span class="persona-tag">👤 Persona : Alexandre, 23 ans · M2 école de commerce · 1er emploi dans le conseil</span>
</div>
""", unsafe_allow_html=True)

n_total = len(dff)
st.caption(f"📊 **{n_total} avis** sélectionnés avec les filtres actuels")


# ══════════════════════════════════════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Vue d'ensemble",
    "🎯 Forces & Faiblesses",
    "👤 Analyse par profil",
    "📈 Dynamiques temporelles",
    "🤖 Score Alexandre",
    "💬 Verbatims",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — VUE D'ENSEMBLE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">📌 Indicateurs clés par cabinet</div>', unsafe_allow_html=True)

    # KPI cards
    cols = st.columns(len(firms_present))
    for col, firm in zip(cols, firms_present):
        sub = dff[dff["source"] == firm]
        note   = sub["rating"].mean()
        reco   = (sub["recommander"] == 1).mean() * 100
        n_avis = len(sub)
        sent   = sub["sentiment_net"].mean()
        color  = COLORS[firm]
        sent_icon = "😊" if sent > 0.05 else ("😐" if sent > -0.05 else "😟")
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-color:{color}">
                <p class="kpi-label" style="color:{color};font-weight:700">{LABELS[firm]}</p>
                <p class="kpi-value" style="color:{color}">{note:.2f}<span style="font-size:.9rem;font-weight:400"> /5</span></p>
                <p class="kpi-label">Note moyenne</p>
                <p class="kpi-sub">✅ {reco:.0f}% recommandent</p>
                <p class="kpi-sub">📝 {n_avis} avis &nbsp;·&nbsp; {sent_icon} Sentiment {sent:+.2f}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("")

    col_l, col_r = st.columns(2)

    with col_l:
        mean_ratings = dff.groupby("source")["rating"].mean().reindex(firms_present)
        fig_bar = go.Figure()
        for firm in firms_present:
            fig_bar.add_trace(go.Bar(
                x=[LABELS[firm]], y=[mean_ratings[firm]], name=LABELS[firm],
                marker_color=COLORS[firm],
                text=[f"{mean_ratings[firm]:.2f}"], textposition="outside",
            ))
        fig_bar.update_layout(
            font=dict(color="#1A1A2E"),
            title="Note moyenne par cabinet (/5)",
            yaxis=dict(range=[0, 5.5], title="Note"),
            showlegend=False, height=320,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_r:
        fig_vio = go.Figure()
        for firm in firms_present:
            sub = dff[dff["source"] == firm]["rating"].dropna()
            fig_vio.add_trace(go.Violin(
                x=[LABELS[firm]] * len(sub), y=sub,
                name=LABELS[firm], fillcolor=COLORS[firm],
                line_color=COLORS[firm], opacity=0.75,
                box_visible=True, meanline_visible=True,
            ))
        fig_vio.update_layout(
            title="Distribution des notes (violin)",
            yaxis=dict(range=[0.5, 5.5], title="Note"),
            showlegend=False, height=320,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_vio, use_container_width=True)

    col_l2, col_r2 = st.columns(2)

    with col_l2:
        reco_data = dff.groupby("source")["recommander"].mean().reindex(firms_present)
        fig_reco = go.Figure()
        for firm in firms_present:
            fig_reco.add_trace(go.Bar(
                x=[LABELS[firm]], y=[reco_data[firm]], name=LABELS[firm],
                marker_color=COLORS[firm],
                text=[f"{reco_data[firm]:.3f}"], textposition="outside",
            ))
        fig_reco.update_layout(
            title="Score de recommandation moyen",
            yaxis=dict(title="Score moyen"),
            showlegend=False, height=300,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_reco, use_container_width=True)

    with col_r2:
        # Sentiment net par cabinet (NLP léger)
        sent_data = dff.groupby("source")["sentiment_net"].mean().reindex(firms_present)
        bar_colors_sent = [COLORS[f] for f in firms_present]
        fig_sent = go.Figure()
        for firm in firms_present:
            v = sent_data[firm]
            fig_sent.add_trace(go.Bar(
                x=[LABELS[firm]], y=[v], name=LABELS[firm],
                marker_color=COLORS[firm],
                text=[f"{v:+.3f}"], textposition="outside",
            ))
        fig_sent.add_hline(y=0, line_color="black", line_width=1)
        fig_sent.update_layout(
            title="Score de sentiment net (NLP verbatims)",
            yaxis=dict(title="Score sentiment"),
            showlegend=False, height=300,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_sent, use_container_width=True)

    st.markdown("""
    <div class="callout callout-blue">
    <b>Lecture :</b> Les notes moyennes sont très proches entre cabinets (3,68–3,82/5).
    La discrimination s'opère sur les dimensions spécifiques. Le sentiment NLP sur les verbatims
    apporte une lecture complémentaire, moins susceptible d'être gonflée par les notes extrêmes.
    </div>""", unsafe_allow_html=True)

    # Tableau récapitulatif
    st.markdown('<div class="section-title">📋 Tableau récapitulatif comparatif</div>', unsafe_allow_html=True)
    summary_rows = []
    for firm in firms_present:
        sub = dff[dff["source"] == firm]
        summary_rows.append({
            "Cabinet": LABELS[firm],
            "Note moy. (/5)": round(sub["rating"].mean(), 2),
            "% Recommandent": f"{(sub['recommander']==1).mean()*100:.0f}%",
            "Nb avis": len(sub),
            "Ancienneté moy.": f"~{sub['employment_duration'].mean():.1f} ans" if "employment_duration" in sub.columns else "—",
            "Sentiment net": f"{sub['sentiment_net'].mean():+.3f}",
        })
    st.dataframe(pd.DataFrame(summary_rows).set_index("Cabinet"), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FORCES & FAIBLESSES
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🌡️ Heatmap des scores nets par grand thème</div>', unsafe_allow_html=True)

    GRAND_THEMES = {
        "Contenu & exécution": (
            "theme_pro: Contenu et exécution du travail",
            "theme_con: Contenu et exécution du travail"),
        "Environnement de travail": (
            "theme_pro: Environnement de travail",
            "theme_con: Environnement de travail"),
        "Aménagement du travail": (
            "theme_pro: Aménagement du travail",
            "theme_con: Aménagement du travail"),
        "Aspect financier": (
            "theme_pro: Aspect financier",
            "theme_con: Aspect financier"),
    }

    rows_gt = []
    for firm in firms_present:
        sub = dff[dff["source"] == firm]
        row = {"Cabinet": LABELS[firm]}
        for theme_label, (pc, cc) in GRAND_THEMES.items():
            if pc in sub.columns and cc in sub.columns:
                row[theme_label] = sub[pc].mean() - sub[cc].mean()
            else:
                row[theme_label] = np.nan
        rows_gt.append(row)

    pivot_gt = pd.DataFrame(rows_gt).set_index("Cabinet")

    fig_heat = px.imshow(
        pivot_gt,
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        zmin=-0.6, zmax=0.6,
        text_auto=".2f",
        aspect="auto",
        title="Forces & Faiblesses — Score net (pro − con) par grand thème",
    )
    fig_heat.update_traces(textfont_size=14)
    fig_heat.update_layout(
        height=280,
        coloraxis_colorbar=dict(title="Score net"),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # ── Barplot scores nets sous-thèmes ───────────────────────────────────────
    st.markdown('<div class="section-title">📊 Scores nets détaillés par sous-thème</div>', unsafe_allow_html=True)

    net_rows = []
    for firm in firms_present:
        sub = dff[dff["source"] == firm]
        for theme_label, (pc, cc) in THEMES.items():
            if pc in sub.columns and cc in sub.columns:
                net = sub[pc].mean() - sub[cc].mean()
            else:
                net = np.nan
            net_rows.append({"Cabinet": LABELS[firm], "Thème": theme_label, "Score net": net})

    net_df = pd.DataFrame(net_rows)

    fig_bar_themes = px.bar(
        net_df, x="Score net", y="Thème", color="Cabinet",
        color_discrete_map={LABELS[f]: COLORS[f] for f in firms_present},
        barmode="group", orientation="h",
        title="Score net par sous-thème et par cabinet (positif = force, négatif = faiblesse)",
    )
    fig_bar_themes.add_vline(x=0, line_color="black", line_width=1)
    fig_bar_themes.update_layout(
        height=480, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig_bar_themes, use_container_width=True)

    # ── Radar multi-critères ──────────────────────────────────────────────────
    st.markdown('<div class="section-title">🕸️ Radar multi-critères normalisé</div>', unsafe_allow_html=True)

    radar_rows = {}
    for firm in firms_present:
        sub = dff[dff["source"] == firm]
        radar_rows[firm] = {}
        for theme_label, (pc, cc) in THEMES.items():
            if pc in sub.columns and cc in sub.columns:
                radar_rows[firm][theme_label] = sub[pc].mean() - sub[cc].mean()
            else:
                radar_rows[firm][theme_label] = 0

    radar_df = pd.DataFrame(radar_rows).T
    mn, mx = radar_df.values.min(), radar_df.values.max()
    radar_norm = (radar_df - mn) / (mx - mn) * 100 if mx > mn else radar_df * 0 + 50
    categories = radar_norm.columns.tolist()

    fig_radar = go.Figure()
    for firm in firms_present:
        vals = radar_norm.loc[firm].tolist()
        raw  = radar_df.loc[firm].tolist()
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=categories + [categories[0]],
            fill="toself", fillcolor=COLORS[firm],
            line=dict(color=COLORS[firm], width=2.5),
            opacity=0.22, name=LABELS[firm],
            customdata=[[f"{r:+.3f}"] for r in (raw + [raw[0]])],
            hovertemplate="<b>%{theta}</b><br>Score net: %{customdata[0]}<extra></extra>",
        ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 100], visible=True, tickfont_size=9),
            angularaxis=dict(tickfont_size=11),
        ),
        legend=dict(orientation="h", y=-0.12),
        height=500, paper_bgcolor="rgba(0,0,0,0)",
        title="Profil multi-critères normalisé (0 = pire, 100 = meilleur parmi les 4 cabinets)",
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Drivers de satisfaction ────────────────────────────────────────────────
    st.markdown('<div class="section-title">📉 Drivers de satisfaction — Corrélation avec la note globale</div>', unsafe_allow_html=True)

    subtheme_cols = (
        [c for c in dff.columns if c.startswith("sous_theme_pro:")]
        + [c for c in dff.columns if c.startswith("sous_theme_con:")]
    )

    if subtheme_cols:
        corr_vec = (
            dff[subtheme_cols + ["rating"]]
            .corr(numeric_only=True)["rating"]
            .drop("rating")
            .sort_values()
        )

        def clean_col(col):
            return (col.replace("sous_theme_pro: ", "(+) ")
                       .replace("sous_theme_con: ", "(−) ")
                       .replace("Travail stimulant/ satisfaction dans le travail/ sens du travail / motivation",
                                "Travail stimulant / motivation")
                       .replace("Ambiance et collaboration en équipe / appartenance à l\u2019entreprise",
                                "Ambiance & équipe")
                       .replace("Bienveillance managériale et reconnaissance / qualité de l\u2019encadrement",
                                "Management & reconnaissance")
                       .replace("Equilibre vie privée - vie professionnelle", "Équil. vie pro/perso")
                       .replace("Autonomie et liberté d\u2019action / confiance", "Autonomie & confiance")
                       .replace("Opportunité de développement professionnel", "Développement pro.")
                       .replace("Charge de travail / travail stressant", "Charge de travail")
                       .replace("Outils et infrastructures", "Outils & infra"))

        labels_clean = [clean_col(c) for c in corr_vec.index]
        bar_colors_corr = ["#E74C3C" if v < 0 else "#27AE60" for v in corr_vec.values]

        fig_drivers = go.Figure(go.Bar(
            x=corr_vec.values, y=labels_clean,
            orientation="h", marker_color=bar_colors_corr,
            text=[f"{v:+.3f}" for v in corr_vec.values], textposition="outside",
        ))
        fig_drivers.add_vline(x=0, line_width=1, line_color="black")
        fig_drivers.update_layout(
            title="Impact de chaque sous-thème sur la note (corrélation de Pearson)",
            xaxis=dict(title="Corrélation avec la note globale"),
            height=480, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_drivers, use_container_width=True)

    st.markdown("""
    <div class="callout callout-green">
    <b>Insight clé :</b> L'<b>ambiance d'équipe</b> mentionnée positivement est le 1er levier
    de satisfaction (r ≈ +0.20). Le <b>management perçu négativement</b> est le 1er levier de
    dégradation (r ≈ −0.17), devant la charge de travail et la rémunération.
    </div>
    <div class="callout callout-red" style="margin-top:6px">
    <b>Point universel :</b> La <b>charge de travail</b> est structurellement négative dans
    <b>tous</b> les cabinets — ce n'est pas un critère différenciant, c'est une contrainte à anticiper.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANALYSE PAR PROFIL
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">👤 Satisfaction selon le type d\'employé</div>', unsafe_allow_html=True)

    seg_emp = dff.groupby(["source", "emp_cat"])["rating"].mean().reset_index()
    cats_a  = ["Stagiaire", "Employé actuel", "Ancien employé"]
    cols_a  = ["#3498DB", "#27AE60", "#E74C3C"]

    fig_emp = go.Figure()
    for cat, col in zip(cats_a, cols_a):
        vals, xlbls = [], []
        for f in firms_present:
            sub = seg_emp[(seg_emp["source"] == f) & (seg_emp["emp_cat"] == cat)]
            vals.append(sub["rating"].values[0] if len(sub) else None)
            xlbls.append(LABELS[f])
        fig_emp.add_trace(go.Bar(
            name=cat, x=xlbls, y=vals, marker_color=col, opacity=0.85,
            text=[f"{v:.2f}" if v else "" for v in vals], textposition="outside",
        ))

    fig_emp.update_layout(
        barmode="group", title="Note moyenne par profil employé et par cabinet",
        yaxis=dict(range=[0, 5.8], title="Note (/5)"),
        legend=dict(orientation="h", y=-0.2),
        height=380, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_emp, use_container_width=True)

    st.markdown("""
    <div class="callout callout-orange">
    <b>Attention biais :</b> Les stagiaires affichent systématiquement +0,4 à +0,6 point vs les
    employés actuels. Privilégiez les avis <i>"Employé actuel"</i> pour une image réaliste de
    l'intégration. EY affiche le score junior le plus bas (&lt; 3/5) — signal à surveiller.
    </div>""", unsafe_allow_html=True)

    # ── Grade hiérarchique ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🏅 Satisfaction par niveau hiérarchique</div>', unsafe_allow_html=True)

    grades_b = ["Junior", "Senior", "Direction"]
    cols_b   = ["#3498DB", "#E67E22", "#8E44AD"]
    seg_grade = (
        dff[dff["grade_hierarchical"].isin(grades_b)]
        .groupby(["source", "grade_hierarchical"])["rating"]
        .mean().reset_index()
    )

    fig_grade = go.Figure()
    for grd, col in zip(grades_b, cols_b):
        vals, xlbls = [], []
        for f in firms_present:
            sub = seg_grade[(seg_grade["source"] == f) & (seg_grade["grade_hierarchical"] == grd)]
            vals.append(sub["rating"].values[0] if len(sub) else None)
            xlbls.append(LABELS[f])
        fig_grade.add_trace(go.Bar(
            name=grd, x=xlbls, y=vals, marker_color=col, opacity=0.85,
            text=[f"{v:.2f}" if v else "" for v in vals], textposition="outside",
        ))

    fig_grade.update_layout(
        barmode="group", title="Note moyenne par grade hiérarchique",
        yaxis=dict(range=[0, 5.8], title="Note (/5)"),
        legend=dict(orientation="h", y=-0.2),
        height=360, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_grade, use_container_width=True)

    # ── Ancienneté ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">⏱️ Évolution de la satisfaction selon l\'ancienneté</div>', unsafe_allow_html=True)

    DUR_ORDER = ["< 1 an", "1–3 ans", "3–6 ans", "6 ans +"]
    seg_dur = (
        dff[dff["duration_cat"].notna()]
        .groupby(["source", "duration_cat"])["rating"]
        .mean().reset_index()
    )

    fig_dur = go.Figure()
    for firm in firms_present:
        sub = seg_dur[seg_dur["source"] == firm]
        sub = sub.set_index("duration_cat").reindex(DUR_ORDER).reset_index()
        fig_dur.add_trace(go.Scatter(
            x=sub["duration_cat"], y=sub["rating"],
            mode="lines+markers+text",
            name=LABELS[firm],
            line=dict(color=COLORS[firm], width=2.5),
            marker=dict(size=8),
            text=[f"{v:.2f}" if not pd.isna(v) else "" for v in sub["rating"]],
            textposition="top center",
        ))

    fig_dur.update_layout(
        title="Note moyenne selon l'ancienneté (tranche)",
        xaxis=dict(title="Ancienneté", categoryorder="array", categoryarray=DUR_ORDER),
        yaxis=dict(range=[0, 5.5], title="Note (/5)"),
        legend=dict(orientation="h", y=-0.2),
        height=360, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_dur, use_container_width=True)

    st.markdown("""
    <div class="callout callout-red">
    <b>Point de rupture 1–3 ans :</b> La satisfaction chute dans tous les cabinets après la 1re année,
    correspondant à la montée en responsabilités. C'est la période critique de rétention.
    Les Big Four <b>attirent</b> les talents mais peinent à les <b>fidéliser</b>.
    </div>""", unsafe_allow_html=True)

    # ── Sentiment net par profil ───────────────────────────────────────────────
    st.markdown('<div class="section-title">😊 Sentiment NLP des verbatims par profil</div>', unsafe_allow_html=True)

    seg_sent = dff.groupby(["source", "emp_cat"])["sentiment_net"].mean().reset_index()

    fig_sent2 = go.Figure()
    for cat, col in zip(cats_a, cols_a):
        vals, xlbls = [], []
        for f in firms_present:
            sub = seg_sent[(seg_sent["source"] == f) & (seg_sent["emp_cat"] == cat)]
            vals.append(sub["sentiment_net"].values[0] if len(sub) else None)
            xlbls.append(LABELS[f])
        fig_sent2.add_trace(go.Bar(
            name=cat, x=xlbls, y=vals, marker_color=col, opacity=0.85,
            text=[f"{v:+.2f}" if v is not None else "" for v in vals],
            textposition="outside",
        ))

    fig_sent2.add_hline(y=0, line_color="black", line_width=1)
    fig_sent2.update_layout(
        barmode="group", title="Sentiment net des verbatims par type d'employé (NLP bag-of-words)",
        yaxis=dict(title="Score sentiment"),
        legend=dict(orientation="h", y=-0.2),
        height=360, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_sent2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DYNAMIQUES TEMPORELLES
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    df_trend = dff[dff["year"].notna()].copy()
    df_trend["year"] = df_trend["year"].astype(int)

    if df_trend.empty:
        st.warning("Aucune donnée temporelle disponible avec les filtres actuels.")
    else:
        min_y = int(df_trend["year"].min())
        max_y = int(df_trend["year"].max())

        st.markdown('<div class="section-title">📅 Évolution de la note moyenne par année</div>', unsafe_allow_html=True)

        trend_note = df_trend.groupby(["year", "source"])["rating"].mean().reset_index()

        fig_trend_note = go.Figure()
        if 2020 in df_trend["year"].values:
            fig_trend_note.add_vrect(
                x0=2020, x1=2021, fillcolor="rgba(231,76,60,0.08)",
                layer="below", line_width=0,
                annotation_text="Covid", annotation_position="top left",
            )

        for firm in firms_present:
            sub = trend_note[trend_note["source"] == firm].sort_values("year")
            if len(sub) == 0: continue
            fig_trend_note.add_trace(go.Scatter(
                x=sub["year"], y=sub["rating"],
                mode="lines+markers", name=LABELS[firm],
                line=dict(color=COLORS[firm], width=2.5),
                marker=dict(size=7),
            ))

        fig_trend_note.update_layout(
            title=f"Note moyenne par année ({min_y}–{max_y})",
            xaxis=dict(title="Année", tickmode="linear", dtick=1),
            yaxis=dict(range=[1.5, 5.5], title="Note (/5)"),
            legend=dict(orientation="h", y=-0.2),
            height=380, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_trend_note, use_container_width=True)

        # ── Taux de recommandation ─────────────────────────────────────────────
        st.markdown('<div class="section-title">📉 Évolution du taux de recommandation (%)</div>', unsafe_allow_html=True)

        trend_reco = (
            df_trend.groupby(["year", "source"])
            .apply(lambda x: (x["recommander"] == 1).mean() * 100)
            .reset_index(name="pct_reco")
        )

        fig_trend_reco = go.Figure()
        if 2020 in df_trend["year"].values:
            fig_trend_reco.add_vrect(
                x0=2020, x1=2021, fillcolor="rgba(231,76,60,0.08)",
                layer="below", line_width=0,
            )
        fig_trend_reco.add_hline(y=50, line_dash="dot", line_color="grey",
                                  annotation_text="Seuil 50%", annotation_position="right")

        for firm in firms_present:
            sub = trend_reco[trend_reco["source"] == firm].sort_values("year")
            if len(sub) == 0: continue
            fig_trend_reco.add_trace(go.Scatter(
                x=sub["year"], y=sub["pct_reco"],
                mode="lines+markers", name=LABELS[firm],
                line=dict(color=COLORS[firm], width=2.5, dash="dash"),
                marker=dict(size=7, symbol="square"),
            ))

        fig_trend_reco.update_layout(
            title=f"Taux de recommandation par année ({min_y}–{max_y})",
            xaxis=dict(title="Année", tickmode="linear", dtick=1),
            yaxis=dict(range=[0, 100], title="% recommandent"),
            legend=dict(orientation="h", y=-0.2),
            height=380, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_trend_reco, use_container_width=True)

        st.markdown("""
        <div class="callout callout-red">
        <b>Tendance structurelle :</b> Le taux de recommandation est passé de ~75 % (2019)
        à ~30 % (2023–2024) dans tous les cabinets. Le Covid a été un choc ponctuel ;
        la baisse post-2021 est <b>structurelle</b>. Priorisez les avis récents (2022–2024)
        pour refléter le contexte actuel.
        </div>""", unsafe_allow_html=True)

        # ── Sentiment NLP dans le temps ────────────────────────────────────────
        st.markdown('<div class="section-title">🤖 Évolution du sentiment NLP par année</div>', unsafe_allow_html=True)

        trend_sent = df_trend.groupby(["year", "source"])["sentiment_net"].mean().reset_index()
        fig_sent_t = go.Figure()
        fig_sent_t.add_hline(y=0, line_color="black", line_width=1)
        for firm in firms_present:
            sub = trend_sent[trend_sent["source"] == firm].sort_values("year")
            if len(sub) == 0: continue
            fig_sent_t.add_trace(go.Scatter(
                x=sub["year"], y=sub["sentiment_net"],
                mode="lines+markers", name=LABELS[firm],
                line=dict(color=COLORS[firm], width=2.5, dash="dot"),
                marker=dict(size=7),
            ))

        fig_sent_t.update_layout(
            title="Sentiment net des verbatims par année (NLP)",
            xaxis=dict(title="Année", tickmode="linear", dtick=1),
            yaxis=dict(title="Sentiment net"),
            legend=dict(orientation="h", y=-0.2),
            height=360, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_sent_t, use_container_width=True)

        # ── Volume d'avis ──────────────────────────────────────────────────────
        st.markdown('<div class="section-title">📦 Volume d\'avis par année</div>', unsafe_allow_html=True)

        trend_count = df_trend.groupby(["year", "source"]).size().reset_index(name="count")
        fig_vol = go.Figure()
        for firm in firms_present:
            sub = trend_count[trend_count["source"] == firm].sort_values("year")
            fig_vol.add_trace(go.Bar(
                x=sub["year"], y=sub["count"],
                name=LABELS[firm], marker_color=COLORS[firm], opacity=0.85,
            ))
        fig_vol.update_layout(
            barmode="stack", title="Nombre d'avis déposés par année",
            xaxis=dict(title="Année", tickmode="linear", dtick=1),
            yaxis=dict(title="Nombre d'avis"),
            legend=dict(orientation="h", y=-0.2),
            height=320, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_vol, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SCORE ALEXANDRE (NOUVEAU)
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div class="callout callout-purple">
    <b>🎯 Score personnalisé Alexandre :</b> Définissez vos propres priorités (poids 1–5) pour chaque
    critère. Le dashboard calcule un <b>score composite pondéré</b> pour chaque cabinet, directement
    basé sur les données réelles des avis employés.
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚖️ Définir ses priorités</div>', unsafe_allow_html=True)
    st.markdown("*Ajustez l'importance de chaque critère selon votre profil (1 = peu important, 5 = essentiel)*")

    weights = {}
    col1, col2, col3 = st.columns(3)
    theme_list = list(THEMES.keys())
    for i, theme in enumerate(theme_list):
        col = [col1, col2, col3][i % 3]
        with col:
            default_w = ALEXANDRE_DEFAULT.get(theme, 3)
            weights[theme] = st.slider(theme, 1, 5, default_w, key=f"w_{theme}")

    st.markdown("---")

    # Calcul du score composite
    st.markdown('<div class="section-title">🏆 Score composite par cabinet</div>', unsafe_allow_html=True)

    score_rows = []
    for firm in firms_present:
        sub = dff[dff["source"] == firm]
        total_weight = sum(weights.values())
        composite = 0
        detail = {}
        for theme, (pc, cc) in THEMES.items():
            if pc in sub.columns and cc in sub.columns:
                net = sub[pc].mean() - sub[cc].mean()
            else:
                net = 0
            w = weights[theme]
            composite += net * w
            detail[theme] = net
        composite /= total_weight if total_weight > 0 else 1
        score_rows.append({"firm": firm, "score": composite, **detail})

    score_df = pd.DataFrame(score_rows).set_index("firm")
    score_df_sorted = score_df.sort_values("score", ascending=False)

    # Podium visuel
    podium_cols = st.columns(len(firms_present))
    rank_emojis = ["🥇", "🥈", "🥉", "4️⃣"]
    for i, (firm, row) in enumerate(score_df_sorted.iterrows()):
        with podium_cols[i]:
            color = COLORS[firm]
            rank_e = rank_emojis[i] if i < len(rank_emojis) else ""
            st.markdown(f"""
            <div class="kpi-card" style="border-color:{color}; text-align:center;">
                <p style="font-size:1.8rem;margin:0">{rank_e}</p>
                <p class="kpi-label" style="color:{color};font-weight:700;font-size:1rem">{LABELS[firm]}</p>
                <p class="kpi-value" style="color:{color}">{row['score']:+.4f}</p>
                <p class="kpi-label">Score composite pondéré</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("")

    # Graphique scores composites
    firms_sorted = score_df_sorted.index.tolist()
    scores_sorted = score_df_sorted["score"].tolist()
    bar_colors_score = [COLORS[f] for f in firms_sorted]

    fig_score = go.Figure(go.Bar(
        x=[LABELS[f] for f in firms_sorted],
        y=scores_sorted,
        marker_color=bar_colors_score,
        text=[f"{s:+.4f}" for s in scores_sorted],
        textposition="outside",
    ))
    fig_score.add_hline(y=0, line_color="black", line_width=1)
    fig_score.update_layout(
        title="Score composite pondéré selon vos priorités",
        yaxis=dict(title="Score composite"),
        height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    st.plotly_chart(fig_score, use_container_width=True)

    # Détail par thème pour chaque cabinet
    st.markdown('<div class="section-title">🔍 Contribution de chaque critère au score</div>', unsafe_allow_html=True)

    contrib_rows = []
    for firm in firms_present:
        sub = dff[dff["source"] == firm]
        for theme, (pc, cc) in THEMES.items():
            if pc in sub.columns and cc in sub.columns:
                net = sub[pc].mean() - sub[cc].mean()
            else:
                net = 0
            contrib = net * weights[theme]
            contrib_rows.append({"Cabinet": LABELS[firm], "Thème": theme, "Score net": net,
                                  "Poids": weights[theme], "Contribution": contrib})

    contrib_df = pd.DataFrame(contrib_rows)

    fig_contrib = px.bar(
        contrib_df, x="Contribution", y="Thème", color="Cabinet",
        color_discrete_map={LABELS[f]: COLORS[f] for f in firms_present},
        barmode="group", orientation="h",
        title="Contribution pondérée de chaque critère (Score net × Poids)",
    )
    fig_contrib.add_vline(x=0, line_color="black", line_width=1)
    fig_contrib.update_layout(
        height=460, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig_contrib, use_container_width=True)

    # Matrice décisionnelle synthétique
    st.markdown('<div class="section-title">📋 Matrice décisionnelle — Recommandations par priorité</div>', unsafe_allow_html=True)

    RECO_MAP = {
        "Apprentissage & Évolution": ("EY", "#E8A000", "Score 'travail stimulant' +0.474 (1er) · Développement pro. +0.397 (1er)"),
        "Rémunération & Finances":   ("KPMG", "#00338D", "Seul score financier positif (+0.027) · Contre −0.087 à −0.115 ailleurs"),
        "Ambiance & Équipe":         ("KPMG / PwC", "#6C5CE7", "KPMG ambiance +0.473 · PwC équipe +0.474 (ex aequo)"),
        "Satisfaction globale":      ("Deloitte", "#86BC25", "Note 3.82/5 (1er) · Environnement de travail fort"),
        "Meilleur compromis":        ("KPMG", "#00338D", "Recommandation 0.351 (ex aequo 1er) · Financier positif · Ambiance forte · 1 332 avis"),
    }

    for priorite, (cabinet, color, justif) in RECO_MAP.items():
        st.markdown(f"""
        <div class="reco-card" style="background: #FAFBFF; border-color: {color}; border-left: 4px solid {color};">
            <h4 style="color:{color}">{'🎯 ' if priorite == 'Meilleur compromis' else ''}{priorite} → <b>{cabinet}</b></h4>
            <p style="margin:0; color:#555; font-size:0.85rem">{justif}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="callout callout-blue" style="margin-top:1rem">
    <b>Conclusion pour Alexandre :</b> Compte tenu de ses priorités (développement rapide, progression
    structurée, équilibre vie pro/perso acceptable), <b>EY</b> se positionne comme 1er choix si
    l'objectif est la montée en compétences et l'exit vers l'industrie. <b>KPMG</b> offre le meilleur
    compromis global (données robustes, rémunération, ambiance). Dans tous les cas, le vrai
    différenciateur sera l'équipe et le manager directs — bien plus que le cabinet lui-même.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — VERBATIMS & NUAGES DE MOTS
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-title">☁️ Nuages de mots — Avantages & Inconvénients par cabinet</div>', unsafe_allow_html=True)

    firm_wc = st.selectbox(
        "Choisir un cabinet",
        [LABELS[f] for f in firms_present],
        key="wc_firm",
    )
    firm_key_wc = {v: k for k, v in LABELS.items()}[firm_wc]
    sub_wc = dff[dff["source"] == firm_key_wc]

    def make_wordcloud(texts, color):
        text = " ".join(
            t for t in texts.dropna()
            if str(t).strip().lower() not in {"none","nan","aucun","rien","ras",""}
        )
        if len(text.strip()) < 50:
            return None
        wc = WordCloud(
            width=700, height=320,
            background_color="white",
            stopwords=STOPWORDS_FR,
            color_func=lambda *a, **k: color,
            max_words=100,
            collocations=False,
            prefer_horizontal=0.9,
        ).generate(text)
        return wc

    col_pro, col_con = st.columns(2)

    with col_pro:
        st.markdown(f"**✅ Avantages — {firm_wc}**")
        wc_pro = make_wordcloud(sub_wc["pros_clean"], COLORS[firm_key_wc])
        if wc_pro:
            fig_wcp, ax_wcp = plt.subplots(figsize=(7, 3.2))
            ax_wcp.imshow(wc_pro, interpolation="bilinear")
            ax_wcp.axis("off")
            plt.tight_layout(pad=0)
            st.pyplot(fig_wcp, use_container_width=True)
            plt.close()
        else:
            st.info("Données insuffisantes pour ce cabinet / ces filtres.")

    with col_con:
        st.markdown(f"**⚠️ Inconvénients — {firm_wc}**")
        wc_con = make_wordcloud(sub_wc["cons_clean"], "#E74C3C")
        if wc_con:
            fig_wcc, ax_wcc = plt.subplots(figsize=(7, 3.2))
            ax_wcc.imshow(wc_con, interpolation="bilinear")
            ax_wcc.axis("off")
            plt.tight_layout(pad=0)
            st.pyplot(fig_wcc, use_container_width=True)
            plt.close()
        else:
            st.info("Données insuffisantes pour ce cabinet / ces filtres.")

    # ── Top mots fréquents ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 Top 15 mots les plus fréquents</div>', unsafe_allow_html=True)

    def top_words(texts, n=15):
        text = " ".join(str(t) for t in texts.dropna())
        words = re.findall(r"\b[a-zA-Zéèêëàâùûüïîôçæœ]{3,}\b", norm(text))
        words = [w for w in words if w not in STOPWORDS_FR]
        freq = pd.Series(words).value_counts().head(n)
        return freq

    col_tw1, col_tw2 = st.columns(2)

    with col_tw1:
        freq_pros = top_words(sub_wc["pros_clean"])
        if len(freq_pros):
            fig_tw1 = go.Figure(go.Bar(
                x=freq_pros.values, y=freq_pros.index,
                orientation="h", marker_color=COLORS[firm_key_wc],
            ))
            fig_tw1.update_layout(
                title="Top mots — Avantages",
                height=380, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_tw1, use_container_width=True)

    with col_tw2:
        freq_cons = top_words(sub_wc["cons_clean"])
        if len(freq_cons):
            fig_tw2 = go.Figure(go.Bar(
                x=freq_cons.values, y=freq_cons.index,
                orientation="h", marker_color="#E74C3C",
            ))
            fig_tw2.update_layout(
                title="Top mots — Inconvénients",
                height=380, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_tw2, use_container_width=True)

    st.markdown("---")

    # ── Extraits d'avis ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">💬 Extraits d\'avis (échantillon)</div>', unsafe_allow_html=True)

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        n_sample = st.slider("Nombre d'avis à afficher", 3, 20, 6, key="n_sample")
    with col_filter2:
        sort_mode = st.selectbox("Trier par", ["Aléatoire", "Note décroissante", "Note croissante", "Sentiment décroissant"])

    sample_pool = sub_wc[["rating", "grade_hierarchical", "employee_type", "pros", "cons", "sentiment_net", "year"]].dropna(subset=["pros", "cons"])

    if sort_mode == "Note décroissante":
        sample = sample_pool.sort_values("rating", ascending=False).head(n_sample)
    elif sort_mode == "Note croissante":
        sample = sample_pool.sort_values("rating", ascending=True).head(n_sample)
    elif sort_mode == "Sentiment décroissant":
        sample = sample_pool.sort_values("sentiment_net", ascending=False).head(n_sample)
    else:
        sample = sample_pool.sample(min(n_sample, len(sample_pool)), random_state=None)

    for _, row in sample.iterrows():
        rating_stars = "⭐" * int(row["rating"]) if not pd.isna(row["rating"]) else "—"
        grade_str    = str(row.get("grade_hierarchical", "—"))
        year_str     = str(int(row["year"])) if not pd.isna(row.get("year", float("nan"))) else "—"
        sent_val     = row.get("sentiment_net", 0)
        sent_icon    = "😊" if sent_val > 0.1 else ("😟" if sent_val < -0.1 else "😐")
        with st.expander(f"{rating_stars}  ·  {grade_str}  ·  {year_str}  ·  Sentiment {sent_icon} {sent_val:+.2f}"):
            c1, c2 = st.columns(2)
            c1.markdown(f"**✅ Avantages**\n\n{row['pros']}")
            c2.markdown(f"**⚠️ Inconvénients**\n\n{row['cons']}")


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    "<small>📊 Data Challenge — Master IMCDS — Paris 1 Panthéon-Sorbonne | "
    "Joana & Mahélène | Source : Glassdoor FR, 2 135 avis (2008–2024) | "
    "Analyse : EDA + NLP bag-of-words + score composite pondéré</small>",
    unsafe_allow_html=True,
)