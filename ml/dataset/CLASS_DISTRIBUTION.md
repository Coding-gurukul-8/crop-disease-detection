# Class Distribution and Imbalance Analysis

## 1. Dataset Overview

The Crop Disease Detection project uses a filtered PlantVillage dataset containing 8 selected classes.

- Total number of classes: 8
- Total number of images: 9,127
- Image dimensions: 256 × 256 pixels
- Dataset source: PlantVillage

## 2. Class-wise Image Distribution

| Class | Image Count | % of Total |
|---|---:|---:|
| Pepper,_bell___Bacterial_spot | 997 | 10.92% |
| Pepper,_bell___healthy | 1,478 | 16.19% |
| Potato___Early_blight | 1,000 | 10.96% |
| Potato___Late_blight | 1,000 | 10.96% |
| Potato___healthy | 152 | 1.67% |
| Tomato___Early_blight | 1,000 | 10.96% |
| Tomato___Late_blight | 1,909 | 20.92% |
| Tomato___healthy | 1,591 | 17.43% |
| **Total** | **9,127** | **100.01% (rounding)** |

## 3. Observations

1. The largest class is Tomato___Late_blight, containing 1,909 images (20.92%).
2. The smallest class is Potato___healthy, containing 152 images (1.67%).
3. The imbalance ratio is:

   1,909 / 152 = 12.56:1

4. The largest class contains approximately 12.56 times more images than the smallest class.
5. This imbalance is significant because the ratio is higher than the commonly used 3:1 rule of thumb.
6. Therefore, class weighting is recommended to reduce the effect of class imbalance during model training.

## 4. Planned Mitigation

To handle class imbalance, the project will use class weighting during model training.

The Python file:

`ml/preprocessing/class_weights.py`

will be created in Prompt 24.

It will calculate appropriate weights for each class based on the number of training images.

These weights will help give more importance to underrepresented classes, such as Potato___healthy, during model training.

Stratified train, validation and test splitting will also be used to maintain class proportions across the three datasets.

## 5. Conclusion

The filtered PlantVillage dataset contains 9,127 images belonging to 8 selected classes.

The dataset has a significant class imbalance, with a ratio of 12.56:1 between the largest and smallest classes.

Class weighting will be used in Prompt 24 to address this imbalance and support more balanced model training.