# Cross-Camera Vehicle ReID — N. Eagleville @ Hillside

**Site / date:** North Eagleville at Hillside, 2026-04-06  
**Clip window:** first 30 seconds of each camera view  
**Goal:** match the same vehicle across cameras using appearance only

## Models Used

| Stage | Model | Role |
|-------|-------|------|
| Detection | YOLO11 | Detect vehicles in each frame |
| Tracking | BoT-SORT | Link detections into per-camera tracks |
| ReID embedding | ResNet101-IBN (ImageNet pretrained) | Embed one crop per track |
| Matching | Cosine similarity, top-5 | Rank cross-camera candidates (same camera excluded) |

## Dataset Preparation

1. **Trim** four synchronized camera clips to `00h00m00s–00h00m30s` (Eastbound, Northbound, Westbound, SE Corner).
2. **Track** each clip with YOLO11 + BoT-SORT (vehicle classes).
3. **Export** one representative JPEG per track: the highest-confidence vehicle crop (`export-reid-thumbs` / `prepare-reid-batch`).
4. **Gallery build:** all crops land in one shared folder with AIC-style names `{Camera}_{videoStem}_{trackId}.jpg`, plus a combined `manifest.csv`.

**Gallery size:** 29 vehicle tracks across 4 cameras.

| Camera | Tracks |
|--------|--------|
| Eastbound | 9 |
| Northbound | 8 |
| SECorner | 10 |
| Westbound | 2 |

## Results

Each query track is compared to tracks from **other cameras only**. Below, every query shows the original crop and its top-5 matches, captioned with track ID and cosine score.

**Summary statistics (top-1 score per query):**

- Mean top-1 cosine: **0.8806** (min 0.7368, max 0.9399)
- Top-1 ≥ 0.90: **12/29** queries
- Top-1 ≥ 0.85: **23/29** queries
- Reciprocal top-1 pairs (A→B and B→A): **5**

**How to read the figures:** high scores mean similar appearance, not proven identity. Without labeled ground truth, some strong matches may still be false positives (similar color/shape vehicles).

## Eastbound — top-5 matches

### Eastbound track#1 (0042)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_1.jpg" alt="query" width="140"/><br/><sub>Eastbound track#1 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.9316</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.9116</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.9035</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_53.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#53 (0043)<br/>0.8835</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8799</sub></td>
</tr></table>

### Eastbound track#2 (0042)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="query" width="140"/><br/><sub>Eastbound track#2 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.9162</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.9058</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.9026</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_53.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#53 (0043)<br/>0.8996</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.8922</sub></td>
</tr></table>

### Eastbound track#3 (0042)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="query" width="140"/><br/><sub>Eastbound track#3 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.9261</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.9253</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.9147</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.8900</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8884</sub></td>
</tr></table>

### Eastbound track#7 (0042)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_7.jpg" alt="query" width="140"/><br/><sub>Eastbound track#7 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.8946</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8918</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.8894</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8795</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8654</sub></td>
</tr></table>

### Eastbound track#9 (0042)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_9.jpg" alt="query" width="140"/><br/><sub>Eastbound track#9 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.9103</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.9087</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.9063</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8993</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8870</sub></td>
</tr></table>

### Eastbound track#13 (0042)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="query" width="140"/><br/><sub>Eastbound track#13 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.9399</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.9234</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.9139</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.9005</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8985</sub></td>
</tr></table>

### Eastbound track#14 (0042)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_14.jpg" alt="query" width="140"/><br/><sub>Eastbound track#14 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_53.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#53 (0043)<br/>0.8519</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.8493</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8412</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8392</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.8313</sub></td>
</tr></table>

### Eastbound track#17 (0042)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_17.jpg" alt="query" width="140"/><br/><sub>Eastbound track#17 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.8678</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8613</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8465</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_45.jpg" alt="rank-4" width="140"/><br/><sub>SECorner track#45 (Public)<br/>0.8370</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.8368</sub></td>
</tr></table>

### Eastbound track#24 (0042)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_24.jpg" alt="query" width="140"/><br/><sub>Eastbound track#24 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_45.jpg" alt="rank-1" width="140"/><br/><sub>SECorner track#45 (Public)<br/>0.8115</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_37.jpg" alt="rank-2" width="140"/><br/><sub>SECorner track#37 (Public)<br/>0.8110</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_107.jpg" alt="rank-3" width="140"/><br/><sub>SECorner track#107 (Public)<br/>0.8099</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8021</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_113.jpg" alt="rank-5" width="140"/><br/><sub>SECorner track#113 (Public)<br/>0.7957</sub></td>
</tr></table>

## Northbound — top-5 matches

### Northbound track#1 (0043)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="query" width="140"/><br/><sub>Northbound track#1 (0043)</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_1.jpg" alt="rank-1" width="140"/><br/><sub>Eastbound track#1 (0042)<br/>0.9316</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="rank-2" width="140"/><br/><sub>Eastbound track#13 (0042)<br/>0.9234</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="rank-3" width="140"/><br/><sub>Eastbound track#3 (0042)<br/>0.9147</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_9.jpg" alt="rank-4" width="140"/><br/><sub>Eastbound track#9 (0042)<br/>0.9103</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="rank-5" width="140"/><br/><sub>Eastbound track#2 (0042)<br/>0.9058</sub></td>
</tr></table>

### Northbound track#2 (0043)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="query" width="140"/><br/><sub>Northbound track#2 (0043)</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="rank-1" width="140"/><br/><sub>Eastbound track#3 (0042)<br/>0.9253</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="rank-2" width="140"/><br/><sub>Eastbound track#2 (0042)<br/>0.9026</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="rank-3" width="140"/><br/><sub>Eastbound track#13 (0042)<br/>0.9005</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_9.jpg" alt="rank-4" width="140"/><br/><sub>Eastbound track#9 (0042)<br/>0.8993</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_7.jpg" alt="rank-5" width="140"/><br/><sub>SECorner track#7 (Public)<br/>0.8990</sub></td>
</tr></table>

### Northbound track#4 (0043)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="query" width="140"/><br/><sub>Northbound track#4 (0043)</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_37.jpg" alt="rank-1" width="140"/><br/><sub>SECorner track#37 (Public)<br/>0.9094</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="rank-2" width="140"/><br/><sub>Eastbound track#13 (0042)<br/>0.8985</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="rank-3" width="140"/><br/><sub>Eastbound track#2 (0042)<br/>0.8916</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_7.jpg" alt="rank-4" width="140"/><br/><sub>SECorner track#7 (Public)<br/>0.8901</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="rank-5" width="140"/><br/><sub>Eastbound track#3 (0042)<br/>0.8884</sub></td>
</tr></table>

### Northbound track#5 (0043)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Northbound_5.jpg" alt="query" width="140"/><br/><sub>Northbound track#5 (0043)</sub></td>
<td align="center"><img src="preview_thumbs/Westbound_16.jpg" alt="rank-1" width="140"/><br/><sub>Westbound track#16 (0117)<br/>0.7871</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_113.jpg" alt="rank-2" width="140"/><br/><sub>SECorner track#113 (Public)<br/>0.7637</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_37.jpg" alt="rank-3" width="140"/><br/><sub>SECorner track#37 (Public)<br/>0.7183</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_21.jpg" alt="rank-4" width="140"/><br/><sub>SECorner track#21 (Public)<br/>0.7020</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_7.jpg" alt="rank-5" width="140"/><br/><sub>SECorner track#7 (Public)<br/>0.7005</sub></td>
</tr></table>

### Northbound track#6 (0043)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Northbound_6.jpg" alt="query" width="140"/><br/><sub>Northbound track#6 (0043)</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_113.jpg" alt="rank-1" width="140"/><br/><sub>SECorner track#113 (Public)<br/>0.7368</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_7.jpg" alt="rank-2" width="140"/><br/><sub>SECorner track#7 (Public)<br/>0.7158</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_45.jpg" alt="rank-3" width="140"/><br/><sub>SECorner track#45 (Public)<br/>0.7100</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="rank-4" width="140"/><br/><sub>Eastbound track#13 (0042)<br/>0.7080</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_37.jpg" alt="rank-5" width="140"/><br/><sub>SECorner track#37 (Public)<br/>0.7075</sub></td>
</tr></table>

### Northbound track#7 (0043)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="query" width="140"/><br/><sub>Northbound track#7 (0043)</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="rank-1" width="140"/><br/><sub>Eastbound track#3 (0042)<br/>0.9261</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="rank-2" width="140"/><br/><sub>Eastbound track#2 (0042)<br/>0.9162</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="rank-3" width="140"/><br/><sub>Eastbound track#13 (0042)<br/>0.9139</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_9.jpg" alt="rank-4" width="140"/><br/><sub>Eastbound track#9 (0042)<br/>0.9063</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_37.jpg" alt="rank-5" width="140"/><br/><sub>SECorner track#37 (Public)<br/>0.9039</sub></td>
</tr></table>

### Northbound track#46 (0043)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="query" width="140"/><br/><sub>Northbound track#46 (0043)</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="rank-1" width="140"/><br/><sub>Eastbound track#13 (0042)<br/>0.9399</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_1.jpg" alt="rank-2" width="140"/><br/><sub>Eastbound track#1 (0042)<br/>0.9116</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_9.jpg" alt="rank-3" width="140"/><br/><sub>Eastbound track#9 (0042)<br/>0.9087</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="rank-4" width="140"/><br/><sub>Eastbound track#2 (0042)<br/>0.8922</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="rank-5" width="140"/><br/><sub>Eastbound track#3 (0042)<br/>0.8900</sub></td>
</tr></table>

### Northbound track#53 (0043)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Northbound_53.jpg" alt="query" width="140"/><br/><sub>Northbound track#53 (0043)</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="rank-1" width="140"/><br/><sub>Eastbound track#2 (0042)<br/>0.8996</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_1.jpg" alt="rank-2" width="140"/><br/><sub>Eastbound track#1 (0042)<br/>0.8835</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="rank-3" width="140"/><br/><sub>Eastbound track#13 (0042)<br/>0.8811</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="rank-4" width="140"/><br/><sub>Eastbound track#3 (0042)<br/>0.8731</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_7.jpg" alt="rank-5" width="140"/><br/><sub>Eastbound track#7 (0042)<br/>0.8652</sub></td>
</tr></table>

## SECorner — top-5 matches

### SECorner track#1 (Public)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/SECorner_1.jpg" alt="query" width="140"/><br/><sub>SECorner track#1 (Public)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8813</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8758</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8614</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.8383</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="rank-5" width="140"/><br/><sub>Eastbound track#3 (0042)<br/>0.8371</sub></td>
</tr></table>

### SECorner track#2 (Public)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/SECorner_2.jpg" alt="query" width="140"/><br/><sub>SECorner track#2 (Public)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8939</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.8897</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8876</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.8764</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8746</sub></td>
</tr></table>

### SECorner track#3 (Public)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/SECorner_3.jpg" alt="query" width="140"/><br/><sub>SECorner track#3 (Public)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8817</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8766</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8685</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.8568</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="rank-5" width="140"/><br/><sub>Eastbound track#2 (0042)<br/>0.8473</sub></td>
</tr></table>

### SECorner track#7 (Public)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/SECorner_7.jpg" alt="query" width="140"/><br/><sub>SECorner track#7 (Public)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8990</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8901</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8889</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="rank-4" width="140"/><br/><sub>Eastbound track#3 (0042)<br/>0.8683</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="rank-5" width="140"/><br/><sub>Eastbound track#13 (0042)<br/>0.8570</sub></td>
</tr></table>

### SECorner track#21 (Public)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/SECorner_21.jpg" alt="query" width="140"/><br/><sub>SECorner track#21 (Public)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8807</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8791</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8779</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="rank-4" width="140"/><br/><sub>Eastbound track#3 (0042)<br/>0.8617</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="rank-5" width="140"/><br/><sub>Eastbound track#13 (0042)<br/>0.8556</sub></td>
</tr></table>

### SECorner track#37 (Public)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/SECorner_37.jpg" alt="query" width="140"/><br/><sub>SECorner track#37 (Public)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.9094</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.9039</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8971</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.8851</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#46 (0043)<br/>0.8842</sub></td>
</tr></table>

### SECorner track#45 (Public)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/SECorner_45.jpg" alt="query" width="140"/><br/><sub>SECorner track#45 (Public)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8833</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="rank-2" width="140"/><br/><sub>Eastbound track#2 (0042)<br/>0.8694</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8687</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8636</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.8556</sub></td>
</tr></table>

### SECorner track#92 (Public)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/SECorner_92.jpg" alt="query" width="140"/><br/><sub>SECorner track#92 (Public)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8780</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8612</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8578</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="rank-4" width="140"/><br/><sub>Eastbound track#3 (0042)<br/>0.8365</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.8295</sub></td>
</tr></table>

### SECorner track#107 (Public)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/SECorner_107.jpg" alt="query" width="140"/><br/><sub>SECorner track#107 (Public)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.9005</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.8872</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.8822</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="rank-4" width="140"/><br/><sub>Eastbound track#2 (0042)<br/>0.8765</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.8723</sub></td>
</tr></table>

### SECorner track#113 (Public)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/SECorner_113.jpg" alt="query" width="140"/><br/><sub>SECorner track#113 (Public)</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_24.jpg" alt="rank-1" width="140"/><br/><sub>Eastbound track#24 (0042)<br/>0.7957</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="rank-2" width="140"/><br/><sub>Northbound track#4 (0043)<br/>0.7850</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.7777</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_5.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#5 (0043)<br/>0.7637</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.7636</sub></td>
</tr></table>

## Westbound — top-5 matches

### Westbound track#1 (0117)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Westbound_1.jpg" alt="query" width="140"/><br/><sub>Westbound track#1 (0117)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_53.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#53 (0043)<br/>0.8422</sub></td>
<td align="center"><img src="preview_thumbs/Eastbound_2.jpg" alt="rank-2" width="140"/><br/><sub>Eastbound track#2 (0042)<br/>0.8305</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#7 (0043)<br/>0.8014</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_2.jpg" alt="rank-4" width="140"/><br/><sub>Northbound track#2 (0043)<br/>0.7954</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="rank-5" width="140"/><br/><sub>Northbound track#1 (0043)<br/>0.7814</sub></td>
</tr></table>

### Westbound track#16 (0117)

<table><tr><th>Original</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Westbound_16.jpg" alt="query" width="140"/><br/><sub>Westbound track#16 (0117)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_5.jpg" alt="rank-1" width="140"/><br/><sub>Northbound track#5 (0043)<br/>0.7871</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_113.jpg" alt="rank-2" width="140"/><br/><sub>SECorner track#113 (Public)<br/>0.6779</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_6.jpg" alt="rank-3" width="140"/><br/><sub>Northbound track#6 (0043)<br/>0.6701</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_2.jpg" alt="rank-4" width="140"/><br/><sub>SECorner track#2 (Public)<br/>0.6470</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_21.jpg" alt="rank-5" width="140"/><br/><sub>SECorner track#21 (Public)<br/>0.6449</sub></td>
</tr></table>


## Reciprocal top-1 pairs (highlighted)

These are the **5** cases where A’s top-1 match is B and B’s top-1 match is A. This is a consistency check only — not proof of correct identity.

### Pair 1 — score 0.9399

<table><tr><th>A</th><th>B</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_13.jpg" alt="A" width="180"/><br/><sub>Eastbound track#13 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_46.jpg" alt="B" width="180"/><br/><sub>Northbound track#46 (0043)</sub></td>
</tr></table>

- **Eastbound track#13 (0042)** ↔ **Northbound track#46 (0043)**

### Pair 2 — score 0.9316

<table><tr><th>A</th><th>B</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_1.jpg" alt="A" width="180"/><br/><sub>Eastbound track#1 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_1.jpg" alt="B" width="180"/><br/><sub>Northbound track#1 (0043)</sub></td>
</tr></table>

- **Eastbound track#1 (0042)** ↔ **Northbound track#1 (0043)**

### Pair 3 — score 0.9261

<table><tr><th>A</th><th>B</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Eastbound_3.jpg" alt="A" width="180"/><br/><sub>Eastbound track#3 (0042)</sub></td>
<td align="center"><img src="preview_thumbs/Northbound_7.jpg" alt="B" width="180"/><br/><sub>Northbound track#7 (0043)</sub></td>
</tr></table>

- **Eastbound track#3 (0042)** ↔ **Northbound track#7 (0043)**

### Pair 4 — score 0.9094

<table><tr><th>A</th><th>B</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Northbound_4.jpg" alt="A" width="180"/><br/><sub>Northbound track#4 (0043)</sub></td>
<td align="center"><img src="preview_thumbs/SECorner_37.jpg" alt="B" width="180"/><br/><sub>SECorner track#37 (Public)</sub></td>
</tr></table>

- **Northbound track#4 (0043)** ↔ **SECorner track#37 (Public)**

### Pair 5 — score 0.7871

<table><tr><th>A</th><th>B</th></tr>
<tr>
<td align="center"><img src="preview_thumbs/Northbound_5.jpg" alt="A" width="180"/><br/><sub>Northbound track#5 (0043)</sub></td>
<td align="center"><img src="preview_thumbs/Westbound_16.jpg" alt="B" width="180"/><br/><sub>Westbound track#16 (0117)</sub></td>
</tr></table>

- **Northbound track#5 (0043)** ↔ **Westbound track#16 (0117)**

## Next Steps

1. **Scale the gallery.** Run the same pipeline on more days and longer clips so we can see whether high-scoring matches remain stable outside this 30-second window.
2. **Score false positives.** Manually label a sample of top-1 / top-5 pairs as true match vs false match, then report precision at score thresholds (e.g. ≥0.90, ≥0.85) and propose an operating threshold.

