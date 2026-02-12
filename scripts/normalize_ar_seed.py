#!/usr/bin/env python3
"""
Normalize Arabic text in seed CSVs.

Goals (minimal + boring):
- Remove Arabic diacritics (harakat).
- Fix a small, safe set of common hamza/alif spelling mistakes.
- Light phrase polishing for app-natural tone (very limited, opt-in by default).

This script preserves row order and uses LF line endings.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


HARAKAT_RE = re.compile(r"[\u064B-\u0652\u0670]")  # tanwin + short vowels + dagger alif


def _strip_harakat(s: str) -> Tuple[str, int]:
    before = s
    after = HARAKAT_RE.sub("", s)
    return after, len(before) - len(after)


def _collapse_spaces(s: str) -> str:
    # Keep it conservative: collapse repeated spaces, trim.
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def _replace_word(s: str, old: str, new: str) -> Tuple[str, int]:
    """
    Replace whole-word occurrences for Arabic-ish text without relying on \\b.
    """
    # Delimiters include whitespace and common Arabic/Latin punctuation.
    pat = re.compile(
        r"(^|[\s\"'«»\(\)\[\]\{}/\\])" + re.escape(old) + r"(?=($|[\s،,.:;!?؟\"'«»\)\]\}]))"
    )

    n = 0

    def repl(m: re.Match) -> str:
        nonlocal n
        n += 1
        return m.group(1) + new

    out = pat.sub(repl, s)
    return out, n


@dataclass
class ChangeStats:
    rows_changed: int = 0
    harakat_removed: int = 0
    replacements: Dict[str, int] = None
    phrase_edits: Dict[str, int] = None

    def __post_init__(self) -> None:
        self.replacements = {}
        self.phrase_edits = {}

    def bump(self, m: Dict[str, int], key: str, n: int) -> None:
        if n <= 0:
            return
        m[key] = m.get(key, 0) + n


def normalize_arabic(s: str, *, polish_phrases: bool) -> Tuple[str, ChangeStats]:
    st = ChangeStats()
    if not s:
        return s, st

    out = s

    out, removed = _strip_harakat(out)
    st.harakat_removed += removed

    # Safe-ish whole-word fixes.
    for old, new in [
        ("الى", "إلى"),
        ("تاثير", "تأثير"),
        ("تاثيرا", "تأثيرا"),
        ("تاثيرك", "تأثيرك"),
        ("تاثيره", "تأثيره"),
        ("تاثيرها", "تأثيرها"),
        ("تاثيرهم", "تأثيرهم"),
        ("اثر", "أثر"),
        ("اثرك", "أثرك"),
        ("اثره", "أثره"),
        ("اثرها", "أثرها"),
        ("اداء", "أداء"),
        ("ادائك", "أدائك"),
        ("اداؤك", "أداؤك"),
        ("مسؤوليه", "مسؤولية"),
    ]:
        out, n = _replace_word(out, old, new)
        st.bump(st.replacements, f"{old}->{new}", n)

    # A couple of common prefix forms (avoid trying to be a full spellchecker).
    # Example: "لاظهر" often intended "لأظهر".
    if "لاظهر" in out:
        out = out.replace("لاظهر", "لأظهر")
        st.bump(st.replacements, "لاظهر->لأظهر", 1)

    if polish_phrases:
        # Keep phrase polishing minimal and meaning-preserving.
        if "بحب" in out:
            out = out.replace("بحب", "بمحبة")
            st.bump(st.phrase_edits, "بحب->بمحبة", 1)

        if "أحضر بالكامل" in out:
            out = out.replace("أحضر بالكامل", "أحضر وأشارك بشكل كامل")
            st.bump(st.phrase_edits, "أحضر بالكامل->أحضر وأشارك بشكل كامل", 1)

    out = _collapse_spaces(out)
    return out, st


def process_csv(
    in_path: Path,
    out_path: Path,
    *,
    fields: List[str],
    polish_phrases: bool,
) -> ChangeStats:
    total = ChangeStats()

    # Some seed CSVs can be malformed (e.g., unquoted commas in an English field).
    # We read with csv.reader and repair "ragged" rows by merging extra columns into
    # the second-to-last field, keeping the last field intact (commonly *_ar).
    with in_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        hlen = len(header)
        rows: List[Dict[str, str]] = []
        for raw in reader:
            row = list(raw)
            if hlen and len(row) > hlen:
                # Merge extras into the penultimate column.
                pen = hlen - 2
                merged = ",".join(row[pen:-1])
                row = row[:pen] + [merged, row[-1]]
            if hlen and len(row) < hlen:
                row = row + [""] * (hlen - len(row))
            d = {header[i]: (row[i] if i < len(row) else "") for i in range(hlen)}
            rows.append(d)

    for row in rows:
        row_changed = False
        for field in fields:
            if field not in row:
                continue
            before = row[field] or ""
            after, st = normalize_arabic(before, polish_phrases=polish_phrases)
            if after != before:
                row[field] = after
                row_changed = True
            total.harakat_removed += st.harakat_removed
            for k, v in st.replacements.items():
                total.bump(total.replacements, k, v)
            for k, v in st.phrase_edits.items():
                total.bump(total.phrase_edits, k, v)
        if row_changed:
            total.rows_changed += 1

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", required=True)
    ap.add_argument("--out", dest="out_path", required=True)
    ap.add_argument("--fields", required=True, help="Comma-separated fields to normalize")
    ap.add_argument("--polish-phrases", action="store_true")
    args = ap.parse_args()

    st = process_csv(
        Path(args.in_path),
        Path(args.out_path),
        fields=[f.strip() for f in args.fields.split(",") if f.strip()],
        polish_phrases=args.polish_phrases,
    )

    # Report for humans (keep stable/brief).
    print(f"{args.in_path} -> {args.out_path}")
    print(f"rows_changed={st.rows_changed} harakat_removed={st.harakat_removed}")
    if st.replacements:
        top = sorted(st.replacements.items(), key=lambda kv: (-kv[1], kv[0]))[:20]
        print("replacements_top20=" + ", ".join([f"{k}({v})" for k, v in top]))
    if st.phrase_edits:
        top = sorted(st.phrase_edits.items(), key=lambda kv: (-kv[1], kv[0]))[:20]
        print("phrase_edits=" + ", ".join([f"{k}({v})" for k, v in top]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
