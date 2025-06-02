import xlsxwriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import sys
import os
import socket
import getpass
import win32print
import win32ui
import win32api
from PIL import Image, ImageWin
import PyPDF2
from datetime import datetime
import pyodbc

# ================= SQL Server Configuration =================
SERVER = 'YOUR_SQL-SERVER NAME'
DATABASE = 'YOUR_DATABASE NAME'
USERNAME = 'YOUR_USERNAME'
PASSWORD = 'YOUR_PASSWORD'
DRIVER = '{ODBC Driver 17 for SQL Server}'


def connect_db():
    return pyodbc.connect(f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}')


def init_database():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            IF NOT EXISTS (
                SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'PrintLog'
            )
            CREATE TABLE PrintLog (
                id INT IDENTITY(1,1) PRIMARY KEY,
                document_name NVARCHAR(255),
                pc_name NVARCHAR(100),
                ip_address NVARCHAR(50),
                username NVARCHAR(100),
                timestamp DATETIME,
                page_count INT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"SQL Server connection error: {e}")


def insert_log(document_name, pc_name, ip_address, username, timestamp, page_count):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO PrintLog (document_name, pc_name, ip_address, username, timestamp, page_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (document_name, pc_name, ip_address, username, timestamp, page_count))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error inserting log into SQL Server: {e}")


def get_system_info():
    pc_name = socket.gethostname()
    ip_address = socket.gethostbyname(pc_name)
    username = getpass.getuser()
    return pc_name, ip_address, username


def list_printers():
    try:
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        return [printer[2] for printer in printers]
    except Exception as e:
        print(f"Error listing printers: {e}")
        return []


def count_pdf_pages(file_path):
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    except Exception as e:
        print(f"Error counting PDF pages: {e}")
        return 0


def print_image(printer_name, file_path):
    try:
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name)
        pdc.StartDoc(file_path)
        pdc.StartPage()

        img = Image.open(file_path)
        hdc = pdc.GetHandleOutput()
        dib = ImageWin.Dib(img)
        dib.draw(hdc, (0, 0))

        pdc.EndPage()
        pdc.EndDoc()
        print(f"Image printed to {printer_name}")
    except Exception as e:
        print(f"Error printing image: {e}")


def print_text(printer_name, file_path):
    try:
        win32api.ShellExecute(0, "print", file_path, f'/d:"{printer_name}"', ".", 0)
        print(f"Text printed to {printer_name}")
    except Exception as e:
        print(f"Error printing text: {e}")


def print_pdf(printer_name, file_path):
    try:
        win32api.ShellExecute(0, "print", file_path, f'/d:"{printer_name}"', ".", 0)
        print(f"PDF printed to {printer_name}")
    except Exception as e:
        print(f"Error printing PDF: {e}")


# ================= Admin Panel =================
# (Keep all your current imports)
import pyodbc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QDateEdit
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QIcon
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import xlsxwriter
import sys


def connect_db():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=DESKTOP-5I2QMLI\\SQLEXPRESS;'
            'DATABASE=PrintTracker;'
            'UID=sa;'
            'PWD=sa_123;'
        )
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None


class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖨️ Print Logs")
        self.setGeometry(0, 0, QApplication.desktop().availableGeometry().width(),
                         QApplication.desktop().availableGeometry().height())

        self.LIGHT_THEME = """
            QWidget { font-family: 'Segoe UI'; font-size: 10pt; background-color: #f9f9f9; }
            QTableWidget { background-color: #ffffff; border: 1px solid #ddd; }
            QHeaderView::section { background-color: #0078d7; color: white; padding: 6px; border: none; }
            QPushButton { background-color: #0078d7; color: white; border-radius: 5px; padding: 6px 12px; }
            QPushButton:hover { background-color: #005bb5; }
        """
        self.setStyleSheet(self.LIGHT_THEME)

        layout = QVBoxLayout()

        title_label = QLabel("🖨️ Print Logs")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #333; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter by username, document, IP, etc...")
        self.search_input.textChanged.connect(self.apply_filter)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.dateChanged.connect(self.apply_filter)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.apply_filter)

        self.dark_mode_toggle = QCheckBox("🌙 Dark Mode")
        self.dark_mode_toggle.stateChanged.connect(
            lambda state: self.setStyleSheet(self.LIGHT_THEME if state != Qt.Checked else """
            QWidget { background-color: #2e2e2e; color: #ddd; font-family: 'Segoe UI'; font-size: 10pt; }
            QTableWidget { background-color: #3c3c3c; color: #ddd; border: 1px solid #555; }
            QHeaderView::section { background-color: #444; color: white; padding: 6px; border: none; }
            QPushButton { background-color: #555; color: white; border-radius: 5px; padding: 6px 12px; }
            QPushButton:hover { background-color: #777; }
        """))

        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_settings)

        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(QLabel("📅 From:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(self.dark_mode_toggle)
        filter_layout.addWidget(self.reset_btn)
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "📎 Document Name", "💻 PC Name", "🌐 IP Address",
            "👤 Username", "🕒 Date & Time", "📄 Page Count"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        stats_layout = QHBoxLayout()
        self.total_jobs_label = QLabel("🧾 Total Print Jobs: 0")
        self.total_pages_label = QLabel("📄 Total Pages: 0")
        stats_layout.addWidget(self.total_jobs_label)
        stats_layout.addWidget(self.total_pages_label)
        layout.addLayout(stats_layout)

        export_layout = QHBoxLayout()
        self.export_excel_btn = QPushButton("📤 Export to Excel")
        self.export_excel_btn.clicked.connect(self.export_to_excel)
        self.export_pdf_btn = QPushButton("📝 Export to PDF")
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        self.delete_btn = QPushButton("🗑️ Delete Selected Row")
        self.delete_btn.clicked.connect(self.delete_selected_row)
        export_layout.addStretch()
        export_layout.addWidget(self.export_excel_btn)
        export_layout.addWidget(self.export_pdf_btn)
        export_layout.addWidget(self.delete_btn)
        layout.addLayout(export_layout)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        self.load_logs()

    def load_logs(self):
        try:
            conn = connect_db()
            if not conn:
                QMessageBox.critical(self, "Error", "Cannot connect to DB.")
                return
            cursor = conn.cursor()
            cursor.execute(
                "SELECT document_name, pc_name, ip_address, username, timestamp, page_count FROM PrintLog ORDER BY timestamp DESC")
            self.all_logs = cursor.fetchall()
            if self.all_logs:
                timestamps = [row[4].date() for row in self.all_logs if hasattr(row[4], 'date')]
                if timestamps:
                    self.start_date.setDate(QDate(timestamps[-1].year, timestamps[-1].month, timestamps[-1].day))
                    self.end_date.setDate(QDate(timestamps[0].year, timestamps[0].month, timestamps[0].day))
            self.display_logs(self.all_logs)
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed loading logs: {e}")

    def display_logs(self, logs):
        self.table.setRowCount(0)
        total_pages = 0
        for row_data in logs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)
            try:
                total_pages += int(row_data[5])
            except:
                pass
        self.total_jobs_label.setText(f"🧾 Total Print Jobs: {len(logs)}")
        self.total_pages_label.setText(f"📄 Total Pages: {total_pages}")

    def apply_filter(self):
        keyword = self.search_input.text().lower()
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()

        filtered = []
        for row in self.all_logs:
            timestamp = row[4]
            if hasattr(timestamp, 'date'):
                date_value = timestamp.date()
            else:
                continue
            if start_date <= date_value <= end_date:
                if any(keyword in str(cell).lower() for cell in row):
                    filtered.append(row)
        self.display_logs(filtered)

    def reset_settings(self):
        self.search_input.clear()
        if self.all_logs:
            timestamps = [row[4].date() for row in self.all_logs if hasattr(row[4], 'date')]
            if timestamps:
                self.start_date.setDate(QDate(timestamps[-1].year, timestamps[-1].month, timestamps[-1].day))
                self.end_date.setDate(QDate(timestamps[0].year, timestamps[0].month, timestamps[0].day))
        else:
            self.start_date.setDate(QDate.currentDate().addMonths(-1))
            self.end_date.setDate(QDate.currentDate())
        self.dark_mode_toggle.setChecked(False)
        self.display_logs(self.all_logs)
        self.status_label.setText("✅ Settings reset successfully.")
        QTimer.singleShot(3000, self.status_label.clear)

    def delete_selected_row(self):
        try:
            selected_row = self.table.currentRow()
            if selected_row >= 0:
                doc_name = self.table.item(selected_row, 0).text()
                reply = QMessageBox.question(self, 'Delete',
                                             f"Are you sure you want to delete the record for '{doc_name}'?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    conn = connect_db()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM PrintLog WHERE document_name = ?", (doc_name,))
                        conn.commit()
                        conn.close()
                    self.table.removeRow(selected_row)
                    self.status_label.setText(f"✅ Row '{doc_name}' deleted successfully.")
                    QTimer.singleShot(3000, self.status_label.clear)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete row: {e}")

    def export_to_excel(self):
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Save as Excel", "", "Excel Files (*.xlsx)")
            if not path:
                return
            workbook = xlsxwriter.Workbook(path)
            worksheet = workbook.add_worksheet()
            for col in range(self.table.columnCount()):
                worksheet.write(0, col, self.table.horizontalHeaderItem(col).text())
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    worksheet.write(row + 1, col, self.table.item(row, col).text())
            row_count = self.table.rowCount()
            worksheet.write(row_count + 2, 0, "Total Print Jobs:")
            worksheet.write(row_count + 2, 1, str(row_count))
            total_pages = sum(int(self.table.item(r, 5).text()) for r in range(row_count))
            worksheet.write(row_count + 3, 0, "Total Pages Printed:")
            worksheet.write(row_count + 3, 1, str(total_pages))
            worksheet.write(row_count + 5, 0, "H.O.D. Deshmukh J.V")
            workbook.close()
            self.status_label.setText("✅ Excel exported successfully.")
            QTimer.singleShot(3000, self.status_label.clear)
        except Exception as e:
            print(f"❌ Excel export failed: {e}")

    def export_to_pdf(self):
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Save as PDF", "", "PDF Files (*.pdf)")
            if not path:
                return
            c = canvas.Canvas(path, pagesize=A4)
            width, height = A4
            y = height - 50
            headers = [self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())]
            x_positions = [30, 150, 280, 400, 510, 620]
            for i, header in enumerate(headers):
                c.setFont("Helvetica-Bold", 10)
                c.drawString(x_positions[i], y, header)
            y -= 20
            c.setFont("Helvetica", 9)
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    c.drawString(x_positions[col], y, self.table.item(row, col).text()[:25])
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50
            if y < 100:
                c.showPage()
                y = height - 50
            c.setFont("Helvetica-Bold", 10)
            c.drawString(30, y - 30, f"Total Print Jobs: {self.table.rowCount()}")
            total_pages = sum(int(self.table.item(r, 5).text()) for r in range(self.table.rowCount()))
            c.drawString(30, y - 50, f"Total Pages Printed: {total_pages}")
            c.drawString(30, y - 80, "H.O.D. Deshmukh J.V")
            c.save()
            self.status_label.setText("✅ PDF exported successfully.")
            QTimer.singleShot(3000, self.status_label.clear)
        except Exception as e:
            print(f"❌ PDF export failed: {e}")


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = AdminPanel()
#     window.show()
#     sys.exit(app.exec_())


# ================= GUI Application =================
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFileDialog, QMessageBox, QDialog, QSpinBox, QRadioButton, QGroupBox, QFormLayout, QLineEdit
)
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtCore import Qt, QTimer

# Assuming these functions are defined elsewhere and imported properly:
# from utils import list_printers, print_image, print_text, print_pdf, count_pdf_pages, get_system_info, insert_log
# from admin_panel import AdminPanel

class PrinterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖨️ HP LaserJet Printer Manager")
        self.setGeometry(100, 100, 800, 300)
        self.setStyleSheet(""" 
            QWidget {
                font-family: 'Segoe UI';
                font-size: 11pt;
                background-color: #f4f7fb;
            }
            QLabel {
                font-size: 12pt;
            }
            QPushButton {
                padding: 10px 16px;
                background-color: #0078d4;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                text-align: center;
                border: none;
            }
            QPushButton:hover {
                background-color: #006bb3;
            }
            QComboBox {
                font-size: 11pt;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QComboBox:editable {
                background-color: #e6f7ff;
            }
            QComboBox:!editable {
                background-color: #ffffff;
            }
            QLabel.status {
                font-size: 14pt;
                font-weight: bold;
                color: #333;
                text-align: center;
                padding: 10px;
            }
            .error {
                color: red;
            }
            .success {
                color: green;
            }
        """)

        main_layout = QVBoxLayout()

        # Title
        self.label = QLabel("📄 Select a Printer and File to Print")
        self.label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        main_layout.addWidget(self.label)

        # Printer and File Selection
        top_layout = QHBoxLayout()
        self.printer_combo = QComboBox()
        self.printers = list_printers()
        if self.printers:
            self.printer_combo.addItems(self.printers)
        else:
            self.printer_combo.addItem("⚠️ No printers found")
        self.printer_combo.setMinimumWidth(250)
        top_layout.addWidget(QLabel("🖨️ Printer:"))
        top_layout.addWidget(self.printer_combo)

        self.file_button = QPushButton("📁 Select File")
        self.file_button.clicked.connect(self.select_file)
        top_layout.addWidget(self.file_button)

        self.print_button = QPushButton("🖨️ Print")
        self.print_button.clicked.connect(self.handle_print)
        top_layout.addWidget(self.print_button)

        self.page_setup_button = QPushButton("📑 Page Setup")
        self.page_setup_button.clicked.connect(self.open_page_setup_dialog)
        top_layout.addWidget(self.page_setup_button)

        main_layout.addLayout(top_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("status")
        main_layout.addWidget(self.status_label)

        self.admin_button = QPushButton("🔐 Open Admin Panel")
        self.admin_button.clicked.connect(self.open_admin_panel)
        main_layout.addWidget(self.admin_button)

        self.selected_file = None
        self.page_properties = {"copies": 1, "page_size": "A4", "orientation": "Portrait", "margins": (10, 10, 10, 10),
                                "paper_type": "Plain"}

        # Developer Label
        self.developer_label = QLabel("👨‍💻 Created For Computer Department ")
        self.developer_label.setAlignment(Qt.AlignCenter)
        self.developer_label.setStyleSheet("font-size: 10pt; color: #555; font-style: italic;")
        main_layout.addWidget(self.developer_label)

        self.setLayout(main_layout)

    def open_admin_panel(self):
        self.admin_panel = AdminPanel()
        self.admin_panel.show()

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select File to Print", "",
            "All Files (*.*);;Images (*.png *.jpg *.bmp *.jpeg);;Text Files (*.txt);;PDF Files (*.pdf)"
        )
        if file:
            self.selected_file = file
            self.status_label.setStyleSheet("color: green;")
            self.status_label.setText(f"✅ File Selected: <b>{os.path.basename(file)}</b>")
        else:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText("⚠️ No file selected.")

    def open_page_setup_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Page Setup")
        layout = QFormLayout()

        self.copies_spinbox = QSpinBox()
        self.copies_spinbox.setRange(1, 100)
        self.copies_spinbox.setValue(self.page_properties["copies"])
        layout.addRow("Copies:", self.copies_spinbox)

        self.page_size_group = QGroupBox("Page Size")
        self.page_size_layout = QVBoxLayout()
        self.page_size_a4 = QRadioButton("A4")
        self.page_size_a4.setChecked(self.page_properties["page_size"] == "A4")
        self.page_size_a3 = QRadioButton("A3")
        self.page_size_a3.setChecked(self.page_properties["page_size"] == "A3")
        self.page_size_layout.addWidget(self.page_size_a4)
        self.page_size_layout.addWidget(self.page_size_a3)
        self.page_size_group.setLayout(self.page_size_layout)
        layout.addRow(self.page_size_group)

        self.orientation_group = QGroupBox("Orientation")
        self.orientation_layout = QVBoxLayout()
        self.orientation_portrait = QRadioButton("Portrait")
        self.orientation_portrait.setChecked(self.page_properties["orientation"] == "Portrait")
        self.orientation_landscape = QRadioButton("Landscape")
        self.orientation_landscape.setChecked(self.page_properties["orientation"] == "Landscape")
        self.orientation_layout.addWidget(self.orientation_portrait)
        self.orientation_layout.addWidget(self.orientation_landscape)
        self.orientation_group.setLayout(self.orientation_layout)
        layout.addRow(self.orientation_group)

        self.margin_top = QSpinBox()
        self.margin_top.setRange(0, 50)
        self.margin_top.setValue(self.page_properties["margins"][0])
        self.margin_bottom = QSpinBox()
        self.margin_bottom.setRange(0, 50)
        self.margin_bottom.setValue(self.page_properties["margins"][1])
        self.margin_left = QSpinBox()
        self.margin_left.setRange(0, 50)
        self.margin_left.setValue(self.page_properties["margins"][2])
        self.margin_right = QSpinBox()
        self.margin_right.setRange(0, 50)
        self.margin_right.setValue(self.page_properties["margins"][3])

        layout.addRow("Top Margin:", self.margin_top)
        layout.addRow("Bottom Margin:", self.margin_bottom)
        layout.addRow("Left Margin:", self.margin_left)
        layout.addRow("Right Margin:", self.margin_right)

        self.paper_type_input = QLineEdit(self.page_properties["paper_type"])
        layout.addRow("Paper Type:", self.paper_type_input)

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_page_properties)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout = QHBoxLayout()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def apply_page_properties(self):
        self.page_properties["copies"] = self.copies_spinbox.value()
        self.page_properties["page_size"] = "A4" if self.page_size_a4.isChecked() else "A3"
        self.page_properties["orientation"] = "Portrait" if self.orientation_portrait.isChecked() else "Landscape"
        self.page_properties["margins"] = (
            self.margin_top.value(),
            self.margin_bottom.value(),
            self.margin_left.value(),
            self.margin_right.value()
        )
        self.page_properties["paper_type"] = self.paper_type_input.text()
        QMessageBox.information(self, "Page Setup", "Page setup applied successfully.")

    def handle_print(self):
        if not self.selected_file:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText("❌ Please select a file before printing.")
            return

        selected_printer = self.printer_combo.currentText()
        if "No printers found" in selected_printer:
            QMessageBox.critical(self, "Printer Error", "❌ No printer available. Please check your printer connection.")
            return

        file_ext = os.path.splitext(self.selected_file)[1].lower()

        try:
            if file_ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                self.simulate_printing(lambda: print_image(selected_printer, self.selected_file), 1)
            elif file_ext == '.txt':
                self.simulate_printing(lambda: print_text(selected_printer, self.selected_file), 1)
            elif file_ext == '.pdf':
                page_count = count_pdf_pages(self.selected_file)
                self.simulate_printing(lambda: print_pdf(selected_printer, self.selected_file), page_count)
            else:
                QMessageBox.warning(self, "Unsupported File", "❌ Unsupported file type.")
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"❌ An error occurred: {str(e)}")

    def simulate_printing(self, print_func, page_count):
        dialog = QDialog(self)
        dialog.setWindowTitle("🖨️ Printing in Progress")
        layout = QVBoxLayout()
        loading_label = QLabel()
        movie = QMovie("loading.gif")  # Ensure this file exists
        loading_label.setMovie(movie)
        movie.start()
        layout.addWidget(QLabel("Please wait while the document is being printed..."))
        layout.addWidget(loading_label)
        dialog.setLayout(layout)
        dialog.setFixedSize(300, 200)

        def complete_print():
            dialog.accept()
            print_func()
            pc_name, ip_address, username = get_system_info()
            insert_log(
                os.path.basename(self.selected_file),
                pc_name,
                ip_address,
                username,
                datetime.now(),
                page_count
            )
            QMessageBox.information(self, "Print Success", "✅ Document has been successfully sent to the printer.")
            self.status_label.setText("🖨️ Document printed successfully.")
            self.status_label.setStyleSheet("color: green;")

        QTimer.singleShot(2000, complete_print)
        dialog.exec_()


if __name__ == "__main__":
    init_database()
    app = QApplication(sys.argv)
    window = PrinterApp()
    window.show()
    sys.exit(app.exec_())



