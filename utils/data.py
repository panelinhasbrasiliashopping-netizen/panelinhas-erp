import streamlit as st
import pandas as pd
import requests
import threading
import re
from datetime import datetime

# ── TABELAS LENTAS (mudam raramente): TTL = 90s
_TABELAS_LENTAS = {"itens", "fornecedores", "composicao", "usuarios", "mapeamento_swfast"}
# ── TABELAS RÁPIDAS (mudam com frequência): TTL = 12s
_TABELAS_RAPIDAS = {"estoque", "movimentos"}


def _get_config():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    return url, key, headers


@st.cache_data(ttl=90, show_spinner=False)
def _cache_lento(nome):
    url_base, _, headers = _get_config()
    res = requests.get(f"{url_base}/rest/v1/{nome}?select=*&limit=10000", headers=headers)
    if res.ok:
        data = res.json()
        return pd.DataFrame(data).fillna("") if data else pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(ttl=12, show_spinner=False)
def _cache_rapido(nome):
    url_base, _, headers = _get_config()
    res = requests.get(f"{url_base}/rest/v1/{nome}?select=*&limit=10000", headers=headers)
    if res.ok:
        data = res.json()
        return pd.DataFrame(data).fillna("") if data else pd.DataFrame()
    return pd.DataFrame()


def ler(nome):
    if nome in _TABELAS_LENTAS:
        df = _cache_lento(nome)
    else:
        df = _cache_rapido(nome)
    return df.copy() if not df.empty else pd.DataFrame()


def _invalidar(nome):
    if nome in _TABELAS_LENTAS:
        _cache_lento.clear()
    else:
        _cache_rapido.clear()


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
        "composicao": "id",
        "mapeamento_swfast": "codigo_swfast",
    }
    pk = pk_map.get(nome)
    url_base, _, headers = _get_config()
    url = f"{url_base}/rest/v1/{nome}"

    if pk and not old_df.empty and pk in old_df.columns and pk in df.columns:
        old_ids = set(old_df[pk].astype(str).tolist())
        new_ids = set(df[pk].astype(str).tolist())
        for did in old_ids - new_ids:
            requests.delete(f"{url}?{pk}=eq.{did}", headers=headers)

    if nome == "composicao" and "id" not in df.columns:
        requests.delete(f"{url}?id=gt.0", headers=headers)

    h = headers.copy()
    h["Prefer"] = "resolution=merge-duplicates"
    records = df.fillna("").to_dict("records")
    for i in range(0, len(records), 500):
        requests.post(url, headers=h, json=records[i : i + 500])

    _invalidar(nome)


# ── ITENS ────────────────────────────────────────────────────────────────────

def listar_itens():
    return ler("itens")


def buscar_item(id_item):
    df = ler("itens")
    if df.empty:
        return None
    res = df[df["id_item"] == id_item]
    return res.iloc[0].to_dict() if not res.empty else None


# ── FORNECEDORES ─────────────────────────────────────────────────────────────

def listar_fornecedores():
    return ler("fornecedores")


# ── ESTOQUE ──────────────────────────────────────────────────────────────────

def listar_estoque():
    return ler("estoque")


def saldo_item(id_item):
    est = ler("estoque")
    if est.empty:
        return 0.0
    res = est[est["id_item"] == id_item]
    if res.empty:
        return 0.0
    try:
        return float(res.iloc[0]["saldo_atual"])
    except Exception:
        return 0.0


def status_item(saldo, minimo):
    try:
        s = float(saldo)
    except Exception:
        s = 0.0
    try:
        m = float(minimo)
    except Exception:
        m = 0.0
    if s == 0:
        return "🔴 Zerado"
    if s <= m:
        return "🟡 Baixo"
    return "🟢 Normal"


def _atualizar_saldo(id_item, delta):
    url_base, _, headers = _get_config()
    url = f"{url_base}/rest/v1/estoque?id_item=eq.{id_item}&select=*"
    res = requests.get(url, headers=headers)
    new_saldo = 0.0

    if res.ok and res.json():
        row = res.json()[0]
        try:
            curr = float(row.get("saldo_atual", 0))
        except Exception:
            curr = 0.0
        new_saldo = curr + delta
        requests.patch(
            f"{url_base}/rest/v1/estoque?id_item=eq.{id_item}",
            headers=headers,
            json={
                "saldo_atual": str(new_saldo),
                "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
    else:
        item = buscar_item(id_item)
        if item:
            new_saldo = delta
            requests.post(
                f"{url_base}/rest/v1/estoque",
                headers=headers,
                json={
                    "id_item": id_item,
                    "nome": item.get("nome", ""),
                    "categoria": item.get("categoria", ""),
                    "local": item.get("local", ""),
                    "unidade": item.get("unidade", ""),
                    "saldo_atual": str(delta),
                    "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            )

    # Sincronização com Sheets em background — nunca bloqueia o usuário
    try:
        from utils.sheets import sincronizar_saldo
        item = buscar_item(id_item)
        if item:
            threading.Thread(
                target=sincronizar_saldo,
                args=(id_item, item.get("nome", ""), item.get("categoria", ""),
                      item.get("local", ""), item.get("unidade", ""), new_saldo),
                daemon=True,
            ).start()
    except Exception:
        pass

    _cache_rapido.clear()


# ── MOVIMENTOS ───────────────────────────────────────────────────────────────

def listar_movimentos(limit=200):
    df = ler("movimentos")
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df.sort_values("timestamp", ascending=False).head(limit)


def _proximo_id():
    df = ler("movimentos")
    if df.empty or "id" not in df.columns:
        return "MOV-00001"
    nums = [int(m.group()) for x in df["id"].dropna() if (m := re.search(r"\d+", str(x)))]
    return f"MOV-{(max(nums) + 1):05d}" if nums else "MOV-00001"


def registrar_movimento(tipo, id_item, quantidade, operador,
                        valor_unit="", fornecedor_id="", motivo="", obs=""):
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
    url_base, _, headers = _get_config()
    requests.post(f"{url_base}/rest/v1/movimentos", headers=headers, json=nova)

    # Sheets em background
    try:
        from utils.sheets import sincronizar_movimento
        threading.Thread(target=sincronizar_movimento, args=(nova,), daemon=True).start()
    except Exception:
        pass

    if tipo == "ENTRADA":
        _atualizar_saldo(id_item, qtd)
    elif tipo == "SAÍDA":
        _atualizar_saldo(id_item, -qtd)
    elif tipo == "AJUSTE":
        curr = saldo_item(id_item)
        _atualizar_saldo(id_item, qtd - curr)

    _cache_rapido.clear()


def registrar_movimento_batch(movimentos_list):
    """Registra N movimentos em lote: 1 POST para todos + saldos em paralelo."""
    if not movimentos_list:
        return

    df_mov = ler("movimentos")
    if df_mov.empty or "id" not in df_mov.columns:
        next_num = 1
    else:
        nums = [int(m.group()) for x in df_mov["id"].dropna()
                if (m := re.search(r"\d+", str(x)))]
        next_num = (max(nums) + 1) if nums else 1

    url_base, _, headers = _get_config()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_itens = ler("itens")
    df_comp = ler("composicao")

    def _nome(id_item):
        if df_itens.empty:
            return id_item
        row = df_itens[df_itens["id_item"] == id_item]
        return row.iloc[0]["nome"] if not row.empty else id_item

    records = []
    deltas = {}

    for i, mov in enumerate(movimentos_list):
        qtd = float(mov["quantidade"])
        vunit = float(mov.get("valor_unit") or 0)
        tipo = mov["tipo"]
        records.append({
            "id": f"MOV-{(next_num + i):05d}",
            "timestamp": now_str,
            "tipo": tipo,
            "id_item": mov["id_item"],
            "nome_item": mov.get("nome_item") or _nome(mov["id_item"]),
            "quantidade": str(qtd),
            "valor_unit": str(vunit),
            "total": str(round(qtd * vunit, 2)),
            "fornecedor_id": mov.get("fornecedor_id", ""),
            "motivo": mov.get("motivo", ""),
            "operador": mov["operador"],
            "obs": mov.get("obs", ""),
        })

        sinal = 1 if tipo == "ENTRADA" else (-1 if tipo == "SAÍDA" else 0)
        if sinal != 0:
            deltas[mov["id_item"]] = deltas.get(mov["id_item"], 0) + sinal * qtd
            if not df_comp.empty and "id_produto" in df_comp.columns:
                for _, ing in df_comp[df_comp["id_produto"] == mov["id_item"]].iterrows():
                    try:
                        q_ing = float(ing["quantidade"])
                    except Exception:
                        q_ing = 0.0
                    deltas[ing["id_ingrediente"]] = (
                        deltas.get(ing["id_ingrediente"], 0) + sinal * q_ing * qtd
                    )

    h = headers.copy()
    h["Prefer"] = "resolution=merge-duplicates"
    requests.post(f"{url_base}/rest/v1/movimentos", headers=h, json=records)

    threads = []
    for id_item, delta in deltas.items():
        if delta != 0:
            t = threading.Thread(target=_atualizar_saldo, args=(id_item, delta))
            threads.append(t)
            t.start()
    for t in threads:
        t.join()

    # Sheets em background
    try:
        from utils.sheets import inicializar_sheets
        threading.Thread(
            target=inicializar_sheets,
            args=(ler("itens"), ler("estoque"), ler("fornecedores"), ler("movimentos")),
            daemon=True,
        ).start()
    except Exception:
        pass

    _cache_rapido.clear()


# ── AUTENTICAÇÃO ─────────────────────────────────────────────────────────────

def autenticar(usuario, senha):
    df = ler("usuarios")
    if df.empty:
        return None
    row = df[(df["usuario"] == usuario) & (df["senha"] == senha) & (df["ativo"] == "Sim")]
    if not row.empty:
        r = row.iloc[0].to_dict()
        if "nome_completo" in r:
            r["nome"] = r["nome_completo"]
        return r
    return None


# ── COMPOSIÇÃO ───────────────────────────────────────────────────────────────

def listar_composicao():
    return ler("composicao")


def composicao_produto(id_produto):
    comp = listar_composicao()
    if comp.empty or "id_produto" not in comp.columns:
        return []
    res = comp[comp["id_produto"] == id_produto]
    return res.to_dict("records") if not res.empty else []


def is_composto(id_item):
    comp = listar_composicao()
    if comp.empty:
        return False
    return id_item in comp["id_produto"].values


def registrar_entrada_composta(id_produto, quantidade, operador,
                               nf="", valor_unit="", fornecedor_id="", obs=""):
    def _bg():
        registrar_movimento("ENTRADA", id_produto, quantidade, operador,
                            valor_unit=valor_unit, fornecedor_id=fornecedor_id,
                            motivo=f"NF: {nf}", obs=obs)
        for ing in composicao_produto(id_produto):
            try:
                q_ing = float(ing["quantidade"])
            except Exception:
                q_ing = 0.0
            _atualizar_saldo(ing["id_ingrediente"], q_ing * float(quantidade))
    threading.Thread(target=_bg, daemon=True).start()


def registrar_saida_composta(id_produto, quantidade, operador, motivo="", obs=""):
    def _bg():
        registrar_movimento("SAÍDA", id_produto, quantidade, operador, motivo=motivo, obs=obs)
        for ing in composicao_produto(id_produto):
            try:
                q_ing = float(ing["quantidade"])
            except Exception:
                q_ing = 0.0
            _atualizar_saldo(ing["id_ingrediente"], -(q_ing * float(quantidade)))
    threading.Thread(target=_bg, daemon=True).start()


# ── SAÍDA EM LOTE ─────────────────────────────────────────────────────────────

def registrar_saida_em_lote(lote, operador, motivo="", obs=""):
    for mov in lote:
        qtd = float(mov["quantidade"])
        if qtd <= 0:
            continue
        registrar_movimento("SAÍDA", mov["id_item"], qtd, operador, motivo=motivo, obs=obs)
        if is_composto(mov["id_item"]):
            for ing in composicao_produto(mov["id_item"]):
                try:
                    q_ing = float(ing["quantidade"])
                except Exception:
                    q_ing = 0.0
                _atualizar_saldo(ing["id_ingrediente"], -(q_ing * qtd))
    _cache_rapido.clear()


# ── MAPEAMENTO SWFAST ────────────────────────────────────────────────────────

def listar_mapeamentos():
    df = ler("mapeamento_swfast")
    if df.empty:
        return pd.DataFrame(columns=["codigo_swfast", "nome_swfast", "id_item", "ultima_atualizacao"])
    if "nome_swfast" in df.columns:
        return df.sort_values("nome_swfast")
    return df


def salvar_mapeamento(codigo_swfast, nome_swfast, id_item):
    df = ler("mapeamento_swfast")
    nova = pd.DataFrame([{
        "codigo_swfast": str(codigo_swfast),
        "nome_swfast": str(nome_swfast),
        "id_item": str(id_item),
        "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])
    if not df.empty and "codigo_swfast" in df.columns:
        df["codigo_swfast"] = df["codigo_swfast"].astype(str)
        df = df[df["codigo_swfast"] != str(codigo_swfast)]
    _salvar("mapeamento_swfast", pd.concat([df, nova], ignore_index=True))


def remover_mapeamento(codigo_swfast):
    df = ler("mapeamento_swfast")
    if not df.empty and "codigo_swfast" in df.columns:
        df["codigo_swfast"] = df["codigo_swfast"].astype(str)
        _salvar("mapeamento_swfast", df[df["codigo_swfast"] != str(codigo_swfast)])
