import os
import sys

import PyQt5
import pymysql
from PyQt5 import QtWidgets  # works for pyqt5
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, \
    QHBoxLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, \
    QComboBox
from PyQt5.QtWidgets import QDialog, QFormLayout


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def show_success_message(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(message)
    msg_box.setWindowTitle("Success")
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


def startup_message():
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText("Notice: The first time you create a column in a table, it will not show up until you add data.")
    msg_box.setWindowTitle("Notice")
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


def show_error_message(message):
    print(message)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle("Error")
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


class ConnectDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set up the dialog layout
        self.setWindowTitle("Connect to SQL Server")
        self.setWindowIcon(QIcon(resource_path("images/sql.ico")))
        layout = QFormLayout()
        self.host_input = QLineEdit()
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.db_input = QLineEdit()
        layout.addRow("Host:", self.host_input)
        layout.addRow("Username:", self.user_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("Database:", self.db_input)

        # Set up the buttons
        self.submit_button = QPushButton("Connect")
        self.submit_button.clicked.connect(self.accept)
        layout.addRow(self.submit_button)

        self.setLayout(layout)

    def get_connection_info(self):
        # Return the entered connection information as a dictionary
        return {
            "host": self.host_input.text(),
            "user": self.user_input.text(),
            "password": self.password_input.text(),
            "db": self.db_input.text()
        }


class ServerDetailsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.host_label = QLabel("Host:")
        self.host_input = QLineEdit()
        self.user_label = QLabel("User:")
        self.user_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.db_label = QLabel("Database:")
        self.db_input = QLineEdit()

        layout = QGridLayout()
        layout.addWidget(self.host_label, 0, 0)
        layout.addWidget(self.host_input, 0, 1)
        layout.addWidget(self.user_label, 1, 0)
        layout.addWidget(self.user_input, 1, 1)
        layout.addWidget(self.password_label, 2, 0)
        layout.addWidget(self.password_input, 2, 1)
        layout.addWidget(self.db_label, 3, 0)
        layout.addWidget(self.db_input, 3, 1)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.accept)
        layout.addWidget(self.submit_button, 4, 1)

        self.setLayout(layout)
        self.setWindowTitle("Server Details")

    def get_details(self):
        host = self.host_input.text()
        user = self.user_input.text()
        password = self.password_input.text()
        db = self.db_input.text()
        return host, user, password, db


class MainWindow(QMainWindow):
    def __init__(self):
        global host, user, password, db
        super().__init__()

        server_details_dialog = ServerDetailsDialog()
        if server_details_dialog.exec_() == QDialog.Accepted:
            host, user, password, db = server_details_dialog.get_details()

        try:
            self.db = pymysql.connect(host=host, user=user, password=password, db=db)
            self.cursor = self.db.cursor()
        except pymysql.Error as e:
            print("Error connecting to database:", e)
            sys.exit(1)

        # Initialize main layout
        main_layout = QVBoxLayout()

        # Initialize table and value viewer
        self.setWindowIcon(QIcon(resource_path("images/sql.ico")))
        startup_message()
        self.table_tree = QTreeWidget()
        self.table_tree.setHeaderLabels(["Tables"])
        self.table_tree.itemClicked.connect(self.show_table_values)
        self.value_table = QTableWidget()
        self.value_table.setColumnCount(2)
        self.value_table.itemChanged.connect(self.update_table_value)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_table)
        self.timer.start(1000)  #

        # Initialize buttons
        add_table_button = QPushButton("Add Table")
        add_table_button.clicked.connect(self.add_table)
        edit_table_button = QPushButton("Edit Table")
        edit_table_button.clicked.connect(self.edit_table)
        remove_table_button = QPushButton("Remove Table")
        remove_table_button.clicked.connect(self.remove_table)
        edit_value_button = QPushButton("Edit Value")
        edit_value_button.clicked.connect(self.edit_value)
        add_value_button = QPushButton("Add Value")
        add_value_button.clicked.connect(self.add_value)
        remove_value_button = QPushButton("Remove Value")
        remove_value_button.clicked.connect(self.remove_value)
        add_column_button = QPushButton("Add Column")
        add_column_button.clicked.connect(self.add_column)
        remove_column_button = QPushButton("Remove Column")
        remove_column_button.clicked.connect(self.remove_column)

        # Add buttons to button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(add_table_button)
        button_layout.addWidget(edit_table_button)
        button_layout.addWidget(remove_table_button)
        button_layout.addWidget(add_value_button)
        button_layout.addWidget(remove_value_button)
        button_layout.addWidget(add_column_button)
        button_layout.addWidget(edit_value_button)
        button_layout.addWidget(remove_column_button)

        # Add table and button layouts to main layout
        main_layout.addWidget(self.table_tree)
        main_layout.addWidget(self.value_table)
        main_layout.addLayout(button_layout)

        # Set main widget and window properties
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setWindowTitle("SQL Database Manager")
        self.setWindowIcon(QIcon(resource_path("images/sql.ico")))

        # Populate table tree with existing tables
        self.populate_table_tree()

        # Initialize add column dialog
        self.add_column_dialog = QDialog(self)
        self.add_column_dialog.setWindowTitle("Add Column")
        self.add_column_dialog_layout = QGridLayout()
        self.add_column_dialog.setLayout(self.add_column_dialog_layout)

        # Add column dialog widgets
        self.column_name_label = QLabel("Column Name:")
        self.column_name_input = QLineEdit()
        self.column_type_label = QLabel("Column Type:")
        self.column_type_dropdown = QComboBox()
        self.column_type_dropdown.addItems(["INT", "VARCHAR(255)", "DATE", "DATETIME"])
        self.add_column_dialog_layout.addWidget(self.column_name_label, 0, 0)
        self.add_column_dialog_layout.addWidget(self.column_name_input, 0, 1)
        self.add_column_dialog_layout.addWidget(self.column_type_label, 1, 0)
        self.add_column_dialog_layout.addWidget(self.column_type_dropdown, 1, 1)

    def get_columns(self, table_name):
        self.cursor.execute(f"DESCRIBE {table_name}")
        return [column[0] for column in self.cursor.fetchall()]

    def get_primary_key(self, table_name):
        self.cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
        primary_key = self.cursor.fetchone()
        if primary_key is not None:
            return primary_key[4]
        else:
            return None

    def update_table_value(self, item):
        row = item.row()
        col = item.column()
        table_name = self.table_tree.currentItem().text(0)
        primary_key = self.get_primary_key(table_name)
        primary_key_col = self.get_columns(table_name).index(primary_key)
        primary_key_val = self.value_table.item(row, primary_key_col).text()
        column_name = self.value_table.horizontalHeaderItem(col).text()
        new_value = item.text()
        query = f"UPDATE {table_name} SET {column_name} = '{new_value}' WHERE {primary_key} = '{primary_key_val}'"
        try:
            self.cursor.execute(query)
            self.commit_changes()
        except Exception as e:
            show_error_message(f"Error updating value: {str(e)}")
            self.refresh_table()

    def commit_changes(self):
        try:
            self.db.commit()
            print("Changes successfully committed.")
        except:
            self.db.rollback()
            print("Error committing changes to the database.")

    def get_column_type(self, table_name, column_name):
        self.cursor.execute(f"SHOW COLUMNS FROM {table_name} WHERE Field = '{column_name}'")
        column_data = self.cursor.fetchone()
        if column_data is not None:
            column_type = column_data[1]
            return column_type
        else:
            return None

    def refresh_table(self):
        try:
            table_name = self.table_tree.currentItem()
            if table_name is None:
                return
            self.cursor.execute(f"SELECT * FROM {table_name}")
            data = self.cursor.fetchall()
            num_rows = len(data)
            num_cols = len(self.get_columns(table_name))
            self.value_table.setRowCount(num_rows)
            self.value_table.setColumnCount(num_cols)
            self.value_table.setHorizontalHeaderLabels(self.get_columns(table_name))
            for i, row_data in enumerate(data):
                for j, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    self.value_table.setItem(i, j, item)

            # Set default values for new columns
            columns = self.get_columns(table_name)
            for i in range(num_cols, len(columns)):
                column_type = self.get_column_type(table_name, columns[i])
                if column_type == "int":
                    for j in range(num_rows):
                        item = QTableWidgetItem(str(0))
                        self.value_table.setItem(j, i, item)
                else:
                    for j in range(num_rows):
                        item = QTableWidgetItem("hi")
                        self.value_table.setItem(j, i, item)

        except Exception as e:
            print(f"Error refreshing table: {str(e)}")

    def populate_table_tree(self):
        self.table_tree.clear()
        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()
        for table in tables:
            table_name = table[0]
            table_item = QTreeWidgetItem([table_name])
            self.table_tree.addTopLevelItem(table_item)

    def show_table_values(self, item, column):
        table_name = item.text(column)
        self.cursor.execute(f"SELECT * FROM {table_name}")
        values = self.cursor.fetchall()

        # Set the number of rows and columns in the table
        num_rows = len(values)
        num_columns = len(values[0]) if num_rows > 0 else 0
        self.value_table.setRowCount(num_rows)
        self.value_table.setColumnCount(num_columns)

        # Set column headers based on the retrieved data
        if num_rows > 0:
            column_headers = [desc[0] for desc in self.cursor.description]
            self.value_table.setHorizontalHeaderLabels(column_headers)

        # Populate the table with data
        for i, value in enumerate(values):
            for j, column in enumerate(value):
                item = QTableWidgetItem(str(column))
                self.value_table.setItem(i, j, item)

        def update_table_value(self, item):
            table_item = self.table_tree.currentItem()
            if table_item is None:
                return
            table_name = table_item.text(0)
            row = item.row()
            column = item.column()
            column_name = self.value_table.horizontalHeaderItem(column).text()

            primary_key = self.get_primary_key(table_name)
            primary_key_value = self.value_table.item(row, 0).text()
            primary_key_col = self.get_columns(table_name).index(primary_key) + 1

            if column == primary_key_col:
                # Do not update primary key column
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                return

            # Build the SQL query
            value = item.text()
            primary_key_name = self.get_primary_key(table_name)

            if column_name is None or value is None:
                print("none")
                pass
            elif isinstance(column_name, PyQt5.QtWidgets.QTableWidgetItem):
                print("oops")
                pass
            else:
                sql = f"UPDATE {table_name} SET {column_name} = %s WHERE {primary_key_name} = %s"
                params = (value, primary_key_value)

                # Execute the query
                try:
                    self.cursor.execute(sql, params)
                    self.db.commit()
                except pymysql.Error as e:
                    print("Error updating table value: " + str(e))
                    self.refresh_table()

                self.show_table_values(self.table_tree.currentItem(), 0)

    def get_primary_key_name(self, table_name):
        sql = f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if result:
            return result[4]
        else:
            return None

    def add_table(self):
        table_name, ok = QInputDialog.getText(self, "Add Table", "Table Name:")
        if ok and table_name:
            sql = f"CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY)"
            try:
                self.cursor.execute(sql)
                self.db.commit()
                table_item = QTreeWidgetItem([table_name])
                self.table_tree.addTopLevelItem(table_item)
            except Exception as e:
                print(f"Error creating table: {e}")
                self.db.rollback()
                show_error_message(f"Failed to create table: {e}")

    def edit_table(self):
        current_table = self.table_tree.currentItem()
        if current_table:
            new_table_name, ok = QInputDialog.getText(self, "Edit Table", "New Table Name:", text=current_table.text(0))
            if ok and new_table_name:
                old_table_name = current_table.text(0)
                sql = f"ALTER TABLE {old_table_name} RENAME TO {new_table_name}"
                try:
                    self.cursor.execute(sql)
                    self.db.commit()
                    current_table.setText(0, new_table_name)
                except Exception as e:
                    print(f"Error renaming table: {e}")
                    self.db.rollback()
                    show_error_message(f"Failed to rename table: {e}")
        else:
            show_error_message("No table selected.")

    def remove_table(self):
        current_table = self.table_tree.currentItem()
        if current_table:
            table_name = current_table.text(0)
            confirm = QMessageBox.question(self, "Delete Table",
                                           f"Are you sure you want to delete the table '{table_name}'?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                sql = f"DROP TABLE {table_name}"
                try:
                    self.cursor.execute(sql)
                    self.db.commit()
                    self.table_tree.takeTopLevelItem(self.table_tree.indexOfTopLevelItem(current_table))
                    self.value_table.setRowCount(0)
                except Exception as e:
                    print(f"Error deleting table: {e}")
                    self.db.rollback()
                    show_error_message(f"Failed to delete table: {e}")
        else:
            show_error_message("No table selected.")

    def add_value(self):
        current_table = self.table_tree.currentItem()
        if current_table:
            table_name = self.table_tree.currentItem().text(0)
            print(table_name)
            columns = self.get_columns(table_name)
            print(columns)
            values = []
            for column in columns:
                print(column)
                value, ok = QInputDialog.getText(self, f"Add Value - {column}", f"Enter value for {column}:")

                if ok:
                    print(value)
                    values.append(value)
                else:
                    return
            values_str = ", ".join([f"'{value}'" for value in values])
            columns_str = ", ".join(columns)
            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
            try:
                self.cursor.execute(sql)
                self.db.commit()
                show_success_message(f"Success! Added {values_str} to {columns_str} in {table_name}")
            except Exception as e:
                print(f"Error adding value: {e}")
                show_error_message(str(e))
        else:
            show_error_message("No table Selected")

    def remove_value(self):
        current_table = self.table_tree.currentItem()
        if current_table:
            item = self.value_table.currentItem()
            if item:
                row = item.row()
                primary_key_name = self.get_primary_key_name(self.table_tree.currentItem().text(0))
                primary_key_value = self.value_table.item(row, 0).text()
                sql = \
                    f"DELETE FROM {self.table_tree.currentItem().text(0)} WHERE {primary_key_name} = {primary_key_value} "
                try:
                    self.cursor.execute(sql)
                    self.db.commit()
                    self.value_table.removeRow(row)
                except Exception as e:
                    print(f"Error deleting value: {e}")
                    self.db.rollback()
                    show_error_message(f"Failed to delete value: {e}")

            else:
                show_error_message("No value selected.")
        else:
            show_error_message("No table selected.")

    def edit_value(self):
        current_table = self.table_tree.currentItem()
        if current_table:
            selected_items = self.value_table.selectedItems()
            if selected_items:
                if len(selected_items) == 1:
                    row = selected_items[0].row()
                    column = selected_items[0].column()
                    item = self.value_table.item(row, column)
                    new_value, ok = QInputDialog.getText(self, "Edit Value", "New Value:", text=item.text())
                    if ok:
                        item.setText(new_value)
                        self.update_table_value(item)
            else:
                show_error_message("No items selected.")
        else:
            show_error_message("No tables selected.")

    def add_column(self):
        current_table = self.table_tree.currentItem()
        if current_table:
            self.add_column_dialog.show()

            def ok_pressed(default_value=None):
                table_name = self.table_tree.currentItem().text(0)
                column_name = self.column_name_input.text()
                column_type = self.column_type_dropdown.currentText()
                if column_type == 'INT':
                    default_value = 0
                elif column_type == 'VARCHAR(255)':
                    default_value = 'NULL'
                else:
                    show_error_message("What did you even do?")
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
                try:
                    self.cursor.execute(sql)
                    self.db.commit()
                    self.add_column_dialog.close()
                    self.populate_table_tree()
                    self.refresh_table()
                    print('success')
                    # self.show_success_message(f"Success, Column '{column_name}' added to table '{table_name}'.")
                except Exception as e:
                    print(f"Error adding column: {e}")
                    self.db.rollback()
                    show_error_message(f"Failed to add column: {e}")

            ok_button = QPushButton("OK")
            ok_button.clicked.connect(ok_pressed)
            self.add_column_dialog_layout.addWidget(ok_button, 2, 0, 1, 2)

        elif current_table is None:
            show_error_message("No table selected!")
        else:
            show_error_message("No table selected!")

    def remove_column(self):
        current_table = self.table_tree.currentItem()
        if current_table:
            table_name = current_table.text(0)
            column_name = self.column_name_input.text()
            if column_name:
                confirm = QMessageBox.question(self, "Delete Column",
                                               f"Are you sure you want to delete the column '{column_name}'?",
                                               QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
                    try:
                        self.cursor.execute(sql)
                        self.db.commit()
                        self.refresh_table()
                    except Exception as e:
                        print(f"Error deleting column: {e}")
                        self.db.rollback()
                        show_error_message(f"Failed to delete column: {e}")
            else:
                show_error_message("No column selected.")
        else:
            show_error_message("No table selected.")

    def get_column_names(self, table_name):
        sql = f"SHOW COLUMNS FROM {table_name}"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if result:
            column_names = []
            for column in result:
                column_names.append(column[0])
            return column_names
        else:
            return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowIcon(QIcon(resource_path('images/sql.ico')))
    app.setWindowIcon(QIcon(resource_path('images/sql.ico')))
    window.show()
    app.setWindowIcon(QIcon(resource_path("images/sql.ico")))
    sys.exit(app.exec_())
