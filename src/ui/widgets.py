from __future__ import annotations

from collections.abc import Callable

from PySide6 import QtGui, QtWidgets


class LogTextEdit(QtWidgets.QTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)

    def append_line(self, line: str) -> None:
        if not line.endswith("\n"):
            line += "\n"
        self.moveCursor(QtGui.QTextCursor.End)
        self.insertPlainText(line)
        self.moveCursor(QtGui.QTextCursor.End)


def make_browse_row(
    edit: QtWidgets.QLineEdit,
    on_browse: Callable[[], None],
    *,
    button_text: str = "Browse…",
) -> tuple[QtWidgets.QHBoxLayout, QtWidgets.QPushButton]:
    row = QtWidgets.QHBoxLayout()
    row.addWidget(edit, 1)
    button = QtWidgets.QPushButton(button_text)
    button.clicked.connect(on_browse)
    row.addWidget(button)
    return row, button

