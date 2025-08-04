# run.py
import sys
from PySide6.QtWidgets import QApplication
import database as db
from views.main_window import MainWindow

def main():
    """Função principal que inicia a aplicação."""
    # Inicializa o banco de dados (cria se não existir)
    db.init_db()
    
    # Cria a aplicação
    app = QApplication(sys.argv)
    
    # Cria e exibe a janela principal
    window = MainWindow()
    window.show()
    
    # Inicia o loop de eventos da aplicação
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
