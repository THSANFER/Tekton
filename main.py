# main.py
import sys
from PyQt5.QtWidgets import QApplication
import database as db
from views.main_window import MainWindow

if __name__ == '__main__':
    # 1. Inicializa o banco de dados
    db.init_db()
    
    # 2. Cria a aplicação
    app = QApplication(sys.argv)
    
    # 3. Cria e exibe a janela principal
    window = MainWindow()
    window.show()
    
    # 4. Inicia o loop de eventos da aplicação
    sys.exit(app.exec_())