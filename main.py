import sys

from PyQt6 import QtWidgets

from amachecker.gui import Gui


class MainWindow(QtWidgets.QMainWindow):
    """AmaChecker MainWindow."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AmaChecker")
        self.setGeometry(100, 100, 800, 600)
        with open("assets/styles/style.qss") as f:
            self.setStyleSheet(f.read())

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.gui = Gui()
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.gui)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
