"""
Quick check script to verify required imports and print versions.
Run: python verify_imports.py
"""
import importlib
import sys

packages = ["matplotlib", "pandas", "streamlit"]

ok = True
for pkg in packages:
    try:
        m = importlib.import_module(pkg)
        ver = getattr(m, "__version__", "<version not exposed>")
        print(f"{pkg}: OK, version={ver}")
    except Exception as e:
        print(f"{pkg}: import FAILED -> {e}")
        ok = False

if not ok:
    print("\nOne or more imports failed. Make sure you're using the same Python interpreter where packages are installed.")
    sys.exit(1)
else:
    print("\nAll imports OK.")
