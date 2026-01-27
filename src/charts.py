import matplotlib
# Configurar backend não-interativo ANTES de importar pyplot para evitar erros em threads/exe
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import src.database as database

def gerar_grafico_vendas_7dias(output_path):
    """
    Gera uma imagem do gráfico de vendas dos últimos 7 dias.
    Retorna True se gerou com sucesso, False caso contrário.
    """
    try:
        # Configurar backend para não precisar de GUI
        plt.switch_backend('Agg')
        
        dados_7dias = database.get_vendas_ultimos_7_dias()
        
        plt.figure(figsize=(6, 3))
        
        # Cores do Tema Deep Ocean
        bg_color = '#1E293B' # COLOR_SURFACE
        text_color = '#F8FAFC' # COLOR_TEXT
        bar_color = '#10B981' # Green for consistency
        
        # Configurar cores globais para este plot
        plt.rcParams['text.color'] = text_color
        plt.rcParams['axes.labelcolor'] = text_color
        plt.rcParams['xtick.color'] = text_color
        plt.rcParams['ytick.color'] = text_color
        
        if dados_7dias:
            df_7dias = pd.DataFrame(dados_7dias, columns=['data', 'total'])
            df_7dias['data_fmt'] = pd.to_datetime(df_7dias['data']).dt.strftime('%d/%m')
            
            # Criar axes com fundo correto
            ax = plt.gca()
            ax.set_facecolor(bg_color)
            plt.gcf().set_facecolor(bg_color)
            
            plt.bar(df_7dias['data_fmt'], df_7dias['total'], color=bar_color)
            
            plt.title('Vendas dos Últimos 7 Dias', fontsize=10, color=text_color)
            plt.xlabel('Data', fontsize=8, color=text_color)
            plt.ylabel('Vendas (MT)', fontsize=8, color=text_color)
            
            plt.xticks(fontsize=8, rotation=0)
            plt.yticks(fontsize=8)
            
            # Remover bordas desnecessárias e pintar as restantes
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color(text_color)
            ax.spines['left'].set_color(text_color)
            
            plt.tight_layout()
        else:
            plt.gcf().set_facecolor(bg_color)
            plt.text(0.5, 0.5, 'Sem dados recentes', ha='center', va='center', color=text_color)
            plt.axis('off')
            
        plt.savefig(output_path, dpi=100, facecolor=bg_color) # Salvar com fundo colorido
        plt.close()
        return True
        
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")
        return False

def gerar_grafico_top_produtos(output_path):
    """
    Gera gráfico de barras horizontais dos top 5 produtos.
    """
    try:
        plt.switch_backend('Agg')
        dados = database.get_top_produtos(5)
        
        plt.figure(figsize=(6, 4)) # Um pouco mais alto
        
        # Cores do Tema
        bg_color = '#1E293B'
        text_color = '#F8FAFC'
        bar_color = '#0EA5E9' # Blue for Top Prod
        
        if dados:
            df = pd.DataFrame(dados, columns=['nome', 'total'])
            df = df.sort_values(by='total', ascending=True)
            
            ax = plt.gca()
            ax.set_facecolor(bg_color)
            plt.gcf().set_facecolor(bg_color)
            
            plt.barh(df['nome'], df['total'], color=bar_color)
            
            plt.title('5 Produtos Mais Vendidos', fontsize=12, color=text_color)
            plt.xlabel('Quantidade Vendida', fontsize=10, color=text_color)
            
            # Cores dos eixos
            plt.tick_params(axis='x', colors=text_color)
            plt.tick_params(axis='y', colors=text_color)
            
            # Remover bordas
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color(text_color)
            ax.spines['left'].set_color(text_color)
            
            plt.tight_layout()
        else:
            plt.gcf().set_facecolor(bg_color)
            plt.text(0.5, 0.5, 'Sem dados de vendas', ha='center', va='center', color=text_color)
            plt.axis('off')
            
        plt.savefig(output_path, dpi=100, facecolor=bg_color)
        plt.close()
        return True
    except Exception as e:
        print(f"Erro ao gerar gráfico top produtos: {e}")
        return False
