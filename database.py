
import sqlite3
import os
from datetime import datetime

import sys

# Definir caminho do Banco de Dados
try:
    if getattr(sys, 'frozen', False):
        APP_DIR = os.path.dirname(sys.executable)
    else:
        # Script rodando na raiz
        APP_DIR = os.path.dirname(os.path.abspath(__file__))
        
    DB_NAME = os.path.join(APP_DIR, "db", "gestor_facil.db")
except Exception:
    # Fallback seguro para mobile
    APP_DIR = os.path.expanduser("~")
    DB_NAME = os.path.join(APP_DIR, "gestor_facil.db")

def conectar():
    """Conecta ao banco de dados SQLite."""
    # Garantir que a pasta db existe
    if not os.path.exists(os.path.dirname(DB_NAME)):
        os.makedirs(os.path.dirname(DB_NAME))
    # Timeout aumentado para 20s para evitar lock
    conn = sqlite3.connect(DB_NAME, timeout=20)
    conn.row_factory = sqlite3.Row  # Permite aceder às colunas pelo nome
    return conn

def inicializar_banco():
    """Cria as tabelas necessárias se não existirem."""
    import time
    max_retries = 3
    
    for attempt in range(max_retries):
        conn = None
        try:
            conn = conectar()
            # Ativar WAL mode para melhor concorrencia
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()

            # Tabela de Produtos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    preco_custo REAL NOT NULL,
                    preco_venda REAL NOT NULL,
                    quantidade INTEGER NOT NULL DEFAULT 0,
                    minimo_alerta INTEGER NOT NULL DEFAULT 5,
                    detalhes TEXT,
                    categoria TEXT
                )
            ''')

            # Tabela de Vendas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_hora TEXT NOT NULL,
                    total_venda REAL NOT NULL,
                    lucro_total REAL NOT NULL,
                    cliente TEXT,
                    sync_status INTEGER DEFAULT 0
                )
            ''')
            
            # Migrações (simples try/except para cada coluna)
            try: cursor.execute("ALTER TABLE vendas ADD COLUMN cliente TEXT")
            except sqlite3.OperationalError: pass 
            try: cursor.execute("ALTER TABLE produtos ADD COLUMN detalhes TEXT")
            except sqlite3.OperationalError: pass
            try: cursor.execute("ALTER TABLE produtos ADD COLUMN categoria TEXT DEFAULT 'Geral'")
            except sqlite3.OperationalError: pass

            # V45: Attribuicao de Vendas (Quem vendeu?)
            try: cursor.execute("ALTER TABLE vendas ADD COLUMN vendedor_id INTEGER")
            except sqlite3.OperationalError: pass
            try: cursor.execute("ALTER TABLE vendas ADD COLUMN vendedor_nome TEXT")
            except sqlite3.OperationalError: pass

            # Tabela de Despesas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS despesas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_hora TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    valor REAL NOT NULL
                )
            ''')
            
            # Tabela de Usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE NOT NULL,
                    nome_completo TEXT,
                    senha TEXT NOT NULL,
                    cargo TEXT NOT NULL,
                    email TEXT,
                    whatsapp TEXT,
                    status TEXT DEFAULT 'ativo',
                    last_login TEXT,
                    last_password_update TEXT
                )
            ''')
            
            # --- Migrações (Para bancos existentes) ---
            # V19/V20: Status e Last Login
            try: cursor.execute("ALTER TABLE usuarios ADD COLUMN status TEXT DEFAULT 'ativo'")
            except sqlite3.OperationalError: pass
            try: cursor.execute("ALTER TABLE usuarios ADD COLUMN last_login TEXT")
            except sqlite3.OperationalError: pass
            
            # V21: Last Password Update
            try: cursor.execute("ALTER TABLE usuarios ADD COLUMN last_password_update TEXT")
            except sqlite3.OperationalError: pass
            
            # Garantir colunas antigas (vias das duvidas)
            try: cursor.execute("ALTER TABLE usuarios ADD COLUMN email TEXT")
            except sqlite3.OperationalError: pass 
            try: cursor.execute("ALTER TABLE usuarios ADD COLUMN whatsapp TEXT")
            except sqlite3.OperationalError: pass
            try: cursor.execute("ALTER TABLE usuarios ADD COLUMN nome_completo TEXT")
            except sqlite3.OperationalError: pass
            
            # V44: Created By (Rastreio de quem criou o usuario)
            try: cursor.execute("ALTER TABLE usuarios ADD COLUMN created_by TEXT")
            except sqlite3.OperationalError: pass
            
            # Definir data de update de senha para hoje se estiver vazio (para usuários antigos)
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try: cursor.execute("UPDATE usuarios SET last_password_update = ? WHERE last_password_update IS NULL", (agora,))
            except sqlite3.OperationalError: pass

            # Criar usuários padrões
            try:
                # Admin padrão
                cursor.execute("INSERT INTO usuarios (usuario, nome_completo, senha, cargo, whatsapp, status, last_password_update) VALUES (?, ?, ?, ?, ?, 'ativo', ?)", 
                               ('admin', 'Soares Inocencia Massaete', 'admin', 'super_admin', '258849343350', agora))
            except sqlite3.IntegrityError:
                pass
            
            try:
                # Super Admin solicitado (smassaete)
                # Tenta inserir
                cursor.execute("INSERT INTO usuarios (usuario, nome_completo, senha, cargo, whatsapp, status, last_password_update) VALUES (?, ?, ?, ?, ?, 'ativo', ?)", 
                               ('smassaete', 'Soares Inocencia Massaete', '23568932', 'super_admin', '258849343350', None)) 
                               # last_password_update=None forca troca? O usuario pediu senha fixa, entao vou por data atual para NAO expirar agora, ou None?
                               # O usuario pediu senha especifica, melhor nao expirar ja no primeiro login.
                               # Vou por 'agora' em last_password_update para dar 30 dias.
            except sqlite3.IntegrityError:
                # Se ja existe, ATUALIZA a senha e cargo para garantir acesso
                cursor.execute("UPDATE usuarios SET senha='23568932', cargo='super_admin', status='ativo' WHERE usuario='smassaete'")
                
            conn.commit()
            return # Sucesso, sai da funcao

        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                print(f"Banco de dados bloqueado, tentando novamente... ({attempt+1}/{max_retries})")
                time.sleep(1.0) # Espera 1s
            else:
                raise e # Outro erro, levanta
        finally:
            if conn: conn.close()
    
    # Se falhou apos retries
    raise sqlite3.OperationalError("Não foi possível acessar o banco de dados após várias tentativas. Verifique se o programa já está aberto.")


def verificar_login(usuario, senha):
    """Verifica credenciais, status e atualiza login."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
        user = cursor.fetchone()
        
        if user:
            user_dict = dict(user)
            
            # Check Status
            if user_dict.get('status') == 'bloqueado':
                conn.close()
                return "BLOCKED"
            
            # Check Password Expiry (30 dias) OR First Login (None)
            last_update = user_dict.get('last_password_update')
            
            if last_update is None:
                 conn.close()
                 return "EXPIRED" # Forcar troca no primeiro acesso
                 
            if last_update:
                try:
                    last_date = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
                    dias = (datetime.now() - last_date).days
                    if dias >= 45:
                        conn.close()
                        return "EXPIRED" # Senha expirada
                except ValueError:
                    pass # Se data invalida, ignora
                
            # Update Last Login
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("UPDATE usuarios SET last_login = ? WHERE id = ?", (agora, user_dict['id']))
            conn.commit()
            
        conn.close()
        return user
    except Exception as e:
        print(f"Erro login DB: {e}")
        return None

def atualizar_senha(user_id, nova_senha):
    """Atualiza senha e timestamp."""
    conn = conectar()
    cursor = conn.cursor()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE usuarios SET senha = ?, last_password_update = ? WHERE id = ?", (nova_senha, agora, user_id))
    conn.commit()
    conn.close()

def criar_usuario(user, senha, cargo, email, wpp, nome, created_by=None):
    """Cria um novo usuário no banco de dados."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        # last_password_update = NULL forca a troca no primeiro login
        cursor.execute('''
            INSERT INTO usuarios (usuario, senha, cargo, email, whatsapp, nome_completo, status, last_password_update, created_by)
            VALUES (?, ?, ?, ?, ?, ?, 'ativo', NULL, ?)
        ''', (user, senha, cargo, email, wpp, nome, created_by))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False
    except Exception as e:
        print(f"Erro ao criar usuario: {e}")
        conn.close()
        return False

def editar_usuario(id_user, nome, usuario, email, whatsapp):
    """Atualiza dados do usuário (menos senha/cargo)."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios SET nome_completo = ?, usuario = ?, email = ?, whatsapp = ?
            WHERE id = ?
        """, (nome, usuario, email, whatsapp, id_user))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False 

def remover_usuario(user_id):
    """Remove um usuário pelo ID."""
    conn = conectar()
    conn.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# Funções duplicadas removidas. Ver definição consolidada abaixo.

def get_usuario_por_id(user_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
    u = cursor.fetchone()
    conn.close()
    return u


# --- Gestão de Usuários (Novo) ---
        
# --- Funções de Gestão de Usuários (Consolidadas) ---
def listar_todos_usuarios():
    """Retorna lista de todos os usuários."""
    conn = conectar()
    cursor = conn.cursor()
    # Ordenar por nome facilita a busca, mas por last_login ajuda a ver atividade. 
    # Vou manter last_login pois era o comportamento mais recente definido.
    cursor.execute("SELECT id, usuario, nome_completo, cargo, status, last_login, email, whatsapp, senha, created_by FROM usuarios ORDER BY last_login DESC")
    users = cursor.fetchall()
    conn.close()
    return users

def alterar_status_usuario(user_id, novo_status):
    """Bloqueia ou desbloqueia usuário."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET status = ? WHERE id = ?", (novo_status, user_id))
    conn.commit()
    conn.close()

def get_metricas_super_admin():
    """Calcula estatisticas para o dashboard do Super Admin."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Total de Clientes (Admins)
    cursor.execute("SELECT count(*) FROM usuarios WHERE cargo = 'admin'")
    total_clientes = cursor.fetchone()[0]
    
    # Clientes Ativos
    cursor.execute("SELECT count(*) FROM usuarios WHERE cargo = 'admin' AND status = 'ativo'")
    clientes_ativos = cursor.fetchone()[0]
    
    # Clientes Bloqueados
    cursor.execute("SELECT count(*) FROM usuarios WHERE cargo = 'admin' AND status = 'bloqueado'")
    clientes_bloqueados = cursor.fetchone()[0]
    
    # Total Vendedores (Global)
    cursor.execute("SELECT count(*) FROM usuarios WHERE cargo = 'vendedor'")
    total_vendedores = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_clientes': total_clientes,
        'clientes_ativos': clientes_ativos,
        'clientes_bloqueados': clientes_bloqueados,
        'total_vendedores': total_vendedores
    }

def get_clientes_para_dashboard():
    """Retorna lista de clientes (admins) para o dashboard do Super Admin."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome_completo, usuario, status, whatsapp, email 
        FROM usuarios 
        WHERE cargo = 'admin' 
        ORDER BY status DESC, nome_completo ASC
    """)
    dados = cursor.fetchall()
    conn.close()
    return dados


# --- CRUD Despesas ---
def adicionar_despesa(descricao, categoria, valor):
    conn = conectar()
    cursor = conn.cursor()
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO despesas (data_hora, descricao, categoria, valor)
        VALUES (?, ?, ?, ?)
    ''', (data_hora, descricao, categoria, valor))
    conn.commit()
    conn.close()

def listar_despesas(limit=50):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM despesas ORDER BY data_hora DESC LIMIT ?', (limit,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def remover_despesa(despesa_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM despesas WHERE id = ?', (despesa_id,))
    conn.commit()
    conn.close()

def get_despesas_mes(ano, mes):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM despesas 
        WHERE strftime('%Y', data_hora) = ? AND strftime('%m', data_hora) = ?
    ''', (str(ano), str(mes).zfill(2)))
    dados = cursor.fetchall()
    conn.close()
    return dados

# Funções CRUD básicas

def adicionar_produto(nome, preco_custo, preco_venda, quantidade, minimo_alerta, detalhes="", categoria="Geral"):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO produtos (nome, preco_custo, preco_venda, quantidade, minimo_alerta, detalhes, categoria)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nome, preco_custo, preco_venda, quantidade, minimo_alerta, detalhes, categoria))
    conn.commit()
    conn.close()

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def atualizar_produto(produto_id, nome, preco_custo, preco_venda, quantidade, minimo_alerta, detalhes="", categoria="Geral"):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE produtos 
        SET nome=?, preco_custo=?, preco_venda=?, quantidade=?, minimo_alerta=?, detalhes=?, categoria=?
        WHERE id=?
    ''', (nome, preco_custo, preco_venda, quantidade, minimo_alerta, detalhes, categoria, produto_id))
    conn.commit()
    conn.close()

def remover_produto(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
    conn.commit()
    conn.close()

def atualizar_stock(produto_id, quantidade_vendida):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?
    ''', (quantidade_vendida, produto_id))
    conn.commit()
    conn.close()

# Funções de gestão de usuários movidas/baleadas para baixo para evitar duplicatas

def registar_venda(itens, total, lucro, cliente=None, vendedor_id=None, vendedor_nome=None):
    """
    Regista uma venda e seus itens.
    itens: lista de tuplas (produto_id, quantidade, preco_unitario)
    cliente: Nome do cliente (opcional)
    vendedor_id/nome: Identificacao de quem fez a venda
    """
    conn = conectar()
    cursor = conn.cursor()
    
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Inserir venda
    cursor.execute('''
        INSERT INTO vendas (data_hora, total_venda, lucro_total, cliente, sync_status, vendedor_id, vendedor_nome)
        VALUES (?, ?, ?, ?, 0, ?, ?)
    ''', (data_hora, total, lucro, cliente, vendedor_id, vendedor_nome))
    
    venda_id = cursor.lastrowid
    
    # Inserir itens
    for item in itens:
        prod_id, qtd, preco = item
        cursor.execute('''
            INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario)
            VALUES (?, ?, ?, ?)
        ''', (venda_id, prod_id, qtd, preco))
        
        # Baixar stock
        cursor.execute('''
            UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?
        ''', (qtd, prod_id))
        
    conn.commit()
    conn.close()
    return venda_id

def get_resumo_hoje():
    """Retorna (faturamento, lucro, num_vendas) de hoje."""
    conn = conectar()
    cursor = conn.cursor()
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    # SQLite string comparison for date prefix
    cursor.execute('''
        SELECT sum(total_venda), sum(lucro_total), count(*)
        FROM vendas 
        WHERE data_hora LIKE ?
    ''', (f'{hoje}%',))
    
    resultado = cursor.fetchone()
    conn.close()
    
    faturamento = resultado[0] if resultado[0] else 0.0
    lucro = resultado[1] if resultado[1] else 0.0
    num = resultado[2] if resultado[2] else 0
    
    return faturamento, lucro, num

def get_vendas_mes(ano, mes):
    """Retorna dados de vendas do mês especificado."""
    conn = conectar()
    # Usar pandas se possível seria melhor, mas aqui retornamos raw data para processar no reports.py
    # Ou melhor, retornar lista de tuplas
    cursor = conn.cursor()
    cursor.execute('''
        SELECT data_hora, total_venda, lucro_total, vendedor_nome
        FROM vendas 
        WHERE strftime('%Y', data_hora) = ? AND strftime('%m', data_hora) = ?
    ''', (str(ano), str(mes).zfill(2)))
    dados = cursor.fetchall()
    conn.close()
    return dados

def get_vendas_ultimos_7_dias():
    """Retorna totais diários dos últimos 7 dias."""
    conn = conectar()
    cursor = conn.cursor()
    # Query compatível com SQLite para pegar últimos 7 dias
    cursor.execute('''
        SELECT date(data_hora) as data, SUM(total_venda) as total
        FROM vendas
        WHERE date(data_hora) >= date('now', '-6 days')
        GROUP BY date(data_hora)
        ORDER BY date(data_hora) ASC
    ''')
    dados = cursor.fetchall()
    conn.close()
    return dados

def get_top_produtos(limit=5):
    """Retorna lista dos top produtos mais vendidos (nome, qtd_total)."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT p.nome, SUM(iv.quantidade) as total_qtd
        FROM itens_venda iv
        JOIN produtos p ON iv.produto_id = p.id
        GROUP BY iv.produto_id
        ORDER BY total_qtd DESC
        LIMIT {limit}
    ''')
    dados = cursor.fetchall()
    conn.close()
    return dados

def get_produtos_baixo_stock():
    """Retorna produtos onde quantidade <= minimo_alerta."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT nome, quantidade, minimo_alerta
        FROM produtos
        WHERE quantidade <= minimo_alerta
        ORDER BY quantidade ASC
    ''')
    dados = cursor.fetchall()
    conn.close()
    return dados

def get_produto_por_nome(nome):
    """Busca produto exato pelo nome (case insensitive)."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos WHERE lower(nome) = ?', (nome.lower(),))
    res = cursor.fetchone()
    conn.close()
    return res

def get_produto_unico(nome, detalhes):
    """Busca produto por nome E detalhes para diferenciar variações."""
    conn = conectar()
    cursor = conn.cursor()
    if detalhes:
        cursor.execute('SELECT * FROM produtos WHERE lower(nome) = ? AND lower(detalhes) = ?', (nome.lower(), detalhes.lower()))
    else:
        # Se detalhes é vazio, busca onde detalhes é vazio ou null
        cursor.execute("SELECT * FROM produtos WHERE lower(nome) = ? AND (detalhes IS NULL OR details = '')", (nome.lower(),))
        
    res = cursor.fetchone()
    # Fallback: se não achar exato, tenta só pelo nome se detalhes for muito especifico? 
    # Não, o usuario quer diferenciar. Se não achou combinacao, retorna None (novo produto)
    conn.close()
    return res

def listar_nomes_produtos():
    """Retorna lista de nomes de produtos para autocomplete."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT nome FROM produtos ORDER BY nome')
    nomes = [row['nome'] for row in cursor.fetchall()]
    conn.close()
    return nomes

# --- Funções de Sincronização ---

def get_vendas_nao_sincronizadas():
    """Retorna todas as vendas com sync_status = 0 (pendentes)."""
    conn = conectar()
    # Retornamos dicts para facilitar JSON
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Pegar vendas
    cursor.execute("SELECT * FROM vendas WHERE sync_status = 0")
    vendas = [dict(row) for row in cursor.fetchall()]
    
    # Para cada venda, pegar itens
    for v in vendas:
        cursor.execute("SELECT * FROM itens_venda WHERE venda_id = ?", (v['id'],))
        v['itens'] = [dict(row) for row in cursor.fetchall()]
        
    conn.close()
    return vendas

def marcar_venda_como_sincronizada(venda_id):
    """Atualiza sync_status para 1."""
    conn = conectar()
    conn.execute("UPDATE vendas SET sync_status = 1 WHERE id = ?", (venda_id,))
    conn.commit()
    conn.close()

def upsert_produto_from_cloud(produto_data):
    """
    Atualiza ou cria produto vindo da nuvem.
    Usa o NOME como chave única por enquanto (simplificação).
    """
    conn = conectar()
    cursor = conn.cursor()
    
    try:
        # Tenta achar pelo nome
        cursor.execute("SELECT id FROM produtos WHERE nome = ?", (produto_data['nome'],))
        exists = cursor.fetchone()
        
        if exists:
            # Atualiza (Preços, Detalhes). NÃO atualiza estoque local para não quebrar contagem em andamento?
            # Estratégia: Nuvem manda no preço, mas somamos estoque? 
            # Por simplicidade V1: Nuvem sobreescreve tudo (Master-Slave logic)
            cursor.execute("""
                UPDATE produtos 
                SET preco_custo=?, preco_venda=?, quantidade=?, minimo_alerta=?, detalhes=?, categoria=?
                WHERE id=?
            """, (
                produto_data['preco_custo'], 
                produto_data['preco_venda'], 
                produto_data['quantidade'], # Cuidado aqui com race condition de estoque
                produto_data['minimo_alerta'],
                produto_data.get('detalhes', ''),
                produto_data.get('categoria', 'Geral'),
                exists['id']
            ))
        else:
            # Cria novo
            cursor.execute("""
                INSERT INTO produtos (nome, preco_custo, preco_venda, quantidade, minimo_alerta, detalhes, categoria)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                produto_data['nome'],
                produto_data['preco_custo'],
                produto_data['preco_venda'],
                produto_data['quantidade'],
                produto_data['minimo_alerta'],
                produto_data.get('detalhes', ''),
                produto_data.get('categoria', 'Geral')
            ))
            
        conn.commit()
    except Exception as e:
        print(f"Erro ao sincronizar produto {produto_data.get('nome')}: {e}")
    finally:
        conn.close()

def verificar_se_venda_existe(data_hora, total, vendedor):
    """Verifica duplicidade de venda vinda da nuvem."""
    conn = conectar()
    cursor = conn.cursor()
    # Margem de erro de 1 segundo na data? ou string exata? 
    # Supabase retorna ISO com T e Z. SQLite local tem espaco. Precisamos normalizar.
    # Hack V1: Ignorar segundos finais ou usar LIKE.
    
    # Vamos converter o total para float para garantir
    total = float(total)
    
    cursor.execute("""
        SELECT id FROM vendas 
        WHERE total_venda = ? AND vendedor_nome = ? AND substr(data_hora, 1, 13) = substr(?, 1, 13)
    """, (total, vendedor, data_hora))
    # substr(..., 1, 13) pega YYYY-MM-DD HH (a hora bate).
    
    data = cursor.fetchone()
    conn.close()
    return data is not None

def registar_venda_importada(venda_data):
    """Registra uma venda vinda da nuvem no banco local."""
    conn = conectar()
    cursor = conn.cursor()
    
    # O JSON do itens vem no campo 'itens'
    itens = venda_data.get('itens', [])
    if isinstance(itens, str):
        import json
        itens = json.loads(itens)
        
    # Inserir Venda (Marcamos como synced=1 pois veio da nuvem)
    cursor.execute('''
        INSERT INTO vendas (data_hora, total_venda, lucro_total, cliente, sync_status, vendedor_id, vendedor_nome)
        VALUES (?, ?, ?, ?, 1, NULL, ?)
    ''', (
        venda_data['data_hora'], 
        venda_data['total_venda'], 
        venda_data['lucro_total'], 
        venda_data['cliente'], 
        venda_data.get('vendedor_nome')
    ))
    venda_id = cursor.lastrowid
    
    # Inserir Itens
    # Nota: Não baixamos stock aqui novamente pois 'sync_produtos' já atualiza o saldo final.
    # Mas para histórico fica registrado.
    for item in itens:
        # produto_id local pode ser diferente do remoto. Precisamos buscar pelo nome.
        # sync_produtos ja rodou antes, entao produto deve existir.
        cursor.execute("SELECT id FROM produtos WHERE nome = ?", (item.get('nome'),))
        prod_local = cursor.fetchone()
        prod_id = prod_local['id'] if prod_local else None
        
        if prod_id:
            cursor.execute('''
                INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
            ''', (venda_id, prod_id, item.get('qtd', 0), item.get('preco', 0)))
            
    conn.commit()
    conn.close()
