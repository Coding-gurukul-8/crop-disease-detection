# Crop Disease Detection — Dataset Documentation

## 1. Dataset Source

**Dataset Name:** PlantVillage Dataset

**Source:** Kaggle

**Dataset URL:** https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset

**Dataset Slug:** `abdallahalidev/plantvillage-dataset`

**Variant Used:** `color/`

This project uses the original colour images from the PlantVillage dataset. The dataset contains images of healthy and diseased plant leaves.

The original dataset contains 38 classes. This project selects 8 target classes for crop disease classification.

## ## 2. License

The Kaggle dataset is distributed under the **CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International)** license.

License link: https://creativecommons.org/licenses/by-nc-sa/4.0/

The main conditions are:

- **Attribution (BY):** Give credit to the original creator and provide the source link.
- **NonCommercial (NC):** The licensed material may only be used for non-commercial purposes.
- **ShareAlike (SA):** Adapted material shared publicly must use the same or a compatible license.

Users should review the complete license terms before redistributing or using the dataset.

Dataset source: https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset


## 3. Classes

This project uses the following 8 target classes:

| No. | Exact Folder Name | Human-Readable Name |
|---|---|---|
| 1 | `Pepper,_bell___Bacterial_spot` | Pepper Bell – Bacterial Spot |
| 2 | `Pepper,_bell___healthy` | Pepper Bell – Healthy |
| 3 | `Potato___Early_blight` | Potato – Early Blight |
| 4 | `Potato___Late_blight` | Potato – Late Blight |
| 5 | `Potato___healthy` | Potato – Healthy |
| 6 | `Tomato___Early_blight` | Tomato – Early Blight |
| 7 | `Tomato___Late_blight` | Tomato – Late Blight |
| 8 | `Tomato___healthy` | Tomato – Healthy |

The folder names must match the `TARGET_CLASSES` constant in the filtering script.

## 4. Folder Layout

```text
ml/dataset/
│
├── raw/
│   └── Original PlantVillage images
│
├── filtered/
│   ├── Pepper,_bell___Bacterial_spot/
│   ├── Pepper,_bell___healthy/
│   ├── Potato___Early_blight/
│   ├── Potato___Late_blight/
│   ├── Potato___healthy/
│   ├── Tomato___Early_blight/
│   ├── Tomato___Late_blight/
│   └── Tomato___healthy/
│
├── split/
│   ├── train/
│   │   └── <class>/
│   ├── val/
│   │   └── <class>/
│   └── test/
│       └── <class>/
│
└── real_world_sample/
    └── <class>/
        (Populated in Phase 1.G)
```

### Folder Description

- `raw/`: Original downloaded PlantVillage dataset.
- `filtered/`: Contains only the 8 selected classes.
- `split/train/`: Training images (70%).
- `split/val/`: Validation images (15%).
- `split/test/`: Testing images (15%).
- `real_world_sample/`: Real-world leaf images collected later in Phase 1.G.

## 5. Reproducing This Dataset

Follow these steps in the given order to recreate the dataset from scratch.

Run all commands from the project root directory.

### Step 1: Download the Dataset

```powershell
python ml/dataset/download_dataset.py
```

Downloads the PlantVillage dataset from Kaggle into `ml/dataset/raw/`.

A valid Kaggle API token (`kaggle.json`) is required.

### Step 2: Filter the Target Classes

```powershell
python ml/dataset/filter_classes.py
```

Selects the 8 required classes and saves them in `ml/dataset/filtered/`.

### Step 3: Validate the Images

```powershell
python ml/dataset/validate_images.py
```

Checks the filtered images for validity and identifies problematic images.

### Step 4: Split the Dataset

```powershell
python ml/dataset/split_dataset.py
```

Creates a stratified 70/15/15 training, validation, and testing split in `ml/dataset/split/`.

### Final Result

After completing all four steps, the following folders should exist:

```text
ml/dataset/split/
├── train/
├── val/
└── test/
```

All three folders contain the 8 target class subfolders.

The split uses a fixed random seed to make the dataset reproducible.

## 6. Dataset Summary

| Item | Details |
|---|---|
| Dataset | PlantVillage |
| Source | Kaggle |
| Variant | Color |
| Original Classes | 38 |
| Selected Classes | 8 |
| Total Selected Images | 9,127 |
| Training Images | 6,388 |
| Validation Images | 1,369 |
| Testing Images | 1,370 |
| Split Ratio | 70:15:15 |
| Random Seed | 42 |

**Note:** Update this document if the dataset source, target classes, or processing scripts change.