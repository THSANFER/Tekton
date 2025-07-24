# views/dialogs.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QDialogButtonBox, QMessageBox, QDoubleSpinBox,
                             QComboBox, QLabel, QTableWidget, QTableWidgetItem,
                             QPushButton, QHeaderView)
from PyQt5.QtGui import QFont
import database as db

class AddEditClientDialog(QDialog):
    def __init__(self, client_id=None, parent=None):
        super().__init__(parent); self.client_id = client_id; self.setWindowTitle("Informações do Cliente" if self.client_id else "Adicionar Cliente"); self.setMinimumWidth(400); layout, form_layout = QVBoxLayout(self), QFormLayout(); self.nome_input, self.cpf_input, self.telefone_input, self.email_input, self.logradouro_input, self.numero_input, self.cidade_input, self.uf_input = QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(); self.uf_input.setMaxLength(2); form_layout.addRow("Nome*:", self.nome_input); form_layout.addRow("CPF/CNPJ:", self.cpf_input); form_layout.addRow("Telefone:", self.telefone_input); form_layout.addRow("Email*:", self.email_input); form_layout.addRow("Endereço:", self.logradouro_input); form_layout.addRow("Número:", self.numero_input); form_layout.addRow("Cidade:", self.cidade_input); form_layout.addRow("UF:", self.uf_input); layout.addLayout(form_layout); self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); self.button_box.accepted.connect(self.accept_form); self.button_box.rejected.connect(self.reject); layout.addWidget(self.button_box);
        if self.client_id: self.load_client_data()
    def load_client_data(self):
        c = db.get_cliente_by_id(self.client_id);
        if c: self.nome_input.setText(c['nome']); self.cpf_input.setText(c['cpf']); self.telefone_input.setText(c['telefone']); self.email_input.setText(c['email']); self.logradouro_input.setText(c['logradouro']); self.numero_input.setText(c['numero']); self.cidade_input.setText(c['cidade']); self.uf_input.setText(c['uf'])
    def accept_form(self):
        nome, email = self.nome_input.text().strip(), self.email_input.text().strip()
        if not nome or not email: QMessageBox.warning(self, "Obrigatório", "Nome e Email são obrigatórios."); return
        data = {"nome": nome, "cpf": self.cpf_input.text().strip(), "telefone": self.telefone_input.text().strip(), "email": email, "cidade": self.cidade_input.text().strip(), "uf": self.uf_input.text().strip().upper(), "logradouro": self.logradouro_input.text().strip(), "numero": self.numero_input.text().strip()}
        if db.update_cliente(self.client_id, **data) if self.client_id else db.add_cliente(**data): self.accept()
        else: QMessageBox.critical(self, "Erro", "CPF ou Email já cadastrado.")

class AddEditMaterialDialog(QDialog):
    def __init__(self, material_id=None, parent=None):
        super().__init__(parent); self.material_id = material_id; self.setWindowTitle("Informações do Material" if self.material_id else "Novo Material"); self.setMinimumWidth(400); layout, form = QVBoxLayout(self), QFormLayout(); self.tipo_input = QLineEdit(); self.largura_input, self.altura_input, self.preco_input = QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1e5), QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1e5), QDoubleSpinBox(decimals=2, minimum=0.01, maximum=1e6); self.largura_input.setSuffix(" cm"); self.altura_input.setSuffix(" cm"); self.preco_input.setPrefix("R$ "); form.addRow("Tipo/Nome*:", self.tipo_input); form.addRow("Largura:", self.largura_input); form.addRow("Altura:", self.altura_input); form.addRow("Preço Chapa:", self.preco_input); layout.addLayout(form); self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); self.button_box.accepted.connect(self.accept_form); self.button_box.rejected.connect(self.reject); layout.addWidget(self.button_box);
        if self.material_id: self.load_material_data()
    def load_material_data(self):
        m = db.get_material_by_id(self.material_id);
        if m: self.tipo_input.setText(m['tipo']); self.largura_input.setValue(m['largura_cm']); self.altura_input.setValue(m['altura_cm']); self.preco_input.setValue(m['preco_total'])
    def accept_form(self):
        if not (tipo := self.tipo_input.text().strip()): QMessageBox.warning(self, "Obrigatório", "Tipo/Nome é obrigatório."); return
        data = {"tipo": tipo, "largura_cm": self.largura_input.value(), "altura_cm": self.altura_input.value(), "preco_total": self.preco_input.value()}
        if db.update_material(self.material_id, **data) if self.material_id else db.add_material(**data): self.accept()
        else: QMessageBox.critical(self, "Erro", "Já existe um material com este nome.")

class ConfigsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Configurações de Custo"); self.setMinimumWidth(450); layout, form = QVBoxLayout(self), QFormLayout(); self.preco_tubo, self.duracao_tubo, self.gasto_energia, self.reserva_manutencao, self.horas_dia = QDoubleSpinBox(decimals=2, maximum=1e5, prefix="R$ "), QDoubleSpinBox(decimals=2, maximum=1e5, suffix=" h"), QDoubleSpinBox(decimals=2, maximum=1e5, prefix="R$ "), QDoubleSpinBox(decimals=2, maximum=1e5, prefix="R$ "), QDoubleSpinBox(decimals=2, maximum=24, suffix=" h"); form.addRow("Preço Tubo:", self.preco_tubo); form.addRow("Duração Tubo:", self.duracao_tubo); form.addRow("Gasto Energia/Mês:", self.gasto_energia); form.addRow("Reserva Manutenção/Mês:", self.reserva_manutencao); form.addRow("Horas/Dia:", self.horas_dia); layout.addLayout(form); self.button_box = QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); self.button_box.accepted.connect(self.save_and_accept); self.button_box.rejected.connect(self.reject); layout.addWidget(self.button_box); self.load_data()
    def load_data(self):
        c = db.load_configs();
        if c: self.preco_tubo.setValue(c['preco_tubo']); self.duracao_tubo.setValue(c['duracao_tubo_horas']); self.gasto_energia.setValue(c['gasto_energia_mensal']); self.reserva_manutencao.setValue(c['reserva_manutencao_mensal']); self.horas_dia.setValue(c['horas_trabalho_dia'])
    def save_and_accept(self):
        db.save_configs({'preco_tubo':self.preco_tubo.value(), 'duracao_tubo_horas':self.duracao_tubo.value(), 'gasto_energia_mensal':self.gasto_energia.value(), 'reserva_manutencao_mensal':self.reserva_manutencao.value(), 'horas_trabalho_dia':self.horas_dia.value()}); self.accept()

class AddOrderItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Adicionar Item"); self.setMinimumWidth(500); self.configs, self.materials = db.load_configs(), db.get_all_materials(); self.preco_custo_laser_por_minuto = self.calculate_laser_cost_per_minute(); layout, form = QVBoxLayout(self), QFormLayout(); self.desc_input, self.material_combo, self.area_input, self.tempo_corte_input = QLineEdit(), QComboBox(), QDoubleSpinBox(decimals=2, maximum=1e5, suffix=" cm²"), QDoubleSpinBox(decimals=2, maximum=1e5, suffix=" min"); self.valor_material_label, self.valor_laser_label, self.custo_total_label = QLabel("R$ 0.00"), QLabel("R$ 0.00"), QLabel("R$ 0.00"); self.custo_total_label.setFont(QFont("Arial", 10, QFont.Bold)); form.addRow("Descrição*:", self.desc_input); form.addRow("Material:", self.material_combo); form.addRow("Área Usada:", self.area_input); form.addRow("Tempo Corte:", self.tempo_corte_input); form.addRow(QLabel("-"*30)); form.addRow("Custo Material:", self.valor_material_label); form.addRow("Custo Laser:", self.valor_laser_label); form.addRow("CUSTO TOTAL:", self.custo_total_label); layout.addLayout(form); self.button_box = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); layout.addWidget(self.button_box);
        for m in self.materials: self.material_combo.addItem(m['tipo'], userData=m['id_material'])
        self.material_combo.currentIndexChanged.connect(self.update_calculations); self.area_input.valueChanged.connect(self.update_calculations); self.tempo_corte_input.valueChanged.connect(self.update_calculations); self.button_box.accepted.connect(self.accept_form); self.button_box.rejected.connect(self.reject); self.update_calculations()
    def calculate_laser_cost_per_minute(self):
        if not self.configs or self.configs['duracao_tubo_horas'] <= 0: return 0
        min_tubo = (self.configs['preco_tubo'] / (self.configs['duracao_tubo_horas'] / 2)) / 60
        minutos_mensal = (self.configs['horas_trabalho_dia'] * 30) * 60
        if minutos_mensal <= 0: return min_tubo
        return min_tubo + (self.configs['gasto_energia_mensal']/minutos_mensal) + (self.configs['reserva_manutencao_mensal']/minutos_mensal)
    def update_calculations(self):
        s_mat = next((m for m in self.materials if m['id_material'] == self.material_combo.currentData()), None)
        area_chapa = s_mat['largura_cm'] * s_mat['altura_cm'] if s_mat else 0
        v_mat = (self.area_input.value() * (s_mat['preco_total'] / area_chapa)) if area_chapa > 0 else 0
        self.valor_material_label.setText(f"R$ {v_mat:.2f}")
        v_laser = self.preco_custo_laser_por_minuto * self.tempo_corte_input.value()
        self.valor_laser_label.setText(f"R$ {v_laser:.2f}")
        self.custo_total_label.setText(f"R$ {v_mat + v_laser:.2f}")
    def get_item_data(self):
        if not self.desc_input.text().strip(): return None
        return {"id_material":self.material_combo.currentData(), "nome_material":self.material_combo.currentText(), "descricao":self.desc_input.text().strip(), "tempo_corte":self.tempo_corte_input.value(), "custo_item":float(self.custo_total_label.text().replace("R$ ", ""))}
    def accept_form(self):
        if not self.desc_input.text().strip(): QMessageBox.warning(self, "Obrigatório", "Descrição é obrigatória."); return
        self.accept()

class PedidoDetailsDialog(QDialog):
    def __init__(self, pedido_id, parent=None):
        super().__init__(parent); self.setWindowTitle(f"Detalhes do Pedido #{pedido_id}"); self.setMinimumWidth(600); layout = QVBoxLayout(self); self.itens_table = QTableWidget(); self.itens_table.setColumnCount(4); self.itens_table.setHorizontalHeaderLabels(["Descrição", "Material", "Tempo Corte", "Custo (R$)"]); self.itens_table.setEditTriggers(QTableWidget.NoEditTriggers); self.itens_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); layout.addWidget(QLabel(f"<b>Itens do Pedido #{pedido_id}:</b>")); layout.addWidget(self.itens_table); close_button = QPushButton("Fechar"); close_button.clicked.connect(self.accept); layout.addWidget(close_button); self.load_itens_data(pedido_id)
    def load_itens_data(self, pedido_id):
        itens = db.get_pedido_detalhes(pedido_id); self.itens_table.setRowCount(len(itens))
        for r, item in enumerate(itens): self.itens_table.setItem(r,0,QTableWidgetItem(item['descricao'])); self.itens_table.setItem(r,1,QTableWidgetItem(item['nome_material'])); self.itens_table.setItem(r,2,QTableWidgetItem(f"{item['tempo_corte_min']:.2f} min")); self.itens_table.setItem(r,3,QTableWidgetItem(f"R$ {item['valor_item']:.2f}"))