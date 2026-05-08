"""
Rebuild pages/utm/cuckoo-sandbox/configuration.adoc from DOCX-derived paragraphs.

Skips paragraphs that belong on overview/architecture pages in this site's split.

Run from repo root: python tools/regen_cuckoo_configuration_adoc.py
"""

from pathlib import Path
import zipfile
import re
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "incoming/cuckoo-sandbox-antcolony.docx"
OUT = ROOT / "content/modules/ROOT/pages/utm/cuckoo-sandbox/configuration.adoc"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def paragraphs_from_docx(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    out: list[str] = []
    for node in root.iter(W + "p"):
        texts: list[str] = []
        for t in node.iter(W + "t"):
            if t.text:
                texts.append(t.text)
            if t.tail:
                texts.append(t.tail)
        line = "".join(texts).strip()
        if line:
            out.append(line)
    return out


def postprocess_txt(s: str) -> str:
    # Split merged headings from DOCX glue (machinery/ip/connection bullets)
    s = re.sub(
        r"(machinery в cuckoo:)(Этот)",
        r"\1\n\n\2",
        s,
    )
    s = re.sub(r"(ip и port в resultserver:)(Эти)", r"\1\n\n\2", s)
    s = re.sub(
        r"(connection в database:)(Строка)",
        r"\1\n\n\2",
        s,
    )
    # Separate Windows software list blobs (minimal fix)
    s = re.sub(r"10-x64:Adobe", "10-x64:\n\nAdobe", s)
    s = re.sub(r"disabled.Firefox", "disabled.\n\nFirefox", s)
    s = re.sub(
        r"(\.msi \(https:[^\)]+\))VC\+\+",
        r"\1\n\nVC++",
        s,
    )
    return s


def insert_images(parts: list[str]) -> None:
    """Mutate paragraphs list: append image directives after matched paragraphs."""

    def after_text(needle: str, image_line: str) -> None:
        for i, p in enumerate(parts):
            if needle in p and (
                image_line not in parts[i : min(i + 5, len(parts))]
            ):
                parts.insert(i + 1, image_line)
                return

    after_text(
        "curl http://127.0.0.1",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-01.png[Снимок экрана 1]",
    )
    after_text(
        "DHCP Server Enable",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-02.png[Снимок экрана 2]\n\n"
        + "image::utm/cuckoo-sandbox/cuckoo-screenshot-03.png[Снимок экрана 3]",
    )
    after_text(
        "папку там.",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-04.png[Снимок экрана 4]",
    )
    after_text(
        "ipconfig в cmd.",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-05.png[Снимок экрана 5]",
    )
    after_text(
        "ping 192.168.56.1",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-06.png[Снимок экрана 6]",
    )
    after_text(
        "ping 192.168.56.101",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-07.png[Снимок экрана 7]",
    )
    after_text(
        "фоновый процесс.",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-08.png[Снимок экрана 8]",
    )
    after_text(
        "cuckoo community",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-09.png[Снимок экрана 9]",
    )
    after_text(
        "INFO: Waiting for analysis tasks.",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-10.png[Снимок экрана 10]",
    )
    after_text(
        "http://localhost:8080.",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-11.png[Снимок экрана 11]",
    )
    after_text(
        "нажмите Open.",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-12.png[Снимок экрана 12]",
    )
    after_text(
        'выберите ff (так называется пакет firefox в Cuckoo Sandbox).',
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-13.png[Снимок экрана 13]",
    )
    after_text(
        "настраивали Volatility.",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-14.png[Снимок экрана 14]",
    )
    after_text(
        "ошибка веб-интерфейса.",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-15.png[Снимок экрана 15]\n\n"
        + "image::utm/cuckoo-sandbox/cuckoo-screenshot-16.png[Снимок экрана 16]\n\n"
        + "image::utm/cuckoo-sandbox/cuckoo-screenshot-17.png[Снимок экрана 17]",
    )
    after_text(
        "Откройте отчет eicar.zip.",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-18.png[Снимок экрана 18]",
    )
    after_text(
        "в меню слева.",
        "image::utm/cuckoo-sandbox/cuckoo-screenshot-19.png[Снимок экрана 19]",
    )


def add_guest_anchor(parts: list[str]) -> None:
    for i, p in enumerate(parts):
        if p.startswith("Виртуальные сети.") and (
            i == 0 or not parts[i - 1].startswith("[#guest-network]")
        ):
            parts.insert(i, "[#guest-network]")
            return


def main() -> None:
    paras = paragraphs_from_docx(DOCX)
    chunk1 = paras[5:79]
    chunk2 = paras[126:248]

    merged = [postprocess_txt(p) for p in chunk1 + chunk2]

    footer = (
        "\nСледующая страница: xref:utm/cuckoo-sandbox/"
        'perfomance.adoc[Анализ производительности и '
        "варианты оптимизации Cuckoo Sandbox]."
    )

    expanded: list[str] = []
    for block in merged:
        for piece in block.split("\n\n"):
            piece = piece.strip()
            if piece:
                expanded.append(piece)

    insert_images(expanded)
    add_guest_anchor(expanded)

    body = "\n\n".join(expanded)

    asc = "= Варианты конфигурации и сценарии настройки Cuckoo Sandbox\n\n" + body.strip() + footer + "\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(asc, encoding="utf-8")
    print("Wrote", OUT, "(paragraphs:", len(expanded), ")")


if __name__ == "__main__":
    main()
