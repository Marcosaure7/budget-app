import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
import sqlite3
from datetime import datetime

class BudgetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Budget App")
        self.setGeometry(100, 100, 600, 400)
        
        self.initialize_database()
        self.init_ui()

        self.load_transactions()

    def initialize_database(self):
        self.conn = sqlite3.connect("budget.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                category TEXT,
                date TEXT
            )
        """)
        self.conn.commit()

    def init_ui(self):
        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Input fields
        self.input_layout = QHBoxLayout()
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Montant")
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Catégorie")
        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.add_transaction)
        self.input_layout.addWidget(self.amount_input)
        self.input_layout.addWidget(self.category_input)
        self.input_layout.addWidget(self.add_button)
        self.layout.addLayout(self.input_layout)

        # Table to display transactions
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Montant", "Catégorie", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

    def add_transaction(self):
        amount = self.amount_input.text()
        category = self.category_input.text()
        if amount and category:
            try:
                amount = amount.replace(",", ".")
                if amount.count('+') == 0 and amount.count('-') == 0:
                    amount = '-' + amount
                if not amount.replace('.', '', 1).replace('-', '').isdigit():
                    raise ValueError("Montant invalide")
                amount = float(amount)
                date = datetime.now().strftime("%Y-%m-%d")
                self.cursor.execute(
                    "INSERT INTO transactions (amount, category, date) VALUES (?, ?, ?)",
                    (amount, category, date)
                )
                self.conn.commit()
                self.amount_input.clear()
                self.category_input.clear()
                self.load_transactions()
            except ValueError as error:
                print("Erreur: ", error)

    def load_transactions(self):
        self.table.setRowCount(0)
        self.cursor.execute("SELECT amount, category, date FROM transactions")
        for row_data in self.cursor.fetchall():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                str_data = str(data)
                text_color = "black"
                if col == 0:
                    try:
                        if float(data) <= 0:
                            str_data.replace("-", "")
                        else:
                            str_data = "+ " + str_data
                            text_color = "green"
                    except ValueError:
                        pass
                
                item = QTableWidgetItem(str_data)
                item.setForeground(QBrush(QColor(text_color)))
                self.table.setItem(row, col, item)

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BudgetApp()
    window.show()
    sys.exit(app.exec_())