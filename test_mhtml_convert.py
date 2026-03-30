#!/usr/bin/env python3
"""Test script to extract HTML from MHTML and convert to DOCX"""

import base64
import email
import shutil
import subprocess
import tempfile
from pathlib import Path

def extract_html_from_mhtml(mhtml_file: Path) -> str:
    """Extract HTML content from MHTML file"""
    with mhtml_file.open("rb") as f:
        msg = email.message_from_binary_file(f)

    # Find the HTML part
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)
            # MHTML HTML is typically UTF-16LE encoded
            try:
                return payload.decode("utf-16le")
            except UnicodeDecodeError:
                return payload.decode("utf-8", errors="ignore")

    raise ValueError("No HTML content found in MHTML file")


def test_mhtml_conversion():
    mhtml_file = Path(r"D:\NĂM 2025\THÁNG 10\BAN TIN CUOI NGAY 22H NGAY 1.10.2025 01-10-2025.docx.doc")

    if not mhtml_file.exists():
        print(f"ERROR: File not found: {mhtml_file}")
        return

    print(f"Testing MHTML conversion for: {mhtml_file.name}")
    print(f"File size: {mhtml_file.stat().st_size} bytes\n")

    # Step 1: Extract HTML
    print("Step 1: Extracting HTML from MHTML...")
    try:
        html_content = extract_html_from_mhtml(mhtml_file)
        print(f"[OK] Extracted HTML ({len(html_content)} characters)\n")
    except Exception as e:
        print(f"[ERROR] Failed to extract: {e}\n")
        return

    # Step 2: Save to temp HTML file
    print("Step 2: Saving to temporary HTML file...")
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_html = Path(tmpdir) / "temp.html"
        temp_html.write_text(html_content, encoding="utf-8")
        print(f"[OK] Temp file: {temp_html}\n")

        # Step 3: Find LibreOffice
        print("Step 3: Finding LibreOffice...")
        soffice_candidates = [
            Path(r"D:\Project\batch_convert_document_gui\dist\batch-doc-to-docx-gui\LibreOffice\program\soffice.exe"),
            Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
            Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
        ]

        soffice = None
        for candidate in soffice_candidates:
            if candidate.exists():
                soffice = candidate
                print(f"[OK] Found: {soffice}\n")
                break

        if not soffice:
            print("[ERROR] LibreOffice not found\n")
            return

        # Step 4: Convert HTML to DOCX
        print("Step 4: Converting HTML to DOCX...")
        dest_dir = Path(tmpdir) / "output"
        dest_dir.mkdir()

        cmd = [
            str(soffice),
            "--headless",
            "--nologo",
            "--nodefault",
            "--nolockcheck",
            "--norestore",
            "--convert-to",
            "docx:MS Word 2007 XML",
            "--outdir",
            str(dest_dir),
            str(temp_html),
        ]

        print(f"Command: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, capture_output=True, text=True)

        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"stdout: {result.stdout}")
        if result.stderr:
            print(f"stderr: {result.stderr}")

        # Check output
        output_docx = dest_dir / "temp.docx"
        if output_docx.exists():
            print(f"\n[OK] Conversion successful!")
            print(f"  Output: {output_docx}")
            print(f"  Size: {output_docx.stat().st_size} bytes")

            # Copy to desktop for inspection
            dest_path = Path.home() / "Desktop" / "test_output.docx"
            shutil.copy2(output_docx, dest_path)
            print(f"  Copied to: {dest_path}")
        else:
            print(f"\n[ERROR] Conversion failed - no output file generated")


if __name__ == "__main__":
    test_mhtml_conversion()
