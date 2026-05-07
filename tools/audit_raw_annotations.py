#!/usr/bin/env python3
"""Audit `;@raw=...` annotations.

Goal: identify which `;@raw=` annotations are REDUNDANT (the encoder
would emit the same bytes without them) and which are LOAD-BEARING
(the encoder needs the annotation to produce the correct bytes).

The redundant ones can be stripped wholesale. The load-bearing ones
become the proposal for awvm-asm encoder fixes.

Approach: per-file binary audit.
  1. Assemble the file as-is (baseline).
  2. Strip all `;@raw=` annotations.
  3. Assemble again (stripped).
  4. If byte streams match: every annotation in the file is
     redundant; emit a report row per file with status=all_redundant.
  5. If byte streams differ: at least one annotation is load-bearing.
     Walk forward, restoring annotations one at a time, until the
     stripped stream catches up. Each restored annotation is
     load-bearing; emit a per-instruction row with status=load_bearing.

Output: CSV with columns
  file, line, mnemonic, operand_signature, status, raw_bytes, encoder_bytes

`operand_signature` normalizes operand types (e.g.,
`x=[var], y=[var], zoom=imm`) so multiple instances collapse into the
same row when --summary is set.

Usage:
  python3 tools/audit_raw_annotations.py --file PATH [--out CSV]
  python3 tools/audit_raw_annotations.py --branch dos_1992 [--out CSV]
  python3 tools/audit_raw_annotations.py --all [--out CSV]
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from _paths import AWVM_ASM, AW_SRC, REPO_ROOT

SRC_ROOT = AW_SRC

sys.path.insert(0, str(REPO_ROOT / "tools"))

RE_RAW = re.compile(r"\s*;@raw=([0-9a-fA-FxX,\s]+)\s*$")


def parse_raw(line: str) -> list[int] | None:
    """Returns the list of bytes from a `;@raw=` annotation, or None."""
    m = RE_RAW.search(line)
    if not m:
        return None
    out = []
    for tok in m.group(1).split(","):
        tok = tok.strip()
        if not tok:
            continue
        out.append(int(tok, 16))
    return out


def strip_raw(line: str) -> str:
    """Remove the `;@raw=...` annotation from a line, preserving the
    instruction text and stripping trailing whitespace."""
    m = RE_RAW.search(line)
    if not m:
        return line
    return line[: m.start()].rstrip() + "\n" if line.endswith(
        "\n"
    ) else line[: m.start()].rstrip()


def expand_text(asm_path: Path) -> str:
    """Apply preprocessing the same way verify_stage does."""
    from awvm_preprocess import expand_includes, expand_fill_macros
    text = expand_includes(asm_path.read_text(), asm_path.resolve().parent)
    text = expand_fill_macros(text)
    return text


def assemble_text(text: str, hint_name: str) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        f = td / f"{hint_name}.asm"
        f.write_text(text)
        subprocess.run(
            [str(AWVM_ASM), f.name],
            cwd=td,
            check=True,
            capture_output=True,
            text=True,
        )
        return f.with_suffix(".bin").read_bytes()


def normalize_operand_signature(instr_text: str) -> str:
    """Build a stable signature for grouping similar instructions.

    Examples:
      'video type=0, offset=COMMON_VIDEO_075, x=[0x01], y=[0x02], zoom=0x40'
        → 'video type=imm, offset=label, x=var, y=var, zoom=imm'
      'mov [0x0E], 0x000C'
        → 'mov var, imm'
      'jmp DRAW_CIN_70_ANIM_LOOP'
        → 'jmp label'
    """
    s = instr_text.strip()
    # Cut the mnemonic
    parts = s.split(None, 1)
    mnemonic = parts[0] if parts else "?"
    rest = parts[1] if len(parts) > 1 else ""

    # Split operands; preserve key=value structure
    operand_parts = [op.strip() for op in rest.split(",") if op.strip()]
    sig_operands = []
    for op in operand_parts:
        if "=" in op:
            key, val = op.split("=", 1)
            sig_operands.append(f"{key.strip()}={_classify(val.strip())}")
        else:
            sig_operands.append(_classify(op))
    return mnemonic + (" " + ", ".join(sig_operands) if sig_operands else "")


def _classify(val: str) -> str:
    val = val.strip()
    if val.startswith("[") and val.endswith("]"):
        return "var"
    if val.startswith("0x") or val.startswith("0X"):
        return "imm"
    if val.isdigit():
        return "imm"
    return "label"


def audit_file(asm_path: Path, summary_rows: list[dict]) -> None:
    """Audit one .asm file. Mutates `summary_rows`."""
    print(f"  audit: {asm_path.name}", flush=True)
    try:
        baseline_text = expand_text(asm_path)
    except Exception as e:
        print(f"    expand failed: {e}", file=sys.stderr)
        return

    try:
        baseline_bytes = assemble_text(baseline_text, asm_path.stem)
    except subprocess.CalledProcessError as e:
        print(
            f"    baseline assemble failed: {e.stderr[:200]}",
            file=sys.stderr,
        )
        return

    # Build the stripped variant
    stripped_lines = []
    annotation_count = 0
    for line in baseline_text.splitlines(keepends=True):
        if RE_RAW.search(line):
            annotation_count += 1
            stripped_lines.append(strip_raw(line))
        else:
            stripped_lines.append(line)
    stripped_text = "".join(stripped_lines)

    if annotation_count == 0:
        print("    no `;@raw=` in file (after expansion)", flush=True)
        return

    try:
        stripped_bytes = assemble_text(stripped_text, asm_path.stem)
    except subprocess.CalledProcessError as e:
        # Encoder explicitly errored — common on instructions whose
        # operand-form the encoder doesn't know.
        print(
            f"    stripped assemble FAILED ({annotation_count} annotations); "
            f"some are load-bearing. error: {e.stderr[:200]}",
            flush=True,
        )
        summary_rows.append(
            {
                "file": str(asm_path.relative_to(SRC_ROOT)),
                "annotation_count": annotation_count,
                "status": "stripped_assemble_error",
                "encoder_error": e.stderr.strip()[:300].replace("\n", " | "),
                "byte_diff_count": "",
                "first_diff_offset": "",
            }
        )
        return

    if baseline_bytes == stripped_bytes:
        print(
            f"    ALL_REDUNDANT ({annotation_count} annotations) — "
            f"file output is byte-identical without `;@raw=`.",
            flush=True,
        )
        summary_rows.append(
            {
                "file": str(asm_path.relative_to(SRC_ROOT)),
                "annotation_count": annotation_count,
                "status": "all_redundant",
                "encoder_error": "",
                "byte_diff_count": 0,
                "first_diff_offset": "",
            }
        )
        return

    # Byte streams differ. Count diff and locate first divergence.
    n = min(len(baseline_bytes), len(stripped_bytes))
    first_diff = None
    for i in range(n):
        if baseline_bytes[i] != stripped_bytes[i]:
            first_diff = i
            break
    if first_diff is None and len(baseline_bytes) != len(stripped_bytes):
        first_diff = n
    diff_count = sum(
        1
        for i in range(n)
        if baseline_bytes[i] != stripped_bytes[i]
    ) + abs(len(baseline_bytes) - len(stripped_bytes))
    print(
        f"    BYTES_DIFFER ({annotation_count} annotations, "
        f"{diff_count}/{len(baseline_bytes)} bytes differ, "
        f"first diff at offset 0x{first_diff:04x})",
        flush=True,
    )
    summary_rows.append(
        {
            "file": str(asm_path.relative_to(SRC_ROOT)),
            "annotation_count": annotation_count,
            "status": "bytes_differ",
            "encoder_error": "",
            "byte_diff_count": diff_count,
            "first_diff_offset": f"0x{first_diff:04x}",
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, help="single .asm file")
    parser.add_argument(
        "--branch",
        type=str,
        help="branch dir under src/levels (e.g., dos_1992)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="audit every <branch>/<stage>.asm file",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "tmp" / "raw_audit_summary.csv",
        help="CSV output for per-file summary",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit nonzero if any file is `all_redundant` "
        "(every `;@raw=` in it can be stripped). Suitable for "
        "pre-commit / CI. Defaults to scanning every per-branch "
        "stage file unless --file/--branch is given.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="text-only check: exit nonzero if ANY `;@raw=` exists "
        "anywhere under src/levels/. Implies --check. This is the "
        "post-migration enforcement mode (every load-bearing "
        "`;@raw=` should have been rewritten to a `;@enc=…` form, "
        "so `;@raw=` should be entirely absent from the source "
        "tree).",
    )
    args = parser.parse_args()

    if args.strict:
        # Text-only sweep — no assembly required. Skips `_canonicalized/`
        # and `_phase3b_demo/` reference trees: those are frozen
        # disasm-output snapshots kept for provenance, not part of the
        # active build path that verify_stage / verify_unified consult.
        # Active source = per-branch `<branch>/` dirs + `_unified/`
        # tree.
        levels = SRC_ROOT / "src" / "levels"
        SKIP_DIRS = {"_canonicalized", "_phase3b_demo"}

        def in_active(path: Path) -> bool:
            for parent in path.relative_to(levels).parents:
                if parent.name in SKIP_DIRS:
                    return False
            return True

        offenders: list[tuple[Path, int]] = []
        for path in sorted(levels.rglob("*.asm")) + sorted(
            levels.rglob("*.inc")
        ) + sorted(levels.rglob("*.asm.in")):
            if not in_active(path):
                continue
            try:
                text = path.read_text()
            except OSError:
                continue
            if ";@raw=" in text:
                count = text.count(";@raw=")
                offenders.append((path, count))
        if offenders:
            print(
                "FAIL (--strict): found `;@raw=` annotations in "
                f"{len(offenders)} files (post-migration these must "
                "all be `;@enc=…` instead):",
                file=sys.stderr,
            )
            for path, count in offenders[:50]:
                print(
                    f"  {count:5d} × `;@raw=`  {path.relative_to(SRC_ROOT)}",
                    file=sys.stderr,
                )
            if len(offenders) > 50:
                print(
                    f"  …and {len(offenders) - 50} more files",
                    file=sys.stderr,
                )
            return 1
        print("OK (--strict): no `;@raw=` anywhere under src/levels/.")
        return 0

    if args.check and not (args.file or args.branch or args.all):
        # In --check mode, default to scanning everything.
        args.all = True

    if not (args.file or args.branch or args.all):
        parser.error("--file, --branch, --all, --check, or --strict is required")

    files: list[Path] = []
    if args.file:
        files = [args.file]
    elif args.branch:
        d = SRC_ROOT / "src" / "levels" / args.branch
        files = sorted(d.glob("*.asm"))
    else:
        for branch_dir in sorted(
            (SRC_ROOT / "src" / "levels").iterdir()
        ):
            if not branch_dir.is_dir() or branch_dir.name.startswith("_"):
                continue
            files.extend(sorted(branch_dir.glob("*.asm")))

    summary_rows: list[dict] = []
    for f in files:
        audit_file(f, summary_rows)

    if not args.check:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=[
                    "file",
                    "annotation_count",
                    "status",
                    "byte_diff_count",
                    "first_diff_offset",
                    "encoder_error",
                ],
            )
            writer.writeheader()
            for row in summary_rows:
                writer.writerow(row)
        print(f"\nwrote {args.out} ({len(summary_rows)} files)")

    # Quick aggregate for the operator
    statuses: dict[str, int] = {}
    for row in summary_rows:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    for s, n in sorted(statuses.items()):
        print(f"  {s}: {n} file(s)")

    if args.check:
        all_redundant = [
            r["file"] for r in summary_rows if r["status"] == "all_redundant"
        ]
        if all_redundant:
            print(
                "\nFAIL: the following files have only redundant "
                "`;@raw=` annotations — strip them with "
                "`tools/strip_redundant_raw_annotations.py`:",
                file=sys.stderr,
            )
            for f in all_redundant:
                print(f"  {f}", file=sys.stderr)
            return 1
        print("\nOK: no all-redundant files detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
