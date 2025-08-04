# views/dialogs.py
import time
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QDialogButtonBox, QMessageBox, QDoubleSpinBox,
                             QComboBox, QLabel, QTableWidget, QTableWidgetItem,
                             QPushButton, QHeaderView, QSpinBox, QHBoxLayout, QWidget,
                             QApplication, QFileDialog, QTextEdit, QDateEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QPixmap
import database as db
import utils

# (As classes AddEditClientDialog, AddEditMaterialDialog, ConfigsDialog, AddOrderItemDialog e PedidoDetailsDialog vêm aqui, como nas respostas anteriores)

class ShowQRCodeDialog(QDialog):
    def __init__(self, pixmap, url, parent=None):
        super().__init__(parent); self.setWindowTitle("QR Code de Rastreamento"); layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Mostre este QR Code para o cliente escanear:")); qr_label = QLabel(); qr_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio)); qr_label.setAlignment(Qt.AlignCenter); layout.addWidget(qr_label)
        layout.addWidget(QLabel("Ou compartilhe este link:")); link_input = QLineEdit(url); link_input.setReadOnly(True); layout.addWidget(link_input)
        close_button = QDialogButtonBox(QDialogButtonBox.Ok); close_button.accepted.connect(self.accept); layout.addWidget(close_button)

class EditPedidoDialog(QDialog):
    def __init__(self, pedido_id, parent=None):
        super().__init__(parent); self.setWindowTitle(f"Editando Pedido #{pedido_id}"); self.setMinimumSize(800, 600); self.pedido_id = pedido_id; self.current_order_items = []
        self.pedido_data = db.get_pedido_completo_by_id(self.pedido_id); itens_db = db.get_pedido_detalhes(self.pedido_id)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.cliente_combo = QComboBox(); self.desc_input = QTextEdit(); self.entrega_date = QDateEdit(calendarPopup=True); self.pagamento_combo = QComboBox(); self.pagamento_combo.addItems(["PIX", "Dinheiro", "Débito", "Crédito"]); self.lucro_spinbox = QDoubleSpinBox(suffix=" %", decimals=2, maximum=1000)
        for c in db.get_all_clientes(): self.cliente_combo.addItem(c['nome'], userData=c['id_cliente'])
        if self.pedido_data:
            cliente_idx = self.cliente_combo.findData(self.pedido_data['id_cliente']); self.cliente_combo.setCurrentIndex(cliente_idx if cliente_idx != -1 else 0)
            self.desc_input.setText(self.pedido_data['descricao']); self.entrega_date.setDate(QDate.fromString(self.pedido_data['data_entrega'], Qt.ISODate)); self.pagamento_combo.setCurrentText(self.pedido_data['pagamento'])
            custo_total_itens = sum(item['valor_item'] for item in itens_db)
            if self.pedido_data['valor_total'] > 0 and custo_total_itens > 0: lucro = ((self.pedido_data['valor_total'] / custo_total_itens) - 1) * 100; self.lucro_spinbox.setValue(lucro)
        form.addRow("Cliente*:", self.cliente_combo); form.addRow("Descrição:", self.desc_input); form.addRow("Entrega:", self.entrega_date); form.addRow("Pagamento:", self.pagamento_combo); form.addRow("Margem de Lucro:", self.lucro_spinbox)
        layout.addLayout(form); layout.addWidget(QLabel("Itens do Pedido:"))
        self.itens_table = QTableWidget(); self.itens_table.setColumnCount(6); self.itens_table.setHorizontalHeaderLabels(["ID Material", "Descrição", "Tempo", "Custo", "Editar", "Excluir"]); self.itens_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.itens_table.setColumnHidden(0, True); self.itens_table.setEditTriggers(QTableWidget.NoEditTriggers); self.itens_table.setSelectionBehavior(QTableWidget.SelectRows); layout.addWidget(self.itens_table)
        add_item_btn = QPushButton("Adicionar Novo Item"); add_item_btn.clicked.connect(self.open_add_order_item_dialog); layout.addWidget(add_item_btn)
        total_layout = QFormLayout(); self.custo_label = QLabel("R$ 0.00"); self.lucro_label = QLabel("R$ 0.00"); self.final_label = QLabel("R$ 0.00"); self.final_label.setFont(QFont("Arial", 14, QFont.Bold)); total_layout.addRow("Custo Total:", self.custo_label); total_layout.addRow("Valor Lucro:", self.lucro_label); total_layout.addRow("PREÇO FINAL:", self.final_label); layout.addLayout(total_layout)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); layout.addWidget(self.button_box)
        self.lucro_spinbox.valueChanged.connect(self.update_order_totals); self.button_box.accepted.connect(self.accept_form); self.button_box.rejected.connect(self.reject)
        for item in itens_db:
            desc_completa = item['descricao']; desc_base = desc_completa.split(' (x')[0].split(' (+R$')[0].strip()
            try: quantidade = int(desc_completa.split('(x')[-1].split(')')[0])
            except: quantidade = 1
            custo_adicional = 0
            if '(+R$' in desc_completa:
                try: custo_adicional = float(desc_completa.split('(+R$')[-1].split(' extra)')[0])
                except: custo_adicional = 0
            self.current_order_items.append({"descricao_base": desc_base, "id_material": item['id_material'], "largura_cm": 0, "altura_cm": 0, "tempo_corte_unitario": (item['tempo_corte_min']/quantidade) if quantidade > 0 else 0, "custo_adicional_unitario": custo_adicional, "quantidade": quantidade, "nome_material": item['nome_material'], "descricao_final": desc_completa, "tempo_corte_total": item['tempo_corte_min'], "custo_item_total": item['valor_item']})
        self.refresh_order_table()
    def open_add_order_item_dialog(self):
        dialog = AddOrderItemDialog(self);
        if dialog.exec():
            if item_data := dialog.get_item_data(): self.current_order_items.append(item_data); self.refresh_order_table()
    def edit_order_item(self, row):
        if not (0 <= row < len(self.current_order_items)): return
        dialog = AddOrderItemDialog(self, initial_data=self.current_order_items[row])
        if dialog.exec():
            if updated_data := dialog.get_item_data(): self.current_order_items[row] = updated_data; self.refresh_order_table()
    def delete_order_item(self, row):
        if 0 <= row < len(self.current_order_items): del self.current_order_items[row]; self.refresh_order_table()
    def refresh_order_table(self):
        self.itens_table.setRowCount(0)
        for row, item in enumerate(self.current_order_items):
            self.itens_table.insertRow(row); self.itens_table.setItem(row, 0, QTableWidgetItem(str(item['id_material']))); self.itens_table.setItem(row, 1, QTableWidgetItem(item['descricao_final'])); self.itens_table.setItem(row, 2, QTableWidgetItem(f"{item['tempo_corte_total']:.2f} min")); self.itens_table.setItem(row, 3, QTableWidgetItem(f"{item['custo_item_total']:.2f}")); 
            edit_btn = QPushButton("Editar"); edit_btn.clicked.connect(lambda _, r=row: self.edit_order_item(r)); self.itens_table.setCellWidget(row, 4, edit_btn)
            del_btn = QPushButton("X"); del_btn.clicked.connect(lambda _, r=row: self.delete_order_item(r)); self.itens_table.setCellWidget(row, 5, del_btn)
        self.update_order_totals()
    def update_order_totals(self):
        custo_itens = sum(item['custo_item_total'] for item in self.current_order_items)
        self.custo_label.setText(f"R$ {custo_itens:.2f}"); lucro = custo_itens * (self.lucro_spinbox.value() / 100); self.lucro_label.setText(f"R$ {lucro:.2f}"); self.final_label.setText(f"R$ {custo_itens + lucro:.2f}")
    def accept_form(self):
        p_data = {'id_cliente': self.cliente_combo.currentData(),'descricao': self.desc_input.toPlainText(),'data_entrega': self.entrega_date.date().toString(Qt.ISODate),'pagamento': self.pagamento_combo.currentText(),'valor_total': float(self.final_label.text().replace("R$ ", "")),'custo_adicional': self.pedido_data['custo_adicional'],'caminho_arquivo': self.pedido_data['caminho_arquivo'],'tracking_uuid': self.pedido_data['tracking_uuid']}
        i_data = [{'id_material':item['id_material'],'descricao':item['descricao_final'],'tempo_corte':item['tempo_corte_total'],'custo_item':item['custo_item_total']} for item in self.current_order_items]
        if db.update_pedido_completo(self.pedido_id, p_data, i_data):
            pedido_atualizado = db.get_pedido_by_id(self.pedido_id); itens_atualizados = db.get_pedido_detalhes(self.pedido_id)
            if pedido_atualizado and itens_atualizados: utils.generate_tracking_page(pedido_atualizado, itens_atualizados)
            QMessageBox.information(self, "Sucesso", "Pedido atualizado com sucesso!"); self.accept()
        else: QMessageBox.critical(self, "Erro", "Não foi possível atualizar o pedido.")
