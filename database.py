# database.py
import sqlite3

DATABASE_NAME = 'sgtek.db'

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados e cria todas as tabelas se não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            preco_tubo REAL DEFAULT 0,
            duracao_tubo_horas REAL DEFAULT 1,
            gasto_energia_mensal REAL DEFAULT 0,
            reserva_manutencao_mensal REAL DEFAULT 0,
            horas_trabalho_dia REAL DEFAULT 1
        );
    ''')
    cursor.execute('INSERT OR IGNORE INTO configuracoes (id) VALUES (1);')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cliente (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            telefone TEXT,
            email TEXT UNIQUE,
            cidade TEXT,
            uf TEXT,
            logradouro TEXT,
            numero TEXT
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS material (
            id_material INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL UNIQUE,
            largura_cm REAL NOT NULL,
            altura_cm REAL NOT NULL,
            preco_total REAL NOT NULL
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedido (
            id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            descricao TEXT,
            data_entrega TEXT,
            pagamento TEXT,
            valor_total REAL,
            data_pedido TEXT,
            status TEXT DEFAULT 'Pendente',
            status_pagamento TEXT DEFAULT 'Não Pago',
            FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente)
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_pedido (
            id_item INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pedido INTEGER NOT NULL,
            id_material INTEGER,
            descricao TEXT NOT NULL,
            tempo_corte_min REAL,
            valor_item REAL,
            FOREIGN KEY (id_pedido) REFERENCES pedido (id_pedido),
            FOREIGN KEY (id_material) REFERENCES material (id_material)
        );
    ''')
    
    print("Banco de dados inicializado com sucesso.")
    conn.commit()
    conn.close()

# --- Funções de Configuração ---
def save_configs(configs):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE configuracoes SET
            preco_tubo = ?, duracao_tubo_horas = ?, gasto_energia_mensal = ?,
            reserva_manutencao_mensal = ?, horas_trabalho_dia = ?
        WHERE id = 1
    ''', (configs['preco_tubo'], configs['duracao_tubo_horas'], configs['gasto_energia_mensal'],
          configs['reserva_manutencao_mensal'], configs['horas_trabalho_dia']))
    conn.commit()
    conn.close()

def load_configs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM configuracoes WHERE id = 1")
    configs = cursor.fetchone()
    conn.close()
    return configs

# --- Funções CRUD para Clientes ---
def add_cliente(nome, cpf, telefone, email, cidade, uf, logradouro, numero):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cliente (nome, cpf, telefone, email, cidade, uf, logradouro, numero) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (nome, cpf, telefone, email, cidade, uf, logradouro, numero))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_all_clientes(search_term=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_term:
        query = "SELECT * FROM cliente WHERE nome LIKE ? OR email LIKE ? OR cpf LIKE ?"
        cursor.execute(query, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
    else:
        cursor.execute("SELECT * FROM cliente ORDER BY nome")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def get_cliente_by_id(client_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cliente WHERE id_cliente = ?", (client_id,))
    cliente = cursor.fetchone()
    conn.close()
    return cliente

def update_cliente(client_id, nome, cpf, telefone, email, cidade, uf, logradouro, numero):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE cliente SET nome = ?, cpf = ?, telefone = ?, email = ?, cidade = ?, uf = ?, logradouro = ?, numero = ? WHERE id_cliente = ?', (nome, cpf, telefone, email, cidade, uf, logradouro, numero, client_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def delete_cliente(client_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cliente WHERE id_cliente = ?", (client_id,))
    conn.commit()
    conn.close()

# --- Funções CRUD para Materiais ---
def add_material(tipo, largura_cm, altura_cm, preco_total):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO material (tipo, largura_cm, altura_cm, preco_total) VALUES (?, ?, ?, ?)', (tipo, largura_cm, altura_cm, preco_total))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_all_materials(search_term=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_term:
        cursor.execute("SELECT * FROM material WHERE tipo LIKE ?", (f'%{search_term}%',))
    else:
        cursor.execute("SELECT * FROM material ORDER BY tipo")
    materials = cursor.fetchall()
    conn.close()
    return materials

def get_material_by_id(material_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM material WHERE id_material = ?", (material_id,))
    material = cursor.fetchone()
    conn.close()
    return material

def update_material(material_id, tipo, largura_cm, altura_cm, preco_total):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE material SET tipo = ?, largura_cm = ?, altura_cm = ?, preco_total = ? WHERE id_material = ?', (tipo, largura_cm, altura_cm, preco_total, material_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def delete_material(material_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM material WHERE id_material = ?", (material_id,))
    conn.commit()
    conn.close()

# --- Funções para Pedidos ---
def add_pedido_com_itens(pedido_data, itens_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO pedido (id_cliente, descricao, data_entrega, pagamento, valor_total, data_pedido) VALUES (?, ?, ?, ?, ?, date("now"))',
                       (pedido_data['id_cliente'], pedido_data['descricao'], pedido_data['data_entrega'], pedido_data['pagamento'], pedido_data['valor_total']))
        pedido_id = cursor.lastrowid
        for item in itens_data:
            cursor.execute('INSERT INTO item_pedido (id_pedido, id_material, descricao, tempo_corte_min, valor_item) VALUES (?, ?, ?, ?, ?)',
                           (pedido_id, item['id_material'], item['descricao'], item['tempo_corte'], item['custo_item']))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao salvar pedido: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_status_pedido(pedido_id, novo_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pedido SET status = ? WHERE id_pedido = ?", (novo_status, pedido_id))
    conn.commit()
    conn.close()

def update_status_pagamento(pedido_id, novo_status_pagamento):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pedido SET status_pagamento = ? WHERE id_pedido = ?", (novo_status_pagamento, pedido_id))
    conn.commit()
    conn.close()

def get_all_pedidos_com_cliente(search_term=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT p.id_pedido, p.data_pedido, p.valor_total, p.status, p.status_pagamento, COALESCE(c.nome, 'Cliente Deletado') as nome_cliente 
        FROM pedido p LEFT JOIN cliente c ON p.id_cliente = c.id_cliente
    """
    params = []
    if search_term:
        try:
            search_id = int(search_term)
            query += " WHERE c.nome LIKE ? OR p.id_pedido = ?"
            params.extend([f'%{search_term}%', search_id])
        except ValueError:
            query += " WHERE c.nome LIKE ?"
            params.append(f'%{search_term}%')

    query += " ORDER BY p.id_pedido DESC"
    cursor.execute(query, params)
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

def get_pedido_detalhes(pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ip.descricao, ip.tempo_corte_min, ip.valor_item, COALESCE(m.tipo, 'Material Avulso') as nome_material
        FROM item_pedido ip LEFT JOIN material m ON ip.id_material = m.id_material
        WHERE ip.id_pedido = ?
    """, (pedido_id,))
    itens = cursor.fetchall()
    conn.close()
    return itens

# Adicione estas funções em database.py

def get_pedidos_atuais():
    """Busca pedidos que ainda não foram finalizados (Pendente ou Em Produção)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT p.id_pedido, p.data_pedido, p.status, COALESCE(c.nome, 'Cliente Deletado') as nome_cliente
        FROM pedido p
        LEFT JOIN cliente c ON p.id_cliente = c.id_cliente
        WHERE p.status = 'Pendente' OR p.status = 'Em Produção'
        ORDER BY p.id_pedido ASC;
    """
    cursor.execute(query)
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

def get_pedidos_nao_pagos():
    """Busca todos os pedidos, de qualquer status, que ainda não foram pagos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT p.id_pedido, p.valor_total, p.status_pagamento, COALESCE(c.nome, 'Cliente Deletado') as nome_cliente
        FROM pedido p
        LEFT JOIN cliente c ON p.id_cliente = c.id_cliente
        WHERE p.status_pagamento = 'Não Pago'
        ORDER BY p.id_pedido ASC;
    """
    cursor.execute(query)
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

if __name__ == '__main__':
    init_db()