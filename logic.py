from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from gui import Ui_MainWindow
from model import FilamentModel
from datetime import date


class Logic(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.model = FilamentModel()

        # 1. Setup Dropdown
        brands = [
            "None Selected", "Atomic Filament", "Bambu Lab", "Cookiecad", "Creality",
            "Elegoo", "eSUN", "Fiberlogy", "Fillamentum", "FormFutura",
            "Gembird", "Hatchbox", "Inland", "MatterHackers", "NinjaTek",
            "Overture", "Polymaker", "Proto-Pasta", "Prusament",
            "Sunlu", "3DJAKE", "Other"
        ]
        self.comboBox.addItems(brands)
        self.comboBox.setCurrentIndex(0)

        # 2. Connect Buttons
        self.addButton.clicked.connect(self.add_spool)
        self.weightButton.clicked.connect(self.update_weight)
        self.markButton.clicked.connect(self.mark_dried)
        self.deleteButton.clicked.connect(self.delete_spool)

        # 3. Connect CheckBoxes
        self.brandCheckBox.toggled.connect(lambda ch: self.brandCheckBox.setText("Locked" if ch else "Unlocked"))
        self.materialCheckBox.toggled.connect(lambda ch: self.materialCheckBox.setText("Locked" if ch else "Unlocked"))
        self.colorCheckBox.toggled.connect(lambda ch: self.colorCheckBox.setText("Locked" if ch else "Unlocked"))
        self.weightCheckBox.toggled.connect(lambda ch: self.weightCheckBox.setText("Locked" if ch else "Unlocked"))

        # 4. Status Bar Style
        self.statusBar.setFixedHeight(30)
        self.refresh_table()

    def update_status(self, message, is_error=False):
        color = "#e74c3c" if is_error else "#2ecc71"
        self.statusBar.setStyleSheet(
            f"QStatusBar {{ background-color: #2c3e50; color: {color}; font-weight: bold; font-size: 14px; }}")
        self.statusBar.showMessage(message)

    def refresh_table(self):
        data = self.model.get_data()
        self.filamentTable.setRowCount(len(data))
        self.filamentTable.setColumnCount(8)
        self.filamentTable.setHorizontalHeaderLabels(
            ['Select', 'Brand', 'Material', 'Color', 'ID', 'InitialWeight(g)', 'CurrentWeight(g)', 'LastDried'])

        # Sizing Logic
        header = self.filamentTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.filamentTable.setColumnWidth(0, 50)
        for i in range(1, 8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        for i, row in enumerate(data):
            # Centered Checkbox
            chk = QCheckBox()
            chk_widget = QWidget()
            layout = QHBoxLayout(chk_widget)
            layout.addWidget(chk)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.filamentTable.setCellWidget(i, 0, chk_widget)

            self.filamentTable.setItem(i, 1, QTableWidgetItem(str(row.get('Brand', ''))))
            self.filamentTable.setItem(i, 2, QTableWidgetItem(str(row.get('Material', ''))))
            self.filamentTable.setItem(i, 3, QTableWidgetItem(str(row.get('Color', ''))))
            self.filamentTable.setItem(i, 4, QTableWidgetItem(str(row.get('ID', ''))))
            self.filamentTable.setItem(i, 5, QTableWidgetItem(str(row.get('InitialWeight', ''))))
            self.filamentTable.setItem(i, 6, QTableWidgetItem(str(row.get('CurrentWeight', ''))))
            self.filamentTable.setItem(i, 7, QTableWidgetItem(str(row.get('LastDried', ''))))

    def get_selected_rows(self):
        selected = []
        for i in range(self.filamentTable.rowCount()):
            container = self.filamentTable.cellWidget(i, 0)
            if container:
                chk = container.findChild(QCheckBox)
                if chk and chk.isChecked():
                    selected.append(i)
        return selected

    def add_spool(self):
        if self.comboBox.currentText() == "None Selected":
            self.update_status("Error: Please select a brand!", is_error=True)
            return
        if not self.inputMaterial.text().strip():
            self.update_status("Error: Enter Valid Material Type", is_error=True)
            return
        if not self.inputColor.text().strip():
            self.update_status("Error: Enter Color", is_error=True)
            return

        try:
            raw_weight = self.inputWeight.text().strip()
            g_val = int(float(raw_weight) * 1000) if raw_weight else "NA"
        except ValueError:
            g_val = "NA"

        new_row = {
            'Brand': self.comboBox.currentText(), 'Material': self.inputMaterial.text(),
            'Color': self.inputColor.text(), 'ID': self.inputID.text() if self.inputID.text().strip() else "NA",
            'InitialWeight': g_val, 'CurrentWeight': g_val, 'LastDried': "Never"
        }
        self.model.add_data(new_row)
        self.refresh_table()
        self.clear_unlocked_inputs()
        self.update_status("Spool Added Successfully!")

    def clear_unlocked_inputs(self):
        if not self.brandCheckBox.isChecked(): self.comboBox.setCurrentIndex(0)
        if not self.materialCheckBox.isChecked(): self.inputMaterial.clear()
        if not self.colorCheckBox.isChecked(): self.inputColor.clear()
        if not self.weightCheckBox.isChecked(): self.inputWeight.clear()
        self.inputID.clear()

    def delete_spool(self):
        selected = self.get_selected_rows()
        if not selected:
            self.update_status("Error: Select rows to delete!", is_error=True)
            return
        data = self.model.get_data()
        for index in sorted(selected, reverse=True):
            data.pop(index)
        self.model.save_all(data)
        self.refresh_table()
        self.update_status(f"Deleted {len(selected)} spools.")

    def update_weight(self):
        row = self.filamentTable.currentRow()
        if row >= 0:
            data = self.model.get_data()
            data[row]['CurrentWeight'] = self.inputWeight.text()
            self.model.save_all(data)
            self.refresh_table()
            self.update_status("Weight Updated!")

    def mark_dried(self):
        selected = self.get_selected_rows()
        if not selected:
            selected = [self.filamentTable.currentRow()] if self.filamentTable.currentRow() >= 0 else []
        if not selected:
            self.update_status("Error: Select rows to mark dried!", is_error=True)
            return
        data = self.model.get_data()
        for index in selected:
            data[index]['LastDried'] = str(date.today())
        self.model.save_all(data)
        self.refresh_table()
        self.update_status(f"Marked {len(selected)} spools as dried!")