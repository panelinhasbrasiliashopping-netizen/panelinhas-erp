import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from utils.data import (autenticar, listar_itens, listar_fornecedores,
                        listar_composicao, composicao_produto, is_composto,
                        registrar_saida_composta, registrar_movimento_batch,
                        registrar_saida_em_lote,
                        listar_estoque, listar_movimentos, registrar_movimento,
                        saldo_item, status_item)
from utils.logo import LOGO_B64

st.set_page_config(page_title="Panelinhas do Brasil", page_icon="🍳", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* ═══════════════════════════════════════════════════════
   PANELINHAS DO BRASIL — DESIGN SYSTEM v2.0 (Premium)
   Cor Primária: #E85D0C  |  Font: Outfit
   ═══════════════════════════════════════════════════════ */

/* ── Reset & Base ──────────────────────────────────────── */
#MainMenu, footer, header,
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stToolbar"] { display:none !important; }

html, body, [class*="css"], .stMarkdown, .stText,
select, input, textarea, button, label, p, span, div, h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}

/* ── Botões do Menu Lateral ────────────────────────────── */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:first-child .stButton > button {
    background: rgba(255,255,255,0.03) !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 10px 10px 0 !important;
    color: #9a9a9a !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 10px 16px !important;
    width: 100% !important;
    margin-bottom: 3px !important;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
    letter-spacing: 0.2px !important;
}
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:first-child .stButton > button:hover {
    background: rgba(232, 93, 12, 0.08) !important;
    color: #fff !important;
    border-left: 3px solid #E85D0C !important;
    transform: translateX(3px) !important;
}
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:first-child .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(232,93,12,0.15) 0%, rgba(232,93,12,0.06) 100%) !important;
    color: #FF8A3D !important;
    border-left: 3px solid #E85D0C !important;
    font-weight: 700 !important;
    box-shadow: inset 0 0 20px rgba(232, 93, 12, 0.04) !important;
}

/* ── Botões de Ação (Confirmar) ────────────────────────── */
.main .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF7B25 0%, #E85D0C 50%, #D14E00 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    padding: 12px 0 !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 15px rgba(232, 93, 12, 0.25) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.main .stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(232, 93, 12, 0.35) !important;
    background: linear-gradient(135deg, #FF8A3D 0%, #E85D0C 50%, #C94500 100%) !important;
}
.main .stButton > button[kind="primary"]:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 8px rgba(232, 93, 12, 0.2) !important;
}

/* ── Cards de Métricas ─────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #FFFCFA 0%, #FFF6F0 100%);
    border: 1.5px solid #FFE0CC;
    border-radius: 14px;
    padding: 16px 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(232, 93, 12, 0.1);
    border-color: #E85D0C;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: #E85D0C;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-family: 'Outfit', sans-serif;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #888;
}

/* ── Alertas Premium ───────────────────────────────────── */
.ar {
    background: linear-gradient(135deg, #FFF0F0 0%, #FFE8E8 100%);
    border-left: 4px solid #EF4444;
    border-radius: 0 12px 12px 0;
    padding: 12px 18px;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #7F1D1D;
    transition: all 0.2s ease;
}
.ar:hover { background: linear-gradient(135deg, #FFE8E8 0%, #FFDCDC 100%); }
.aa {
    background: linear-gradient(135deg, #FFFEF0 0%, #FFF8E1 100%);
    border-left: 4px solid #F59E0B;
    border-radius: 0 12px 12px 0;
    padding: 12px 18px;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #78350F;
    transition: all 0.2s ease;
}
.aa:hover { background: linear-gradient(135deg, #FFF8E1 0%, #FFF3CC 100%); }
.ag {
    background: linear-gradient(135deg, #F0FFF0 0%, #E8F5E9 100%);
    border-left: 4px solid #22C55E;
    border-radius: 0 12px 12px 0;
    padding: 12px 18px;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #14532D;
    transition: all 0.2s ease;
}
.ag:hover { background: linear-gradient(135deg, #E8F5E9 0%, #DCFCE7 100%); }

/* ── Cards de Movimentos ───────────────────────────────── */
.mv {
    background: linear-gradient(135deg, #FFFFFF 0%, #FEFEFE 100%);
    border: 1px solid #F0F0F0;
    border-radius: 10px;
    padding: 11px 16px;
    margin-bottom: 6px;
    font-size: 13px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s ease;
}
.mv:hover {
    border-color: #FFD8C4;
    box-shadow: 0 4px 12px rgba(232, 93, 12, 0.06);
    transform: translateX(3px);
}

/* ── Header de Página ──────────────────────────────────── */
.ph {
    display: flex;
    align-items: center;
    gap: 14px;
    border-left: 5px solid #E85D0C;
    padding-left: 18px;
    margin-bottom: 24px;
    padding-top: 4px;
    padding-bottom: 4px;
    background: linear-gradient(90deg, rgba(232,93,12,0.04) 0%, transparent 60%);
    border-radius: 0 12px 12px 0;
}
.ph h2 {
    margin: 0;
    font-family: 'Outfit', sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: #1a1a1a;
    letter-spacing: -0.3px;
}
.ph p {
    margin: 0;
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    color: #888;
    font-weight: 400;
}

/* ── Campos de Formulário ──────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div {
    font-family: 'Outfit', sans-serif !important;
    border-radius: 10px !important;
    border: 1.5px solid #E8E8E8 !important;
    transition: all 0.25s ease !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #E85D0C !important;
    box-shadow: 0 0 0 3px rgba(232, 93, 12, 0.12) !important;
}

/* ── Tabs ──────────────────────────────────────────────── */
.stTabs [data-baseweb="tab"] {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: 0.3px !important;
}
.stTabs [aria-selected="true"] {
    color: #E85D0C !important;
    border-bottom-color: #E85D0C !important;
}

/* ── Dividers ──────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid #F0EDED !important;
    margin: 18px 0 !important;
}

/* ── DataFrames ────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Scrollbar Premium ─────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(232, 93, 12, 0.2);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(232, 93, 12, 0.4); }

/* ── Coluna do Menu Lateral (fundo escuro em toda a coluna) ── */
[data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child {
    background: linear-gradient(180deg, #151515 0%, #1A1A1A 60%, #1E1E1E 100%) !important;
    border-right: 2px solid rgba(232, 93, 12, 0.3) !important;
    padding: 12px 8px 16px !important;
    min-height: 92vh !important;
    border-radius: 0 !important;
}
/* Garante que botões dentro da coluna do menu herdem o estilo escuro */
[data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child .stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.03) !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 10px 10px 0 !important;
    color: #9a9a9a !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 10px 16px !important;
    width: 100% !important;
    margin-bottom: 3px !important;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child .stButton > button[kind="secondary"]:hover {
    background: rgba(232, 93, 12, 0.1) !important;
    color: #fff !important;
    border-left: 3px solid #E85D0C !important;
    transform: translateX(3px) !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(232,93,12,0.18) 0%, rgba(232,93,12,0.08) 100%) !important;
    color: #FF8A3D !important;
    border: none !important;
    border-left: 3px solid #E85D0C !important;
    border-radius: 0 10px 10px 0 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    text-align: left !important;
    padding: 10px 16px !important;
    width: 100% !important;
    margin-bottom: 3px !important;
    box-shadow: none !important;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
    transform: none !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child .stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(232,93,12,0.25) 0%, rgba(232,93,12,0.12) 100%) !important;
    transform: translateX(3px) !important;
    box-shadow: none !important;
}

</style>
""", unsafe_allow_html=True)

if "usuario" not in st.session_state: st.session_state.usuario = None
if "menu"    not in st.session_state: st.session_state.menu    = "entrada"
if "_dados_pre_carregados" not in st.session_state: st.session_state._dados_pre_carregados = False

# ── LOGIN ───────────────────────────────────────────────
def tela_login():
    # ── CSS exclusivo da tela de login ────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
    /* ── RESET STREAMLIT ──────────────────────────────────────────────────── */
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"] { background: #141210 !important; }
    .block-container                   { padding: 0 !important; max-width: 100vw !important; }
    [data-testid="stHorizontalBlock"]  { gap: 0 !important; align-items: stretch !important; }

    /* ── COLUNAS: altura mínima e sem gap ────────────────────────────────── */
    [data-testid="stColumn"] {
        min-height: 100vh !important;
        box-sizing: border-box;
    }

    /* ── COLUNA DIREITA — padding para centralizar formulário ────────────── */
    [data-testid="stColumn"]:has(.form-box-wrap) {
        padding-top: max(3rem, calc(50vh - 260px)) !important;
        padding-left: 4rem !important;
        padding-right: 4rem !important;
    }

    /* ── BRAND PANEL: ESTRUTURA INTERNA ──────────────────────────────────── */
    .brand-wrap {
        position: relative;
        min-height: 100vh;
        padding: 4rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
        box-sizing: border-box;
        background-color: #1E1A17;
        background-image:
            linear-gradient(rgba(232,93,4,.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(232,93,4,.07) 1px, transparent 1px);
        background-size: 48px 48px;
        border-right: 1px solid rgba(232,93,4,.22);
    }
    .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(80px);
        pointer-events: none;
    }
    .orb-1 {
        width: 320px; height: 320px;
        background: rgba(232,93,4,.22);
        top: -80px; left: -80px;
        animation: lgi-drift 8s ease-in-out infinite;
    }
    .orb-2 {
        width: 220px; height: 220px;
        background: rgba(196,75,0,.15);
        bottom: 60px; right: 60px;
        animation: lgi-drift 11s ease-in-out infinite reverse;
    }
    .bg-letter {
        position: absolute;
        right: -60px; bottom: -30px;
        font-family: 'Bebas Neue', 'Outfit', sans-serif;
        font-size: 460px;
        line-height: 1;
        color: rgba(232,93,4,.04);
        pointer-events: none;
        user-select: none;
        letter-spacing: -10px;
    }
    .brand-content { position: relative; z-index: 1; }

    .eyebrow {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
        font-size: 11px; font-weight: 500;
        letter-spacing: .22em; text-transform: uppercase;
        color: #E85D04; margin: 0 0 2rem 0;
        opacity: 0; transform: translateY(12px);
        animation: lgi-fadeUp .6s .1s forwards;
    }
    .logo-lockup {
        margin-bottom: 2.5rem;
        opacity: 0; transform: translateY(16px);
        animation: lgi-fadeUp .7s .22s forwards;
    }
    .logo-name {
        font-family: 'Bebas Neue', 'Outfit', sans-serif;
        font-size: 96px; line-height: .9;
        letter-spacing: 1px; color: #FFF8F0; margin: 0;
    }
    .logo-name span {
        color: #E85D04; display: block;
        font-size: 60px; letter-spacing: 6px;
    }
    .tagline {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
        font-size: 14px; font-weight: 300;
        color: #8A7B72; letter-spacing: .04em;
        line-height: 1.7; max-width: 340px; margin: 0;
        opacity: 0; transform: translateY(12px);
        animation: lgi-fadeUp .7s .36s forwards;
    }
    .stats-row {
        display: flex; gap: 2.5rem; margin-top: 4rem;
        opacity: 0; transform: translateY(12px);
        animation: lgi-fadeUp .7s .5s forwards;
    }
    .stat-item { border-left: 2px solid #E85D04; padding-left: 1rem; }
    .stat-value {
        font-family: 'Bebas Neue', 'Outfit', sans-serif;
        font-size: 32px; color: #FFF8F0; line-height: 1; margin: 0;
    }
    .stat-label {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
        font-size: 11px; color: #8A7B72;
        letter-spacing: .1em; text-transform: uppercase; margin-top: 2px;
    }

    /* ── FORM PANEL: ESTRUTURA INTERNA ───────────────────────────────────── */
    .form-box-wrap {
        opacity: 0; transform: translateX(20px);
        animation: lgi-fadeIn .7s .4s forwards;
        margin-bottom: .4rem;
    }
    .form-title {
        font-family: 'Bebas Neue', 'Outfit', sans-serif !important;
        font-size: 56px !important; letter-spacing: 1px !important;
        color: #FFF8F0 !important; line-height: 1.05 !important; margin: 0 0 6px 0 !important;
    }
    .form-subtitle {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif !important;
        font-size: 14px !important; color: #8A7B72 !important;
        font-weight: 300 !important; margin: 0 0 1.8rem 0 !important;
    }
    .field-label {
        display: flex; align-items: center; gap: 7px;
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
        font-size: 11px; font-weight: 600;
        letter-spacing: .13em; text-transform: uppercase;
        color: #8A7B72; margin-bottom: 5px; margin-top: 1rem;
    }
    .field-label svg { flex-shrink: 0; }

    /* ── INPUTS NATIVOS (login) ───────────────────────────────────────────── */
    [data-testid="stTextInput"] label { display: none !important; }
    [data-testid="stTextInput"] input {
        background: #1E1A17 !important;
        border: 1px solid rgba(232,93,4,.18) !important;
        border-radius: 10px !important;
        color: #FFF8F0 !important;
        height: 50px !important;
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif !important;
        font-size: 14px !important;
        transition: border-color .25s, box-shadow .25s, background .25s !important;
    }
    [data-testid="stTextInput"] input::placeholder { color: rgba(138,123,114,.4) !important; }
    [data-testid="stTextInput"] input:focus {
        border-color: #E85D04 !important;
        box-shadow: 0 0 0 3px rgba(232,93,4,.12) !important;
        background: #2A2420 !important;
    }

    /* ── BOTÃO SUBMIT ─────────────────────────────────────────────────────── */
    [data-testid="stButton"] > button {
        background: #E85D04 !important;
        border: none !important;
        border-radius: 10px !important;
        color: #fff !important;
        height: 52px !important;
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        letter-spacing: .04em !important;
        position: relative !important;
        overflow: hidden !important;
        transition: background .2s, transform .15s, box-shadow .2s !important;
    }
    [data-testid="stButton"] > button::before {
        content: '' !important;
        position: absolute !important; inset: 0 !important;
        background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,.12) 50%, transparent 70%) !important;
        transform: translateX(-100%) !important;
        transition: transform .5s !important;
    }
    [data-testid="stButton"] > button:hover::before { transform: translateX(100%) !important; }
    [data-testid="stButton"] > button:hover {
        background: #C44B00 !important;
        box-shadow: 0 6px 24px rgba(232,93,4,.35) !important;
    }
    [data-testid="stButton"] > button:active { transform: scale(.98) !important; }

    /* ── ERRO DE AUTENTICAÇÃO ─────────────────────────────────────────────── */
    [data-testid="stAlert"] {
        background: rgba(239,68,68,.08) !important;
        border: 1px solid rgba(239,68,68,.25) !important;
        border-radius: 10px !important;
        color: #FCA5A5 !important;
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif !important;
        font-size: 13px !important;
        margin-top: .5rem !important;
    }

    /* ── FOOTER / WATERMARK ───────────────────────────────────────────────── */
    .form-footer {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
        font-size: 11px; color: rgba(138,123,114,.45);
        line-height: 1.6; text-align: center; margin-top: 2.5rem;
    }
    .corner-mark {
        position: fixed; bottom: 1.8rem; right: 2rem;
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
        font-size: 10px; letter-spacing: .12em;
        color: rgba(138,123,114,.25); text-transform: uppercase;
    }

    /* ── ANIMAÇÕES ────────────────────────────────────────────────────────── */
    @keyframes lgi-drift {
        0%, 100% { transform: translate(0, 0); }
        50%       { transform: translate(24px, 16px); }
    }
    @keyframes lgi-fadeUp {
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes lgi-fadeIn {
        to { opacity: 1; transform: translateX(0); }
    }
    </style>
    """, unsafe_allow_html=True)

    # ── LAYOUT 2 COLUNAS ─────────────────────────────────────────────────────
    col_brand, col_form = st.columns([52, 48])

    # ── BRAND PANEL (esquerda) ────────────────────────────────────────────────
    with col_brand:
        import base64
        import os
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
            logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:100%;max-width:340px;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,0.4);" />'
        else:
            logo_html = '<div class="logo-name">Pane<br>linhas<span>do Brasil</span></div>'

        st.markdown(f"""
        <div class="brand-wrap">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="bg-letter">PB</div>
            <div class="brand-content">
                <p class="eyebrow">Sistema de Controle de Estoque</p>
                <div class="logo-lockup">
                    {logo_html}
                </div>
                <p class="tagline">
                    Gerencie seu estoque com precisão e agilidade.<br>
                    Controle total na palma da sua mão.
                </p>
                <div class="stats-row">
                    <div class="stat-item">
                        <div class="stat-value">100%</div>
                        <div class="stat-label">Online</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">ERP</div>
                        <div class="stat-label">Integrado</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">V10.0</div>
                        <div class="stat-label">Versão atual</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── FORM PANEL (direita) ──────────────────────────────────────────────────
    with col_form:
        st.markdown("""
        <div class="form-box-wrap">
            <h1 class="form-title">BEM-VINDO<br>DE VOLTA.</h1>
            <p class="form-subtitle">Insira suas credenciais para continuar</p>
        </div>
        <div class="field-label">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                 stroke="#8A7B72" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
            </svg>
            Usuário
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form", border=False):
            usuario = st.text_input("", placeholder="seu usuário",
                                    label_visibility="collapsed", key="li_usr")

            st.markdown("""
            <div class="field-label" style="margin-top:1.1rem;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                     stroke="#8A7B72" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                Senha
            </div>
            """, unsafe_allow_html=True)
            senha = st.text_input("", placeholder="••••••••", type="password",
                                  label_visibility="collapsed", key="li_pw")

            st.markdown("""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.8rem; margin-bottom:1.5rem;">
                <label style="font-family:'Plus Jakarta Sans', 'Outfit', sans-serif; font-size:12px; color:#8A7B72; cursor:pointer; display:flex; align-items:center;">
                    <input type="checkbox" style="accent-color:#E85D04; margin-right:8px; width:14px; height:14px; cursor:pointer; background:#1E1A17; border:1px solid rgba(232,93,4,.18);"> 
                    Manter conectado
                </label>
                <a href="#" style="font-family:'Plus Jakarta Sans', 'Outfit', sans-serif; font-size:12px; color:#E85D04; text-decoration:none; font-weight:500; letter-spacing:.03em;">Esqueci a senha</a>
            </div>
            """, unsafe_allow_html=True)

            submitted = st.form_submit_button("Entrar no sistema  →", type="primary", use_container_width=True)
            if submitted:
                r = autenticar(usuario.strip(), senha.strip())
                if r:
                    st.session_state.usuario = r
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

        st.markdown("""
        <div class="form-footer">Acesso restrito · Panelinhas do Brasil © 2026</div>
        <div class="corner-mark">ERP v10.0</div>
        """, unsafe_allow_html=True)

if not st.session_state.usuario:
    tela_login()
    st.stop()

# ── PRÉ-CARREGAMENTO DE SESSÃO (executa 1x por login) ───────────────────────
if not st.session_state._dados_pre_carregados:
    st.session_state["_itens_df"]       = listar_itens()
    st.session_state["_fornecedores_df"] = listar_fornecedores()
    st.session_state["_composicao_df"]   = listar_composicao()
    st.session_state._dados_pre_carregados = True

u      = st.session_state.usuario
perfil = u["perfil"]

NAV = [("entrada","📥  Entrada"),("saida","📤  Saída"),
       ("ajuste","🔧  Ajuste"),("consulta","🔍  Consulta")]
if perfil in ("gerente","admin"):
    NAV.append(("dashboard","📊  Dashboard"))
    NAV.append(("planejamento","🗓️  Planejamento"))
    NAV.append(("guia_gerente","📘  Guia Gerente"))
if perfil == "admin":
    NAV.append(("composicao","🧩  Composição"))
    NAV.append(("sync","☁️  Google Sheets"))
    NAV.append(("guia_admin","📘  Guia Admin"))

def ir(dest):
    st.session_state.menu = dest
    st.rerun()

# ── LAYOUT 2 COLUNAS ────────────────────────────────────
col_menu, col_conteudo = st.columns([1, 4], gap="small")

with col_menu:
    # Logo + User card (o fundo escuro vem do CSS aplicado na coluna)
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #FF7B25 0%, #E85D0C 50%, #D14E00 100%);
            border-radius: 14px;
            padding: 14px 10px 10px;
            text-align: center;
            margin-bottom: 14px;
            box-shadow: 0 6px 20px rgba(232, 93, 12, 0.3);
        ">
            <img src="data:image/png;base64,{LOGO_B64}"
                 style="width:100%;max-width:160px;height:auto;border-radius:8px;
                        filter: drop-shadow(0 2px 6px rgba(0,0,0,0.15));"/>
            <div style="font-family:'Outfit',sans-serif;font-size:9px;color:rgba(255,255,255,0.65);
        letter-spacing:2px;text-transform:uppercase;margin-top:6px;font-weight:600;">ERP · Estoque</div>
        </div>
        <div style="
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px;
            padding: 10px 14px;
            margin-bottom: 6px;
        ">
            <div style="font-family:'Outfit',sans-serif;font-size:14px;font-weight:600;color:#fff;">👤 {u["nome"]}</div>
            <div style="font-family:'Outfit',sans-serif;font-size:11px;color:#666;font-weight:500;margin-top:2px;">{perfil.title()}</div>
        </div>
        <div style="font-family:'Outfit',sans-serif;font-size:9px;color:rgba(255,255,255,0.2);
                    letter-spacing:2.5px;margin:10px 0 6px 4px;text-transform:uppercase;font-weight:700;">Navegação</div>
    """, unsafe_allow_html=True)

    for key, label in NAV:
        ativo = st.session_state.menu == key
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if ativo else "secondary"):
            ir(key)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪  Sair", use_container_width=True, key="nav_sair"):
        st.session_state.usuario = None
        st.session_state.menu    = "entrada"
        st.rerun()

# ── CONTEÚDO ────────────────────────────────────────────
with col_conteudo:

    def header(ico, titulo, sub=""):
        st.markdown(f"""
        <div class="ph">
            <span style="font-size:26px">{ico}</span>
            <div><h2>{titulo}</h2><p>{sub}</p></div>
        </div>""", unsafe_allow_html=True)

    # ── ENTRADA ─────────────────────────────────────────
    def tela_entrada():
        st.markdown("""
        <style>
        /* ── CSS Entrada Dark Theme ── */
        .block-container { padding-top: 1.5rem !important; }
        
        input[type="text"], input[type="number"],
        .stTextInput > div > div > input, .stNumberInput > div > div > input {
            background: #141210 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            color: #FFF8F0 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 14px !important;
            height: 48px !important;
            transition: all 0.2s ease !important;
        }
        input[type="text"]:focus, input[type="number"]:focus,
        .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
            border-color: #E85D04 !important;
            box-shadow: 0 0 0 3px rgba(232,93,4,0.15) !important;
        }
        .stSelectbox > div > div {
            background: #141210 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            color: #FFF8F0 !important;
            min-height: 48px !important;
        }
        .stSelectbox > div > div:focus-within {
            border-color: #E85D04 !important;
            box-shadow: 0 0 0 3px rgba(232,93,4,0.15) !important;
        }
        .stTextInput label, .stNumberInput label, .stSelectbox label {
            display: none !important; /* Esconde nativas */
        }
        
        /* Botão Adicionar ao lançamento (Outline/Azulado) */
        .btn-add > div > button {
            background: rgba(43,76,140,0.15) !important;
            color: #7BA1F2 !important;
            border: 1px solid rgba(43,76,140,0.4) !important;
            border-radius: 8px !important;
            font-size: 13.5px !important;
            font-weight: 600 !important;
            height: 44px !important;
            transition: all 0.2s !important;
        }
        .btn-add > div > button:hover {
            background: rgba(43,76,140,0.25) !important;
            border-color: rgba(43,76,140,0.6) !important;
            color: #93B2F4 !important;
        }
        
        /* Botão Confirmar (Laranja) */
        .btn-confirm > div > button {
            background: #E85D04 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            height: 44px !important;
            transition: all 0.2s !important;
        }
        .btn-confirm > div > button:hover {
            background: #FF6B1A !important;
        }
        
        /* Botão Cancelar (Cinza) */
        .btn-cancel > div > button {
            background: transparent !important;
            color: #8A7B72 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            height: 44px !important;
            transition: all 0.2s !important;
        }
        .btn-cancel > div > button:hover {
            background: #1A1715 !important;
            color: #FFF8F0 !important;
            border-color: #554A40 !important;
        }
        
        .stDataFrame {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid #332B25 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-bottom: 24px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <h1 style="font-family:'Bebas Neue',sans-serif;font-size:42px;color:#FFF8F0;letter-spacing:1px;margin:0;line-height:1;">ENTRADA DE ESTOQUE</h1>
                <span style="background:#0F2A1B;color:#2ED297;border:1px solid #164028;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:5px 12px;border-radius:20px;">Novo Lançamento</span>
            </div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;color:#554A40;margin-top:6px;font-style:italic;">Registre o recebimento de mercadorias — adicione vários itens antes de confirmar</div>
        </div>
        """, unsafe_allow_html=True)

        itens = listar_itens(); forn = listar_fornecedores()
        if itens.empty: st.warning("Nenhum item cadastrado."); return

        # Entrada permite todos os itens, inclusive kits/refeições (PAN)
        itens_entrada = itens.copy()
        if itens_entrada.empty:
            st.warning("Nenhum item de entrada cadastrado."); return

        # Ordenar para que PAN apareça primeiro, em ordem crescente de código
        itens_entrada['is_pan'] = itens_entrada['id_item'].str.startswith('PAN-')
        itens_entrada = itens_entrada.sort_values(by=['is_pan', 'id_item'], ascending=[False, True])

        op_item = {f"{r['id_item']} — {r['nome']}":r['id_item'] for _,r in itens_entrada.iterrows()}
        op_forn = {f"{r['id_fornecedor']} — {r['nome']}":r['id_fornecedor'] for _,r in forn.iterrows()}

        if "carrinho_entrada" not in st.session_state:
            st.session_state["carrinho_entrada"] = []

        reset_key = st.session_state.get("entrada_reset_key", 0)

        # ── FORM CARD ────────────────────────────────────────────────────
        st.markdown("""
        <div style="background:#1A1715;border-radius:12px 12px 0 0;border:1px solid #2A2624;border-bottom:none;">
            <div style="padding:18px 24px;display:flex;align-items:center;gap:14px;border-bottom:1px solid #2A2624;">
                <div style="width:36px;height:36px;background:#141210;border:1px solid #2A2624;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;color:#A987D9;">➕</div>
                <div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:14.5px;font-weight:700;color:#FFF8F0;">Adicionar item ao lançamento</div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;color:#554A40;margin-top:2px;">Preencha os dados do item recebido</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="background:#1A1715;border-radius:0 0 12px 12px;border:1px solid #2A2624;border-top:none;padding:24px;margin-bottom:24px;">', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;display:flex;align-items:center;gap:6px;">📦 ITEM <span style="color:#E85D04">*</span></div>', unsafe_allow_html=True)
            item_sel = st.selectbox("Item", list(op_item.keys()), index=None, placeholder="Selecione o item...", key=f"ent_item_{reset_key}", label_visibility="collapsed")
            
            st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;margin-top:16px;display:flex;align-items:center;gap:6px;">🏭 FORNECEDOR <span style="color:#E85D04">*</span></div>', unsafe_allow_html=True)
            forn_sel = st.selectbox("Fornecedor", list(op_forn.keys()), index=None, placeholder="Selecione o fornecedor...", key=f"ent_forn_{reset_key}", label_visibility="collapsed")
            
            st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;margin-top:16px;display:flex;align-items:center;gap:6px;">📄 Nº NF <span style="color:#E85D04">*</span></div>', unsafe_allow_html=True)
            nf = st.text_input("Nº NF", placeholder="obrigatório", key=f"ent_nf_{reset_key}", label_visibility="collapsed")
            
        with c2:
            st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;display:flex;align-items:center;gap:6px;">🔢 QUANTIDADE <span style="color:#E85D04">*</span></div>', unsafe_allow_html=True)
            qtd  = st.number_input("Quantidade", min_value=0.001, step=1.0, format="%.0f", value=None, placeholder="0", key=f"ent_qtd_{reset_key}", label_visibility="collapsed")
            
            st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;margin-top:16px;display:flex;align-items:center;gap:6px;">💰 CUSTO UNIT. (R$)</div>', unsafe_allow_html=True)
            vunt = st.number_input("Custo", min_value=0.0, step=0.01, format="%.2f", value=0.0, key=f"ent_vunt_{reset_key}", label_visibility="collapsed")
            
            st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;margin-top:16px;display:flex;align-items:center;gap:6px;">💬 OBSERVAÇÃO</div>', unsafe_allow_html=True)
            obs  = st.text_input("Observação", placeholder="opcional", key=f"ent_obs_{reset_key}", label_visibility="collapsed")

        st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

        # Stock info panel
        if item_sel:
            id_item = op_item[item_sel]
            info    = itens_entrada[itens_entrada["id_item"]==id_item].iloc[0]
            sal     = saldo_item(id_item)
            q_val   = qtd if qtd is not None else 0.0
            v_val   = vunt if vunt is not None else 0.0

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;padding:12px 18px;background:#0F1D1A;border-radius:8px;border:1px solid #143A2A;margin-bottom:20px;">
                <span style="font-size:18px;">✔️</span>
                <div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;color:#2ED297;"><strong style="color:#FFF8F0;">Saldo atual:</strong> {sal:.0f} {info['unidade']}</div>
                    <div style="font-size:11.5px;color:#1D9E75;margin-top:2px;">Entrada: +{q_val:.0f} &nbsp;|&nbsp; Novo: {sal + q_val:.0f} &nbsp;|&nbsp; R$ {q_val * v_val:,.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display:flex;align-items:center;gap:12px;padding:14px 18px;background:#2A200B;border-radius:8px;border:1px solid #4A3510;margin-bottom:20px;">
                <span style="font-size:16px;">💡</span>
                <span style="font-size:13px;color:#D99F2A;">Selecione um item para ver o saldo atual e adicioná-lo ao lançamento.</span>
            </div>
            """, unsafe_allow_html=True)

        col_space, col_add = st.columns([5, 3])
        with col_add:
            st.markdown('<div class="btn-add">', unsafe_allow_html=True)
            if st.button("＋ Adicionar ao lançamento", use_container_width=True, key="btn_add_cart"):
                if not item_sel: st.error("Selecione o item.")
                elif not forn_sel: st.error("Selecione o fornecedor.")
                elif not nf or not str(nf).strip(): st.error("Informe a Nota Fiscal (NF).")
                elif qtd is None or qtd <= 0: st.error("Quantidade deve ser maior que zero.")
                else:
                    forn_nome = forn_sel.split(" — ", 1)[1] if " — " in forn_sel else forn_sel
                    st.session_state["carrinho_entrada"].append({
                        "id_item":       id_item,
                        "nome":          info["nome"],
                        "unidade":       info["unidade"],
                        "fornecedor_id": op_forn[forn_sel],
                        "fornecedor":    forn_nome,
                        "qtd":           qtd,
                        "vunit":         v_val,
                        "total":         round(qtd * v_val, 2),
                        "nf":            str(nf).strip(),
                        "obs":           obs if obs else "—",
                        "saldo_antes":   sal,
                    })
                    st.success(f"✅ **{info['nome']}** adicionado ao lançamento!")
                    st.session_state["entrada_reset_key"] = reset_key + 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

        # ─── ITEMS LIST ───────────────────────────────────────────────────
        n = len(st.session_state["carrinho_entrada"])
        count_label = f"{n} item" if n == 1 else f"{n} itens"
        total_num = sum([float(i["total"]) for i in st.session_state["carrinho_entrada"]])

        st.markdown("""
        <div style="background:#1A1715;border-radius:12px 12px 0 0;border:1px solid #2A2624;border-bottom:none;">
            <div style="padding:18px 24px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #2A2624;">
                <div style="display:flex;align-items:center;gap:14px;">
                    <div style="width:36px;height:36px;background:#141210;border:1px solid #2A2624;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;color:#D99F2A;">📁</div>
                    <div>
                        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:14.5px;font-weight:700;color:#FFF8F0;">Itens do lançamento</div>
                        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;color:#554A40;margin-top:2px;">Itens adicionados nesta entrada serão listados aqui</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="background:#1A1715;border-radius:0 0 12px 12px;border:1px solid #2A2624;border-top:none;padding:24px;">', unsafe_allow_html=True)

        if n == 0:
            st.markdown("""
            <div style="text-align:center;padding:30px 0;">
                <div style="font-size:13px;color:#554A40;">Nenhum item adicionado ao lançamento.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            df = pd.DataFrame(st.session_state["carrinho_entrada"])
            df_disp = df[["nome", "qtd", "vunit", "total", "fornecedor", "nf", "obs"]].copy()
            df_disp.rename(columns={"nome":"📦 Item", "qtd":"🔢 Qtd", "vunit":"💰 Custo unit.", "total":"💵 Total", "fornecedor":"🏭 Fornecedor", "nf":"📄 Nº NF", "obs":"💬 Obs."}, inplace=True)
            
            st.dataframe(
                df_disp,
                use_container_width=True,
                hide_index=True,
                height=min(100 + n * 48, 380),
            )

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns([2, 2, 6])
            with col_a:
                st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
                if st.button("🗑️ Remover último", use_container_width=True):
                    st.session_state["carrinho_entrada"].pop()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col_b:
                st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
                if st.button("✕ Limpar tudo", use_container_width=True):
                    st.session_state["carrinho_entrada"] = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ─── FOOTER BAR ───────────────────────────────────────────────────
        st.markdown(f"""
        <div style="margin-top:30px; border-top:1px solid #332B25; padding-top:20px; display:flex; align-items:center; justify-content:space-between;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:8px;height:8px;background:#D99F2A;border-radius:50%; box-shadow: 0 0 6px rgba(217,159,42,0.6);"></div>
                <span style="font-size:12.5px;color:#8A7B72;">Lançamento em andamento · {n} item(ns)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
        col_space, col_cancel, col_confirm = st.columns([5, 2, 3])
        with col_cancel:
            st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
            if st.button("🗑️ Cancelar", use_container_width=True):
                st.session_state["carrinho_entrada"] = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_confirm:
            st.markdown('<div class="btn-confirm">', unsafe_allow_html=True)
            if st.button("✓ Confirmar entrada", use_container_width=True):
                if n == 0:
                    st.error("Adicione itens ao lançamento antes de confirmar.")
                else:
                    erros = []
                    ok = 0
                    for item in st.session_state["carrinho_entrada"]:
                        try:
                            if is_composto(item["id_item"]):
                                from utils.data import registrar_entrada_composta
                                registrar_entrada_composta(
                                    item["id_item"],
                                    item["qtd"],
                                    u["usuario"],
                                    nf=item["nf"],
                                    valor_unit=item["vunit"] if item["vunit"] > 0 else "",
                                    fornecedor_id=item["fornecedor_id"],
                                    obs=item["obs"]
                                )
                            else:
                                registrar_movimento(
                                    "ENTRADA", 
                                    item["id_item"], 
                                    item["qtd"], 
                                    u["usuario"],
                                    valor_unit=item["vunit"] if item["vunit"] > 0 else "",
                                    fornecedor_id=item["fornecedor_id"],
                                    motivo=f"NF: {item['nf']}",
                                    obs=item["obs"]
                                )
                            ok += 1
                        except Exception as e:
                            erros.append(f"{item['nome']}: {e}")
                    
                    if erros:
                        st.error(f"⚠️ {ok} registrado(s). Erros: {'; '.join(erros)}")
                    else:
                        st.success(f"🎉 **Lançamento confirmado!** {n} item(s) registrado(s) no estoque.")
                    
                    st.session_state["carrinho_entrada"] = []
                    st.session_state["entrada_reset_key"] = reset_key + 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)





    # ── SAÍDA ────────────────────────────────────────────
    TIPOS_SAIDA = ["Consumo", "Descarte", "Devolução", "Transferência", "Baixa manual", "Outro"]
    ICONES_SAIDA = ["📦", "🗑️", "↩️", "🔄", "📉", "💼"]
    
    def tela_saida():
        st.markdown("""
        <style>
        /* ── CSS Saída Dark Theme ── */
        .block-container { padding-top: 1.5rem !important; }
        input[type="text"], input[type="number"],
        .stTextInput > div > div > input, .stNumberInput > div > div > input {
            background: #141210 !important; border: 1px solid #332B25 !important;
            border-radius: 8px !important; color: #FFF8F0 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 14px !important; height: 48px !important; transition: all 0.2s ease !important;
        }
        input[type="text"]:focus, input[type="number"]:focus,
        .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
            border-color: #EF4444 !important; box-shadow: 0 0 0 3px rgba(239,68,68,0.15) !important;
        }
        .stSelectbox > div > div {
            background: #141210 !important; border: 1px solid #332B25 !important;
            border-radius: 8px !important; color: #FFF8F0 !important; min-height: 48px !important;
        }
        .stSelectbox > div > div:focus-within {
            border-color: #EF4444 !important; box-shadow: 0 0 0 3px rgba(239,68,68,0.15) !important;
        }
        .stTextInput label, .stNumberInput label, .stSelectbox label { display: none !important; }
        .stRadio > div[role="radiogroup"] {
            display: grid !important; grid-template-columns: 1fr 1fr 1fr !important; gap: 12px !important;
        }
        .stRadio > div[role="radiogroup"] > label {
            background: #141210 !important; border: 1px solid #2A2624 !important;
            border-radius: 12px !important; padding: 24px 16px !important; cursor: pointer !important;
            transition: all 0.2s !important; color: #FFF8F0 !important; text-align: center !important;
            display: flex !important; flex-direction: column !important;
            align-items: center !important; justify-content: center !important;
        }
        .stRadio > div[role="radiogroup"] > label:hover { border-color: #554A40 !important; background: #1C1917 !important; }
        .stRadio > div[role="radiogroup"] > label:has(input:checked) {
            border-color: #EF4444 !important; background: rgba(239,68,68,0.05) !important;
            box-shadow: 0 0 0 1px #EF4444 !important;
        }
        .stRadio > div[role="radiogroup"] > label > div:first-child { display: none !important; }
        .stRadio div[data-testid="stMarkdownContainer"] > p { font-size: 15px !important; font-weight: 600 !important; margin: 0 !important; }
        .btn-confirm > div > button {
            background: #EF4444 !important; color: #ffffff !important; border: none !important;
            border-radius: 8px !important; font-size: 14px !important; font-weight: 600 !important;
            height: 44px !important; transition: all 0.2s !important;
        }
        .btn-confirm > div > button:hover { background: #DC2626 !important; }
        .btn-add > div > button {
            background: #1C3020 !important; color: #2ED297 !important; border: 1px solid #2A4A35 !important;
            border-radius: 8px !important; font-size: 14px !important; font-weight: 600 !important;
            height: 44px !important; transition: all 0.2s !important;
        }
        .btn-add > div > button:hover { background: #243D2A !important; border-color: #2ED297 !important; }
        .btn-cancel > div > button {
            background: transparent !important; color: #8A7B72 !important; border: 1px solid #332B25 !important;
            border-radius: 8px !important; font-size: 14px !important; font-weight: 500 !important;
            height: 44px !important; transition: all 0.2s !important;
        }
        .btn-cancel > div > button:hover { background: #1A1715 !important; color: #FFF8F0 !important; border-color: #554A40 !important; }
        </style>
        """, unsafe_allow_html=True)

        # ── Inicializar carrinho ─────────────────────────────────────────────
        if "carrinho_saida" not in st.session_state:
            st.session_state["carrinho_saida"] = []

        itens = listar_itens()
        if itens.empty: st.warning("Nenhum item cadastrado."); return
        op_item = {f"{r['id_item']} — {r['nome']}":r['id_item'] for _,r in itens.iterrows()}
        reset_key = st.session_state.get("saida_reset_key", 0)

        # ── HEADER ──────────────────────────────────────────────────────────
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <h1 style="font-family:'Bebas Neue',sans-serif;font-size:42px;color:#FFF8F0;letter-spacing:1px;margin:0;line-height:1;">SAÍDA DE ESTOQUE</h1>
                <span style="background:#3B1219;color:#EF4444;border:1px solid #5A1A22;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:5px 12px;border-radius:20px;">BAIXA / CONSUMO</span>
            </div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;color:#554A40;margin-top:6px;font-style:italic;">Registre consumo, descarte ou baixa de itens do estoque</div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPIs DINÂMICOS ───────────────────────────────────────────────────
        movs = listar_movimentos()
        saidas_hoje = 0
        mais_consumido = "Nenhum"
        ultimo_lanc = "Nenhum"
        if not movs.empty:
            saidas_df = movs[movs["tipo"] == "SAÍDA"]
            if not saidas_df.empty:
                saidas_hoje = len(saidas_df[saidas_df["timestamp"].dt.date == date.today()])
                mais_consumido = saidas_df["nome_item"].value_counts().idxmax()
                ultimo_lanc = saidas_df["timestamp"].max().strftime("%d/%m")

        kpi_saldo_val = "—"
        kpi_saldo_cor = "#8A7B72"
        if st.session_state["carrinho_saida"]:
            ultimo = st.session_state["carrinho_saida"][-1]
            novo_s = ultimo["saldo_antes"] - ultimo["qtd"]
            kpi_saldo_val = f"{novo_s:.0f} {ultimo['unidade']}"
            kpi_saldo_cor = "#EF4444" if novo_s <= 0 else "#2ED297"

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px;margin-bottom:24px;">
            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;background:#141210;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;border:1px solid #2A2624;">📊</div>
                <div><div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">Saídas Hoje</div><div style="font-size:16px;color:#FFF8F0;font-weight:700;margin-top:2px;">{saidas_hoje}</div></div>
            </div>
            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;background:#2A200B;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;border:1px solid #4A3510;">⚠️</div>
                <div><div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">Último Saldo</div><div style="font-size:16px;color:{kpi_saldo_cor};font-weight:700;margin-top:2px;">{kpi_saldo_val}</div></div>
            </div>
            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;background:#3B1A19;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;border:1px solid #5A2222;">🔥</div>
                <div><div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">Mais Consumido</div><div style="font-size:16px;color:#FFF8F0;font-weight:700;margin-top:2px;">{mais_consumido}</div></div>
            </div>
            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;background:#0F2A1B;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;border:1px solid #164028;">✅</div>
                <div><div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">Último Lançamento</div><div style="font-size:16px;color:#FFF8F0;font-weight:700;margin-top:2px;">{ultimo_lanc}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── CARD 1: TIPO DE SAÍDA DO LOTE ───────────────────────────────────
        st.markdown("""
        <div style="background:#1A1715;border-radius:12px 12px 0 0;border:1px solid #2A2624;border-bottom:none;">
            <div style="padding:18px 24px;display:flex;align-items:center;gap:14px;border-bottom:1px solid #2A2624;">
                <div style="width:36px;height:36px;background:#2A200B;border:1px solid #4A3510;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#D99F2A;">🏷️</div>
                <div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:14.5px;font-weight:700;color:#FFF8F0;">Tipo de saída do lote</div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;color:#554A40;margin-top:2px;">Classifique o motivo — aplicado a todos os itens do lançamento</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="background:#1A1715;border-radius:0 0 12px 12px;border:1px solid #2A2624;border-top:none;padding:24px;margin-bottom:24px;">', unsafe_allow_html=True)

        radio_options = [f"{ICONES_SAIDA[i]} {TIPOS_SAIDA[i]}" for i in range(6)]
        tipo_said_val = st.radio("Tipo de saída", radio_options, index=0, key=f"sai_tipo_{reset_key}", label_visibility="collapsed")
        tipo_said = ""
        for i, opt in enumerate(radio_options):
            if tipo_said_val == opt:
                tipo_said = TIPOS_SAIDA[i]; break

        st.markdown('</div>', unsafe_allow_html=True)

        # ── CARD 2: ADICIONAR ITEM ──────────────────────────────────────────
        st.markdown("""
        <div style="background:#1A1715;border-radius:12px 12px 0 0;border:1px solid #2A2624;border-bottom:none;">
            <div style="padding:18px 24px;display:flex;align-items:center;gap:14px;border-bottom:1px solid #2A2624;">
                <div style="width:36px;height:36px;background:#3B1219;border:1px solid #5A1A22;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#EF4444;">📤</div>
                <div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:14.5px;font-weight:700;color:#FFF8F0;">Adicionar item ao lançamento</div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;color:#554A40;margin-top:2px;">Selecione o item e a quantidade — adicione quantos quiser antes de confirmar</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="background:#1A1715;border-radius:0 0 12px 12px;border:1px solid #2A2624;border-top:none;padding:24px;margin-bottom:24px;">', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;display:flex;align-items:center;gap:6px;">❓ ITEM <span style="color:#EF4444">*</span></div>', unsafe_allow_html=True)
            item_sel = st.selectbox("Item", list(op_item), index=None, placeholder="Selecione o item...", key=f"sai_item_{reset_key}", label_visibility="collapsed")
        with c2:
            st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;display:flex;align-items:center;gap:6px;">🔢 QUANTIDADE <span style="color:#EF4444">*</span></div>', unsafe_allow_html=True)
            qtd = st.number_input("Quantidade", min_value=0.001, step=1.0, format="%.0f", value=None, placeholder="0", key=f"sai_qtd_{reset_key}", label_visibility="collapsed")

        st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;margin-top:16px;display:flex;align-items:center;gap:6px;">📝 OBSERVAÇÃO</div>', unsafe_allow_html=True)
        obs = st.text_input("Observação", placeholder="opcional ➔ detalhe o motivo ou destino", key=f"sai_obs_{reset_key}", label_visibility="collapsed")

        st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

        sal = 0; mn = 0; novo = 0; composto = False

        if item_sel:
            id_item  = op_item[item_sel]
            info     = itens[itens["id_item"] == id_item].iloc[0]
            sal      = saldo_item(id_item)
            mn       = float(info["estoque_minimo"])
            q_val    = qtd if qtd is not None else 0.0
            novo     = sal - q_val
            composto = is_composto(id_item)
            composicao = composicao_produto(id_item) if composto else []

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;padding:12px 18px;background:#0F1D1A;border-radius:8px;border:1px solid #143A2A;">
                <span style="font-size:18px;">✔️</span>
                <div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;color:#2ED297;"><strong style="color:#FFF8F0;">Saldo atual:</strong> {sal:.0f} {info['unidade']}</div>
                    <div style="font-size:11.5px;color:#1D9E75;margin-top:2px;">Saída: -{q_val:.0f} &nbsp;|&nbsp; Novo saldo: {novo:.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if composto:
                linhas = "".join([
                    f"<li style='color:#A8A59E;'><b style='color:#FFF8F0;'>{c['id_ingrediente']}</b> — {c['nome_ingrediente']} × {float(c['quantidade'])*q_val:.0f} {c['unidade']}</li>"
                    for c in composicao
                ])
                st.markdown(f"<div style='margin-top:12px;padding:12px 16px;background:#141210;border-radius:8px;border:1px solid #332B25;font-size:13px;'>🧩 <b style='color:#A987D9;'>Produto composto</b> — ingredientes descontados:<ul style='margin:6px 0 0 16px'>{linhas}</ul></div>", unsafe_allow_html=True)

            if sal <= 0: st.error(f"🔴 ZERADO! Saldo: {sal:.0f} {info['unidade']}")
            elif sal <= mn: st.warning(f"🟡 CRÍTICO. Saldo: {sal:.0f} | mín: {mn:.0f}")
            if novo < 0: st.error(f"⛔ Quantidade maior que o disponível ({sal:.0f}).")
        else:
            st.markdown("""
            <div style="display:flex;align-items:center;gap:12px;padding:14px 18px;background:#2A200B;border-radius:8px;border:1px solid #4A3510;">
                <span style="font-size:16px;">💡</span>
                <span style="font-size:13px;color:#D99F2A;">Selecione um item para ver o saldo atual e adicioná-lo ao lançamento.</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
        col_space, col_add = st.columns([5, 3])
        with col_add:
            st.markdown('<div class="btn-add">', unsafe_allow_html=True)
            if st.button("＋ Adicionar ao lançamento", use_container_width=True, key="btn_add_saida"):
                if not item_sel: st.error("Selecione o item.")
                elif not tipo_said: st.error("Selecione o tipo de saída.")
                elif qtd is None or qtd <= 0: st.error("Quantidade deve ser maior que zero.")
                elif novo < 0: st.error(f"Quantidade maior que o disponível ({sal:.0f}).")
                else:
                    id_it = op_item[item_sel]
                    inf   = itens[itens["id_item"] == id_it].iloc[0]
                    sal_a = saldo_item(id_it)
                    st.session_state["carrinho_saida"].append({
                        "id_item":     id_it,
                        "nome":        inf["nome"],
                        "unidade":     inf["unidade"],
                        "qtd":         qtd,
                        "saldo_antes": sal_a,
                        "obs":         obs if obs else "—",
                        "composto":    is_composto(id_it),
                    })
                    st.success(f"✅ **{inf['nome']}** adicionado ao lançamento!")
                    st.session_state["saida_reset_key"] = reset_key + 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── CARD 3: LISTA DO LANÇAMENTO ─────────────────────────────────────
        n = len(st.session_state["carrinho_saida"])

        st.markdown("""
        <div style="background:#1A1715;border-radius:12px 12px 0 0;border:1px solid #2A2624;border-bottom:none;">
            <div style="padding:18px 24px;display:flex;align-items:center;gap:14px;border-bottom:1px solid #2A2624;">
                <div style="width:36px;height:36px;background:#141210;border:1px solid #2A2624;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;color:#EF4444;">📋</div>
                <div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:14.5px;font-weight:700;color:#FFF8F0;">Itens do lançamento</div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;color:#554A40;margin-top:2px;">Itens adicionados para baixa em lote</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="background:#1A1715;border-radius:0 0 12px 12px;border:1px solid #2A2624;border-top:none;padding:24px;">', unsafe_allow_html=True)

        if n == 0:
            st.markdown("""
            <div style="text-align:center;padding:30px 0;">
                <div style="font-size:13px;color:#554A40;">Nenhum item adicionado ao lançamento.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            df_cart = pd.DataFrame(st.session_state["carrinho_saida"])
            df_disp = df_cart[["nome", "qtd", "saldo_antes", "obs"]].copy()
            df_disp["novo_saldo"] = df_disp["saldo_antes"] - df_disp["qtd"]
            df_disp.rename(columns={
                "nome": "📦 Item", "qtd": "🔢 Qtd",
                "saldo_antes": "📊 Saldo Antes", "novo_saldo": "➡️ Novo Saldo", "obs": "💬 Obs.",
            }, inplace=True)
            st.dataframe(df_disp, use_container_width=True, hide_index=True, height=min(100 + n * 48, 380))

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            col_a, col_b, _ = st.columns([2, 2, 6])
            with col_a:
                st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
                if st.button("🗑️ Remover último", use_container_width=True, key="saida_rem_ultimo"):
                    st.session_state["carrinho_saida"].pop(); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col_b:
                st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
                if st.button("✕ Limpar tudo", use_container_width=True, key="saida_limpar"):
                    st.session_state["carrinho_saida"] = []; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── FOOTER + CONFIRMAR ───────────────────────────────────────────────
        indicador_texto = f"{n} item(ns) no lançamento" if n > 0 else "Nenhum item adicionado"
        indicador_cor   = "#EF4444" if n > 0 else "#554A40"

        if st.session_state.get("msg_saida"):
            msg = st.session_state.pop("msg_saida")
            st.success(msg)

        st.markdown(f"""
        <div style="margin-top:30px; border-top:1px solid #332B25; padding-top:20px; display:flex; align-items:center; justify-content:space-between;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:8px;height:8px;background:{indicador_cor};border-radius:50%; box-shadow: 0 0 6px {indicador_cor}88;"></div>
                <span style="font-size:12.5px;color:#8A7B72;">{indicador_texto} · tipo: <b style="color:#FFF8F0;">{tipo_said}</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
        col_space2, col_cancel, col_confirm = st.columns([5, 2, 3])
        with col_cancel:
            st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
            if st.button("🗑️ Cancelar", use_container_width=True, key="saida_cancelar"):
                st.session_state["carrinho_saida"] = []
                st.session_state["saida_reset_key"] = reset_key + 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_confirm:
            st.markdown('<div class="btn-confirm">', unsafe_allow_html=True)
            if st.button("✓ Confirmar baixa em lote", use_container_width=True, key="saida_confirmar"):
                if n == 0:
                    st.error("Adicione itens ao lançamento antes de confirmar.")
                elif not tipo_said:
                    st.error("Selecione o tipo de saída.")
                else:
                    erros = []; ok = 0
                    for item in st.session_state["carrinho_saida"]:
                        try:
                            if item["composto"]:
                                registrar_saida_composta(item["id_item"], item["qtd"], u["usuario"], motivo=tipo_said, obs=item["obs"])
                            else:
                                registrar_movimento("SAÍDA", item["id_item"], item["qtd"], u["usuario"], motivo=tipo_said, obs=item["obs"])
                            ok += 1
                        except Exception as e:
                            erros.append(f"{item['nome']}: {e}")
                    if erros:
                        st.session_state["msg_saida"] = f"⚠️ {ok} registrado(s). Erros: {'; '.join(erros)}"
                    else:
                        st.session_state["msg_saida"] = f"🎉 **Baixa confirmada!** {ok} item(s) baixado(s). Tipo: {tipo_said}"
                    st.session_state["carrinho_saida"] = []
                    st.session_state["saida_reset_key"] = reset_key + 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ── AJUSTE ───────────────────────────────────────────
    MOTIVOS_AJUSTE  = ["Inventário", "Divergência", "Erro de sistema", "Avaria", "Recontagem", "Outro"]
    ICONES_AJUSTE   = ["📋", "⚠️", "💻", "📦", "🔄", "🟠"]
    SUBTIT_AJUSTE   = ["Contagem periódica programada", "Diferença encontrada na conferência",
                       "Lançamento incorreto no sistema", "Produto danificado não registrado",
                       "Correção de uma segunda contagem", "Descreva nas observações acima"]
    def tela_ajuste():
        st.markdown("""
        <style>
        /* ── CSS Ajuste Dark Theme ── */
        .block-container { padding-top: 1.5rem !important; }

        input[type="text"], input[type="number"],
        .stTextInput > div > div > input, .stNumberInput > div > div > input {
            background: #141210 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            color: #FFF8F0 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 14px !important;
            height: 48px !important;
            transition: all 0.2s ease !important;
        }
        input[type="text"]:focus, input[type="number"]:focus,
        .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
            border-color: #D99F2A !important;
            box-shadow: 0 0 0 3px rgba(217,159,42,0.15) !important;
        }
        .stSelectbox > div > div {
            background: #141210 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            color: #FFF8F0 !important;
            min-height: 48px !important;
        }
        .stSelectbox > div > div:focus-within {
            border-color: #D99F2A !important;
            box-shadow: 0 0 0 3px rgba(217,159,42,0.15) !important;
        }
        .stTextInput label, .stNumberInput label, .stSelectbox label {
            display: none !important;
        }

        /* Cards de motivo via Radio */
        .stRadio > div[role="radiogroup"] {
            display: grid !important;
            grid-template-columns: 1fr 1fr 1fr !important;
            gap: 12px !important;
        }
        .stRadio > div[role="radiogroup"] > label {
            background: #141210 !important;
            border: 1px solid #2A2624 !important;
            border-radius: 12px !important;
            padding: 20px 16px !important;
            cursor: pointer !important;
            transition: all 0.2s !important;
            color: #FFF8F0 !important;
            text-align: center !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 6px !important;
        }
        .stRadio > div[role="radiogroup"] > label:hover {
            border-color: #554A40 !important;
            background: #1C1917 !important;
        }
        .stRadio > div[role="radiogroup"] > label:has(input:checked) {
            border-color: #D99F2A !important;
            background: rgba(217,159,42,0.05) !important;
            box-shadow: 0 0 0 1px #D99F2A !important;
        }
        .stRadio > div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }
        .stRadio div[data-testid="stMarkdownContainer"] > p {
            font-size: 13px !important;
            font-weight: 600 !important;
            margin: 0 !important;
        }

        /* Botões */
        .btn-confirm-ajuste > div > button {
            background: #D99F2A !important;
            color: #1A1208 !important;
            border: none !important;
            border-radius: 8px !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            height: 44px !important;
            transition: all 0.2s !important;
        }
        .btn-confirm-ajuste > div > button:hover {
            background: #F0B830 !important;
        }
        .btn-cancel > div > button {
            background: transparent !important;
            color: #8A7B72 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            height: 44px !important;
            transition: all 0.2s !important;
        }
        .btn-cancel > div > button:hover {
            background: #1A1715 !important;
            color: #FFF8F0 !important;
            border-color: #554A40 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # ── HEADER ──────────────────────────────────────────────────────
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <h1 style="font-family:'Bebas Neue',sans-serif;font-size:42px;color:#FFF8F0;letter-spacing:1px;margin:0;line-height:1;">AJUSTE DE ESTOQUE</h1>
                <span style="background:#2A1F08;color:#D99F2A;border:1px solid #4A3510;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:5px 12px;border-radius:20px;">INVENTÁRIO FÍSICO</span>
            </div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;color:#554A40;margin-top:6px;font-style:italic;">Corrija diferenças entre o sistema e a contagem física real</div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPIs MOCK ───────────────────────────────────────────────────
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px;margin-bottom:24px;">
            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;background:#2A1F08;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;border:1px solid #4A3510;">🔧</div>
                <div><div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">Ajustes Hoje</div><div style="font-size:16px;color:#FFF8F0;font-weight:700;margin-top:2px;">{len(listar_movimentos()[listar_movimentos()['timestamp'].dt.date == date.today()][listar_movimentos()['tipo'].str.contains('AJUSTE')]) if not listar_movimentos().empty else 0}</div></div>
            </div>
            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;background:#3B1219;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;border:1px solid #5A1A22;">📨</div>
                <div><div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">Com Divergência</div><div style="font-size:16px;color:#FFF8F0;font-weight:700;margin-top:2px;">{len(listar_movimentos()[listar_movimentos()['tipo'].str.contains('AJUSTE')]) if not listar_movimentos().empty else 0}</div></div>
            </div>
            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;background:#0F2430;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;border:1px solid #1A3A50;">🎯</div>
                <div><div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">Saldo Sistema</div><div style="font-size:16px;color:#FFF8F0;font-weight:700;margin-top:2px;">{len(listar_estoque())} itens</div></div>
            </div>
            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;background:#0F2A1B;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;border:1px solid #164028;">✅</div>
                <div><div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;">Último Ajuste</div><div style="font-size:16px;color:#FFF8F0;font-weight:700;margin-top:2px;">{listar_movimentos()[listar_movimentos()['tipo'].str.contains('AJUSTE')]['timestamp'].max().strftime('%d/%m') if not listar_movimentos().empty and not listar_movimentos()[listar_movimentos()['tipo'].str.contains('AJUSTE')].empty else 'Nenhum'}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        itens = listar_itens()
        if itens.empty: st.warning("Nenhum item cadastrado."); return
        op_item = {f"{r['id_item']} — {r['nome']}":r['id_item'] for _,r in itens.iterrows()}
        reset_key = st.session_state.get("ajuste_reset_key", 0)

        # ── CARD 1: DADOS DO AJUSTE ──────────────────────────────────────
        st.markdown("""
        <div style="background:#1A1715;border-radius:12px 12px 0 0;border:1px solid #2A2624;border-bottom:none;">
            <div style="padding:18px 24px;display:flex;align-items:center;gap:14px;border-bottom:1px solid #2A2624;">
                <div style="width:36px;height:36px;background:#2A1F08;border:1px solid #4A3510;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#D99F2A;">🔧</div>
                <div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:14.5px;font-weight:700;color:#FFF8F0;">Dados do ajuste</div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;color:#554A40;margin-top:2px;">Informe o item e a quantidade física contada no estoque</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="background:#1A1715;border-radius:0 0 12px 12px;border:1px solid #2A2624;border-top:none;padding:24px;margin-bottom:24px;">', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;display:flex;align-items:center;gap:6px;">📦 ITEM <span style="color:#D99F2A">*</span></div>', unsafe_allow_html=True)
            item_sel = st.selectbox("Item", list(op_item), index=None, placeholder="Selecione o item...", key=f"ajt_item_{reset_key}", label_visibility="collapsed")
        with c2:
            st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;display:flex;align-items:center;gap:6px;">📋 QUANTIDADE CONTADA <span style="color:#D99F2A">*</span></div>', unsafe_allow_html=True)
            qtd_fis = st.number_input("Quantidade contada", min_value=0.0, step=1.0, format="%.0f", value=None, placeholder="Digite a contagem física...", key=f"ajt_qtd_{reset_key}", label_visibility="collapsed")

        st.markdown('<div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;margin-bottom:6px;margin-top:16px;display:flex;align-items:center;gap:6px;">💬 OBSERVAÇÃO</div>', unsafe_allow_html=True)
        obs = st.text_input("Observação", placeholder="opcional — descreva o contexto do ajuste", key=f"ajt_obs_{reset_key}", label_visibility="collapsed")

        st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

        # Inicializar variáveis
        sal = 0; diff = 0; tipo_mov = None

        if item_sel:
            id_item = op_item[item_sel]
            info    = itens[itens["id_item"]==id_item].iloc[0]
            sal     = saldo_item(id_item)
            diff    = (qtd_fis - sal) if qtd_fis is not None else 0.0
            tipo_mov = "AJUSTE_POS" if diff > 0 else ("AJUSTE_NEG" if diff < 0 else None)

            cor_diff = "#2ED297" if diff >= 0 else "#EF4444"
            sinal = "+" if diff > 0 else ""
            label_diff = f"{sinal}{diff:.0f}" if qtd_fis is not None else "—"

            st.markdown(f"""
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:16px;">
                <div style="background:#141210;border:1px solid #2A2624;border-radius:10px;padding:14px;text-align:center;">
                    <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">No sistema</div>
                    <div style="font-size:22px;font-weight:700;color:#FFF8F0;">{sal:.0f} <span style="font-size:12px;font-weight:400;color:#8A7B72;">{info['unidade']}</span></div>
                </div>
                <div style="background:#141210;border:1px solid #2A2624;border-radius:10px;padding:14px;text-align:center;">
                    <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Contado</div>
                    <div style="font-size:22px;font-weight:700;color:#FFF8F0;">{f"{qtd_fis:.0f}" if qtd_fis is not None else "—"} <span style="font-size:12px;font-weight:400;color:#8A7B72;">{info['unidade']}</span></div>
                </div>
                <div style="background:#141210;border:1.5px solid {cor_diff}33;border-radius:10px;padding:14px;text-align:center;">
                    <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Diferença</div>
                    <div style="font-size:22px;font-weight:700;color:{cor_diff};">{label_diff}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display:flex;align-items:center;gap:12px;padding:14px 18px;background:#2A200B;border-radius:8px;border:1px solid #4A3510;margin-bottom:16px;">
                <span style="font-size:16px;">💡</span>
                <span style="font-size:13px;color:#D99F2A;">Selecione um item para ver o saldo do sistema e realizar o lançamento.</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ── CARD 2: MOTIVO DO AJUSTE ──────────────────────────────────────
        st.markdown("""
        <div style="background:#1A1715;border-radius:12px 12px 0 0;border:1px solid #2A2624;border-bottom:none;">
            <div style="padding:18px 24px;display:flex;align-items:center;gap:14px;border-bottom:1px solid #2A2624;">
                <div style="width:36px;height:36px;background:#2A1F08;border:1px solid #4A3510;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#D99F2A;">🏷️</div>
                <div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:14.5px;font-weight:700;color:#FFF8F0;">Motivo do ajuste</div>
                    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;color:#554A40;margin-top:2px;">Classifique o motivo para rastreabilidade e auditoria</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="background:#1A1715;border-radius:0 0 12px 12px;border:1px solid #2A2624;border-top:none;padding:24px;">', unsafe_allow_html=True)

        radio_ajuste = [f"{ICONES_AJUSTE[i]}\n{MOTIVOS_AJUSTE[i]}\n{SUBTIT_AJUSTE[i]}" for i in range(6)]
        motivo_val = st.radio("Motivo do ajuste", 
            [f"{ICONES_AJUSTE[i]} {MOTIVOS_AJUSTE[i]}" for i in range(6)], 
            index=0, key=f"ajt_motivo_{reset_key}", label_visibility="collapsed")

        motivo = ""
        for i, tipo in enumerate(MOTIVOS_AJUSTE):
            if f"{ICONES_AJUSTE[i]} {tipo}" == motivo_val:
                motivo = tipo
                break

        if st.session_state.get("msg_ajuste"):
            st.success(st.session_state.pop("msg_ajuste"))

        st.markdown('</div>', unsafe_allow_html=True)

        # ─── FOOTER BAR ───────────────────────────────────────────────────
        indicador_texto = "Nenhum item selecionado" if not item_sel else f"{item_sel.split(' — ')[1]} selecionado"
        indicador_cor   = "#D99F2A" if not item_sel else "#2ED297"

        st.markdown(f"""
        <div style="margin-top:30px;border-top:1px solid #332B25;padding-top:20px;display:flex;align-items:center;justify-content:space-between;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:8px;height:8px;background:{indicador_cor};border-radius:50%;box-shadow:0 0 6px {indicador_cor}88;"></div>
                <span style="font-size:12.5px;color:#8A7B72;">{indicador_texto}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
        col_space, col_cancel, col_confirm = st.columns([5, 2, 3])
        with col_cancel:
            st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
            if st.button("🗑️ Cancelar", use_container_width=True, key="ajt_cancel"):
                st.session_state["ajuste_reset_key"] = reset_key + 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_confirm:
            st.markdown('<div class="btn-confirm-ajuste">', unsafe_allow_html=True)
            if st.button("✓ Confirmar ajuste", use_container_width=True, key="btn_ajt"):
                if not item_sel:    st.error("Por favor, selecione o item.")
                elif qtd_fis is None: st.error("Por favor, insira a quantidade contada.")
                elif tipo_mov is None: st.info("Nenhuma diferença encontrada entre o sistema e a contagem.")
                else:
                    registrar_movimento(tipo_mov, id_item, abs(diff), u["usuario"], motivo=motivo, obs=obs)
                    st.session_state["msg_ajuste"] = f"✅ Ajuste registrado com sucesso! Novo saldo: {qtd_fis:.0f} {info['unidade']}"
                    st.session_state["ajuste_reset_key"] = reset_key + 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)



    # ── CONSULTA ─────────────────────────────────────────
    def tela_consulta():
        st.markdown("""
        <style>
        /* ── CSS Consulta Dark Theme ── */
        .block-container { padding-top: 1.5rem !important; }

        input[type="text"],
        .stTextInput > div > div > input {
            background: #1A1715 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            color: #FFF8F0 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 14px !important;
            height: 44px !important;
        }
        input[type="text"]:focus,
        .stTextInput > div > div > input:focus {
            border-color: #E85D04 !important;
            box-shadow: 0 0 0 3px rgba(232,93,4,0.12) !important;
        }
        .stSelectbox > div > div {
            background: #1A1715 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            color: #FFF8F0 !important;
            min-height: 44px !important;
        }
        .stTextInput label, .stSelectbox label { display:none !important; }

        /* Fix Popover icon font collision */
        [data-testid="stPopover"] p { font-family: 'Plus Jakarta Sans', sans-serif !important; }
        [data-testid="stPopover"] span { font-family: 'Material Symbols Rounded' !important; font-size: 20px !important; }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
            border-bottom: 1px solid #2A2624 !important;
            gap: 4px !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: #1A1715 !important;
            border: 1px solid #2A2624 !important;
            border-radius: 8px 8px 0 0 !important;
            color: #8A7B72 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            padding: 8px 18px !important;
        }
        .stTabs [aria-selected="true"] {
            background: #E85D04 !important;
            border-color: #E85D04 !important;
            color: #fff !important;
        }

        /* Botão Exportar */
        .btn-export > div > button {
            background: #1A1715 !important;
            color: #FFF8F0 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            height: 40px !important;
        }
        .btn-export > div > button:hover {
            background: #332B25 !important;
            border-color: #554A40 !important;
        }

        .stDataFrame { border-radius: 0 0 12px 12px !important; border: 1px solid #2A2624 !important; }
        </style>
        """, unsafe_allow_html=True)

        # ── HEADER ──────────────────────────────────────────────────────
        col_h, col_btns = st.columns([5.5, 4.5])
        with col_h:
            st.markdown("""
            <div style="margin-bottom: 18px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <h1 style="font-family:'Bebas Neue',sans-serif;font-size:42px;color:#FFF8F0;letter-spacing:1px;margin:0;line-height:1;">CONSULTA DE ESTOQUE</h1>
                    <span style="background:#0F2A1B;color:#2ED297;border:1px solid #164028;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:5px 12px;border-radius:20px;">POSIÇÃO ATUAL</span>
                </div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;color:#554A40;margin-top:6px;font-style:italic;">Posição atual e histórico de movimentos do estoque</div>
            </div>
            """, unsafe_allow_html=True)
        with col_btns:
            st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
            c_csv, c_html, c_a = st.columns([1.1, 1.1, 1])
            with c_csv:
                st.markdown('<div class="btn-export">', unsafe_allow_html=True)
                export_csv_container = st.empty()
                st.markdown('</div>', unsafe_allow_html=True)
            with c_html:
                st.markdown('<div class="btn-export">', unsafe_allow_html=True)
                export_html_container = st.empty()
                st.markdown('</div>', unsafe_allow_html=True)
            with c_a:
                st.markdown('<div class="btn-export">', unsafe_allow_html=True)
                if st.button("↻ Atualizar", use_container_width=True, key="btn_refresh_consulta"):
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        aba1, aba2 = st.tabs(["📦 Estoque Atual", "📋 Histórico"])

        with aba1:
            df = listar_estoque()
            if df.empty:
                st.info("Nenhum item cadastrado.")
                return

            # Cruza com itens para obter estoque_minimo e custo_unitario
            itens_c = listar_itens()
            if not itens_c.empty:
                cols_c = [c for c in ["id_item", "estoque_minimo", "custo_unitario"] if c in itens_c.columns]
                df = df.merge(itens_c[cols_c], on="id_item", how="left")

            # Montar dados de status
            rows = []
            for _, r in df.iterrows():
                s  = float(pd.to_numeric(r.get("saldo_atual",  0), errors="coerce") or 0)
                mn = float(pd.to_numeric(r.get("estoque_minimo", 0), errors="coerce") or 0)
                c  = float(pd.to_numeric(r.get("custo_unitario",  0), errors="coerce") or 0)
                rows.append({
                    "Status": status_item(s, mn),
                    "Código": r["id_item"],
                    "Produto": r["nome"],
                    "Categoria": r["categoria"],
                    "Local": r["local"],
                    "Und": r["unidade"],
                    "Saldo": s,
                    "Mínimo": mn,
                    "Valor R$": round(s * c, 2)
                })
            dt_full = pd.DataFrame(rows)

            # ── FILTROS ───────────────────────────────────────────────
            st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">', unsafe_allow_html=True)
            c_busca, c_cat, c_local, c_crit = st.columns([4, 2, 2, 1])
            with c_busca:
                st.markdown('<div style="font-size:0px;">', unsafe_allow_html=True)
                busca = st.text_input("Buscar", placeholder="🔍 Buscar por nome, código ou categoria", key="b1", label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)
            with c_cat:
                cats = ["Todas as categorias"] + sorted(df["categoria"].dropna().unique().tolist())
                cat  = st.selectbox("Categoria", cats, key="c1", label_visibility="collapsed")
            with c_local:
                locais = ["Todos os locais"] + sorted(df["local"].dropna().unique().tolist())
                local  = st.selectbox("Local", locais, key="l1", label_visibility="collapsed")
            with c_crit:
                so_criticos = st.checkbox("Só críticos", key="chk_crit")
            st.markdown('</div>', unsafe_allow_html=True)

            # ── FILTRAR ───────────────────────────────────────────────
            dt = dt_full.copy()
            if busca:
                m = (dt["Código"].str.contains(busca, case=False, na=False) |
                     dt["Produto"].str.contains(busca, case=False, na=False) |
                     dt["Categoria"].str.contains(busca, case=False, na=False))
                dt = dt[m]
            if cat != "Todas as categorias":
                dt = dt[dt["Categoria"] == cat]
            if local != "Todos os locais":
                dt = dt[dt["Local"] == local]
            if so_criticos:
                dt = dt[dt["Status"].str.contains("Zerado|Baixo", na=False)]

            # ── TABELA ────────────────────────────────────────────────
            st.markdown('<div style="border-radius:12px;overflow:hidden;border:1px solid #2A2624;">', unsafe_allow_html=True)
            st.dataframe(
                dt,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Saldo":    st.column_config.NumberColumn(format="%.0f"),
                    "Mínimo":   st.column_config.NumberColumn(format="%.0f"),
                    "Valor R$": st.column_config.NumberColumn(format="R$ %.2f"),
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)

            # Exportar CSV ou HTML (Injetado via st.empty acima)
            with export_csv_container:
                csv = dt.to_csv(index=False, sep=";").encode("utf-8-sig")
                st.download_button("📊 Excel", csv, "estoque.csv", "text/csv", key="dl_csv", use_container_width=True)
            
            with export_html_container:
                try:
                    from utils.relatorios import gerar_html_inventario
                    html_report = gerar_html_inventario(dt).encode("utf-8")
                    st.download_button("📄 Imprimir", html_report, "Relatorio_Inventario.html", "text/html", key="dl_html", use_container_width=True)
                except Exception as e:
                    st.error(f"Erro HTML: {e}")

            # ── BARRA RESUMO ──────────────────────────────────────────
            total     = len(dt)
            zerados   = int(dt["Status"].str.contains("Zerado", na=False).sum())
            criticos  = int(dt["Status"].str.contains("Baixo",  na=False).sum())
            ok_count  = int(dt["Status"].str.contains("Normal", na=False).sum())
            valor_tot = dt["Valor R$"].sum()

            st.markdown(f"""
            <div style="margin-top:20px;background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:20px;">📦</span>
                    <div>
                        <div style="font-size:22px;font-weight:700;color:#FFF8F0;">{total}</div>
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Total Itens</div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:10px;height:10px;background:#EF4444;border-radius:50%;"></div>
                    <div>
                        <div style="font-size:22px;font-weight:700;color:#EF4444;">{zerados}</div>
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Zerados</div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:10px;height:10px;background:#D99F2A;border-radius:50%;"></div>
                    <div>
                        <div style="font-size:22px;font-weight:700;color:#D99F2A;">{criticos}</div>
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Críticos</div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:10px;height:10px;background:#2ED297;border-radius:50%;"></div>
                    <div>
                        <div style="font-size:22px;font-weight:700;color:#2ED297;">{ok_count}</div>
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">OK</div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:20px;">💰</span>
                    <div>
                        <div style="font-size:22px;font-weight:700;color:#E85D04;">R$ {valor_tot:,.2f}</div>
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Valor Total</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with aba2:
            dm = listar_movimentos()
            if dm.empty:
                st.info("Nenhum movimento ainda.")
                return

            # Filtros do histórico
            ch1, ch2 = st.columns([3, 1])
            with ch1:
                bm = st.text_input("Buscar histórico", placeholder="🔍 Buscar por item ou operador", key="b2", label_visibility="collapsed")
            with ch2:
                tps = ["Todos"] + sorted(dm["tipo"].dropna().unique().tolist())
                tf  = st.selectbox("Tipo", tps, key="t2", label_visibility="collapsed")

            df3 = dm.copy()
            if bm:
                m = (df3["nome_item"].str.contains(bm, case=False, na=False) |
                     df3["operador"].str.contains(bm, case=False, na=False))
                df3 = df3[m]
            if tf != "Todos":
                df3 = df3[df3["tipo"] == tf]

            cols = [c for c in ["timestamp", "tipo", "nome_item", "quantidade", "valor_unit", "total", "operador", "motivo", "obs"] if c in df3.columns]
            st.markdown('<div style="border-radius:12px;overflow:hidden;border:1px solid #2A2624;">', unsafe_allow_html=True)
            st.dataframe(
                df3[cols].head(100),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "timestamp":  st.column_config.DatetimeColumn("Data/Hora", format="DD/MM/YY HH:mm"),
                    "quantidade": st.column_config.NumberColumn("Qtd",   format="%.0f"),
                    "valor_unit": st.column_config.NumberColumn("Custo", format="R$ %.2f"),
                    "total":      st.column_config.NumberColumn("Total", format="R$ %.2f"),
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)



    # ── DASHBOARD ────────────────────────────────────────
    def tela_dashboard():
        from datetime import timedelta

        st.markdown("""
        <style>
        .block-container { padding-top: 1.5rem !important; }
        .stDataFrame { border-radius: 12px !important; border: 1px solid #2A2624 !important; }
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
            border-bottom: 2px solid #2A2624 !important;
            gap: 4px !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: #1A1715 !important;
            border: 1px solid #2A2624 !important;
            border-radius: 10px 10px 0 0 !important;
            color: #8A7B72 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            padding: 8px 20px !important;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #E85D04, #C44D00) !important;
            border-color: #E85D04 !important;
            color: #fff !important;
        }
        .btn-periodo > div > button {
            background: #1A1715 !important;
            color: #8A7B72 !important;
            border: 1px solid #2A2624 !important;
            border-radius: 20px !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            height: 34px !important;
            padding: 0 14px !important;
            transition: all 0.15s !important;
        }
        .btn-periodo > div > button:hover {
            background: #2A2420 !important;
            color: #FFF8F0 !important;
            border-color: #554A40 !important;
        }
        .btn-periodo-ativo > div > button {
            background: rgba(232,93,4,0.15) !important;
            color: #E85D04 !important;
            border: 1px solid rgba(232,93,4,0.4) !important;
            border-radius: 20px !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            height: 34px !important;
            padding: 0 14px !important;
        }
        .btn-export > div > button {
            background: #1A1715 !important;
            color: #FFF8F0 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            height: 40px !important;
        }
        .stDateInput > div > div > input {
            background: #1A1715 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            color: #FFF8F0 !important;
            font-size: 13px !important;
        }
        .stDateInput label { font-size:12px !important; color:#8A7B72 !important; }
        </style>
        """, unsafe_allow_html=True)

        # ── HEADER ──────────────────────────────────────────────────────
        col_h, col_btn = st.columns([8, 2])
        with col_h:
            st.markdown(f"""
            <div style="margin-bottom:18px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <h1 style="font-family:'Bebas Neue',sans-serif;font-size:42px;color:#FFF8F0;letter-spacing:1px;margin:0;line-height:1;">DASHBOARD GERENCIAL</h1>
                    <span style="background:#1A2240;color:#7BA1F2;border:1px solid #2A3A60;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:5px 12px;border-radius:20px;">VISÃO GERAL</span>
                </div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;color:#554A40;margin-top:6px;font-style:italic;">Resumo executivo, histórico e inventário por data</div>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-export">', unsafe_allow_html=True)
            if st.button("↻ Atualizar", use_container_width=True, key="dash_refresh"):
                _ler_cached.clear()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── CARREGA DADOS BASE ───────────────────────────────────────────
        hoje      = date.today()
        est_raw   = listar_estoque()
        itens_df  = listar_itens()
        movs_all  = listar_movimentos(limit=2000)

        if est_raw.empty:
            st.info("Sem dados de estoque.")
            return

        # Merge estoque + itens
        if not itens_df.empty:
            cols_m = [c for c in ["id_item","estoque_minimo","estoque_maximo","custo_unitario"] if c in itens_df.columns]
            est = est_raw.merge(itens_df[cols_m], on="id_item", how="left")
        else:
            est = est_raw.copy()

        est["s"]  = pd.to_numeric(est["saldo_atual"],     errors="coerce").fillna(0)
        est["mn"] = pd.to_numeric(est.get("estoque_minimo",  0), errors="coerce").fillna(0)
        est["cu"] = pd.to_numeric(est.get("custo_unitario",  0), errors="coerce").fillna(0)
        est["vl"] = est["s"] * est["cu"]
        est["st"] = est.apply(lambda r: status_item(r["s"], r["mn"]), axis=1)
        custo_dict = est.set_index("id_item")["cu"].to_dict()

        n_total   = len(est)
        n_zerado  = int(est["st"].str.contains("Zerado").sum())
        n_critico = int(est["st"].str.contains("Baixo").sum())
        n_ok      = int(est["st"].str.contains("Normal").sum())
        vl_total  = est["vl"].sum()

        # ── ABAS ────────────────────────────────────────────────────────
        aba_geral, aba_hist, aba_tm = st.tabs(["📊 Visão Geral", "📈 Histórico", "🕐 Inventário por Data"])

        # ════════════════════════════════════════════════════════════════
        # ABA 1 — VISÃO GERAL
        # ════════════════════════════════════════════════════════════════
        with aba_geral:

            # ── KPI CARDS ───────────────────────────────────────────────
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:14px;margin:18px 0 24px;">
                <div style="background:#1A1715;border:1px solid #2A2624;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;">
                    <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#7BA1F2,#A987D9);border-radius:0 0 14px 14px;"></div>
                    <div style="font-size:18px;margin-bottom:8px;">📦</div>
                    <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Total de Itens</div>
                    <div style="font-size:38px;font-weight:800;color:#FFF8F0;line-height:1;">{n_total}</div>
                    <div style="font-size:11px;color:#554A40;margin-top:4px;">cadastrados no sistema</div>
                </div>
                <div style="background:#1A1715;border:1px solid #2A2624;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;">
                    <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:#EF4444;border-radius:0 0 14px 14px;"></div>
                    <div style="font-size:18px;margin-bottom:8px;">🔴</div>
                    <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Zerados</div>
                    <div style="font-size:38px;font-weight:800;color:#EF4444;line-height:1;">{n_zerado}</div>
                    <div style="font-size:11px;color:#554A40;margin-top:4px;">saldo = 0</div>
                </div>
                <div style="background:#1A1715;border:1px solid #2A2624;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;">
                    <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:#D99F2A;border-radius:0 0 14px 14px;"></div>
                    <div style="font-size:18px;margin-bottom:8px;">⚠️</div>
                    <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Críticos</div>
                    <div style="font-size:38px;font-weight:800;color:#D99F2A;line-height:1;">{n_critico}</div>
                    <div style="font-size:11px;color:#554A40;margin-top:4px;">abaixo do mínimo</div>
                </div>
                <div style="background:#1A1715;border:1px solid #2A2624;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;">
                    <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:#2ED297;border-radius:0 0 14px 14px;"></div>
                    <div style="font-size:18px;margin-bottom:8px;">✅</div>
                    <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">OK</div>
                    <div style="font-size:38px;font-weight:800;color:#2ED297;line-height:1;">{n_ok}</div>
                    <div style="font-size:11px;color:#554A40;margin-top:4px;">dentro do mínimo</div>
                </div>
                <div style="background:#1A1715;border:1px solid #2A2624;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;">
                    <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:#E85D04;border-radius:0 0 14px 14px;"></div>
                    <div style="font-size:18px;margin-bottom:8px;">💰</div>
                    <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Valor Total</div>
                    <div style="font-size:26px;font-weight:800;color:#E85D04;line-height:1;">R$ {vl_total:,.2f}</div>
                    <div style="font-size:11px;color:#554A40;margin-top:4px;">estoque valorizado</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── FILTROS RÁPIDOS DE PERÍODO ──────────────────────────────
            st.markdown("""
            <div style="font-size:12px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:10px;">
                📅 Período de análise
            </div>
            """, unsafe_allow_html=True)

            PERIODOS = [
                ("Hoje",          0,  0),
                ("Ontem",         1,  1),
                ("7 dias",        6,  0),
                ("Mês atual",    -1,  0),   # -1 = flag especial
                ("Mês anterior", -2,  0),   # -2 = flag especial
            ]
            if "dash_periodo" not in st.session_state:
                st.session_state["dash_periodo"] = "7 dias"

            cols_per = st.columns([1,1,1,1,1,1.5])
            labels   = [p[0] for p in PERIODOS]
            for i, (lbl, _, _) in enumerate(PERIODOS):
                ativo = st.session_state["dash_periodo"] == lbl
                css   = "btn-periodo-ativo" if ativo else "btn-periodo"
                with cols_per[i]:
                    st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
                    if st.button(lbl, key=f"per_{lbl}", use_container_width=True):
                        st.session_state["dash_periodo"] = lbl
                        st.session_state.pop("dash_dt_ini", None)
                        st.session_state.pop("dash_dt_fim", None)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            with cols_per[5]:
                ativo = st.session_state["dash_periodo"] == "custom"
                css   = "btn-periodo-ativo" if ativo else "btn-periodo"
                st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
                if st.button("📅 Personalizado", key="per_custom", use_container_width=True):
                    st.session_state["dash_periodo"] = "custom"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Calcula intervalo
            periodo_sel = st.session_state.get("dash_periodo", "7 dias")
            if periodo_sel == "custom":
                cc1, cc2 = st.columns(2)
                with cc1:
                    dt_ini = st.date_input("De", value=hoje - timedelta(days=6), max_value=hoje, key="dash_dt_ini")
                with cc2:
                    dt_fim = st.date_input("Até", value=hoje, max_value=hoje, key="dash_dt_fim")
            elif periodo_sel == "Hoje":
                dt_ini = dt_fim = hoje
            elif periodo_sel == "Ontem":
                dt_ini = dt_fim = hoje - timedelta(days=1)
            elif periodo_sel == "7 dias":
                dt_ini = hoje - timedelta(days=6); dt_fim = hoje
            elif periodo_sel == "Mês atual":
                dt_ini = hoje.replace(day=1); dt_fim = hoje
            elif periodo_sel == "Mês anterior":
                primeiro_atual = hoje.replace(day=1)
                dt_fim = primeiro_atual - timedelta(days=1)
                dt_ini = dt_fim.replace(day=1)
            else:
                dt_ini = hoje - timedelta(days=6); dt_fim = hoje

            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

            # Seletor de produto para CMV individual
            opcoes_itens = ["Todos"]
            if not itens_df.empty:
                opcoes_itens += sorted(itens_df["nome"].dropna().unique().tolist())
            
            c_prod_sel = st.selectbox(
                "🔍 Filtrar CMV por Produto Específico", 
                opcoes_itens, 
                index=0, 
                key="dash_cmv_produto"
            )

            # Filtra movimentos pelo período
            movs_per = pd.DataFrame()
            if not movs_all.empty:
                movs_per = movs_all[
                    (movs_all["timestamp"].dt.date >= dt_ini) &
                    (movs_all["timestamp"].dt.date <= dt_fim)
                ]

            # ── CMV DO PERÍODO ─────────────────────────────────────────
            valor_compras = 0.0; valor_saidas = 0.0
            
            if c_prod_sel == "Todos":
                # Lógica Global original
                if not movs_per.empty:
                    ent = movs_per[movs_per["tipo"] == "ENTRADA"]
                    sai = movs_per[movs_per["tipo"] == "SAÍDA"]
                    if not ent.empty:
                        valor_compras = sum(float(r["quantidade"]) * custo_dict.get(r["id_item"], 0) for _, r in ent.iterrows())
                    if not sai.empty:
                        valor_saidas  = sum(float(r["quantidade"]) * custo_dict.get(r["id_item"], 0) for _, r in sai.iterrows())
                estoque_final   = vl_total
                estoque_inicial = estoque_final - valor_compras + valor_saidas
                cmv             = estoque_inicial + valor_compras - estoque_final
                label_analise   = "Custo de Mercadoria Vendida (Geral)"
            else:
                # Filtrar pelo item selecionado
                item_row = itens_df[itens_df["nome"] == c_prod_sel]
                if not item_row.empty:
                    id_item_sel = item_row.iloc[0]["id_item"]
                    custo_item = custo_dict.get(id_item_sel, 0.0)
                    
                    # Movimentos filtrados
                    movs_item_per = movs_per[movs_per["id_item"] == id_item_sel] if not movs_per.empty else pd.DataFrame()
                    if not movs_item_per.empty:
                        ent_item = movs_item_per[movs_item_per["tipo"] == "ENTRADA"]
                        sai_item = movs_item_per[movs_item_per["tipo"] == "SAÍDA"]
                        if not ent_item.empty:
                            valor_compras = sum(float(r["quantidade"]) * custo_item for _, r in ent_item.iterrows())
                        if not sai_item.empty:
                            valor_saidas  = sum(float(r["quantidade"]) * custo_item for _, r in sai_item.iterrows())
                    
                    # Saldo final do item
                    est_item = est[est["id_item"] == id_item_sel]
                    estoque_final = float(est_item.iloc[0]["vl"]) if not est_item.empty else 0.0
                    
                    estoque_inicial = estoque_final - valor_compras + valor_saidas
                    cmv             = estoque_inicial + valor_compras - estoque_final
                else:
                    estoque_final = 0.0
                    estoque_inicial = 0.0
                    cmv = 0.0
                label_analise = f"Custo de Mercadoria Vendida — {c_prod_sel}"

            label_per       = f"{dt_ini.strftime('%d/%m')} → {dt_fim.strftime('%d/%m/%Y')}"

            st.markdown(f"""
            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:14px;padding:20px 24px;margin-bottom:20px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="width:32px;height:32px;background:#1A2240;border:1px solid #2A3A60;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px;">📊</div>
                        <div>
                            <div style="font-size:14px;font-weight:700;color:#FFF8F0;">Análise de CMV</div>
                            <div style="font-size:12px;color:#554A40;margin-top:2px;">{label_analise} — {label_per}</div>
                        </div>
                    </div>
                    <span style="background:#1A2240;color:#7BA1F2;border:1px solid #2A3A60;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:4px 12px;border-radius:20px;">{periodo_sel.upper()}</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 30px 1fr 30px 1fr 30px 1fr;align-items:center;gap:6px;">
                    <div style="background:#141210;border:1px solid #2A2624;border-radius:10px;padding:14px;">
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">📋 Est. Inicial</div>
                        <div style="font-size:20px;font-weight:800;color:#FFF8F0;">R$ {estoque_inicial:,.2f}</div>
                    </div>
                    <div style="text-align:center;font-size:18px;color:#554A40;font-weight:700;">+</div>
                    <div style="background:#141210;border:1px solid #2A2624;border-radius:10px;padding:14px;">
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">📥 Compras</div>
                        <div style="font-size:20px;font-weight:800;color:#2ED297;">R$ {valor_compras:,.2f}</div>
                    </div>
                    <div style="text-align:center;font-size:18px;color:#554A40;font-weight:700;">–</div>
                    <div style="background:#141210;border:1px solid #2A2624;border-radius:10px;padding:14px;">
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">📦 Est. Final</div>
                        <div style="font-size:20px;font-weight:800;color:#FFF8F0;">R$ {estoque_final:,.2f}</div>
                    </div>
                    <div style="text-align:center;font-size:18px;color:#554A40;font-weight:700;">=</div>
                    <div style="background:#0F2A1B;border:1px solid #164028;border-radius:10px;padding:14px;">
                        <div style="font-size:10px;color:#2ED297;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">✅ CMV</div>
                        <div style="font-size:20px;font-weight:800;color:#2ED297;">R$ {cmv:,.2f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── ALERTAS + MOVIMENTOS DO PERÍODO ────────────────────────
            import html as _html
            col_left, col_right = st.columns(2)

            with col_left:
                al   = est[est["st"].str.contains("Zerado|Baixo")]
                n_al = len(al)
                # Renderiza header do card
                st.markdown(f"""
                <div style="background:#1A1715;border-radius:12px;border:1px solid #2A2624;overflow:hidden;margin-bottom:0;">
                    <div style="padding:14px 18px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #2A2624;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:30px;height:30px;background:#3B1219;border:1px solid #5A1A22;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;">🚨</div>
                            <div>
                                <div style="font-size:13px;font-weight:700;color:#FFF8F0;">Precisam de ação</div>
                                <div style="font-size:11px;color:#554A40;">Zerados e abaixo do mínimo</div>
                            </div>
                        </div>
                        <span style="background:#EF4444;color:#fff;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;">{n_al}</span>
                    </div>
                """, unsafe_allow_html=True)
                # Renderiza itens individualmente para evitar limite de tamanho do st.markdown
                if al.empty:
                    st.markdown('<div style="padding:20px;text-align:center;font-size:13px;color:#2ED297;">✅ Todos os itens estão OK!</div></div>', unsafe_allow_html=True)
                else:
                    rows_al = []
                    for _, r in al.iterrows():
                        is_z  = "Zerado" in r["st"]
                        dot   = "#EF4444" if is_z else "#D99F2A"
                        bbg   = "#3B1219" if is_z else "#2A1F08"
                        bbrd  = "#5A1A22" if is_z else "#4A3510"
                        btxt  = "#EF4444" if is_z else "#D99F2A"
                        lbl   = "ZERADO" if is_z else "BAIXO"
                        nome_safe = _html.escape(str(r['nome']))
                        rows_al.append(f"""
                        <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 18px;border-bottom:1px solid #1F1C1A;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <div style="width:7px;height:7px;background:{dot};border-radius:50%;flex-shrink:0;"></div>
                                <span style="font-size:13px;color:#FFF8F0;">{nome_safe}</span>
                            </div>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="background:{bbg};color:{btxt};border:1px solid {bbrd};font-size:10px;font-weight:700;padding:2px 7px;border-radius:5px;">{lbl}</span>
                                <span style="font-size:11px;color:#8A7B72;">{r['s']:.0f}/{r['mn']:.0f}</span>
                            </div>
                        </div>""")
                    # Renderiza em blocos de 30 itens para evitar limite de markdown
                    CHUNK = 30
                    st.markdown('<div style="max-height:300px;overflow-y:auto;border-top:none;">', unsafe_allow_html=True)
                    for i in range(0, len(rows_al), CHUNK):
                        st.markdown("".join(rows_al[i:i+CHUNK]), unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)

            with col_right:
                n_mov = len(movs_per)
                # Renderiza header do card
                st.markdown(f"""
                <div style="background:#1A1715;border-radius:12px;border:1px solid #2A2624;overflow:hidden;margin-bottom:0;">
                    <div style="padding:14px 18px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #2A2624;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:30px;height:30px;background:#0F2A1B;border:1px solid #164028;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;">📋</div>
                            <div>
                                <div style="font-size:13px;font-weight:700;color:#FFF8F0;">Movimentos — {label_per}</div>
                                <div style="font-size:11px;color:#554A40;">Movimentações do período</div>
                            </div>
                        </div>
                        <span style="background:#2ED297;color:#0A1F14;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;">{n_mov}</span>
                    </div>
                """, unsafe_allow_html=True)
                # Renderiza itens individualmente
                if movs_per.empty:
                    st.markdown(f'<div style="padding:20px;text-align:center;font-size:13px;color:#554A40;">Nenhum movimento em {label_per}.</div></div>', unsafe_allow_html=True)
                else:
                    rows_mv = []
                    for _, m in movs_per.head(20).iterrows():
                        tipo = m["tipo"]
                        ico  = "📥" if tipo == "ENTRADA" else ("📤" if tipo == "SAÍDA" else "🔧")
                        bg   = "#0F2A1B" if tipo == "ENTRADA" else ("#2A1210" if tipo == "SAÍDA" else "#2A200B")
                        brd  = "#164028" if tipo == "ENTRADA" else ("#4A1A1A" if tipo == "SAÍDA" else "#4A3510")
                        hora = m["timestamp"].strftime("%d/%m %H:%M")
                        qtd  = float(m["quantidade"])
                        nome_mv  = _html.escape(str(m['nome_item']))
                        oper_mv  = _html.escape(str(m['operador']))
                        rows_mv.append(f"""
                        <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 18px;border-bottom:1px solid #1F1C1A;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <div style="width:28px;height:28px;background:{bg};border:1px solid {brd};border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:13px;">{ico}</div>
                                <div>
                                    <div style="font-size:12px;font-weight:500;color:#FFF8F0;">{nome_mv}</div>
                                    <div style="font-size:10px;color:#554A40;">{oper_mv}</div>
                                </div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:12px;color:#8A7B72;">{qtd:.0f}</div>
                                <div style="font-size:10px;color:#554A40;">{hora}</div>
                            </div>
                        </div>"""
                        )
                    st.markdown('<div style="max-height:300px;overflow-y:auto;">', unsafe_allow_html=True)
                    st.markdown("".join(rows_mv), unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════
        # ABA 2 — HISTÓRICO
        # ════════════════════════════════════════════════════════════════
        with aba_hist:
            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

            if movs_all.empty:
                st.info("Nenhum movimento registrado ainda.")
            else:
                # ── FILTROS DE PERÍODO INDEPENDENTES DA ABA HISTÓRICO ──
                st.markdown("""
                <div style="font-size:12px;font-weight:700;color:#8A7B72;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:10px;">
                    📅 Período do histórico
                </div>
                """, unsafe_allow_html=True)

                PERIODOS_H = [
                    ("Hoje",          0,  0),
                    ("Ontem",         1,  1),
                    ("7 dias",        6,  0),
                    ("Mês atual",    -1,  0),
                    ("Mês anterior", -2,  0),
                ]
                if "hist_periodo" not in st.session_state:
                    st.session_state["hist_periodo"] = "7 dias"

                cols_hper = st.columns([1,1,1,1,1,1.5])
                for i, (lbl, _, _) in enumerate(PERIODOS_H):
                    ativo = st.session_state["hist_periodo"] == lbl
                    css   = "btn-periodo-ativo" if ativo else "btn-periodo"
                    with cols_hper[i]:
                        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
                        if st.button(lbl, key=f"hper_{lbl}", use_container_width=True):
                            st.session_state["hist_periodo"] = lbl
                            st.session_state.pop("hist_dt_ini", None)
                            st.session_state.pop("hist_dt_fim", None)
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

                with cols_hper[5]:
                    ativo = st.session_state["hist_periodo"] == "custom"
                    css   = "btn-periodo-ativo" if ativo else "btn-periodo"
                    st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
                    if st.button("📅 Personalizado", key="hper_custom", use_container_width=True):
                        st.session_state["hist_periodo"] = "custom"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                # Calcula intervalo do histórico
                hperiodo_sel = st.session_state.get("hist_periodo", "7 dias")
                if hperiodo_sel == "custom":
                    hc1, hc2 = st.columns(2)
                    with hc1:
                        hdt_ini = st.date_input("De", value=hoje - timedelta(days=6), max_value=hoje, key="hist_dt_ini")
                    with hc2:
                        hdt_fim = st.date_input("Até", value=hoje, max_value=hoje, key="hist_dt_fim")
                elif hperiodo_sel == "Hoje":
                    hdt_ini = hdt_fim = hoje
                elif hperiodo_sel == "Ontem":
                    hdt_ini = hdt_fim = hoje - timedelta(days=1)
                elif hperiodo_sel == "7 dias":
                    hdt_ini = hoje - timedelta(days=6); hdt_fim = hoje
                elif hperiodo_sel == "Mês atual":
                    hdt_ini = hoje.replace(day=1); hdt_fim = hoje
                elif hperiodo_sel == "Mês anterior":
                    primeiro_atual = hoje.replace(day=1)
                    hdt_fim = primeiro_atual - timedelta(days=1)
                    hdt_ini = hdt_fim.replace(day=1)
                else:
                    hdt_ini = hoje - timedelta(days=6); hdt_fim = hoje

                hlabel_per = f"{hdt_ini.strftime('%d/%m')} → {hdt_fim.strftime('%d/%m/%Y')}"
                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

                # Filtra movimentos pelo período do histórico
                movs_h = movs_all[
                    (movs_all["timestamp"].dt.date >= hdt_ini) &
                    (movs_all["timestamp"].dt.date <= hdt_fim)
                ]

                # ── KPIs DO PERÍODO ─────────────────────────────────────
                n_ent_h = int((movs_h["tipo"] == "ENTRADA").sum()) if not movs_h.empty else 0
                n_sai_h = int((movs_h["tipo"] == "SAÍDA").sum()) if not movs_h.empty else 0
                n_aju_h = int((movs_h["tipo"] == "AJUSTE").sum()) if not movs_h.empty else 0
                n_mov_h = len(movs_h)
                val_ent = sum(float(r["quantidade"]) * custo_dict.get(r["id_item"], 0) for _, r in movs_h[movs_h["tipo"]=="ENTRADA"].iterrows()) if not movs_h.empty else 0
                val_sai = sum(float(r["quantidade"]) * custo_dict.get(r["id_item"], 0) for _, r in movs_h[movs_h["tipo"]=="SAÍDA"].iterrows()) if not movs_h.empty else 0

                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-bottom:18px;">
                    <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:14px 18px;">
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">📋 Total de movimentos</div>
                        <div style="font-size:26px;font-weight:800;color:#FFF8F0;">{n_mov_h}</div>
                        <div style="font-size:11px;color:#554A40;margin-top:2px;">{hlabel_per}</div>
                    </div>
                    <div style="background:#1A1715;border:1px solid #164028;border-radius:12px;padding:14px 18px;">
                        <div style="font-size:10px;color:#2ED297;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">📥 Entradas</div>
                        <div style="font-size:26px;font-weight:800;color:#2ED297;">{n_ent_h}</div>
                        <div style="font-size:11px;color:#554A40;margin-top:2px;">R$ {val_ent:,.2f}</div>
                    </div>
                    <div style="background:#1A1715;border:1px solid #4A1A1A;border-radius:12px;padding:14px 18px;">
                        <div style="font-size:10px;color:#E85D04;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">📤 Saídas</div>
                        <div style="font-size:26px;font-weight:800;color:#E85D04;">{n_sai_h}</div>
                        <div style="font-size:11px;color:#554A40;margin-top:2px;">R$ {val_sai:,.2f}</div>
                    </div>
                    <div style="background:#1A1715;border:1px solid #4A3510;border-radius:12px;padding:14px 18px;">
                        <div style="font-size:10px;color:#D99F2A;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">🔧 Ajustes</div>
                        <div style="font-size:26px;font-weight:800;color:#D99F2A;">{n_aju_h}</div>
                        <div style="font-size:11px;color:#554A40;margin-top:2px;">inventário manual</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── GRÁFICO ENTRADAS × SAÍDAS POR DIA ──────────────────
                card_header = f"""<div style="background:#1A1715;border:1px solid #2A2624;border-radius:14px;padding:20px 24px;margin-bottom:20px;">
<div style="font-size:14px;font-weight:700;color:#FFF8F0;margin-bottom:4px;">📊 Entradas × Saídas por dia</div>
<div style="font-size:12px;color:#554A40;margin-bottom:16px;">Comparativo diário de movimentações — {hlabel_per}</div>"""

                if movs_h.empty:
                    card_html = card_header + '<div style="padding:20px;text-align:center;color:#554A40;font-size:13px;">Sem movimentos no período.</div></div>'
                else:
                    dias = pd.date_range(hdt_ini, hdt_fim).date.tolist()
                    ent_por_dia = movs_h[movs_h["tipo"]=="ENTRADA"].groupby(movs_h["timestamp"].dt.date)["quantidade"].apply(lambda x: x.astype(float).sum()).to_dict()
                    sai_por_dia = movs_h[movs_h["tipo"]=="SAÍDA"].groupby(movs_h["timestamp"].dt.date)["quantidade"].apply(lambda x: x.astype(float).sum()).to_dict()

                    max_val = max([max(ent_por_dia.values() or [1]), max(sai_por_dia.values() or [1])], default=1)
                    BAR_H   = 120  # altura máx px da barra

                    bars_html = '<div style="display:flex;align-items:flex-end;gap:6px;height:160px;overflow-x:auto;padding-bottom:4px;">'
                    for d in dias:
                        e = ent_por_dia.get(d, 0)
                        s = sai_por_dia.get(d, 0)
                        h_e = int(e / max_val * BAR_H) if max_val > 0 else 0
                        h_s = int(s / max_val * BAR_H) if max_val > 0 else 0
                        lbl = d.strftime("%d/%m")
                        bars_html += f"""<div style="display:flex;flex-direction:column;align-items:center;gap:2px;flex:1;min-width:36px;">
<div style="display:flex;align-items:flex-end;gap:2px;height:{BAR_H}px;">
<div title="Entrada: {e:.0f}" style="width:14px;height:{h_e}px;background:linear-gradient(180deg,#2ED297,#1A9E72);border-radius:3px 3px 0 0;min-height:2px;"></div>
<div title="Saída: {s:.0f}" style="width:14px;height:{h_s}px;background:linear-gradient(180deg,#E85D04,#C44D00);border-radius:3px 3px 0 0;min-height:2px;"></div>
</div>
<div style="font-size:9px;color:#554A40;white-space:nowrap;">{lbl}</div>
</div>"""
                    bars_html += '</div>'
                    legenda = """<div style="display:flex;gap:16px;margin-top:10px;">
<div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#8A7B72;">
<div style="width:10px;height:10px;background:#2ED297;border-radius:2px;"></div> Entradas
</div>
<div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#8A7B72;">
<div style="width:10px;height:10px;background:#E85D04;border-radius:2px;"></div> Saídas
</div>
</div>"""
                    card_html = card_header + bars_html + legenda + "</div>"

                st.markdown(card_html, unsafe_allow_html=True)

                # ── TOP 10 MAIS MOVIMENTADOS ────────────────────────────
                col_t10, col_ajust = st.columns(2)

                with col_t10:
                    st.markdown("""
                    <div style="font-size:13px;font-weight:700;color:#FFF8F0;margin-bottom:10px;">🏆 Top 10 — Mais Movimentados</div>
                    """, unsafe_allow_html=True)
                    if movs_h.empty:
                        st.info("Sem dados no período.")
                    else:
                        saidas_h = movs_h[movs_h["tipo"] == "SAÍDA"]
                        if saidas_h.empty:
                            st.info("Sem saídas no período.")
                        else:
                            top = (saidas_h.groupby("nome_item")["quantidade"]
                                   .apply(lambda x: x.astype(float).sum())
                                   .sort_values(ascending=False)
                                   .head(10)
                                   .reset_index())
                            top.columns = ["Produto", "Total Saído"]
                            max_v = top["Total Saído"].max() or 1

                            for i, row in top.iterrows():
                                pct = row["Total Saído"] / max_v * 100
                                medal = ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"
                                st.markdown(f"""
                                <div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #1F1C1A;">
                                    <span style="font-size:14px;width:28px;text-align:center;">{medal}</span>
                                    <div style="flex:1;">
                                        <div style="font-size:12px;color:#FFF8F0;font-weight:500;">{row['Produto']}</div>
                                        <div style="height:4px;background:#2A2624;border-radius:2px;margin-top:4px;">
                                            <div style="height:4px;width:{pct:.0f}%;background:linear-gradient(90deg,#E85D04,#D99F2A);border-radius:2px;"></div>
                                        </div>
                                    </div>
                                    <span style="font-size:12px;color:#E85D04;font-weight:700;white-space:nowrap;">{row['Total Saído']:.0f}</span>
                                </div>
                                """, unsafe_allow_html=True)

                with col_ajust:
                    st.markdown("""
                    <div style="font-size:13px;font-weight:700;color:#FFF8F0;margin-bottom:10px;">🔧 Auditoria de Ajustes</div>
                    """, unsafe_allow_html=True)
                    ajustes = movs_h[movs_h["tipo"] == "AJUSTE"] if not movs_h.empty else pd.DataFrame()
                    if ajustes.empty:
                        st.markdown('<div style="padding:16px;background:#1A1715;border:1px solid #2A2624;border-radius:10px;text-align:center;font-size:12px;color:#554A40;">Nenhum ajuste no período ✅</div>', unsafe_allow_html=True)
                    else:
                        for _, aj in ajustes.iterrows():
                            qtd = float(aj["quantidade"])
                            st.markdown(f"""
                            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:8px;padding:10px 14px;margin-bottom:6px;">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <span style="font-size:12px;font-weight:600;color:#FFF8F0;">{aj['nome_item']}</span>
                                    <span style="font-size:11px;color:#D99F2A;font-weight:700;">→ {qtd:.0f}</span>
                                </div>
                                <div style="font-size:10px;color:#554A40;margin-top:3px;">{aj['operador']} · {aj['timestamp'].strftime('%d/%m/%Y %H:%M')} · {aj.get('obs','') or aj.get('motivo','')}</div>
                            </div>
                            """, unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════
        # ABA 3 — INVENTÁRIO POR DATA (TIME MACHINE)
        # ════════════════════════════════════════════════════════════════
        with aba_tm:
            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="background:linear-gradient(135deg,#1A1A2E,#16213E);border:1px solid #2A3A60;border-radius:14px;padding:20px 24px;margin-bottom:20px;">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                    <span style="font-size:24px;">🕐</span>
                    <div>
                        <div style="font-size:16px;font-weight:700;color:#7BA1F2;">Inventário por Data</div>
                        <div style="font-size:12px;color:#4A6A9A;margin-top:2px;">Reconstrói o saldo de cada item como estava em qualquer data passada</div>
                    </div>
                </div>
                <div style="font-size:11px;color:#4A6A9A;background:rgba(123,161,242,0.08);border:1px solid #2A3A60;border-radius:8px;padding:8px 12px;">
                    ⚠️ <strong style="color:#7BA1F2;">Nota:</strong> A reconstrução é baseada nos movimentos registrados. Ajustes manuais podem causar pequenas variações.
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_tm1, col_tm2, col_tm3 = st.columns([2, 1, 1])
            with col_tm1:
                data_tm = st.date_input(
                    "📅 Selecione a data para ver o inventário",
                    value=hoje - timedelta(days=1),
                    max_value=hoje - timedelta(days=1),
                    key="tm_data",
                )
            with col_tm2:
                st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
                rodar = st.button("🕐 Ver inventário", use_container_width=True, key="tm_rodar")
            with col_tm3:
                st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
                st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

            if rodar or st.session_state.get("tm_resultado") is not None:
                if rodar:
                    st.session_state["tm_data_usada"] = data_tm

                data_ref = st.session_state.get("tm_data_usada", data_tm)

                # Reconstrói saldo: pega saldo atual e desfaz movimentos APÓS data_ref
                movs_depois = pd.DataFrame()
                if not movs_all.empty:
                    movs_depois = movs_all[movs_all["timestamp"].dt.date > data_ref]

                # Deltas a reverter por item
                delta_por_item = {}
                if not movs_depois.empty:
                    for _, mv in movs_depois.iterrows():
                        iid  = mv["id_item"]
                        qtd  = float(mv.get("quantidade", 0) or 0)
                        tipo = mv["tipo"]
                        if tipo == "ENTRADA":
                            delta_por_item[iid] = delta_por_item.get(iid, 0) - qtd
                        elif tipo == "SAÍDA":
                            delta_por_item[iid] = delta_por_item.get(iid, 0) + qtd
                        # AJUSTE: pula — não é reversível de forma confiável

                rows_tm = []
                for _, r in est.iterrows():
                    iid      = r["id_item"]
                    s_atual  = float(r["s"])
                    delta    = delta_por_item.get(iid, 0)
                    s_hist   = max(0, s_atual + delta)
                    diff     = s_hist - s_atual
                    diff_txt = (f"▲ +{diff:.0f}" if diff > 0 else (f"▼ {diff:.0f}" if diff < 0 else "—"))
                    diff_cor = "#2ED297" if diff > 0 else ("#EF4444" if diff < 0 else "#554A40")
                    vl_hist  = s_hist * float(r["cu"])
                    rows_tm.append({
                        "Status":    status_item(s_hist, float(r["mn"])),
                        "Código":    iid,
                        "Produto":   r["nome"],
                        "Categoria": r.get("categoria",""),
                        "Saldo em": round(s_hist, 2),
                        "Atual":    round(s_atual, 2),
                        "_diff_txt": diff_txt,
                        "_diff_cor": diff_cor,
                        "Mínimo":   round(float(r["mn"]), 2),
                        "Valor R$": round(vl_hist, 2),
                    })

                df_tm = pd.DataFrame(rows_tm)
                vl_hist_total = df_tm["Valor R$"].sum()
                n_zer_h = int(df_tm["Status"].str.contains("Zerado").sum())
                n_bai_h = int(df_tm["Status"].str.contains("Baixo").sum())

                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin:16px 0;">
                    <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:14px 18px;">
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">📅 Data consultada</div>
                        <div style="font-size:20px;font-weight:800;color:#7BA1F2;">{data_ref.strftime('%d/%m/%Y')}</div>
                    </div>
                    <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:14px 18px;">
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">💰 Valor do estoque</div>
                        <div style="font-size:20px;font-weight:800;color:#E85D04;">R$ {vl_hist_total:,.2f}</div>
                    </div>
                    <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:14px 18px;">
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">🔴 Zerados nessa data</div>
                        <div style="font-size:20px;font-weight:800;color:#EF4444;">{n_zer_h}</div>
                    </div>
                    <div style="background:#1A1715;border:1px solid #2A2624;border-radius:12px;padding:14px 18px;">
                        <div style="font-size:10px;color:#8A7B72;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">⚠️ Críticos nessa data</div>
                        <div style="font-size:20px;font-weight:800;color:#D99F2A;">{n_bai_h}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Tabela com diff
                df_show = df_tm[["Status","Código","Produto","Categoria","Saldo em","Atual","Mínimo","Valor R$"]].copy()
                df_show.rename(columns={"Saldo em": f"Saldo {data_ref.strftime('%d/%m')}"}, inplace=True)

                st.markdown('<div style="border-radius:12px;overflow:hidden;border:1px solid #2A2624;">', unsafe_allow_html=True)
                st.dataframe(
                    df_show,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        f"Saldo {data_ref.strftime('%d/%m')}": st.column_config.NumberColumn(format="%.0f"),
                        "Atual":    st.column_config.NumberColumn("Saldo Atual", format="%.0f"),
                        "Mínimo":   st.column_config.NumberColumn(format="%.0f"),
                        "Valor R$": st.column_config.NumberColumn(format="R$ %.2f"),
                    }
                )
                st.markdown('</div>', unsafe_allow_html=True)

                # Export CSV
                csv_tm = df_show.to_csv(index=False, sep=";").encode("utf-8-sig")
                st.download_button(
                    f"⬇ Exportar snapshot de {data_ref.strftime('%d/%m/%Y')} como CSV",
                    csv_tm,
                    f"inventario_{data_ref.strftime('%Y%m%d')}.csv",
                    "text/csv",
                    key="dl_tm_csv",
                    use_container_width=True,
                )

                st.session_state["tm_resultado"] = True




    # ── PLANEJAMENTO DE COMPRAS ──────────────────────────
    def tela_planejamento():
        from datetime import timedelta
        st.markdown("""
        <style>
        /* ── CSS Planejamento Dark Theme ── */
        .block-container { padding-top: 1.5rem !important; }

        input[type="text"],
        .stTextInput > div > div > input {
            background: #1A1715 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            color: #FFF8F0 !important;
            font-size: 14px !important;
            height: 44px !important;
        }
        .stTextInput label { display:none !important; }

        .btn-plan > div > button {
            background: #0F4A3A !important;
            color: #2ED297 !important;
            border: 1px solid #1A7A5A !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            height: 40px !important;
        }
        .btn-plan > div > button:hover {
            background: #144A2A !important;
        }
        .btn-plan-outline > div > button {
            background: #1A1715 !important;
            color: #FFF8F0 !important;
            border: 1px solid #332B25 !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            height: 40px !important;
        }
        .btn-pedido > div > button {
            background: rgba(232,93,4,0.12) !important;
            color: #E85D04 !important;
            border: 1px solid rgba(232,93,4,0.3) !important;
            border-radius: 6px !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            height: 34px !important;
            padding: 0 12px !important;
        }
        .btn-pedido > div > button:hover {
            background: rgba(232,93,4,0.25) !important;
        }
        .stDataFrame { border-radius: 12px !important; border: 1px solid #2A2624 !important; }
        </style>
        """, unsafe_allow_html=True)

        # ── HEADER ──────────────────────────────────────────────────────
        col_h, col_btns = st.columns([5.5, 4.5])
        hoje = date.today()
        
        with col_h:
            st.markdown("""
            <div style="margin-bottom: 8px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <h1 style="font-family:'Bebas Neue',sans-serif;font-size:42px;color:#FFF8F0;letter-spacing:1px;margin:0;line-height:1;">PLANEJAMENTO DE COMPRAS</h1>
                    <span style="background:#0F2A1B;color:#2ED297;border:1px solid #164028;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:5px 12px;border-radius:20px;">PREVISÃO INTELIGENTE</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c_date, c_window = st.columns(2)
            with c_date:
                data_plan = st.date_input(
                    "📅 Data do estoque de referência",
                    value=hoje,
                    max_value=hoje,
                    key="plan_data_ref"
                )
            with c_window:
                janela_dias = st.selectbox(
                    "🧮 Média de consumo baseada em",
                    options=[7, 15, 30, 45, 60, 90],
                    format_func=lambda x: f"Últimos {x} dias",
                    index=0,
                    key="plan_janela_dias"
                )
            
        with col_btns:
            st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)
            cb1, cb2, cb3 = st.columns(3)
            with cb1:
                st.markdown('<div class="btn-plan-outline">', unsafe_allow_html=True)
                export_csv_container = st.empty()
                st.markdown('</div>', unsafe_allow_html=True)
            with cb2:
                st.markdown('<div class="btn-plan-outline">', unsafe_allow_html=True)
                export_html_container = st.empty()
                st.markdown('</div>', unsafe_allow_html=True)
            with cb3:
                st.markdown('<div class="btn-plan">', unsafe_allow_html=True)
                if st.button("↻ Atualizar", use_container_width=True, key="ref_plan"):
                    _ler_cached.clear()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── DADOS ───────────────────────────────────────────────────────
        est   = listar_estoque()
        movs  = listar_movimentos(limit=10000)
        itens = listar_itens()
        forn  = listar_fornecedores()

        if est.empty:
            st.info("Sem dados de estoque.")
            return
 
        # ── RECONSTRUÇÃO DO ESTOQUE HISTÓRICO ───────────────────────────
        movs_for_calc = movs
        if data_plan < hoje:
            movs_all_reconstruct = listar_movimentos(limit=10000)
            movs_for_calc = movs_all_reconstruct
            movs_depois = pd.DataFrame()
            if not movs_all_reconstruct.empty:
                movs_depois = movs_all_reconstruct[movs_all_reconstruct["timestamp"].dt.date > data_plan]
            
            delta_por_item = {}
            if not movs_depois.empty:
                for _, mv in movs_depois.iterrows():
                    iid  = mv["id_item"]
                    qtd  = float(mv.get("quantidade", 0) or 0)
                    tipo = mv["tipo"]
                    if tipo == "ENTRADA":
                        delta_por_item[iid] = delta_por_item.get(iid, 0) - qtd
                    elif tipo == "SAÍDA":
                        delta_por_item[iid] = delta_por_item.get(iid, 0) + qtd
            
            reconstruido = []
            for _, r in est.iterrows():
                iid = r["id_item"]
                s_atual = float(pd.to_numeric(r.get("saldo_atual", 0), errors="coerce") or 0)
                delta = delta_por_item.get(iid, 0)
                s_hist = max(0.0, s_atual + delta)
                r_copy = r.copy()
                r_copy["saldo_atual"] = s_hist
                reconstruido.append(r_copy)
            est = pd.DataFrame(reconstruido)
 
        # ── CÁLCULO DO PLANEJAMENTO ─────────────────────────────────────
        # IMPORTANTE: consumo médio calculado sobre a janela selecionada
        JANELA_CONSUMO = janela_dias
 
        plano = []
        for _, item in itens.iterrows():
            if item.get("categoria") == "Ingrediente":
                continue
            id_item = item["id_item"]
            nome    = item["nome"]
            und     = item["unidade"]
            est_min = float(item.get("estoque_minimo") or 0)
            est_max = float(item.get("estoque_maximo") or 0)
            forn_id = item.get("fornecedor_id", "")

            est_row = est[est["id_item"] == id_item]
            saldo   = float(est_row.iloc[0]["saldo_atual"]) if not est_row.empty else 0.0

            forn_row  = forn[forn["id_fornecedor"] == forn_id]
            prazo     = int(forn_row.iloc[0]["prazo_dias"]) if not forn_row.empty else 7
            forn_nome = forn_row.iloc[0]["nome_curto"] if not forn_row.empty else "—"

            # Consumo médio — dividido por 7 (janela real de análise)
            if not movs_for_calc.empty:
                saidas_item = movs_for_calc[
                    (movs_for_calc["id_item"] == id_item) &
                    (movs_for_calc["tipo"] == "SAÍDA") &
                    (movs_for_calc["timestamp"] >= pd.Timestamp(data_plan - timedelta(days=JANELA_CONSUMO))) &
                    (movs_for_calc["timestamp"] < pd.Timestamp(data_plan + timedelta(days=1)))
                ]
                total_saida = saidas_item["quantidade"].astype(float).sum()
                consumo_dia = round(total_saida / JANELA_CONSUMO, 2)
            else:
                consumo_dia = 0.0

            dias_rest    = int(saldo / consumo_dia) if consumo_dia > 0 else 999
            data_ruptura = data_plan + timedelta(days=dias_rest) if dias_rest < 999 else None
            data_compra  = (data_ruptura - timedelta(days=prazo)) if data_ruptura else None
            data_chegada = (data_compra  + timedelta(days=prazo)) if data_compra  else None
            # Quantidade sugerida baseada no consumo durante o prazo + janela de consumo, menos saldo, com 20% de garantia
            qtd_sugerida = max(0, round((consumo_dia * (prazo + JANELA_CONSUMO) - saldo) * 1.20, 0)) if consumo_dia > 0 else 0
            
            # Se o saldo estiver abaixo do estoque mínimo (acabando), garante que a sugestão cubra a reposição + 20%
            if saldo < est_min:
                qtd_minima_reposicao = max(0, round((est_min - saldo) * 1.20, 0))
                qtd_sugerida = max(qtd_sugerida, qtd_minima_reposicao)

            # Lógica para avisar quando estiver acabando
            if saldo <= 0:
                status = "🔴 URGENTE"
                status_key = "urgente"
            elif est_min > 0 and saldo <= est_min:
                status = "🔴 URGENTE"
                status_key = "urgente"
            elif dias_rest <= prazo:
                status = "🔴 URGENTE"
                status_key = "urgente"
            elif dias_rest <= prazo * 2:
                status = "🟡 EM BREVE"
                status_key = "breve"
            else:
                status = "🟢 ESTÁVEL"
                status_key = "estavel"

            comprar_ate_txt = "Hoje" if data_compra and data_compra <= data_plan else (data_compra.strftime("%d/%m") if data_compra else "—")

            plano.append({
                "_status_key":  status_key,
                "_dias_rest":   dias_rest,
                "_data_compra": data_compra,
                "_qtd_sug":     qtd_sugerida,
                "_und":         und,
                "_saldo":       saldo,
                "_consumo":     consumo_dia,
                "_min":         est_min,
                "_prazo":       prazo,
                "_forn":        forn_nome,
                "_nome":        nome,
                "_id":          id_item,
                "Status":       status,
                "Produto":      nome,
                "Saldo":        saldo,
                "Mínimo":       est_min,
                "Consumo/dia":  f"{consumo_dia:.1f}/dia",
                "Prazo Fornec.": f"{prazo} dias",
                "Comprar até":  comprar_ate_txt,
                "Qtd sugerida": f"{qtd_sugerida:.0f} {und}" if qtd_sugerida > 0 else "—",
            })

        df_plano = pd.DataFrame(plano)
        urgentes = sum(1 for p in plano if p["_status_key"] == "urgente")
        breve    = sum(1 for p in plano if p["_status_key"] == "breve")
        estaveis = sum(1 for p in plano if p["_status_key"] == "estavel")
        total    = len(plano)

        # ── KPI CARDS ───────────────────────────────────────────────────
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px;margin-bottom:24px;">
            <div style="background:#1A1715;border:1px solid #3B1219;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;">
                <div style="position:absolute;top:12px;right:12px;background:#3B1219;color:#EF4444;border:1px solid #5A1A22;font-size:9px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:3px 8px;border-radius:10px;">URGENTE</div>
                <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:#EF4444;border-radius:0 0 14px 14px;"></div>
                <div style="font-size:20px;margin-bottom:8px;">🚨</div>
                <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Comprar JÁ</div>
                <div style="font-size:44px;font-weight:800;color:#EF4444;line-height:1;">{urgentes}</div>
                <div style="font-size:11px;color:#554A40;margin-top:4px;">zerados ou abaixo do mínimo</div>
            </div>
            <div style="background:#1A1715;border:1px solid #4A3510;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;">
                <div style="position:absolute;top:12px;right:12px;background:#2A200B;color:#D99F2A;border:1px solid #4A3510;font-size:9px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:3px 8px;border-radius:10px;">EM BREVE</div>
                <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:#D99F2A;border-radius:0 0 14px 14px;"></div>
                <div style="font-size:20px;margin-bottom:8px;">⏳</div>
                <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Comprar em Breve</div>
                <div style="font-size:44px;font-weight:800;color:#D99F2A;line-height:1;">{breve}</div>
                <div style="font-size:11px;color:#554A40;margin-top:4px;">próximos dias, monitorar</div>
            </div>
            <div style="background:#1A1715;border:1px solid #164028;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;">
                <div style="position:absolute;top:12px;right:12px;background:#0F2A1B;color:#2ED297;border:1px solid #164028;font-size:9px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:3px 8px;border-radius:10px;">ESTÁVEL</div>
                <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:#2ED297;border-radius:0 0 14px 14px;"></div>
                <div style="font-size:20px;margin-bottom:8px;">✅</div>
                <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Estáveis</div>
                <div style="font-size:44px;font-weight:800;color:#2ED297;line-height:1;">{estaveis}</div>
                <div style="font-size:11px;color:#554A40;margin-top:4px;">estoque dentro do planejado</div>
            </div>
            <div style="background:#1A1715;border:1px solid #2A2624;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;">
                <div style="position:absolute;top:12px;right:12px;background:#1A2240;color:#7BA1F2;border:1px solid #2A3A60;font-size:9px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:3px 8px;border-radius:10px;">TOTAL</div>
                <div style="position:absolute;bottom:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#7BA1F2,#A987D9);border-radius:0 0 14px 14px;"></div>
                <div style="font-size:20px;margin-bottom:8px;">📦</div>
                <div style="font-size:10px;color:#8A7B72;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px;">Total de Itens</div>
                <div style="font-size:44px;font-weight:800;color:#FFF8F0;line-height:1;">{total}</div>
                <div style="font-size:11px;color:#554A40;margin-top:4px;">itens monitorados</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── BARRA DE FILTROS + BUSCA ─────────────────────────────────────
        f1, f2 = st.columns([3, 5])
        with f1:
            busca_plan = st.text_input("Buscar produto", placeholder="🔍 Buscar produto...", key="bp1", label_visibility="collapsed")
        with f2:
            filtro_cols = st.columns(4)
            filtros_opts = ["Todos", "🔴 Urgente", "🟡 Em breve", "🟢 Estável"]
            filtro_sel = filtro_cols[0].button(f"Todos  {total}", key="ft_all",  use_container_width=True)
            filtro_urg = filtro_cols[1].button(f"🚨 Urgente  {urgentes}", key="ft_urg", use_container_width=True)
            filtro_brv = filtro_cols[2].button(f"⏳ Em breve  {breve}", key="ft_brv", use_container_width=True)
            filtro_est = filtro_cols[3].button(f"✅ Estável  {estaveis}", key="ft_est", use_container_width=True)

        # Filtro de estado (session_state)
        if filtro_urg: st.session_state["plan_filter"] = "urgente"
        elif filtro_brv: st.session_state["plan_filter"] = "breve"
        elif filtro_est: st.session_state["plan_filter"] = "estavel"
        elif filtro_sel: st.session_state["plan_filter"] = "todos"
        filtro_ativo = st.session_state.get("plan_filter", "todos")

        # ── LISTA DE ITENS ──────────────────────────────────────────────
        import textwrap
        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
        
        # Grid columns structure (8 columns): 120px 1fr 70px 70px 90px 90px 90px 100px
        header_html = textwrap.dedent("""
        <div style="background:#1A1715;border-radius:12px 12px 0 0;border:1px solid #2A2624;border-bottom:none;">
            <div style="display:grid;grid-template-columns:120px 1fr 70px 70px 90px 90px 90px 100px;gap:0;padding:10px 20px;border-bottom:1px solid #2A2624;">
                <div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.05em;text-transform:uppercase;">PRIORIDADE</div>
                <div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.05em;text-transform:uppercase;">PRODUTO</div>
                <div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.05em;text-transform:uppercase;text-align:right;">SALDO</div>
                <div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.05em;text-transform:uppercase;text-align:right;">MÍNIMO</div>
                <div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.05em;text-transform:uppercase;text-align:center;">CONSUMO/DIA</div>
                <div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.05em;text-transform:uppercase;text-align:center;">PRAZO FORNEC.</div>
                <div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.05em;text-transform:uppercase;text-align:center;">COMPRAR ATÉ</div>
                <div style="font-size:10px;font-weight:700;color:#8A7B72;letter-spacing:0.05em;text-transform:uppercase;text-align:right;">QTD SUGERIDA</div>
            </div>
        </div>
        """).strip()
        
        body_rows = []
        itens_visiveis = 0
        for p in plano:
            sk = p["_status_key"]
            nome_p = p["_nome"].lower()

            if filtro_ativo != "todos" and sk != filtro_ativo:
                continue
            if busca_plan and busca_plan.lower() not in nome_p:
                continue
            itens_visiveis += 1

            badge_bg  = "#3B1219" if sk == "urgente" else ("#2A1F08" if sk == "breve" else "#0F2A1B")
            badge_brd = "#5A1A22" if sk == "urgente" else ("#4A3510" if sk == "breve" else "#164028")
            badge_txt = "#EF4444" if sk == "urgente" else ("#D99F2A" if sk == "breve" else "#2ED297")
            badge_lbl = "URGENTE"  if sk == "urgente" else ("EM BREVE" if sk == "breve" else "ESTÁVEL")
            dot_cor   = "#EF4444" if sk == "urgente" else ("#D99F2A" if sk == "breve" else "#2ED297")

            saldo_cor = "#EF4444" if p["_saldo"] <= 0 else ("#D99F2A" if p["_saldo"] <= p["_min"] else "#FFF8F0")
            comprar_ate_cor = "#EF4444" if p["Comprar até"] == "Hoje" else "#FFF8F0"

            # Barra de progresso (saldo / mínimo)
            pct = min(100, int((p["_saldo"] / p["_min"] * 100))) if p["_min"] > 0 else 100
            bar_cor = "#EF4444" if pct < 30 else ("#D99F2A" if pct < 80 else "#2ED297")

            row_html = textwrap.dedent(f"""
            <div style="display:grid;grid-template-columns:120px 1fr 70px 70px 90px 90px 90px 100px;gap:0;padding:14px 20px;border-bottom:1px solid #2A2624;align-items:center;">
                <div><span style="background:{badge_bg};color:{badge_txt};border:1px solid {badge_brd};font-size:10px;font-weight:700;padding:4px 10px;border-radius:8px;">{badge_lbl}</span></div>
                <div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="width:8px;height:8px;background:{dot_cor};border-radius:50%;flex-shrink:0;"></div>
                        <span style="font-size:13px;font-weight:500;color:#FFF8F0;">{p['_nome']}</span>
                    </div>
                    <div style="margin-top:5px;height:3px;background:#2A2624;border-radius:2px;width:160px;">
                        <div style="height:3px;background:{bar_cor};border-radius:2px;width:{pct}%;"></div>
                    </div>
                </div>
                <div style="text-align:right;font-size:14px;font-weight:700;color:{saldo_cor};">{p['_saldo']:.0f}</div>
                <div style="text-align:right;font-size:13px;color:#8A7B72;">{p['_min']:.0f}</div>
                <div style="text-align:center;font-size:13px;color:#FFF8F0;">{p['_consumo']:.1f}/dia</div>
                <div style="text-align:center;">
                    <span style="background:#1A2240;color:#7BA1F2;border:1px solid #2A3A60;font-size:11px;font-weight:600;padding:3px 10px;border-radius:8px;">{p['_prazo']} dias</span>
                </div>
                <div style="text-align:center;font-size:13px;font-weight:700;color:{comprar_ate_cor};">{p['Comprar até']}</div>
                <div style="text-align:right;font-size:13px;font-weight:700;color:#FFF8F0;">{p['_qtd_sug']:.0f} <span style="font-size:11px;color:#8A7B72;">{p['_und']}</span></div>
            </div>
            """).strip()
            body_rows.append(row_html)

        if itens_visiveis == 0:
            body_content = '<div style="padding:32px;text-align:center;font-size:13px;color:#554A40;">Nenhum item encontrado com os filtros atuais.</div>'
        else:
            body_content = "".join(body_rows)

        # Renderizar tudo em um ÚNICO bloco st.markdown dedentado para evitar erros de auto-fechamento do Streamlit
        full_table_html = textwrap.dedent(f"""
        {header_html}
        <div style="background:#1A1715;border-radius:0 0 12px 12px;border:1px solid #2A2624;border-top:none;max-height:480px;overflow-y:auto;">
            {body_content}
        </div>
        """).strip()
        st.markdown(full_table_html, unsafe_allow_html=True)



        # ── FOOTER BAR ──────────────────────────────────────────────────
        st.markdown(f"""
        <div style="margin-top:20px;display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-top:1px solid #2A2624;">
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:8px;height:8px;background:#2ED297;border-radius:50%;box-shadow:0 0 6px #2ED29788;"></div>
                <span style="font-size:12px;color:#8A7B72;">{itens_visiveis} itens · Atualizado agora</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── EXPORTAÇÕES (Injetados via st.empty na parte superior) ────────
        with export_csv_container:
            cols_exp = ["Status", "Produto", "Saldo", "Mínimo", "Consumo/dia", "Prazo Fornec.", "Comprar até", "Qtd sugerida"]
            csv_plan = df_plano[cols_exp].to_csv(index=False, sep=";").encode("utf-8-sig")
            st.download_button(
                "📊 Excel",
                csv_plan,
                f"planejamento_{data_plan.strftime('%Y%m%d')}.csv",
                "text/csv",
                key="dl_plan_csv",
                use_container_width=True
            )

        with export_html_container:
            try:
                from utils.relatorios import gerar_html_planejamento
                html_report = gerar_html_planejamento(df_plano, data_plan).encode("utf-8")
                st.download_button(
                    "📄 Imprimir",
                    html_report,
                    f"Planejamento_Compras_{data_plan.strftime('%Y%m%d')}.html",
                    "text/html",
                    key="dl_plan_html",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erro HTML: {e}")

        foot_l, foot_r = st.columns([7, 3])
        with foot_l:
            st.caption("Você pode exportar a planilha ou imprimir usando os botões no topo da página.")
        with foot_r:
            st.markdown('<div class="btn-plan">', unsafe_allow_html=True)
            if st.button("✓ Gerar lista de compras", use_container_width=True, key="gen_list"):
                urgentes_list = [p for p in plano if p["_status_key"] in ("urgente", "breve") and p["_qtd_sug"] > 0]
                if urgentes_list:
                    linhas = "\n".join([f"• {p['_nome']}: {p['_qtd_sug']:.0f} {p['_und']}" for p in urgentes_list])
                    st.success(f"Lista gerada com {len(urgentes_list)} itens:\n\n{linhas}")
                else:
                    st.info("Nenhum item urgente com quantidade sugerida.")
            st.markdown('</div>', unsafe_allow_html=True)



    # ── GOOGLE SHEETS SYNC ───────────────────────────────
    def tela_sync():
        header("☁️","Google Sheets","Status da sincronização em nuvem")
        from utils.sheets import sheets_ok, inicializar_sheets

        conectado = sheets_ok()
        if conectado:
            st.markdown("<div class='ag'>✅ <b>Conectado ao Google Sheets</b> — sincronização ativa</div>",unsafe_allow_html=True)
        else:
            st.markdown("<div class='ar'>🔴 <b>Sem conexão com Google Sheets</b></div>",unsafe_allow_html=True)
            st.info("Certifique-se que: 1) `gspread` e `google-auth` estão instalados  2) A planilha foi compartilhada com a conta de serviço  3) A Google Sheets API está ativada no projeto")

        st.markdown("---")
        st.markdown("#### 📤 Sincronizar dados para o Sheets")

        if st.button("🔄  Sincronizar agora", type="primary", use_container_width=True, key="btn_sync"):
            if not conectado:
                st.error("Sem conexão. Verifique as credenciais e tente reiniciar o app.")
                return
            with st.spinner("Enviando dados para o Google Sheets..."):
                try:
                    inicializar_sheets(listar_itens(), listar_estoque(), listar_fornecedores(), listar_movimentos(limit=10000))
                    st.success("✅ Sincronizado! Abra a planilha para confirmar.")
                    st.markdown("👉 [Abrir Google Sheets](https://docs.google.com/spreadsheets/d/1v7eEbP49FiwU34ob3d4OBobIQ3BuCIrE-E2k2Y3pUR4/edit)")
                except Exception as e:
                    st.error(f"Erro durante sincronização: {e}")

        st.markdown("---")
        st.markdown("#### ℹ️ Como funciona")
        st.markdown("""
        - Cada lançamento é salvo **simultaneamente** no CSV local e no Google Sheets
        - CSV local = backup offline, funciona sem internet
        - Google Sheets = acesso remoto, integração com Excel, relatórios
        - Se a internet cair, o dado fica no CSV. Clique "Sincronizar agora" depois para enviar
        """)
        st.caption(f"ID: 1v7eEbP49FiwU34ob3d4OBobIQ3BuCIrE-E2k2Y3pUR4 | panelinhas-app@panelinhas-erp.iam.gserviceaccount.com")


    # ── COMPOSIÇÃO (BOM) ─────────────────────────────────
    def tela_composicao():
        header("🧩","Composição de Produtos","Defina quais ingredientes compõem cada Panelinha")
        import pandas as pd
        from pathlib import Path
        from utils.data import listar_composicao, _salvar, _ler_cached

        df_comp = listar_composicao()
        itens   = listar_itens()

        # Produtos compostos existentes
        if not df_comp.empty:
            st.markdown("#### 📋 Composições cadastradas")
            for prod in df_comp["id_produto"].unique():
                grupo = df_comp[df_comp["id_produto"]==prod]
                nome_prod = grupo.iloc[0]["nome_produto"]
                st.markdown(f"**{prod} — {nome_prod}**")
                for _, r in grupo.iterrows():
                    st.markdown(
                        f"&nbsp;&nbsp;&nbsp;↳ `{r['id_ingrediente']}` {r['nome_ingrediente']} × **{r['quantidade']} {r['unidade']}**"
                    )
            st.markdown("---")

        # Formulário para adicionar nova linha
        st.markdown("#### ➕ Adicionar ingrediente a um produto")

        pans = itens[itens["id_item"].str.startswith("PAN")]
        ings = itens[itens["id_item"].str.startswith("ING")]

        if pans.empty:
            st.info("Nenhum produto PAN cadastrado em itens.csv")
            return
        if ings.empty:
            st.info("Nenhum ingrediente ING cadastrado em itens.csv")
            return

        op_pan = {f"{r['id_item']} — {r['nome']}":r['id_item'] for _,r in pans.iterrows()}
        op_ing = {f"{r['id_item']} — {r['nome']}":r['id_item'] for _,r in ings.iterrows()}

        c1,c2,c3 = st.columns(3)
        with c1:
            pan_sel = st.selectbox("🍲 Produto (PAN)", list(op_pan), key="comp_pan")
        with c2:
            ing_sel = st.selectbox("🥗 Ingrediente (ING)", list(op_ing), key="comp_ing")
        with c3:
            qtd_comp = st.number_input("Quantidade por unidade", min_value=0.001,
                                       value=1.0, step=0.5, format="%.1f", key="comp_qtd")

        id_pan = op_pan[pan_sel]
        id_ing = op_ing[ing_sel]
        nome_pan = itens[itens["id_item"]==id_pan].iloc[0]["nome"]
        nome_ing = itens[itens["id_item"]==id_ing].iloc[0]["nome"]
        und_ing  = itens[itens["id_item"]==id_ing].iloc[0]["unidade"]

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅  Adicionar composição", type="primary", use_container_width=True, key="btn_comp"):
            # Verifica se já existe
            ja_existe = (
                not df_comp.empty and
                ((df_comp["id_produto"]==id_pan) & (df_comp["id_ingrediente"]==id_ing)).any()
            )
            if ja_existe:
                st.warning(f"⚠️ {id_ing} já está cadastrado em {id_pan}. Remova primeiro para alterar.")
            else:
                nova = pd.DataFrame([{
                    "id_produto":     id_pan,
                    "nome_produto":   nome_pan,
                    "id_ingrediente": id_ing,
                    "nome_ingrediente": nome_ing,
                    "quantidade":     qtd_comp,
                    "unidade":        und_ing,
                }])
                df_novo = pd.concat([df_comp, nova], ignore_index=True)
                _salvar("composicao", df_novo)
                _ler_cached.clear()
                st.session_state["msg_comp"] = f"✅ {nome_ing} adicionado à composição de {nome_pan}"
                st.rerun()

        if st.session_state.get("msg_comp"):
            st.success(st.session_state.pop("msg_comp"))

        # Remover ingrediente
        if not df_comp.empty:
            st.markdown("---")
            st.markdown("#### 🗑️ Remover ingrediente")
            opcoes_rem = {
                f"{r['id_produto']} → {r['id_ingrediente']} ({r['nome_ingrediente']})": i
                for i, r in df_comp.iterrows()
            }
            rem_sel = st.selectbox("Selecione para remover", list(opcoes_rem), key="comp_rem")
            if st.button("🗑️ Remover", type="secondary", use_container_width=False, key="btn_rem"):
                idx_rem = opcoes_rem[rem_sel]
                df_comp = df_comp.drop(idx_rem).reset_index(drop=True)
                _salvar("composicao", df_comp)
                _ler_cached.clear()
                st.success("✅ Removido!")
                st.rerun()


    def tela_guia_gerente():
        import textwrap
        # Custom CSS for modern card designs
        st.markdown(textwrap.dedent("""
        <style>
        /* ── CSS do Guia Gerente ── */
        .manual-card {
            background: #1A1715;
            border: 1px solid #2A2624;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .manual-card-welcome {
            background: linear-gradient(135deg, #18122B 0%, #110E1C 100%);
            border: 1px solid #332159;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .manual-card-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }
        .manual-badge {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content:center;
            font-size: 15px;
            font-weight: 700;
        }
        .manual-title {
            font-size: 18px;
            font-weight: 800;
            color: #FFF8F0;
            margin: 0;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }
        .manual-objective {
            background: rgba(26, 23, 21, 0.5);
            border: 1px solid #2A2624;
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 18px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }
        .manual-steps {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 18px;
            padding-left: 4px;
        }
        .manual-step-row {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            font-size: 13px;
            color: #FFF8F0;
            line-height: 1.5;
        }
        .manual-step-num {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 800;
            flex-shrink: 0;
            margin-top: 1px;
        }
        .manual-alert-box {
            border-radius: 10px;
            padding: 14px 18px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
            font-size: 12px;
            line-height: 1.6;
        }
        .manual-side-link {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            background: #1A1715;
            border: 1px solid #2A2624;
            color: #8A7B72;
            border-radius: 8px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 13px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s ease-in-out;
        }
        .manual-side-link:hover {
            border-color: #554A40;
            color: #FFF8F0;
        }
        .manual-side-link-active {
            background: #2A2240 !important;
            border: 1px solid #4A3560 !important;
            color: #9B87D9 !important;
        }
        </style>
        """), unsafe_allow_html=True)

        # ── TOP BAR / HEADER ──
        top_bar_html = textwrap.dedent("""
        <div style="display:flex; justify-content:space-between; align-items:center; background:#1A1715; border:1px solid #2A2624; border-radius:10px; padding:10px 16px; margin-bottom:20px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="background:#2A2240; color:#9B87D9; border:1px solid #4A3560; padding:6px 10px; border-radius:8px; font-size:14px; display:flex; align-items:center; justify-content:center;">📁</span>
                <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:12px; color:#8A7B72;">
                    ERP <span style="margin:0 4px; color:#554A40;">&gt;</span> Ferramentas <span style="margin:0 4px; color:#554A40;">&gt;</span> <span style="color:#FFF8F0; font-weight:700;">Guia Gerente</span>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:16px;">
                <div style="display:flex; align-items:center; gap:6px; font-family:'Plus Jakarta Sans',sans-serif; font-size:12px; color:#8A7B72;">
                    <div style="width:8px; height:8px; background:#2ED297; border-radius:50%; box-shadow:0 0 6px #2ED29788;"></div>
                    Manual v2.0
                </div>
                <a href="#" style="background:#2A2624; border:1px solid #332B25; color:#FFF8F0; text-decoration:none; font-family:'Plus Jakarta Sans',sans-serif; font-size:12px; font-weight:600; padding:6px 12px; border-radius:6px; display:flex; align-items:center; gap:6px;">
                    📥 Imprimir guia
                </a>
            </div>
        </div>
        """).strip()
        st.markdown(top_bar_html, unsafe_allow_html=True)

        # Split layout
        col_content, col_nav = st.columns([3.5, 1.1], gap="medium")

        with col_nav:
            st.markdown(textwrap.dedent("""
            <div style="position: sticky; top: 20px;">
                <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:10px; font-weight:700; color:#8A7B72; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:12px; padding-left:8px;">Neste Guia</div>
                <div style="display:flex; flex-direction:column; gap:6px;">
                    <a href="#bem-vindo" class="manual-side-link manual-side-link-active">
                        <span>👋</span> Bem-vindo
                    </a>
                    <a href="#1-entrada-de-estoque" class="manual-side-link">
                        <span>📥</span> 1. Entrada
                    </a>
                    <a href="#2-saida-de-estoque" class="manual-side-link">
                        <span>📤</span> 2. Saída
                    </a>
                    <a href="#3-ajuste-de-estoque" class="manual-side-link">
                        <span>⚖️</span> 3. Ajuste
                    </a>
                    <a href="#4-dashboard-painel-de-metricas" class="manual-side-link">
                        <span>📊</span> 4. Dashboard
                    </a>
                    <a href="#5-planejamento-de-compras" class="manual-side-link">
                        <span>🗓️</span> 5. Planejamento
                    </a>
                    <a href="#6-consulta-de-estoque" class="manual-side-link">
                        <span>🔍</span> 6. Consulta
                    </a>
                    <div style="height:1px; background:#2A2624; margin:4px 0;"></div>
                    <a href="#boas-praticas-do-gerente" class="manual-side-link">
                        <span>💡</span> Boas práticas
                    </a>
                </div>
            </div>
            """), unsafe_allow_html=True)

        with col_content:
            # Welcome Card
            welcome_html = textwrap.dedent("""
            <div id="bem-vindo" class="manual-card-welcome">
                <div style="position:absolute; top:-20px; right:-20px; font-size:120px; opacity:0.03; font-weight:900; user-select:none;">📋</div>
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:14px;">
                    <span style="font-size:22px;">👋</span>
                    <h2 style="font-family:'Bebas Neue',sans-serif; font-size:26px; color:#FFF8F0; margin:0; letter-spacing:1px; line-height:1; display:flex; align-items:center; gap:8px;">
                        BEM-VINDO AO GUIA DO GERENTE!
                        <span style="background:#2A2240; color:#9B87D9; border:1px solid #4A3560; font-size:9px; font-weight:700; padding:4px 10px; border-radius:20px; font-family:'Plus Jakarta Sans',sans-serif;">MANUAL OPERACIONAL</span>
                    </h2>
                </div>
                <p style="font-size:13.5px; color:#8A7B72; line-height:1.6; margin:0;">
                    Este guia foi elaborado para auxiliar você, Gerente, na gestão diária de estoques do <b>Panelinhas do Brasil</b>.
                    O sistema foi estruturado para fornecer controles precisos, alertas automáticos e previsões inteligentes em tempo real.
                    Leia cada seção com atenção — as operações são simples, mas os detalhes fazem a diferença.
                </p>
            </div>
            """).strip()
            st.markdown("\n".join(line.strip() for line in welcome_html.splitlines()), unsafe_allow_html=True)

            # Card 1. Entrada de Estoque
            entrada_html = textwrap.dedent("""
            <div id="1-entrada-de-estoque" class="manual-card" style="border-left: 4px solid #2ED297;">
                <div class="manual-card-header">
                    <div class="manual-badge" style="background:#0F2A1B; color:#2ED297; border:1px solid #164028;">1</div>
                    <h3 class="manual-title">📥 Entrada de Estoque</h3>
                </div>
                <div class="manual-objective">
                    <div style="font-size:18px;">🎯</div>
                    <div>
                        <div style="font-size:10px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase;">Objetivo</div>
                        <div style="font-size:13px; color:#FFF8F0; margin-top:2px;">Registrar o recebimento de ingredientes, hortifrutis, embalagens e itens operacionais comprados.</div>
                    </div>
                </div>
                <div style="font-size:11px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:12px; margin-top:6px;">Como Funciona</div>
                <div class="manual-steps">
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#0F2A1B; color:#2ED297;">1</div>
                        <div>Selecione o <b>Item</b> e o <b>Fornecedor</b> — esses campos iniciam vazios para evitar lançamentos incorretos.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#0F2A1B; color:#2ED297;">2</div>
                        <div>Insira a <b>Quantidade</b> física recebida e o <b>Custo unitário</b> de compra.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#0F2A1B; color:#2ED297;">3</div>
                        <div>O número da <b>NF</b> (Nota Fiscal) e a <b>Observação</b> são opcionais, mas fortemente recomendados para rastreabilidade.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#0F2A1B; color:#2ED297;">4</div>
                        <div>O app exibe em tempo real o <b>Saldo atual</b>, o <b>Novo saldo</b> projetado e o <b>Total em R$</b> da compra.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#0F2A1B; color:#2ED297;">5</div>
                        <div>Ao clicar em <b>Confirmar Entrada</b>, a transação é registrada e o formulário é automaticamente limpo.</div>
                    </div>
                </div>
            </div>
            """).strip()
            st.markdown("\n".join(line.strip() for line in entrada_html.splitlines()), unsafe_allow_html=True)

            # Card 2. Saída de Estoque
            saida_html = textwrap.dedent("""
            <div id="2-saida-de-estoque" class="manual-card" style="border-left: 4px solid #EF4444;">
                <div class="manual-card-header">
                    <div class="manual-badge" style="background:#3B1219; color:#EF4444; border:1px solid #5A1A22;">2</div>
                    <h3 class="manual-title">📤 Saída de Estoque</h3>
                </div>
                <div class="manual-objective">
                    <div style="font-size:18px;">🎯</div>
                    <div>
                        <div style="font-size:10px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase;">Objetivo</div>
                        <div style="font-size:13px; color:#FFF8F0; margin-top:2px;">Registrar baixas no estoque de duas formas: baixas avulsas (manual) ou baixas automáticas diárias (via relatórios de vendas do SWFast).</div>
                    </div>
                </div>

                <div style="font-size:12px; font-weight:700; color:#FFF8F0; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:8px; border-bottom:1px solid #2A2624; padding-bottom:4px;">Método 1 — Registrar Saída (Manual)</div>
                <div style="font-size:12px; color:#8A7B72; margin-bottom:12px; font-style:italic;">Ideal para consumo de funcionários, descartes, vencimentos, perdas ou devoluções de um item específico.</div>
                <div class="manual-steps">
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#3B1219; color:#EF4444;">1</div>
                        <div>Na aba <b>"Registrar Saída"</b>, selecione o <b>Item</b> e digite a <b>Quantidade</b> a ser baixada.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#3B1219; color:#EF4444;">2</div>
                        <div>Escolha o <b>Tipo de saída</b> correspondente (ex: <i>Consumo, Descarte, Ajuste de Inventário</i>) e escreva uma observação se necessário.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#3B1219; color:#EF4444;">3</div>
                        <div>Se o item for um <b>produto composto</b> (como pratos antigos), a caixa amarela exibirá os subingredientes que serão baixados automaticamente (conforme a receita cadastrada).</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#3B1219; color:#EF4444;">4</div>
                        <div>Confirme clicando em <b>"Confirmar saída"</b>. Os saldos serão atualizados e o formulário será limpo.</div>
                    </div>
                </div>

                <div style="height:12px;"></div>

                <div style="font-size:12px; font-weight:700; color:#FFF8F0; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:8px; border-bottom:1px solid #2A2624; padding-bottom:4px;">Método 2 — Importar Vendas SWFast (Em Lote)</div>
                <div style="font-size:12px; color:#8A7B72; margin-bottom:12px; font-style:italic;">Ideal para dar baixa automática em lote no estoque com base nas vendas do dia do sistema SWFast.</div>
                
                <div style="margin-left: 8px; margin-bottom:16px;">
                    <div style="font-size:12px; font-weight:700; color:#EF4444; margin-bottom:4px;">Etapa 1: Mapeamento de Itens (Feito apenas uma vez)</div>
                    <p style="font-size:12.5px; color:#8A7B72; line-height:1.5; margin:0 0 10px 0;">
                        Antes de importar relatórios, o sistema precisa saber qual item do SWFast corresponde a qual ingrediente/item no ERP.<br>
                        • Vá até a aba <b>"Mapeamento SWFast"</b>.<br>
                        • Preencha o <b>Código SWFast</b> (código do produto no relatório), o <b>Nome no SWFast</b> e selecione o correspondente <b>Item no ERP</b>.<br>
                        • Clique em <b>"Salvar Mapeamento"</b>. O vínculo fica registrado na lista abaixo.
                    </p>

                    <div style="font-size:12px; font-weight:700; color:#EF4444; margin-bottom:4px;">Etapa 2: Exportar Relatório do SWFast</div>
                    <p style="font-size:12.5px; color:#8A7B72; line-height:1.5; margin:0 0 10px 0;">
                        No sistema SWFast, exporte diariamente o relatório de <b>Venda de Produtos</b> ou <b>Venda de Insumos</b>. O sistema aceita tanto o arquivo original em <b>PDF</b> quanto em Excel (<b>.xlsx ou .xls</b>).
                    </p>

                    <div style="font-size:12px; font-weight:700; color:#EF4444; margin-bottom:4px;">Etapa 3: Importar no ERP e Confirmar Baixa</div>
                    <p style="font-size:12.5px; color:#8A7B72; line-height:1.5; margin:0;">
                        • Vá até a aba <b>"Importar SWFast"</b>.<br>
                        • Envie o arquivo exportado do SWFast pelo campo de upload.<br>
                        • O sistema fará a leitura automática e exibirá uma <b>Pré-visualização da Baixa</b> showing: item, quantidade vendida, saldo atual e o novo saldo projetado no ERP.<br>
                        • Caso haja itens no arquivo que ainda não foram mapeados, eles serão exibidos em uma aba retrátil logo abaixo para que você possa mapeá-los.<br>
                        • Verifique se as informações estão corretas e clique no botão vermelho <b>"Confirmar Baixa em Lote"</b> para registrar todas as saídas de uma vez só!
                    </p>
                </div>

                <div class="manual-alert-box" style="background:#2A1F08; border:1px solid #4A3510; color:#D99F2A;">
                    <div style="font-size:16px; margin-top:-2px;">⚠️</div>
                    <div>
                        <b>ATENÇÃO — DIVERGÊNCIAS NO MAPEAMENTO</b><br>
                        Itens não mapeados são ignorados na baixa. Se o relatório contiver produtos novos vendidos, certifique-se de cadastrá-los primeiro na aba <b>Mapeamento SWFast</b> para que o estoque seja descontado corretamente nas próximas importações.
                    </div>
                </div>
            </div>
            """).strip()
            st.markdown("\n".join(line.strip() for line in saida_html.splitlines()), unsafe_allow_html=True)

            # Card 3. Ajuste de Estoque
            ajuste_html = textwrap.dedent("""
            <div id="3-ajuste-de-estoque" class="manual-card" style="border-left: 4px solid #D99F2A;">
                <div class="manual-card-header">
                    <div class="manual-badge" style="background:#2A1F08; color:#D99F2A; border:1px solid #4A3510;">3</div>
                    <h3 class="manual-title">⚖️ Ajuste de Estoque</h3>
                </div>
                <div class="manual-objective">
                    <div style="font-size:18px;">🎯</div>
                    <div>
                        <div style="font-size:10px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase;">Objetivo</div>
                        <div style="font-size:13px; color:#FFF8F0; margin-top:2px;">Corrigir discrepâncias pontuais entre o sistema e a contagem física, identificadas em inventários periódicos.</div>
                    </div>
                </div>
                <div style="font-size:11px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:12px; margin-top:6px;">Como Funciona</div>
                <div class="manual-steps">
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A1F08; color:#D99F2A;">1</div>
                        <div>Selecione o <b>Item</b>, escolha o <b>Motivo</b> (ex: <i>Inventário Físico</i>) e informe a <b>Quantidade física contada</b>.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A1F08; color:#D99F2A;">2</div>
                        <div>O sistema calcula automaticamente a <b>Diferença</b> entre o saldo no sistema e a contagem real, classificando como ajuste <span style="color:#2ED297; font-weight:700;">POSITIVO</span> ou <span style="color:#EF4444; font-weight:700;">NEGATIVO</span>.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A1F08; color:#D99F2A;">3</div>
                        <div>Clique em <b>Confirmar Ajuste</b> para regularizar o saldo do estoque.</div>
                    </div>
                </div>
                <div class="manual-alert-box" style="background:#1A2240; border:1px solid #2A3A60; color:#7BA1F2;">
                    <div style="font-size:16px; margin-top:-2px;">💡</div>
                    <div>
                        <b>BOA PRÁTICA</b><br>
                        Realize inventários físicos pelo menos <b>uma vez por semana</b> nos itens críticos (ingredientes de alto giro) e mensalmente nos demais. Registre sempre o motivo real para manter o histórico de auditoria limpo.
                    </div>
                </div>
            </div>
            """).strip()
            st.markdown("\n".join(line.strip() for line in ajuste_html.splitlines()), unsafe_allow_html=True)

            # Card 4. Dashboard
            dashboard_html = textwrap.dedent("""
            <div id="4-dashboard-painel-de-metricas" class="manual-card" style="border-left: 4px solid #9B87D9;">
                <div class="manual-card-header">
                    <div class="manual-badge" style="background:#2A2240; color:#9B87D9; border:1px solid #4A3560;">4</div>
                    <h3 class="manual-title">📊 Dashboard — Painel de Métricas</h3>
                </div>
                <div class="manual-objective">
                    <div style="font-size:18px;">🎯</div>
                    <div>
                        <div style="font-size:10px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase;">Objetivo</div>
                        <div style="font-size:13px; color:#FFF8F0; margin-top:2px;">Painel visual e analítico exclusivo para Gerentes e Administradores, com visão consolidada do estoque e indicadores financeiros do período.</div>
                    </div>
                </div>
                <div style="font-size:11px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:12px; margin-top:6px;">O que você encontra aqui</div>
                <div class="manual-steps">
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A2240; color:#9B87D9;">📊</div>
                        <div><b>KPIs do estoque:</b> total de itens, quantidade de zerados, críticos e itens em situação normal.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A2240; color:#9B87D9;">💰</div>
                        <div><b>Análise de CMV</b> (Custo da Mercadoria Vendida): fórmula Estoque Inicial + Compras - Estoque Final = CMV do mês.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A2240; color:#9B87D9;">🚨</div>
                        <div><b>Alertas de ação imediata:</b> lista priorizada de itens <span style="color:#EF4444; font-weight:700;">ZERADOS</span> e <span style="color:#D99F2A; font-weight:700;">CRÍTICOS</span> com barra de progresso do saldo.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A2240; color:#9B87D9;">🔧</div>
                        <div><b>Movimentos do dia:</b> histórico em tempo real das entradas, saídas e ajustes realizados na data atual.</div>
                    </div>
                </div>
            </div>
            """).strip()
            st.markdown("\n".join(line.strip() for line in dashboard_html.splitlines()), unsafe_allow_html=True)

            # Card 5. Planejamento
            planejamento_html = textwrap.dedent("""
            <div id="5-planejamento-de-compras" class="manual-card" style="border-left: 4px solid #2ED297;">
                <div class="manual-card-header">
                    <div class="manual-badge" style="background:#0F2A1B; color:#2ED297; border:1px solid #164028;">5</div>
                    <h3 class="manual-title">🗓️ Planejamento de Compras</h3>
                </div>
                <div class="manual-alert-box" style="background:#0F2A1B; border:1px solid #164028; color:#2ED297; margin-bottom:18px;">
                    <div style="font-size:16px; margin-top:-2px;">🤖</div>
                    <div>
                        <b>ALGORITMO PREDITIVO DE RUPTURA</b><br>
                        Esta é a tela mais estratégica do sistema. O algoritmo calcula automaticamente quais itens precisam ser comprados e em qual quantidade, baseando-se no consumo histórico real.
                    </div>
                </div>
                <div style="font-size:11px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:12px;">Como Interpretar os Status</div>
                <div class="manual-steps">
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#3B1219; color:#EF4444; font-size:8px;">🚨</div>
                        <div><span style="background:#3B1219; color:#EF4444; border:1px solid #5A1A22; font-size:9px; font-weight:700; padding:2px 6px; border-radius:4px; margin-right:6px;">COMPRAR JÁ</span> O estoque atual dura menos tempo do que o prazo de entrega do fornecedor (<i>Prazo do Fornecedor</i>). <b>Há risco real de ruptura</b>. Faça o pedido imediatamente.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A1F08; color:#D99F2A; font-size:8px;">⏳</div>
                        <div><span style="background:#2A1F08; color:#D99F2A; border:1px solid #4A3510; font-size:9px; font-weight:700; padding:2px 6px; border-radius:4px; margin-right:6px;">EM BREVE</span> O estoque restante dura menos do que o dobro do prazo de entrega. Não é urgente hoje, mas <b>monitore diariamente</b>.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#0F2A1B; color:#2ED297; font-size:8px;">✅</div>
                        <div><span style="background:#0F2A1B; color:#2ED297; border:1px solid #164028; font-size:9px; font-weight:700; padding:2px 6px; border-radius:4px; margin-right:6px;">ESTÁVEL</span> Estoque suficiente para o período planejado. <b>Sem ação necessária</b>.</div>
                    </div>
                </div>
                <div style="font-size:11px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:12px; margin-top:6px;">Fórmulas Utilizadas</div>
                <div class="manual-steps">
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#1A2240; color:#7BA1F2;">📊</div>
                        <div><b>Consumo/dia:</b> média aritmética de todas as saídas registradas nos últimos 7 dias.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#1A2240; color:#7BA1F2;">⚙️</div>
                        <div><b>Quantidade Sugerida:</b> calculada com base no consumo diário, prazo de entrega do fornecedor e um <b>buffer de segurança +20%</b> para evitar desabastecimento.</div>
                    </div>
                </div>
            </div>
            """).strip()
            st.markdown("\n".join(line.strip() for line in planejamento_html.splitlines()), unsafe_allow_html=True)

            # Card 6. Consulta
            consulta_html = textwrap.dedent("""
            <div id="6-consulta-de-estoque" class="manual-card" style="border-left: 4px solid #3B82F6;">
                <div class="manual-card-header">
                    <div class="manual-badge" style="background:#1A2240; color:#7BA1F2; border:1px solid #2A3A60;">6</div>
                    <h3 class="manual-title">🔍 Consulta de Estoque</h3>
                </div>
                <div class="manual-objective">
                    <div style="font-size:18px;">🎯</div>
                    <div>
                        <div style="font-size:10px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase;">Objetivo</div>
                        <div style="font-size:13px; color:#FFF8F0; margin-top:2px;">Visualizar a posição atual de todo o estoque com filtros por categoria, local e status, além de acessar o histórico completo de movimentos.</div>
                    </div>
                </div>
                <div style="font-size:11px; font-weight:700; color:#8A7B72; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:12px; margin-top:6px;">Recursos Disponíveis</div>
                <div class="manual-steps">
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#1A2240; color:#7BA1F2;">🔍</div>
                        <div><b>Busca ao vivo</b> por nome, código ou categoria — filtragem instantânea sem recarregar a página.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#1A2240; color:#7BA1F2;">🔴</div>
                        <div>Botão <b>"Só críticos"</b> para filtrar rapidamente zerados e abaixo do mínimo.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#1A2240; color:#7BA1F2;">📋</div>
                        <div>Aba <b>Histórico</b> para rastrear todas as movimentações registradas no período.</div>
                    </div>
                </div>
            </div>
            """).strip()
            st.markdown("\n".join(line.strip() for line in consulta_html.splitlines()), unsafe_allow_html=True)

            # Card Boas Práticas
            boas_praticas_html = textwrap.dedent("""
            <div id="boas-praticas-do-gerente" class="manual-card" style="border-left: 4px solid #FF8C00;">
                <div class="manual-card-header">
                    <div class="manual-badge" style="background:#2A1F08; color:#FF8C00; border:1px solid #4A3510;">💡</div>
                    <h3 class="manual-title">💡 ✨ Boas Práticas do Gerente</h3>
                </div>
                <div class="manual-steps">
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A1F08; color:#FF8C00;">☀️</div>
                        <div><b>Rotina diária:</b> abra o Dashboard toda manhã. Se houver itens <span style="background:#3B1219; color:#EF4444; border:1px solid #5A1A22; font-size:10px; font-weight:700; padding:1px 5px; border-radius:4px;">ZERADOS</span>, acione o fornecedor antes das 9h.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A1F08; color:#FF8C00;">📥</div>
                        <div><b>Entrada imediata:</b> registre cada compra no momento do recebimento. Nunca acumule lançamentos para o fim do dia — isso distorce o Planejamento.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A1F08; color:#FF8C00;">📋</div>
                        <div><b>Inventário semanal:</b> nos ingredientes de alto giro (carnes, hortifrutis), faça contagem toda semana e use o Ajuste para corrigir diferenças.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A1F08; color:#FF8C00;">🗓️</div>
                        <div><b>Planejamento preventivo:</b> acesse a tela de Planejamento às sextas-feiras e gere a lista de compras para a semana seguinte com antecedência.</div>
                    </div>
                    <div class="manual-step-row">
                        <div class="manual-step-num" style="background:#2A1F08; color:#FF8C00;">🚫</div>
                        <div><b>Nunca ignore os alertas:</b> um item <span style="background:#3B1219; color:#EF4444; border:1px solid #5A1A22; font-size:10px; font-weight:700; padding:1px 5px; border-radius:4px;">ZERADO</span> que aparece no Dashboard é ruptura — afeta diretamente a operação e o atendimento ao cliente.</div>
                    </div>
                </div>
            </div>
            """).strip()
            st.markdown("\n".join(line.strip() for line in boas_praticas_html.splitlines()), unsafe_allow_html=True)


    def tela_guia_admin():
        header("📘", "Guia do Administrador", "Manual avançado para Administradores de TI e Sistemas")
        st.markdown("""
        ### 👑 Bem-vindo ao Guia do Administrador!
        Como Administrador, você possui controle total sobre a infraestrutura de dados local e em nuvem do ERP **Panelinhas do Brasil**. Além de todas as funções do Gerente, você é responsável pelas receitas de produtos e sincronizações.
        
        ---
        
        ### 🧩 1. Gestão de Composição (Ficha Técnica / BOM)
        * **Objetivo**: Definir quais ingredientes (`ING-xxx`) compõem cada prato final (`PAN-xxx`) e suas respectivas proporções.
        * **Como funciona**:
          1. Na aba **Composição**, selecione o prato acabado (PAN) e o ingrediente individual (ING).
          2. Insira a **Quantidade por unidade** (ex: 1 porção de arroz para o prato de Feijoada).
          3. Clique em **Adicionar composição** para salvar. A alteração atualiza a ficha técnica do prato em tempo real.
          4. Se uma composição estiver incorreta, utilize o formulário inferior **Remover ingrediente** para deletá-la da base.
        * *Nota*: Os novos pratos da **Naturall Foods** (`PAN-001` a `PAN-034`) são kits prontos adquiridos e estocados diretamente do fornecedor. Portanto, eles não necessitam de receitas de ingredientes em `composicao.csv`!
        
        ---
        
        ### ☁️ 2. Google Sheets Cloud Integration
        * **Objetivo**: Manter os dados locais da loja sincronizados com a nuvem em tempo real e integrá-los com as planilhas do Excel.
        * **Como funciona**:
          1. O app web realiza lançamentos locais em arquivos CSV e também atualiza o Google Sheets dinamicamente a cada transação (Entrada/Saída/Ajuste).
          2. Se houver falha de internet ou para inicializar uma nova base de dados, utilize a tela de **Sincronização** e clique em **Sincronizar agora**.
          3. O sistema usa um mecanismo de **gravação em lote de alta performance (Batch Write)**, otimizando as tabelas `ITENS`, `ESTOQUE` e `FORNECEDORES` em apenas 3 chamadas consolidadas, evitando erros de cota (Erro 429) do Google Sheets.
        
        ---
        
        ### 📊 3. Sincronização com Planilhas Excel
        * Para puxar os dados mais recentes do Google Sheets para o painel administrativo do gerente local (**Panelinhas_ERP_v7.xlsx**):
          1. Acesse o terminal da máquina local.
          2. Execute o comando de integração:
             ```bash
             python sincronizar_excel.py
             ```
          3. O script detecta automaticamente todos os arquivos Excel na pasta de downloads e na pasta do projeto e apresenta uma lista numerada.
          4. Escolha a opção correspondente a **Panelinhas_ERP_v7.xlsx** (geralmente opção `3`).
          5. O script atualiza exclusivamente as abas de dados brutos (`csv&sheet=MOVIMENTOS`, `csv&sheet=ESTOQUE`, `csv&sheet=ITENS`, `csv&sheet=FORNECEDORES`) e preserva 100% de todas as fórmulas de consolidação gerencial do administrador!
          6. O Excel realiza a validação automaticamente e cria um arquivo de backup em segundos.
        """)


    # ── ROTEADOR ─────────────────────────────────────────
    {"entrada":tela_entrada,"saida":tela_saida,"ajuste":tela_ajuste,
     "consulta":tela_consulta,"dashboard":tela_dashboard,
     "planejamento":tela_planejamento,
     "composicao":tela_composicao,
     "sync":tela_sync,
     "guia_gerente":tela_guia_gerente,
     "guia_admin":tela_guia_admin}.get(st.session_state.menu, tela_entrada)()
