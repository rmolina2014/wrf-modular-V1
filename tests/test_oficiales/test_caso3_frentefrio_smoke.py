from pathlib import Path

def test_caso3_estructura():
    root = Path(__file__).resolve().parents[2]
    caso = root / "outputs" / "runs" / "2026-05-16_0000z" / "caso3_frentefrio"
    assert caso.exists()
    assert (caso / "input").exists()
    assert (caso / "control").exists()
    assert (caso / "nudged").exists()
