"""Batch-track and export ReID thumbs for multiple intersections."""

from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace
from typing import Sequence

from tools.export_reid_thumbs import (
    DEFAULT_MIN_DETECTIONS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PAD,
    DEFAULT_VEHICLE_CLASSES,
    export_thumbs,
    parse_class_names,
    write_manifest,
)
from tools.reid_jobs import load_jobs
from traffic_track import parse_classes, run as run_traffic_track


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Build and parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Track and export ReID thumbs for multiple intersections from a jobs CSV. "
            "Writes a shared thumbs/ gallery and one combined manifest.csv."
        )
    )
    parser.add_argument(
        "--jobs",
        type=Path,
        required=True,
        help="CSV with columns camera_name,video[,tracks_dir].",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Shared gallery directory. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--tracks-root",
        type=Path,
        default=Path("outputs/reid"),
        help="Root for per-camera tracking outputs. Default: outputs/reid",
    )
    parser.add_argument(
        "--model",
        default="yolo11n.pt",
        help="YOLO model weights or model name. Defaults to yolo11n.pt.",
    )
    parser.add_argument(
        "--device",
        default="0",
        help='Inference device, for example "0", "cpu", or "mps". Defaults to 0.',
    )
    parser.add_argument(
        "--classes",
        type=parse_classes,
        default=[2, 3, 5, 7],
        help="Comma-separated COCO class IDs to track. Defaults to 2,3,5,7.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.05,
        help="Detection confidence threshold. Defaults to 0.05.",
    )
    parser.add_argument(
        "--tracker",
        default="botsort.yaml",
        help="Ultralytics tracker config. Defaults to botsort.yaml.",
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
        "--export-classes",
        default=",".join(sorted(DEFAULT_VEHICLE_CLASSES)),
        help=(
            "Comma-separated class names to keep when exporting thumbs. "
            f"Default: {','.join(sorted(DEFAULT_VEHICLE_CLASSES))}."
        ),
    )
    parser.add_argument(
        "--skip-track",
        action="store_true",
        help="Reuse existing tracks.csv under each job tracks dir; skip tracking.",
    )
    return parser.parse_args(argv)


def build_track_args(
    *,
    video_path: Path,
    output_dir: Path,
    model: str,
    device: str,
    classes: list[int],
    conf: float,
    tracker: str,
    min_detections: int,
) -> SimpleNamespace:
    """Build a Namespace compatible with traffic_track.run()."""
    return SimpleNamespace(
        video_path=video_path,
        output_dir=output_dir,
        model=model,
        device=device,
        classes=classes,
        conf=conf,
        tracker=tracker,
        min_summary_detections=min_detections,
        summary_class_label="majority",
    )


def run_batch(args: argparse.Namespace) -> None:
    """Track and export thumbs for every job in the CSV."""
    jobs_path = args.jobs.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    tracks_root = args.tracks_root.expanduser().resolve()
    export_class_names = parse_class_names(args.export_classes)

    jobs = load_jobs(jobs_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    tracks_root.mkdir(parents=True, exist_ok=True)

    all_manifest_rows: list[dict[str, object]] = []
    per_camera_counts: dict[str, int] = {}

    for job in jobs:
        tracks_dir = job.resolved_tracks_dir(tracks_root).resolve()
        tracks_path = tracks_dir / "tracks.csv"
        print(f"\n=== {job.camera_name} ===")
        print(f"Video: {job.video}")
        print(f"Tracks dir: {tracks_dir}")

        if args.skip_track:
            if not tracks_path.exists():
                raise FileNotFoundError(
                    f"--skip-track set but tracks.csv missing: {tracks_path}"
                )
            print(f"Skipping track; reusing {tracks_path}")
        else:
            track_args = build_track_args(
                video_path=job.video,
                output_dir=tracks_dir,
                model=args.model,
                device=args.device,
                classes=args.classes,
                conf=args.conf,
                tracker=args.tracker,
                min_detections=args.min_detections,
            )
            run_traffic_track(track_args)

        written, rows = export_thumbs(
            tracks_path=tracks_path,
            video_path=job.video,
            camera_name=job.camera_name,
            output_dir=output_dir,
            min_detections=args.min_detections,
            pad=args.pad,
            class_names=export_class_names,
            write_manifest_file=False,
        )
        per_camera_counts[job.camera_name] = written
        all_manifest_rows.extend(rows)

    manifest_path = output_dir / "manifest.csv"
    write_manifest(manifest_path, all_manifest_rows)

    print("\n=== Batch complete ===")
    for camera_name, count in per_camera_counts.items():
        print(f"  {camera_name}: {count} thumbs")
    print(f"  Total: {len(all_manifest_rows)} thumbs → {output_dir / 'thumbs'}")
    print(f"  Manifest → {manifest_path}")


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point."""
    args = parse_args(argv)
    run_batch(args)


if __name__ == "__main__":
    main()
