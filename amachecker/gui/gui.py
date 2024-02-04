import datetime
import logging
import os
import re
import sys

import pandas as pd
from PyQt6 import QtCore, QtWidgets

from amachecker.export_reader import export_asins_from_csv
from amachecker.product_page_checker import check_pages

from amachecker.gui.thread import run_in_thread
from amachecker.gui.style import STYLE

log = logging.getLogger(__name__)

TITLE = "AmaChecker"

DESCRIPTION = """Hallo Mama,
Bitte lade bei "Amazon Export" deinen Amazon Export hoch.
Wenn du dann unten auf den Startknopf drückst, überprüft das Programm die entsprechenden
Amazon Seiten und gibt dir eine Rückmeldung nichts gefunden wurde.
"""

DEFAULT_REGEX = r"\d+,\d{2}€ / [A-Za-z]+"


def get_download_folder_path() -> str:
    """Returns the path of the Downloads folder for macOS or Windows.

    Returns:
        str: Path to the Downloads folder.
    """
    if sys.platform == "darwin":
        # macOS
        return os.path.join(os.path.expanduser("~"), "Downloads")
    if sys.platform in ["win32", "cygwin"]:
        # Windows - using USERPROFILE environment variable
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    raise NotImplementedError("This function supports only macOS and Windows.")


class FileInput(QtWidgets.QWidget):
    """QWidget to input a file, with a file selection dialog.

    Args:
        placeholder: the placeholder text
        default_path: the default path to open the file dialog in
    """

    def __init__(self, placeholder: str | None = None, default_path: str | None = None):
        super().__init__()
        self.default_path = default_path
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.file_path = QtWidgets.QLineEdit()
        self.file_path.setPlaceholderText(
            (
                placeholder
                if placeholder is not None
                else "Datei auswählen oder Pfad kopieren"
            ),
        )
        self.file_path.setMinimumWidth(400)
        lay.addWidget(self.file_path)

        self.select_button = QtWidgets.QPushButton("...")
        self.select_button.setMaximumWidth(64)
        self.select_button.clicked.connect(self.select_path)
        lay.addWidget(self.select_button)

    @QtCore.pyqtSlot()
    def select_path(self):
        filter_pattern = "Text Files (*.txt);;CSV Files (*.csv)"
        default_path = (
            self.default_path if self.default_path is not None else os.getcwd()
        )
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            default_path,
            filter_pattern,
        )
        if file_name:
            self.file_path.setText(file_name)

    @property
    def selected_file(self) -> str:
        return self.file_path.text()


class Gui(QtWidgets.QWidget):
    """The main AmaChecker GUI."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loaded_data: pd.DataFrame | None = None

        self._init_gui()

    def _init_gui(self):
        self.main_lay = QtWidgets.QVBoxLayout()
        self.main_lay.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft,
        )

        self.title = QtWidgets.QLabel(TITLE)
        self.title.setObjectName("Title")
        self.main_lay.addWidget(self.title)

        self.description = QtWidgets.QLabel(DESCRIPTION)
        self.description.setObjectName("Description")
        self.main_lay.addWidget(self.description)

        form_lay = QtWidgets.QFormLayout()

        self.regex_input = QtWidgets.QLineEdit()
        self.regex_input.setPlaceholderText("ReGex String to check ...")
        self.regex_input.setText(DEFAULT_REGEX)
        self.regex_input.setMinimumWidth(400)
        form_lay.addRow("Regular Expression: ", self.regex_input)

        self.file_entry = FileInput("Amazon Export", get_download_folder_path())
        form_lay.addRow("Amazon Export", self.file_entry)

        self.main_lay.addLayout(form_lay)

        self.log_box = QtWidgets.QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.main_lay.addWidget(self.log_box)

        self.start_button = QtWidgets.QPushButton("Start")
        self.start_button.clicked.connect(self.start)

        self.main_lay.addWidget(self.start_button)

        self.setLayout(self.main_lay)

    @QtCore.pyqtSlot()
    def start(self):
        self.setDisabled(True)
        self.start_threadded()

    @run_in_thread
    def start_threadded(self, log_func):
        export_file = self.file_entry.selected_file
        if not os.path.isfile(export_file):
            raise FileNotFoundError(f"Datei {export_file} existiert nicht!")

        regex_pattern = re.compile(self.regex_input.text())
        if not re.compile(regex_pattern):
            raise ValueError(f"{self.regex_input.text()} ist nicht gültig!")

        log_func(f"Suche alle ASINs in {os.path.basename(export_file)} ...")
        asins = export_asins_from_csv(export_file)

        log_func("Überprüfung der Amazon Seiten. Das kann eine Weile dauern ...")
        results = check_pages(asins, regex_pattern, log_func)

        df = pd.DataFrame(results)
        df = df.sort_values("result")
        df = df.reset_index(drop=True)

        wrong_sites = len(df[df["result"].eq(False)])
        total_sites = len(df)
        log_func(f"{wrong_sites}/{total_sites} fehlerhafte Seiten gefunden!")
        self.loaded_data = df

    @QtCore.pyqtSlot(Exception)
    def handle_error(self, exc: Exception):
        text = f"{exc.__class__.__name__}: {exc}"
        self.handle_message(text)
        QtWidgets.QMessageBox.critical(self, "AmaChecker - ERROR", text)
        self.setDisabled(False)

    @QtCore.pyqtSlot()
    def handle_done(self):
        csv_path = os.path.join(
            os.getcwd(),
            f"AmaChecker_{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.csv",
        )
        self.loaded_data.to_csv(csv_path)
        text = f"AmaChecker ist fertig! Die Ergebnisse findest du unter {csv_path}"
        self.handle_message(
            f"AmaChecker ist fertig! Die Ergebnisse findest du unter {csv_path}",
        )
        QtWidgets.QMessageBox.information(self, "AmaChecker - Erfolg", text)
        self.setDisabled(False)

    @QtCore.pyqtSlot(str)
    def handle_message(self, msg: str):
        time_str = f'<span style="color: gray;">[{datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}]</span>'
        self.log_box.appendHtml(f"{time_str}: {msg}")
