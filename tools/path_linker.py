#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parent.parent
TOOL_PATH = REPO_ROOT / "tools" / "third-party"

HOUDINI_ROOT = Path(r"C:\Program Files\Side Effects Software")
GIT_BASH_EXE = Path(r"C:\Program Files\Git\bin\bash.exe")
HOUDINI_BIN_NAMES = ["houdini", "hcmd", "mplay", "hython"]


def find_latest_houdini_version() -> Optional[str]:
    if not HOUDINI_ROOT.exists():
        return None

    versions: list[tuple[int, ...]] = []
    for child in HOUDINI_ROOT.iterdir():
        if not child.is_dir():
            continue

        match = re.fullmatch(r"Houdini\s+([0-9]+(?:\.[0-9]+)*)", child.name)
        if not match:
            continue

        version_text = match.group(1)
        try:
            versions.append(tuple(int(x) for x in version_text.split(".")))
        except ValueError:
            pass

    if not versions:
        return None

    return ".".join(str(x) for x in max(versions))


def parse_houdini_version_from_target(target: str) -> Optional[str]:
    match = re.search(r"Houdini\s+([0-9]+(?:\.[0-9]+)*)", target)
    return match.group(1) if match else None


def is_same_app_symlink(app: str, target: str) -> bool:
    normalized = target.replace("/", "\\").lower()
    if app == "houdini":
        return "\\side effects software\\houdini " in normalized
    if app == "git-bash":
        return "\\program files\\git\\" in normalized
    return False


def replace_link(link_path: Path, target: Path, app: str) -> None:
    if not target.exists():
        print(f"[WARN] Missing source executable: {target}")
        return

    if link_path.exists() or link_path.is_symlink():
        if link_path.is_symlink():
            old_target = os.readlink(link_path)
            if is_same_app_symlink(app, old_target):
                old_version = parse_houdini_version_from_target(old_target) if app == "houdini" else None
                new_version = parse_houdini_version_from_target(str(target)) if app == "houdini" else None

                link_path.unlink()
                link_path.symlink_to(target)

                if old_version and new_version and old_version != new_version:
                    direction = "upgraded" if tuple(map(int, new_version.split("."))) > tuple(map(int, old_version.split("."))) else "downgraded"
                    print(f"[OK] {link_path.name}: {direction} {old_version} -> {new_version}")
                else:
                    print(f"[OK] {link_path.name}: updated link target")
                return

            print(f"[WARN] {link_path} is a symlink to another app ({old_target}); leaving as-is")
            return

        print(f"[WARN] {link_path} exists and is not a symlink; leaving as-is")
        return

    link_path.symlink_to(target)
    print(f"[OK] Created {link_path.name} -> {target}")


def link_houdini(version_arg: Optional[str]) -> int:
    if version_arg is None or version_arg.lower() == "latest":
        version = find_latest_houdini_version()
        if not version:
            print("[ERROR] Could not find any installed Houdini versions in 'C:\\Program Files\\Side Effects Software'.")
            return 1
    else:
        version = version_arg

    base = HOUDINI_ROOT / f"Houdini {version}" / "bin"
    if not base.exists():
        print(f"[ERROR] Houdini folder not found: {base}")
        return 1

    TOOL_PATH.mkdir(parents=True, exist_ok=True)
    for bin_name in HOUDINI_BIN_NAMES:
        replace_link(TOOL_PATH / f"{bin_name}.exe", base / f"{bin_name}.exe", "houdini")

    return 0


def link_git_bash() -> int:
    TOOL_PATH.mkdir(parents=True, exist_ok=True)
    replace_link(TOOL_PATH / "git-bash.exe", GIT_BASH_EXE, "git-bash")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="path_linker",
        description="Create symlinks for known third-party app executables in tools/third-party.",
    )
    parser.add_argument("app", nargs="?", help="Application to link: houdini | git-bash | git")
    parser.add_argument("version", nargs="?", help="Version for versioned apps (e.g. houdini 20.5.654 or latest)")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.app:
        parser.print_usage()
        print("Examples:")
        print("  path_linker houdini 20.5.654")
        print("  path_linker houdini latest")
        print("  path_linker git-bash")
        return 0

    app = args.app.lower()

    try:
        if app == "houdini":
            return link_houdini(args.version)
        if app in {"git", "git-bash"}:
            return link_git_bash()
    except OSError as ex:
        print(f"[ERROR] Failed to create/replace symlink: {ex}")
        print("Hint: On Windows, symlink creation may require Developer Mode or elevated privileges.")
        return 1

    print(f"[ERROR] Unsupported app '{args.app}'. Supported: houdini, git-bash")
    return 1


if __name__ == "__main__":
    sys.exit(main())