import pandas as pd
import pdfplumber
import re
import io

def parse_swfast_file(file_obj, filename):
    """
    Função principal que detecta a extensão do arquivo (Excel ou PDF)
    e chama o parser correspondente.
    Retorna uma lista de dicionários:
    [{"codigo_swfast": "50072", "nome_swfast": "INS ANGU", "quantidade": 5.0}]
    """
    fn_lower = filename.lower()
    if fn_lower.endswith(('.xlsx', '.xls')):
        return parse_swfast_excel(file_obj)
    elif fn_lower.endswith('.pdf'):
        # pdfplumber pode precisar ler o arquivo como bytes.
        # Se for st.UploadedFile, já se comporta como file-like object.
        return parse_swfast_pdf(file_obj)
    else:
        raise ValueError("Formato de arquivo não suportado. Envie um arquivo Excel (.xlsx, .xls) ou PDF.")

def parse_swfast_excel(file_obj):
    """
    Lê a planilha Excel (.xlsx / .xls) do SWFast, detectando se é o relatório
    de Insumos ou de Produtos vendidos, e extrai os itens.
    """
    # Lê todo o Excel sem cabeçalhos definidos para analisar a estrutura
    df = pd.read_excel(file_obj, header=None)
    
    # Detecta se é o relatório de Insumos procurando o termo 'Preço médio'
    is_insumos = False
    for r in range(df.shape[0]):
        for c in range(df.shape[1]):
            val = str(df.iloc[r, c])
            if 'Preço médio' in val:
                is_insumos = True
                break
        if is_insumos:
            break
            
    parsed_items = []
    col_prod = 3  # Coluna D (índice 3) contém o código-nome do produto
    col_qty = 6 if is_insumos else 9  # Coluna G (índice 6) para Insumos, Coluna J (índice 9) para Produtos
    
    for r in range(df.shape[0]):
        if r >= df.shape[0] or col_prod >= df.shape[1] or col_qty >= df.shape[1]:
            continue
        prod_val = df.iloc[r, col_prod]
        if pd.isnull(prod_val):
            continue
        prod_str = str(prod_val).strip()
        
        # Expressão regular para casar [Código]-[Nome]
        # Ex: "50072- INS ANGU" -> "50072", "INS ANGU"
        m = re.match(r'^(\d+)\s*-\s*(.*)$', prod_str)
        if not m:
            continue
            
        code = m.group(1)
        desc = m.group(2)
        
        qty_val = df.iloc[r, col_qty]
        if pd.isnull(qty_val):
            continue
            
        try:
            if isinstance(qty_val, (int, float)):
                qty = float(qty_val)
            else:
                qty_str = str(qty_val).replace('.', '').replace(',', '.')
                qty = float(qty_str)
                
            parsed_items.append({
                'codigo_swfast': code,
                'nome_swfast': desc,
                'quantidade': qty
            })
        except ValueError:
            continue
            
    return parsed_items

def parse_swfast_pdf(file_obj):
    """
    Lê o relatório em PDF do SWFast, detectando se é de Insumos ou Produtos,
    e extrai os itens usando pdfplumber.
    """
    parsed_items = []
    
    # Se file_obj for bytes, envolvemos em BytesIO
    if isinstance(file_obj, bytes):
        file_obj = io.BytesIO(file_obj)
        
    with pdfplumber.open(file_obj) as pdf:
        text_all = ""
        for page in pdf.pages:
            text_all += page.extract_text() + "\n"
            
        is_insumos = 'VENDA DE INSUMOS' in text_all or 'Preço médio' in text_all
        is_produtos = 'VENDA DE PRODUTOS' in text_all
        
        for line in text_all.split('\n'):
            line = line.strip()
            tokens = line.split()
            if len(tokens) < 3:
                continue
                
            try:
                def parse_br_float(val):
                    return float(val.replace('.', '').replace(',', '.'))
                
                if is_insumos:
                    if len(tokens) < 4:
                        continue
                    qty = parse_br_float(tokens[-3])
                    product_id = ' '.join(tokens[:-3])
                elif is_produtos:
                    qty = parse_br_float(tokens[-2])
                    product_id = ' '.join(tokens[:-2])
                else:
                    continue
                
                # Expressão regular para separar código e descrição
                m = re.match(r'^(\d+)\s*-\s*(.*)$', product_id)
                if m:
                    code = m.group(1)
                    desc = m.group(2)
                else:
                    parts = product_id.split('-', 1)
                    if len(parts) == 2:
                        code = parts[0].strip()
                        desc = parts[1].strip()
                    else:
                        code = 'N/A'
                        desc = product_id
                
                # Desconsidera falsos positivos sem código numérico
                if code == 'N/A' or not code.isdigit():
                    continue
                    
                parsed_items.append({
                    "codigo_swfast": code,
                    "nome_swfast": desc,
                    "quantidade": qty
                })
            except (ValueError, IndexError):
                continue
                
    return parsed_items
