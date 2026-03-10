#!/usr/bin/env python3
"""
Utility to clean up temporary/obsolete scripts from the workspace.
Run this before demonstration delivery to the professor.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Files considered "auxiliaires" (non indispensables pour le pipeline)
CANDIDATES = [
    PROJECT_ROOT / 'scripts' / 'test_hf_api.py',
    PROJECT_ROOT / 'scripts' / 'test_hf.py',
    PROJECT_ROOT / 'simple_hf_test.py',
    PROJECT_ROOT / 'quick_elk_test.py',
    PROJECT_ROOT / 'run_hf_test.py',
    PROJECT_ROOT / 'diagnostic_test.py',
    PROJECT_ROOT / 'generate_report.py',
    PROJECT_ROOT / 'generate_architecture_diagram.py'
]

print("\n🌪️  Cleaning project - removing auxiliary files")
removed = []
for f in CANDIDATES:
    if f.exists():
        try:
            f.unlink()
            removed.append(str(f))
        except Exception as e:
            print(f"⚠️  Could not delete {f}: {e}")
    else:
        print(f"ℹ️  Not present (skipped): {f}")

if removed:
    print("\n✅ Deleted the following files:")
    for r in removed:
        print(f"   - {r}")
else:
    print("\nℹ️  No auxiliary files were removed.")

print("\n🧹  Cleanup complete. Only core modules remain.")
