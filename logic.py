"""
Logic for Filament Manager.
Creator: Adam Romero
Last Updated: 07/28/2026
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from gui import *
from model import FilamentModel
from datetime import date


class Logic(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.model = FilamentModel()

        # added these purely to remove my last 7 warnings, no idea if it matters, although I suspect it's just a coding style discrepancy.
        self.figure = None
        self.axes = None
        self.ax1 = None
        self.ax2 = None
        self.ax3 = None
        self.ax4 = None
        self.canvas = None

        #Sets the font for the status bar
        self.statusBar.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.update_status("Ready", success=True)

        #brand optins for adding filament
        brands = [
            "None Selected", "Atomic Filament", "Bambu Lab", "Cookiecad", "Creality",
            "Elegoo", "eSUN", "Fiberlogy", "Fillamentum", "FormFutura", "Gembird",
            "Hatchbox", "Inland", "MatterHackers", "NinjaTek", "Overture", "Polymaker",
            "Proto-Pasta", "Prusament", "Sunlu", "3DJAKE", "Other"
        ]
        self.comboBox.addItems(brands)
        self.searchBar.setPlaceholderText("Search by Brand, Material, Color, or ID...")
        self.searchBar.textChanged.connect(self.filter_table)

        #This connects the button presses of the dashboard to their respective functions
        self.setup_dashboard()
        self.addSpoolButton.clicked.connect(self.add_spool)
        self.updateWeightButton.clicked.connect(self.update_weight)
        self.dryButton.clicked.connect(self.mark_dried)
        self.deleteSpoolButton.clicked.connect(self.delete_spool)

        #This connects the checkboxes to the labels to toggle from Unlocked to Locked
        self.brandCheckBox.toggled.connect(
            lambda checked: self.brandCheckBox.setText("Locked" if checked else "Unlocked"))
        self.materialCheckBox.toggled.connect(
            lambda checked: self.materialCheckBox.setText("Locked" if checked else "Unlocked"))
        self.colorCheckBox.toggled.connect(
            lambda checked: self.colorCheckBox.setText("Locked" if checked else "Unlocked"))
        self.weightCheckBox.toggled.connect(
            lambda checked: self.weightCheckBox.setText("Locked" if checked else "Unlocked"))

        self.last_checked_row = None

        self.refresh_table()
        self.tabWidget.setCurrentIndex(0) #sets startup initial tab to Inventory



    def setup_dashboard(self) -> None:
        """Initiailizes the dashboard by adding all the widgets and their locations"""
        self.figure, self.axes = plt.subplots(2, 2, figsize=(8, 6))

        self.ax1 = self.axes[0, 0]
        self.ax2 = self.axes[0, 1]
        self.ax3 = self.axes[1, 0]
        self.ax4 = self.axes[1, 1]

        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self.dashboardCanvas)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.currentChanged.connect(self.update_dashboard)

    def update_dashboard(self, index: int) -> None:
        """Updates the dashboard everytime the tab is switched to it"""
        #Only run when switching to the Dashboard tab (index 1)
        if index != 1 or not hasattr(self, 'ax1'):
            return

        data = self.model.get_data()
        if not data:
            return

        #parse weights and collect materials
        weights = []
        materials = []

        for r in data:
            mat = r.get('Material', 'Unknown').strip()
            if not mat:
                mat = 'Unknown'
            materials.append(mat)

            val_str = str(r.get('CurrentWeight', '0')).replace('NA', '0')
            try:
                weight_val = float(val_str) if val_str.strip() else 0.0
            except ValueError:
                weight_val = 0.0
            weights.append(weight_val)

        #get unique material list and sum weights for each
        unique_mats = list(set(materials))

        sums = []
        for mat in unique_mats:
            total_weight = 0.0
            for m, w in zip(materials, weights):
                if m == mat:
                    total_weight += w
            sums.append(total_weight)

        # Clear old charts
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()

        #Bar Chart: Weight by Material
        self.ax1.bar(unique_mats, sums, color='#3498db')
        self.ax1.set_title("Weight by Material (g)")

        #Pie Chart: Material Distribution
        total_weight = sum(sums)
        if total_weight > 0:
            self.ax2.pie(sums, labels=unique_mats, autopct='%1.1f%%')
        else:
            self.ax2.text(0.5, 0.5, "No Weight Data Available", ha='center', va='center', fontsize=12)
            self.ax2.axis('off')

        self.ax2.set_title("Material Distribution")

        #Low Spool Alerts (<200g)
        low_spools = []
        for r, w in zip(data, weights):
            if w < 200:
                brand = r.get('Brand', '')
                color_name = r.get('Color', 'Unknown')
                spool_id = r.get('ID', 'NA')

                label = f"• {brand} {color_name}".strip()
                if spool_id != "NA" and spool_id != "":
                    label += f" ({spool_id})"
                label += f": {int(w)}g"

                low_spools.append(label)

        if low_spools:
            txt = "LOW SPOOL ALERTS (<200g):\n\n" + "\n".join(low_spools)
        else:
            txt = "LOW SPOOL ALERTS:\n\nNo low spools."

        self.ax3.text(0.0, 1.0, txt, color='red', fontweight='bold', va='top', fontsize=11)
        self.ax3.axis('off')

        #total Inventory Box (in kg)
        total_kg = total_weight / 1000
        self.ax4.text(0.5, 0.5, f"Total Inventory:\n{total_kg:.2f} kg", ha='center', va='center', fontsize=14,
                      fontweight='bold')
        self.ax4.axis('off')

        self.figure.tight_layout()
        self.canvas.draw_idle()
    def update_status(self, msg: str, success: bool = True):
        """helper function to call whenever the status bar gets updated"""
        color = "green" if success else "red"
        self.statusBar.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
        self.statusBar.showMessage(msg, 0) # 0 means persistent

    def filter_table(self) -> None:
        """used to take the input of the filter bar and use it to filter the filament table"""
        text = self.searchBar.text().lower()
        for i in range(self.filamentTable.rowCount()):
            match = any(text in (self.filamentTable.item(i, col).text().lower() if self.filamentTable.item(i, col) else "") for col in range(1, 5))
            self.filamentTable.setRowHidden(i, not match)

    def refresh_table(self) -> None:
        """Used to refresh the table with the new info everytime an action is performed."""
        self.filamentTable.setSortingEnabled(False)
        data = self.model.get_data()
        self.filamentTable.setRowCount(len(data))
        self.filamentTable.setColumnCount(8)

        self.filamentTable.setHorizontalHeaderLabels(
            ['Select', 'Brand', 'Material', 'Color', 'ID', 'Initial Weight(g)', 'Current Weight(g)', 'Last Dried']
        )

        #Set Column Widths in the table
        self.filamentTable.setColumnWidth(0, 50)
        self.filamentTable.setColumnWidth(1, 100)
        self.filamentTable.setColumnWidth(2, 75)
        self.filamentTable.setColumnWidth(5, 125)
        self.filamentTable.setColumnWidth(6, 125)

        keys = ['Brand', 'Material', 'Color', 'ID', 'InitialWeight', 'CurrentWeight', 'LastDried']

        for i, row in enumerate(data):
            # Checkbox setup
            chk = QCheckBox()
            chk.toggled.connect(lambda checked, current_row=i: self.handle_checkbox_click(current_row, checked))
            w = QWidget()
            l = QHBoxLayout(w)
            l.addWidget(chk)
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.setContentsMargins(0, 0, 0, 0)
            self.filamentTable.setCellWidget(i, 0, w)

            for j, key in enumerate(keys, 1):
                val_str = str(row.get(key, ''))

                if key == 'CurrentWeight':
                    try:
                        val = float(val_str.replace('NA', '0') or 0)
                    except ValueError:
                        val = 0.0

                    item = QTableWidgetItem(str(val))
                    # Foreground coloring
                    if val >= 500:
                        item.setForeground(QColor("green"))
                    elif val < 250:
                        item.setForeground(QColor("red"))
                    elif val < 500:
                        item.setForeground(QColor("orange"))
                    self.filamentTable.setItem(i, j, item)
                else:
                    self.filamentTable.setItem(i, j, QTableWidgetItem(val_str))

        self.filamentTable.setSortingEnabled(True)

    def add_spool(self) -> None:
        """used to add the spool to the table, handles all data handling for the inputs."""
        brand = self.comboBox.currentText()
        material = self.inputMaterial.text().strip()
        color = self.inputColor.text().strip()

        if brand == "None Selected" or not material or not color:
            self.update_status("Error: Brand, Material, and Color are required", False)
            return

        # Grab weight from spinBox
        w = str(self.spinBox.value())

        # Add spool to data model
        self.model.add_data({
            'Brand': brand,
            'Material': material,
            'Color': color,
            'ID': self.inputID.text().strip() or "NA",
            'InitialWeight': w,
            'CurrentWeight': w,
            'LastDried': "Never"
        })

        self.refresh_table()
        self.uncheck_all()
        self.inputID.clear()

        # Only reset fields if their checkbox is NOT checked (unlocked)
        if not self.brandCheckBox.isChecked():
            self.comboBox.setCurrentIndex(0)

        if not self.materialCheckBox.isChecked():
            self.inputMaterial.clear()

        if not self.colorCheckBox.isChecked():
            self.inputColor.clear()

        if not self.weightCheckBox.isChecked():
            self.spinBox.setValue(0)

        self.update_status("Success: Spool Added")

    def delete_spool(self) -> None:
        """Deletes any selected spools from the table"""
        selected = []
        for i in range(self.filamentTable.rowCount()):
            cell_widget = self.filamentTable.cellWidget(i, 0)
            if cell_widget and cell_widget.findChild(QCheckBox).isChecked():
                selected.append(i)

        if not selected:
            self.update_status("Error: Select at least one spool to Delete", False)
            return

        data = self.model.get_data()
        for i in sorted(selected, reverse=True):
            data.pop(i)
        self.model.save_all(data)
        self.refresh_table()
        self.uncheck_all()
        self.update_status("Success: Spool Deleted")

    def update_weight(self) -> None:
        """Updates the weight of any selected spools based on the weight input box"""
        selected = []
        for i in range(self.filamentTable.rowCount()):
            cell_widget = self.filamentTable.cellWidget(i, 0)
            if cell_widget and cell_widget.findChild(QCheckBox).isChecked():
                selected.append(i)

        if not selected:
            self.update_status("Error: Select at least one spool to Update", False)
            return

        weight_input = str(self.spinBox.value())

        data = self.model.get_data()
        for i in selected:
            data[i]['CurrentWeight'] = weight_input

        self.model.save_all(data)
        self.refresh_table()
        self.uncheck_all()

        # Reset spinBox back to 0
        self.spinBox.setValue(0)

        self.update_status(f"Success: Updated {len(selected)} spool(s)")
    def mark_dried(self) -> None:
        #NOTE TO SELLFFFFFFF: Come back and finish this docstring.
        selected = []
        for i in range(self.filamentTable.rowCount()):
            cell_widget = self.filamentTable.cellWidget(i, 0)
            if cell_widget and cell_widget.findChild(QCheckBox).isChecked():
                selected.append(i)

        #exits if nothing was checked
        if not selected:
            self.update_status("Error: Select at least one spool to Dry", False)
            return

        data = self.model.get_data()
        today = str(date.today())

        for i in selected:
            data[i]['LastDried'] = today

        self.model.save_all(data)
        self.refresh_table()
        self.update_status("Success: Dried spool(s)")

    def uncheck_all(self) -> None:
        """Unchecks the selection checkbox on every row in the table."""
        table = self.filamentTable
        for i in range(table.rowCount()):
            cell_widget = table.cellWidget(i, 0)
            if cell_widget:
                chk = cell_widget.findChild(QCheckBox)
                if chk:
                    chk.blockSignals(True)
                    chk.setChecked(False)
                    chk.blockSignals(False)

        self.last_checked_row = None

    def handle_checkbox_click(self, row: int, state: bool) -> None:
        """Checks if the user is holding the shift key down to make a multi selection of table componets"""
        modifiers = QApplication.keyboardModifiers()
        is_shift_held = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)

        if is_shift_held and self.last_checked_row is not None:
            # Determine start and end row numbers (handles clicking top-to-bottom or bottom-to-top)
            start_row = min(self.last_checked_row, row)
            end_row = max(self.last_checked_row, row)

            # Loop through every row in the range and match the checkbox state
            for i in range(start_row, end_row + 1):
                cell_widget = self.filamentTable.cellWidget(i, 0)
                if cell_widget:
                    chk = cell_widget.findChild(QCheckBox)
                    if chk:
                        # Block signals briefly so we don't trigger recursive events
                        chk.blockSignals(True)
                        chk.setChecked(state)
                        chk.blockSignals(False)

        self.last_checked_row = row