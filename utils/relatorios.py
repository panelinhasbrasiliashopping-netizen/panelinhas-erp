import base64
import os
from datetime import datetime

def get_logo_b64():
    path = os.path.join(os.path.dirname(__file__), '..', 'logo.png')
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def gerar_html_inventario(df_estoque):
    logo = get_logo_b64()
    img_tag = f'<img src="data:image/png;base64,{logo}" class="logo" />' if logo else '<h2>Panelinhas</h2>'
    
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Inventário - Panelinhas</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        body {{
            font-family: 'Outfit', sans-serif;
            color: #222;
            margin: 0;
            padding: 40px;
            background-color: #f9f9f9;
            font-size: 13px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: #fff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #E85D04;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .logo {{
            max-width: 160px;
        }}
        .title-box h2 {{
            margin: 0;
            font-size: 28px;
            color: #1a1a1a;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .title-box p {{
            margin: 4px 0 0 0;
            color: #888;
            font-size: 13px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }}
        th {{
            background-color: #f0f0f0;
            color: #333;
            text-align: left;
            padding: 12px;
            font-weight: 700;
            border-bottom: 2px solid #ddd;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
            vertical-align: middle;
        }}
        tr:nth-child(even) {{
            background-color: #fafafa;
        }}
        .category-header {{
            background-color: #1A1715 !important;
            color: #FFF8F0 !important;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .category-header td {{
            padding: 14px 12px;
            border-bottom: none;
        }}
        .status-ok {{
            background-color: #DCFCE7;
            color: #14532D;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 11px;
        }}
        .status-critico {{
            background-color: #FFF3CC;
            color: #78350F;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 11px;
        }}
        .status-zerado {{
            background-color: #FFE8E8;
            color: #7F1D1D;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 11px;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 11px;
            color: #aaa;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .container {{ box-shadow: none; padding: 0; margin: 0; width: 100%; max-width: 100%; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title-box">
                <h2>Inventário de Estoque</h2>
                <p>Posição atual gerada em: {agora}</p>
            </div>
            <div>
                {img_tag}
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 15%;">Código</th>
                    <th style="width: 45%;">Produto</th>
                    <th style="width: 15%; text-align: right;">Saldo</th>
                    <th style="width: 10%;">Und</th>
                    <th style="width: 15%; text-align: center;">Status</th>
                </tr>
            </thead>
            <tbody>"""
    
    # Ordenar por Categoria e depois Produto
    df_estoque = df_estoque.sort_values(by=["Categoria", "Produto"])
    
    categoria_atual = None
    
    for _, row in df_estoque.iterrows():
        import pandas as pd
        
        cat = row.get("Categoria", "Sem Categoria")
        if pd.isna(cat) or str(cat).strip() == "":
            cat = "Sem Categoria"
            
        # Se mudou de categoria, imprime a linha de cabeçalho da categoria
        if cat != categoria_atual:
            html += f"""
                <tr class="category-header">
                    <td colspan="5">📦 {cat}</td>
                </tr>"""
            categoria_atual = cat
            
        status = str(row.get("Status", "OK")).upper()
        if "ZERADO" in status:
            badge = '<span class="status-zerado">ZERADO</span>'
        elif "CRÍTICO" in status or "CRITICO" in status:
            badge = '<span class="status-critico">CRÍTICO</span>'
        else:
            badge = '<span class="status-ok">OK</span>'
            
        codigo = row.get("Código", "")
        produto = row.get("Produto", "")
        saldo = row.get("Saldo", 0)
        und = row.get("Und", "")
        
        try:
            saldo_fmt = f"{float(saldo):.2f}".replace(".", ",")
        except:
            saldo_fmt = str(saldo)
            
        html += f"""
                <tr>
                    <td><strong>{codigo}</strong></td>
                    <td>{produto}</td>
                    <td style="text-align: right; font-weight: 600;">{saldo_fmt}</td>
                    <td>{und}</td>
                    <td style="text-align: center;">{badge}</td>
                </tr>"""
        
    html += """
            </tbody>
        </table>
        
        <div class="footer">
            Relatório gerado automaticamente pelo ERP Panelinhas do Brasil
        </div>
    </div>
</body>
</html>"""
    return html
