"""Run YOLO11 detection only on traffic intersection video."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


DEFAULT_CLASSES = (0, 1, 2, 3, 5, 7)
DETECTION_COLUMNS = (
    "video_id",
    "frame_idx",
    "timestamp_sec",
    "cls_id",
    "cls_name",
    "conf",
    "x",
    "y",
    "w",
    "h",
)
SUMMARY_COLUMNS = (
    "cls_id",
    "cls_name",
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
        description="Detect vehicles and pedestrians in an intersection video with Ultralytics YOLO."
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
        help="Comma-separated COCO class IDs to detect. Defaults to 0,1,2,3,5,7.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Detection confidence threshold. Defaults to 0.25.",
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


def write_detection_rows(
    *,
    results: Iterable[Any],
    detections_path: Path,
    video_id: str,
    fps: float,
    model_names: Any,
) -> tuple[int, Path | None]:
    """Consume detection results frame by frame and write detection rows."""
    rows_written = 0
    save_dir: Path | None = None

    with detections_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=DETECTION_COLUMNS)
        writer.writeheader()

        for frame_idx, result in enumerate(results):
            result_save_dir = getattr(result, "save_dir", None)
            if result_save_dir is not None:
                save_dir = Path(result_save_dir)

            boxes = getattr(result, "boxes", None)
            if boxes is None or boxes.cls is None:
                continue

            class_ids = [int(cls_id) for cls_id in as_python_list(boxes.cls)]
            confidences = [float(conf) for conf in as_python_list(boxes.conf)]
            xywh_values = as_python_list(boxes.xywh)
            timestamp_sec = frame_idx / fps

            for cls_id, conf, xywh in zip(
                class_ids, confidences, xywh_values, strict=True
            ):
                x, y, w, h = (float(value) for value in xywh)
                writer.writerow(
                    {
                        "video_id": video_id,
                        "frame_idx": frame_idx,
                        "timestamp_sec": timestamp_sec,
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


def build_detection_summary(detections_path: Path, summary_path: Path) -> int:
    """Create a per-class detection-count summary CSV from detections.csv."""
    import pandas as pd

    detections = pd.read_csv(detections_path)
    if detections.empty:
        pd.DataFrame(columns=SUMMARY_COLUMNS).to_csv(summary_path, index=False)
        return 0

    summary = (
        detections.groupby(["cls_id", "cls_name"], as_index=False)
        .agg(num_detections=("frame_idx", "size"))
        .sort_values(["cls_name", "cls_id"])
    )
    summary.to_csv(summary_path, index=False, columns=SUMMARY_COLUMNS)
    return int(summary["num_detections"].sum())


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


def summary_lines(summary_path: Path, duration_sec: float) -> list[str]:
    """Build the human-readable detection summary."""
    import pandas as pd

    summary = pd.read_csv(summary_path)
    total_detections = int(summary["num_detections"].sum()) if not summary.empty else 0
    lines = [
        "Detection complete",
        f"Total detections: {total_detections}",
        f"Duration: {duration_sec:.2f} sec",
        "Per-class detection counts:",
    ]

    if summary.empty:
        return [*lines, "  none: 0"]

    return [
        *lines,
        *(
            f"  {row.cls_name}: {int(row.num_detections)}"
            for row in summary.itertuples(index=False)
        ),
    ]


def write_summary(summary_path: Path, report_path: Path, duration_sec: float) -> None:
    """Write the console-style detection summary to disk."""
    report_path.write_text("\n".join(summary_lines(summary_path, duration_sec)) + "\n")


def print_summary(summary_path: Path, duration_sec: float) -> None:
    """Print total detections, per-class detection counts, and video duration."""
    print()
    for line in summary_lines(summary_path, duration_sec):
        print(line)


def default_output_dir(video_path: Path) -> Path:
    """Return the default output directory for an input video."""
    return Path("outputs") / video_path.stem


def run(args: argparse.Namespace) -> None:
    """Run the full detection pipeline."""
    from ultralytics import YOLO

    video_path = args.video_path.expanduser().resolve()
    output_dir = args.output_dir if args.output_dir is not None else default_output_dir(video_path)
    output_dir = output_dir.expanduser().resolve()

    if not video_path.exists():
        raise FileNotFoundError(f"Input video does not exist: {video_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = get_video_metadata(video_path)

    detections_path = output_dir / "detections.csv"
    summary_path = output_dir / "detection_summary.csv"
    report_path = output_dir / "summary.txt"

    model = YOLO(args.model)
    results = model.predict(
        source=str(video_path),
        stream=True,
        classes=args.classes,
        device=args.device,
        conf=args.conf,
        save=True,
        project=str(output_dir.parent),
        name=output_dir.name,
        exist_ok=True,
    )

    _, save_dir = write_detection_rows(
        results=results,
        detections_path=detections_path,
        video_id=video_path.stem,
        fps=metadata.fps,
        model_names=model.names,
    )
    build_detection_summary(detections_path, summary_path)
    place_annotated_video(save_dir, output_dir, video_path)
    write_summary(summary_path, report_path, metadata.duration_sec)
    print_summary(summary_path, metadata.duration_sec)


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point."""
    args = parse_args(argv)
    run(args)


if __name__ == "__main__":
    main()
