#!/usr/bin/env python3
"""
post_write_verify: Verify correct behavior of written code.

Phase 5.1: Verification & trust

Invariant:
- Verify script exists → enforce (run it)
- Missing → warn only (don't block)
- Failure → block
- Negative signal (test failure) blocks; absence does not

This ensures:
- Tests are run if they exist
- Absence of tests doesn't grant false confidence
- Actual failures are caught
"""

import subprocess
import sys
from pathlib import Path

VERIFY = Path("./scripts/verify")


def main():
    # First check: does verify script exist?
    if not VERIFY.exists():
        print(
            "WARNING: ./scripts/verify not found - skipping verification",
            file=sys.stderr,
        )
        # Don't block: absence of tests doesn't grant permission
        # But emit warning for observability
        sys.exit(0)

    # Script exists: run it
    try:
        result = subprocess.run([str(VERIFY)], text=True, timeout=60)
    except subprocess.TimeoutExpired:
        print("BLOCKED: verification script timed out", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"BLOCKED: verification script failed: {str(e)}", file=sys.stderr)
        sys.exit(2)

    # Check result
    if result.returncode != 0:
        print("BLOCKED: verification failed (tests or checks failed)", file=sys.stderr)
        sys.exit(2)

    # Success
    sys.exit(0)


if __name__ == "__main__":
    main()
