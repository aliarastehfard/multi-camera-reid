"""Export one vehicle crop per track for ReID gallery prep.

Reads tracks.csv from traffic-track and the source video, picks the
highest-confidence detection per track, and writes AIC-style JPEG thumbs.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Sequence

import cv2
import pandas as pd

DEFAULT_VEHICLE_CLASSES = frozenset({"car", "motorcycle", "bus", "truck"})
DEFAULT_MIN_DETECTIONS = 5
DEFAULT_PAD = 0.05
DEFAULT_OUTPUT_DIR = Path("data/reid/demo")
MANIFEST_COLUMNS = (
    "camera",
    "video",
    "track_id",
    "frame_idx",
    "cls_name",
    "conf",
    "thumb_path",
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Build and parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Export one JPEG crop per vehicle track from tracks.csv and the "
            "source video for ReID gallery prep."
        )
    )
    parser.add_argument(
        "--tracks",
        type=Path,
        required=True,
        help="Path to tracks.csv from traffic-track.",
    )
    parser.add_argument(
        "--video",
        type=Path,
        required=True,
        help="Source video used for the tracking run.",
    )
    parser.add_argument(
        "--camera-name",
        required=True,
        help="Camera / intersection name used in thumb filenames (e.g. IntersectionOne).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for thumbs/ and manifest.csv. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--min-detections",
        type=int,
        default=DEFAULT_MIN_DETECTIONS,
        help=(
            "Minimum detections a track needs before a thumb is exported. "
            f"Default: {DEFAULT_MIN_DETECTIONS}."
        ),
    )
    parser.add_argument(
        "--pad",
        type=float,
        default=DEFAULT_PAD,
        help=(
            "Relative padding applied to each side of the bbox before cropping. "
            f"Default: {DEFAULT_PAD}."
        ),
    )
    parser.add_argument(
        "--classes",
        default=",".join(sorted(DEFAULT_VEHICLE_CLASSES)),
        help=(
            "Comma-separated class names to keep. "
            f"Default: {','.join(sorted(DEFAULT_VEHICLE_CLASSES))}."
        ),
    )
    return parser.parse_args(argv)


def parse_class_names(raw_classes: str) -> frozenset[str]:
    """Parse comma-separated class names into a frozenset."""
    names = {item.strip() for item in raw_classes.split(",") if item.strip()}
    if not names:
        raise argparse.ArgumentTypeError("At least one class name is required.")
    return frozenset(names)


def xywh_center_to_xyxy(
    x: float,
    y: float,
    w: float,
    h: float,
    frame_w: int,
    frame_h: int,
    pad: float,
) -> tuple[int, int, int, int]:
    """Convert center xywh to padded, clamped integer xyxy crop bounds."""
    pad_x = w * pad
    pad_y = h * pad
    x1 = int(round(x - w / 2.0 - pad_x))
    y1 = int(round(y - h / 2.0 - pad_y))
    x2 = int(round(x + w / 2.0 + pad_x))
    y2 = int(round(y + h / 2.0 + pad_y))

    x1 = max(0, min(x1, frame_w - 1))
    y1 = max(0, min(y1, frame_h - 1))
    x2 = max(x1 + 1, min(x2, frame_w))
    y2 = max(y1 + 1, min(y2, frame_h))
    return x1, y1, x2, y2


def select_representative_rows(
    tracks: pd.DataFrame,
    class_names: frozenset[str],
    min_detections: int,
) -> pd.DataFrame:
    """Keep vehicle tracks with enough detections; pick highest-conf row each."""
    filtered = tracks[tracks["cls_name"].isin(class_names)].copy()
    if filtered.empty:
        return filtered

    counts = filtered.groupby("track_id").size()
    keep_ids = counts[counts >= min_detections].index
    filtered = filtered[filtered["track_id"].isin(keep_ids)]
    if filtered.empty:
        return filtered

    # Highest confidence wins; ties broken by earliest frame for stability.
    ranked = filtered.sort_values(
        ["track_id", "conf", "frame_idx"],
        ascending=[True, False, True],
    )
    return ranked.groupby("track_id", as_index=False).first()


def thumb_filename(camera_name: str, video_stem: str, track_id: int) -> str:
    """Build AIC-style thumb filename: {Camera}_{videoStem}_{trackId}.jpg."""
    return f"{camera_name}_{video_stem}_{track_id}.jpg"


def write_manifest(manifest_path: Path, rows: list[dict[str, object]]) -> None:
    """Write manifest.csv for exported thumbs."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def export_thumbs(
    tracks_path: Path,
    video_path: Path,
    camera_name: str,
    output_dir: Path,
    min_detections: int = DEFAULT_MIN_DETECTIONS,
    pad: float = DEFAULT_PAD,
    class_names: frozenset[str] = DEFAULT_VEHICLE_CLASSES,
    write_manifest_file: bool = True,
) -> tuple[int, list[dict[str, object]]]:
    """Export thumbs; optionally write manifest.csv.

    Returns (written_count, manifest_rows).
    """
    if not tracks_path.exists():
        raise FileNotFoundError(f"tracks.csv does not exist: {tracks_path}")
    if not video_path.exists():
        raise FileNotFoundError(f"Video does not exist: {video_path}")
    if min_detections < 1:
        raise ValueError("--min-detections must be >= 1")
    if pad < 0:
        raise ValueError("--pad must be >= 0")

    tracks = pd.read_csv(tracks_path)
    required = {"frame_idx", "track_id", "cls_name", "conf", "x", "y", "w", "h"}
    missing = required - set(tracks.columns)
    if missing:
        raise ValueError(f"tracks.csv missing columns: {sorted(missing)}")

    representatives = select_representative_rows(tracks, class_names, min_detections)

    thumbs_dir = output_dir / "thumbs"
    thumbs_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.csv"
    manifest_rows: list[dict[str, object]] = []

    if representatives.empty:
        if write_manifest_file:
            write_manifest(manifest_path, manifest_rows)
        print(f"No tracks met the export criteria for {camera_name}.")
        return 0, manifest_rows

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_stem = video_path.stem
    written = 0

    try:
        for row in representatives.itertuples(index=False):
            frame_idx = int(row.frame_idx)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ok, frame = cap.read()
            if not ok or frame is None:
                print(f"Warning: could not read frame {frame_idx} for track {row.track_id}")
                continue

            x1, y1, x2, y2 = xywh_center_to_xyxy(
                float(row.x),
                float(row.y),
                float(row.w),
                float(row.h),
                frame_w,
                frame_h,
                pad,
            )
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                print(f"Warning: empty crop for track {row.track_id} at frame {frame_idx}")
                continue

            filename = thumb_filename(camera_name, video_stem, int(row.track_id))
            thumb_path = thumbs_dir / filename
            if not cv2.imwrite(str(thumb_path), crop):
                print(f"Warning: failed to write {thumb_path}")
                continue

            written += 1
            manifest_rows.append(
                {
                    "camera": camera_name,
                    "video": str(video_path),
                    "track_id": int(row.track_id),
                    "frame_idx": frame_idx,
                    "cls_name": row.cls_name,
                    "conf": float(row.conf),
                    "thumb_path": str(thumb_path),
                }
            )
    finally:
        cap.release()

    if write_manifest_file:
        write_manifest(manifest_path, manifest_rows)

    print(f"Wrote {written} thumbs for {camera_name} → {thumbs_dir}")
    if write_manifest_file:
        print(f"Manifest → {manifest_path}")
    return written, manifest_rows


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point."""
    args = parse_args(argv)
    class_names = parse_class_names(args.classes)
    export_thumbs(
        tracks_path=args.tracks.expanduser().resolve(),
        video_path=args.video.expanduser().resolve(),
        camera_name=args.camera_name,
        output_dir=args.output_dir.expanduser().resolve(),
        min_detections=args.min_detections,
        pad=args.pad,
        class_names=class_names,
        write_manifest_file=True,
    )


if __name__ == "__main__":
    main()
