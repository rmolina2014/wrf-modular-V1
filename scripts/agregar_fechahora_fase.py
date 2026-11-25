#!/usr/bin/env python3
import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

def get_case_info(case_dir):
    case_dir = Path(case_dir)
    # try control_manifest
    for name in ['control_manifest.json']:
        p = case_dir / name
        if p.exists():
            try:
                m = json.loads(p.read_text())
                t0 = m.get('t0') or m.get('start')
                asim = m.get('asim_horas')
                if t0 and isinstance(t0, str) and '_' in t0:
                    t0 = t0.replace('_', ' ')
                if t0 and isinstance(t0, str) and len(t0) == 16:
                    t0 = t0 + ':00'
                return t0, asim
            except Exception:
                pass
    # try namelist
    for name in ['namelist_nudged.input', 'namelist.input']:
        p = case_dir / name
        if p.exists():
            try:
                txt = p.read_text()
                # asim not directly there, try to infer
                return None, None
            except Exception:
                pass
    return None, None

def parse_t0(t0str):
    if not t0str:
        return None
    try:
        # handle formats
        t0str = str(t0str).replace('Z', '').replace('_', ' ')
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M']:
            try:
                return datetime.strptime(t0str, fmt)
            except:
                continue
    except:
        pass
    return None

def main():
    root = Path('/home/pgich/wrf-modular-V1/outputs/runs')
    updated = 0
    for csv_path in root.rglob('errores_largo.csv'):
        case_dir = csv_path.parent
        t0s, asim = get_case_info(case_dir)
        t0 = parse_t0(t0s)
        if asim is None:
            asim = 12  # default per protocolo
        try:
            asim = float(asim)
        except:
            asim = 12
        if not t0:
            print(f'SKIP {csv_path} (no t0)')
            continue
        # read
        rows = []
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for r in reader:
                rows.append(r)
        if not rows:
            continue
        if 'fecha_hora_local' in (fieldnames or []):
            print(f'ALREADY {csv_path}')
            continue
        # add columns
        new_fields = list(fieldnames) + ['fecha_hora_local', 'fase']
        out_rows = []
        for r in rows:
            try:
                h = int(float(r.get('horizonte_h', 0)))
            except:
                h = 0
            f_utc = t0 + timedelta(hours=h)
            f_local = f_utc - timedelta(hours=3)  # ART
            fase = 'asimilacion' if h <= asim else 'pronostico'
            r2 = dict(r)
            r2['fecha_hora_local'] = f_local.strftime('%Y-%m-%d %H:%M:%S')
            r2['fase'] = fase
            out_rows.append(r2)
        # write back
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=new_fields)
            w.writeheader()
            for r in out_rows:
                w.writerow(r)
        print(f'UPDATED {csv_path}')
        updated += 1
    print(f'DONE {updated}')

if __name__ == '__main__':
    main()
