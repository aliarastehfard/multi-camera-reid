"""Load and validate ReID batch job specs from CSV."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


REQUIRED_COLUMNS = ("camera_name", "video")


@dataclass(frozen=True)
class ReIDJob:
    """One intersection/camera video to track and export."""

    camera_name: str
    video: Path
    tracks_dir: Path | None = None

    def resolved_tracks_dir(self, default_root: Path) -> Path:
        """Return tracks output directory for this job."""
        if self.tracks_dir is not None:
            return self.tracks_dir
        return default_root / self.camera_name


def load_jobs(jobs_path: Path) -> list[ReIDJob]:
    """Load ReID jobs from a CSV file with camera_name,video[,tracks_dir]."""
    if not jobs_path.exists():
        raise FileNotFoundError(f"Jobs file does not exist: {jobs_path}")

    with jobs_path.open(newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"Jobs CSV has no header row: {jobs_path}")

        fieldnames = [name.strip() for name in reader.fieldnames]
        missing = [col for col in REQUIRED_COLUMNS if col not in fieldnames]
        if missing:
            raise ValueError(
                f"Jobs CSV missing required columns {missing}. "
                f"Found: {fieldnames}"
            )

        jobs: list[ReIDJob] = []
        seen_cameras: set[str] = set()

        for row_number, row in enumerate(reader, start=2):
            camera_name = (row.get("camera_name") or "").strip()
            video_raw = (row.get("video") or "").strip()
            tracks_raw = (row.get("tracks_dir") or "").strip()

            if not camera_name:
                raise ValueError(f"Row {row_number}: camera_name is required")
            if not video_raw:
                raise ValueError(f"Row {row_number}: video is required")
            if camera_name in seen_cameras:
                raise ValueError(
                    f"Row {row_number}: duplicate camera_name {camera_name!r}"
                )

            video_path = Path(video_raw).expanduser()
            if not video_path.is_absolute():
                video_path = video_path.resolve()
            else:
                video_path = video_path.resolve()

            if not video_path.exists():
                raise FileNotFoundError(
                    f"Row {row_number}: video does not exist: {video_path}"
                )

            tracks_dir: Path | None = None
            if tracks_raw:
                tracks_dir = Path(tracks_raw).expanduser().resolve()

            seen_cameras.add(camera_name)
            jobs.append(
                ReIDJob(
                    camera_name=camera_name,
                    video=video_path,
                    tracks_dir=tracks_dir,
                )
            )

    if not jobs:
        raise ValueError(f"Jobs CSV contains no data rows: {jobs_path}")

    return jobs
