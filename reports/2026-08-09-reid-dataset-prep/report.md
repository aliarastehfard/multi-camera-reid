# ReID Dataset Prep — 2026-08-09

## Goal

Prepare vehicle track thumbnails for cross-camera ReID: one JPEG per track, one shared gallery, AIC-style filenames.

## What we built

| Piece | Location |
|-------|----------|
| Single-camera export | `export-reid-thumbs` → `tools/export_reid_thumbs.py` |
| Multi-intersection batch | `prepare-reid-batch` → `tools/prepare_reid_batch.py` |
| Jobs CSV loader | `tools/reid_jobs.py` |
| Example jobs file | `data/reid/jobs.example.csv` |
| Video trim (unchanged) | `utilities/trim_video.py` |

**Pipeline:** trim video → `traffic-track` (YOLO11 + BoT-SORT) → export highest-confidence crop per track → `data/reid/demo/thumbs/` + combined `manifest.csv`.

**Filename format:** `{Camera}_{videoStem}_{trackId}.jpg` (e.g. `IntersectionOne_..._1.jpg`). Camera prefix is required for cross-camera matching.

**Batch behavior:** one shared `thumbs/` folder; one `manifest.csv` with all intersections (not overwritten per job). Per-camera tracking outputs under `outputs/reid/{camera_name}/`.

## Validation

- Demo clips from carreid (`IntersectionOne/Two/Three`, 30s trims).
- Batch run produced 3 thumbs and a 3-row manifest.
- `infer_carreid.py` (lam23005 AIC stack, ResNet101-IBN) embedded thumbs and returned cross-camera top-K matches. Sanity check passed; demo used the same underlying clip for all three camera names, so scores were 1.0.

## Models (not in repo)

| Stage | Model | Where |
|-------|-------|-------|
| Track | YOLO11n (~5 MB) | Auto-download on first `uv run` |
| Match | ResNet101-IBN (~171 MB) | `/home/lam23005/AIC2021-T5-CLV/AICITY2021-Track2/` |

## Not done yet

- Global vehicle IDs (linking tracks into one identity).
- `matches.csv` export from retrieval.
- `infer_carreid.py` wired to this repo (still hardcoded paths on server).
- Full three-site batch on distinct intersection clips (Two/Three often need `--conf` tuning; BoT-SORT may assign no IDs on some clips).

## Usage

```bash
uv run prepare-reid-batch \
  --jobs data/reid/jobs.example.csv \
  --output-dir data/reid/demo \
  --device 0 --conf 0.05 --classes 2,3,5,7
```

Generated thumbs, videos, and embeddings stay gitignored.
