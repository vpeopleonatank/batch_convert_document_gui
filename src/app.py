from __future__ import annotations

import sys


def main() -> int:
    try:
        from PySide6 import QtWidgets
    except Exception as exc:  # pragma: no cover
        print("PySide6 is required to run the GUI.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1

    from src.ui.main_window import MainWindow

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
