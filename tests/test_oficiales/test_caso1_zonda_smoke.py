from pathlib import Path

def test_caso1_estructura():
    root = Path(__file__).resolve().parents[2]
    caso = root / "outputs" / "runs" / "2026-07-31_0000z" / "caso1_zonda"
    assert caso.exists()
    assert (caso / "input").exists()
    assert (caso / "control").exists()
    assert (caso / "nudged").exists()
