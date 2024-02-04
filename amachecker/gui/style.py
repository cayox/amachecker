STYLE = """
/*
accent: #ef233c
off accent: #d90429
background: #edf2f4
gray: #8d99ae
foreground: #2b2d42
*/

* {
    background-color: #edf2f4;
    color: #2b2d42;
}

QLabel#Title {
    font-size: 32px;
    font-weight: 600;
    color: #ef233c;
}

QLineEdit {
    border: 1px solid #8d99ae;
    border-bottom: 1px solid #ef233c;
    border-radius: 8px;
    padding: 6px 8px;
}

QLineEdit:hover {
    border: 1px solid #ef233c;
}

QLineEdit:focus {
    border: 2px solid #ef233c;
    border-radius: 8px;
}

QPlainTextEdit {
    border: 1px solid #8d99ae;
    border-radius: 8px;
}

QPushButton {
    background-color: #ef233c;
    color: #edf2f4;
    border-radius: 8px;
    padding: 6px 8px;
}

QPushButton:hover {
    background-color: #d90429;
}

QPushButton:pressed {
    background-color: #2b2d42;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 22px;
    margin: 6px;
}

QScrollBar::handle:vertical {
    background: #ef233c;
    border-radius: 4px;
    min-height: 32px;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
    width: 0px;
    height: 0px;
}
"""
