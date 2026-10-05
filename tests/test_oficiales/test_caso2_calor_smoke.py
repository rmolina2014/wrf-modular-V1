from pathlib import Path

def test_caso2_estructura():
    root = Path(__file__).resolve().parents[2]
    caso = root / "outputs" / "runs" / "2026-01-01_0000z" / "caso2_calor"
    assert caso.exists()
    assert (caso / "input").exists()
    assert (caso / "control").exists()
    assert (caso / "nudged").exists()
