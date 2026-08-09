# Detection-Only Methodology

We analyzed seven 1-minute traffic video clips captured at the Hillside at North Eagleville northbound camera. The clips cover April 6 through April 12, 2026.
Each source recording started at 7:00 AM. The analyzed clip window covers video timeline `10:00:00` to `10:01:00`, corresponding to the wall-clock interval from 5:00:00 PM to 5:01:00 PM. This timeframe was selected because it represented the busiest period observed at that intersection.
Using the YOLO11 object detection model, we detected visible road users independently in each video frame. No multi-object tracker was used in this detection-only run.

## Detection Setup

Object detection in each video frame was performed using YOLO11 through Ultralytics `predict` mode. The model was configured to detect the COCO traffic-related classes `person`, `bicycle`, `car`, `motorcycle`, `bus`, and `truck`.

For each detection, YOLO11 outputs a class label, confidence score, and bounding box location. The exported `detections.csv` files store these values with the video name, frame index, timestamp, class ID, class name, confidence, and pixel-space bounding box coordinates (`x`, `y`, `w`, `h`).

## YOLO11 Parameters

The detection-only run used `yolo11n.pt`, the nano YOLO11 model. This model is fast and lightweight, which is useful for processing video clips quickly, but it can be less accurate than larger YOLO11 variants.

The confidence threshold was set to `conf=0.25`. This means YOLO11 only keeps detections whose predicted confidence score is at least 0.25. Lowering this threshold would keep more uncertain detections but may introduce more false positives. Raising it would make the detections stricter but may miss small, partially occluded, or distant road users.

The class filter was set to `classes=0,1,2,3,5,7`, corresponding to `person`, `bicycle`, `car`, `motorcycle`, `bus`, and `truck` in the COCO label set. This removes non-traffic objects from the output.

## Count Interpretation

The reported totals are frame-level detection counts, not unique road-user counts. For example, if the same car is visible across 100 frames, it can contribute approximately 100 `car` detections. This makes detection-only counts useful for understanding model activity and visual object presence, but not for estimating the number of unique vehicles or pedestrians passing through the scene.

This is the main difference from the tracking pipeline. YOLO11 detection answers "what objects are visible in this frame?" while YOLO11 plus BoT-SORT tracking attempts to answer "which detections across frames belong to the same object?"

## Detection Results

Across the seven analyzed clips, the detection-only summaries report 21,340 frame-level detections in total:

- `car`: 17,517 detections
- `person`: 2,509 detections
- `bus`: 909 detections
- `truck`: 399 detections
- `bicycle`: 4 detections
- `motorcycle`: 2 detections

Per-day frame-level detection totals:

- April 6, 2026: 4,146 total detections; 3,459 car, 626 person, 36 bus, 23 truck, 2 motorcycle.
- April 7, 2026: 3,426 total detections; 2,414 car, 845 person, 115 bus, 52 truck.
- April 8, 2026: 2,101 total detections; 1,744 car, 206 person, 151 truck.
- April 9, 2026: 2,840 total detections; 2,416 car, 261 bus, 104 person, 59 truck.
- April 10, 2026: 5,812 total detections; 4,650 car, 628 person, 490 bus, 40 truck, 4 bicycle.
- April 11, 2026: 2,109 total detections; 1,983 car, 100 person, 26 truck.
- April 12, 2026: 906 total detections; 851 car, 48 truck, 7 bus.

## Recommended Next Steps

Review the annotated detection-only videos against the CSV outputs to identify obvious false positives and missed detections. Use these results as a baseline for comparison with the tracking pipeline, where BoT-SORT converts repeated frame-level detections into object-level trajectories.
