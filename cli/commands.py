"""Comandos CLI unificado."""
from __future__ import annotations
import argparse
from pathlib import Path


def add_subcommands(subparsers: argparse._SubParsersAction) -> None:
    p_run = subparsers.add_parser("run", help="Ejecuta pipeline completo")
    p_run.add_argument("--date", required=True)
    p_run.add_argument("--hour", required=True)
    p_run.add_argument("--caso", required=True)
    p_run.add_argument("--json", required=False)
    p_run.add_argument("--namelist", required=False)
    p_run.add_argument("--run-real", action="store_true", default=True)
    p_run.add_argument("--no-run-real", dest="run_real", action="store_false")
    p_run.add_argument("--skip-control", action="store_true")
    p_run.set_defaults(cmd="run")

    p_prep = subparsers.add_parser("prepare", help="Solo preparación")
    p_prep.add_argument("--date", required=True)
    p_prep.add_argument("--hour", required=True)
    p_prep.add_argument("--caso", required=True)
    p_prep.set_defaults(cmd="prepare")

    p_val = subparsers.add_parser("validate", help="Validar corrida existente")
    p_val.add_argument("--nudged", required=True)
    p_val.add_argument("--control", required=True)
    p_val.add_argument("--out", required=True)
    p_val.set_defaults(cmd="validate")

    p_casos = subparsers.add_parser("casos", help="Gestionar casos oficiales")
    p_casos.add_argument("--listar", action="store_true")
    p_casos.add_argument("--oficiales", action="store_true")
    p_casos.set_defaults(cmd="casos")
