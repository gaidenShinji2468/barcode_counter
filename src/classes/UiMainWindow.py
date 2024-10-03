from PyQt5 import QtCore, QtGui, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, pre_close_event):
        super().__init__()
        self.pre_close_event = pre_close_event

    # Sobrescribir el método closeEvent
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Cerrar aplicación",
            "Se perderán los cambios que no se hayan guardado. ¿Estás segur@?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )

        if reply == QtWidgets.QMessageBox.Yes:
            print("Application is closing...")
            self.pre_close_event()
            event.accept()
        else:
            event.ignore()


class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(470, 550)
        MainWindow.setFixedSize(470, 550)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setObjectName("central_widget")
        self.counter_container = QtWidgets.QWidget(self.central_widget)
        self.counter_container.setGeometry(QtCore.QRect(10, 90, 451, 221))
        self.counter_container.setObjectName("counter_container")
        self.code_container = QtWidgets.QWidget(self.counter_container)
        self.code_container.setGeometry(QtCore.QRect(220, 0, 141, 71))
        self.code_container.setObjectName("code_container")
        self.code_label = QtWidgets.QLabel(self.code_container)
        self.code_label.setGeometry(QtCore.QRect(10, 10, 58, 16))
        self.code_label.setObjectName("code_label")
        self.code = QtWidgets.QLineEdit(self.code_container)
        self.code.setGeometry(QtCore.QRect(10, 30, 121, 28))
        self.code.setObjectName("code")
        self.size_container = QtWidgets.QWidget(self.counter_container)
        self.size_container.setGeometry(QtCore.QRect(0, 0, 81, 71))
        self.size_container.setObjectName("size_container")
        self.size_label = QtWidgets.QLabel(self.size_container)
        self.size_label.setGeometry(QtCore.QRect(0, 10, 58, 16))
        self.size_label.setObjectName("size_label")
        self.size = QtWidgets.QLineEdit(self.size_container)
        self.size.setGeometry(QtCore.QRect(0, 30, 71, 28))
        self.size.setObjectName("size")
        self.count_container = QtWidgets.QWidget(self.counter_container)
        self.count_container.setGeometry(QtCore.QRect(360, 0, 91, 71))
        self.count_container.setObjectName("count_container")
        self.count_label = QtWidgets.QLabel(self.count_container)
        self.count_label.setGeometry(QtCore.QRect(10, 10, 58, 16))
        self.count_label.setObjectName("count_label")
        self.count = QtWidgets.QLineEdit(self.count_container)
        self.count.setGeometry(QtCore.QRect(10, 30, 71, 28))
        self.count.setReadOnly(False)
        self.count.setObjectName("count")
        self.save_count = QtWidgets.QPushButton(self.counter_container)
        self.save_count.setGeometry(QtCore.QRect(0, 180, 121, 31))
        self.save_count.setStyleSheet("")
        self.save_count.setDefault(False)
        self.save_count.setFlat(False)
        self.save_count.setObjectName("save_count")
        self.client = QtWidgets.QLabel(self.counter_container)
        self.client.setGeometry(QtCore.QRect(0, 90, 241, 16))
        self.client.setObjectName("client")
        self.piece = QtWidgets.QLabel(self.counter_container)
        self.piece.setGeometry(QtCore.QRect(0, 130, 241, 16))
        self.piece.setObjectName("piece")
        self.clean_count = QtWidgets.QPushButton(self.counter_container)
        self.clean_count.setGeometry(QtCore.QRect(130, 180, 121, 31))
        self.clean_count.setObjectName("clean_count")
        self.order_num_container = QtWidgets.QWidget(self.counter_container)
        self.order_num_container.setGeometry(QtCore.QRect(80, 0, 141, 71))
        self.order_num_container.setObjectName("order_num_container")
        self.order_num = QtWidgets.QLineEdit(self.order_num_container)
        self.order_num.setGeometry(QtCore.QRect(10, 30, 121, 28))
        self.order_num.setObjectName("order_num")
        self.order_num_label = QtWidgets.QLabel(self.order_num_container)
        self.order_num_label.setGeometry(QtCore.QRect(10, 10, 121, 16))
        self.order_num_label.setObjectName("order_num_label")
        self.end_record = QtWidgets.QPushButton(self.counter_container)
        self.end_record.setEnabled(False)
        self.end_record.setGeometry(QtCore.QRect(330, 130, 90, 28))
        self.end_record.setObjectName("end_record")
        self.delete_record = QtWidgets.QPushButton(self.counter_container)
        self.delete_record.setEnabled(False)
        self.delete_record.setGeometry(QtCore.QRect(330, 170, 90, 28))
        self.delete_record.setObjectName("delete_record")
        self.update_record = QtWidgets.QPushButton(self.counter_container)
        self.update_record.setEnabled(False)
        self.update_record.setGeometry(QtCore.QRect(330, 90, 90, 28))
        self.update_record.setObjectName("update_record")
        self.header_container = QtWidgets.QWidget(self.central_widget)
        self.header_container.setGeometry(QtCore.QRect(10, 10, 451, 80))
        self.header_container.setObjectName("header_container")
        self.title = QtWidgets.QLabel(self.header_container)
        self.title.setGeometry(QtCore.QRect(50, 10, 151, 61))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.type = QtWidgets.QWidget(self.header_container)
        self.type.setGeometry(QtCore.QRect(260, 20, 171, 41))
        self.type.setObjectName("type")
        self.add = QtWidgets.QRadioButton(self.type)
        self.add.setGeometry(QtCore.QRect(10, 10, 71, 21))
        self.add.setChecked(True)
        self.add.setObjectName("add")
        self.takeout = QtWidgets.QRadioButton(self.type)
        self.takeout.setGeometry(QtCore.QRect(90, 10, 71, 21))
        self.takeout.setObjectName("takeout")
        self.list_container = QtWidgets.QWidget(self.central_widget)
        self.list_container.setGeometry(QtCore.QRect(10, 310, 451, 231))
        self.list_container.setObjectName("list_container")
        self.list = QtWidgets.QListWidget(self.list_container)
        self.list.setGeometry(QtCore.QRect(0, 0, 451, 181))
        self.list.setStyleSheet("")
        self.list.setObjectName("list")
        self.active = QtWidgets.QPushButton(self.list_container)
        self.active.setGeometry(QtCore.QRect(0, 190, 90, 28))
        self.active.setObjectName("active")
        self.completed = QtWidgets.QPushButton(self.list_container)
        self.completed.setGeometry(QtCore.QRect(100, 190, 90, 28))
        self.completed.setObjectName("completed")
        MainWindow.setCentralWidget(self.central_widget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.size, self.order_num)
        MainWindow.setTabOrder(self.order_num, self.code)
        MainWindow.setTabOrder(self.code, self.count)
        MainWindow.setTabOrder(self.count, self.save_count)
        MainWindow.setTabOrder(self.save_count, self.clean_count)
        MainWindow.setTabOrder(self.clean_count, self.add)
        MainWindow.setTabOrder(self.add, self.takeout)
        MainWindow.setTabOrder(self.takeout, self.list)
        MainWindow.setTabOrder(self.list, self.update_record)
        MainWindow.setTabOrder(self.update_record, self.end_record)
        MainWindow.setTabOrder(self.end_record, self.delete_record)
        MainWindow.setTabOrder(self.delete_record, self.active)
        MainWindow.setTabOrder(self.active, self.completed)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Contador de Códigos"))
        self.code_label.setText(_translate("MainWindow", "Código"))
        self.size_label.setText(_translate("MainWindow", "Talla"))
        self.count_label.setText(_translate("MainWindow", "Cantidad"))
        self.save_count.setText(_translate("MainWindow", "Guardar Conteo"))
        self.client.setText(_translate("MainWindow", "Cliente"))
        self.piece.setText(_translate("MainWindow", "Pieza"))
        self.clean_count.setText(_translate("MainWindow", "Limpiar Conteo"))
        self.order_num_label.setText(_translate("MainWindow", "Número de Orden"))
        self.end_record.setText(_translate("MainWindow", "Finalizar"))
        self.delete_record.setText(_translate("MainWindow", "Eliminar"))
        self.update_record.setText(_translate("MainWindow", "Actualizar"))
        self.title.setText(_translate("MainWindow", "Contador"))
        self.add.setText(_translate("MainWindow", "Añadir"))
        self.takeout.setText(_translate("MainWindow", "Sacar"))
        self.active.setText(_translate("MainWindow", "Activos"))
        self.completed.setText(_translate("MainWindow", "Finalizados"))
