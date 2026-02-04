#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path

VERIFY = Path("./scripts/verify")

def main():
    if not VERIFY.exists():
        print("BLOCKED: ./scripts/verify is required", file=sys.stderr)
        sys.exit(2)

    result = subprocess.run([str(VERIFY)], text=True)
    if result.returncode != 0:
        print("BLOCKED: verification failed", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
