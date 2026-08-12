#!/usr/bin/env python3
import pathlib
import sys


SENTINELS = (
    "ROOT_PASSWORD_SENTINEL_DO_NOT_LOG",
    "RW_SENTINEL_DO_NOT_LOG",
    "CF_SENTINEL_DO_NOT_LOG",
    "RW_API_SENTINEL_DO_NOT_LOG",
    "CF_API_SENTINEL_DO_NOT_LOG",
    "RW_TAG_SENTINEL_DO_NOT_LOG",
    "CF_TAG_SENTINEL_DO_NOT_LOG",
    "FAIL-WARP-SENTINEL",
    "LIMITED-WARP-SENTINEL",
    "GOOD-WARP-SENTINEL",
    "test-secret-0001",
    "test-secret-0041",
)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: assert_no_secret_leaks.py LOG_FILE")
    content = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    leaked = [secret for secret in SENTINELS if secret in content]
    if leaked:
        print("secret sentinel appeared in verbose Ansible output", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
