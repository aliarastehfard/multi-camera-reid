"""Run YOLO11 detection and BoT-SORT tracking on traffic intersection video."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


DEFAULT_CLASSES = (0, 1, 2, 3, 5, 7)
DEFAULT_MIN_SUMMARY_DETECTIONS = 5
TRACK_COLUMNS = (
    "video_id",
    "frame_idx",
    "timestamp_sec",
    "track_id",
    "cls_id",
    "cls_name",
    "conf",
    "x",
    "y",
    "w",
    "h",
)
SUMMARY_COLUMNS = (
    "track_id",
    "cls_name",
    "first_frame",
    "last_frame",
    "first_ts",
    "last_ts",
    "num_detections",
)
VIDEO_EXTENSIONS = {".avi", ".mov", ".mp4", ".mkv", ".webm"}


@dataclass(frozen=True)
class VideoMetadata:
    """Basic input video metadata needed for timestamp conversion."""

    fps: float
    frame_count: int

    @property
    def duration_sec(self) -> float:
        """Return duration in seconds when frame count and fps are available."""
        if self.fps <= 0:
            return 0.0
        return self.frame_count / self.fps


def parse_classes(raw_classes: str) -> list[int]:
    """Parse comma-separated COCO class IDs."""
    class_ids: list[int] = []
    for item in raw_classes.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            class_ids.append(int(item))
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f"Invalid class ID {item!r}. Use a comma-separated list of integers."
            ) from exc

    if not class_ids:
        raise argparse.ArgumentTypeError("At least one class ID is required.")
    return class_ids


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Build and parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Track vehicles and pedestrians in an intersection video with "
            "Ultralytics YOLO and BoT-SORT."
        )
    )
    parser.add_argument("video_path", type=Path, help="Path to the input video.")
    parser.add_argument(
        "output_dir",
        type=Path,
        nargs="?",
        help="Directory for CSV and video outputs. Defaults to outputs/<input-video-stem>.",
    )
    parser.add_argument(
        "--model",
        default="yolo11n.pt",
        help="YOLO model weights or model name. Defaults to yolo11n.pt.",
    )
    parser.add_argument(
        "--device",
        default="mps",
        help='Inference device, for example "mps", "0", or "cpu". Defaults to mps.',
    )
    parser.add_argument(
        "--classes",
        type=parse_classes,
        default=list(DEFAULT_CLASSES),
        help="Comma-separated COCO class IDs to track. Defaults to 0,1,2,3,5,7.",
    )
    parser.add_argument(
        "--tracker",
        default="botsort.yaml",
        help="Ultralytics tracker config. Defaults to botsort.yaml.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Detection confidence threshold. Defaults to 0.25.",
    )
    parser.add_argument(
        "--min-summary-detections",
        type=int,
        default=DEFAULT_MIN_SUMMARY_DETECTIONS,
        help=(
            "Minimum detections a track needs to be counted in summary.txt. "
            f"Defaults to {DEFAULT_MIN_SUMMARY_DETECTIONS}."
        ),
    )
    parser.add_argument(
        "--summary-class-label",
        choices=("majority", "first"),
        default="majority",
        help=(
            "How to choose the class label for each track summary row. "
            'Use "majority" for the most frequent label or "first" for the first observed label. '
            "Defaults to majority."
        ),
    )
    return parser.parse_args(argv)


def get_video_metadata(video_path: Path) -> VideoMetadata:
    """Read fps and frame count from the input video."""
    import cv2

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    try:
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    finally:
        capture.release()

    if fps <= 0:
        raise ValueError(f"Could not determine a valid FPS for video: {video_path}")

    return VideoMetadata(fps=fps, frame_count=frame_count)


def class_name_for(model_names: Any, cls_id: int) -> str:
    """Return a readable class name from Ultralytics model names."""
    if isinstance(model_names, dict):
        return str(model_names.get(cls_id, cls_id))
    if isinstance(model_names, (list, tuple)) and 0 <= cls_id < len(model_names):
        return str(model_names[cls_id])
    return str(cls_id)


def as_python_list(value: Any) -> list[Any]:
    """Convert Ultralytics tensor-like values to a Python list."""
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()
    if hasattr(value, "tolist"):
        return value.tolist()
    return list(value)


def write_track_rows(
    *,
    results: Iterable[Any],
    tracks_path: Path,
    video_id: str,
    fps: float,
    model_names: Any,
) -> tuple[int, Path | None]:
    """Consume tracking results frame by frame and write trajectory rows."""
    rows_written = 0
    save_dir: Path | None = None

    with tracks_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=TRACK_COLUMNS)
        writer.writeheader()

        for frame_idx, result in enumerate(results):
            result_save_dir = getattr(result, "save_dir", None)
            if result_save_dir is not None:
                save_dir = Path(result_save_dir)

            boxes = getattr(result, "boxes", None)
            if boxes is None or getattr(boxes, "id", None) is None:
                continue

            track_ids = as_python_list(boxes.id)
            class_ids = [int(cls_id) for cls_id in as_python_list(boxes.cls)]
            confidences = [float(conf) for conf in as_python_list(boxes.conf)]
            xywh_values = as_python_list(boxes.xywh)
            timestamp_sec = frame_idx / fps

            for track_id, cls_id, conf, xywh in zip(
                track_ids, class_ids, confidences, xywh_values, strict=True
            ):
                x, y, w, h = (float(value) for value in xywh)
                writer.writerow(
                    {
                        "video_id": video_id,
                        "frame_idx": frame_idx,
                        "timestamp_sec": timestamp_sec,
                        "track_id": int(track_id),
                        "cls_id": cls_id,
                        "cls_name": class_name_for(model_names, cls_id),
                        "conf": conf,
                        # x, y, w, h are pixel-space boxes, not world coordinates.
                        "x": x,
                        "y": y,
                        "w": w,
                        "h": h,
                    }
                )
                rows_written += 1

    return rows_written, save_dir


def build_track_summary(
    tracks_path: Path,
    summary_path: Path,
    class_label_strategy: str = "majority",
) -> int:
    """Create a one-row-per-track summary CSV from tracks.csv."""
    import pandas as pd

    tracks = pd.read_csv(tracks_path)
    if tracks.empty:
        pd.DataFrame(columns=SUMMARY_COLUMNS).to_csv(summary_path, index=False)
        return 0

    if class_label_strategy == "majority":
        cls_name_agg = lambda values: values.value_counts().idxmax()
    elif class_label_strategy == "first":
        cls_name_agg = "first"
    else:
        raise ValueError(f"Unknown class label strategy: {class_label_strategy}")

    summary = (
        tracks.sort_values(["track_id", "frame_idx"])
        .groupby("track_id", as_index=False)
        .agg(
            cls_name=("cls_name", cls_name_agg),
            first_frame=("frame_idx", "min"),
            last_frame=("frame_idx", "max"),
            first_ts=("timestamp_sec", "min"),
            last_ts=("timestamp_sec", "max"),
            num_detections=("frame_idx", "size"),
        )
    )
    summary.to_csv(summary_path, index=False, columns=SUMMARY_COLUMNS)
    return int(summary["track_id"].nunique())


def find_saved_video(save_dir: Path, input_video: Path) -> Path | None:
    """Find the video saved by Ultralytics save=True."""
    if not save_dir.exists():
        return None

    preferred = save_dir / input_video.name
    if preferred.exists():
        return preferred

    candidates = [
        path
        for path in save_dir.iterdir()
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def place_annotated_video(save_dir: Path | None, output_dir: Path, input_video: Path) -> Path:
    """Rename the Ultralytics annotated video to the stable output path."""
    annotated_path = output_dir / "annotated.mp4"
    if save_dir is None:
        raise FileNotFoundError("Ultralytics did not report an annotated video output directory.")

    saved_video = find_saved_video(save_dir, input_video)
    if saved_video is None:
        raise FileNotFoundError(f"Could not find annotated video in {save_dir}")

    if saved_video.resolve() == annotated_path.resolve():
        return annotated_path

    if annotated_path.exists():
        annotated_path.unlink()
    saved_video.rename(annotated_path)
    return annotated_path


def summary_lines(
    summary_path: Path,
    duration_sec: float,
    min_detections: int = DEFAULT_MIN_SUMMARY_DETECTIONS,
) -> list[str]:
    """Build the human-readable tracking summary."""
    import pandas as pd

    summary = pd.read_csv(summary_path)
    filtered_summary = summary[summary["num_detections"] >= min_detections]
    total_tracks = int(len(filtered_summary))
    lines = [
        "Tracking complete",
        f"Total tracks: {total_tracks}",
        f"Duration: {duration_sec:.2f} sec",
        f"Minimum detections per counted track: {min_detections}",
        "Per-class track counts:",
    ]

    if filtered_summary.empty:
        return [*lines, "  none: 0"]

    per_class = filtered_summary["cls_name"].value_counts().sort_index()
    return [*lines, *(f"  {cls_name}: {int(count)}" for cls_name, count in per_class.items())]


def write_summary(
    summary_path: Path,
    report_path: Path,
    duration_sec: float,
    min_detections: int = DEFAULT_MIN_SUMMARY_DETECTIONS,
) -> None:
    """Write the console-style tracking summary to disk."""
    report_path.write_text(
        "\n".join(summary_lines(summary_path, duration_sec, min_detections)) + "\n"
    )


def print_summary(
    summary_path: Path,
    duration_sec: float,
    min_detections: int = DEFAULT_MIN_SUMMARY_DETECTIONS,
) -> None:
    """Print total tracks, per-class track counts, and video duration."""
    print()
    for line in summary_lines(summary_path, duration_sec, min_detections):
        print(line)


def default_output_dir(video_path: Path) -> Path:
    """Return the default output directory for an input video."""
    return Path("outputs") / video_path.stem


def run(args: argparse.Namespace) -> None:
    """Run the full tracking pipeline."""
    from ultralytics import YOLO

    video_path = args.video_path.expanduser().resolve()
    output_dir = args.output_dir if args.output_dir is not None else default_output_dir(video_path)
    output_dir = output_dir.expanduser().resolve()

    if not video_path.exists():
        raise FileNotFoundError(f"Input video does not exist: {video_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = get_video_metadata(video_path)

    tracks_path = output_dir / "tracks.csv"
    summary_path = output_dir / "track_summary.csv"
    report_path = output_dir / "summary.txt"

    model = YOLO(args.model)
    results = model.track(
        source=str(video_path),
        stream=True,
        persist=True,
        tracker=args.tracker,
        classes=args.classes,
        device=args.device,
        conf=args.conf,
        save=True,
        project=str(output_dir.parent),
        name=output_dir.name,
        exist_ok=True,
    )

    _, save_dir = write_track_rows(
        results=results,
        tracks_path=tracks_path,
        video_id=video_path.stem,
        fps=metadata.fps,
        model_names=model.names,
    )
    build_track_summary(
        tracks_path,
        summary_path,
        class_label_strategy=args.summary_class_label,
    )
    place_annotated_video(save_dir, output_dir, video_path)
    write_summary(summary_path, report_path, metadata.duration_sec, args.min_summary_detections)
    print_summary(summary_path, metadata.duration_sec, args.min_summary_detections)


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point."""
    args = parse_args(argv)
    run(args)


if __name__ == "__main__":
    main()
