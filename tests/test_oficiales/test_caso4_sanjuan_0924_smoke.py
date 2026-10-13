from pathlib import Path

def test_caso4_estructura():
    root = Path(__file__).resolve().parents[2]
    caso = root / "outputs" / "runs" / "2026-09-24_0000z" / "sanjuan_0924"
    assert caso.exists()
    assert (caso / "input").exists()
    assert (caso / "control").exists()
    assert (caso / "nudged").exists()
