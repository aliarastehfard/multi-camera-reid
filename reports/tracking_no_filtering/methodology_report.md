# Tracking Methodology Without Post-Processing Filters

We analyzed seven 1-minute traffic video clips captured at the Hillside at North Eagleville northbound camera. The clips cover April 6 through April 12, 2026.
Each source recording started at 7:00 AM. The analyzed clip window covers video timeline `10:00:00` to `10:01:00`, corresponding to the wall-clock interval from 5:00:00 PM to 5:01:00 PM. This timeframe was selected because it represented the busiest period observed at that intersection.
Using the YOLO11 object detection model together with BoT-SORT tracking, we detected and linked individual road users frame by frame throughout each segment.

## Detection and Tracking

Object detection in each video frame was performed using YOLO11 through Ultralytics. The model was configured to recognize key COCO categories for traffic analysis: `person`, `bicycle`, `car`, `motorcycle`, `bus`, and `truck`.

BoT-SORT then linked YOLO11 detections across frames, creating continuous object tracks. This tracking step is needed because YOLO11 alone detects objects independently in each frame and does not know whether a vehicle or pedestrian in one frame is the same object in the next frame.

## No-Filtering Configuration

This run intentionally disabled the two track-summary post-processing choices used in the filtered tracking report.

First, the minimum track-length filter was disabled by setting `--min-summary-detections 1`. This means tracks were counted even if they appeared in only one frame. As a result, short-lived tracks and possible false positives remain in the summary.

Second, majority class labeling was disabled by setting `--summary-class-label first`. Each track summary row uses the first class label observed for that track rather than the most frequent label across the full track. This makes the output closer to the raw tracker summary, but it can preserve early misclassifications when an object's label changes over time.

## Count Interpretation

The reported totals are unfiltered track counts, not guaranteed real-world object counts. Compared with the filtered tracking report, these counts are expected to be higher because one-frame and short-lived tracks are included. Some of these additional tracks may represent real but brief appearances, while others may be false positives, fragmented tracks, or temporary ID switches caused by occlusion and missed detections.

This no-filtering run is useful as a sensitivity check. It shows how much the final traffic counts depend on post-processing choices such as minimum track duration and majority label assignment.

## No-Filtering Tracking Results

Across the seven analyzed clips, the no-filtering tracking summaries report 360 counted tracks in total:

- `car`: 261 tracks
- `person`: 72 tracks
- `truck`: 20 tracks
- `bus`: 7 tracks

Per-day unfiltered track totals:

- April 6, 2026: 53 total tracks; 33 car, 17 person, 3 truck.
- April 7, 2026: 51 total tracks; 34 car, 14 person, 2 truck, 1 bus.
- April 8, 2026: 52 total tracks; 44 car, 3 person, 5 truck.
- April 9, 2026: 68 total tracks; 57 car, 4 person, 4 bus, 3 truck.
- April 10, 2026: 76 total tracks; 48 car, 24 person, 2 bus, 2 truck.
- April 11, 2026: 41 total tracks; 29 car, 10 person, 2 truck.
- April 12, 2026: 19 total tracks; 16 car, 3 truck.

## Comparison to Filtered Tracking

The filtered tracking report counted 256 tracks after excluding tracks with fewer than five detections and assigning each track its majority class label. The no-filtering run counted 360 tracks. The difference of 104 tracks shows that the post-processing filters remove a meaningful number of short or unstable trajectories.

## Recommended Next Steps

Review the no-filtering annotated videos and compare them against the filtered tracking outputs. Short tracks that correspond to real road users may indicate that the filtering threshold is too strict, while short tracks caused by flickering detections or ID fragmentation support keeping the filter in place.
