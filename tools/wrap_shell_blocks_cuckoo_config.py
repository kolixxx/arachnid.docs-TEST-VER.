"""
One-off formatter: wrap obvious shell/commands in AsciiDoc [source,shell] blocks.
Run from repo root: python tools/wrap_shell_blocks_cuckoo_config.py
"""

from pathlib import Path
import re

PATH = Path("content/modules/ROOT/pages/utm/cuckoo-sandbox/configuration.adoc")

SKIP_PREFIXES = ("image::", "xref:", "[#", "====", "<<", "include::")


def has_cyrillic(t: str) -> bool:
    return bool(re.search(r"[\u0400-\u04FF]", t))


def is_config_file_desc(s: str) -> bool:
    # Описательные строки «имя.conf: пояснение» — не shell
    if re.match(r"^[a-zA-Z_<>][\w.<>]*\.conf\s*:", s):
        return True
    if s.startswith("<machinery.conf>") or s.startswith("<machinery"):
        return True
    return bool(
        re.match(r"^(?:[a-zA-Z_<>]+\w*\.conf|<machinery\.conf>):\s*$", s)
    )


def is_shell_line(raw: str | None) -> bool:
    if raw is None:
        return False
    s = raw.strip()
    if not s:
        return False
    for p in SKIP_PREFIXES:
        if s.startswith(p):
            return False
    if s.startswith(("browser.", "security.")):
        return False
    if is_config_file_desc(s):
        return False

    if s == "SUCCESS":
        return True
    if s.startswith(("INFO:", "Starting guacd:", "<module ", "ERROR:")):
        return True
    if re.match(r"^\d+\.\d+\.\d+r\d+$", s):
        return True
    if s.startswith("#") and any(x in s for x in ("вы", "вывод")):
        return True

    pats = [
        r"^\$\s",
        r"^\([^)]*\)\s*\$\s",
        r"^\([^)]*\)\s+\S+@",
        r"^sudo\b",
        r"^apt(?:-get|-key)?\b",
        r"^wget\b",
        r"^curl\b",
        r"^echo\b",
        r"^cd\b",
        r"^mkdir\b",
        r"^tar\b",
        r"^python(\.exe)?\b",
        r"^virtualenv\b",
        r"^pip\b",
        r"^make\b",
        r"^\./configure\b",
        r"^VBoxManage\b",
        r"^vboxmanage\b",
        r"^ping\b",
        r"^systemctl\b",
        r"^ldconfig\b",
        r"^inetsim\b",
        r"^gcc\b",
        r"^chmod\b",
        r"^cuckoo\b",
        r"^\.\s+cuckoovenv",
        r"^hostname\b",
        r"^\.\s+~/",
    ]
    for pat in pats:
        if re.match(pat, s, re.I):
            return True
    if re.match(r"^mongo(?:db)?\b", s, re.I):
        return True
    if has_cyrillic(s):
        if re.match(r"^(\$\s|sudo\s|apt\s|wget\s|python|cd\s)", s, re.I):
            return True
        return False
    return False


def peek_next_nonempty(arr: list[str], idx: int) -> str | None:
    j = idx + 1
    while j < len(arr):
        if arr[j].strip():
            return arr[j]
        j += 1
    return None


def main() -> None:
    arr = PATH.read_text(encoding="utf-8").split("\n")
    buf: list[str] = []
    out: list[str] = []

    def flush() -> None:
        nonlocal buf
        if not buf:
            return
        while buf and not buf[-1].strip():
            buf.pop()
        if not buf:
            return
        out.append("[source,shell]")
        out.append("----")
        out.extend(buf)
        out.append("----")
        out.append("")
        buf = []

    i = 0
    while i < len(arr):
        line = arr[i]
        if not line.strip():
            nxt = peek_next_nonempty(arr, i)
            if nxt is not None and is_shell_line(nxt) and buf:
                buf.append("")
            elif buf and nxt is not None and not is_shell_line(nxt):
                flush()
            if not buf:
                out.append("")
            i += 1
            continue
        if is_shell_line(line):
            buf.append(line)
        else:
            flush()
            out.append(line)
        i += 1
    flush()

    result = "\n".join(out)
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")
    PATH.write_text(result.rstrip() + "\n", encoding="utf-8")
    print("Updated", PATH)


if __name__ == "__main__":
    main()
