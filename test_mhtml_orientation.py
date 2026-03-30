#!/usr/bin/env python3
"""Check what CSS/orientation info is in the MHTML file"""

import email
from pathlib import Path


def extract_html_from_mhtml(mhtml_file: Path) -> str:
    """Extract HTML content from MHTML file"""
    with mhtml_file.open("rb") as f:
        msg = email.message_from_binary_file(f)

    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)
            try:
                return payload.decode("utf-16le")
            except UnicodeDecodeError:
                return payload.decode("utf-8", errors="ignore")

    raise ValueError("No HTML content found in MHTML file")


mhtml_file = Path(r"D:\NĂM 2025\THÁNG 10\BAN TIN CUOI NGAY 22H NGAY 1.10.2025 01-10-2025.docx.doc")
html = extract_html_from_mhtml(mhtml_file)

# Look for style tags and page size info
print("=" * 60)
print("Checking for CSS and orientation info in MHTML")
print("=" * 60)

# Find <style> tags
import re

styles = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
if styles:
    print(f"\nFound {len(styles)} <style> block(s):\n")
    for i, style in enumerate(styles[:2], 1):  # Show first 2
        preview = style[:500]
        print(f"Style block {i} (first 500 chars):")
        print(preview)
        print()
else:
    print("\nNo <style> tags found")

# Look for @page directives
if "@page" in html.lower():
    print("\n[FOUND] @page directives in CSS")
    page_css = re.findall(r"@page[^{]*\{[^}]*\}", html, re.IGNORECASE)
    for css in page_css[:3]:
        print(f"  {css}")
else:
    print("\n[NOT FOUND] @page directives")

# Look for orientation keywords
keywords = ["landscape", "portrait", "size:", "page-size", "margin"]
found = []
for keyword in keywords:
    if keyword.lower() in html.lower():
        found.append(keyword)

if found:
    print(f"\n[FOUND] Orientation-related keywords: {', '.join(found)}")
else:
    print("\n[NOT FOUND] Any orientation-related keywords")

# Look for body style or margin info
body_style = re.search(r'<body[^>]*style="([^"]*)"', html, re.IGNORECASE)
if body_style:
    print(f"\n[FOUND] body style attribute:")
    print(f"  {body_style.group(1)[:200]}")
else:
    print("\n[NOT FOUND] body style attribute")

# Summary
print("\n" + "=" * 60)
print("Summary: LibreOffice may or may not preserve orientation")
print("when converting HTML to DOCX. The CSS in the HTML will be")
print("respected to some degree, but complex page settings might be lost.")
print("=" * 60)
