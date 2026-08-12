#!/usr/bin/env python3
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[2]
ROLE_TASKS = ROOT / "roles" / "deploy-rw-by-lynx" / "tasks"


def main():
    sources = [
        ROOT / "deploy.yml",
        *ROOT.glob("tests/playbooks/*.yml"),
        *ROOT.glob("molecule/**/*.yml"),
    ]
    missing = []
    for source in sources:
        content = source.read_text(encoding="utf-8")
        for task_name in re.findall(r"tasks_from:\s*([A-Za-z0-9_.-]+)", content):
            candidate = ROLE_TASKS / task_name
            if candidate.suffix not in {".yml", ".yaml"}:
                candidate = candidate.with_suffix(".yml")
            if not candidate.exists():
                missing.append(f"{source.relative_to(ROOT)}: {task_name}")
    if missing:
        raise SystemExit("missing role task files:\n" + "\n".join(missing))


if __name__ == "__main__":
    main()
