# views/dialogs.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QDialogButtonBox, QMessageBox, QDoubleSpinBox,
                             QComboBox, QLabel, QTableWidget, QTableWidgetItem,
                             QPushButton, QHeaderView, QSpinBox, QHBoxLayout, QWidget)
from PyQt5.QtGui import QFont
import database as db
import utils

class AddEditClientDialog(QDialog):
    def __init__(self, client_id=None, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.setWindowTitle("Informações do Cliente" if self.client_id else "Adicionar Cliente")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        self.nome_input, self.cpf_input, self.telefone_input, self.email_input, self.logradouro_input, self.numero_input, self.cidade_input, self.uf_input = QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()
        self.uf_input.setMaxLength(2)
        form_layout.addRow("Nome*:", self.nome_input)
        form_layout.addRow("CPF/CNPJ:", self.cpf_input)
        form_layout.addRow("Telefone:", self.telefone_input)
        form_layout.addRow("Email*:", self.email_input)
        form_layout.addRow("Endereço:", self.logradouro_input)
        form_layout.addRow("Número:", self.numero_input)
        form_layout.addRow("Cidade:", self.cidade_input)
        form_layout.addRow("UF:", self.uf_input)
        layout.addLayout(form_layout)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_form)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        if self.client_id: self.load_client_data()

    def load_client_data(self):
        c = db.get_cliente_by_id(self.client_id)
        if c: self.nome_input.setText(c['nome']); self.cpf_input.setText(c['cpf']); self.telefone_input.setText(c['telefone']); self.email_input.setText(c['email']); self.logradouro_input.setText(c['logradouro']); self.numero_input.setText(c['numero']); self.cidade_input.setText(c['cidade']); self.uf_input.setText(c['uf'])

    def accept_form(self):
        nome, email, cidade = self.nome_input.text().strip(), self.email_input.text().strip(), self.cidade_input.text().strip()
        if not nome or not email: QMessageBox.warning(self, "Obrigatório", "Nome e Email são obrigatórios."); return
        data = {"nome": nome, "email": email, "cidade": cidade, "cpf": self.cpf_input.text().strip(), "telefone": self.telefone_input.text().strip(), "uf": self.uf_input.text().strip().upper(), "logradouro": self.logradouro_input.text().strip(), "numero": self.numero_input.text().strip()}
        success = db.update_cliente(self.client_id, **data) if self.client_id else db.add_cliente(**data)
        if success:
            if not self.client_id: utils.create_client_folder(cidade, nome)
            self.accept()
        else: QMessageBox.critical(self, "Erro", "CPF ou Email já cadastrado.")

class AddEditMaterialDialog(QDialog):
    def __init__(self, material_id=None, parent=None):
        super().__init__(parent)
        self.material_id = material_id
        self.setWindowTitle("Editar Material" if self.material_id else "Novo Material")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        self.categoria_combo = QComboBox(); self.categorias = ["Placa", "Caneca", "Botton", "Produto Unitário"]; self.categoria_combo.addItems(self.categorias); layout.addWidget(self.categoria_combo)
        self.form_layout = QFormLayout()
        self.tipo_input = QLineEdit()
        self.largura_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=1e5, suffix=" cm")
        self.altura_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=1e5, suffix=" cm")
        self.preco_chapa_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=1e6, prefix="R$ ")
        self.preco_unitario_input = QDoubleSpinBox(decimals=2, minimum=0.00, maximum=1e5, prefix="R$ ")
        self.form_layout.addRow("Tipo/Nome*:", self.tipo_input)
        self.form_layout.addRow("Largura:", self.largura_input)
        self.form_layout.addRow("Altura:", self.altura_input)
        self.form_layout.addRow("Preço Chapa:", self.preco_chapa_input)
        self.form_layout.addRow("Preço Unitário:", self.preco_unitario_input)
        layout.addLayout(self.form_layout)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); layout.addWidget(self.button_box)
        self.categoria_combo.currentTextChanged.connect(self.update_fields_visibility)
        self.button_box.accepted.connect(self.accept_form); self.button_box.rejected.connect(self.reject)
        if self.material_id: self.load_material_data()
        self.update_fields_visibility(self.categoria_combo.currentText())
        
    def update_fields_visibility(self, categoria):
        is_placa = (categoria == "Placa")
        for i in range(1, self.form_layout.rowCount()):
            widget = self.form_layout.itemAt(i, QFormLayout.FieldRole).widget()
            label = self.form_layout.labelForField(widget)
            if widget in [self.largura_input, self.altura_input, self.preco_chapa_input]:
                label.setVisible(is_placa); widget.setVisible(is_placa)
            elif widget == self.preco_unitario_input:
                label.setVisible(not is_placa); widget.setVisible(not is_placa)

    def load_material_data(self):
        m = db.get_material_by_id(self.material_id)
        if m:
            self.categoria_combo.setCurrentText(m['categoria']); self.tipo_input.setText(m['tipo'])
            if m['categoria'] == 'Placa': self.largura_input.setValue(m['largura_cm'] or 0); self.altura_input.setValue(m['altura_cm'] or 0); self.preco_chapa_input.setValue(m['preco_chapa'] or 0)
            else: self.preco_unitario_input.setValue(m['preco_unitario'] or 0)

    def accept_form(self):
        if not (tipo := self.tipo_input.text().strip()): QMessageBox.warning(self, "Obrigatório", "Tipo/Nome é obrigatório."); return
        data = {'categoria': self.categoria_combo.currentText(), 'tipo': tipo}
        if data['categoria'] == 'Placa': data.update({'largura_cm': self.largura_input.value(), 'altura_cm': self.altura_input.value(), 'preco_chapa': self.preco_chapa_input.value()})
        else: data['preco_unitario'] = self.preco_unitario_input.value()
        if db.update_material(self.material_id, data) if self.material_id else db.add_material(data): self.accept()
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
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Item" if initial_data else "Adicionar Item")
        self.setMinimumWidth(500)
        self.initial_data = initial_data
        self.configs = db.load_configs()
        self.materials = db.get_all_materials()
        self.preco_custo_laser_por_minuto = self.calculate_laser_cost_per_minute()
        layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.desc_input = QLineEdit()
        self.material_combo = QComboBox()
        self.largura_material_input = QDoubleSpinBox(decimals=2, maximum=99999.99, suffix=" cm")
        self.altura_material_input = QDoubleSpinBox(decimals=2, maximum=99999.99, suffix=" cm")
        self.area_layout_widget = QWidget()
        area_layout = QHBoxLayout(self.area_layout_widget); area_layout.setContentsMargins(0,0,0,0)
        area_layout.addWidget(self.largura_material_input); area_layout.addWidget(QLabel("x")); area_layout.addWidget(self.altura_material_input)
        self.tempo_corte_input = QDoubleSpinBox(decimals=2, maximum=99999.99, suffix=" min")
        self.custo_adicional_input = QDoubleSpinBox(decimals=2, maximum=10000.00, prefix="R$ ")
        self.quantidade_input = QSpinBox(minimum=1, maximum=1000)
        self.valor_material_label = QLabel("R$ 0.00"); self.valor_laser_label = QLabel("R$ 0.00"); self.custo_unitario_label = QLabel("R$ 0.00"); self.custo_total_label = QLabel("R$ 0.00"); self.custo_total_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.form_layout.addRow("Descrição*:", self.desc_input)
        self.form_layout.addRow("Material:", self.material_combo)
        self.label_dimensoes = QLabel("Dimensões (Larg x Alt):"); self.form_layout.addRow(self.label_dimensoes, self.area_layout_widget)
        self.label_tempo_corte = QLabel("Tempo de Corte (unitário):"); self.form_layout.addRow(self.label_tempo_corte, self.tempo_corte_input)
        self.form_layout.addRow("Custo Adicional (unitário):", self.custo_adicional_input); self.form_layout.addRow("Quantidade:", self.quantidade_input); self.form_layout.addRow(QLabel("-" * 40))
        self.label_custo_material = QLabel("Custo Material (unitário):"); self.form_layout.addRow(self.label_custo_material, self.valor_material_label)
        self.label_custo_laser = QLabel("Custo Laser (unitário):"); self.form_layout.addRow(self.label_custo_laser, self.valor_laser_label)
        self.form_layout.addRow("CUSTO UNITÁRIO:", self.custo_unitario_label); self.form_layout.addRow("CUSTO TOTAL (x Qtde):", self.custo_total_label)
        layout.addLayout(self.form_layout)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); layout.addWidget(self.button_box)
        for m in self.materials: self.material_combo.addItem(m['tipo'], userData=m['id_material'])
        self.material_combo.currentIndexChanged.connect(self.on_material_changed); self.largura_material_input.valueChanged.connect(self.update_calculations); self.altura_material_input.valueChanged.connect(self.update_calculations); self.tempo_corte_input.valueChanged.connect(self.update_calculations); self.custo_adicional_input.valueChanged.connect(self.update_calculations); self.quantidade_input.valueChanged.connect(self.update_calculations); self.button_box.accepted.connect(self.accept_form); self.button_box.rejected.connect(self.reject)
        if self.initial_data: self.populate_fields()
        else: self.on_material_changed()
        self.update_calculations()

    def on_material_changed(self, index=0):
        if self.material_combo.currentIndex() < 0: return
        mat = db.get_material_by_id(self.material_combo.currentData())
        is_placa = (mat and mat['categoria'] == 'Placa')
        self.label_dimensoes.setVisible(is_placa); self.area_layout_widget.setVisible(is_placa)
        self.label_tempo_corte.setVisible(is_placa); self.tempo_corte_input.setVisible(is_placa)
        self.label_custo_material.setVisible(is_placa); self.valor_material_label.setVisible(is_placa)
        self.label_custo_laser.setVisible(is_placa); self.valor_laser_label.setVisible(is_placa)

    def populate_fields(self):
        self.desc_input.setText(self.initial_data['descricao_base']); material_index = self.material_combo.findData(self.initial_data['id_material']); self.material_combo.setCurrentIndex(material_index if material_index!=-1 else 0); self.largura_material_input.setValue(self.initial_data['largura_cm']); self.altura_material_input.setValue(self.initial_data['altura_cm']); self.tempo_corte_input.setValue(self.initial_data['tempo_corte_unitario']); self.custo_adicional_input.setValue(self.initial_data['custo_adicional_unitario']); self.quantidade_input.setValue(self.initial_data['quantidade'])

    def calculate_laser_cost_per_minute(self):
        if not self.configs or self.configs['duracao_tubo_horas'] <= 0: return 0
        min_tubo = (self.configs['preco_tubo'] / (self.configs['duracao_tubo_horas'] / 2)) / 60
        minutos_mensal = (self.configs['horas_trabalho_dia'] * 30) * 60
        if minutos_mensal <= 0: return min_tubo
        return min_tubo + (self.configs['gasto_energia_mensal']/minutos_mensal) + (self.configs['reserva_manutencao_mensal']/minutos_mensal)

    def update_calculations(self):
        if self.material_combo.currentIndex() < 0: return
        mat = db.get_material_by_id(self.material_combo.currentData()); custo_unitario = 0.0; v_mat = 0.0; v_laser = 0.0
        if mat and mat['categoria'] == 'Placa':
            area_chapa = (mat['largura_cm'] or 0) * (mat['altura_cm'] or 0); area_usada = self.largura_material_input.value() * self.altura_material_input.value()
            v_mat = (area_usada * (mat['preco_chapa'] / area_chapa)) if area_chapa > 0 else 0
            v_laser = self.preco_custo_laser_por_minuto * self.tempo_corte_input.value()
            custo_unitario = v_mat + v_laser
        elif mat:
            custo_unitario = mat['preco_unitario'] or 0
        self.valor_material_label.setText(f"R$ {v_mat:.2f}"); self.valor_laser_label.setText(f"R$ {v_laser:.2f}")
        custo_unitario_final = custo_unitario + self.custo_adicional_input.value()
        self.custo_unitario_label.setText(f"R$ {custo_unitario_final:.2f}")
        self.custo_total_label.setText(f"R$ {custo_unitario_final * self.quantidade_input.value():.2f}")

    def get_item_data(self):
        if not self.desc_input.text().strip(): return None
        quantidade = self.quantidade_input.value(); descricao_base = self.desc_input.text().strip(); custo_adicional = self.custo_adicional_input.value(); descricao_final = f"{descricao_base}"
        if custo_adicional > 0: descricao_final += f" (+R${custo_adicional:.2f} extra)"
        descricao_final += f" (x{quantidade})"
        return {"descricao_base": descricao_base, "id_material": self.material_combo.currentData(), "largura_cm": self.largura_material_input.value(), "altura_cm": self.altura_material_input.value(), "tempo_corte_unitario": self.tempo_corte_input.value(), "custo_adicional_unitario": custo_adicional, "quantidade": quantidade, "nome_material": self.material_combo.currentText(), "descricao_final": descricao_final, "tempo_corte_total": self.tempo_corte_input.value() * quantidade, "custo_item_total": float(self.custo_total_label.text().replace("R$ ", "")),}
        
    def accept_form(self):
        if not self.desc_input.text().strip(): QMessageBox.warning(self, "Obrigatório", "A descrição do item é obrigatória."); return
        self.accept()

class PedidoDetailsDialog(QDialog):
    def __init__(self, pedido_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detalhes do Pedido #{pedido_id}")
        self.setMinimumWidth(600)
        layout = QVBoxLayout(self)
        self.itens_table = QTableWidget()
        self.itens_table.setColumnCount(4)
        self.itens_table.setHorizontalHeaderLabels(["Descrição", "Material", "Tempo Corte Total", "Custo (R$)"])
        self.itens_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.itens_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel(f"<b>Itens do Pedido #{pedido_id}:</b>"))
        layout.addWidget(self.itens_table)
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        self.load_itens_data(pedido_id)

    def load_itens_data(self, pedido_id):
        itens = db.get_pedido_detalhes(pedido_id)
        self.itens_table.setRowCount(len(itens))
        for r, item in enumerate(itens):
            self.itens_table.setItem(r, 0, QTableWidgetItem(item['descricao']))
            self.itens_table.setItem(r, 1, QTableWidgetItem(item['nome_material']))
            self.itens_table.setItem(r, 2, QTableWidgetItem(f"{item['tempo_corte_min']:.2f} min"))
            self.itens_table.setItem(r, 3, QTableWidgetItem(f"R$ {item['valor_item']:.2f}"))
