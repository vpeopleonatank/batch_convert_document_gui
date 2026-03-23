from __future__ import annotations

import traceback
from pathlib import Path

from PySide6 import QtCore

from src.core.pipeline import run_pipeline


class Worker(QtCore.QObject):
    progress = QtCore.Signal(int, int)
    current_file = QtCore.Signal(str)
    log = QtCore.Signal(str)
    finished = QtCore.Signal(str)
    failed = QtCore.Signal(str)

    def __init__(
        self,
        *,
        source_dir: Path,
        dest_dir: Path,
        soffice_path: Path,
        copy_existing_docx: bool,
    ) -> None:
        super().__init__()
        self._source_dir = source_dir
        self._dest_dir = dest_dir
        self._soffice_path = soffice_path
        self._copy_existing_docx = copy_existing_docx
        self._cancel_requested = False

    def request_cancel(self) -> None:
        self._cancel_requested = True

    @QtCore.Slot()
    def run(self) -> None:
        try:
            summary = run_pipeline(
                self._source_dir,
                self._dest_dir,
                self._soffice_path,
                copy_existing_docx=self._copy_existing_docx,
                on_log=self.log.emit,
                on_progress=self.progress.emit,
                on_current_file=self.current_file.emit,
                is_cancelled=lambda: self._cancel_requested,
            )
            self.finished.emit(summary)
        except Exception:  # pragma: no cover
            self.failed.emit(traceback.format_exc())

