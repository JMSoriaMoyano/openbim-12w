"""
Smoke test del entorno OpenBIM-12w.
Ejecutar: python scripts/00_smoke_test.py
Si todo pasa, estás listo para la S1·L del lunes 11/05/2026.
"""
import sys
from pathlib import Path

ok = True

def check(name, fn):
    global ok
    try:
        result = fn()
        print(f"  ✓ {name}: {result}")
    except Exception as e:
        print(f"  ✗ {name}: {e}")
        ok = False

print("=== OpenBIM-12w · Smoke test ===\n")

print("[1/4] Python")
check("version", lambda: sys.version.split()[0])
assert sys.version_info >= (3, 10), "Necesitas Python >= 3.10"

print("\n[2/4] IfcOpenShell")
def _ifc():
    import ifcopenshell
    m = ifcopenshell.file(schema="IFC4")
    return f"v{ifcopenshell.version} (creado modelo IFC4 vacío)"
check("import + create", _ifc)

print("\n[3/4] ifctester (validación IDS)")
def _tester():
    from ifctester import ids  # noqa: F401
    return "módulo importable"
check("import", _tester)

print("\n[4/4] Estructura del repo")
expected = ["models", "ids", "scripts", "bcf", "docs", "reports", "final"]
def _struct():
    root = Path(__file__).resolve().parent.parent
    missing = [d for d in expected if not (root / d).is_dir()]
    if missing:
        raise RuntimeError(f"Faltan carpetas: {missing}")
    return f"todas presentes en {root.name}/"
check("carpetas", _struct)

print()
if ok:
    print("✅ Setup OK. Listo para empezar la S1·L (lunes 11/05/2026 07:30).")
    sys.exit(0)
else:
    print("❌ Hay errores. Revisa el README y vuelve a ejecutar.")
    sys.exit(1)
