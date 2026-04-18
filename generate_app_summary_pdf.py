from pathlib import Path


PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT = 48
TOP = 744
LINE = 13


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class PDFBuilder:
    def __init__(self) -> None:
        self.lines = []
        self.y = TOP

    def add(self, text: str, size: int = 11, bold: bool = False, indent: int = 0) -> None:
        font = "/F2" if bold else "/F1"
        x = LEFT + indent
        safe = escape_pdf_text(text)
        self.lines.append(f"BT {font} {size} Tf 1 0 0 1 {x} {self.y} Tm ({safe}) Tj ET")
        self.y -= LINE if size <= 11 else LINE + 2

    def spacer(self, amount: int = 5) -> None:
        self.y -= amount

    def build(self) -> bytes:
        content = "\n".join(self.lines) + "\n"
        objects = [
            "<< /Type /Catalog /Pages 2 0 R >>",
            "<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>",
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
            f"<< /Length {len(content.encode('latin-1'))} >>\nstream\n{content}endstream",
        ]

        parts = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(sum(len(part) for part in parts))
            parts.append(f"{index} 0 obj\n{obj}\nendobj\n".encode("latin-1"))

        xref_offset = sum(len(part) for part in parts)
        xref = [f"xref\n0 {len(objects) + 1}\n", "0000000000 65535 f \n"]
        for offset in offsets[1:]:
            xref.append(f"{offset:010d} 00000 n \n")
        trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
        parts.append("".join(xref).encode("latin-1"))
        parts.append(trailer.encode("latin-1"))
        return b"".join(parts)


def main() -> None:
    output = Path("output/pdf/repo_app_summary.pdf")
    output.parent.mkdir(parents=True, exist_ok=True)

    pdf = PDFBuilder()
    pdf.add("Repository App Summary", size=20, bold=True)
    pdf.add("Generated from repo evidence on 2026-03-24. Current repo contains only .git metadata.", size=10)
    pdf.spacer(6)

    pdf.add("WHAT IT IS", size=12, bold=True)
    pdf.add("This repository does not currently contain application source code, docs, config, or commit history.")
    pdf.add("Based on the checked-out contents, it is an empty Git repository rather than a runnable app.")
    pdf.spacer()

    pdf.add("WHO IT IS FOR", size=12, bold=True)
    pdf.add("Primary user/persona: Not found in repo.")
    pdf.spacer()

    pdf.add("WHAT IT DOES", size=12, bold=True)
    for line in [
        "- Tracks version control metadata via Git.",
        "- Has a repository initialized on branch main.",
        "- Contains Git hook samples under .git/hooks.",
        "- Shows no commits in history.",
        "- Shows no configured remote origin.",
        "- Shows no application files or assets.",
    ]:
        pdf.add(line)
    pdf.spacer()

    pdf.add("HOW IT WORKS", size=12, bold=True)
    for line in [
        "Architecture overview based only on repo evidence:",
        "Components/services: Git repository metadata only.",
        "Data flow: Not found in repo.",
        "App services: Not found in repo.",
        "Storage/schema: Not found in repo.",
        "Runtime/infrastructure: Not found in repo.",
    ]:
        pdf.add(line)
    pdf.spacer()

    pdf.add("HOW TO RUN", size=12, bold=True)
    for line in [
        "1. Running steps for the app: Not found in repo.",
        "2. There is no entry point, dependency manifest, or README to follow.",
        "3. To make this runnable, add app source files and setup docs to the repository.",
    ]:
        pdf.add(line)
    pdf.spacer()

    pdf.add("REPO EVIDENCE USED", size=12, bold=True)
    for line in [
        "- Root directory lists only .git/.",
        "- git status: No commits yet on main.",
        "- git log: no history available.",
        "- git config --get remote.origin.url: no remote found.",
    ]:
        pdf.add(line)

    output.write_bytes(pdf.build())
    print(output.resolve())


if __name__ == "__main__":
    main()
