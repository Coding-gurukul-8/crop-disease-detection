# Crop Disease Detection

An AI/ML-based system that detects crop diseases from leaf images and provides prevention/management guidance.

## Repository Structure

- `ml/` — dataset preparation, preprocessing, model training, evaluation, and the exported model artifacts.
- `backend/` — FastAPI service, PostgreSQL persistence, authentication, and the model-serving API.
- `frontend/` — React/TypeScript web application for uploading leaf images and viewing results.
- `docs/` — setup, architecture, API, security, and testing documentation (the original build prompts live in `docs/prompts/`).

## Tech Stack

- **ML:** TensorFlow / Keras
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Frontend:** React / TypeScript

## Getting Started

- ML environment (Python 3.10 or 3.11 required): see [`ml/README.md`](ml/README.md).
- The dataset is not stored in Git; it is downloaded by script into `ml/dataset/`.
- The trained `ml/models/crop_disease_model.keras` is created by training and is the only `.keras` file tracked in Git.

## Team

- Sadhana Bag
- Priyanshu Kumar Gupta
- Kumar Gaurav
- Rajdeep Kumar
