# Utilities

Small helper CLIs for preparing traffic video inputs.

## Trim Video Clips

Use `trim-video` to cut a shorter clip from a long camera recording before
running tracking. The original video is left unchanged. By default, each trimmed
clip and its `.txt` trim log are written to their own generated subfolder under
`trimmed/`.

FFmpeg must be installed and available on your `PATH`.

Trim by position in the video timeline:

```bash
uv run trim-video path/to/intersection.mp4 10:00:00 10:00:30
```

This writes files under a generated folder like
`trimmed/intersection_trim_10h00m00s-10h00m30s/`.

Trim by duration:

```bash
uv run trim-video path/to/intersection.mp4 10:00:00 --duration 30
```

Re-encode for a frame-accurate trim:

```bash
uv run trim-video path/to/intersection.mp4 10:00:00 10:00:30 --reencode
```

By default, `trim-video` uses FFmpeg stream copy, which is fast and lossless but
may include extra frames around nearby keyframes. Use `--reencode` when the clip
duration needs to match the requested range more closely.

For filenames that include a recording start timestamp like
`2026-04-06_07h00min00s000ms`, trim by wall-clock time:

```bash
uv run trim-video path/to/intersection.mp4 17:00:00 17:00:30 --wallclock
```

### CLI Arguments

```bash
uv run trim-video [-h] [-d DURATION] [-w] [--start-time HH:MM:SS]
                  [-o OUTPUT_DIR] [--reencode] [--dry-run]
                  source start [end]
```

Positional arguments:

- `source`: path to the source video.
- `start`: start time as `HH:MM:SS`, `MM:SS`, or seconds.
- `end`: optional end time, using the same format as `start`.

Options:

- `-d, --duration DURATION`: clip length instead of `end`.
- `-w, --wallclock`: interpret `start` and `end` as wall-clock time of day.
- `--start-time HH:MM:SS`: manually set the recording wall-clock start time.
- `-o, --output, --output-dir OUTPUT_DIR`: parent output directory, defaults to `trimmed/`.
- `--reencode`: re-encode for frame-accurate cuts.
- `--dry-run`: print the FFmpeg command without running it.
- `-h, --help`: show help.
