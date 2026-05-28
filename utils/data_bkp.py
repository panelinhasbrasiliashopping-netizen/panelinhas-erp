import pandas as pd
import streamlit as st
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def _path(nome): return DATA_DIR / f"{nome}.csv"

@st.cache_data(ttl=30)
def _ler_cached(nome):
    return pd.read_csv(_path(nome), dtype=str).fillna("")

def ler(nome):
    return _ler_cached(nome).copy()

def _salvar(nome, df):
    df.to_csv(_path(nome), index=False)
    _ler_cached.clear()

# ── Itens ──────────────────────────────────────────────
def listar_itens():
    return ler("itens")

def buscar_item(id_item):
    df = ler("itens")
    r  = df[df["id_item"] == id_item]
    return r.iloc[0] if not r.empty else None

# ── Fornecedores ───────────────────────────────────────
def listar_fornecedores():
    return ler("fornecedores")

# ── Estoque ────────────────────────────────────────────
def listar_estoque():
    est   = ler("estoque")
    itens = ler("itens")[["id_item","estoque_minimo","estoque_maximo",
                           "custo_unitario","fornecedor_id"]]
    return est.merge(itens, on="id_item", how="left")

def saldo_item(id_item):
    est = ler("estoque")
    r   = est[est["id_item"] == id_item]
    return float(r.iloc[0]["saldo_atual"]) if not r.empty else 0.0

def _atualizar_saldo(id_item, delta):
    from utils.sheets import sincronizar_saldo
    est = ler("estoque")
    idx = est.index[est["id_item"] == id_item]
    if idx.empty: return
    i = idx[0]
    saldo = round(max(float(est.at[i, "saldo_atual"]) + delta, 0), 3)
    est.at[i, "saldo_atual"]        = str(saldo)
    est.at[i, "ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _salvar("estoque", est)
    # Sincroniza com Sheets em background (não bloqueia a interface)
    try:
        import threading
        row = est.iloc[i]
        threading.Thread(
            target=sincronizar_saldo, 
            args=(id_item, row.get("nome",""), row.get("categoria",""), row.get("local",""), row.get("unidade",""), saldo),
            daemon=True
        ).start()
    except Exception:
        pass

# ── Movimentos ─────────────────────────────────────────
def _proximo_id():
    df = ler("movimentos")
    if df.empty or df["id"].str.strip().eq("").all():
        return "MOV-00001"
    nums = df["id"].str.extract(r'(\d+)')[0].dropna().astype(int)
    return f"MOV-{(nums.max()+1):05d}"

def registrar_movimento(tipo, id_item, quantidade, operador,
                        valor_unit="", fornecedor_id="", motivo="", obs=""):
    from utils.sheets import sincronizar_movimento
    item      = buscar_item(id_item)
    nome_item = item["nome"] if item is not None else id_item
    qtd       = float(quantidade)
    vunit     = float(valor_unit) if valor_unit else 0.0

    nova = {
        "id":            _proximo_id(),
        "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo":          tipo,
        "id_item":       id_item,
        "nome_item":     nome_item,
        "quantidade":    qtd,
        "valor_unit":    vunit,
        "total":         round(qtd * vunit, 2),
        "fornecedor_id": fornecedor_id,
        "motivo":        motivo,
        "operador":      operador,
        "obs":           obs,
    }

    # Salva no CSV
    df = ler("movimentos")
    df = pd.concat([df, pd.DataFrame([nova])], ignore_index=True)
    _salvar("movimentos", df)

    # Sincroniza com Sheets em background
    try:
        import threading
        threading.Thread(target=sincronizar_movimento, args=(nova,), daemon=True).start()
    except Exception:
        pass

    # Atualiza saldo
    delta = qtd if tipo in ("ENTRADA", "AJUSTE_POS") else -qtd
    _atualizar_saldo(id_item, delta)

def listar_movimentos(limit=200):
    df = ler("movimentos")
    if df.empty: return df
    df = df[df["id"].str.strip() != ""].copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df.sort_values("timestamp", ascending=False).head(limit)

# ── Auth ───────────────────────────────────────────────
def autenticar(usuario, senha):
    df = ler("usuarios")
    r  = df[(df["usuario"] == usuario) & (df["senha"] == senha) & (df["ativo"] == "Sim")]
    if r.empty: return None
    return {"usuario": r.iloc[0]["usuario"],
            "perfil":  r.iloc[0]["perfil"],
            "nome":    r.iloc[0]["nome_completo"]}

# ── Status ─────────────────────────────────────────────
def status_item(saldo, minimo):
    s, m = float(saldo), float(minimo)
    if s <= 0:  return "🔴 ZERADO"
    if s <= m:  return "🟡 CRÍTICO"
    return              "🟢 OK"

# ── Composição (BOM) ───────────────────────────────────
def listar_composicao():
    try:
        return ler("composicao")
    except Exception:
        import pandas as pd
        return pd.DataFrame(columns=["id_produto","nome_produto","id_ingrediente",
                                     "nome_ingrediente","quantidade","unidade"])

def composicao_produto(id_produto):
    """Retorna lista de ingredientes de um produto composto."""
    df = listar_composicao()
    r  = df[df["id_produto"] == id_produto]
    return r.to_dict('records') if not r.empty else []

def is_composto(id_item):
    """True se o item tem composição cadastrada."""
    return len(composicao_produto(id_item)) > 0

def registrar_entrada_composta(id_produto, quantidade, operador, nf="", valor_unit="", fornecedor_id="", obs=""):
    """
    Registra entrada de produto composto:
    - 1 movimento do produto (PAN)
    - N movimentos dos ingredientes (ING), adicionados proporcionalmente
    """
    quantidade = float(quantidade)
    composicao = composicao_produto(id_produto)

    # Registra entrada do kit (PAN)
    registrar_movimento(
        "ENTRADA", id_produto, quantidade, operador,
        valor_unit=valor_unit, fornecedor_id=fornecedor_id,
        motivo=f"NF: {nf}" if nf else "", obs=obs
    )

    # Explode e dá entrada nos ingredientes
    for ing in composicao:
        id_ing   = ing["id_ingrediente"]
        qtd_ing  = float(ing["quantidade"]) * quantidade
        registrar_movimento(
            "ENTRADA", id_ing, qtd_ing, operador,
            motivo=f"Entrada em Lote - Embutido no Kit {id_produto}",
            obs=obs
        )

def registrar_saida_composta(id_produto, quantidade, operador, motivo="", obs=""):
    """
    Registra saída de produto composto:
    - 1 movimento do produto (PAN)
    - N movimentos dos ingredientes (ING), descontados automaticamente
    Retorna lista de ingredientes descontados.
    """
    quantidade = float(quantidade)
    composicao = composicao_produto(id_produto)

    # Registra saída do produto composto
    registrar_movimento("SAÍDA", id_produto, quantidade, operador,
                        motivo=motivo, obs=obs)

    # Explode e desconta cada ingrediente
    descontados = []
    for ing in composicao:
        id_ing   = ing["id_ingrediente"]
        qtd_ing  = float(ing["quantidade"]) * quantidade
        nome_ing = ing["nome_ingrediente"]

        registrar_movimento(
            "SAÍDA", id_ing, qtd_ing, operador,
            motivo=f"Consumo automático — {id_produto} × {quantidade:.0f}",
            obs=obs
        )
        saldo_ing = saldo_item(id_ing)
        descontados.append({
            "id":    id_ing,
            "nome":  nome_ing,
            "qtd_descontada": qtd_ing,
            "saldo_restante": saldo_ing,
        })

    return descontados
