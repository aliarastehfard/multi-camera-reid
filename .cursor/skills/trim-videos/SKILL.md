---
name: trim-videos
description: Trim all videos in a directory with this repository's trim-video utility. Use when the user provides a video directory path and asks to trim videos, cut clips, extract time ranges, or process prompt-provided timeframes for video files.
---

# Trim Videos

## Purpose

Use this skill to trim every video in a user-provided directory using the repository's `trim-video` CLI, which is implemented by `utilities.trim_video`.

## Required Prompt Inputs

Before running trims, identify these inputs from the user's prompt:

- Video directory path.
- Start time.
- Either end time or duration.
- Whether times are video timeline offsets or wall-clock times.

If any required input is missing or ambiguous, ask for it before trimming.

## Command Pattern

Run commands from the repository root.

Use `trim-video` when available:

```bash
trim-video "SOURCE_VIDEO" "START" "END_OR_DURATION" --output "OUTPUT_DIR"
```

If the console script is not on `PATH`, use the module directly:

```bash
python -m utilities.trim_video "SOURCE_VIDEO" "START" "END_OR_DURATION" --output "OUTPUT_DIR"
```

For a duration instead of an end time:

```bash
trim-video "SOURCE_VIDEO" "START" --duration "DURATION" --output "OUTPUT_DIR"
```

For wall-clock times:

```bash
trim-video "SOURCE_VIDEO" "START" "END" --wallclock --output "OUTPUT_DIR"
```

If the source filename does not include the recording start time and wall-clock times are requested, include:

```bash
--start-time "HH:MM:SS"
```

## Workflow

1. Confirm the directory exists and list supported video files in it.
2. Use only regular video files with extensions such as `.mp4`, `.mov`, `.mkv`, `.avi`, `.m4v`, or `.webm`.
3. Derive the intersection name, camera name, recording date, and timeframe tag from the prompt and/or source filename.
4. Build one `trim-video` command per source video.
5. First run each command with `--dry-run` unless the user explicitly asks to execute immediately.
6. If dry runs resolve the expected offset, duration, and output path, run the same commands without `--dry-run`.
7. Report the generated clip and trim-log paths.

## Output Path Convention

Output paths must include the intersection name, camera name, recording date, and timeframe.

Use this final directory pattern:

```text
trimmed/INTERSECTION_NAME/CAMERA_NAME/DATE/TIMEFRAME/
```

The trimmed `.mp4` and `.txt` trim log should live directly inside the `TIMEFRAME/` directory. Do not leave an extra generated folder like `SOURCE_NAME_trim_TIMEFRAME/` inside the timeframe folder.

Because the trim utility creates a clip-specific subfolder inside `--output`, run it into the timeframe directory, then move the generated `.mp4` and `.txt` files up one level and remove the empty generated subfolder.

For a source named:

```text
0043 Road - Hillside @ N. Eagleville Northbound-2026-04-06_07h00min00s000ms.mp4
```

and video timeline `10:00:00` to `10:01:00`, use:

```text
trimmed/Hillside @ N. Eagleville/Northbound/2026-04-06/10h00m00s-10h01m00s/
```

Final contents should look like:

```text
trimmed/Hillside @ N. Eagleville/Northbound/2026-04-06/10h00m00s-10h01m00s/
├── 0043 Road - Hillside @ N. Eagleville Northbound_trim_10h00m00s-10h01m00s.mp4
└── 0043 Road - Hillside @ N. Eagleville Northbound_trim_10h00m00s-10h01m00s.txt
```

## Defaults

- Use `trimmed/INTERSECTION_NAME/CAMERA_NAME/DATE/TIMEFRAME/` unless the user provides another output directory.
- Prefer stream-copy trimming, which is lossless and does not re-encode.
- Use `--reencode` only when the user requests frame-accurate cuts or the stream-copy output is unsuitable.
- Leave source videos unchanged.

## Safety Notes

- Quote all paths, especially video filenames with spaces.
- Do not invent missing times, dates, or recording start times.
- Do not delete or overwrite source videos.
- If a command fails because `ffmpeg` is missing, report that `ffmpeg` must be installed or added to `PATH`.
