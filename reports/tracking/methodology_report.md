# Methodology

We analyzed seven 1-minute traffic video clips captured at the Hillside at North Eagleville northbound camera. The clips cover April 6 through April 12, 2026.
Each source recording started at 7:00 AM. The analyzed clip window covers video timeline `10:00:00` to `10:01:00`, corresponding to the wall-clock interval from 5:00:00 PM to 5:01:00 PM. This timeframe was selected because it represented the busiest period observed at that intersection.
Using the YOLO11 object detection model together with BoT-SORT tracking, we detected and linked individual road users frame by frame throughout each segment.

## Detection and Tracking

Object detection in each video frame was performed using the YOLO model, which is configured to recognize key COCO categories for traffic analysis: `person`, `bicycle`, `car`, `motorcycle`, `bus`, and `truck`. The BoT-SORT tracker then linked these detections across frames, creating continuous object tracks. This approach enables us to count the number of unique road user trajectories that occurred during each clip.

## False Label Filtering

To improve the accuracy of the track summary, we implemented two measures. First, each track is assigned the most frequent (majority) class label observed across its detections, rather than relying on the initial class label. Second, the summary excludes tracks with fewer than five detections by default, filtering out short-lived or spurious results such as single-frame misclassifications.

## Count Interpretation and Initial Findings

The reported totals are filtered track counts, not guaranteed real-world object counts. For example, `car: 29` means 29 car-class trajectories passed the filtering rule, but a real vehicle may be split into multiple tracks if it is occluded or briefly missed.

Across the seven analyzed clips, the filtered summaries report 256 counted tracks in total:

- `car`: 205 tracks
- `person`: 35 tracks
- `truck`: 9 tracks
- `bus`: 7 tracks

Per-day filtered track totals:

- April 6, 2026: 37 total tracks; 28 car, 8 person, 1 bus.
- April 7, 2026: 39 total tracks; 28 car, 9 person, 1 bus, 1 truck.
- April 8, 2026: 38 total tracks; 33 car, 1 person, 4 truck.
- April 9, 2026: 48 total tracks; 42 car, 3 person, 3 bus.
- April 10, 2026: 55 total tracks; 39 car, 12 person, 2 bus, 2 truck.
- April 11, 2026: 27 total tracks; 24 car, 2 person, 1 truck.
- April 12, 2026: 12 total tracks; 11 car, 1 truck.

## Recommended Next Steps

Review the annotated videos against the CSV outputs to validate the filtered counts. Then consider adding line-crossing or zone-based counting if the goal is directional traffic volume rather than general object presence.
