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
            print("La aplicación se está cerrando...")
            self.pre_close_event()
            event.accept()
        else:
            event.ignore()


class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(470, 550)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.counter_container = QtWidgets.QWidget(self.centralwidget)
        self.counter_container.setGeometry(QtCore.QRect(10, 90, 451, 161))
        self.counter_container.setObjectName("counter_container")
        self.code_container = QtWidgets.QWidget(self.counter_container)
        self.code_container.setGeometry(QtCore.QRect(90, 0, 271, 71))
        self.code_container.setObjectName("code_container")
        self.code_label = QtWidgets.QLabel(self.code_container)
        self.code_label.setGeometry(QtCore.QRect(10, 10, 58, 16))
        self.code_label.setObjectName("code_label")
        self.code = QtWidgets.QLineEdit(self.code_container)
        self.code.setGeometry(QtCore.QRect(10, 30, 251, 28))
        self.code.setObjectName("code")
        self.size_container = QtWidgets.QWidget(self.counter_container)
        self.size_container.setGeometry(QtCore.QRect(0, 0, 91, 71))
        self.size_container.setObjectName("size_container")
        self.size_label = QtWidgets.QLabel(self.size_container)
        self.size_label.setGeometry(QtCore.QRect(0, 10, 58, 16))
        self.size_label.setObjectName("size_label")
        self.size = QtWidgets.QLineEdit(self.size_container)
        self.size.setGeometry(QtCore.QRect(0, 30, 81, 28))
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
        self.end_count = QtWidgets.QPushButton(self.counter_container)
        self.end_count.setGeometry(QtCore.QRect(0, 120, 121, 31))
        self.end_count.setStyleSheet("")
        self.end_count.setDefault(False)
        self.end_count.setFlat(False)
        self.end_count.setObjectName("end_count")
        self.client = QtWidgets.QLabel(self.counter_container)
        self.client.setGeometry(QtCore.QRect(0, 80, 201, 16))
        self.client.setObjectName("client")
        self.piece = QtWidgets.QLabel(self.counter_container)
        self.piece.setGeometry(QtCore.QRect(220, 80, 211, 16))
        self.piece.setObjectName("piece")
        self.clean_count = QtWidgets.QPushButton(self.counter_container)
        self.clean_count.setGeometry(QtCore.QRect(130, 120, 121, 31))
        self.clean_count.setObjectName("clean_count")
        self.title_container = QtWidgets.QWidget(self.centralwidget)
        self.title_container.setGeometry(QtCore.QRect(10, 10, 451, 80))
        self.title_container.setObjectName("title_container")
        self.title = QtWidgets.QLabel(self.title_container)
        self.title.setGeometry(QtCore.QRect(140, 10, 161, 61))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.list_container = QtWidgets.QWidget(self.centralwidget)
        self.list_container.setGeometry(QtCore.QRect(10, 250, 451, 271))
        self.list_container.setObjectName("list_container")
        self.list = QtWidgets.QListWidget(self.list_container)
        self.list.setGeometry(QtCore.QRect(0, 0, 451, 271))
        self.list.setStyleSheet("")
        self.list.setObjectName("list")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Contador de Códigos"))
        self.code_label.setText(_translate("MainWindow", "Código"))
        self.size_label.setText(_translate("MainWindow", "Talla"))
        self.count_label.setText(_translate("MainWindow", "Cantidad"))
        self.end_count.setText(_translate("MainWindow", "Guardar Conteo"))
        self.client.setText(_translate("MainWindow", "Cliente"))
        self.piece.setText(_translate("MainWindow", "Pieza"))
        self.clean_count.setText(_translate("MainWindow", "Limpiar Conteo"))
        self.title.setText(_translate("MainWindow", "Contador"))
