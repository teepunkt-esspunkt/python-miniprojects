#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# since i use comfyUI and automatic1111 and the model files are very big but can be used by both i created this to check if all files are linked correctly in both places
import os
import sys
from pathlib import Path
import argparse
from typing import List, Tuple

DEFAULT_EXTS = [".safetensors", ".ckpt", ".pt", ".bin", ".onnx", ".gguf"]

def read_dest_dirs(config_path: Path) -> List[Path]:
    if not config_path.exists():
        print(f"[ERROR] Config file not found: {config_path}")
        sys.exit(2)
    dests = []
    for raw in config_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Expand ~ and %ENV%
        expanded = os.path.expanduser(os.path.expandvars(line))
        p = Path(expanded).resolve()
        dests.append(p)
    return dests

def list_models(folder: Path, exts: List[str]) -> List[Path]:
    exts_lower = {e.lower() for e in exts}
    return [p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in exts_lower]

def classify_target(source: Path, target: Path) -> Tuple[str, str]:
    """
    Returns (status, detail)
    status ∈ {"OK", "MISSING", "WRONG_TARGET", "NOT_A_LINK_BUT_SAMEFILE", "EXISTS_BUT_DIFFERENT_FILE"}
    """
    if not target.exists():
        return ("MISSING", "no file at target")

    # Try to see if it is literally the same file (hardlink or same inode)
    try:
        if os.path.samefile(source, target):
            if target.is_symlink():
                return ("OK", "symlink, samefile")
            else:
                # could be a hardlink or just the same path
                return ("NOT_A_LINK_BUT_SAMEFILE", "exists; not a symlink (likely hardlink/same file)")
    except FileNotFoundError:
        pass  # fall through

    # If it's a symlink, check where it points
    if target.is_symlink():
        try:
            link_target = Path(os.readlink(target)).resolve()
        except OSError as e:
            return ("WRONG_TARGET", f"symlink unreadable: {e}")
        if link_target == source.resolve():
            return ("OK", "symlink points to source (resolved)")
        else:
            return ("WRONG_TARGET", f"symlink points elsewhere -> {link_target}")
    else:
        # Exists but is a regular file (copy?) that is not samefile
        return ("EXISTS_BUT_DIFFERENT_FILE", "regular file present, not samefile")

def main():
    parser = argparse.ArgumentParser(
        description="Verify model symlinks from shared folder to multiple destinations."
    )
    parser.add_argument(
        "--config",
        default="link_paths.txt",
        help="Name of the text file listing destination directories (default: link_paths.txt)",
    )
    parser.add_argument(
        "--ext",
        nargs="*",
        default=DEFAULT_EXTS,
        help=f"Model file extensions to check (default: {', '.join(DEFAULT_EXTS)})",
    )
    parser.add_argument(
        "--relative",
        action="store_true",
        help="Display paths relative to the script directory in output."
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    config_path = script_dir / args.config

    dest_dirs = read_dest_dirs(config_path)
    if not dest_dirs:
        print(f"[WARN] No destination directories found in {config_path}")
        sys.exit(1)

    # Warn if any dest directory does not exist
    missing_dirs = [d for d in dest_dirs if not d.exists()]
    for d in missing_dirs:
        print(f"[WARN] Destination directory does not exist: {d}")
    # Continue anyway—maybe you’ll create them later.

    models = list_models(script_dir, args.ext)
    if not models:
        print(f"[INFO] No model files with extensions {args.ext} found in {script_dir}")
        sys.exit(0)

    total = 0
    ok = 0
    missing = 0
    wrong = 0
    notlink_but_same = 0
    exists_diff = 0

    def _fmt(p: Path) -> str:
        return str(p.relative_to(script_dir) if args.relative else p)

    print("\n=== Model Link Verification ===")
    print(f"Shared folder: {_fmt(script_dir)}")
    print(f"Config file : {_fmt(config_path)}")
    print(f"Extensions  : {', '.join(args.ext)}")
    print(f"Dest dirs   :")
    for d in dest_dirs:
        print(f"  - {_fmt(d)}")

    print("\n--- Detailed Report ---")
    for src in models:
        print(f"\nModel: {_fmt(src)}")
        for dest in dest_dirs:
            target = dest / src.name
            status, detail = classify_target(src, target)
            total += 1
            if status == "OK":
                ok += 1
            elif status == "MISSING":
                missing += 1
            elif status == "WRONG_TARGET":
                wrong += 1
            elif status == "NOT_A_LINK_BUT_SAMEFILE":
                notlink_but_same += 1
            elif status == "EXISTS_BUT_DIFFERENT_FILE":
                exists_diff += 1
            print(f"  -> {status:<26} {_fmt(target)}  ({detail})")

    print("\n=== Summary ===")
    print(f"Total checks                : {total}")
    print(f"OK                          : {ok}")
    print(f"Missing                     : {missing}")
    print(f"Symlink points elsewhere    : {wrong}")
    print(f"Not a link but same file    : {notlink_but_same}")
    print(f"Exists but different file   : {exists_diff}")
    print("Done.")

if __name__ == "__main__":
    main()

