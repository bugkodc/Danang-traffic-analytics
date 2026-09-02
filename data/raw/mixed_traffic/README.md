---
license: cc-by-4.0
task_categories:
  - object-detection
tags:
  - traffic
  - vehicles
  - autonomous-driving
  - south-asia
  - dashcam
  - yolo
size_categories:
  - n<1K
pretty_name: Visaitech Mixed-Traffic Vehicle Detection (v0.1)
---

# Visaitech Mixed-Traffic Vehicle Detection Dataset (v0.1)

Dashcam frames annotated for **pedestrian / 2-wheeler / 3-wheeler / 4-wheeler**
detection in South Asian mixed traffic, a class taxonomy general-purpose
COCO-trained detectors don't cover (COCO has no concept of an auto-rickshaw
or motorcycle-vs-bicycle-as-one-class "2-wheeler" grouping tuned for how
this traffic actually mixes on the road).

This is an early **v0.1 release**: 293 annotated frames from 6 source videos,
published now so the data and annotation format are public and versioned.
The full anonymized raw clip archive (203 clips, ~12GB, unannotated) ships
alongside it in `videos/`, with annotations for it to follow in future
releases (see Limitations below).

## Sample frames

One mid-clip frame from six of the raw clips in `videos/`, exactly as
published: faces and license plates pixelated, timestamp band blacked out
(see Privacy and anonymization below).

| ![Motorcycles sharing the lane with cars, riders pixelated](samples/clip_040.jpg) | ![Close-up of stopped nose-to-tail congestion](samples/clip_015.jpg) |
|:--:|:--:|
| Motorcycles sharing the lane with cars (clip_040) | Stopped congestion at close range (clip_015) |
| ![Cargo rickshaws lining a bright street](samples/clip_120.jpg) | ![Multi-lane urban arterial with mixed vehicles](samples/clip_140.jpg) |
| Cargo rickshaws lining a bright street (clip_120) | Multi-lane arterial, mixed vehicles (clip_140) |
| ![Dense bazaar street with 2- and 3-wheelers](samples/clip_160.jpg) | ![Squeezing past a truck in dense mixed traffic](samples/clip_129.jpg) |
| Dense bazaar street, 2- and 3-wheelers (clip_160) | Squeezing past a truck at close range (clip_129) |

## Classes

| id | class       | description                                   |
|----|-------------|------------------------------------------------|
| 0  | `pedestrian`| Person on foot                                |
| 1  | `2-wheeler` | Motorcycle / scooter / bicycle                |
| 2  | `3-wheeler` | Auto-rickshaw / three-wheeled vehicle          |
| 3  | `4-wheeler` | Car / van / bus / truck                       |

Occlusion is **not** a separate class. Partially-visible boxes (tagged
`... half` by the original annotators) are folded into their base class,
with the flag preserved per-box in `attributes.csv` (`occluded` column) for
anyone who wants to filter or weight by visibility.

## Dataset structure

```
images/{train,val}/*.jpg   # source video id prefixed, e.g. V003__frame.jpg
labels/{train,val}/*.txt   # YOLO format: class x_center y_center width height (normalized)
data.yaml                  # Ultralytics-ready config
classes.txt                # class id -> name, one per line
attributes.csv             # image, class, occluded (per-box)
videos/clip_001.mp4 ...    # 203 anonymized raw dashcam clips (~12GB, unannotated),
                           # flat sequential naming, ~2 minutes each
samples/clip_XXX.jpg       # preview frames from six of the clips (see Sample frames)
```

Directly usable with Ultralytics:

```python
from ultralytics import YOLO
model = YOLO("yolo11n.pt")
model.train(data="data.yaml", epochs=100, imgsz=640)
```

## Statistics

- **293 images** (640x480), **1,506 boxes**, split by whole source video
  (not by frame) to avoid near-duplicate leakage between train/val.
- Split: 239 train / 54 val images.

| class       | train | val | total | occluded |
|-------------|------:|----:|------:|---------:|
| pedestrian  |    30 |   9 |    39 |        0 |
| 2-wheeler   |   731 | 128 |   859 |      121 |
| 3-wheeler   |   185 |  32 |   217 |       56 |
| 4-wheeler   |   351 |  40 |   391 |      153 |
| **total**   | **1297** | **209** | **1506** | **330** |

Boxes per source video: V001=377, V002=136, V003=325, V004=262, V005=333,
VEHICLES=73.

## Collection methodology

Frames were extracted from vehicle-mounted dashcam recordings and manually
annotated with bounding boxes using [VoTT](https://github.com/microsoft/VoTT)
(Visual Object Tagging Tool). Annotation JSON was normalized from VoTT's
per-project tag conventions (which varied in capitalization/spacing across
annotation sessions, e.g. `"2 Wheeler"` / `"2 wheeler"` / `"PERSON"`) into the
canonical 4-class taxonomy above.

## Privacy and anonymization

All published frames are anonymized. Detected regions are pixelated rather
than Gaussian-blurred, since blur can be partially reversible. Labels are
unaffected: pixelation does not move bounding boxes.

- **People**: the primary redaction signal is a general COCO-pretrained
  person detector run at a low threshold (favoring recall), with the head
  region of every detected person (top ~32% of the box, expanded upward and
  sideways) pixelated. Dedicated face detectors were evaluated first but
  perform poorly on this footage's haze, glare, and compression, so a face
  detector runs only as a supplementary layer on top of the person-based
  pass.
- **License plates**: an automatic plate detector runs at a deliberately low
  confidence threshold, but in this footage detector confidence does not
  cleanly separate legible plates from illegible ones. So on top of the
  automatic pass, every frame went through a manual audit: a detector sweep
  at near-zero confidence with each plate-like candidate reviewed by eye,
  crop-level checks of large vehicles, and an OCR sweep over vehicle crops
  of the output as a final net. The 80 hand-marked plate boxes this audit
  produced are pixelated unconditionally.
- **Burned-in timestamps**: the camera's timestamp overlay (exact date and
  time of recording) is blacked out. The blackout covers only the measured
  region the timestamps occupy, which clips 35 of the 1,506 annotation
  boxes by at most ~11% of their height; those pixels were already partly
  covered by the timestamp text itself.
- One advertisement poster on a truck showing a person's photo and phone
  number was also manually pixelated, even though it is public commercial
  signage.

## Known limitations

- **Small v0.1 sample**: 293 frames from 6 videos, out of a much larger
  (~12GB, 203-clip) raw footage archive that is not yet annotated. The full
  anonymized archive is included in this repository under `videos/` so others
  can extract and annotate frames themselves. Expect this dataset to grow in
  future releases.
- **Daytime only**: all footage in this release was recorded in daylight
  hours (the 6 annotated videos span 10:14 to 16:19). Night clips were
  recorded during the same pilot but excluded from the release: in low
  light the camera falls to roughly 6 fps with long exposures, so frames
  are dominated by motion blur and headlight bloom and contain no
  annotatable vehicle shapes. This release should not be assumed to
  generalize to low-light conditions.
- **Class imbalance**: `pedestrian` is only ~2.6% of boxes and has zero
  occluded examples, so expect weaker detector performance on this class
  until more data is added.
- **Playback speed is mixed across the raw archive**: the dashcam stamps a
  20 fps header on every clip regardless of its true capture rate, which
  varies from roughly 6 fps at night to 15 fps in daylight. Most of the
  anonymized archive is written at a per-clip real rate measured from the
  burned-in timestamps (before they are blacked out), so those clips play
  at real-world speed; the first ~100 clips processed kept the camera's
  20 fps header and play 1.3-3.3x faster than real time. Frame content is
  identical either way, only the playback timing differs, so this does not
  affect training on extracted frames.
- **Anonymization is best-effort, not a guarantee**: the combination of
  automated detection and full manual audit described above was verified by
  visual review, but redaction of real-world footage can never be proven
  exhaustive. Pixelated head and plate regions also mean a small fraction
  of annotated-object pixels are destroyed; boxes are kept at their
  original geometry, and models trained on this data will see pixelation
  artifacts inside some boxes. Measured effect: a YOLO26n baseline trained
  on the original frames scores mAP50 0.719 on the original validation
  images but 0.629 on this anonymized copy of them.

## License

CC BY 4.0: free to use, share, and adapt, including commercially, with
attribution to Visaitech.

## Citation

```
@dataset{visaitech_vehicle_mixed_traffic_2026,
  title        = {Visaitech Mixed-Traffic Vehicle Detection Dataset},
  author       = {Visaitech},
  year         = {2026},
  version      = {0.1},
  publisher    = {Hugging Face},
  url          = {https://huggingface.co/datasets/visaitech/vehicle-mixed-traffic-detection}
}
```
