import re
import streamlit as st
from datetime import datetime
from pathlib import Path

SPREADSHEET_ID = "1v7eEbP49FiwU34ob3d4OBobIQ3BuCIrE-E2k2Y3pUR4"

HEADERS = {
    "MOVIMENTOS":  ["id","timestamp","tipo","id_item","nome_item","quantidade",
                    "valor_unit","total","fornecedor_id","motivo","operador","obs"],
    "ESTOQUE":     ["id_item","nome","categoria","local","unidade",
                    "saldo_atual","ultima_atualizacao"],
    "ITENS":       ["id_item","nome","descricao","categoria","subcategoria",
                    "unidade","local","estoque_minimo","estoque_maximo",
                    "custo_unitario","fornecedor_id","ativo","obs"],
    "FORNECEDORES":["id_fornecedor","nome","nome_curto","cnpj","contato",
                    "telefone","email","prazo_dias","frequencia","status","obs"],
}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def _ler_credenciais():
    """Lê o secrets.toml diretamente do disco — sem cache."""
    secrets_path = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"
    content = secrets_path.read_text(encoding="utf-8")

    def extract(field):
        m = re.search(rf'{field}\s*=\s*"([^"]+)"', content)
        return m.group(1) if m else ""

    key_match = re.search(r'private_key\s*=\s*"""(.*?)"""', content, re.DOTALL)
    if not key_match:
        key_match = re.search(r'private_key\s*=\s*"(.*?)"', content, re.DOTALL)
    pk = key_match.group(1).replace('\\n', '\n') if key_match else ""

    return {
        "type": "service_account",
        "project_id":   extract("project_id"),
        "private_key_id": extract("private_key_id"),
        "private_key":  pk,
        "client_email": extract("client_email"),
        "client_id":    extract("client_id"),
        "auth_uri":     extract("auth_uri"),
        "token_uri":    extract("token_uri"),
        "auth_provider_x509_cert_url": extract("auth_provider_x509_cert_url"),
        "client_x509_cert_url": extract("client_x509_cert_url"),
    }

def _conectar():
    """Abre conexão fresca com o Sheets — sem cache."""
    import gspread
    from google.oauth2.service_account import Credentials
    info  = _ler_credenciais()
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    gc    = gspread.authorize(creds)
    return gc.open_by_key(SPREADSHEET_ID)

def _get_sheet(sh, nome_aba):
    try:
        return sh.worksheet(nome_aba)
    except Exception:
        ws = sh.add_worksheet(title=nome_aba, rows=2000, cols=20)
        if nome_aba in HEADERS:
            ws.append_row(HEADERS[nome_aba])
        return ws

def sheets_ok():
    try:
        _conectar()
        return True
    except Exception:
        return False

def inicializar_sheets(df_itens, df_estoque, df_fornecedores):
    """Envia todos os dados para o Sheets em lote (batch). Lança exceção se falhar."""
    import pandas as pd
    sh = _conectar()  # vai lançar exceção se falhar — sem silêncio
    for nome_aba, df in [
        ("ITENS",        df_itens),
        ("ESTOQUE",      df_estoque),
        ("FORNECEDORES", df_fornecedores),
    ]:
        ws   = _get_sheet(sh, nome_aba)
        cols = [c for c in HEADERS[nome_aba] if c in df.columns]
        ws.clear()
        
        # Constrói o lote de dados (cabeçalho + linhas)
        rows_to_write = [cols]
        for _, row in df[cols].iterrows():
            row_vals = []
            for v in row.values:
                if v is None or pd.isna(v):
                    row_vals.append("")
                else:
                    row_vals.append(str(v))
            rows_to_write.append(row_vals)
            
        # Envia todas as linhas de uma vez só (1 única chamada de API)
        try:
            ws.update(rows_to_write)
        except TypeError:
            # Compatibilidade com versões mais antigas do gspread
            ws.update("A1", rows_to_write)

def sincronizar_movimento(linha: dict):
    try:
        sh  = _conectar()
        ws  = _get_sheet(sh, "MOVIMENTOS")
        row = [str(linha.get(h, "")) for h in HEADERS["MOVIMENTOS"]]
        ws.append_row(row)
        return True
    except Exception:
        return False

def sincronizar_saldo(id_item, nome, categoria, local, unidade, saldo):
    try:
        sh    = _conectar()
        ws    = _get_sheet(sh, "ESTOQUE")
        dados = ws.get_all_values()
        for i, row in enumerate(dados[1:], start=2):
            if row and row[0] == id_item:
                ws.update_cell(i, 6, str(round(saldo, 3)))
                ws.update_cell(i, 7, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                return True
        ws.append_row([id_item, nome, categoria, local, unidade,
                       str(round(saldo, 3)),
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        return True
    except Exception:
        return False
