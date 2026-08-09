"""Trim clips from long camera recordings with FFmpeg."""

from __future__ import annotations

import argparse
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


def parse_clock(text: str) -> float:
    """Parse HH:MM:SS, MM:SS, H:MM:SS.mmm, or plain seconds."""
    text = text.strip()
    if re.fullmatch(r"\d+(\.\d+)?", text):
        return float(text)

    parts = text.split(":")
    if not 1 <= len(parts) <= 3:
        raise argparse.ArgumentTypeError(f"bad time {text!r}; use HH:MM:SS or seconds")

    try:
        values = [float(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"bad time {text!r}; use HH:MM:SS or seconds"
        ) from exc

    while len(values) < 3:
        values.insert(0, 0.0)
    hours, minutes, seconds = values
    return hours * 3600 + minutes * 60 + seconds


def format_clock(seconds: float) -> str:
    """Format seconds as H:MM:SS."""
    rounded_seconds = int(round(seconds))
    hours, remainder = divmod(rounded_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def format_tag(seconds: float) -> str:
    """Format seconds as a filename-safe tag like 10h00m00s."""
    rounded_seconds = int(round(seconds))
    hours, remainder = divmod(rounded_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}h{minutes:02d}m{seconds:02d}s"


def format_length(seconds: float) -> str:
    """Format a clip length for the sidecar trim log."""
    rounded_seconds = int(round(seconds))
    if rounded_seconds < 60:
        return f"{rounded_seconds} seconds"
    return f"{rounded_seconds} seconds ({format_clock(rounded_seconds)})"


def recording_start_from_name(path: Path) -> tuple[float | None, str | None]:
    """Read a wall-clock start time from camera filenames with h/min/s markers."""
    match = re.search(
        r"(\d{1,2})h(\d{1,2})min(\d{1,2})s(?:(\d{1,3})ms)?",
        path.name,
    )
    if match is None:
        return None, None

    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    milliseconds = int(match.group(4)) if match.group(4) else 0
    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    return total_seconds, f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def clean_video_stem(path: Path) -> str:
    """Strip the extension and trailing recording timestamp from a video filename."""
    stem = path.stem
    stem = re.sub(
        r"-\d{4}-\d{2}-\d{2}_\d{1,2}h\d{1,2}min\d{1,2}s\d{0,3}ms?$",
        "",
        stem,
    )
    return stem.strip()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Build and parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Losslessly trim a clip from a recording and write a trim-log .txt."
    )
    parser.add_argument("source", type=Path, help="Path to the source video.")
    parser.add_argument("start", type=parse_clock, help="Start time as HH:MM:SS or seconds.")
    parser.add_argument(
        "end",
        type=parse_clock,
        nargs="?",
        help="End time as HH:MM:SS or seconds.",
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=parse_clock,
        help="Clip length, as HH:MM:SS or seconds. Alternative to end.",
    )
    parser.add_argument(
        "-w",
        "--wallclock",
        action="store_true",
        help="Interpret start/end as wall-clock time of day.",
    )
    parser.add_argument(
        "--start-time",
        type=parse_clock,
        metavar="HH:MM:SS",
        help="Override the recording's wall-clock start time.",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--output-dir",
        dest="output_dir",
        type=Path,
        default=Path("trimmed"),
        help="Directory for the clipped video and trim log. Defaults to trimmed/.",
    )
    parser.add_argument(
        "--reencode",
        action="store_true",
        help="Re-encode for frame-accurate cuts. Defaults to lossless stream copy.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without running FFmpeg.",
    )
    return parser.parse_args(argv)


def resolve_trim_range(args: argparse.Namespace) -> tuple[float, float, float, str | None]:
    """Resolve CLI start/end values to offsets into the source file."""
    if args.end is None and args.duration is None:
        raise ValueError("give either an end time or --duration")
    if args.end is not None and args.duration is not None:
        raise ValueError("give only one of end / --duration")

    if args.start_time is not None:
        recording_start_seconds = args.start_time
        recording_start_human = format_clock(args.start_time)
    else:
        recording_start_seconds, recording_start_human = recording_start_from_name(args.source)

    if args.wallclock:
        if recording_start_seconds is None:
            raise ValueError(
                "--wallclock needs the recording start time; none found in filename, "
                "pass --start-time HH:MM:SS"
            )
        start_offset = args.start - recording_start_seconds
        end_offset = args.end - recording_start_seconds if args.end is not None else None
    else:
        start_offset = args.start
        end_offset = args.end

    if end_offset is not None:
        duration = end_offset - start_offset
    else:
        duration = args.duration
        end_offset = start_offset + duration

    if start_offset < 0:
        raise ValueError(
            f"start is before the recording began (offset {format_clock(start_offset)})"
        )
    if duration <= 0:
        raise ValueError(f"end must be after start (got length {duration} s)")

    return start_offset, end_offset, duration, recording_start_human


def build_ffmpeg_command(
    *,
    source: Path,
    output_path: Path,
    start_offset: float,
    duration: float,
    reencode: bool,
) -> list[str]:
    """Build the FFmpeg command used to produce the clip."""
    command = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{start_offset:.3f}",
        "-i",
        str(source),
        "-t",
        f"{duration:.3f}",
    ]
    if reencode:
        command += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac"]
    else:
        command += ["-c", "copy"]
    command += ["-avoid_negative_ts", "make_zero", str(output_path)]
    return command


def resolve_output_paths(
    *,
    args: argparse.Namespace,
    source: Path,
    start_offset: float,
    end_offset: float,
) -> tuple[Path, Path]:
    """Resolve the default clip and log filenames in the selected output directory."""
    output_dir = args.output_dir.expanduser().resolve()
    stem = clean_video_stem(source)
    tag = f"{format_tag(start_offset)}-{format_tag(end_offset)}"
    output_stem = f"{stem}_trim_{tag}"
    output_run_dir = output_dir / output_stem
    output_path = output_run_dir / f"{output_stem}{source.suffix}"
    return output_path, output_run_dir / f"{output_stem}.txt"


def write_trim_log(
    *,
    log_path: Path,
    args: argparse.Namespace,
    output_name: str,
    start_offset: float,
    end_offset: float,
    duration: float,
    recording_start_human: str | None,
    method: str,
) -> None:
    """Write a small sidecar text file documenting the trim."""
    lines = [
        "Trim log",
        "=========",
        "",
        f"Source video : {args.source.name}",
        f"Output clip  : {output_name}",
        "",
        "Trimmed range (video timeline / position into the file):",
        f"  Start : {format_clock(start_offset)}",
        f"  End   : {format_clock(end_offset)}",
        f"  Length: {format_length(duration)}",
        "",
    ]

    if args.wallclock:
        end_wallclock = args.end if args.end is not None else args.start + duration
        lines += [
            "Wall-clock range (real time of day):",
            f"  Start : {format_clock(args.start)}",
            f"  End   : {format_clock(end_wallclock)}",
            "",
        ]

    note = "Source file left intact."
    if recording_start_human:
        hours_in = int(start_offset // 3600)
        note += (
            f" Range refers to the {hours_in}-hour mark of the recording\n"
            f"         (the recording itself began at {recording_start_human} wall-clock time)."
        )

    lines += [
        f"Method : {method}",
        f"Note   : {note}",
        "",
    ]
    log_path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    """Trim the requested clip and write a sidecar log."""
    source = args.source.expanduser().resolve()
    args.source = source

    if not source.is_file():
        raise FileNotFoundError(f"source not found: {source}")

    start_offset, end_offset, duration, recording_start_human = resolve_trim_range(args)
    output_path, log_path = resolve_output_paths(
        args=args,
        source=source,
        start_offset=start_offset,
        end_offset=end_offset,
    )
    command = build_ffmpeg_command(
        source=source,
        output_path=output_path,
        start_offset=start_offset,
        duration=duration,
        reencode=args.reencode,
    )
    method = (
        "re-encode (frame-accurate)"
        if args.reencode
        else "stream copy (lossless, no re-encode)"
    )

    print(f"Source : {source}")
    print(f"Output : {output_path}")
    print(
        f"Offset into file : {format_clock(start_offset)} -> {format_clock(end_offset)} "
        f"(length {format_length(duration)})"
    )
    if args.wallclock:
        end_wallclock = args.end if args.end is not None else args.start + duration
        print(f"Wall-clock range : {format_clock(args.start)} -> {format_clock(end_wallclock)}")
    print(f"Method : {method}")

    if args.dry_run:
        print("\n[dry-run] would run:\n  " + " ".join(shlex.quote(part) for part in command))
        return

    if shutil.which("ffmpeg") is None:
        raise FileNotFoundError("ffmpeg is not installed or is not available on PATH")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("\nRunning ffmpeg...")
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed (exit {result.returncode})")

    write_trim_log(
        log_path=log_path,
        args=args,
        output_name=output_path.name,
        start_offset=start_offset,
        end_offset=end_offset,
        duration=duration,
        recording_start_human=recording_start_human,
        method=method,
    )
    print(f"\nDone.\n  clip : {output_path}\n  log  : {log_path}")


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point."""
    args = parse_args(argv)
    try:
        run(args)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        sys.exit(str(exc))


if __name__ == "__main__":
    main()
