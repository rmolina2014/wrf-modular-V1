# Configuración op15km vs Operativo (sanjuan) vs Control (caso oficial)

| Parámetro | Operativo (sanjuan d01) | Control oficial | op15km | Notas |
|---|---|---|---|---|
| **Dominio** |  |  |  |  |
| e_we | 141 | 80 | 80 | Resolución 15 km requiere dominio menor |
| e_sn | 200 | 60 | 60 | Resolución 15 km requiere dominio menor |
| e_vert | 35 | 35 | 35 | Igual en todos |
| **Espacial** |  |  |  |  |
| dx | 4000 | 15000 | 15000 | op15km = control (sin cambio) |
| dy | 4000 | 15000 | 15000 | op15km = control (sin cambio) |
| **Temporal** |  |  |  |  |
| time_step | 15 | 45 | 45 | op15km = control |
| run_hours | 24 | 3 | 3 | Caso de estudio 3 horas |
| fdda_end | N/A | 720 | 720 | Asimilación 12 horas (diferente del caso 4 diag que usa 180) |
| **Física de convección** |  |  |  |  |
| cu_physics | 0 | -1 | **6** | **op15km: explícito (Grell-3D), cambio respecto a control** |
| **Radiación** |  |  |  |  |
| ra_lw_physics | 1 | -1 | **4** | **op15km: RRTMG, cambio respecto a control** |
| ra_sw_physics | 2 | -1 | **4** | **op15km: RRTMG, cambio respecto a control** |
| radt | 4 | 15 | 15 | op15km = control |
| **Capa límite y superficie** |  |  |  |  |
| bl_pbl_physics | 2 | -1 | 2 | op15km = operativo, explícito (YSU) |
| sf_sfclay_physics | 2 | -1 | 2 | op15km = operativo, explícito (Monin-Obukhov) |
| sf_surface_physics | 2 | -1 | 2 | op15km = operativo, explícito (Noah LSM) |
| **Urbano** |  |  |  |  |
| sf_urban_physics | **0** | 0 | **2** | **op15km: BEP (Building Effect Parameterization), cambio respecto a control** |
| **Micrófisica** |  |  |  |  |
| mp_physics | 8 | -1 | 8 | op15km = operativo (WSM6), explícito |
| num_metgrid_levels | 32 | 34 | 34 | op15km = control |

## Fuentes
- **Operativo (sanjuan d01)**: `/home/pgich/wrf-operativo/datos/namelists/sanjuan/namelistTemp.input`
- **Control oficial**: `/home/pgich/wrf-modular-V1/outputs/runs/2026-09-24_0000z/sanjuan_0924/namelist_control.input`
- **op15km**: Rama op15km (commit 30ea08c y posteriores)

## Cambios clave op15km vs control
1. **Física explícita** (todos los parámetros negativos → números)
2. **cu_physics=6** (Grell-3D en lugar de -1/deseleccionado)
3. **ra_lw/ra_sw=4** (RRTMG en lugar de -1)
4. **sf_urban_physics=2** (BEP en lugar de 0/sin modelo urbano)
5. **fdda_end=720** (igual al control oficial, 12 horas)
