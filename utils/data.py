import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    SUPABASE_URL = ""
    SUPABASE_KEY = ""

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

@st.cache_data(ttl=5)
def _ler_cached(nome):
    url = f"{SUPABASE_URL}/rest/v1/{nome}?select=*"
    url += "&limit=10000"
    res = requests.get(url, headers=HEADERS)
    if res.ok:
        data = res.json()
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data).fillna("")
    return pd.DataFrame()

def ler(nome):
    df = _ler_cached(nome)
    return df.copy() if not df.empty else pd.DataFrame()

def _salvar(nome, df):
    if df.empty:
        return
        
    old_df = ler(nome)
    
    pk_map = {
        "itens": "id_item",
        "estoque": "id_item",
        "fornecedores": "id_fornecedor",
        "usuarios": "usuario",
        "movimentos": "id",
        "composicao": "id"
    }
    pk = pk_map.get(nome)
    
    url = f"{SUPABASE_URL}/rest/v1/{nome}"
    
    if pk and not old_df.empty and pk in old_df.columns and pk in df.columns:
        old_ids = set(old_df[pk].astype(str).tolist())
        new_ids = set(df[pk].astype(str).tolist())
        deleted_ids = old_ids - new_ids
        for did in deleted_ids:
            requests.delete(f"{url}?{pk}=eq.{did}", headers=HEADERS)
            
    if nome == "composicao" and "id" not in df.columns:
        requests.delete(f"{url}?id=gt.0", headers=HEADERS)
    
    h = HEADERS.copy()
    h["Prefer"] = "resolution=merge-duplicates"
    records = df.fillna("").to_dict('records')
    
    for i in range(0, len(records), 500):
        requests.post(url, headers=h, json=records[i:i+500])
        
    _ler_cached.clear()

def listar_itens(): return ler("itens")
def buscar_item(id_item):
    df = ler("itens")
    if df.empty: return None
    res = df[df["id_item"] == id_item]
    return res.iloc[0].to_dict() if not res.empty else None

def listar_fornecedores(): return ler("fornecedores")
def listar_estoque(): return ler("estoque")
def saldo_item(id_item):
    est = ler("estoque")
    if est.empty: return 0.0
    res = est[est["id_item"] == id_item]
    if res.empty: return 0.0
    val = res.iloc[0]["saldo_atual"]
    try: return float(val)
    except: return 0.0

def _atualizar_saldo(id_item, delta):
    url = f"{SUPABASE_URL}/rest/v1/estoque?id_item=eq.{id_item}&select=*"
    res = requests.get(url, headers=HEADERS)
    if res.ok and len(res.json()) > 0:
        row = res.json()[0]
        try: curr = float(row.get("saldo_atual", 0))
        except: curr = 0.0
        new_saldo = curr + delta
        patch_url = f"{SUPABASE_URL}/rest/v1/estoque?id_item=eq.{id_item}"
        payload = {
            "saldo_atual": str(new_saldo),
            "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        requests.patch(patch_url, headers=HEADERS, json=payload)
    else:
        item = buscar_item(id_item)
        if item:
            payload = {
                "id_item": id_item,
                "nome": item.get("nome", ""),
                "categoria": item.get("categoria", ""),
                "local": item.get("local", ""),
                "unidade": item.get("unidade", ""),
                "saldo_atual": str(delta),
                "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            post_url = f"{SUPABASE_URL}/rest/v1/estoque"
            requests.post(post_url, headers=HEADERS, json=payload)
    _ler_cached.clear()

def _proximo_id():
    df = ler("movimentos")
    if df.empty or "id" not in df.columns:
        return "MOV-00001"
    import re
    nums = []
    for x in df["id"].dropna():
        m = re.search(r'\d+', str(x))
        if m: nums.append(int(m.group()))
    if not nums: return "MOV-00001"
    return f"MOV-{(max(nums)+1):05d}"

def registrar_movimento(tipo, id_item, quantidade, operador, valor_unit="", fornecedor_id="", motivo="", obs=""):
    item = buscar_item(id_item)
    nome_item = item["nome"] if item else id_item
    qtd = float(quantidade)
    vunit = float(valor_unit) if valor_unit else 0.0
    nova = {
        "id": _proximo_id(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo,
        "id_item": id_item,
        "nome_item": nome_item,
        "quantidade": str(qtd),
        "valor_unit": str(vunit),
        "total": str(round(qtd * vunit, 2)),
        "fornecedor_id": fornecedor_id,
        "motivo": motivo,
        "operador": operador,
        "obs": obs,
    }
    url = f"{SUPABASE_URL}/rest/v1/movimentos"
    requests.post(url, headers=HEADERS, json=nova)
    if tipo == "ENTRADA": _atualizar_saldo(id_item, qtd)
    elif tipo == "SAÍDA": _atualizar_saldo(id_item, -qtd)
    elif tipo == "AJUSTE":
        curr = saldo_item(id_item)
        _atualizar_saldo(id_item, qtd - curr)
    _ler_cached.clear()

def listar_movimentos(limit=200):
    df = ler("movimentos")
    if df.empty: return df
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp", ascending=False).head(limit)
    return df

def autenticar(usuario, senha):
    df = ler("usuarios")
    if df.empty: return None
    user_row = df[(df["usuario"] == usuario) & (df["senha"] == senha) & (df["ativo"] == "Sim")]
    if not user_row.empty:
        r = user_row.iloc[0].to_dict()
        if "nome_completo" in r:
            r["nome"] = r["nome_completo"]
        return r
    return None

def status_item(saldo, minimo):
    try: s = float(saldo)
    except: s = 0.0
    try: m = float(minimo)
    except: m = 0.0
    if s == 0: return "🔴 Zerado"
    if s <= m: return "🟡 Baixo"
    return "🟢 Normal"

def listar_composicao(): return ler("composicao")
def composicao_produto(id_produto):
    comp = listar_composicao()
    if comp.empty or "id_produto" not in comp.columns: return []
    res = comp[comp["id_produto"] == id_produto]
    return res.to_dict('records') if not res.empty else []

def is_composto(id_item):
    comp = listar_composicao()
    if comp.empty: return False
    return id_item in comp["id_produto"].values

def registrar_entrada_composta(id_produto, quantidade, operador, nf="", valor_unit="", fornecedor_id="", obs=""):
    import threading
    def _bg_task():
        registrar_movimento("ENTRADA", id_produto, quantidade, operador, valor_unit=valor_unit, fornecedor_id=fornecedor_id, motivo=f"NF: {nf}", obs=obs)
        comp = composicao_produto(id_produto)
        for ing in comp:
            try: q_ing = float(ing["quantidade"])
            except: q_ing = 0.0
            total_ing = q_ing * float(quantidade)
            _atualizar_saldo(ing["id_ingrediente"], total_ing)
    threading.Thread(target=_bg_task, daemon=True).start()

def registrar_saida_composta(id_produto, quantidade, operador, motivo="", obs=""):
    import threading
    def _bg_task():
        registrar_movimento("SAÍDA", id_produto, quantidade, operador, motivo=motivo, obs=obs)
        comp = composicao_produto(id_produto)
        for ing in comp:
            try: q_ing = float(ing["quantidade"])
            except: q_ing = 0.0
            total_ing = q_ing * float(quantidade)
            _atualizar_saldo(ing["id_ingrediente"], -total_ing)
    threading.Thread(target=_bg_task, daemon=True).start()
