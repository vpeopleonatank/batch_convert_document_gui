from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtWidgets

from src.core.libreoffice import resolve_soffice_path
from src.ui.worker import Worker
from src.ui.widgets import LogTextEdit, make_browse_row


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Batch DOC → DOCX Converter")

        self._thread: QtCore.QThread | None = None
        self._worker: Worker | None = None

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)

        self._source_edit = QtWidgets.QLineEdit()
        self._dest_edit = QtWidgets.QLineEdit()
        self._copy_docx_checkbox = QtWidgets.QCheckBox("Copy existing .docx")

        self._soffice_edit = QtWidgets.QLineEdit()
        self._soffice_status = QtWidgets.QLabel()
        self._soffice_status.setWordWrap(True)

        self._start_button = QtWidgets.QPushButton("Start")
        self._cancel_button = QtWidgets.QPushButton("Cancel")
        self._cancel_button.setEnabled(False)

        self._progress = QtWidgets.QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)

        self._current_file = QtWidgets.QLabel("Idle")
        self._current_file.setWordWrap(True)

        self._log = LogTextEdit()

        form = QtWidgets.QFormLayout()

        source_row, _source_browse = make_browse_row(self._source_edit, self._browse_source)
        form.addRow("Source folder", source_row)

        dest_row, _dest_browse = make_browse_row(self._dest_edit, self._browse_dest)
        form.addRow("Destination folder", dest_row)

        form.addRow("", self._copy_docx_checkbox)

        soffice_row, _soffice_browse = make_browse_row(self._soffice_edit, self._browse_soffice)
        form.addRow("LibreOffice (soffice)", soffice_row)
        form.addRow("", self._soffice_status)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(self._start_button)
        buttons.addWidget(self._cancel_button)

        layout = QtWidgets.QVBoxLayout(central)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self._progress)
        layout.addWidget(self._current_file)
        layout.addWidget(self._log, 1)

        self._start_button.clicked.connect(self._on_start_clicked)
        self._cancel_button.clicked.connect(self._on_cancel_clicked)

        self._source_edit.textChanged.connect(self._refresh_start_enabled)
        self._dest_edit.textChanged.connect(self._refresh_start_enabled)
        self._soffice_edit.textChanged.connect(self._refresh_start_enabled)

        detected = resolve_soffice_path(None)
        if detected is not None:
            self._soffice_edit.setText(str(detected))

        self._refresh_start_enabled()
        self.resize(900, 650)

    def _refresh_start_enabled(self) -> None:
        source_dir = Path(self._source_edit.text().strip()) if self._source_edit.text().strip() else None
        dest_dir = Path(self._dest_edit.text().strip()) if self._dest_edit.text().strip() else None
        soffice = resolve_soffice_path(self._soffice_edit.text().strip() or None)

        source_ok = source_dir is not None and source_dir.exists() and source_dir.is_dir()
        dest_ok = dest_dir is not None
        soffice_ok = soffice is not None

        if soffice_ok:
            self._soffice_status.setText("LibreOffice detected.")
        else:
            self._soffice_status.setText("LibreOffice not found. Browse to `soffice` to enable Start.")

        can_start = source_ok and dest_ok and soffice_ok and self._worker is None
        self._start_button.setEnabled(can_start)

    @QtCore.Slot()
    def _browse_source(self) -> None:
        start_dir = self._source_edit.text().strip() or str(Path.home())
        selected = QtWidgets.QFileDialog.getExistingDirectory(self, "Select source folder", start_dir)
        if selected:
            self._source_edit.setText(selected)

    @QtCore.Slot()
    def _browse_dest(self) -> None:
        start_dir = self._dest_edit.text().strip() or str(Path.home())
        selected = QtWidgets.QFileDialog.getExistingDirectory(self, "Select destination folder", start_dir)
        if selected:
            self._dest_edit.setText(selected)

    @QtCore.Slot()
    def _browse_soffice(self) -> None:
        start_dir = self._soffice_edit.text().strip() or str(Path.home())
        selected, _filter = QtWidgets.QFileDialog.getOpenFileName(self, "Select LibreOffice (soffice)", start_dir)
        if selected:
            self._soffice_edit.setText(selected)

    @QtCore.Slot()
    def _on_start_clicked(self) -> None:
        if self._worker is not None:
            return

        source_dir = Path(self._source_edit.text().strip())
        dest_dir = Path(self._dest_edit.text().strip())
        soffice = resolve_soffice_path(self._soffice_edit.text().strip() or None)
        if soffice is None:
            QtWidgets.QMessageBox.warning(self, "LibreOffice not found", "Please select a valid `soffice` executable.")
            self._refresh_start_enabled()
            return

        self._log.clear()
        self._log.append_line("Starting…")

        self._progress.setRange(0, 0)
        self._progress.setValue(0)
        self._current_file.setText("Scanning…")

        thread = QtCore.QThread(self)
        worker = Worker(
            source_dir=source_dir,
            dest_dir=dest_dir,
            soffice_path=soffice,
            copy_existing_docx=self._copy_docx_checkbox.isChecked(),
        )
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self._on_progress)
        worker.current_file.connect(self._current_file.setText)
        worker.log.connect(self._log.append_line)
        worker.finished.connect(self._on_finished)
        worker.failed.connect(self._on_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        self._thread = thread
        self._worker = worker

        self._start_button.setEnabled(False)
        self._cancel_button.setEnabled(True)
        thread.start()

    @QtCore.Slot()
    def _on_cancel_clicked(self) -> None:
        if self._worker is None:
            return
        self._log.append_line("Cancel requested…")
        self._cancel_button.setEnabled(False)
        self._worker.request_cancel()

    @QtCore.Slot(int, int)
    def _on_progress(self, total: int, done: int) -> None:
        self._progress.setRange(0, max(total, 1))
        self._progress.setValue(done)

    @QtCore.Slot(str)
    def _on_finished(self, summary: str) -> None:
        self._log.append_line(summary)
        QtWidgets.QMessageBox.information(self, "Done", summary)
        self._cleanup_worker()

    @QtCore.Slot(str)
    def _on_failed(self, error: str) -> None:
        self._log.append_line(error)
        QtWidgets.QMessageBox.critical(self, "Error", error)
        self._cleanup_worker()

    def _cleanup_worker(self) -> None:
        self._thread = None
        self._worker = None
        self._cancel_button.setEnabled(False)
        self._refresh_start_enabled()
