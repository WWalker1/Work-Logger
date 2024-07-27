import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import logging_logic as log

class WorkLogApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Work Log Application")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Input fields
        input_layout = QHBoxLayout()
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("Date (YYYY-MM-DD)")
        self.minutes_input = QLineEdit()
        self.minutes_input.setPlaceholderText("Minutes worked")
        self.pay_rate_input = QLineEdit()
        self.pay_rate_input.setPlaceholderText("Pay rate")
        self.project_title_input = QLineEdit()
        self.project_title_input.setPlaceholderText("Project title")
        input_layout.addWidget(self.date_input)
        input_layout.addWidget(self.minutes_input)
        input_layout.addWidget(self.pay_rate_input)
        input_layout.addWidget(self.project_title_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Entry")
        self.update_button = QPushButton("Update Entry")
        self.delete_button = QPushButton("Delete Entry")
        self.weekly_stats_button = QPushButton("Show Weekly Stats")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.weekly_stats_button)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Minutes", "Pay Rate", "Project Title"])

        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

        # Connect buttons to functions
        self.add_button.clicked.connect(self.add_entry)
        self.update_button.clicked.connect(self.update_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.weekly_stats_button.clicked.connect(self.show_weekly_stats)
        self.table.itemClicked.connect(self.populate_input_fields)

        self.load_entries()

    def load_entries(self):
        entries = log.read_entries()
        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            for col, value in enumerate(entry):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def add_entry(self):
        date = self.date_input.text()
        minutes = self.minutes_input.text()
        pay_rate = self.pay_rate_input.text()
        project_title = self.project_title_input.text()

        if not (log.validate_date(date) and log.validate_minutes(minutes) and log.validate_pay_rate(pay_rate)):
            self.show_error("Invalid input. Please check your entries.")
            return

        log.create_entry(date, minutes, pay_rate, project_title)
        self.load_entries()
        self.clear_input_fields()

    def update_entry(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            self.show_error("Please select a row to update.")
            return

        date = self.date_input.text()
        minutes = self.minutes_input.text()
        pay_rate = self.pay_rate_input.text()
        project_title = self.project_title_input.text()

        if not (log.validate_date(date) and log.validate_minutes(minutes) and log.validate_pay_rate(pay_rate)):
            self.show_error("Invalid input. Please check your entries.")
            return

        if log.update_entry(selected_row, date, minutes, pay_rate, project_title):
            self.load_entries()
            self.clear_input_fields()
        else:
            self.show_error("Failed to update entry.")

    def delete_entry(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            self.show_error("Please select a row to delete.")
            return

        if log.delete_entry(selected_row):
            self.load_entries()
            self.clear_input_fields()
        else:
            self.show_error("Failed to delete entry.")

    def populate_input_fields(self, item):
        row = item.row()
        self.date_input.setText(self.table.item(row, 0).text())
        self.minutes_input.setText(self.table.item(row, 1).text())
        self.pay_rate_input.setText(self.table.item(row, 2).text())
        self.project_title_input.setText(self.table.item(row, 3).text())

    def clear_input_fields(self):
        self.date_input.clear()
        self.minutes_input.clear()
        self.pay_rate_input.clear()
        self.project_title_input.clear()

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_weekly_stats(self):
        stats = log.calculate_weekly_stats()
        if not stats:
            self.show_error("No data available for weekly statistics.")
            return

        stats_window = WeeklyStatsWindow(stats)
        stats_window.exec_()

class WeeklyStatsWindow(QMessageBox):
    def __init__(self, stats):
        super().__init__()
        self.setWindowTitle("Weekly Statistics")
        self.setIcon(QMessageBox.Information)

        text = "Weekly Statistics:\n\n"
        for week in stats:
            text += f"Week: {week['week']}\n"
            text += f"Total Hours: {week['total_hours']}\n"
            text += f"Total Pay (before tax): ${week['total_pay']:.2f}\n"
            text += f"Average Hourly Rate: ${week['avg_hourly_rate']:.2f}\n"
            text += f"Take Home Pay: ${week['take_home_pay']:.2f}\n\n"

        self.setText(text)
        self.setStandardButtons(QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WorkLogApp()
    window.show()
    sys.exit(app.exec_())