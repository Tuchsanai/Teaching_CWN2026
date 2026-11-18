The dataset is downloaded onto **vapp-lab2**, and the sample image is saved at `lab2_multigpu/results/dataset_samples.jpg`. I opened it: the boxes and class names line up with the people.

## How it went
1. **ultralytics 8.4.215 and roboflow 1.7.3** were already installed on the machine. I imported both, plus OpenCV, without errors.
2. **Download:** I downloaded hard-hat-workers version 13 from joseph-nelson in YOLO format into `/workspace/hardhat` on the rented machine.
3. **API key:** I read the key from `.env` on your computer and passed it to the script through stdin, so it was never shown in output or written to a file. After downloading I searched the rented machine for it in `/root`, `/tmp`, the dataset folder, environment variables and Roboflow's config files, and **found no copy**.
4. **Sample image:** `show_samples.py` makes a 4 × 2 grid of 8 Training Set images. It draws boxes and class names from the real label files: 🟩 helmet (wearing a hard hat) and 🟥 head (bare head). The black squares and tilted images in the samples are augmentations Roboflow added to the dataset itself.

## Dataset summary

| Split | Images | Boxes: `head` (no hard hat) | Boxes: `helmet` (hard hat) | Total boxes |
|---|---:|---:|---:|---:|
| Training Set | 14,748 | 13,670 | 41,450 | 55,120 |
| Validation Set | 1,413 | 1,339 | 3,913 | 5,252 |
| Test Set | 706 | 726 | 1,915 | 2,641 |
| **Total** | **16,867** | **15,735** | **47,278** | **63,013** |

- **Dataset size:** 557 MB on disk. Every image is 416 × 416 pixels. There are 2 classes: `0 = head`, `1 = helmet`.
- **Class balance:** the data is uneven. There are about 3 `helmet` boxes for every `head` box.
- **Empty label:** one image in the Training Set has an empty label file, meaning it contains no boxes.

## A real label line
From `train/labels/000001_jpg.rf.37162496c40765905dfd791dd99e63a0.txt`:
```
1 0.5697115384615384 0.30288461538461536 0.12259615384615384 0.1778846153846154
```
| Field | Value | Meaning |
|---|---|---|
| 1 | `1` | Class ID: 1 = `helmet`, so this person is wearing a hard hat |
| 2 | `0.5697` | x_center: the box's centre point measured horizontally, as a fraction of image width, so about 237 px from the left |
| 3 | `0.3029` | y_center: the box's centre point measured vertically, as a fraction of image height, so about 126 px from the top |
| 4 | `0.1226` | width: box width as a fraction of image width, so about 51 px |
| 5 | `0.1779` | height: box height as a fraction of image height, so about 74 px |

All values are between 0 and 1, so the labels work at any image size. Each line is one box, and each image has one `.txt` file.

## Files on your computer
- `lab2_multigpu/code/download_dataset.py`: downloads the dataset and reads the key from stdin.
- `lab2_multigpu/code/dataset_stats.py`: counts images and boxes for each split.
- `lab2_multigpu/code/show_samples.py`: makes the grid of 8 sample images.
- `lab2_multigpu/results/dataset_samples.jpg`

## Machine status
**vapp-lab2 is still on:** id <id>, status `running`, 2 × RTX 3090, about **$0.41 per hour**. The dataset is still at `/workspace/hardhat`, ready for the next step.
