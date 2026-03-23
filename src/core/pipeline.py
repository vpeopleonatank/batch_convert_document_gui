from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from src.core.convert import convert_doc_to_docx
from src.core.copy import copy_docx
from src.core.paths import ensure_within_root, map_dest_path_for_source
from src.core.scan import scan_files
from src.core.work_items import WorkItem

LogCallback = Callable[[str], None]
ProgressCallback = Callable[[int, int], None]
CurrentFileCallback = Callable[[str], None]
CancelChecker = Callable[[], bool]


def build_work_items_from_scanned(
    scanned_files: list[Path],
    source_root: Path,
    dest_root: Path,
    *,
    copy_existing_docx: bool,
) -> list[WorkItem]:
    work_items: list[WorkItem] = []
    for source_file in scanned_files:
        suffix = source_file.suffix.lower()
        if suffix == ".doc":
            dest_file = map_dest_path_for_source(source_root, dest_root, source_file, ".docx")
            dest_file = ensure_within_root(dest_root, dest_file)
            work_items.append(WorkItem(kind="convert", source=source_file, dest_file=dest_file))
        elif suffix == ".docx" and copy_existing_docx:
            dest_file = map_dest_path_for_source(source_root, dest_root, source_file, ".docx")
            dest_file = ensure_within_root(dest_root, dest_file)
            work_items.append(WorkItem(kind="copy", source=source_file, dest_file=dest_file))
    return work_items


def build_work_items(source_root: Path, dest_root: Path, *, copy_existing_docx: bool) -> list[WorkItem]:
    scanned_files = scan_files(source_root)
    return build_work_items_from_scanned(scanned_files, source_root, dest_root, copy_existing_docx=copy_existing_docx)


@dataclass(frozen=True, slots=True)
class PipelineSummary:
    scanned_doc: int
    scanned_docx: int
    work_items: int
    converted: int
    copied: int
    failed: int
    cancelled: bool
    duration_seconds: float

    def to_text(self) -> str:
        cancelled = "yes" if self.cancelled else "no"
        return (
            "Summary\n"
            f"- scanned: .doc={self.scanned_doc}, .docx={self.scanned_docx}\n"
            f"- work items: {self.work_items}\n"
            f"- converted: {self.converted}\n"
            f"- copied: {self.copied}\n"
            f"- failed: {self.failed}\n"
            f"- cancelled: {cancelled}\n"
            f"- duration: {self.duration_seconds:.2f}s"
        )


def run_pipeline(
    source_root: Path,
    dest_root: Path,
    soffice_path: Path,
    *,
    copy_existing_docx: bool,
    on_log: LogCallback | None = None,
    on_progress: ProgressCallback | None = None,
    on_current_file: CurrentFileCallback | None = None,
    is_cancelled: CancelChecker | None = None,
) -> str:
    start = time.monotonic()
    dest_root.mkdir(parents=True, exist_ok=True)

    scanned_files = scan_files(source_root)
    scanned_doc = sum(1 for p in scanned_files if p.suffix.lower() == ".doc")
    scanned_docx = sum(1 for p in scanned_files if p.suffix.lower() == ".docx")

    work_items = build_work_items_from_scanned(
        scanned_files,
        source_root,
        dest_root,
        copy_existing_docx=copy_existing_docx,
    )
    total = len(work_items)

    def log(line: str) -> None:
        if on_log is not None:
            on_log(line)

    def progress(done: int) -> None:
        if on_progress is not None:
            on_progress(total, done)

    def current(text: str) -> None:
        if on_current_file is not None:
            on_current_file(text)

    converted = 0
    copied = 0
    failed = 0
    cancelled = False

    progress(0)
    for done, item in enumerate(work_items, start=1):
        if is_cancelled is not None and is_cancelled():
            cancelled = True
            log("Cancelled.")
            break

        current(str(item.source))
        try:
            if item.kind == "copy":
                copy_docx(item.source, item.dest_file)
                copied += 1
                log(f"COPIED: {item.source} -> {item.dest_file}")
            else:
                ok, convert_log = convert_doc_to_docx(soffice_path, item.source, item.dest_file.parent)
                if ok:
                    converted += 1
                    log(f"CONVERTED: {item.source} -> {item.dest_file}")
                else:
                    failed += 1
                    log(f"FAILED: {item.source} -> {item.dest_file}")
                    log(convert_log.rstrip())
        except Exception as exc:
            failed += 1
            log(f"ERROR: {item.source} ({exc})")

        progress(done)

    duration = time.monotonic() - start
    summary = PipelineSummary(
        scanned_doc=scanned_doc,
        scanned_docx=scanned_docx,
        work_items=total,
        converted=converted,
        copied=copied,
        failed=failed,
        cancelled=cancelled,
        duration_seconds=duration,
    )
    current("Done")
    return summary.to_text()
