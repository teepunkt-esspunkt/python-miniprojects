import os
import sys
from pathlib import Path

EXT = ".safetensors"
CONFIG_FILE = "link_paths.txt"

def read_dest_dirs(config_path: Path):
    if not config_path.exists():
        print(f"[ERROR] No config file at {config_path}")
        sys.exit(1)
    dests = []
    for raw in config_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        expanded = os.path.expanduser(os.path.expandvars(line))
        dests.append(Path(expanded).resolve())
    return dests

def main():
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir / CONFIG_FILE
    dest_dirs = read_dest_dirs(config_path)

    models = [p for p in script_dir.glob(f"*{EXT}") if p.is_file()]
    if not models:
        print(f"[INFO] No {EXT} files in {script_dir}")
        return

    print(f"=== Creating symlinks for {len(models)} {EXT} models ===")
    for src in models:
        for dest in dest_dirs:
            dest.mkdir(parents=True, exist_ok=True)
            target = dest / src.name
            if target.exists():
                print(f"[SKIP] Already exists: {target}")
                continue
            try:
                os.symlink(src, target, target_is_directory=False)
                print(f"[OK] {target} -> {src}")
            except OSError as e:
                print(f"[FAIL] Could not link {target}: {e}")

    print("Done.")

if __name__ == "__main__":
    main()
