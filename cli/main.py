"""CLI unificado (usa núcleo orquestador)."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from cli import commands


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wrf-cli", description="CLI unificado WRF Modular")
    subparsers = parser.add_subparsers(dest="cmd")
    commands.add_subcommands(subparsers)
    args = parser.parse_args(argv)

    if not args.cmd:
        parser.print_help()
        return 0

    root = Path(__file__).resolve().parents[1]
    if args.cmd == "casos":
        casos_path = root / "config" / "casos_oficiales.json"
        if args.listar or args.oficiales:
            try:
                data = json.loads(casos_path.read_text(encoding="utf-8"))
                for c in data.get("casos", []):
                    print(f"{c['num']}: {c['id']} ({c['fecha']}) -> {c['resultados_dir']}")
            except Exception as e:
                print(f"Error leyendo casos: {e}", file=sys.stderr)
                return 1
        return 0

    print(f"Ejecutando comando '{args.cmd}' (núcleo orquestador placeholder)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
