#!/usr/bin/env python3
"""One-off import: install-docs -> Antora cuckoo-sandbox KVM pages."""
import re
import shutil
from pathlib import Path

SRC_INSTALL = Path(r"c:\Users\nnirm\OneDrive\Desktop\install-docs\installation.adoc")
SRC_TROUBLE = Path(r"c:\Users\nnirm\OneDrive\Desktop\install-docs\troubleshooting.adoc")
SRC_IMAGES = Path(r"c:\Users\nnirm\OneDrive\Desktop\install-docs\images")
DST_PAGES = Path(r"c:\Users\nnirm\OneDrive\Desktop\antoraDocs\content\modules\ROOT\pages\utm\cuckoo-sandbox")
DST_IMAGES = Path(
    r"c:\Users\nnirm\OneDrive\Desktop\antoraDocs\content\modules\ROOT\images\utm\cuckoo-sandbox\kvm"
)

IMG_PREFIX = "utm/cuckoo-sandbox/kvm/"


def convert_line(line: str) -> str:
    if line.startswith(":imagesdir:"):
        return ""
    line = re.sub(
        r"link:troubleshooting\.adoc#([^[]+)\[([^\]]*)\]",
        r"xref:utm/cuckoo-sandbox/troubleshooting.adoc#\1[\2]",
        line,
    )
    line = re.sub(
        r"link:troubleshooting\.adoc\[([^\]]*)\]",
        r"xref:utm/cuckoo-sandbox/troubleshooting.adoc[\1]",
        line,
    )
    line = re.sub(
        r"link:installation\.adoc#([^[]+)\[([^\]]*)\]",
        r"xref:utm/cuckoo-sandbox/installationKVM.adoc#\1[\2]",
        line,
    )
    line = re.sub(
        r"link:installation\.adoc\[([^\]]*)\]",
        r"xref:utm/cuckoo-sandbox/installationKVM.adoc[\1]",
        line,
    )
    line = re.sub(
        r"этап (\d+) installation\.adoc",
        r"этап \1 xref:utm/cuckoo-sandbox/installationKVM.adoc[установки KVM]",
        line,
    )
    line = re.sub(
        r"этап (\d+) в installation\.adoc",
        r"этап \1 в xref:utm/cuckoo-sandbox/installationKVM.adoc[установке KVM]",
        line,
    )

    def _img(m):
        return f"image::{IMG_PREFIX}{m.group(1).lstrip('/')}["

    line = re.sub(r"image::([^[]+)\[", _img, line)
    return line.replace("[source,bash]", "[source,shell]")


def convert_body(text: str, skip_title: bool = False) -> str:
    out = []
    for line in text.splitlines():
        if skip_title and line.startswith("= "):
            continue
        if line.strip() == "Установка с нуля — link:installation.adoc[installation.adoc].":
            continue
        if line.strip() == "":
            out.append("")
            continue
        out.append(convert_line(line))
    return "\n".join(out)


def collect_images(text: str) -> set:
    return {m.group(1) for m in re.finditer(r"image::utm/cuckoo-sandbox/kvm/([^[]+)", text)}


def main():
    DST_IMAGES.mkdir(parents=True, exist_ok=True)

    inst_raw = SRC_INSTALL.read_text(encoding="utf-8")
    inst_body = convert_body(inst_raw)
    inst_body = re.sub(
        r"^= Cuckoo Sandbox 2\.0\.7 — установка \(Ubuntu 18\.04 \+ KVM\)",
        "= Установка Cuckoo Sandbox (KVM)",
        inst_body,
        count=1,
        flags=re.M,
    )
    inst_body = inst_body.replace(
        "Ошибки и отладка — xref:utm/cuckoo-sandbox/troubleshooting.adoc[Troubleshooting].",
        "Ошибки и отладка — xref:utm/cuckoo-sandbox/troubleshooting.adoc#kvm-troubleshooting[раздел устранения неисправностей KVM].",
    )
    if "kvm-troubleshooting" not in inst_body:
        inst_body = inst_body.replace(
            "Ошибки и отладка — link:troubleshooting.adoc[Troubleshooting].",
            "Ошибки и отладка — xref:utm/cuckoo-sandbox/troubleshooting.adoc#kvm-troubleshooting[раздел устранения неисправностей KVM].",
        )
    inst_body = inst_body.rstrip() + "\n\n'''\n\n"
    inst_body += (
        "Следующая страница: xref:utm/cuckoo-sandbox/perfomance.adoc"
        "[Анализ производительности и варианты оптимизации Cuckoo Sandbox].\n"
    )
    (DST_PAGES / "installationKVM.adoc").write_text(inst_body, encoding="utf-8")

    existing = (DST_PAGES / "troubleshooting.adoc").read_text(encoding="utf-8")
    if "[[kvm-troubleshooting]]" in existing:
        # Keep only the general (VBox) prefix before KVM section
        kvm_pos = existing.index("[[kvm-troubleshooting]]")
        existing = existing[:kvm_pos].rstrip() + "\n\n"
    else:
        existing = existing.rstrip() + "\n\n"
    trouble_body = convert_body(SRC_TROUBLE.read_text(encoding="utf-8"), skip_title=True)
    trouble_body = trouble_body.replace(
        "link:installation.adoc#win10-defender-off[installation.adoc: реестр + Safe Mode]",
        "xref:utm/cuckoo-sandbox/installationKVM.adoc#win10-defender-off[установка KVM: реестр + Safe Mode]",
    )
    trouble_body = trouble_body.replace(
        "link:installation.adoc#win10-firewall[этап 6 в installation.adoc]",
        "xref:utm/cuckoo-sandbox/installationKVM.adoc#win10-firewall[этап 6 в установке KVM]",
    )
    trouble_body = trouble_body.replace(
        "этап 9 в link:installation.adoc[installation.adoc]",
        "этап 9 в xref:utm/cuckoo-sandbox/installationKVM.adoc[установке KVM]",
    )
    trouble_body = trouble_body.replace(
        "В link:installation.adoc[installation.adoc] Firefox",
        "В xref:utm/cuckoo-sandbox/installationKVM.adoc[установке KVM] Firefox",
    )
    trouble_body = trouble_body.replace(
        "Полная настройка — link:installation.adoc[installation.adoc], раздел PostgreSQL / конфигурация.",
        "Полная настройка — xref:utm/cuckoo-sandbox/installationKVM.adoc[установка KVM], раздел PostgreSQL / конфигурация.",
    )
    trouble_body = trouble_body.replace(
        "link:installation.adoc#win10-defender-off[реестр + Safe Mode]",
        "xref:utm/cuckoo-sandbox/installationKVM.adoc#win10-defender-off[реестр + Safe Mode]",
    )

    kvm_section = """[[kvm-troubleshooting]]
== Устранение неисправностей при установке KVM (Ubuntu 18.04 + libvirt)

Материалы ниже относятся к пошаговой установке Cuckoo Sandbox 2.0.7 с гостевой ВМ в **KVM/libvirt** (не VirtualBox). Процедура установки — xref:utm/cuckoo-sandbox/installationKVM.adoc[Установка Cuckoo Sandbox (KVM)].

"""
    merged = existing + kvm_section + trouble_body.lstrip() + "\n"
    (DST_PAGES / "troubleshooting.adoc").write_text(merged, encoding="utf-8")

    needed = collect_images(inst_body) | collect_images(merged)
    missing = []
    for name in sorted(needed):
        src = SRC_IMAGES / name
        if src.exists():
            shutil.copy2(src, DST_IMAGES / name)
        else:
            missing.append(name)

    print(f"installationKVM: {len(inst_body.splitlines())} lines")
    print(f"images: {len(needed)} referenced, {len(missing)} missing")
    if missing:
        print("missing:", ", ".join(missing))


if __name__ == "__main__":
    main()
