from __future__ import annotations

import email
import subprocess
import tempfile
from pathlib import Path


def _is_mhtml(source_doc: Path) -> bool:
    try:
        with source_doc.open("rb") as f:
            header = f.read(512)
        # Case-insensitive check for MIME-Version header
        return header.lstrip().lower().startswith(b"mime-version:")
    except OSError:
        return False


def _extract_html_from_mhtml(mhtml_file: Path) -> str | None:
    """Extract HTML content from MHTML file. Returns None if extraction fails."""
    try:
        with mhtml_file.open("rb") as f:
            msg = email.message_from_binary_file(f)

        # Find the first text/html part
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                if not payload:
                    continue

                # Try charset specified in email header first
                email_charset = part.get_param("charset")
                if email_charset:
                    try:
                        return payload.decode(email_charset)
                    except (UnicodeDecodeError, LookupError):
                        pass

                # Fallback to common encodings
                # Order matters: utf-8 is more common than utf-16le
                encodings = ["utf-8", "utf-16le", "utf-16be", "iso-8859-1", "cp1252"]
                for encoding in encodings:
                    try:
                        return payload.decode(encoding)
                    except (UnicodeDecodeError, LookupError):
                        continue

                # Last resort: decode with errors='ignore'
                return payload.decode("utf-8", errors="ignore")
        return None
    except Exception:
        return None


def _convert_html_to_docx(soffice_path: Path, html_content: str, dest_file: Path) -> tuple[bool, str]:
    """Convert HTML content to DOCX using LibreOffice."""
    dest_file.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_html = Path(tmpdir) / "temp.html"
        temp_html.write_text(html_content, encoding="utf-8")

        cmd = [
            str(soffice_path),
            "--headless",
            "--nologo",
            "--nodefault",
            "--nolockcheck",
            "--norestore",
            "--convert-to",
            "docx:MS Word 2007 XML",
            "--outdir",
            str(dest_file.parent),
            str(temp_html),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        temp_output = dest_file.parent / "temp.docx"

        if result.returncode == 0 and temp_output.exists():
            temp_output.rename(dest_file)
            return True, ""

        log = (
            f"cmd: {' '.join(cmd)}\n"
            f"returncode: {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}\n"
        )
        return False, log


def convert_doc_to_docx(soffice_path: Path, source_doc: Path, dest_dir: Path) -> tuple[bool, str]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    expected_output = dest_dir / f"{source_doc.stem}.docx"

    # Handle MHTML files separately
    if _is_mhtml(source_doc):
        html_content = _extract_html_from_mhtml(source_doc)
        if html_content:
            return _convert_html_to_docx(soffice_path, html_content, expected_output)
        else:
            return False, "Failed to extract HTML from MHTML file"

    # Standard conversion for regular .doc files
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

