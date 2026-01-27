from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A7
from reportlab.lib.units import mm
import os
import src.database as database
import src.utils as utils
from datetime import datetime

def gerar_recibo(venda_id, vendedor_info=None):
    """Gera um recibo PDF simples para a venda."""
    try:
        conn = database.conectar()
        cursor = conn.cursor()
        
        # Obter dados da venda
        cursor.execute("SELECT * FROM vendas WHERE id = ?", (venda_id,))
        venda = cursor.fetchone()
        
        # Obter itens
        cursor.execute('''
            SELECT p.nome, i.quantidade, i.preco_unitario 
            FROM itens_venda i
            JOIN produtos p ON i.produto_id = p.id
            WHERE i.venda_id = ?
        ''', (venda_id,))
        itens = cursor.fetchall()
        conn.close()
        
        if not venda:
            print("Venda não encontrada.")
            return

        # Salvar em Documentos/GestorFacil
        filename = utils.get_documents_path(f"recibo_venda_{venda_id}.pdf")
        c = canvas.Canvas(filename, pagesize=(80*mm, 200*mm)) # Tamanho térmico aproximado
        
        y = 190 * mm
        x = 5 * mm
        line_height = 5 * mm
        
        # Logo
        # Tentar carregar logotipo.png
        try:
            logoo = utils.resource_path(os.path.join("assets", "logotipo.png"))
            if os.path.exists(logoo):
                c.drawImage(logoo, x + 20*mm, y - 15*mm, width=30*mm, height=15*mm, mask='auto', preserveAspectRatio=True)
                y -= 20 * mm
        except: pass
        
        # Cabeçalho
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, "GESTOR FÁCIL - MPE")
        y -= line_height * 2
        
        c.setFont("Helvetica", 8)
        c.drawString(x, y, f"Venda #: {venda['id']}")
        y -= line_height
        c.drawString(x, y, f"Data: {venda['data_hora']}")
        y -= line_height
        
        # Cliente
        cliente = venda['cliente'] if venda['cliente'] else "Consumidor Final"
        c.drawString(x, y, f"Cliente: {cliente}")
        y -= line_height * 2
        
        # Itens
        c.drawString(x, y, "Item | Qtd | Preço")
        y -= line_height
        c.line(x, y+2, 75*mm, y+2)
        y -= 2*mm
        
        total_qty = 0
        for item in itens:
            nome = item['nome'][:15] # Truncar nome
            qtd = item['quantidade']
            preco = item['preco_unitario']
            
            c.drawString(x, y, f"{nome}")
            c.drawString(x+40*mm, y, f"{qtd} x {preco:.2f}")
            y -= line_height
            total_qty += qtd
            
        y -= line_height
        c.line(x, y+2, 75*mm, y+2)
        
        # Total
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, f"TOTAL: {utils.formatar_moeda(venda['total_venda'])}")
        
        y -= line_height * 3
        c.setFont("Helvetica", 7)
        c.drawString(x, y, "Obrigado pela preferência!")
        
        # Vendedor Info
        if vendedor_info:
             y -= line_height * 2
             c.setFont("Helvetica", 7)
             if vendedor_info.get('nome'):
                 c.drawString(x, y, f"Atendido por: {vendedor_info['nome']}")
                 y -= line_height
             if vendedor_info.get('whatsapp'):
                 c.drawString(x, y, f"Contato: {vendedor_info['whatsapp']}")
                 y -= line_height
             if vendedor_info.get('email'):
                 c.drawString(x, y, f"Email: {vendedor_info['email']}")

        c.save()
        print(f"Recibo gerado: {filename}")
        
        return filename
        
    except Exception as e:
        print(f"Erro ao gerar recibo: {e}")
        return None

def gerar_relatorio_mensal(ano, mes):
    """Gera relatório financeiro mensal com gráficos."""
    import pandas as pd
    import matplotlib.pyplot as plt
    from reportlab.lib.pagesizes import A4
    
    try:
        # Configurar backend do matplotlib para não precisar de GUI
        plt.switch_backend('Agg')
        
        # 1. Obter Dados
        dados_mes = database.get_vendas_mes(ano, mes)
        dados_despesas = database.get_despesas_mes(ano, mes) # Buscar despesas
        dados_7dias = database.get_vendas_ultimos_7_dias()
        
        if not dados_mes and not dados_despesas:
            print("Sem dados para este mês.")
            
        # 2. Processar Totais
        # dados_mes agora tem 4 colunas: data, total, lucro, vendedor
        # row_factory=Row, mas se passarmos para DataFrame direto pode dar zebra se nao convertermos
        # Vamos usar lista de dicts ou deixar o pandas se virar com as Rows (que sao iteraveis como tuplas)
        # Se for tuple: (data, total, lucro, vendedor)
        
        df_mes = pd.DataFrame(dados_mes, columns=['data', 'total', 'lucro', 'vendedor'])
        total_vendido = df_mes['total'].sum() if not df_mes.empty else 0.0
        total_lucro_bruto = df_mes['lucro'].sum() if not df_mes.empty else 0.0
        total_custo_prod = total_vendido - total_lucro_bruto
        
        # Processar Despesas
        total_despesas = 0.0
        if dados_despesas:
             # dados_despesas é lista de rows, índice 4 é valor (id, data, desc, cat, valor)
             total_despesas = sum(d['valor'] for d in dados_despesas)
             
        lucro_liquido = total_lucro_bruto - total_despesas
        
        # 3. Gerar Gráfico (Temp)
        img_path = utils.get_writable_path("temp_grafico_relatorio.png")
        import src.charts as charts
        charts.gerar_grafico_vendas_7dias(img_path)
        
        # 4. Gerar PDF (Documentos)
        filename = utils.get_documents_path(f"Relatorio_Mensal_{mes}_{ano}.pdf")
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Logo (Canto Superior Direito)
        try:
            logo_path = utils.resource_path(os.path.join("assets", "logotipo.png"))
            if os.path.exists(logo_path):
                logo_w = 40*mm
                logo_h = 40*mm
                # Posicao: X = Direita - Margem - Largura, Y = Topo - Margem - Altura
                c.drawImage(logo_path, width - 20*mm - logo_w, height - 10*mm - logo_h, 
                           width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
        except: pass
        
        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(20*mm, height - 20*mm, f"Relatório Mensal - {mes}/{ano}")
        c.setFont("Helvetica", 10)
        c.drawString(20*mm, height - 28*mm, "Gestor Fácil - Análise de Desempenho")
        
        c.line(20*mm, height - 32*mm, width - 20*mm, height - 32*mm)
        
        # Resumo Financeiro
        y = height - 50*mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20*mm, y, "Resumo Financeiro:")
        y -= 10*mm
        
        c.setFont("Helvetica", 10)
        c.drawString(30*mm, y, f"Total Vendido:       {utils.formatar_moeda(total_vendido)}")
        y -= 6*mm
        c.drawString(30*mm, y, f"Custo Produtos:      {utils.formatar_moeda(total_custo_prod)}")
        y -= 6*mm
        c.drawString(30*mm, y, f"Lucro Bruto:         {utils.formatar_moeda(total_lucro_bruto)}")
        y -= 6*mm
        c.setFillColorRGB(0.8, 0, 0) # Vermelho
        c.drawString(30*mm, y, f"Despesas Operac.:  - {utils.formatar_moeda(total_despesas)}")
        c.setFillColorRGB(0, 0, 0)
        y -= 8*mm
        
        c.setFont("Helvetica-Bold", 12)
        if lucro_liquido >= 0:
            c.setFillColorRGB(0, 0.5, 0) # Verde
        else:
            c.setFillColorRGB(0.8, 0, 0) # Vermelho
            
        c.drawString(30*mm, y, f"LUCRO LÍQUIDO:   {utils.formatar_moeda(lucro_liquido)}")
        c.setFillColorRGB(0, 0, 0)
        
        # Tabela de Vendas por Vendedor (Novo)
        y -= 25*mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20*mm, y, "Vendas por Vendedor:")
        y -= 8*mm
        
        c.setFont("Helvetica", 9)
        # Processar agregado manual (ja que nao temos pandas group by facil aqui sem recarregar)
        vendas_por_user = {} # nome -> total
        for row in dados_mes:
            # row: data, total, lucro, vendedor_nome
            v_nome = row['vendedor_nome'] if row['vendedor_nome'] else "Não Identificado"
            v_total = row['total_venda'] # Agora indexacao por nome nas rows? Row factory=sqlite3.Row
            # Row factory permite access por nome se definido no select.
            # No select: data_hora, total_venda, lucro_total, vendedor_nome
            
            # Se for sqlite3.Row, podemos usar ['total_venda']
            if v_nome not in vendas_por_user: vendas_por_user[v_nome] = 0.0
            vendas_por_user[v_nome] += row['total_venda']
            
        if not vendas_por_user:
            c.drawString(30*mm, y, "- Sem dados de vendedores.")
            y -= 6*mm
        else:
            for nome, val in vendas_por_user.items():
                c.drawString(30*mm, y, f"{nome}: {utils.formatar_moeda(val)}")
                y -= 6*mm
        
        # Gráfico
        y -= 15*mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20*mm, y, "Evolução Recente:")
        
        # Inserir imagem do gráfico
        # Ajustar posição Y baseado na altura da imagem
        c.drawImage(img_path, 20*mm, y - 90*mm, width=160*mm, height=80*mm)
        
        # Rodapé
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(20*mm, 20*mm, "Documento gerado automaticamente para fins de controlo interno.")
        
        c.save()
        
        # Limpar temp
        if os.path.exists(img_path):
            os.remove(img_path)
            
        return filename
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return None

def gerar_cotacao(itens, total, cliente_nome, vendedor_info=None):
    """Gera um PDF de cotação (similar ao recibo, mas sem valor fiscal)."""
    try:
        # Salvar em Documentos/GestorFacil
        filename = utils.get_documents_path(f"cotacao_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
        c = canvas.Canvas(filename, pagesize=(80*mm, 200*mm))
        
        y = 190 * mm
        x = 5 * mm
        line_height = 5 * mm
        
        # Logo
        logo_path = utils.resource_path(os.path.join("assets", "logotipo.png"))
        if os.path.exists(logo_path):
            c.drawImage(logo_path, x + 20*mm, y - 15*mm, width=30*mm, height=15*mm, mask='auto')
            y -= 20 * mm
        
        # Cabeçalho
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, "GESTOR FÁCIL - MPE")
        y -= line_height * 1.5
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "COTAÇÃO DE PREÇOS")
        y -= line_height
        
        c.setFont("Helvetica", 8)
        c.drawString(x, y, f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        y -= line_height
        
        # Cliente
        cliente = cliente_nome if cliente_nome else "Consumidor Final"
        c.drawString(x, y, f"Cliente: {cliente}")
        y -= line_height * 2
        
        # Itens
        c.drawString(x, y, "Item | Qtd | Preço")
        y -= line_height
        c.line(x, y+2, 75*mm, y+2)
        y -= 2*mm
        
        for item in itens:
            # item = {'nome':..., 'qtd':..., 'preco_venda':..., 'total':...}
            nome = item['nome'][:15]
            qtd = item['qtd']
            preco = item['preco_venda']
            
            c.drawString(x, y, f"{nome}")
            c.drawString(x+40*mm, y, f"{qtd} x {preco:.2f}")
            y -= line_height
            
        y -= line_height
        c.line(x, y+2, 75*mm, y+2)
        
        # Total
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, f"TOTAL: {utils.formatar_moeda(total)}")
        
        y -= line_height * 3
        c.setFont("Helvetica", 7)
        c.drawString(x, y, "Válido por 15 dias.")
        y -= line_height
        c.drawString(x, y, "Documento sem valor fiscal.")
        
        # Vendedor Info
        if vendedor_info:
             y -= line_height * 2
             c.setFont("Helvetica", 7)
             if vendedor_info.get('nome'):
                 c.drawString(x, y, f"Atendido por: {vendedor_info['nome']}")
                 y -= line_height
             if vendedor_info.get('whatsapp'):
                 c.drawString(x, y, f"Contato: {vendedor_info['whatsapp']}")
                 y -= line_height
             if vendedor_info.get('email'):
                 c.drawString(x, y, f"Email: {vendedor_info['email']}")
        
        c.save()
        print(f"Cotação gerada: {filename}")
        return filename
        
    except Exception as e:
        print(f"Erro ao gerar cotação: {e}")
        return None
