# views/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QStackedWidget, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, 
                             QDateEdit, QHeaderView, QComboBox, QMessageBox, 
                             QFormLayout, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import database as db
import utils
from .dialogs import (AddEditClientDialog, AddEditMaterialDialog, ConfigsDialog, 
                      AddOrderItemDialog, PedidoDetailsDialog)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SGTEK - Sistema de Gerenciamento")
        self.setGeometry(100, 100, 1200, 700)
        self.current_order_items = []
        main_widget = QWidget(); self.setCentralWidget(main_widget); main_layout = QHBoxLayout(main_widget); main_layout.setContentsMargins(0,0,0,0); main_layout.setSpacing(0)
        nav_panel = QWidget(); nav_panel.setStyleSheet("background-color:#000080; color:white;"); nav_panel.setFixedWidth(200); nav_layout = QVBoxLayout(nav_panel)
        title_label = QLabel("SGTEK"); title_label.setFont(QFont("Arial", 20, QFont.Bold)); title_label.setAlignment(Qt.AlignCenter); nav_layout.addWidget(title_label)
        self.nav_list = QListWidget(); self.nav_list.setFont(QFont("Arial", 12)); self.nav_list.addItems(["Início", "Vendas", "Pedidos", "Clientes", "Histórico", "Material"]); self.nav_list.setStyleSheet("QListWidget{border:none;outline:none} QListWidget::item{padding:15px} QListWidget::item:selected,QListWidget::item:hover{background-color:#4169E1}"); nav_layout.addWidget(self.nav_list); nav_layout.addStretch()
        config_button = QPushButton("Configurações"); config_button.setStyleSheet("color:white; background-color:#4CAF50; padding:5px;"); config_button.clicked.connect(self.open_configs_dialog); nav_layout.addWidget(config_button, alignment=Qt.AlignBottom)
        self.stacked_widget = QStackedWidget(); main_layout.addWidget(nav_panel); main_layout.addWidget(self.stacked_widget)
        self.create_pages()
        self.nav_list.currentRowChanged.connect(self.on_nav_changed)
        self.nav_list.setCurrentRow(0)

    def on_nav_changed(self, index):
        if index == 0: self.load_dashboard_data()
        elif index == 1: self.load_vendas_data()
        elif index == 2: self.prepare_pedidos_page()
        elif index == 4: self.load_historico_data()
        self.stacked_widget.setCurrentIndex(index)
        
    def create_pages(self):
        self.create_inicio_page()
        self.create_vendas_page()
        self.create_pedidos_page()
        self.create_clientes_page()
        self.create_historico_page()
        self.create_material_page()
        self.load_clients_data(); self.load_materials_data(); self.load_dashboard_data()

    def create_inicio_page(self):
        page = QWidget(); layout = QVBoxLayout(page); title_label = QLabel("Dashboard - Resumo Atual"); title_label.setFont(QFont("Arial", 16, QFont.Bold)); layout.addWidget(title_label, alignment=Qt.AlignCenter); main_h_layout = QHBoxLayout(); left_panel = QWidget(); left_layout = QVBoxLayout(left_panel); left_layout.addWidget(QLabel("<b>Pedidos Atuais</b>"), alignment=Qt.AlignCenter); self.dashboard_atuais_table = QTableWidget(); self.dashboard_atuais_table.setColumnCount(4); self.dashboard_atuais_table.setHorizontalHeaderLabels(["Cliente", "Data", "Status", "Detalhes"]); self.dashboard_atuais_table.setEditTriggers(QTableWidget.NoEditTriggers); self.dashboard_atuais_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); left_layout.addWidget(self.dashboard_atuais_table); right_panel = QWidget(); right_layout = QVBoxLayout(right_panel); right_layout.addWidget(QLabel("<b>Pagamentos Pendentes</b>"), alignment=Qt.AlignCenter); self.dashboard_pagamentos_table = QTableWidget(); self.dashboard_pagamentos_table.setColumnCount(3); self.dashboard_pagamentos_table.setHorizontalHeaderLabels(["Cliente", "Valor a Pagar", "Detalhes"]); self.dashboard_pagamentos_table.setEditTriggers(QTableWidget.NoEditTriggers); self.dashboard_pagamentos_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); right_layout.addWidget(self.dashboard_pagamentos_table); main_h_layout.addWidget(left_panel); main_h_layout.addWidget(right_panel); layout.addLayout(main_h_layout); self.stacked_widget.addWidget(page)
    
    def create_vendas_page(self):
        page=QWidget();layout=QVBoxLayout(page);self.search_input_vendas=QLineEdit(placeholderText="Pesquisar por cliente ou ID...");self.search_input_vendas.textChanged.connect(self.load_vendas_data);layout.addWidget(self.search_input_vendas);self.vendas_table=QTableWidget();self.vendas_table.setColumnCount(7);self.vendas_table.setHorizontalHeaderLabels(["ID","Cliente","Data","Valor","Status Pedido","Status Pagamento","Detalhes"]);self.vendas_table.setEditTriggers(QTableWidget.NoEditTriggers);self.vendas_table.setSelectionBehavior(QTableWidget.SelectRows);self.vendas_table.verticalHeader().setVisible(False);self.vendas_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);layout.addWidget(self.vendas_table);self.stacked_widget.addWidget(page)

    def create_historico_page(self):
        page = QWidget(); layout = QVBoxLayout(page); self.search_input_historico = QLineEdit(placeholderText="Pesquisar por cliente, cidade ou descrição..."); self.search_input_historico.textChanged.connect(self.load_historico_data); layout.addWidget(self.search_input_historico); self.historico_table = QTableWidget(); self.historico_table.setColumnCount(5); self.historico_table.setHorizontalHeaderLabels(["Cliente", "Cidade", "Descrição", "Valor Final", "Arquivo"]); self.historico_table.setEditTriggers(QTableWidget.NoEditTriggers); self.historico_table.setSelectionBehavior(QTableWidget.SelectRows); self.historico_table.verticalHeader().setVisible(False); self.historico_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); layout.addWidget(self.historico_table); self.stacked_widget.addWidget(page)
    
    def create_clientes_page(self):
        page=QWidget();layout=QVBoxLayout(page);action_layout=QHBoxLayout();self.search_input_c=QLineEdit(placeholderText="Pesquisar clientes...");self.search_input_c.textChanged.connect(self.load_clients_data);add_btn=QPushButton("Adicionar Cliente");add_btn.clicked.connect(self.open_add_client_dialog);action_layout.addWidget(self.search_input_c);action_layout.addWidget(add_btn);layout.addLayout(action_layout);self.client_table=QTableWidget();self.client_table.setColumnCount(6);self.client_table.setHorizontalHeaderLabels(["ID","Nome","Email","Telefone","Editar","Excluir"]);self.client_table.setEditTriggers(QTableWidget.NoEditTriggers);self.client_table.setSelectionBehavior(QTableWidget.SelectRows);self.client_table.verticalHeader().setVisible(False);self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);self.client_table.setColumnHidden(0,True);layout.addWidget(self.client_table);self.stacked_widget.addWidget(page)
    
    def create_material_page(self):
        page=QWidget();layout=QVBoxLayout(page);action_layout=QHBoxLayout();self.search_input_m=QLineEdit(placeholderText="Pesquisar materiais...");self.search_input_m.textChanged.connect(self.load_materials_data);add_btn=QPushButton("Adicionar Material");add_btn.clicked.connect(self.open_add_material_dialog);action_layout.addWidget(self.search_input_m);action_layout.addWidget(add_btn);layout.addLayout(action_layout);self.material_table=QTableWidget();self.material_table.setColumnCount(8);self.material_table.setHorizontalHeaderLabels(["ID","Tipo","Largura","Altura","Área(cm²)","Preço/cm²","Editar","Excluir"]);self.material_table.setEditTriggers(QTableWidget.NoEditTriggers);self.material_table.setSelectionBehavior(QTableWidget.SelectRows);self.material_table.verticalHeader().setVisible(False);self.material_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);self.material_table.setColumnHidden(0,True);layout.addWidget(self.material_table);self.stacked_widget.addWidget(page)

    def create_pedidos_page(self):
        page = QWidget(); layout = QVBoxLayout(page); form = QFormLayout()
        self.pedido_cliente_combo = QComboBox(); self.pedido_desc_input = QTextEdit(); self.pedido_entrega_date = QDateEdit(calendarPopup=True); self.pedido_pagamento_combo = QComboBox(); self.pedido_pagamento_combo.addItems(["PIX", "Dinheiro", "Débito", "Crédito"]); self.pedido_lucro_spinbox = QDoubleSpinBox(suffix=" %", decimals=2, maximum=1000)
        form.addRow("Cliente*:", self.pedido_cliente_combo); form.addRow("Descrição:", self.pedido_desc_input); form.addRow("Entrega:", self.pedido_entrega_date); form.addRow("Pagamento:", self.pedido_pagamento_combo); form.addRow("Margem de Lucro:", self.pedido_lucro_spinbox)
        layout.addLayout(form); layout.addWidget(QLabel("Itens do Pedido:"))
        self.itens_pedido_table = QTableWidget(); self.itens_pedido_table.setColumnCount(6); self.itens_pedido_table.setHorizontalHeaderLabels(["ID Material", "Descrição", "Tempo Total", "Custo Total", "Editar", "Excluir"]); self.itens_pedido_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.itens_pedido_table.setColumnHidden(0, True); self.itens_pedido_table.setEditTriggers(QTableWidget.NoEditTriggers); self.itens_pedido_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.itens_pedido_table)
        add_item_btn = QPushButton("Adicionar Item"); add_item_btn.clicked.connect(self.open_add_order_item_dialog); layout.addWidget(add_item_btn)
        total_layout = QFormLayout(); self.custo_total_pedido_label = QLabel("R$ 0.00"); self.valor_lucro_label = QLabel("R$ 0.00"); self.preco_final_venda_label = QLabel("R$ 0.00"); self.preco_final_venda_label.setFont(QFont("Arial", 14, QFont.Bold)); total_layout.addRow("Custo Total (Itens):", self.custo_total_pedido_label); total_layout.addRow("Valor Lucro:", self.valor_lucro_label); total_layout.addRow("PREÇO FINAL DE VENDA:", self.preco_final_venda_label); layout.addLayout(total_layout)
        self.confirmar_pedido_btn = QPushButton("SALVAR PEDIDO"); self.confirmar_pedido_btn.setStyleSheet("padding:10px;font-weight:bold;background-color:green;color:white"); self.confirmar_pedido_btn.clicked.connect(self.save_order); layout.addWidget(self.confirmar_pedido_btn)
        self.stacked_widget.addWidget(page)
        self.pedido_lucro_spinbox.valueChanged.connect(self.update_order_totals)
        self.itens_pedido_table.itemDoubleClicked.connect(lambda item: self.edit_order_item(item.row()))
    
    def load_dashboard_data(self):
        self.dashboard_atuais_table.setRowCount(0);pedidos_atuais=db.get_pedidos_atuais();[self.dashboard_atuais_table.insertRow(r)or self.dashboard_atuais_table.setItem(r,0,QTableWidgetItem(p['nome_cliente']))or self.dashboard_atuais_table.setItem(r,1,QTableWidgetItem(p['data_pedido']))or self.dashboard_atuais_table.setItem(r,2,QTableWidgetItem(p['status']))or(btn:=QPushButton("Ver Detalhes"),btn.clicked.connect(lambda _,pid=p['id_pedido']:self.show_pedido_details_by_id(pid)),self.dashboard_atuais_table.setCellWidget(r,3,btn))for r,p in enumerate(pedidos_atuais)]
        self.dashboard_pagamentos_table.setRowCount(0);pedidos_nao_pagos=db.get_pedidos_nao_pagos();total=sum(p['valor_total']for p in pedidos_nao_pagos);[self.dashboard_pagamentos_table.insertRow(r)or self.dashboard_pagamentos_table.setItem(r,0,QTableWidgetItem(p['nome_cliente']))or self.dashboard_pagamentos_table.setItem(r,1,QTableWidgetItem(f"R$ {p['valor_total']:.2f}"))or(btn:=QPushButton("Ver Detalhes"),btn.clicked.connect(lambda _,pid=p['id_pedido']:self.show_pedido_details_by_id(pid)),self.dashboard_pagamentos_table.setCellWidget(r,2,btn))for r,p in enumerate(pedidos_nao_pagos)]
        if total>0:r=self.dashboard_pagamentos_table.rowCount();self.dashboard_pagamentos_table.insertRow(r);t=QTableWidgetItem("TOTAL A RECEBER");t.setFont(QFont("Arial",10,QFont.Bold));self.dashboard_pagamentos_table.setItem(r,0,t);v=QTableWidgetItem(f"R$ {total:.2f}");v.setFont(QFont("Arial",10,QFont.Bold));self.dashboard_pagamentos_table.setItem(r,1,v)

    def load_vendas_data(self):
        self.vendas_table.blockSignals(True);self.vendas_table.setRowCount(0);pedidos=db.get_all_pedidos_com_cliente(self.search_input_vendas.text());
        for r,p in enumerate(pedidos):self.vendas_table.insertRow(r);p_id=p['id_pedido'];self.vendas_table.setItem(r,0,QTableWidgetItem(str(p_id)));self.vendas_table.setItem(r,1,QTableWidgetItem(p['nome_cliente']));self.vendas_table.setItem(r,2,QTableWidgetItem(p['data_pedido']));self.vendas_table.setItem(r,3,QTableWidgetItem(f"R$ {p['valor_total']:.2f}"));combo_s=QComboBox();combo_s.addItems(["Pendente","Em Produção","Finalizado"]);combo_s.setCurrentText(p['status']);combo_s.currentTextChanged.connect(lambda txt,pid=p_id:db.update_status_pedido(pid,txt));self.vendas_table.setCellWidget(r,4,combo_s);combo_p=QComboBox();combo_p.addItems(["Não Pago","Pago"]);combo_p.setCurrentText(p['status_pagamento']);combo_p.currentTextChanged.connect(lambda txt,pid=p_id:db.update_status_pagamento(pid,txt));self.vendas_table.setCellWidget(r,5,combo_p);d_btn=QPushButton("Ver Detalhes");d_btn.clicked.connect(lambda _,pid=p_id:self.show_pedido_details_by_id(pid));self.vendas_table.setCellWidget(r,6,d_btn)
        self.vendas_table.blockSignals(False)

    def load_historico_data(self):
        """Carrega e exibe os dados na tabela de Histórico."""
        # Limpa a tabela antes de preencher
        self.historico_table.setRowCount(0)
        
        # Busca os dados no banco de dados
        pedidos = db.get_historico_pedidos(self.search_input_historico.text())
        
        # Itera sobre cada pedido e preenche a tabela linha por linha
        for row, pedido in enumerate(pedidos):
            self.historico_table.insertRow(row)
            
            # Preenche as colunas de texto
            self.historico_table.setItem(row, 0, QTableWidgetItem(pedido['nome_cliente']))
            self.historico_table.setItem(row, 1, QTableWidgetItem(pedido['cidade']))
            self.historico_table.setItem(row, 2, QTableWidgetItem(pedido['desc_pedido']))
            self.historico_table.setItem(row, 3, QTableWidgetItem(f"R$ {pedido['valor_total']:.2f}"))
            
            # Adiciona o botão "Abrir Pasta" se o caminho existir
            if (path := pedido['caminho_arquivo']):
                button = QPushButton("Abrir Pasta")
                # Usa uma função lambda para capturar o caminho correto para o clique
                button.clicked.connect(lambda _, p=path: utils.open_folder(p))
                self.historico_table.setCellWidget(row, 4, button)
    
    def show_pedido_details_by_id(self, pedido_id): PedidoDetailsDialog(pedido_id, self).exec_()
    
    def load_clients_data(self):
        self.client_table.setRowCount(0);clientes=db.get_all_clientes(self.search_input_c.text());
        for r,c in enumerate(clientes):self.client_table.insertRow(r);self.client_table.setItem(r,0,QTableWidgetItem(str(c['id_cliente'])));self.client_table.setItem(r,1,QTableWidgetItem(c['nome']));self.client_table.setItem(r,2,QTableWidgetItem(c['email']));self.client_table.setItem(r,3,QTableWidgetItem(c['telefone']));edit_btn=QPushButton("Editar");edit_btn.clicked.connect(lambda _,row=r:self.open_edit_client_dialog(row));self.client_table.setCellWidget(r,4,edit_btn);del_btn=QPushButton("Excluir");del_btn.clicked.connect(lambda _,row=r:self.delete_client(row));self.client_table.setCellWidget(r,5,del_btn)

    def load_materials_data(self):
        self.material_table.setRowCount(0);materials=db.get_all_materials(self.search_input_m.text());
        for r,m in enumerate(materials):area=m['largura_cm']*m['altura_cm'] if m['largura_cm'] and m['altura_cm'] else 0; p_cm2=m['preco_chapa']/area if area>0 else 0;self.material_table.insertRow(r);self.material_table.setItem(r,0,QTableWidgetItem(str(m['id_material'])));self.material_table.setItem(r,1,QTableWidgetItem(m['tipo']));self.material_table.setItem(r,2,QTableWidgetItem(f"{m['largura_cm']:.2f}" if m['largura_cm'] else 'N/A'));self.material_table.setItem(r,3,QTableWidgetItem(f"{m['altura_cm']:.2f}" if m['altura_cm'] else 'N/A'));self.material_table.setItem(r,4,QTableWidgetItem(f"{area:.2f}" if area>0 else 'N/A'));self.material_table.setItem(r,5,QTableWidgetItem(f"{p_cm2:.6f}" if p_cm2>0 else 'N/A'));edit_btn=QPushButton("Editar");edit_btn.clicked.connect(lambda _,row=r:self.open_edit_material_dialog(row));self.material_table.setCellWidget(r,6,edit_btn);del_btn=QPushButton("Excluir");del_btn.clicked.connect(lambda _,row=r:self.delete_material(row));self.material_table.setCellWidget(r,7,del_btn)
    
    def prepare_pedidos_page(self):
        self.current_order_items.clear(); self.refresh_order_table(); self.pedido_cliente_combo.clear();
        for c in db.get_all_clientes(): self.pedido_cliente_combo.addItem(c['nome'],userData=c['id_cliente'])
        self.pedido_entrega_date.setDate(QDate.currentDate().addDays(7))
    
    def open_add_client_dialog(self):
        if AddEditClientDialog(parent=self).exec_(): self.load_clients_data()
    
    def open_edit_client_dialog(self, row):
        if AddEditClientDialog(int(self.client_table.item(row,0).text()), self).exec_(): self.load_clients_data()
    
    def delete_client(self, row):
        if QMessageBox.question(self,"Confirmar","Excluir cliente?",QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes: db.delete_cliente(int(self.client_table.item(row,0).text())); self.load_clients_data()
    
    def open_add_material_dialog(self):
        if AddEditMaterialDialog(parent=self).exec_(): self.load_materials_data()
    
    def open_edit_material_dialog(self, row):
        if AddEditMaterialDialog(int(self.material_table.item(row,0).text()),self).exec_(): self.load_materials_data()
    
    def delete_material(self, row):
        if QMessageBox.question(self,"Confirmar","Excluir material?",QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes: db.delete_material(int(self.material_table.item(row,0).text())); self.load_materials_data()
    
    def open_configs_dialog(self): ConfigsDialog(self).exec_()
    
    def open_add_order_item_dialog(self):
        dialog = AddOrderItemDialog(self)
        if dialog.exec_():
            if item_data := dialog.get_item_data(): self.current_order_items.append(item_data); self.refresh_order_table()
    
    def edit_order_item(self, row):
        if not (0 <= row < len(self.current_order_items)): return
        dialog = AddOrderItemDialog(self, initial_data=self.current_order_items[row])
        if dialog.exec_():
            if updated_data := dialog.get_item_data(): self.current_order_items[row] = updated_data; self.refresh_order_table()

    def delete_order_item(self, row):
        if 0 <= row < len(self.current_order_items): del self.current_order_items[row]; self.refresh_order_table()

    def refresh_order_table(self):
        self.itens_pedido_table.setRowCount(0)
        for row, item in enumerate(self.current_order_items):
            self.itens_pedido_table.insertRow(row)
            self.itens_pedido_table.setItem(row, 0, QTableWidgetItem(str(item['id_material'])))
            self.itens_pedido_table.setItem(row, 1, QTableWidgetItem(item['descricao_final']))
            self.itens_pedido_table.setItem(row, 2, QTableWidgetItem(f"{item['tempo_corte_total']:.2f} min"))
            self.itens_pedido_table.setItem(row, 3, QTableWidgetItem(f"{item['custo_item_total']:.2f}"))
            edit_btn = QPushButton("Editar"); edit_btn.clicked.connect(lambda _, r=row: self.edit_order_item(r)); self.itens_pedido_table.setCellWidget(row, 4, edit_btn)
            del_btn = QPushButton("X"); del_btn.clicked.connect(lambda _, r=row: self.delete_order_item(r)); self.itens_pedido_table.setCellWidget(row, 5, del_btn)
        self.update_order_totals()
    
    def update_order_totals(self):
        custo_itens = sum(item['custo_item_total'] for item in self.current_order_items)
        custo_total = custo_itens
        self.custo_total_pedido_label.setText(f"R$ {custo_total:.2f}")
        lucro = custo_total * (self.pedido_lucro_spinbox.value() / 100)
        self.valor_lucro_label.setText(f"R$ {lucro:.2f}")
        self.preco_final_venda_label.setText(f"R$ {custo_total + lucro:.2f}")
    
    def save_order(self):
        if not (c_id:=self.pedido_cliente_combo.currentData()) or not self.current_order_items:
            QMessageBox.warning(self,"Erro","Selecione um cliente e adicione pelo menos um item."); return
        self.confirmar_pedido_btn.setEnabled(False)
        try:
            cliente_info = db.get_cliente_by_id(c_id)
            cidade, nome_cliente = cliente_info['cidade'], cliente_info['nome']
            desc_pedido = self.pedido_desc_input.toPlainText().strip() or self.current_order_items[0]['descricao_base']
            caminho = utils.create_pedido_folder_and_get_path(cidade, nome_cliente, desc_pedido)
            p_data={'id_cliente':c_id,'descricao':desc_pedido,'data_entrega':self.pedido_entrega_date.date().toString(Qt.ISODate),'pagamento':self.pedido_pagamento_combo.currentText(),'valor_total':float(self.preco_final_venda_label.text().replace("R$ ","")), 'custo_adicional':0, 'caminho_arquivo':caminho}
            i_data=[{'id_material':item['id_material'],'descricao':item['descricao_final'],'tempo_corte':item['tempo_corte_total'],'custo_item':item['custo_item_total']} for item in self.current_order_items]
            if db.add_pedido_com_itens(p_data, i_data):
                QMessageBox.information(self,"Sucesso","Pedido salvo!"); self.current_order_items.clear(); self.refresh_order_table(); self.pedido_desc_input.clear()
            else: QMessageBox.critical(self,"Erro","Não foi possível salvar o pedido.")
        finally:
            self.confirmar_pedido_btn.setEnabled(True)
