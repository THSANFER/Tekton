# utils.py
import os
import sys
import subprocess

def sanitize_filename(name):
    """Remove caracteres inválidos para nomes de pastas."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '-')
    return name.strip()

def get_desktop_path():
    """Retorna o caminho para a área de trabalho do usuário."""
    return os.path.join(os.path.expanduser('~'), 'Desktop')

def get_base_folder_path():
    """Retorna o caminho para a pasta principal 'Tektõn - Clientes'."""
    return os.path.join(get_desktop_path(), "Tektõn - Clientes")

def setup_base_folder():
    """Cria a pasta 'Tektõn - Clientes' na área de trabalho se não existir."""
    base_path = get_base_folder_path()
    os.makedirs(base_path, exist_ok=True)
    return base_path

def create_client_folder(cidade, nome_cliente):
    """Cria a estrutura de pastas para um cliente e retorna o caminho."""
    base_path = get_base_folder_path()
    safe_cidade = sanitize_filename(cidade)
    safe_cliente = sanitize_filename(nome_cliente)
    
    client_path = os.path.join(base_path, safe_cidade, safe_cliente)
    os.makedirs(client_path, exist_ok=True)
    return client_path

def create_pedido_folder_and_get_path(cidade, nome_cliente, desc_pedido):
    """Cria a pasta final do pedido e retorna o caminho completo."""
    client_path = create_client_folder(cidade, nome_cliente)
    safe_desc = sanitize_filename(desc_pedido)
    
    pedido_path = os.path.join(client_path, safe_desc)
    os.makedirs(pedido_path, exist_ok=True)
    return pedido_path

def open_folder(path):
    """Abre uma pasta no explorador de arquivos padrão do sistema operacional."""
    if not os.path.isdir(path):
        print(f"Erro: O caminho '{path}' não é um diretório válido.")
        return
        
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'darwin': # macOS
        subprocess.run(['open', path])
    else: # linux
        subprocess.run(['xdg-open', path])