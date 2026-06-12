import re
import streamlit as st
import time
import random
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

def executar_com_retry(func, *args, max_retries=3, base_delay=2.0, **kwargs):
    """Executa uma função da API do Google Sheets com retentativas e recuo exponencial."""
    for tentativa in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if tentativa == max_retries - 1:
                raise e
            delay = base_delay * (2 ** tentativa) + random.uniform(0.1, 1.0)
            time.sleep(delay)

def _ler_credenciais():
    """Lê o secrets.toml diretamente do st.secrets."""
    import streamlit as st
    gcp = st.secrets["gcp_service_account"]
    pk = gcp["private_key"].replace('\\n', '\n')
    return {
        "type": gcp["type"],
        "project_id": gcp["project_id"],
        "private_key_id": gcp["private_key_id"],
        "private_key": pk,
        "client_email": gcp["client_email"],
        "client_id": gcp["client_id"],
        "auth_uri": gcp["auth_uri"],
        "token_uri": gcp["token_uri"],
        "auth_provider_x509_cert_url": gcp["auth_provider_x509_cert_url"],
        "client_x509_cert_url": gcp["client_x509_cert_url"],
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
        executar_com_retry(_conectar)
        return True
    except Exception:
        return False

def inicializar_sheets(df_itens, df_estoque, df_fornecedores, df_movimentos, df_usuarios=None):
    """Envia todos os dados para o Sheets em lote (batch). Lança exceção se falhar."""
    import pandas as pd
    sh = executar_com_retry(_conectar)
    for nome_aba, df in [
        ("ITENS",        df_itens),
        ("ESTOQUE",      df_estoque),
        ("FORNECEDORES", df_fornecedores),
        ("MOVIMENTOS",   df_movimentos),
    ]:
        ws   = executar_com_retry(_get_sheet, sh, nome_aba)
        cols = [c for c in HEADERS[nome_aba] if c in df.columns]
        executar_com_retry(ws.clear)
        
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
            executar_com_retry(ws.update, rows_to_write)
        except TypeError:
            # Compatibilidade com versões mais antigas do gspread
            executar_com_retry(ws.update, "A1", rows_to_write)

def sincronizar_movimento(linha: dict):
    try:
        sh  = executar_com_retry(_conectar)
        ws  = executar_com_retry(_get_sheet, sh, "MOVIMENTOS")
        row = [str(linha.get(h, "")) for h in HEADERS["MOVIMENTOS"]]
        executar_com_retry(ws.append_row, row)
        return True
    except Exception:
        return False

def sincronizar_saldo(id_item, nome, categoria, local, unidade, saldo):
    try:
        sh    = executar_com_retry(_conectar)
        ws    = executar_com_retry(_get_sheet, sh, "ESTOQUE")
        dados = executar_com_retry(ws.get_all_values)
        for i, row in enumerate(dados[1:], start=2):
            if row and row[0] == id_item:
                executar_com_retry(ws.update_cell, i, 6, str(round(saldo, 3)))
                executar_com_retry(ws.update_cell, i, 7, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                return True
        executar_com_retry(ws.append_row, [id_item, nome, categoria, local, unidade,
                       str(round(saldo, 3)),
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        return True
    except Exception:
        return False
