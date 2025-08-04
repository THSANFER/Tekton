# utils.py
import os
import sys
import subprocess
import uuid
import qrcode
import tempfile
import time
from PySide6.QtGui import QPixmap
from PIL.ImageQt import ImageQt
import git

# --- CONFIGURAÇÃO CENTRAL DE CAMINHOS ---
APP_DATA_PATH = os.getenv('APPDATA')
if not APP_DATA_PATH:
    APP_DATA_PATH = os.path.expanduser('~')
SGTEK_DATA_DIR = os.path.join(APP_DATA_PATH, "SGTEK")
os.makedirs(SGTEK_DATA_DIR, exist_ok=True)
# ---------------------------------------------

# --- CONFIGURAÇÃO DO SITE DE RASTREAMENTO ---
GITHUB_USERNAME = "THSANFER"
REPO_NAME = "sgtek-rastreio"
BASE_TRACKING_URL = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/"
# ---------------------------------------------

def sanitize_filename(name):
    """Remove caracteres inválidos para nomes de pastas e arquivos."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '-')
    return name.strip()

def get_base_folder_path():
    """Retorna o caminho para a pasta 'Clientes' na Área de Trabalho."""
    client_folder_path = os.path.join(os.path.join(os.path.expanduser('~'), 'Desktop'), "Tektõn - Clientes")
    os.makedirs(client_folder_path, exist_ok=True)
    return client_folder_path

def get_tracking_pages_path():
    """Retorna o caminho para a pasta local do repositório, em AppData."""
    path = os.path.join(SGTEK_DATA_DIR, REPO_NAME)
    return path

def setup_base_folder():
    """Cria a pasta 'Tektõn - Clientes' na área de trabalho, se não existir."""
    return get_base_folder_path()

def create_client_folder(cidade, nome_cliente):
    """Cria a estrutura de pastas para um cliente e retorna o caminho."""
    base_path = get_base_folder_path()
    safe_cidade = sanitize_filename(cidade) if cidade else "Sem Cidade"
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
    if not os.path.isdir(path):
        print(f"Erro: O caminho '{path}' não é um diretório válido."); return
    if sys.platform == 'win32': os.startfile(path)
    elif sys.platform == 'darwin': subprocess.run(['open', path])
    else: subprocess.run(['xdg-open', path])

def generate_tracking_page(pedido, itens):
    if not pedido['tracking_uuid']: return None
    status_colors = {'Pendente': 'warning', 'Em Produção': 'info', 'Finalizado': 'success', 'Não Pago': 'danger', 'Pago': 'success'}
    itens_html = ""; total_itens = 0
    for item in itens:
        desc_completa = item['descricao']; desc_limpa = desc_completa.split('(+R$')[0].strip()
        if '(x' not in desc_limpa:
            try: qty_str = desc_completa.split('(x')[-1].split(')')[0]; desc_limpa += f" (x{qty_str})"
            except (ValueError, IndexError): pass
        itens_html += f"<li class='list-group-item'>{desc_limpa}</li>"
        try: qty_str = desc_completa.split('(x')[-1].split(')')[0]; total_itens += int(qty_str)
        except (ValueError, IndexError): total_itens += 1
    html_template = f"""
    <!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Acompanhe seu Pedido - Tektõn Presentes</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body{{background-color:#f8f9fa;}} .card-header{{background-color:#000080;color:white;}}</style></head><body>
    <div class="container mt-5"><div class="card shadow-sm"><div class="card-header"><h3>Acompanhe seu Pedido</h3></div>
    <div class="card-body"><p><strong>Cliente:</strong> {pedido['nome_cliente']}</p><p><strong>Descrição:</strong> {pedido['descricao']}</p>
    <p><strong>Quantidade Total de Itens:</strong> {total_itens}</p><p><strong>Valor Total:</strong> R$ {pedido['valor_total']:.2f}</p><hr>
    <h4>Status do Pedido: <span class="badge bg-{status_colors.get(pedido['status'], 'secondary')}">{pedido['status']}</span></h4>
    <h4>Status do Pagamento: <span class="badge bg-{status_colors.get(pedido['status_pagamento'], 'secondary')}">{pedido['status_pagamento']}</span></h4></div>
    <div class="card-footer text-muted">Data do Pedido: {pedido['data_pedido']}</div></div>
    <div class="card mt-3"><div class="card-header"><strong>Itens do Pedido</strong></div><ul class="list-group list-group-flush">{itens_html}</ul></div></div></body></html>
    """
    filepath = os.path.join(get_tracking_pages_path(), f"{pedido['tracking_uuid']}.html")
    with open(filepath, 'w', encoding='utf-8') as f: f.write(html_template)
    print(f"Página de rastreamento gerada/atualizada em: {filepath}")

def generate_qr_code(tracking_uuid, save_path=None):
    if not tracking_uuid: return None
    cache_buster = int(time.time())
    url = f"{BASE_TRACKING_URL}{tracking_uuid}.html?v={cache_buster}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url); qr.make(fit=True); img = qr.make_image(fill_color="black", back_color="white")
    if save_path:
        try: img.save(save_path); print(f"QR Code salvo em: {save_path}")
        except Exception as e: print(f"Erro ao salvar QR Code: {e}")
    temp_filename = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_filename = temp_file.name; img.save(temp_filename)
        pixmap = QPixmap(temp_filename)
    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)
    return pixmap

def sync_tracking_pages():
    repo_path = get_tracking_pages_path()
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        print(f"Repositório local não encontrado. Clonando de 'origin' para '{repo_path}'...")
        try:
            os.makedirs(repo_path, exist_ok=True); remote_url = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
            git.Repo.clone_from(remote_url, repo_path, branch='main'); print("Repositório clonado com sucesso.")
            repo = git.Repo(repo_path)
            with repo.config_writer() as config: config.set_value("user", "name", "SGTEK-App"); config.set_value("user", "email", "app@sgtek.com")
            print("Identidade do Git configurada para o repositório local.")
        except Exception as e: print(f"Falha ao clonar repositório: {e}"); return f"Erro de configuração inicial: {e}"
    try:
        repo = git.Repo(repo_path)
        if 'origin' not in repo.remotes: return "Erro: Repositório remoto 'origin' não configurado."
        origin = repo.remotes.origin
        origin.pull()
        if repo.is_dirty(untracked_files=True):
            print("Mudanças detectadas. Iniciando sincronização..."); repo.git.add(A=True); repo.git.commit(m="Atualizacao automatica de status do SGTEK"); origin.push(); print("Sincronização concluída com sucesso.")
            return "Sincronizado com sucesso!"
        else:
            print("Nenhuma mudança para sincronizar."); return "Nenhuma mudança nova para sincronizar."
    except git.exc.GitCommandError as e:
        print(f"Erro de comando Git: {e.stderr}"); return f"Erro de Git: {e.stderr}"
    except Exception as e:
        print(f"Erro inesperado durante a sincronização: {e}"); return f"Erro inesperado: {e}"
