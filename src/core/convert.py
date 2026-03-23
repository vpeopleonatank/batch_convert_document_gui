from __future__ import annotations

import subprocess
from pathlib import Path


def convert_doc_to_docx(soffice_path: Path, source_doc: Path, dest_dir: Path) -> tuple[bool, str]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    expected_output = dest_dir / f"{source_doc.stem}.docx"

    cmd = [
        str(soffice_path),
        "--headless",
        "--nologo",
        "--nodefault",
        "--nolockcheck",
        "--norestore",
        "--convert-to",
        "docx",
        "--outdir",
        str(dest_dir),
        str(source_doc),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    log = (
        f"cmd: {' '.join(cmd)}\n"
        f"returncode: {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}\n"
    )
    success = result.returncode == 0 and expected_output.exists()
    return success, log

