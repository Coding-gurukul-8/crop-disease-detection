# Crop Disease Detection

Project scaffold for crop-disease classification, an API backend, and a web
frontend.

## Project layout

- `ml/` contains data preparation, training, and evaluation code.
- `backend/` contains the API, persistence, and authentication layers.
- `frontend/` contains the web application.
- `docs/` contains setup, architecture, API, and operational documentation.

The dataset directories are placeholders. Add the dataset before running the ML
pipeline. The trained `crop_disease_model.keras` artifact is intentionally not
included; create it by training a model and place it in `ml/models/`.

The original phase prompt documents are preserved in `IMAGE_Processing/`.
