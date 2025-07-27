# main.py
import sys
from PyQt5.QtWidgets import QApplication
import database as db
import utils # Adicione esta importação
from views.main_window import MainWindow

if __name__ == '__main__':
    # 1. Garante que a pasta base 'Tektõn - Clientes' exista
    utils.setup_base_folder()
    
    # 2. Inicializa o banco de dados
    db.init_db()
    
    # 3. Cria a aplicação
    app = QApplication(sys.argv)
    
    # 4. Cria e exibe a janela principal
    window = MainWindow()
    window.show()
    
    # 5. Inicia o loop de eventos da aplicação
    sys.exit(app.exec_())
