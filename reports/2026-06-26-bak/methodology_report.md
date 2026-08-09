# Methodology

We analyzed a 1-minute segment of traffic video captured at the Hillside at North Eagleville northbound intersection. 
The recording started at 7:00 AM on April 6, 2026.
The clip covers video timeline `10:00:00` to `10:01:00`. this corresponds to the wall-clock interval from 5:00:00 PM to 5:01:00 PM. This specific timeframe was selected because it represented the busiest period observed at that intersection. 
Using the YOLO11 object detection model together with BoT-SORT tracking, we detected and linked individual road users frame by frame throughout the segment. 

## Detection and Tracking

Object detection in each video frame was performed using the YOLO model, which is configured to recognize key COCO categories for traffic analysis: `person`, `bicycle`, `car`, `motorcycle`, `bus`, and `truck`. The BoT-SORT tracker then linked these detections across frames, creating continuous object tracks. This approach enables us to count the number of unique road user trajectories that occurred during the clip.

## False Label Filtering

To improve the accuracy of the track summary, we implemented two measures. First, each track is assigned the most frequent (majority) class label observed across its detections, rather than relying on the initial class label. Second, the summary excludes tracks with fewer than five detections by default, filtering out short-lived or spurious results such as single-frame misclassifications.

## Count Interpretation and Initial Findings

The reported totals are filtered track counts, not guaranteed real-world object counts. For example, `car: 29` means 29 car-class trajectories passed the filtering rule, but a real vehicle may be split into multiple tracks if it is occluded or briefly missed. For this clip, the filtered summary reports one bus track, twenty-nine car tracks, and twelve person tracks.

## Recommended Next Steps

Review the annotated video against the CSV outputs to validate the filtered counts. Then run the same workflow on additional clips and consider adding line-crossing or zone-based counting if the goal is directional traffic volume rather than general object presence.
