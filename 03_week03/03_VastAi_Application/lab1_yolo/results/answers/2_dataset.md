The dataset is downloaded to the rented machine and the sample image is at `lab1_yolo/results/dataset_samples.jpg`. One problem first: the Roboflow key was exposed in my tool output.

**About the key:** I accidentally ran a check on the `.env` file that printed the `ROBOFLOW_API_KEY` value into my tool output. It never went to the rented machine. Please rotate the key at Roboflow (Settings → API Keys) to be safe.

On the rented machine, the key was sent only through stdin. I searched all of `/root` and `/workspace` and the key is not there. There is no Roboflow config file, and the download script has been deleted.

## Dataset summary: construction-site-safety v28 (YOLO format)

| Set | Images | Boxes |
|---|---:|---:|
| Training Set | 2,605 | 36,895 |
| Validation Set | 114 | 697 |
| Test Set | 82 | 760 |

| # | Class | Boxes in Training Set |
|---|---|---:|
| 0 | Hardhat (wearing a hard hat) | 3,145 |
| 1 | Mask (wearing a mask) | 1,651 |
| 2 | NO-Hardhat (no hard hat) | 2,317 |
| 3 | NO-Mask (no mask) | 3,097 |
| 4 | NO-Safety Vest (no safety vest) | 3,962 |
| 5 | Person | 9,532 |
| 6 | Safety Cone | 3,366 |
| 7 | Safety Vest (wearing a safety vest) | 3,033 |
| 8 | machinery (heavy machinery) | 5,247 |
| 9 | vehicle | 1,545 |

**Results:**
- `ultralytics` 8.4.215 and `roboflow` 1.7.3 are installed and working, with torch 2.8.0 on CUDA (RTX 4090 GPU).
- The dataset is at `/workspace/datasets/construction-site-safety-28` on the rented machine.
- The sample image is a grid of 8 Training Set images, chosen so the answer boxes cover all 10 classes. I opened it and it looks right.
- Many Training Set images are mosaics: one image made of 4 photos stitched together. That is how the dataset was built (augmentation done at Roboflow), so some images look split into 4.
- Classes are unbalanced: Person has about 6 times as many boxes as vehicle or Mask.
- The Validation and Test Sets are much smaller than the Training Set.

The scripts are in `lab1_yolo/code/`: `download_dataset.py` and `dataset_samples.py`.

**The rented machine vapp-lab1 (RTX 4090) is still running and billing at about $0.41/hour.** I have not closed it.
