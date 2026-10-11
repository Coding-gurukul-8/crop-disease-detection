# Crop Disease Detection App — Full Build Prompt Library (Expanded Edition)

**220 Execution-Ready, Fully-Specified Prompts · 4 Phases · ML + Backend + Frontend + Deployment**

Prepared for: Priyanshu Kumar Gupta & Team (Sadhana Bag, Kumar Gaurav, Rajdeep Kumar)

> This is the expanded edition of the prompt library. Every prompt from the original 220-item list has been rewritten as a complete, self-contained specification: exact file paths, exact function/class/route names, required parameters and return shapes, edge cases to handle, and testable acceptance criteria. Each prompt is written so that pasting it into Claude Code with nothing else produces a correct, complete, non-ambiguous result — no follow-up clarification should be needed. Complete Phase 1 fully before starting Phase 2, and so on.

---

## How to Use This Library

1. Copy **one prompt at a time**, in numeric order, into Claude Code (or a fresh Claude conversation with code execution).
2. Do not skip ahead within a phase — later prompts in a phase assume the exact file/function names created by earlier prompts in that same phase.
3. Do not start Phase 2 until every Phase 1 acceptance criterion is met and `ml/models/crop_disease_model.keras` + `ml/models/class_names.json` exist and are frozen.
4. Do not start Phase 4's integration work (Section 4.A) until both Phase 2's full test suite (Prompt 110) and Phase 3's visual QA (Prompt 165) are complete. Phase 3 may be scaffolded in parallel with Phase 2 using clearly-marked temporary mocks, which must all be removed before Phase 4.
5. Each prompt's **Acceptance Criteria** section is the definition of "done" — re-run it and check every box before moving to the next prompt.
6. Each prompt's **Must Not Break** section lists prior work it must not silently alter — if a change is needed there, treat it as a deliberate refactor, not a side effect.

## Global Conventions Used Across Every Prompt

- **Python** (`ml/`, `backend/`): PEP8, type hints on all function signatures, docstrings on every public function/class, `snake_case` for files and functions, `PascalCase` for classes.
- **TypeScript/React** (`frontend/`): strict mode, functional components with hooks only (no class components), `PascalCase` for components/files, `camelCase` for functions/variables.
- **All API responses**: JSON, `snake_case` field names, ISO-8601 timestamps, a consistent error shape `{"detail": "<message>", "error_code": "<UPPER_SNAKE_CASE>"}` for every non-2xx response.
- **All secrets** (DB URLs, JWT secret, API keys) live only in `.env` files that are git-ignored; `.env.example` documents every required variable with a placeholder value and one-line comment.
- **Every module that touches the database** must use the shared session dependency — no ad-hoc connections.
- **Every route that returns user-specific data** must derive the user identity from the verified JWT (`get_current_user`), never from a client-supplied `user_id` field, query param, or form field.

---

## Cross-Phase Sync Contracts (the "no loopholes" table)

These are the values that must be identical in every phase. If any prompt appears to conflict with this table, this table wins and the conflicting prompt's output must be corrected.

| Contract | Defined in | Must be honored by |
|---|---|---|
| **Class order and names**: 8 classes, alphabetical by PlantVillage folder name, exactly as `train_ds.class_names` | Prompts 20, 43 | Backend `model_service` (86), `diseases` seed (67), frontend filters (150, 159) |
| **Input preprocessing**: RGB, 224x224, bilinear resize, `[0,1]` float32. Model-specific rescaling (e.g. `[-1,1]`) lives *inside* the model | Prompts 16, 34, 38 | Backend `preprocessing_service` (87), parity test (95), client compression (193) |
| **Confidence**: float fraction `0.0-1.0` everywhere in storage and API; percentage conversion only in the UI | Prompts 63, 88 | Frontend (130, 143, 144), threshold sweep (47) |
| **Confidence threshold**: single value chosen from the real sweep | Prompt 48 | `config.py` (58), `/predict` (90), e2e uncertain test (177) |
| **Identity**: user id comes only from the verified JWT, never from client input | Prompts 74, 92, 99 | Every protected route, audit (184), isolation tests (100, 172, 179) |
| **Error shape**: `{"detail", "error_code"}` on every non-2xx | Global Conventions, 101 | Frontend `api.ts` (118), error displays (123, 140, 158) |
| **Frozen artifacts**: `crop_disease_model.keras` + `class_names.json`, SHA-256 recorded | Prompt 55 | Backend (86), deployment (199), report numbers (211) |
| **Upload limits**: one max size, validated at three layers (client, route, server) | Prompts 58, 82, 89, 104, 137 | Env vars `MAX_UPLOAD_SIZE_MB` / `VITE_MAX_UPLOAD_SIZE_MB` kept equal |

---
## 3. PHASE 1 — Machine Learning & Data Pipeline

*Prompts 1–55*

This phase produces the two frozen artifacts every other phase depends on: `ml/models/crop_disease_model.keras` and `ml/models/class_names.json`. Nothing in Phase 2 or 3 may reference these files until this phase's final prompt (55) is complete and both files are committed.

### 1.A Environment & Project Setup

#### Prompt 1 — Create the Monorepo Root Structure

**Do:** Create the root folder `crop-disease-detection/` containing four empty subfolders — `ml/`, `backend/`, `frontend/`, `docs/` — and a root `README.md`.

**Context & Why:** Every later prompt in every phase assumes this exact top-level layout. Getting the folder names or nesting wrong here breaks every relative path referenced later (e.g. `ml/models/crop_disease_model.keras`, `backend/app/main.py`).

**Requirements:**
- Root `README.md` must contain: a one-paragraph project description ("An AI/ML-based system that detects crop diseases from leaf images and provides prevention/management guidance"), a bullet list of the four subfolders with one line each on their purpose, a "Tech Stack" section listing TensorFlow/Keras, FastAPI, PostgreSQL, React/TypeScript, and a "Team" section naming Sadhana Bag, Priyanshu Kumar Gupta, Kumar Gaurav, and Rajdeep Kumar.
- No other files yet — this prompt only creates structure and the root README.
- Use exactly these folder names, lowercase, no trailing slashes in Git: `ml`, `backend`, `frontend`, `docs`.

**Acceptance Criteria:**
- [ ] `crop-disease-detection/{ml,backend,frontend,docs}/` all exist as empty directories.
- [ ] `crop-disease-detection/README.md` exists and renders correctly as Markdown.
- [ ] Running `tree -L 1 crop-disease-detection/` shows exactly the four folders plus the README.

**Must Not Break:** N/A (first prompt).

---

#### Prompt 2 — Scaffold the `ml/` Folder and Its Dependencies

**Do:** Inside `ml/`, create the subfolders `dataset/`, `notebooks/`, `preprocessing/`, `training/`, `evaluation/`, `models/`, and a `requirements.txt` at `ml/requirements.txt`.

**Context & Why:** These six subfolders map one-to-one onto the six remaining sub-sections of Phase 1 (1.B through 1.G). Every subsequent Phase 1 prompt writes into one of these folders by exact name — do not rename or merge any of them.

**Requirements:**
- `ml/requirements.txt` must pin these packages with compatible version ranges (not unpinned `latest`): `tensorflow>=2.15,<2.17`, `keras`, `opencv-python`, `pillow`, `numpy`, `pandas`, `matplotlib`, `scikit-learn`, `jupyter`, `kaggle`.
- Each of the six subfolders should contain a placeholder `.gitkeep` file so Git tracks the empty directory.
- Do not install anything yet — this prompt only writes the requirements file and folder structure.

**Acceptance Criteria:**
- [ ] `ml/{dataset,notebooks,preprocessing,training,evaluation,models}/` all exist.
- [ ] `ml/requirements.txt` lists all nine packages above with version pins.
- [ ] `pip install -r ml/requirements.txt --dry-run` (or equivalent) resolves without conflict errors.

**Must Not Break:** The root structure from Prompt 1.

---

#### Prompt 3 — Set Up the ML Virtual Environment

**Do:** Create a Python virtual environment for `ml/` and document exact activation/installation steps in `ml/README.md`.

**Context & Why:** All ML work in Prompts 4–55 must run inside this isolated environment so package versions stay consistent between team members and match what gets deployed later in the FastAPI backend (Prompt 86 loads the same TensorFlow-trained model format).

**Requirements:**
- Create the venv at `ml/venv/` using `python3 -m venv venv` run from inside `ml/`.
- `ml/README.md` must include: the exact `python3 -m venv venv` command, the exact activation command for both bash/zsh (`source venv/bin/activate`) and Windows PowerShell (`venv\Scripts\Activate.ps1`), the exact `pip install -r requirements.txt` command, and a note on the required Python version (3.10 or 3.11 — not 3.12, for TensorFlow compatibility at the pinned version).
- Add `ml/venv/` to the root `.gitignore` (create the `.gitignore` now if Prompt 5 hasn't run yet; otherwise append to it).

**Acceptance Criteria:**
- [ ] `ml/venv/` exists and activates without error.
- [ ] `pip install -r ml/requirements.txt` completes successfully inside the activated venv.
- [ ] `ml/README.md` contains copy-pasteable setup commands for both Unix and Windows.
- [ ] `ml/venv/` never gets committed to Git.

**Must Not Break:** The folder structure and requirements.txt from Prompt 2.

---

#### Prompt 4 — Colab Setup Notebook

**Do:** Create `ml/notebooks/00_colab_setup.ipynb`, a notebook designed to run in Google Colab (not locally), that mounts Google Drive, installs `ml/requirements.txt`, and verifies GPU availability.

**Context & Why:** Training in Prompts 27–39 is computationally heavy; the team will primarily train on Colab's free GPU runtime rather than local machines. This notebook is the standard entrypoint every teammate runs first in any new Colab session.

**Requirements:**
- Cell 1: mount Google Drive via `from google.colab import drive; drive.mount('/content/drive')`.
- Cell 2: `cd` into the project folder on Drive (use a clearly marked, easily-editable variable `PROJECT_PATH = "/content/drive/MyDrive/crop-disease-detection"` at the top so each teammate only edits one line).
- Cell 3: `!pip install -r {PROJECT_PATH}/ml/requirements.txt -q`.
- Cell 4: verify GPU with `import tensorflow as tf; print("GPU available:", tf.config.list_physical_devices('GPU'))` and print a clear warning message (not a silent pass) if the list is empty, telling the user to enable a GPU runtime via Runtime → Change runtime type.
- Cell 5 (markdown): a short usage note explaining that every other notebook in `ml/notebooks/` should start by running this one first, or at minimum re-running its Drive-mount and path-setup cells.

**Acceptance Criteria:**
- [ ] Notebook runs top-to-bottom in a fresh Colab session without manual intervention beyond the Drive-auth popup.
- [ ] GPU check clearly reports whether a GPU is attached.
- [ ] `PROJECT_PATH` is the only line a teammate needs to edit to point at their own Drive layout.

**Must Not Break:** Nothing yet exists to break; this notebook must, however, reference the exact `requirements.txt` path from Prompt 2.

---

#### Prompt 5 — Git Initialization and Ignore Rules

**Do:** Initialize a Git repository at the project root, create a comprehensive `.gitignore`, and make the first commit.

**Context & Why:** From this point forward every prompt's output should be committed as its own logical unit so the team can track exactly which of the 220 prompts have been completed and roll back cleanly if one introduces a regression.

**Requirements:**
- Run `git init` at `crop-disease-detection/`.
- `.gitignore` at the root must cover, at minimum: `venv/`, `**/venv/`, `__pycache__/`, `*.pyc`, `node_modules/`, `.env`, `**/.env`, `ml/dataset/` (raw/filtered/split images are too large and reproducible from the download script), `*.keras` and `*.h5` inside `ml/models/` EXCEPT the two final frozen files (use a negative pattern: ignore `ml/models/*.keras` then explicitly un-ignore `ml/models/crop_disease_model.keras` with a `!` rule, and never ignore `ml/models/class_names.json`), `.DS_Store`, `*.log`, `dist/`, `build/`, `.vscode/`, `*.ipynb_checkpoints/`.
- First commit message: `"chore: initial project scaffold (ml, backend, frontend, docs)"`.
- Confirm `git status` shows a clean tree immediately after the commit.

**Acceptance Criteria:**
- [ ] `.git/` exists at the project root (only one repo — do not `git init` inside subfolders).
- [ ] `git log` shows exactly one commit with the specified message.
- [ ] `git status` is clean after the commit.
- [ ] Creating a dummy file inside `ml/venv/` or `node_modules/` and running `git status` shows it as ignored, not untracked.

**Must Not Break:** All folders and files from Prompts 1–4 must be included in this first commit, not ignored by accident.

---
### 1.B Dataset Acquisition & Exploration

#### Prompt 6 — Kaggle Dataset Download Script

**Do:** Write `ml/dataset/download_dataset.py`, a script that downloads the PlantVillage dataset from Kaggle via the Kaggle API into `ml/dataset/raw/`.

**Context & Why:** Every later dataset step (filtering, splitting, training) assumes `ml/dataset/raw/` contains the full, unmodified PlantVillage folder structure (one subfolder per crop-disease class). This script is the single reproducible source of truth for that data — it must never be committed to Git (see Prompt 5's `.gitignore`), so anyone on the team can regenerate it from scratch.

**Requirements:**
- Read Kaggle credentials from the standard `~/.kaggle/kaggle.json` location (do not hardcode credentials or accept them as CLI arguments).
- Use `kaggle datasets download -d <plantvillage-dataset-slug>` via `subprocess` or the `kaggle` Python package — pick one approach and document it with a comment.
- Unzip the downloaded archive into `ml/dataset/raw/`, then delete the `.zip` after successful extraction to save disk space.
- If `ml/dataset/raw/` already contains data, print a message and exit without re-downloading (idempotent behavior), unless a `--force` CLI flag is passed.
- On any failure (missing credentials, network error, disk-full), print a clear, actionable error message and exit with a non-zero exit code — do not leave a partially-extracted folder behind on failure.
- Add a top-of-file docstring explaining how to obtain a `kaggle.json` API token (Kaggle account → Settings → API → Create New Token).

**Acceptance Criteria:**
- [ ] Running `python ml/dataset/download_dataset.py` with valid credentials populates `ml/dataset/raw/<class_name>/*.jpg` for every PlantVillage class.
- [ ] Running it a second time without `--force` does not re-download.
- [ ] Running it with missing/invalid credentials fails loudly with a helpful message, not a stack trace dump.

**Must Not Break:** N/A — first dataset script.

---

#### Prompt 7 — Dataset Exploration Notebook

**Do:** Write `ml/notebooks/01_dataset_exploration.ipynb` that counts total images and images per class folder in `ml/dataset/raw/` and prints a summary table.

**Context & Why:** This is the team's first real look at the data — it directly informs the class-imbalance findings documented in Prompt 12 and the class-selection decision in Prompt 9.

**Requirements:**
- First cell re-uses the Drive-mount / path-setup pattern from Prompt 4's notebook (import path, do not duplicate the mount logic inline).
- Iterate over every subdirectory of `ml/dataset/raw/`, count `.jpg`/`.jpeg`/`.png` files in each (case-insensitive extension match), and build a pandas DataFrame with columns `class_name`, `image_count`.
- Sort the DataFrame descending by `image_count` and display it with `.style.background_gradient()` or an equivalent visually readable rendering.
- Print total image count and total class count as a final summary line.
- Handle the case where a class folder contains zero images (e.g. an empty folder from a failed download) — flag it explicitly rather than silently reporting 0 with no comment.

**Acceptance Criteria:**
- [ ] Notebook runs top-to-bottom against a populated `ml/dataset/raw/` and produces a sorted table with no errors.
- [ ] Total image count printed matches `find ml/dataset/raw -type f | wc -l` (adjusted for any non-image files).
- [ ] Any zero-image class is visibly flagged, not silently listed as 0.

**Must Not Break:** Assumes `ml/dataset/raw/` populated by Prompt 6's script — do not hardcode a different path.

---

#### Prompt 8 — Class Distribution Bar Chart

**Do:** Extend `ml/notebooks/01_dataset_exploration.ipynb` with a new cell that plots a bar chart of class distribution using Matplotlib and saves it to `ml/evaluation/class_distribution.png`.

**Context & Why:** This chart becomes both a debugging tool now and a reusable figure for the final project report and presentation (it can replace or supplement the confusion-matrix-style figures already produced in the report document).

**Requirements:**
- Use the same DataFrame built in Prompt 7 (do not re-count from disk in this cell).
- Horizontal bar chart if there are more than ~15 classes (better label readability), vertical if fewer.
- X-axis (or Y-axis) labeled "Number of Images", the other axis labeled "Class", chart title "PlantVillage Dataset — Class Distribution".
- Sort bars descending by count so imbalance is visually obvious at a glance.
- Save at `ml/evaluation/class_distribution.png` at ≥150 DPI; create the `ml/evaluation/` folder if it does not already exist (it will also be used starting Prompt 29 onward).
- Do not call `plt.show()` as the only output — explicitly save to disk with `plt.savefig(...)` before/instead of showing, so the file exists even in non-interactive runs.

**Acceptance Criteria:**
- [ ] `ml/evaluation/class_distribution.png` exists after running the notebook.
- [ ] Chart is legible: no overlapping labels, clear axis titles, descending sort visible.
- [ ] Re-running the cell overwrites the file cleanly (no accumulating duplicate files).

**Must Not Break:** Prompt 7's counting cell — this prompt only adds a new cell after it.

---

#### Prompt 9 — Filter to the 8 Target Classes

**Do:** Write `ml/dataset/filter_classes.py` that copies only 8 target classes from `ml/dataset/raw/` into `ml/dataset/filtered/`.

**Context & Why:** The full PlantVillage dataset covers many more crops than this project scopes to (per the project report's stated limitation: "focus on a defined set of crops and diseases rather than claiming to detect every possible crop disease"). This script defines that exact scope and is the boundary between "everything Kaggle gives us" and "what we actually train on."

**Requirements:**
- Hardcode the exact 8 target class folder names as a module-level constant `TARGET_CLASSES` (a Python list), matching PlantVillage's actual folder-naming convention (verify exact names against the downloaded data — they typically look like `Tomato___healthy`, `Tomato___Early_blight`, `Tomato___Late_blight`, `Potato___healthy`, `Potato___Early_blight`, `Potato___Late_blight`, `Pepper__bell___healthy`, `Pepper__bell___Bacterial_spot` — adjust to whatever the actual downloaded folder names are and note any mismatch in a code comment).
- For each target class, copy (do not move) the entire folder from `raw/` to `filtered/`, preserving filenames.
- Skip and warn (not crash) if a target class folder is missing from `raw/`.
- Print a final summary: how many classes were copied, how many images total, and any classes that were skipped.
- Must be re-runnable / idempotent: running twice should not duplicate files (overwrite or skip existing).

**Acceptance Criteria:**
- [ ] `ml/dataset/filtered/` contains exactly the 8 target class folders (no more, no fewer) after a successful run.
- [ ] Image counts per class in `filtered/` match the corresponding counts in `raw/` from Prompt 7's table.
- [ ] Running the script twice in a row produces an identical result the second time (no duplicated or corrupted files).

**Must Not Break:** Must read from the exact `ml/dataset/raw/` path populated by Prompt 6, and must not modify or delete anything inside `raw/`.

---

#### Prompt 10 — Corrupted/Duplicate Image Checker

**Do:** Write `ml/dataset/validate_images.py` using PIL and `hashlib` to detect corrupted and duplicate images, and generate a validation report.

**Context & Why:** Silently training on corrupted files crashes `tf.data` pipelines deep inside a long training run (Prompt 27+), and duplicate images across train/val/test splits (created later in Prompt 13) would leak test data into training, inflating reported accuracy. Catching both issues now, before splitting, is far cheaper than debugging them after a failed multi-hour training run.

**Requirements:**
- Walk every file under `ml/dataset/filtered/`.
- For corruption: attempt `PIL.Image.open(path).verify()` inside a try/except; log any file that raises as corrupted, with its full path.
- For duplicates: compute an MD5 (or SHA-256) hash of each file's raw bytes, group by hash, and report any group with more than one file as duplicates (list all paths in the group).
- Write a structured report to `ml/dataset/validation_report.json` with keys `total_images_scanned`, `corrupted_files` (list of paths), `duplicate_groups` (list of lists of paths), `duplicate_file_count`.
- Do NOT automatically delete anything — this script only reports; deletion is a manual, reviewed decision the team makes based on the report.
- Print a human-readable summary to stdout as well (counts, not full file lists, to keep terminal output scannable).

**Acceptance Criteria:**
- [ ] `ml/dataset/validation_report.json` is created and is valid JSON matching the schema above.
- [ ] A deliberately corrupted test file (e.g. a `.jpg` with truncated bytes) is correctly flagged when manually tested.
- [ ] Two byte-identical copies of the same image in different class folders are correctly flagged as a duplicate group.
- [ ] The script does not modify, move, or delete any file under `ml/dataset/filtered/`.

**Must Not Break:** Must run against `ml/dataset/filtered/` as produced by Prompt 9, not `raw/`.

---

#### Prompt 11 — Image Dimension Statistics

**Do:** Write `ml/dataset/image_stats.py` that reports min/max/average image dimensions (width × height) per class.

**Context & Why:** The preprocessing pipeline (Prompt 16) resizes every image to a fixed 224×224 input; knowing the actual size distribution beforehand tells the team whether that resize will involve heavy downscaling (likely fine) or upscaling small images (which degrades quality and should be flagged in the report's limitations section).

**Requirements:**
- Walk `ml/dataset/filtered/`, open each image with PIL, and record `(width, height)`.
- Group by class folder; compute min width, max width, min height, max height, mean width, mean height per class, plus the same stats aggregated across the whole filtered dataset.
- Output as a pandas DataFrame printed to stdout AND saved as `ml/dataset/image_dimension_stats.csv`.
- Skip files that fail to open (they've already been caught by Prompt 10's validator — do not crash on them here, just skip and count them as "skipped_unreadable" in the summary).

**Acceptance Criteria:**
- [ ] `ml/dataset/image_dimension_stats.csv` exists with one row per class plus one aggregate "ALL" row.
- [ ] Numbers are sane (e.g. PlantVillage images are typically 256×256, so mean values should be in a similar range — flag in a comment if wildly different, as that suggests a data issue).
- [ ] Script completes without crashing even if 1+ corrupted files are present.

**Must Not Break:** Reads from `ml/dataset/filtered/` from Prompt 9.

---

#### Prompt 12 — Document Class Imbalance

**Do:** Write `ml/dataset/CLASS_DISTRIBUTION.md` documenting the discovered class imbalance, including exact counts per class.

**Context & Why:** This written record is what later justifies the class-weighting decision in Prompt 24 and should be referenced directly in the final project report's "Dataset" section and in viva answers about how imbalance was handled (Prompt 216).

**Requirements:**
- Pull the exact per-class counts from Prompt 7's exploration output (for the 8 filtered classes specifically, not the full raw dataset).
- Present as a Markdown table: `Class | Image Count | % of Total`.
- Add a short "Observations" section: state the largest and smallest class, the ratio between them (e.g. "the most common class has 3.2x as many images as the rarest"), and whether this ratio is severe enough to warrant class weighting (a common rule of thumb: ratios above ~3:1 typically warrant weighting).
- Add a "Planned Mitigation" section referencing that `ml/preprocessing/class_weights.py` (Prompt 24) will be used to counteract this imbalance during training.

**Acceptance Criteria:**
- [ ] Table counts exactly match Prompt 9's `filtered/` folder counts (spot-check at least 3 classes).
- [ ] Document clearly states the imbalance ratio and a concrete mitigation plan, not just raw numbers with no interpretation.

**Must Not Break:** Numbers must be consistent with Prompts 7, 9, and 11 — no contradicting figures across documents.

---

#### Prompt 13 — Stratified Train/Val/Test Split

**Do:** Write `ml/dataset/split_dataset.py` that performs a stratified 70/15/15 train/val/test split and writes results into `ml/dataset/split/{train,val,test}/<class>/`.

**Context & Why:** This is the exact folder structure `ml/preprocessing/dataset_pipeline.py` (Prompt 20) will point `image_dataset_from_directory` at. Getting the split percentages, stratification, and folder naming exactly right here is load-bearing for every training and evaluation prompt that follows (26 onward).

**Requirements:**
- Use `sklearn.model_selection.train_test_split` twice (or `StratifiedShuffleSplit`) to achieve a stratified split — every class must be represented in train/val/test in roughly the same 70/15/15 proportion as its overall representation, not a flat random split that could starve a rare class from the val or test set.
- Use a fixed `random_state=42` (or documented equivalent) so the split is exactly reproducible across team members and re-runs.
- Copy (not move) files from `ml/dataset/filtered/<class>/` into `ml/dataset/split/train/<class>/`, `.../val/<class>/`, `.../test/<class>/` accordingly.
- Print a final table confirming per-class counts in each of the three splits, so imbalance-aware stratification can be visually verified.
- Must be safely re-runnable: if `ml/dataset/split/` already exists, prompt for confirmation (or accept a `--force` flag) before overwriting, to avoid accidentally re-splitting with a different random seed mid-project.

**Acceptance Criteria:**
- [ ] `ml/dataset/split/{train,val,test}/<class>/` exist for all 8 classes.
- [ ] Total files across all three splits for each class equal that class's count in `filtered/` (no images lost or duplicated).
- [ ] Split ratios are close to 70/15/15 per class (within a few percentage points, exact rounding is fine).
- [ ] Running the script twice with the same seed produces byte-for-byte identical splits.

**Must Not Break:** Source data in `ml/dataset/filtered/` from Prompt 9 must remain untouched (read-only access).

---

#### Prompt 14 — Visual Label Sanity Check

**Do:** Add a sanity-check notebook cell (in `ml/notebooks/01_dataset_exploration.ipynb`, or a new cell block clearly appended at the end) that displays 5 random sample images per class to visually confirm labels are correct.

**Context & Why:** Automated counting and hashing (Prompts 7–11) cannot catch mislabeled data — e.g., a healthy leaf accidentally filed under a disease folder during the original dataset compilation. A human glance at real samples is the only check for this, and it's cheap insurance against training a model on silently wrong labels.

**Requirements:**
- For each of the 8 classes in `ml/dataset/split/train/`, randomly sample 5 image paths (fixed seed for reproducibility) and display them in a grid using `matplotlib.pyplot.subplots` with the class name as each subplot's title.
- Use a large enough figure size that leaf detail is actually visible, not thumbnail-sized.
- Add a markdown cell immediately above asking the team to visually confirm: "Do these images look correctly labeled? Note any obvious mismatches below."
- Leave a markdown cell below for the team to record findings (even if the initial content is just "No mismatches found as of [date] — reviewed by [name]").

**Acceptance Criteria:**
- [ ] Running the cell displays a labeled grid of 40 images (5 × 8 classes) without error.
- [ ] Images are large enough to visually assess.
- [ ] A findings cell exists and is not left as a lorem-ipsum placeholder.

**Must Not Break:** Reads from `ml/dataset/split/train/` from Prompt 13.

---

#### Prompt 15 — Dataset README

**Do:** Write `ml/dataset/README.md` documenting dataset source, license, class list, and folder layout.

**Context & Why:** This closes out the dataset sub-phase with a single reference document anyone (including a viva examiner, per Prompt 216–217) can read to understand exactly what data the model was trained on, without having to reverse-engineer it from five separate scripts.

**Requirements:**
- "Source" section: name PlantVillage, link to the Kaggle dataset page, and note the license under which it's distributed (verify the actual license on Kaggle and state it accurately — do not guess).
- "Classes" section: list all 8 target classes with their exact folder names (matching Prompt 9's `TARGET_CLASSES` constant) and human-readable names (e.g. `Tomato___Early_blight` → "Tomato – Early Blight").
- "Folder Layout" section: an ASCII tree showing `raw/`, `filtered/`, `split/{train,val,test}/<class>/`, and `real_world_sample/<class>/` (the last one is created later in Prompt 51 — mention it as "populated in Phase 1.G").
- "Reproducing This Dataset" section: the exact ordered list of scripts to run from scratch (`download_dataset.py` → `filter_classes.py` → `validate_images.py` → `split_dataset.py`), so a new teammate can regenerate everything without re-reading every prompt in this library.

**Acceptance Criteria:**
- [ ] Every class folder name mentioned matches Prompt 9's constant exactly (no typos/inconsistencies).
- [ ] The reproduction steps, followed in order on a clean checkout, produce a working `ml/dataset/split/` folder.
- [ ] License information is factually accurate, not a placeholder.

**Must Not Break:** Must accurately reflect the real behavior of Prompts 6, 9, 10, 13 — update this doc if any of those scripts change later.

---
### 1.C Pre-processing Pipeline

#### Prompt 16 — Image Loader

**Do:** Create `ml/preprocessing/loader.py` implementing an image loader that reads, converts to RGB, resizes to 224×224, and normalizes pixel values to `[0,1]`.

**Context & Why:** This exact function's logic must be replicated byte-for-byte later inside `backend/app/services/preprocessing_service.py` (Prompt 87) so that a live user-uploaded image is preprocessed identically to how training images were preprocessed — any mismatch here (different resize algorithm, different normalization range, RGB vs BGR) silently degrades production accuracy without raising any error.

**Requirements:**
- Define `def load_and_preprocess_image(path_or_bytes: Union[str, bytes], target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:` accepting either a filesystem path or raw bytes (so it can be reused later for both training-time file loading and inference-time uploaded-file bytes).
- Load with PIL, explicitly `.convert("RGB")` (handles grayscale and RGBA source images uniformly).
- Resize with `PIL.Image.resize(target_size, Image.BILINEAR)` — pick and document one explicit resampling method so it stays consistent everywhere it's reused.
- Convert to a NumPy float32 array and divide by 255.0 to normalize to `[0,1]`.
- Return shape must be `(224, 224, 3)` — add an assertion checking this shape before returning.
- Raise a clear, custom exception (e.g. `ImageLoadError`) with a descriptive message on any failure (unreadable file, unsupported format) rather than letting a raw PIL exception propagate uncaught.

**Acceptance Criteria:**
- [ ] Function correctly loads a `.jpg`, `.png`, and a grayscale image, always returning `(224, 224, 3)` float32 arrays with values in `[0, 1]`.
- [ ] Passing raw bytes (not a path) works identically to passing a path.
- [ ] Passing a corrupted/invalid image raises `ImageLoadError`, not a bare `PIL.UnidentifiedImageError`.

**Must Not Break:** N/A — new module. Note: this exact function signature and behavior is a dependency for Prompt 87; do not change its resize method or normalization range without updating both places.

---

#### Prompt 17 — Augmentation Pipeline

**Do:** Create `ml/preprocessing/augmentation.py` defining a Keras augmentation pipeline with rotation, horizontal flip, zoom, translation, and brightness adjustment.

**Context & Why:** Augmentation only ever applies to the training split — applying it accidentally to validation or test data would make evaluation numbers meaningless (the model would be evaluated on artificially altered images it was never meant to be graded against).

**Requirements:**
- Build the pipeline as a `tf.keras.Sequential` of preprocessing layers: `RandomRotation(0.15)`, `RandomFlip("horizontal")`, `RandomZoom(0.1)`, `RandomTranslation(0.1, 0.1)`, `RandomBrightness(0.15)` — use reasonable, documented magnitude values for each (the ones above are sensible defaults; adjust only with a comment explaining why).
- Expose it as a single importable object: `def get_augmentation_pipeline() -> tf.keras.Sequential:`.
- Add a module-level docstring stating explicitly: "Apply this ONLY to the training dataset split. Never apply to validation or test data."
- Do not flip vertically (`RandomFlip("horizontal_and_vertical")`) — a vertically-flipped leaf image is not a realistic real-world photo orientation and would teach the model on unrealistic data.

**Acceptance Criteria:**
- [ ] Calling `get_augmentation_pipeline()(sample_batch)` on a batch of images returns a batch of the same shape with visibly altered pixel content.
- [ ] Two consecutive calls on the same input produce different outputs (confirms randomness is actually active, not a fixed no-op transform).
- [ ] No vertical flip is present in the pipeline.

**Must Not Break:** Must operate on the `(224, 224, 3)` shape and `[0,1]` value range produced by Prompt 16's loader.

---

#### Prompt 18 — Preprocessing Visual Verification Notebook

**Do:** Write `ml/notebooks/02_preprocessing_test.ipynb` that visually verifies preprocessing output on 6 sample images (before/after).

**Context & Why:** A silent bug in resize or normalization (e.g. accidentally normalizing to `[0,255]` instead of `[0,1]`, or an off-by-one crop) can train a model that looks fine in metrics but is subtly wrong — visual before/after comparison catches the class of bug that pure shape/dtype assertions in unit tests (Prompt 23) cannot.

**Requirements:**
- Load 6 sample images directly from `ml/dataset/split/train/` (2–3 different classes, not all from one class).
- For each, display a side-by-side pair: left = original image as loaded raw by PIL (no processing), right = output of Prompt 16's `load_and_preprocess_image` (remember to multiply back by 255 and cast to `uint8` only for *display* purposes — the underlying pipeline must still output `[0,1]` floats).
- Print each image's `shape` and `dtype` and `(min, max)` pixel value directly above its plot, so a numeric sanity check accompanies the visual one.
- Add a markdown conclusion cell stating whether preprocessing looks correct.

**Acceptance Criteria:**
- [ ] All 6 before/after pairs display correctly with printed shape/dtype/range matching expectations (`(224,224,3)`, `float32`, `[0.0, 1.0]`).
- [ ] Visually, the "after" images are clearly the same leaf/scene as "before," just resized — not distorted, cropped wrong, or color-shifted.

**Must Not Break:** Depends directly on Prompt 16's `load_and_preprocess_image` signature — do not reimplement loading logic separately in this notebook.

---

#### Prompt 19 — Augmentation Visual Verification

**Do:** Write a notebook cell that visually verifies augmentation output by plotting 8 augmented variants of one sample image.

**Context & Why:** Same rationale as Prompt 18 but for augmentation specifically — confirms the magnitudes chosen in Prompt 17 produce realistic variety (not so mild it's pointless, not so extreme the leaf becomes unrecognizable).

**Requirements:**
- Add this as new cells at the end of `ml/notebooks/02_preprocessing_test.ipynb` (same notebook as Prompt 18, not a separate file).
- Pick one representative sample image, load and preprocess it with Prompt 16's loader, then run it through Prompt 17's `get_augmentation_pipeline()` 8 separate times (each call producing a different random augmentation).
- Display all 8 results in a 2×4 grid alongside the original for reference (9 images total).
- Add a markdown cell asking the team to visually confirm: are the augmented images still clearly recognizable as the same disease class? Flag if any look unrealistically distorted.

**Acceptance Criteria:**
- [ ] Grid displays 8 distinct-looking augmented variants plus the original.
- [ ] None of the 8 variants is an exact duplicate of another (confirms randomness across repeated calls).
- [ ] Leaf subject remains identifiable as the correct class in all 8 variants (a human reviewer's judgment call, recorded in the markdown cell).

**Must Not Break:** Depends on both Prompt 16 (loader) and Prompt 17 (augmentation pipeline) with their exact existing signatures.

---

#### Prompt 20 — `tf.data` Dataset Pipeline

**Do:** Create `ml/preprocessing/dataset_pipeline.py` that builds `tf.data.Dataset` objects for train/val/test using `image_dataset_from_directory`.

**Context & Why:** This is the single function every training script (Prompts 27, 35, 38) and evaluation script (Prompts 31, 44) will call to get consistent, correctly-labeled datasets — centralizing it here prevents each training script from re-implementing (and potentially inconsistently re-implementing) dataset loading.

**Requirements:**
- Define `def build_datasets(split_dir: str = "ml/dataset/split", image_size=(224,224), batch_size=32) -> Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset, List[str]]:` returning `(train_ds, val_ds, test_ds, class_names)`.
- Use `tf.keras.utils.image_dataset_from_directory` three times, pointed at `split_dir/train`, `split_dir/val`, `split_dir/test` respectively, with `label_mode="categorical"` (one-hot, matching the categorical cross-entropy loss planned for Prompt 27), `image_size=image_size`, `batch_size=batch_size`, and a fixed `seed=42` for shuffling determinism on the train set only (val/test should have `shuffle=False` so evaluation results are always reproducible and comparable across runs).
- Extract `class_names` from the train dataset (`train_ds.class_names`) and assert that val and test datasets report the identical class list and ordering — raise an error immediately if they don't (this would silently corrupt every prediction's label mapping downstream).
- Rescale pixel values to `[0,1]` inside this pipeline via a `Rescaling(1./255)` layer applied with `.map()`, consistent with Prompt 16's normalization range.
- Do NOT apply augmentation inside this function — that happens separately, only on `train_ds`, wherever it's used in the training scripts (keeps this function reusable for both training and pure evaluation contexts).

**Acceptance Criteria:**
- [ ] `build_datasets()` returns three `tf.data.Dataset` objects and a list of exactly 8 class name strings.
- [ ] `train_ds`, `val_ds`, `test_ds` all report identical `class_names` in identical order.
- [ ] Iterating one batch from any of the three datasets yields images shaped `(batch_size, 224, 224, 3)` with values in `[0,1]`, and labels shaped `(batch_size, 8)` one-hot.

**Must Not Break:** Reads from `ml/dataset/split/` from Prompt 13; class count/order must match Prompt 43's `class_names.json` once that's generated later (flag this dependency in a code comment for future reference).

---

#### Prompt 21 — Batching and Prefetching Performance Config

**Do:** Add batching and prefetching (`.batch()`, `.prefetch(AUTOTUNE)`) configuration to the `tf.data.Dataset` pipeline for performance.

**Context & Why:** Without prefetching, GPU training (Prompts 27+) stalls waiting on CPU-bound image decoding/resizing between batches — on Colab this can roughly double wall-clock training time for no benefit.

**Requirements:**
- Modify `ml/preprocessing/dataset_pipeline.py`'s `build_datasets` function (do not create a separate file) to chain `.prefetch(tf.data.AUTOTUNE)` onto all three returned datasets before returning them.
- Note that `.batch()` is already applied by `image_dataset_from_directory` in Prompt 20 via its `batch_size` argument — do not double-batch; just confirm/document that this is already handled, and only add the missing `.prefetch()` step.
- Optionally add `.shuffle(buffer_size=...)` with a sensible buffer size (e.g. 1000) specifically to `train_ds` if shuffling quality with the default `image_dataset_from_directory` shuffle seems insufficient for very large datasets — document the decision either way in a code comment.

**Acceptance Criteria:**
- [ ] All three returned datasets have `.prefetch(tf.data.AUTOTUNE)` applied as the final pipeline step.
- [ ] A quick timing comparison (documented in a code comment or the module docstring) shows measurably faster batch-fetch time with prefetching enabled vs. disabled.

**Must Not Break:** Must not change the function signature or return types established in Prompt 20 — this is purely a performance enhancement to the same function.

---

#### Prompt 22 — Caching for Validation and Test Sets

**Do:** Add a caching layer (`.cache()`) to the pipeline for the validation and test sets to speed up repeated evaluation runs.

**Context & Why:** Validation runs once per training epoch (potentially dozens of times per training run across Prompts 27–39) and the test set is re-evaluated repeatedly across Prompts 31, 40, 44–49 — caching the decoded/resized images in memory (or to disk if the dataset is too large for RAM) avoids re-decoding the same JPEG files from scratch every single time.

**Requirements:**
- In `ml/preprocessing/dataset_pipeline.py`, add `.cache()` to `val_ds` and `test_ds` (positioned correctly in the chain — after the initial load/rescale mapping, before `.prefetch()`), but explicitly do NOT cache `train_ds` if training-time augmentation will be applied to it later (caching before augmentation would freeze augmented results instead of regenerating fresh random augmentations each epoch — leave a comment explaining this exclusion).
- Support an optional `cache_to_disk: bool = False` parameter — when `True`, use `.cache(filename="...")` pointing at a temp path instead of in-memory caching, for environments with limited RAM (relevant on some Colab tiers).
- Document memory implications in a docstring: in-memory caching duplicates the entire val/test dataset in RAM after the first pass.

**Acceptance Criteria:**
- [ ] Second and subsequent epochs' validation step is measurably faster than the first epoch's validation step in an actual training run (spot-checked once during Prompt 27's training).
- [ ] `train_ds` is confirmed NOT cached (verify no `.cache()` call appears before augmentation is applied to it in the training scripts).
- [ ] `cache_to_disk=True` works without error and produces a cache file at the given path.

**Must Not Break:** Must preserve Prompt 20's return signature and Prompt 21's prefetching — caching is inserted into the existing chain, not a replacement for it.

---

#### Prompt 23 — Loader Unit Tests

**Do:** Write unit tests `ml/preprocessing/test_loader.py` verifying output image shape and pixel-value range.

**Context & Why:** This is the first automated (not just visual/manual) safety net for the preprocessing logic that Prompt 87 will later duplicate in the backend — a failing test here should be the first signal if someone accidentally changes `loader.py` in a way that would silently break production inference.

**Requirements:**
- Use `pytest` as the test framework (add `pytest` to `ml/requirements.txt` if not already present from an earlier prompt — cross-check and add if missing).
- Test 1: loading a known valid sample image returns shape exactly `(224, 224, 3)`.
- Test 2: returned array's dtype is `float32` (or `float64` — pick one and assert it consistently; document the choice).
- Test 3: all pixel values are within `[0.0, 1.0]` inclusive (`assert arr.min() >= 0.0 and arr.max() <= 1.0`).
- Test 4: loading a corrupted/invalid image path raises the custom `ImageLoadError` from Prompt 16, not an unhandled exception.
- Test 5: loading the same image via a file path vs. via raw bytes produces identical output arrays (`np.allclose`).
- Include a small fixtures folder `ml/preprocessing/test_fixtures/` with 1–2 tiny sample images (a valid one and a deliberately corrupted one) committed to Git specifically for these tests, so they don't depend on the full (gitignored) dataset being present.

**Acceptance Criteria:**
- [ ] `pytest ml/preprocessing/test_loader.py` passes all 5 tests.
- [ ] Tests run successfully on a fresh checkout with only `ml/requirements.txt` installed — no dependency on the full downloaded dataset.
- [ ] Deliberately breaking `loader.py` (e.g. commenting out the `/255.0` normalization) causes Test 3 to fail, confirming the test is actually meaningful and not a false-positive tautology.

**Must Not Break:** Tests must exactly match Prompt 16's real function signature and exception type — update tests if that module's public interface changes.

---

#### Prompt 24 — Class Weight Computation

**Do:** Add class-weight computation `ml/preprocessing/class_weights.py` using `sklearn.utils.class_weight` to address the imbalance documented in Prompt 12.

**Context & Why:** This module's output is passed directly into `model.fit(..., class_weight=...)` in Prompts 27 and 35 — without it, the model would be biased toward over-predicting whichever class has the most training images, which for an agricultural diagnosis tool means systematically under-detecting rarer (potentially more severe) diseases.

**Requirements:**
- Define `def compute_class_weights(train_ds_dir: str = "ml/dataset/split/train", class_names: List[str] = None) -> Dict[int, float]:` that counts images per class directly from the training split's folder structure (not by iterating the `tf.data.Dataset`, which is more error-prone for exact counting) and computes balanced weights via `sklearn.utils.class_weight.compute_class_weight(class_weight="balanced", classes=..., y=...)`.
- Return a dictionary keyed by integer class index (matching the index order from `class_names`, which must be passed in or independently derived in the exact same sorted order `image_dataset_from_directory` uses — alphabetical by folder name — to avoid a silent index/label mismatch).
- Print the computed weight per class name (not just index) so a human can sanity-check that the rarer classes (identified in Prompt 12) receive weights greater than 1.0 and the most common class receives a weight close to or below 1.0.
- Add a warning/assertion if any computed weight is above a suspicious threshold (e.g. 10.0), which would indicate the imbalance is severe enough that class weighting alone may be insufficient (worth flagging for potential oversampling instead, as a documented consideration even if not implemented).

**Acceptance Criteria:**
- [ ] Function returns a dict with exactly 8 integer keys (0–7), each mapping to a positive float weight.
- [ ] Printed class-name-to-weight mapping shows rarer classes (per Prompt 12's findings) receiving weights above 1.0.
- [ ] Weights sum/average in a way consistent with sklearn's standard "balanced" formula (spot-check the math for at least one class by hand).

**Must Not Break:** Class index ordering here must exactly match the ordering `image_dataset_from_directory` (Prompt 20) and `class_names.json` (Prompt 43) use — this is a common, easy-to-introduce silent bug; add an explicit code comment warning about this.

---

#### Prompt 25 — Preprocessing README

**Do:** Document the full preprocessing pipeline (steps + rationale) in `ml/preprocessing/README.md`.

**Context & Why:** Closes out sub-phase 1.C with a single reference explaining exactly what happens to an image between "file on disk" and "tensor fed to the model" — this is the document Prompt 87's backend implementation should be checked against line-by-line to guarantee training/inference parity.

**Requirements:**
- "Pipeline Steps" section, in exact order: load → convert to RGB → resize to 224×224 (bilinear) → normalize to `[0,1]` → (training only) augment → batch → prefetch → (val/test only) cache.
- "Why These Choices" subsection explaining briefly: why 224×224 (matches MobileNetV2's expected input size, relevant ahead of Prompt 34), why `[0,1]` normalization rather than the `[-1,1]` or ImageNet-mean-subtracted normalization some pretrained models expect (and a note-to-self to double check MobileNetV2's actual expected preprocessing in Prompt 34 — TensorFlow's `MobileNetV2` application may require its own `preprocess_input` function rather than a plain `/255.0` rescale; flag this explicitly as an open item to verify).
- "Class Imbalance Handling" subsection linking to `ml/dataset/CLASS_DISTRIBUTION.md` (Prompt 12) and `ml/preprocessing/class_weights.py` (Prompt 24).
- "Files in This Module" subsection listing `loader.py`, `augmentation.py`, `dataset_pipeline.py`, `class_weights.py`, `test_loader.py` each with a one-line description.
- "Parity With Production" subsection explicitly stating: "The backend's `preprocessing_service.py` (Phase 2) must replicate the load → RGB → resize → normalize steps exactly. Augmentation, caching, and batching are training-only concerns and must NOT appear in the production inference path."

**Acceptance Criteria:**
- [ ] Document accurately reflects the real behavior of all files in `ml/preprocessing/` as of this point (cross-check against actual code, not assumptions).
- [ ] The MobileNetV2 preprocessing caveat is explicitly flagged as something to verify in Prompt 34, not silently glossed over.
- [ ] Anyone reading only this file (without reading the code) could correctly re-implement equivalent preprocessing logic elsewhere.

**Must Not Break:** Must stay in sync with Prompts 16, 17, 20, 24 — update this README in the same commit if any of those files' behavior changes later.

---
### 1.D Baseline CNN

#### Prompt 26 — Baseline CNN Architecture

**Do:** Create `ml/training/baseline_cnn.py` defining a simple CNN architecture (3–4 Conv2D+MaxPooling blocks, Dense head) using the Keras Sequential API.

**Context & Why:** This baseline exists specifically to be compared against the transfer-learning models in Prompt 40 — its purpose is to prove (quantitatively, in the final report) that transfer learning is a justified architectural choice rather than an unnecessarily complex one, which directly answers the anticipated viva question in Prompt 216 ("why transfer learning?").

**Requirements:**
- Define `def build_baseline_cnn(input_shape=(224,224,3), num_classes=8) -> tf.keras.Model:`.
- Architecture: 3–4 blocks each of `Conv2D` (increasing filter counts, e.g. 32 → 64 → 128 → optionally 256) + `ReLU` activation + `MaxPooling2D(2,2)`, followed by `Flatten` (or `GlobalAveragePooling2D`, preferred to reduce parameter count), then one `Dense` hidden layer (e.g. 128 units, ReLU), then a final `Dense(num_classes, activation="softmax")` output layer.
- Keep this deliberately simple — no batch normalization, no residual connections, no pretrained weights — it must represent a genuine "from scratch, no transfer learning" baseline for a fair comparison.
- Print `model.summary()` when the module is run directly (`if __name__ == "__main__":`) so parameter count is visible for the comparison table in Prompt 40.
- Add a module docstring explaining this model's purpose is explicitly a comparison baseline, not the production candidate.

**Acceptance Criteria:**
- [ ] `build_baseline_cnn()` returns a compilable `tf.keras.Model` accepting `(None, 224, 224, 3)` input and outputting `(None, 8)`.
- [ ] `model.summary()` runs without error and shows 3–4 conv blocks.
- [ ] Total parameter count is reasonable for a "simple" baseline (expect low single-digit millions, not tens of millions — flag in a comment if it's far outside this range).

**Must Not Break:** N/A — new file, but output shape (8 classes) must match Prompt 20's `class_names` count.

---

#### Prompt 27 — Baseline Training Script

**Do:** Write `ml/training/train_baseline.py` that compiles the baseline model (Adam optimizer, categorical cross-entropy) and trains it for 15 epochs on the train/val datasets.

**Context & Why:** This is the first end-to-end training run of the whole project — it validates that every piece built so far (dataset split, preprocessing pipeline, class weights, model architecture) actually works together before any more complex transfer-learning code is written on top of it.

**Requirements:**
- Import `build_datasets` from Prompt 20's `dataset_pipeline.py` and `build_baseline_cnn` from Prompt 26.
- Import and apply Prompt 17's augmentation pipeline to `train_ds` only (via `.map()`), never to `val_ds`/`test_ds`.
- Compile with `optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3)` (or a documented alternative), `loss="categorical_crossentropy"`, `metrics=["accuracy"]`.
- Call `model.fit(train_ds, validation_data=val_ds, epochs=15, class_weight=compute_class_weights(...))` using Prompt 24's class weights.
- Log training history (the `History` object) to disk as `ml/training/baseline_history.json` (convert the numpy arrays in `history.history` to plain lists before JSON-serializing) so Prompt 29 can plot curves without needing to re-run training.
- Print a final line summarizing best validation accuracy achieved and at which epoch.

**Acceptance Criteria:**
- [ ] Script runs to completion for 15 epochs without crashing, on both a CPU-only environment (slow but functional) and a GPU Colab session.
- [ ] `ml/training/baseline_history.json` exists and contains `loss`, `accuracy`, `val_loss`, `val_accuracy` keys, each a list of 15 values.
- [ ] Training and validation accuracy both trend upward over the 15 epochs (not flat/random, which would indicate a pipeline bug rather than just a weak model).

**Must Not Break:** Must use Prompt 20's `build_datasets`, Prompt 26's `build_baseline_cnn`, Prompt 17's augmentation, and Prompt 24's class weights exactly as those modules currently expose them — do not fork/duplicate their logic inline in this script.

---

#### Prompt 28 — Callbacks: TensorBoard, Checkpointing, Early Stopping

**Do:** Add TensorBoard logging and Keras `ModelCheckpoint`/`EarlyStopping` callbacks to `train_baseline.py`.

**Context & Why:** 15 fixed epochs risk either wasting compute on a model that already plateaued, or (less likely here, more likely in Prompt 36's fine-tuning phase) overfitting past the point where validation performance was best — these callbacks make training self-correcting instead of relying on a hardcoded epoch count as the sole stopping condition.

**Requirements:**
- Add `tf.keras.callbacks.TensorBoard(log_dir="ml/training/logs/baseline_<timestamp>")` (use an actual timestamp so repeated runs don't overwrite each other's logs).
- Add `tf.keras.callbacks.ModelCheckpoint(filepath="ml/models/baseline_cnn_checkpoint.keras", monitor="val_accuracy", save_best_only=True)` so the best-epoch weights are preserved even if a later epoch overfits.
- Add `tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True)` so training halts automatically if validation loss stops improving for 4 consecutive epochs.
- Pass all three callbacks into the existing `model.fit(..., callbacks=[...])` call from Prompt 27 — do not restructure the rest of the training loop.
- Print a note on how to launch TensorBoard locally (`tensorboard --logdir ml/training/logs`) in a code comment or the script's docstring.

**Acceptance Criteria:**
- [ ] `ml/models/baseline_cnn_checkpoint.keras` is created/updated during training and reflects the best validation-accuracy epoch, not necessarily the final epoch.
- [ ] `ml/training/logs/` contains timestamped TensorBoard event files after a run.
- [ ] Deliberately triggering early stopping (e.g. by testing with an intentionally low patience value) correctly halts training before all 15 epochs complete.

**Must Not Break:** Must integrate into the exact `model.fit()` call from Prompt 27 without changing its other arguments (`class_weight`, `validation_data`, etc.).

---

#### Prompt 29 — Training Curve Plots

**Do:** Write `ml/evaluation/plot_training_curves.py` that plots training/validation accuracy and loss curves and saves them as PNGs.

**Context & Why:** These plots are the primary evidence used in Prompt 32's overfitting analysis and are strong candidates for direct inclusion in the final project report and presentation as evidence of a properly-trained (not overfit, not underfit) model.

**Requirements:**
- Define `def plot_curves(history_json_path: str, output_prefix: str) -> None:` that loads a history JSON (matching the schema written by Prompt 27) and produces two separate PNGs: `{output_prefix}_accuracy.png` (train vs. val accuracy across epochs) and `{output_prefix}_loss.png` (train vs. val loss across epochs).
- Each plot: x-axis "Epoch", y-axis the relevant metric name, a legend distinguishing "Training" vs. "Validation" lines, and a descriptive title.
- Make the function generic enough (via the `history_json_path`/`output_prefix` parameters) to reuse later for the transfer-learning models in Prompts 35/36 without rewriting this script — call it with different arguments rather than duplicating it.
- Save at ≥150 DPI into `ml/evaluation/`.

**Acceptance Criteria:**
- [ ] Running `plot_curves("ml/training/baseline_history.json", "ml/evaluation/baseline")` produces `ml/evaluation/baseline_accuracy.png` and `ml/evaluation/baseline_loss.png`.
- [ ] Both plots clearly show separate, correctly-labeled train and validation lines.
- [ ] The same function, called later with the transfer-learning history file, works without modification.

**Must Not Break:** Must match the exact JSON key names (`loss`, `accuracy`, `val_loss`, `val_accuracy`) written by Prompt 27's history-saving logic.

---

#### Prompt 30 — Save Baseline Model

**Do:** Run the baseline training and save the resulting model to `ml/models/baseline_cnn.keras`.

**Context & Why:** This is an explicit "checkpoint the deliverable" step distinct from Prompt 28's best-epoch checkpoint file — `baseline_cnn.keras` is the final, official baseline artifact referenced by name in Prompt 40's comparison script, so it needs a stable, predictable filename independent of the timestamped checkpoint logic.

**Requirements:**
- After `train_baseline.py` (Prompts 27–28) completes a full run, explicitly save the final (post-early-stopping, best-weights-restored) model with `model.save("ml/models/baseline_cnn.keras")` — add this line to the end of `train_baseline.py` itself so it happens automatically on every run, rather than being a separate manual step.
- Confirm this differs in purpose from `ml/models/baseline_cnn_checkpoint.keras` (Prompt 28): the checkpoint file is an intermediate safety net during training, `baseline_cnn.keras` is the definitive saved artifact for downstream comparison.
- Verify the saved file loads back correctly with `tf.keras.models.load_model()` and produces the same predictions on a sample batch as the in-memory model did immediately after training (a quick round-trip sanity check, printed to stdout).

**Acceptance Criteria:**
- [ ] `ml/models/baseline_cnn.keras` exists after a training run.
- [ ] Reloading it and predicting on a fixed test batch gives outputs numerically identical (within floating-point tolerance) to the pre-save in-memory model's predictions on that same batch.

**Must Not Break:** Must not overwrite `baseline_cnn_checkpoint.keras` from Prompt 28 — the two files serve different purposes and both should exist afterward.

---

#### Prompt 31 — Baseline Test-Set Evaluation

**Do:** Evaluate the baseline model on the test set and log accuracy/loss to `ml/evaluation/baseline_results.json`.

**Context & Why:** This is the first genuinely held-out performance number for the project — the test set has not been touched by training or validation-based early stopping/checkpointing decisions, so this number is what should actually be quoted (with appropriate humility, given it's "just" the baseline) if anyone asks "so what accuracy did you get?" before the final model is ready.

**Requirements:**
- Load `ml/models/baseline_cnn.keras` (Prompt 30) and the `test_ds` from Prompt 20's `build_datasets`.
- Call `model.evaluate(test_ds, return_dict=True)` and capture the resulting `{"loss": ..., "accuracy": ...}` dict.
- Write this dict, plus a timestamp and the model filename, to `ml/evaluation/baseline_results.json`.
- Print the results to stdout in a human-readable sentence (e.g. "Baseline CNN — Test Accuracy: 78.3%, Test Loss: 0.612").

**Acceptance Criteria:**
- [ ] `ml/evaluation/baseline_results.json` exists with `loss`, `accuracy`, `timestamp`, `model_file` keys.
- [ ] The reported test accuracy is a plausible number for a from-scratch CNN on this dataset size (not suspiciously at or near 100%, which would suggest data leakage between splits — cross-check against Prompt 13's split logic if so).

**Must Not Break:** Must use the exact `test_ds` from Prompt 20, never the train or val splits, for this evaluation.

---

#### Prompt 32 — Baseline Overfitting/Underfitting Analysis

**Do:** Write a short analysis note `ml/evaluation/baseline_analysis.md` documenting observed overfitting/underfitting behavior from the curves.

**Context & Why:** This written analysis is what turns raw plots (Prompt 29) into an actual finding the team understands and can speak to in the viva (Prompt 216's "what is overfitting" question should be answerable with a concrete, real example from this exact project, not just a textbook definition).

**Requirements:**
- Reference the actual accuracy/loss plots from Prompt 29 (embed or link the PNG files).
- Explicitly diagnose the observed pattern: if validation loss starts increasing while training loss keeps decreasing, call this out as overfitting and note the approximate epoch where divergence begins; if both train and val accuracy plateau at a low, similar value, call this out as underfitting instead; if curves track closely together with both improving, state that no significant overfitting/underfitting was observed for this configuration.
- Tie the diagnosis back to the actual test-set result from Prompt 31 — e.g., a large gap between validation accuracy (during training) and test accuracy could indicate the val set itself was too small or not representative.
- Include one sentence framing this as the direct motivation for the Prompt 33 regularization variant (if overfitting was observed) or a note that regularization may be unnecessary (if it wasn't).

**Acceptance Criteria:**
- [ ] Document makes a clear, specific diagnosis (not a vague "the model performed okay") backed by concrete epoch numbers or accuracy values from the actual run.
- [ ] Explicitly recommends whether Prompt 33's regularization variant is necessary, and why.

**Must Not Break:** Must accurately describe the real curves from Prompt 29 and real numbers from Prompt 31 — do not write a generic analysis that doesn't match the actual data.

---

#### Prompt 33 — Regularized Baseline Variant (Conditional)

**Do:** If overfitting was observed in Prompt 32, add dropout and L2 regularization to a second baseline variant `ml/training/baseline_cnn_v2.py` and re-train.

**Context & Why:** This prompt is explicitly conditional — only execute it if Prompt 32's analysis actually diagnosed overfitting. If underfitting or a well-fit baseline was found instead, skip this prompt's implementation and instead write a one-paragraph note in `ml/evaluation/baseline_analysis.md` explaining why it was skipped, so the project's documentation trail stays honest and complete either way.

**Requirements (if executing):**
- Copy `baseline_cnn.py`'s architecture into a new `build_baseline_cnn_v2()` function inside `ml/training/baseline_cnn_v2.py`, adding `Dropout(0.3–0.5)` after the dense hidden layer and/or after pooling blocks, and adding `kernel_regularizer=tf.keras.regularizers.l2(1e-4)` to the Conv2D and/or Dense layers.
- Reuse the exact same training script logic from Prompt 27–28 (import and call this new architecture instead of forking the whole training script) — create a thin `train_baseline_v2.py` that imports shared training logic if practical, or clearly documents that it deliberately duplicates `train_baseline.py` with only the model-building import changed.
- Re-run training, re-plot curves (reusing Prompt 29's generic `plot_curves` function with a new `output_prefix="baseline_v2"`), and re-evaluate on the test set (reusing Prompt 31's evaluation logic, writing to `ml/evaluation/baseline_v2_results.json`).
- Add a short comparison paragraph to `ml/evaluation/baseline_analysis.md` stating whether v2 measurably reduced the overfitting gap and whether test accuracy improved, stayed flat, or dropped.

**Acceptance Criteria:**
- [ ] If executed: `ml/models/baseline_cnn_v2.keras`, updated curve plots, and `baseline_v2_results.json` all exist, and the analysis doc quantifies the before/after difference.
- [ ] If skipped: `ml/evaluation/baseline_analysis.md` contains an explicit, reasoned statement that this step was intentionally skipped and why — never simply silent/absent with no explanation.

**Must Not Break:** Must not overwrite or delete `baseline_cnn.keras` / `baseline_results.json` from Prompts 30–31 — both baseline versions (original and, if applicable, v2) should exist side by side for the comparison in Prompt 40.

---
### 1.E Transfer Learning

#### Prompt 34 — MobileNetV2 Transfer-Learning Model

**Do:** Create `ml/training/transfer_mobilenetv2.py` that loads MobileNetV2 with ImageNet weights, freezes the base, and attaches a new classification head for 8 classes.

**Context & Why:** This is the architecture the project report names as the intended production model — get its preprocessing and freezing logic right here, since it is what Prompt 42 will ultimately promote to `crop_disease_model.keras`.

**Requirements:**
- Define `def build_mobilenetv2_model(input_shape=(224,224,3), num_classes=8) -> tf.keras.Model:`.
- Load the base with `tf.keras.applications.MobileNetV2(input_shape=input_shape, include_top=False, weights="imagenet")` and set `base_model.trainable = False` (frozen for this first phase).
- **Resolve the preprocessing caveat flagged in Prompt 25**: MobileNetV2's ImageNet weights expect inputs preprocessed via `tf.keras.applications.mobilenet_v2.preprocess_input` (which scales to `[-1,1]`), NOT the plain `[0,1]` scaling used elsewhere in this project's pipeline. Explicitly handle this by inserting a `Lambda` layer (or equivalent) at the start of this model that takes the pipeline's standard `[0,1]` input and rescales it internally to `[-1,1]` before it reaches the MobileNetV2 base — this way `dataset_pipeline.py` (Prompt 20) does not need a special case for this one model, and the conversion is self-contained here. Document this clearly in a code comment since it's easy to silently get wrong.
- Attach a new head on top of the frozen base: `GlobalAveragePooling2D()` → `Dropout(0.3)` → `Dense(num_classes, activation="softmax")`.
- Print `model.summary()` when run directly, and explicitly print the count of trainable vs. non-trainable parameters so the "base is frozen" claim is visibly verifiable.

**Acceptance Criteria:**
- [ ] `model.summary()` shows the MobileNetV2 base's parameters listed as non-trainable and only the new head's parameters as trainable.
- [ ] Passing a `[0,1]`-range input batch (matching Prompt 20's pipeline output) through the full model produces valid `(batch, 8)` softmax outputs summing to ~1.0 per row, confirming the internal `[-1,1]` rescale is correctly wired.

**Must Not Break:** Must accept the same `(224,224,3)`, `[0,1]`-range input that Prompt 20's `build_datasets` produces — do not require callers of this model to pre-rescale their input.

---

#### Prompt 35 — Train the MobileNetV2 Head (Frozen Base)

**Do:** Write `ml/training/train_transfer.py` to train the new classification head for 10 epochs while the base is frozen.

**Context & Why:** Training only the new head first (before any fine-tuning) prevents large, randomly-initialized gradients from the new head from destructively backpropagating into and corrupting the carefully pretrained MobileNetV2 weights — this staged approach is standard transfer-learning practice and should be named as such in any viva answer (Prompt 216).

**Requirements:**
- Import `build_mobilenetv2_model` from Prompt 34, `build_datasets` from Prompt 20, augmentation from Prompt 17 (train split only), and class weights from Prompt 24.
- Compile with `Adam(learning_rate=1e-3)` (a relatively higher rate is fine here since only the small new head is training), `categorical_crossentropy`, `["accuracy"]`.
- Train for 10 epochs with the same callback set pattern as Prompt 28 (TensorBoard, ModelCheckpoint monitoring `val_accuracy`, EarlyStopping on `val_loss`), logged to a distinctly-named directory (`ml/training/logs/transfer_head_<timestamp>`) and checkpoint file (`ml/models/mobilenetv2_head_checkpoint.keras`) so these don't collide with the baseline's logs/checkpoints from Prompt 28.
- Save history to `ml/training/transfer_head_history.json` using the same schema as Prompt 27, so Prompt 29's generic `plot_curves` function works unmodified on it.

**Acceptance Criteria:**
- [ ] Script trains for up to 10 epochs (or fewer if early stopping triggers) without error.
- [ ] `ml/training/transfer_head_history.json` exists with the standard schema.
- [ ] Validation accuracy after this phase is measurably higher than the frozen-base model's accuracy would be with random head weights (sanity check: should clearly be learning, not stuck near random-guess accuracy of ~12.5% for 8 classes).

**Must Not Break:** Must not modify or overwrite any baseline-phase files from Prompts 26–33.

---

#### Prompt 36 — Fine-Tuning Phase

**Do:** Extend `train_transfer.py` with a fine-tuning phase: unfreeze the top N layers of MobileNetV2 and continue training at a lower learning rate for 10 more epochs.

**Context & Why:** Fine-tuning lets the top layers of the pretrained network (which encode more dataset-specific high-level features, as opposed to the generic low-level edge/texture features in early layers) adapt specifically to crop-leaf imagery, typically yielding a meaningful accuracy boost over the frozen-base-only result from Prompt 35 — this is the single most important experiment in the whole ML phase for this reason.

**Requirements:**
- After Prompt 35's head-training phase completes (continuing in the same script, loading the just-trained model/weights rather than starting from scratch), set `base_model.trainable = True`, then explicitly re-freeze all layers except the last N (a reasonable starting point: N = 30–40 layers, or unfreeze from a named block onward, e.g. everything from `"block_13"` onward for MobileNetV2 — pick a concrete, documented value rather than leaving it vague).
- **Critical**: recompile the model after changing `trainable` flags (Keras requires this for the change to take effect) with a much lower learning rate this time, e.g. `Adam(learning_rate=1e-5)` — fine-tuning at the same 1e-3 rate used for head-only training would rapidly destroy the pretrained weights' useful features.
- Continue training for 10 more epochs with the same callback pattern, using distinctly-named logs/checkpoints (e.g. `ml/training/logs/transfer_finetune_<timestamp>`, `ml/models/mobilenetv2_finetune_checkpoint.keras`) and a separate history file `ml/training/transfer_finetune_history.json`.
- Print a clear before/after comparison at the end of the script: head-only validation accuracy (from Prompt 35's run) vs. post-fine-tuning validation accuracy.

**Acceptance Criteria:**
- [ ] The script correctly recompiles the model after unfreezing (verify by checking the trainable parameter count increased compared to Prompt 35's model summary).
- [ ] Fine-tuning improves (or at minimum does not substantially degrade) validation accuracy compared to the head-only phase — if it degrades performance, this must be explicitly noted for `ml/evaluation/MODEL_SELECTION.md` (Prompt 41) rather than silently hidden.
- [ ] Learning rate used for fine-tuning is confirmed lower than the head-training phase's rate (verify in logs/printed output).

**Must Not Break:** Must build on top of Prompt 35's trained weights (load them, don't restart from ImageNet-only weights), and must not corrupt `mobilenetv2_head_checkpoint.keras` — save fine-tuning outputs under distinct filenames.

---

#### Prompt 37 — Save Final MobileNetV2 Model

**Do:** Save the trained transfer-learning model to `ml/models/mobilenetv2_final.keras`.

**Context & Why:** Same rationale as Prompt 30 — a stable, unambiguous filename for the fully-trained (head + fine-tuned) MobileNetV2 model, independent of the intermediate checkpoint files from Prompts 35–36, to be fed into Prompt 40's comparison.

**Requirements:**
- After Prompt 36's fine-tuning phase completes, save the resulting model (with `EarlyStopping(restore_best_weights=True)` already having restored the best fine-tuning-phase weights) via `model.save("ml/models/mobilenetv2_final.keras")`.
- Perform the same reload-and-verify round-trip sanity check described in Prompt 30 (predict on a fixed sample batch before and after save/reload, confirm numerical match).

**Acceptance Criteria:**
- [ ] `ml/models/mobilenetv2_final.keras` exists and is the fine-tuned (not merely head-trained) version of the model.
- [ ] Round-trip prediction check passes.

**Must Not Break:** Must not overwrite `baseline_cnn.keras` (Prompt 30) or any of the intermediate checkpoint files from Prompts 28, 35, 36 — all should coexist for the comparison step.

---

#### Prompt 38 — ResNet50 Comparison Variant

**Do:** Create `ml/training/transfer_resnet50.py` implementing the same transfer-learning approach using ResNet50 as a comparison architecture.

**Context & Why:** A single transfer-learning result (MobileNetV2 alone) doesn't demonstrate that architecture choice was deliberate — training a second, well-known alternative under the identical protocol strengthens the "why this model" justification in `MODEL_SELECTION.md` (Prompt 41) with real comparative evidence rather than an assumption that MobileNetV2 was simply the first thing tried.

**Requirements:**
- Mirror Prompt 34's structure exactly but with `tf.keras.applications.ResNet50(input_shape=(224,224,3), include_top=False, weights="imagenet")` as the base.
- **Handle ResNet50's own distinct preprocessing requirement** the same deliberate way Prompt 34 handled MobileNetV2's: use `tf.keras.applications.resnet50.preprocess_input` semantics (ResNet50's Keras application expects caffe-style BGR mean-subtraction, not `[-1,1]` or `[0,1]`) wrapped in a `Lambda`/preprocessing layer inside this model, converting from the pipeline's standard `[0,1]` input internally — do not assume the same `[-1,1]` conversion used for MobileNetV2 applies here; verify ResNet50's actual expected preprocessing in the TensorFlow documentation and implement that specific transformation.
- Follow the same two-phase training protocol as Prompts 35–36 (frozen head training, then fine-tuning the top N layers at a lower learning rate) inside this same script or a clearly paired `train_resnet50.py`, with distinctly-named logs, checkpoints, and history files (following the `resnet50_*` naming pattern, parallel to the `mobilenetv2_*`/`transfer_*` naming used for the other model).

**Acceptance Criteria:**
- [ ] Model builds, trains (head phase + fine-tune phase), and produces valid predictions without shape or preprocessing errors.
- [ ] The preprocessing wrapper is verified correct (not copy-pasted from the MobileNetV2 version without adjustment) — spot-check by confirming the Lambda layer's transformation matches ResNet50's documented expected input format.
- [ ] History files use the same JSON schema as the other training scripts so `plot_curves` (Prompt 29) works unmodified.

**Must Not Break:** Must not interfere with any MobileNetV2 or baseline files — entirely separate model/checkpoint/log/history filenames throughout.

---

#### Prompt 39 — Save Final ResNet50 Model

**Do:** Train and save the ResNet50 variant to `ml/models/resnet50_final.keras`.

**Context & Why:** Completes the third and final candidate model needed for Prompt 40's three-way comparison table.

**Requirements:**
- Same save-and-verify pattern as Prompts 30 and 37, applied to the fully trained (head + fine-tuned) ResNet50 model from Prompt 38.
- Confirm the saved file's size and the model's total parameter count are recorded somewhere accessible (e.g. printed to stdout and/or written to a small metadata note) for direct use in Prompt 40's comparison table, since ResNet50 is a substantially larger network than MobileNetV2 and this difference is itself a relevant comparison data point (inference speed, deployment size).

**Acceptance Criteria:**
- [ ] `ml/models/resnet50_final.keras` exists, round-trip verified.
- [ ] File size and parameter count are known/recorded ahead of Prompt 40.

**Must Not Break:** All three final candidate models (`baseline_cnn.keras`, `mobilenetv2_final.keras`, `resnet50_final.keras`, plus optionally `baseline_cnn_v2.keras`) must exist simultaneously at this point.

---

#### Prompt 40 — Three-Way Model Comparison

**Do:** Write `ml/evaluation/compare_models.py` that loads baseline, MobileNetV2, and ResNet50 models and compares their test-set accuracy, inference time, and file size in a single table.

**Context & Why:** This script produces the definitive, objective evidence behind the model-selection decision documented in Prompt 41 — every number in that decision document should trace back to this script's output, not to informal impressions from earlier individual training runs.

**Requirements:**
- Load all available final models (`baseline_cnn.keras`, and `baseline_cnn_v2.keras` if it exists from Prompt 33, `mobilenetv2_final.keras`, `resnet50_final.keras`) using `tf.keras.models.load_model`.
- For each model, using the identical `test_ds` from Prompt 20: (a) compute test accuracy/loss via `model.evaluate()`, (b) measure average single-image inference time by timing `model.predict()` on a batch of, e.g., 50 individual test images one at a time and averaging (representative of real-time single-upload inference in Prompt 89, not batch-throughput), (c) get file size in MB via `os.path.getsize()` on the `.keras` file, (d) get total parameter count via `model.count_params()`.
- Assemble all results into a single pandas DataFrame with columns `model_name`, `test_accuracy`, `test_loss`, `avg_inference_time_ms`, `file_size_mb`, `param_count`, printed as a clean table and also saved to `ml/evaluation/model_comparison.csv`.
- Sort the table by `test_accuracy` descending so the best performer is immediately visible at the top.

**Acceptance Criteria:**
- [ ] `ml/evaluation/model_comparison.csv` exists with one row per trained model, all five metric columns populated with real (not placeholder) numbers.
- [ ] Every model in the table was evaluated on the exact same `test_ds` (confirm no accidental use of val_ds for one model and test_ds for another).
- [ ] Numbers are internally consistent with each model's individual earlier evaluation runs where applicable (e.g. baseline's accuracy here should match Prompt 31's `baseline_results.json` value).

**Must Not Break:** Must not retrain any model — this script only loads and evaluates already-saved `.keras` files from Prompts 30, 33, 37, 39.

---

#### Prompt 41 — Document the Model Selection Decision

**Do:** Based on the comparison, write `ml/evaluation/MODEL_SELECTION.md` documenting which model was chosen as final and why.

**Context & Why:** This is the document that directly answers "why did you choose this model?" in the viva (Prompt 216) — it must be a genuine, evidence-based justification referencing Prompt 40's actual numbers, not a generic statement about transfer learning being "better."

**Requirements:**
- Embed or restate Prompt 40's comparison table in full.
- State the chosen model explicitly (expected to be MobileNetV2 based on the project report's existing content, but the decision must follow from the actual comparison data generated in Prompt 40, not be assumed in advance — if ResNet50 or the baseline actually won on accuracy, document that honestly and explain the trade-off reasoning if a different model is still chosen for deployment, e.g. "ResNet50 scored marginally higher accuracy but its 3x larger file size and slower inference time make it a worse fit for the target deployment environment").
- Explicitly weigh all four metrics, not accuracy alone — a real justification should address the accuracy/size/speed trade-off directly, since this is exactly the kind of reasoning a technical evaluator would probe in the viva.
- Include a "Rejected Alternatives" section briefly stating why the other candidate(s) were not chosen.

**Acceptance Criteria:**
- [ ] Every number cited in this document matches Prompt 40's `model_comparison.csv` exactly (no invented or rounded-differently figures).
- [ ] The final decision is a reasoned trade-off analysis, not a single-metric argument.

**Must Not Break:** Must not contradict `ml/evaluation/model_comparison.csv` from Prompt 40.

---

#### Prompt 42 — Promote the Chosen Model to Production Filename

**Do:** Copy the selected final model to `ml/models/crop_disease_model.keras` (the production filename referenced by the backend).

**Context & Why:** This is the exact hand-off point between Phase 1 and Phase 2 — every backend prompt from 86 onward references this literal filename, and it must never be a symlink or an ambiguous "latest" pointer that could silently change.

**Requirements:**
- Physically copy (not symlink — for portability across deployment environments in Prompt 199) the model file chosen in Prompt 41 (e.g. `ml/models/mobilenetv2_final.keras`) to `ml/models/crop_disease_model.keras`.
- After copying, immediately reload `crop_disease_model.keras` independently and re-run the same round-trip prediction sanity check used in Prompts 30/37/39, to confirm the copy is byte-identical in behavior to the source file.
- Add a line to `ml/models/README.md` (create this file if it doesn't exist) recording exactly which training run/model this production file corresponds to, its test accuracy, and the date it was frozen — this is critical provenance information for later debugging or re-training.

**Acceptance Criteria:**
- [ ] `ml/models/crop_disease_model.keras` exists and produces identical predictions to its source model on a fixed sample batch.
- [ ] `ml/models/README.md` records the provenance of this exact file (source model, test accuracy, freeze date).

**Must Not Break:** Must not delete or modify the original source model file it was copied from — both should exist so provenance is traceable.

---

#### Prompt 43 — Generate `class_names.json`

**Do:** Generate `ml/models/class_names.json` mapping numeric class indices to human-readable crop/disease labels, matching the final model's output order.

**Context & Why:** This file is the second of the two frozen production artifacts (alongside Prompt 42's model file) — the backend's `model_service.py` (Prompt 86) uses it to translate the model's raw numeric softmax output back into a disease name a human can read, and `predict.py`'s route (Prompt 89) uses it to look up disease information. Any index mismatch here silently mislabels every single prediction in production.

**Requirements:**
- Derive the index-to-class-name mapping directly and programmatically from `train_ds.class_names` as produced by Prompt 20's `build_datasets()` — do NOT hand-type this list from memory, since `image_dataset_from_directory` orders classes alphabetically by folder name, which may not match the order a human would naturally list them in.
- Write as JSON: an object mapping the string index (`"0"`, `"1"`, ... `"7"`) to a two-part object `{"crop": "...", "disease": "...", "display_name": "..."}` — e.g. `"0": {"crop": "Pepper", "disease": "Bacterial Spot", "display_name": "Pepper — Bacterial Spot"}` — derived by parsing the exact PlantVillage folder-naming convention (e.g. `Pepper__bell___Bacterial_spot`) into clean human-readable fields.
- After writing the file, add an automated check (a short script or an assertion inside this same generation script) that loads `crop_disease_model.keras` (Prompt 42), runs one forward pass, confirms the output layer's size (8) matches the number of entries in `class_names.json`, and confirms the order matches `train_ds.class_names` exactly, position by position.

**Acceptance Criteria:**
- [ ] `ml/models/class_names.json` contains exactly 8 entries, indices `"0"`–`"7"`, each with `crop`, `disease`, `display_name` fields correctly parsed from the real folder names.
- [ ] The index order is verified (via the automated check) to exactly match the model's actual output-neuron order, not assumed.
- [ ] File is valid, parseable JSON.

**Must Not Break:** This file's ordering is permanently tied to `crop_disease_model.keras` (Prompt 42) — if the model is ever retrained with a different class ordering, this file must be regenerated in lockstep, never edited independently.

---
### 1.F Model Evaluation

#### Prompt 44 — Per-Class Precision/Recall/F1 Report

**Do:** Write `ml/evaluation/evaluate.py` computing accuracy, precision, recall, and F1-score per class using scikit-learn's `classification_report`.

**Context & Why:** Overall test accuracy (already known from Prompt 40) can hide poor performance on individual, possibly rarer, classes — this per-class breakdown is what the final report's "Model Evaluation" section (matching the structure already established in the project report document) actually needs, and it's the real, measured version of the currently-illustrative bar chart in that report.

**Requirements:**
- Load `ml/models/crop_disease_model.keras` (Prompt 42) and `ml/models/class_names.json` (Prompt 43).
- Run predictions on the full `test_ds` (Prompt 20), collecting predicted class indices (via `argmax` on softmax output) and true class indices (from the one-hot labels, also via `argmax`) into two flat arrays across all test batches.
- Call `sklearn.metrics.classification_report(y_true, y_pred, target_names=<display names from class_names.json>, output_dict=True)`.
- Save the full report as `ml/evaluation/final_model_metrics.json` (Prompt 46 will also reference this) and print a clean formatted table to stdout (per-class precision/recall/F1/support, plus overall accuracy/macro-avg/weighted-avg rows).

**Acceptance Criteria:**
- [ ] Script runs against the real frozen `crop_disease_model.keras` and reports real, non-illustrative metrics for all 8 classes.
- [ ] Overall accuracy in this report matches Prompt 40's recorded test accuracy for the chosen model (cross-check — any mismatch indicates a bug, e.g. an accidental dataset ordering difference).
- [ ] `target_names` are human-readable (from `class_names.json`'s `display_name` field), not raw folder names or bare indices.

**Must Not Break:** Must evaluate the actual production model (`crop_disease_model.keras`), not an intermediate checkpoint, and must use the same `test_ds` as every prior evaluation prompt.

---

#### Prompt 45 — Confusion Matrix

**Do:** Write `ml/evaluation/confusion_matrix.py` generating and plotting a confusion matrix heatmap for the final model on the test set.

**Context & Why:** This is the real, measured replacement for the currently-illustrative confusion matrix already produced for the project report — it shows exactly which disease classes the model tends to confuse with each other (e.g. Early Blight vs. Late Blight, which often look visually similar), which is valuable both for the report and for the `error_analysis.py` deep-dive in Prompt 49.

**Requirements:**
- Reuse the same prediction-collection logic as Prompt 44 (import/reuse rather than reimplementing prediction collection separately — refactor a shared helper if needed, e.g. `get_predictions_and_labels(model, dataset)` in a small shared utility, since both this and Prompt 44 need the identical `(y_true, y_pred)` arrays).
- Compute the matrix with `sklearn.metrics.confusion_matrix(y_true, y_pred)`.
- Plot as a heatmap (matplotlib `imshow` with a colorbar, or seaborn if already a project dependency — add `seaborn` to `ml/requirements.txt` if used) with class display names as both axis tick labels, annotated cell values, axis titles "Predicted Class" / "Actual Class", and a clear title.
- Save to `ml/evaluation/confusion_matrix.png` at ≥150 DPI, and also save the raw matrix as `ml/evaluation/confusion_matrix.csv` for anyone who wants the exact numbers rather than just the image.

**Acceptance Criteria:**
- [ ] `ml/evaluation/confusion_matrix.png` and `.csv` exist and reflect the real trained model's actual test-set performance.
- [ ] The diagonal (correct predictions) is visibly the dominant pattern if the model is performing reasonably; any notably large off-diagonal values are visually identifiable for discussion.
- [ ] Row/column ordering matches `class_names.json`'s index order exactly.

**Must Not Break:** Must use the same `(y_true, y_pred)` source data as Prompt 44 for internal consistency between the two evaluation artifacts.

---

#### Prompt 46 — Consolidate Final Metrics

**Do:** Save all evaluation metrics to `ml/evaluation/final_model_metrics.json` and `ml/evaluation/final_model_report.md`.

**Context & Why:** This creates one canonical, human-readable summary document that consolidates Prompts 44 and 45's outputs — the single file someone should open if they want "the final numbers" without hunting across five separate evaluation scripts' outputs.

**Requirements:**
- `final_model_metrics.json` (may already partially exist from Prompt 44 — extend rather than overwrite its content) should additionally include: overall test accuracy and loss (from Prompt 40/31-style evaluation), the full per-class classification report dict, the model filename and its file size, and a timestamp.
- `final_model_report.md` should present the same information as readable Markdown: a summary paragraph with headline accuracy, a per-class metrics table, an embedded/linked confusion matrix image (Prompt 45), and a short "How to Reproduce These Numbers" section listing the exact scripts to run in order (`evaluate.py` then `confusion_matrix.py`).
- This Markdown report is the document that should be referenced when filling in "final, measured accuracy/evaluation numbers" back into the main project report (a task explicitly named later in Prompt 211).

**Acceptance Criteria:**
- [ ] `final_model_metrics.json` is a complete, valid JSON superset of Prompt 44's output.
- [ ] `final_model_report.md` renders cleanly and includes real numbers plus the real confusion matrix image, not illustrative placeholders.

**Must Not Break:** Must not contradict any number already established in Prompts 40, 41, 44, 45 — this is a consolidation step, not a re-derivation from a different source.

---

#### Prompt 47 — Confidence Threshold Sweep

**Do:** Write `ml/evaluation/confidence_threshold_experiment.py` that sweeps threshold values (e.g. 0.5 to 0.9) and reports how many test predictions would be flagged as "uncertain" at each threshold.

**Context & Why:** This directly determines the production confidence threshold used in the backend's `/predict` route (Prompt 90) to flag low-confidence results as `is_confident: false` — picking this value from real data here, rather than guessing an arbitrary number later in the backend, keeps the ML and backend phases properly in sync.

**Requirements:**
- For a range of candidate thresholds (e.g. `[0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9]`), and using the max softmax probability per test-set prediction (already computable from Prompt 44's collected predictions — reuse rather than re-run inference), compute for each threshold: (a) the percentage of test predictions that would fall below it (flagged "uncertain"), and (b) the accuracy of the predictions that remain ABOVE the threshold (i.e., does filtering out low-confidence predictions meaningfully improve the accuracy of what's left?).
- Present as a table (threshold, % flagged uncertain, accuracy-above-threshold) printed to stdout and saved to `ml/evaluation/confidence_threshold_sweep.csv`.
- Optionally plot this as a simple line chart (threshold on x-axis, the two metrics as two lines) saved to `ml/evaluation/confidence_threshold_sweep.png`.

**Acceptance Criteria:**
- [ ] `confidence_threshold_sweep.csv` contains one row per candidate threshold, both metrics populated with real numbers derived from actual test-set predictions.
- [ ] Trend is directionally sensible: higher thresholds should generally flag more predictions as uncertain, and accuracy among the remaining (above-threshold) predictions should be equal to or higher than the unfiltered overall accuracy.

**Must Not Break:** Must reuse the exact same test-set predictions as Prompt 44 for consistency.

---

#### Prompt 48 — Document the Chosen Confidence Threshold

**Do:** Based on the sweep, document the chosen production confidence threshold and rationale in `ml/evaluation/CONFIDENCE_THRESHOLD.md`.

**Context & Why:** This document is the explicit hand-off of a concrete numeric decision to the backend team — Prompt 90 should read this file (not guess or use the example `94%` from the illustrative report) to know exactly what threshold value to hardcode/configure in `/predict`.

**Requirements:**
- State the chosen threshold value explicitly and prominently (e.g. as a top-level heading or bolded statement: "**Chosen production confidence threshold: 0.75**").
- Justify the choice using Prompt 47's actual sweep data: explain the trade-off being balanced (higher threshold = fewer wrong "confident" answers shown to farmers, but more results shown as "uncertain" and therefore less immediately useful) and why the chosen value is a reasonable point on that trade-off curve, not the mathematically "optimal" one only — this is a product decision informed by data, not a pure optimization output.
- Explicitly instruct: "Backend implementation (Prompt 90) should read this exact value" and state it should likely live in `backend/app/core/config.py` as a configurable setting rather than a hardcoded magic number, so it can be tuned later without a code change.

**Acceptance Criteria:**
- [ ] A single, unambiguous threshold value is stated and justified with real numbers from Prompt 47.
- [ ] Explicitly connects forward to the backend implementation requirement in Prompt 90.

**Must Not Break:** Must be consistent with the real data in Prompt 47's sweep — do not state a threshold the sweep data doesn't support.

---

#### Prompt 49 — Error Analysis on Most-Confident Wrong Predictions

**Do:** Write `ml/evaluation/error_analysis.py` that saves the top 10 most-confident wrong predictions as images for manual review.

**Context & Why:** A wrong prediction the model was very confident about is more concerning and more informative than a wrong prediction it was already uncertain about (the latter would likely be caught by Prompt 47's threshold anyway) — reviewing these specific cases often reveals a systematic issue (e.g., a particular disease pair that looks visually near-identical, or a data-quality problem in a specific subset of images).

**Requirements:**
- From the full set of test predictions (reuse Prompt 44's collected data), filter to only the incorrect ones (`y_pred != y_true`), sort descending by the model's confidence (max softmax probability) on its (wrong) prediction, and take the top 10.
- For each of the 10, save a plot showing: the actual image, a title stating "True: {true_class} | Predicted: {predicted_class} ({confidence:.1%} confidence)", saved individually or as one combined grid to `ml/evaluation/error_analysis/` (create this subfolder).
- Print a short list to stdout as well, for quick scanning without opening images.

**Acceptance Criteria:**
- [ ] `ml/evaluation/error_analysis/` contains exactly 10 saved images/plots (or one grid image containing all 10), each clearly labeled with true vs. predicted class and confidence.
- [ ] The 10 selected are verifiably the most-confident wrong predictions in the test set, not a random or least-confident sample (spot-check the confidence values are descending and all are misclassifications).

**Must Not Break:** Reuses Prompt 44's prediction data — must reflect the real production model's real test-set errors, not a synthetic example.

---

#### Prompt 50 — Evaluation Summary

**Do:** Summarize key findings (best model, accuracy, confusion patterns) in `ml/evaluation/SUMMARY.md`.

**Context & Why:** This is the single top-level entry point into all of sub-phase 1.F's work — the one document to read first before diving into any of the individual JSON/CSV/PNG artifacts, and a natural direct source for Prompt 211's task of filling final numbers into the main project report.

**Requirements:**
- One-paragraph executive summary: chosen model, final test accuracy, and one sentence on overall confidence in the result.
- Bullet list of key confusion patterns observed from Prompt 45's confusion matrix (name the specific class pairs most often confused, with approximate counts/percentages).
- Bullet list referencing Prompt 49's error analysis findings (any systematic issue identified, or a note that no clear pattern was found among the top errors).
- The chosen confidence threshold from Prompt 48, restated briefly with a link to the full document.
- Links to every artifact produced in 1.F: `final_model_report.md`, `confusion_matrix.png`, `confidence_threshold_sweep.csv`, `error_analysis/`, `CONFIDENCE_THRESHOLD.md`.

**Acceptance Criteria:**
- [ ] Every claim in this summary is traceable to a specific artifact produced earlier in 1.F — no new, unsupported claims introduced here.
- [ ] Document is genuinely usable as a fast, one-stop overview (a reader should not need to open every linked file to get the gist).

**Must Not Break:** Must accurately reflect Prompts 44–49's real outputs.

---
### 1.G Real-World Testing

#### Prompt 51 — Collect Real-World Sample Images

**Do:** Collect (or simulate collecting) 30–50 independently sourced real-world leaf photographs and organize them into `ml/dataset/real_world_sample/<class>/`.

**Context & Why:** PlantVillage images are famously taken under controlled/lab-like conditions (uniform background, consistent lighting) — the whole point of this sub-phase is to honestly test whether the model generalizes to messier real-world photos of the kind actual users will upload through the app's `/scan` page (Prompt 135), rather than reporting only the optimistic PlantVillage test-set accuracy as if it were the final word.

**Requirements:**
- Source images independently from the PlantVillage dataset — e.g. from a different public dataset covering overlapping classes, from manually-taken photos, or from properly licensed stock/agricultural-extension imagery — explicitly do NOT simply re-sample images from `ml/dataset/raw/` or `filtered/`, as that would defeat the entire purpose of this test.
- Aim for at least 3–6 images per one of the 8 target classes (30–50 total is a reasonable range, does not need to be perfectly even across classes, but should not have any class with zero real-world samples).
- Organize into `ml/dataset/real_world_sample/<class>/` using the exact same class folder naming convention as `ml/dataset/filtered/` (Prompt 9), so downstream scripts can treat this folder identically to the main dataset splits.
- Record the source of each image (a simple `ml/dataset/real_world_sample/SOURCES.md` listing where each image or batch of images came from and confirming licensing/usage is appropriate) — this matters for academic integrity and for the "Real-World Findings" writeup in Prompt 54.

**Acceptance Criteria:**
- [ ] `ml/dataset/real_world_sample/<class>/` exists for at least most (ideally all) of the 8 classes, with genuinely different-looking images than the PlantVillage set (different backgrounds/lighting, visibly distinct from the lab-condition source images).
- [ ] `SOURCES.md` documents provenance for every image or image batch.

**Must Not Break:** Must not be copied from or overlap with `ml/dataset/filtered/`/`split/` — verify no duplicate files exist between this folder and the main dataset (optionally re-run Prompt 10's hashing logic against this folder as a cross-check).

---

#### Prompt 52 — Real-World Evaluation Script

**Do:** Write `ml/evaluation/real_world_eval.py` that runs the final model against the real-world sample and reports accuracy.

**Context & Why:** This produces the actual, honest "how does this perform on photos like a real farmer would take" number, as distinct from the lab-condition PlantVillage test accuracy already established in Prompts 40/44.

**Requirements:**
- Load `ml/models/crop_disease_model.keras` and `ml/models/class_names.json` (Prompts 42–43).
- Build a dataset/loader over `ml/dataset/real_world_sample/` reusing Prompt 16's `load_and_preprocess_image` function directly on each file (this folder is small enough that a full `tf.data` pipeline is unnecessary overhead — a simple loop is appropriate and should be used, documented as a deliberate simplicity choice).
- Compute overall accuracy and a per-class breakdown (reusing `sklearn.metrics.classification_report` as in Prompt 44, applied to this smaller dataset).
- Save results to `ml/evaluation/real_world_results.json` and print a clear summary to stdout, explicitly labeled as "real-world" results so they're never confused with the PlantVillage test-set numbers.

**Acceptance Criteria:**
- [ ] `ml/evaluation/real_world_results.json` exists with overall and per-class accuracy figures against the Prompt 51 sample.
- [ ] Uses the exact same preprocessing function (Prompt 16) that production inference (Prompt 87) will use, for a fair, representative comparison.

**Must Not Break:** Must evaluate `crop_disease_model.keras` specifically (the frozen production model), not an intermediate/experimental one.

---

#### Prompt 53 — Dataset vs. Real-World Comparison Table

**Do:** Write `ml/evaluation/dataset_vs_realworld.py` producing a side-by-side comparison table of test-set accuracy vs. real-world accuracy.

**Context & Why:** A single side-by-side number (e.g. "93.6% on PlantVillage test set vs. 71.2% on real-world photos") is the most honest, presentation-ready statistic this whole ML phase can produce, and directly supports the project report's stated limitation that "training datasets may not fully represent real-world field conditions."

**Requirements:**
- Pull the PlantVillage test-set overall accuracy from `ml/evaluation/final_model_metrics.json` (Prompt 46) and the real-world overall accuracy from `ml/evaluation/real_world_results.json` (Prompt 52) — do not recompute either from scratch; this script only combines already-produced results.
- Present as a small, clean table/chart: two bars (or two rows) — "PlantVillage Test Set" vs. "Real-World Sample" — with accuracy percentages, saved as both `ml/evaluation/dataset_vs_realworld.png` (a simple bar chart) and printed as a two-line stdout summary.
- If per-class breakdowns are available for both, optionally include a per-class side-by-side comparison as well (not required, but valuable if the gap is very uneven across classes).

**Acceptance Criteria:**
- [ ] `ml/evaluation/dataset_vs_realworld.png` exists and clearly, visually communicates the accuracy gap (if any) between the two evaluation contexts.
- [ ] Numbers exactly match the source files from Prompts 46 and 52 (no recalculation, no rounding drift).

**Must Not Break:** Must read from, not duplicate, the existing results files from Prompts 46 and 52.

---

#### Prompt 54 — Document Real-World Findings

**Do:** Document the real-world performance gap and likely causes (lighting, background, camera quality) in `ml/evaluation/REAL_WORLD_FINDINGS.md`.

**Context & Why:** This is the analytical write-up that turns Prompt 53's raw comparison into genuine insight — it is also the direct, evidence-backed source for the "Limitations" section already present in the project report (which currently states the gap only as a hypothetical concern; this document makes it a measured, specific finding).

**Requirements:**
- State the measured gap explicitly (exact percentages from Prompt 53).
- Discuss likely causes specific to what was actually observed in the real-world sample images (e.g., cluttered/non-uniform backgrounds vs. PlantVillage's plain backgrounds, inconsistent lighting/shadows, varying camera quality/focus, leaves photographed at different distances/angles than the standardized lab photos) — ground each cause in a specific observation from the real-world sample images collected in Prompt 51, not generic boilerplate.
- If the error-analysis approach from Prompt 49 was also informally applied to the worst real-world misclassifications, mention any patterns found there too.
- End with a "Recommendations for Future Work" section feeding directly into the "Future Scope" content already established in the project report (e.g. "collect a larger, more diverse real-world training set" ties directly to that report's existing "Larger real-world datasets" future-scope bullet).

**Acceptance Criteria:**
- [ ] Every cause discussed is tied to a specific, real observation, not a generic list of possible reasons copied without verification.
- [ ] Numbers cited match Prompt 53 exactly.

**Must Not Break:** Must be consistent with Prompts 51–53's actual data and images — do not speculate beyond what those artifacts support.

---

#### Prompt 55 — Freeze the Production Artifacts

**Do:** Finalize and freeze `ml/models/crop_disease_model.keras` and `ml/models/class_names.json` as the production artifacts to be handed to the backend team.

**Context & Why:** This is the formal, explicit close of Phase 1 and the gate that must be passed before Phase 2 (Prompt 56 onward) begins — nothing in `ml/` should change these two specific files again without a deliberate, documented re-training decision (and a corresponding version bump), since the entire backend and frontend are about to be built assuming these exact files' behavior and class ordering are stable.

**Requirements:**
- Run one final, complete verification pass: reload both files fresh (not from any in-memory state left over from earlier prompts), run a handful of real sample predictions (including at least 2–3 images from the real-world sample in Prompt 51) end-to-end through load → preprocess → predict → map index to class name via `class_names.json`, and print each prediction clearly for a final human sanity check.
- Compute and record the file hashes (`sha256sum ml/models/crop_disease_model.keras ml/models/class_names.json`) in `ml/models/README.md` (extending the file created in Prompt 42) as an immutable fingerprint of exactly which model version is "the" production model — this hash should be checked against later if anyone ever needs to confirm the backend is running against the exact same model file that was evaluated in Phase 1.
- Explicitly commit these two files to Git now (recall Prompt 5's `.gitignore` was configured to specifically un-ignore only these two exact files inside `ml/models/`) with a clear commit message, e.g. `"freeze: production model artifacts (crop_disease_model.keras, class_names.json) — Phase 1 complete"`.
- Update `ml/models/README.md`'s provenance section (from Prompt 42) with a final "FROZEN" status line and the date.

**Acceptance Criteria:**
- [ ] Final end-to-end sanity predictions on both PlantVillage-style and real-world sample images produce sensible, correctly-labeled results.
- [ ] SHA-256 hashes of both files are recorded in `ml/models/README.md`.
- [ ] Both files are committed to Git and confirmed NOT ignored (`git status`/`git log` shows them tracked).
- [ ] Phase 1 is formally declared complete — Phase 2 (Prompt 56) may now begin.

**Must Not Break:** This is the final Phase 1 gate — nothing here should require changing any file from Prompts 1–54; if final verification reveals a problem, fix it upstream (re-run the relevant earlier prompt) rather than patching the model file directly at this step.

---
## 4. PHASE 2 — Backend & Database (FastAPI)

*Prompts 56–110*

This phase builds the authenticated API that wraps the frozen model from Phase 1 (`ml/models/crop_disease_model.keras` + `class_names.json`, gated by Prompt 55) and gives every user their own private account, history, and stats. Do not begin any prompt in this phase until Phase 1 is formally complete.

### 2.A Project Setup

#### Prompt 56 — Initialize the FastAPI Project

**Do:** Initialize `backend/` as a Python FastAPI project with `requirements.txt` listing fastapi, uvicorn, sqlalchemy, psycopg2-binary, python-jose, passlib[bcrypt], python-multipart, pillow, tensorflow, pydantic-settings.

**Context & Why:** Every later backend prompt (57–110) assumes this exact dependency set is available — in particular, `tensorflow` here (not a lighter inference-only runtime) is a deliberate choice to load the Keras model directly with `tf.keras.models.load_model`, matching exactly how it was saved in Prompt 55, avoiding any format-conversion step that could subtly change model behavior.

**Requirements:**
- `backend/requirements.txt` must pin versions compatible with the TensorFlow version used in `ml/requirements.txt` (Prompt 2) — if they diverge, `.keras` file loading can fail; add a code comment cross-referencing this constraint.
- Full package list, each with a version pin: `fastapi`, `uvicorn[standard]`, `sqlalchemy>=2.0`, `psycopg2-binary`, `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`, `pillow`, `tensorflow` (matching Prompt 2's pin), `pydantic-settings`, `alembic`, `pytest`, `httpx` (needed for FastAPI's `TestClient`/async test support).
- Set up a `backend/venv/` virtual environment following the same pattern as `ml/venv/` (Prompt 3), and add it to the root `.gitignore` if not already covered by the earlier wildcard `**/venv/` rule (confirm rather than duplicate).

**Acceptance Criteria:**
- [ ] `pip install -r backend/requirements.txt` succeeds inside a fresh `backend/venv/`.
- [ ] `import tensorflow`, `import fastapi`, `import sqlalchemy` all succeed with no version-conflict warnings.
- [ ] `backend/venv/` is git-ignored.

**Must Not Break:** N/A — new subproject. Must remain compatible with the TensorFlow version already used and pinned in `ml/requirements.txt`.

---

#### Prompt 57 — Backend Folder Structure

**Do:** Create the backend folder structure: `backend/app/{main.py, routes/, services/, models/, schemas/, core/, db/}` and `backend/app/disease_data/`.

**Context & Why:** This exact layout is assumed by every subsequent Phase 2 prompt's file paths — `routes/` holds one file per resource (auth, users, predict, diseases), `services/` holds business logic decoupled from HTTP concerns (model inference, preprocessing), `models/` holds SQLAlchemy ORM classes, `schemas/` holds Pydantic request/response shapes, `core/` holds cross-cutting config/security/dependency code, `db/` holds session/connection setup.

**Requirements:**
- Create every folder listed, each containing an `__init__.py` so they're importable Python packages.
- `backend/app/disease_data/` starts empty — it will hold the structured disease information JSON/data files referenced by Prompt 67's seeding script.
- Do not create any actual route/model/schema files yet — this prompt is structure only, matching the granularity of Prompt 2's equivalent step for `ml/`.

**Acceptance Criteria:**
- [ ] All listed folders exist under `backend/app/` with `__init__.py` files.
- [ ] `python -c "import app"` (run from `backend/`) succeeds with no output/errors once `main.py` exists (verify again after Prompt 60).

**Must Not Break:** Must sit inside the `backend/` folder created in Prompt 56, alongside its `requirements.txt` and `venv/`.

---

#### Prompt 58 — Application Configuration via Pydantic Settings

**Do:** Create `backend/app/core/config.py` using Pydantic Settings to load environment variables (DATABASE_URL, JWT_SECRET, JWT_EXPIRY, MODEL_PATH).

**Context & Why:** Centralizing all environment-dependent configuration in one typed, validated object prevents the common failure mode of scattered `os.environ.get(...)` calls throughout the codebase with inconsistent defaults or silent `None` values reaching production.

**Requirements:**
- Define a `Settings(BaseSettings)` class (from `pydantic_settings`) with typed fields: `database_url: str`, `jwt_secret: str`, `jwt_expiry_minutes: int = 60`, `model_path: str = "../ml/models/crop_disease_model.keras"`, `class_names_path: str = "../ml/models/class_names.json"`, `cors_allowed_origins: list[str] = []`, `confidence_threshold: float` (this value should default to whatever was documented in `ml/evaluation/CONFIDENCE_THRESHOLD.md` from Prompt 48 — read that document and hardcode its stated value as the default here, with a code comment citing the source document), `max_upload_size_mb: int = 10`.
- Configure it to read from a `.env` file automatically (`model_config = SettingsConfigDict(env_file=".env")`).
- Expose a single cached instance via `@lru_cache` wrapped `get_settings()` function, so the rest of the app imports and calls this function rather than instantiating `Settings()` repeatedly.
- Raise a clear startup error (Pydantic will do this automatically for missing required fields with no default) if `DATABASE_URL` or `JWT_SECRET` are not set — these must never silently default to an empty string.

**Acceptance Criteria:**
- [ ] `Settings` correctly loads values from a populated `.env` file and raises a validation error if `DATABASE_URL`/`JWT_SECRET` are missing.
- [ ] `confidence_threshold`'s default value matches exactly what Prompt 48's document specifies (verify by reading that file's content, not by guessing).
- [ ] `get_settings()` returns the same cached instance on repeated calls (confirm via `is` identity check in a quick manual test).

**Must Not Break:** N/A — new file, but its `confidence_threshold` default must trace directly to Prompt 48's ML-phase decision, not be independently invented here.

---

#### Prompt 59 — `.env.example` Template

**Do:** Set up `backend/.env.example` documenting required environment variables without real secrets.

**Context & Why:** This is the file new teammates and deployment environments (Prompt 196) actually copy and fill in — it must list every single field `Settings` (Prompt 58) expects, or someone will hit a confusing startup crash from a variable they didn't know they needed to set.

**Requirements:**
- One line per field in `Settings`, in the exact same order as the class definition, each as `VARIABLE_NAME=<placeholder-or-example>` with a `#` comment above explaining its purpose and, where relevant, its expected format (e.g. `# PostgreSQL connection string, e.g. postgresql://user:password@localhost:5432/crop_disease_db`).
- `JWT_SECRET` placeholder must visibly NOT be a usable real secret (e.g. `JWT_SECRET=replace-this-with-a-long-random-string-in-production`) and the comment above it should instruct how to generate a strong one (e.g. `python -c "import secrets; print(secrets.token_urlsafe(32))"`).
- `MODEL_PATH` and `CLASS_NAMES_PATH` placeholders should point at the real relative paths matching Prompt 42/43's frozen file locations.
- Confirm `.env.example` itself is safe to commit (no real secrets) but the actual `.env` it templates remains git-ignored per Prompt 5.

**Acceptance Criteria:**
- [ ] Every field defined in `backend/app/core/config.py`'s `Settings` class has a corresponding, clearly-commented line in `.env.example`.
- [ ] Copying `.env.example` to `.env` and filling in real values, then running `Settings()`, succeeds with no missing-field errors.

**Must Not Break:** Must stay in exact sync with `Settings` (Prompt 58) — if a field is added/removed there later, update this file in the same change.

---

#### Prompt 60 — Base FastAPI App with Health Check

**Do:** Create `backend/app/main.py` with a basic FastAPI app instance, CORS middleware, and a health-check `GET /health` route.

**Context & Why:** This is the very first thing that must run correctly before any other backend prompt can be meaningfully tested — it's also the exact endpoint Prompt 197's deployment step uses to confirm the deployed backend is actually up.

**Requirements:**
- `app = FastAPI(title="Crop Disease Detection API", version="0.1.0")`.
- Add `CORSMiddleware` configured from `get_settings().cors_allowed_origins` (Prompt 58) — do not hardcode `allow_origins=["*"]` even at this early stage, since Prompt 103 will need to tighten this later and it's better established correctly from the start; for local development, `.env`'s `CORS_ALLOWED_ORIGINS` can simply include `http://localhost:5173` (Vite's default dev port, relevant once Prompt 111 scaffolds the frontend).
- Define `@app.get("/health")` returning `{"status": "ok"}` with a 200 status — this route must NOT require authentication and must NOT touch the database or the ML model (it should succeed even if either of those is down, so it's a true "is the process alive" check, not a "is everything fully working" check).
- Do not wire up any routers yet (those are added in later prompts as each router file is created) — this prompt only establishes the running app skeleton.

**Acceptance Criteria:**
- [ ] `uvicorn app.main:app --reload` starts without error (given a valid `.env`).
- [ ] `GET /health` returns `200 {"status": "ok"}`.
- [ ] CORS headers are present on responses and reflect the configured allowed origins, not a wildcard.

**Must Not Break:** Depends on `backend/app/core/config.py` (Prompt 58) for CORS settings — must not hardcode values that bypass that configuration.

---
### 2.B Database Schema & Migrations

#### Prompt 61 — SQLAlchemy Engine and Session Management

**Do:** Set up the SQLAlchemy engine and session management in `backend/app/db/session.py`.

**Context & Why:** This module's `get_db` dependency will be imported into literally every route that touches the database from Prompt 72 onward — getting session lifecycle (creation, commit/rollback, closing) right here once prevents connection leaks and inconsistent transaction handling across dozens of later route handlers.

**Requirements:**
- Create the SQLAlchemy `engine = create_engine(get_settings().database_url)` (importing `get_settings` from Prompt 58).
- Create `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`.
- Define a declarative `Base = declarative_base()` that every model in `backend/app/models/` (Prompts 62–65) will inherit from.
- Define a FastAPI dependency generator `def get_db():` that yields a `SessionLocal()` instance inside a `try/finally` block, always calling `.close()` in the `finally` clause, so every route using `Depends(get_db)` gets automatic cleanup regardless of whether the route raised an exception.
- Do not perform rollback/commit logic inside `get_db` itself — that responsibility belongs to each route/service that actually modifies data (this dependency only manages the session's lifecycle, not its transactions).

**Acceptance Criteria:**
- [ ] `get_db()` used as a FastAPI dependency correctly provides a working session to a test route and closes it afterward (verify no lingering open connections after a request completes, e.g. via a quick connection-count check against Postgres during testing).
- [ ] `Base` is successfully importable and usable by model files created in the next four prompts without circular-import errors.

**Must Not Break:** Depends on `get_settings().database_url` from Prompt 58 being correctly configured.

---

#### Prompt 62 — `User` Model

**Do:** Define the `User` model in `backend/app/models/user.py` with fields: id, name, email, password_hash, phone, location, profile_photo_url, preferred_crops, created_at, last_login_at.

**Context & Why:** This is the anchor table every other table (`Prediction`, `Feedback`) foreign-keys into, and the identity JWT tokens (Prompt 70) ultimately resolve back to via `get_current_user` (Prompt 74) — its exact field set must satisfy every later frontend Profile-page field (Prompt 154) with nothing missing.

**Requirements:**
- `id`: primary key, integer (or UUID — pick one and use it consistently across all four models; integer auto-increment is the simpler default unless the team has a specific reason for UUIDs).
- `name`: `String`, not nullable.
- `email`: `String`, not nullable, **unique constraint** (this uniqueness is what Prompt 72's duplicate-email rejection logic relies on at the database level, as a second line of defense beyond any application-level check).
- `password_hash`: `String`, not nullable — never store plaintext; this column name itself should make it obvious this is a hash, not a password, to prevent any future accidental logging or exposure.
- `phone`: `String`, nullable (optional at signup, per the frontend's optional-phone field in Prompt 120).
- `location`: `String`, nullable.
- `profile_photo_url`: `String`, nullable (defaults to `None`; Prompt 83's initials-avatar logic handles the fallback on the frontend/response side, not by storing a generated image URL here).
- `preferred_crops`: use a `JSON` or `ARRAY(String)` column type (JSON is more portably supported across the SQLAlchemy/Postgres combination if unsure) to store a list of crop-name strings, nullable/default empty list.
- `created_at`: `DateTime`, server-default `now()`, not nullable.
- `last_login_at`: `DateTime`, nullable (only set on first login by Prompt 73, remains `None` until then).
- Add `__tablename__ = "users"`.

**Acceptance Criteria:**
- [ ] Model class defines all 10 fields with the correct types/constraints listed above.
- [ ] `email` column has a unique index/constraint verifiable in the generated migration (Prompt 66).
- [ ] No `password` field exists anywhere on this model — only `password_hash`.

**Must Not Break:** Must inherit from `Base` (Prompt 61).

---

#### Prompt 63 — `Prediction` Model

**Do:** Define the `Prediction` model in `backend/app/models/prediction.py` with fields: id, user_id (FK), image_url, crop, disease, confidence, is_confident, created_at.

**Context & Why:** Every row here represents one completed scan — this is what powers the Dashboard's recent-scans table (Prompt 130), the History page (Prompt 149), and the stats aggregation (Prompt 84); its `user_id` foreign key is the exact mechanism that guarantees per-user data isolation (verified explicitly in Prompt 172).

**Requirements:**
- `id`: primary key, same type convention as `User.id`.
- `user_id`: foreign key to `users.id`, **not nullable** (every prediction must belong to exactly one authenticated user — there is no concept of an anonymous prediction in this schema).
- `image_url`: `String`, nullable (nullable specifically because Prompt 93 marks image persistence as optional — a prediction can exist even if the raw image wasn't separately stored).
- `crop`: `String`, not nullable (e.g. `"Tomato"`).
- `disease`: `String`, not nullable (e.g. `"Early Blight"`) — store the human-readable disease name directly (denormalized) rather than only a foreign key to `Disease`, so historical predictions remain stable/readable even if the `diseases` reference table's content is edited later.
- `confidence`: `Float`, not nullable, expected range `[0.0, 1.0]` (document this range in a code comment; do not store it as a `0–100` percentage to avoid unit-confusion bugs — convert to percentage only at the API/frontend display layer).
- `is_confident`: `Boolean`, not nullable — this is the pre-computed, stored result of comparing `confidence` against `get_settings().confidence_threshold` (Prompt 58) at prediction time, per Prompt 90's logic; storing it (rather than recomputing from `confidence` every time it's displayed) keeps historical predictions' "was this confident" status stable even if the threshold configuration is changed later.
- `created_at`: `DateTime`, server-default `now()`, not nullable.
- Add a SQLAlchemy `relationship()` back to `User` (and correspondingly add the reverse relationship on the `User` model, updating Prompt 62's file) so `user.predictions` and `prediction.user` both work.
- Add `__tablename__ = "predictions"`.

**Acceptance Criteria:**
- [ ] All 7 explicit fields plus the relationship are correctly defined.
- [ ] `user_id` is a proper foreign key with `ondelete` behavior explicitly decided and documented (e.g. `CASCADE` if a deleted user's predictions should be removed too, or `RESTRICT`/leave-as-null if user deletion isn't a feature this app supports yet — pick one and comment why).
- [ ] `confidence` is confirmed to be stored as a `0.0–1.0` float, not a `0–100` integer/float, in a quick manual insert-and-query test.

**Must Not Break:** Foreign key must correctly reference the `users` table from Prompt 62; must update `User` model with the reverse relationship without breaking its existing fields.

---

#### Prompt 64 — `Disease` Model

**Do:** Define the `Disease` model in `backend/app/models/disease.py` with fields: id, crop, disease_name, description, symptoms, prevention, management.

**Context & Why:** This is the reference/lookup table (not user-generated data) that powers both the `/diseases` informational endpoints (Prompts 96–97) and the disease-info portion of every prediction response (Prompt 91) — it should be seeded once (Prompt 67) and rarely if ever modified afterward through the API itself (there is no create/update/delete endpoint for diseases in this schema; it's maintained via the seed script only).

**Requirements:**
- `id`: primary key.
- `crop`: `String`, not nullable (e.g. `"Potato"`).
- `disease_name`: `String`, not nullable (e.g. `"Late Blight"`, or `"Healthy"` for the non-disease classes — confirm the 8 classes from `class_names.json` (Prompt 43) include 3 "healthy" entries and 5 actual diseases, and that this table has one row per one of those 8 classes, matching them exactly by crop+disease_name pairing).
- `description`: `Text` (not `String`, since this can be a longer paragraph), not nullable.
- `symptoms`: `Text`, not nullable — store as a single text field containing the full symptoms description (if a structured bullet list is preferred, store as `JSON` array of strings instead; pick one approach and use it consistently for `symptoms`, `prevention`, and `management` alike).
- `prevention`: same type/structure decision as `symptoms`.
- `management`: same type/structure decision as `symptoms`.
- Add a **unique constraint on the combination of `(crop, disease_name)`** so the same disease entry can't accidentally be seeded twice.
- Add `__tablename__ = "diseases"`.

**Acceptance Criteria:**
- [ ] All 7 fields defined with correct types.
- [ ] Unique constraint on `(crop, disease_name)` is present and verified in the migration.
- [ ] Field types for `symptoms`/`prevention`/`management` are consistent with each other (all `Text` or all `JSON`, not a mix).

**Must Not Break:** Must inherit from `Base` (Prompt 61); the eventual seeded rows (Prompt 67) must exactly match the 8 classes from `ml/models/class_names.json` (Prompt 43) — flag this cross-phase dependency clearly in a code comment.

---

#### Prompt 65 — `Feedback` Model

**Do:** Define the `Feedback` model in `backend/app/models/feedback.py` with fields: id, prediction_id (FK), user_id (FK), actual_disease, is_correct, comment, created_at.

**Context & Why:** This table captures the "Was this correct?" loop from the frontend's Result page (Prompt 148) — over time this is the kind of data that could inform future model retraining, even though that retraining loop is out of scope for the current 220-prompt build.

**Requirements:**
- `id`: primary key.
- `prediction_id`: foreign key to `predictions.id`, not nullable — one feedback entry always refers to exactly one specific past prediction.
- `user_id`: foreign key to `users.id`, not nullable — **must be validated at the route level (Prompt 99) to be the same user who owns the referenced prediction**; storing it redundantly here (rather than joining through `Prediction.user_id`) makes that ownership check a simple direct comparison and makes future queries like "all feedback submitted by user X" trivial without a join.
- `actual_disease`: `String`, nullable (a user confirming "yes, correct" doesn't need to restate the disease name; only populated when the user is correcting a wrong prediction).
- `is_correct`: `Boolean`, not nullable.
- `comment`: `Text`, nullable (optional free-text from the user).
- `created_at`: `DateTime`, server-default `now()`, not nullable.
- Add relationships to both `Prediction` and `User`.
- Add `__tablename__ = "feedback"`.

**Acceptance Criteria:**
- [ ] All 6 explicit fields plus both foreign keys and relationships correctly defined.
- [ ] Confirm via a code comment that route-level logic (Prompt 99) — not a database constraint — is responsible for verifying `user_id` matches the referenced prediction's owner, since this specific business rule isn't easily expressible as a plain FK constraint.

**Must Not Break:** Foreign keys must correctly reference `predictions` (Prompt 63) and `users` (Prompt 62).

---

#### Prompt 66 — Alembic Migration Setup

**Do:** Set up Alembic for migrations in `backend/alembic/` and generate the initial migration covering all four tables.

**Context & Why:** Alembic migrations are the only sanctioned way this schema should ever change from this point forward — never hand-edit the production database schema directly; every future field addition/change gets its own migration file, giving the team a reviewable, reversible history of every schema change.

**Requirements:**
- Run `alembic init alembic` from `backend/`, then configure `alembic/env.py` to import `Base` from `backend/app/db/session.py` (Prompt 61) and all four model modules (Prompts 62–65) so `Base.metadata` is fully populated with every table before autogeneration runs, and to read the database URL from `get_settings().database_url` (Prompt 58) rather than a separately hardcoded value in `alembic.ini`.
- Generate the initial migration with `alembic revision --autogenerate -m "initial schema: users, predictions, diseases, feedback"`.
- Manually review the autogenerated migration file before applying it — confirm all four tables, their columns, foreign keys, and the two unique constraints (email on `users`, `(crop, disease_name)` on `diseases`) are present exactly as specified in Prompts 62–65.
- Apply it with `alembic upgrade head` against a real (local development) Postgres database and confirm all four tables exist with `\dt` in `psql`.

**Acceptance Criteria:**
- [ ] `alembic/versions/` contains one migration file covering all four tables.
- [ ] `alembic upgrade head` runs successfully against a clean database.
- [ ] `alembic downgrade base` then `alembic upgrade head` again both succeed without error (confirms the migration is properly reversible, not just forward-only).
- [ ] All constraints from Prompts 62–65 are present in the actual database schema (verified via `\d users`, `\d diseases` etc. in `psql`, not just by reading the migration file).

**Must Not Break:** Must reflect the exact schema from Prompts 62–65 — do not introduce any field/constraint not specified in those prompts without updating them to match.

---

#### Prompt 67 — Seed the Diseases Table

**Do:** Write `backend/app/db/seed_diseases.py` to populate the `diseases` table with structured data for all 8 classes (description, symptoms, prevention, management).

**Context & Why:** Without this, `/diseases` (Prompt 96) returns an empty list and every `/predict` response (Prompt 91) fails to find matching disease info — this script is what makes the reference data actually exist, and it must produce exactly one row per one of the 8 classes frozen in Phase 1.

**Requirements:**
- Derive the exact list of `(crop, disease_name)` pairs to seed directly from `ml/models/class_names.json` (Prompt 43) — read that file programmatically rather than hardcoding a separately-typed list that could drift out of sync with the actual model's classes.
- For each of the 8 entries, write genuinely researched, accurate agricultural content for `description`, `symptoms`, `prevention`, and `management` — for the "healthy" entries, adapt the fields sensibly (e.g. `symptoms` = "No disease symptoms present; leaf shows normal healthy coloration and structure", `prevention`/`management` = general good-practice maintenance advice rather than a treatment for a disease that isn't present).
- Make the script idempotent: check if a `(crop, disease_name)` row already exists (leveraging the unique constraint from Prompt 64) before inserting, so re-running the seed script doesn't create duplicates or crash on a constraint violation — use an upsert pattern (update if exists, insert if not) so content edits can be re-run safely.
- Print a summary at the end: how many rows inserted, how many updated, how many unchanged.

**Acceptance Criteria:**
- [ ] Running the script against a fresh database inserts exactly 8 rows, one per class in `class_names.json`.
- [ ] Running it a second time produces "0 inserted, 0 or more updated, 8 unchanged" (or similar) rather than a duplicate-key error.
- [ ] Content is genuinely informative and specific to each disease (not generic filler text repeated across classes).

**Must Not Break:** Must derive its class list from Prompt 43's `class_names.json` — if that file's 8 classes ever change, this script's seed data must be updated to match, not silently left stale.

---

#### Prompt 68 — Local Database Reset Script

**Do:** Write `backend/scripts/reset_db.py` to drop and recreate all tables and re-seed disease data, for local development.

**Context & Why:** During active development, schema and seed-data mistakes are common and cheap to fix locally — this script gives every teammate a one-command way to get back to a known-clean state without manually running `alembic downgrade`/`upgrade`/seed commands in the right order every time.

**Requirements:**
- Sequence: (1) drop all tables (`Base.metadata.drop_all(engine)`, or equivalently `alembic downgrade base`), (2) recreate them (`alembic upgrade head`, preferred over `Base.metadata.create_all` so migrations stay the single source of truth even in this reset flow), (3) run Prompt 67's `seed_diseases.py` logic (import and call its function directly, don't shell out to a separate process unnecessarily).
- Add a loud, impossible-to-miss confirmation prompt (`input("This will DELETE ALL DATA in the local database. Type 'yes' to continue: ")`) before proceeding, to prevent an accidental run against the wrong `DATABASE_URL` (e.g. if `.env` was mistakenly pointed at a shared/production database).
- Add a `--force` flag to skip the confirmation for use in automated local test setup (Prompt 105's `conftest.py` may want a non-interactive equivalent — note this as a related future dependency in a comment).

**Acceptance Criteria:**
- [ ] Running the script (confirming the prompt) results in a database with all four tables present and the 8 diseases seeded, with zero users/predictions/feedback.
- [ ] Refusing the confirmation prompt (typing anything other than "yes") aborts with no changes made.
- [ ] Running with `--force` skips the prompt entirely.

**Must Not Break:** Must use the exact same migration/seed logic as Prompts 66–67, not a divergent reimplementation.

---
### 2.C Authentication Module

#### Prompt 69 — Password Hashing Utilities

**Do:** Create `backend/app/core/security.py` with password hashing/verification functions using passlib's bcrypt context.

**Context & Why:** Every password ever touches this exact pair of functions — at signup (Prompt 72, hashing) and at login (Prompt 73, verifying) — and never anywhere else in the codebase; centralizing this is what makes the "password_hash is never plaintext" guarantee (referenced again in Prompt 185's security audit) actually enforceable by code review rather than convention alone.

**Requirements:**
- `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`.
- `def hash_password(plain_password: str) -> str: return pwd_context.hash(plain_password)`.
- `def verify_password(plain_password: str, password_hash: str) -> bool: return pwd_context.verify(plain_password, password_hash)`.
- Both functions must be pure (no database access, no side effects) — they belong here specifically because they're stateless cryptographic utilities, not because they're "auth-related" in a general sense.
- Do not log the plaintext password anywhere in either function, including in exception messages if `verify_password` is called with malformed input.

**Acceptance Criteria:**
- [ ] `hash_password("test123")` returns a bcrypt hash string (starts with `$2b$`), different each time it's called (bcrypt includes a random salt) even for the same input password.
- [ ] `verify_password("test123", hash_password("test123"))` returns `True`.
- [ ] `verify_password("wrong", hash_password("test123"))` returns `False`.

**Must Not Break:** N/A — new file, foundational for Prompts 72–73.

---

#### Prompt 70 — JWT Encode/Decode Helpers

**Do:** Add JWT encode/decode helper functions in `backend/app/core/security.py` using python-jose, including expiry handling.

**Context & Why:** This is the token format every authenticated request in the entire app will present in its `Authorization` header — the same file already holding password hashing (Prompt 69) is the right home for this since both are core cryptographic security utilities.

**Requirements:**
- `def create_access_token(user_id: int, expires_minutes: int = None) -> str:` — if `expires_minutes` is not passed, default to `get_settings().jwt_expiry_minutes` (Prompt 58). Payload must include `sub` (subject, set to the string form of `user_id`), `exp` (expiry timestamp, computed as `datetime.utcnow() + timedelta(minutes=expires_minutes)`), and `iat` (issued-at timestamp). Sign with `jose.jwt.encode(payload, get_settings().jwt_secret, algorithm="HS256")`.
- `def decode_access_token(token: str) -> dict:` — calls `jose.jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])`, letting `jose.exceptions.ExpiredSignatureError` and `JWTError` propagate to the caller (Prompt 74 will be responsible for catching these and converting them into proper HTTP 401 responses — this function itself stays a pure decode/validate utility, not an HTTP-aware one).
- Never embed the user's email or password hash in the JWT payload — only the numeric `user_id` (as `sub`) should be present, keeping the token payload minimal and avoiding stale/sensitive data living inside a token that can't be revoked before its expiry.

**Acceptance Criteria:**
- [ ] `create_access_token(user_id=1)` produces a valid JWT string with `sub="1"`, a future `exp`, and a present-time `iat`.
- [ ] `decode_access_token(token)` on a freshly created token returns the correct payload dict.
- [ ] `decode_access_token(token)` on a manually expired token (e.g. one created with `expires_minutes=-1`) raises `ExpiredSignatureError`.
- [ ] `decode_access_token("garbage-string")` raises `JWTError`, not an unrelated crash.

**Must Not Break:** Uses `get_settings()` from Prompt 58 for both the secret and default expiry — must not hardcode either value here.

---

#### Prompt 71 — Auth Pydantic Schemas

**Do:** Define Pydantic schemas `UserCreate`, `UserLogin`, `UserOut`, `Token` in `backend/app/schemas/auth.py`.

**Context & Why:** These schemas are the exact contract the frontend's Signup/Login forms (Prompts 120–121) are built against — any mismatch in field names or types here versus what the frontend sends/expects becomes exactly the kind of "API-contract mismatch" Prompt 173 has to hunt down and fix later, so getting field names right the first time saves real integration pain.

**Requirements:**
- `UserCreate(BaseModel)`: `name: str`, `email: EmailStr` (requires `pydantic[email]` — add `email-validator` to `backend/requirements.txt` if not already pulled in transitively), `password: str` (add a `Field(min_length=8)` constraint, cross-referencing Prompt 77's password-strength requirement), `phone: Optional[str] = None`, `location: Optional[str] = None`.
- `UserLogin(BaseModel)`: `email: EmailStr`, `password: str`.
- `UserOut(BaseModel)`: `id: int`, `name: str`, `email: str`, `phone: Optional[str]`, `location: Optional[str]`, `profile_photo_url: Optional[str]`, `preferred_crops: List[str] = []`, `created_at: datetime`, `last_login_at: Optional[datetime]` — **explicitly excludes `password_hash`**; add `model_config = ConfigDict(from_attributes=True)` so this schema can be constructed directly from a SQLAlchemy `User` ORM instance.
- `Token(BaseModel)`: `access_token: str`, `token_type: str = "bearer"`.

**Acceptance Criteria:**
- [ ] `UserCreate` rejects a password under 8 characters and an invalid email format with a 422-style validation error when used as a route body.
- [ ] `UserOut.model_validate(some_user_orm_instance)` succeeds and never includes `password_hash` in its output, even if that attribute exists on the ORM object.
- [ ] `Token` serializes to exactly `{"access_token": "...", "token_type": "bearer"}`.

**Must Not Break:** `UserOut`'s fields must exactly match `User` model's public fields from Prompt 62 (minus `password_hash`).

---

#### Prompt 72 — `POST /auth/register`

**Do:** Implement `POST /auth/register` in `backend/app/routes/auth.py`: validate input, hash password, create user row, issue JWT.

**Context & Why:** This is the very first real, stateful API endpoint in the project and the entry point the frontend's Signup page (Prompt 120) calls directly — every later authenticated feature ultimately traces back to a user successfully passing through this route once.

**Requirements:**
- Route signature: `@router.post("/auth/register", response_model=Token, status_code=201)` accepting a `UserCreate` body (Prompt 71) and `db: Session = Depends(get_db)` (Prompt 61).
- Check for an existing user with the same email (`db.query(User).filter(User.email == payload.email).first()`); if found, raise `HTTPException(status_code=409, detail="Email already registered", headers=...)` using the project's standard error shape (per the Global Conventions: `{"detail": ..., "error_code": "EMAIL_ALREADY_EXISTS"}` — adapt FastAPI's default `detail`-only error body to include `error_code` via a custom exception or a consistent dict `detail` value).
- Hash the password with `hash_password` (Prompt 69), construct a new `User` ORM instance with all `UserCreate` fields (mapping `password` → `password_hash`), add/commit/refresh it via the session.
- Issue and return a `Token` via `create_access_token(user_id=new_user.id)` (Prompt 70) — signing the user in immediately on successful registration, matching Prompt 125's expectation that signup leads straight to an authenticated state without a separate login step.
- Wrap the DB insert in appropriate error handling so a race-condition duplicate-email insert (two simultaneous signups with the same email) still fails gracefully with the same 409 response rather than an unhandled `IntegrityError`.

**Acceptance Criteria:**
- [ ] A valid new signup returns `201` with a valid `Token` body.
- [ ] A second signup attempt with the same email returns `409` with a clear error message, and does NOT create a duplicate row (verify in the database).
- [ ] The created user's `password_hash` in the database is a bcrypt hash, never the plaintext submitted password.
- [ ] The returned token, when decoded (Prompt 70), contains the correct new user's `id` as `sub`.

**Must Not Break:** Must use `User` (Prompt 62), `UserCreate`/`Token` (Prompt 71), `hash_password`/`create_access_token` (Prompts 69–70), and `get_db` (Prompt 61) exactly as those modules already define them.

---

#### Prompt 73 — `POST /auth/login`

**Do:** Implement `POST /auth/login` in `backend/app/routes/auth.py`: verify credentials, update `last_login_at`, issue JWT.

**Context & Why:** This is the returning-user counterpart to Prompt 72, and the direct target of the frontend's Login page (Prompt 121) and the JWT-persistence-across-refresh test in Prompt 167.

**Requirements:**
- Route signature: `@router.post("/auth/login", response_model=Token)` accepting a `UserLogin` body (Prompt 71) and `db: Session = Depends(get_db)`.
- Look up the user by email; if not found, OR if found but `verify_password(payload.password, user.password_hash)` returns `False`, raise the **exact same** `HTTPException(status_code=401, detail="Incorrect email or password")` in both cases — deliberately do not distinguish "email not found" from "wrong password" in the response, since revealing which one it was is a well-known account-enumeration security leak.
- On successful verification, update `user.last_login_at = datetime.utcnow()` and commit this change before returning.
- Issue and return a `Token` the same way as Prompt 72.

**Acceptance Criteria:**
- [ ] Correct email+password returns `200` with a valid token, and the user's `last_login_at` in the database is updated to the current time.
- [ ] Wrong password for an existing email returns `401` with the generic message.
- [ ] A completely non-existent email returns the exact same `401` response body/status as the wrong-password case (byte-for-byte identical error response, confirmed by test).

**Must Not Break:** Must reuse `verify_password` (Prompt 69) and `create_access_token` (Prompt 70) unchanged; must not alter the `POST /auth/register` route from Prompt 72 (both live in the same `auth.py` file — keep them clearly separated).

---

#### Prompt 74 — `get_current_user` Dependency

**Do:** Create a `get_current_user` dependency in `backend/app/core/dependencies.py` that decodes the JWT from the Authorization header and loads the user from the database.

**Context & Why:** This single function is what every single protected route in the entire backend (users, predict, diseases-history, feedback — literally everything except `/health`, `/auth/register`, `/auth/login`, and the public `/diseases` listing) will depend on to establish "who is making this request" — it is also the exact mechanism enforcing the critical security rule stated in the Global Conventions that user identity always comes from the verified JWT, never from a client-supplied field.

**Requirements:**
- Use FastAPI's `OAuth2PasswordBearer` or a custom `HTTPBearer` security scheme to extract the raw token string from the `Authorization: Bearer <token>` header (this also makes the requirement show up correctly in the auto-generated `/docs` Swagger UI, relevant to Prompt 107).
- `def get_current_user(token: str = Depends(<scheme>), db: Session = Depends(get_db)) -> User:` — call `decode_access_token(token)` (Prompt 70), extract `sub` as the user id, query `db.query(User).filter(User.id == int(payload["sub"])).first()`.
- If the token is missing, malformed, expired, or the decoded user id doesn't correspond to any existing user (e.g. a user that was deleted after the token was issued), raise `HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})` — one consistent 401 response for every one of these distinct failure causes, not different messages per cause (again, to avoid leaking implementation details, and because the frontend only needs to know "not authenticated," not why).
- Return the fully-loaded `User` ORM object so route handlers can access any of its fields directly.

**Acceptance Criteria:**
- [ ] A route protected with `Depends(get_current_user)` correctly returns the right user object for a valid token.
- [ ] Missing `Authorization` header → 401.
- [ ] Malformed token string → 401.
- [ ] Expired token → 401.
- [ ] Well-formed, valid token whose `sub` refers to a now-deleted user id → 401 (not a 500 crash from a `None` user).

**Must Not Break:** Depends on `decode_access_token` (Prompt 70) and `get_db`/`User` (Prompts 61–62) with their existing signatures.

---

#### Prompt 75 — Consistent 401 Handling Across Protected Routes

**Do:** Add proper 401 error handling for missing/invalid/expired tokens across all protected routes.

**Context & Why:** This prompt is a verification/hardening pass confirming Prompt 74's dependency is actually wired into every route that needs it — a route accidentally left unprotected (forgetting to add `Depends(get_current_user)`) is a serious, easy-to-miss security bug that this pass exists specifically to catch before more routes get built on top of an inconsistent foundation.

**Requirements:**
- Audit every route file that will eventually exist under `backend/app/routes/` (at this point, only `auth.py` exists with two intentionally-public routes; this audit becomes more meaningful as Prompts 80+ add more routes, but establish the checklist/process now) and confirm: every route EXCEPT `/health`, `/auth/register`, `/auth/login`, and the eventual public `GET /diseases`/`GET /diseases/{id}` (Prompts 96–97) explicitly declares `current_user: User = Depends(get_current_user)` as a parameter.
- Add a small automated test (can live in `backend/tests/test_auth.py`, expanded in Prompt 76) that introspects the FastAPI app's route list and asserts that every route path NOT in an explicit allowlist has the `get_current_user` dependency present in its dependency graph — this turns "did we forget to protect a route" from a manual code-review concern into an automatically enforced one.
- Ensure the 401 response body shape is identical regardless of which specific route triggered it (relies on Prompt 74's dependency being the single source of this behavior, not route-specific try/except blocks re-implementing 401 handling inconsistently).

**Acceptance Criteria:**
- [ ] The automated allowlist-based test exists and passes against the current route set, and is written to also apply correctly as future routes (Prompts 80+) are added.
- [ ] Manually calling any currently-protected-in-spirit-but-not-yet-implemented route stub (if any exist as placeholders) with no `Authorization` header returns 401 with the standard shape.

**Must Not Break:** Must not change the intentionally-public routes' behavior (`/health`, `/auth/register`, `/auth/login`).

---

#### Prompt 76 — Auth Test Suite

**Do:** Write `backend/tests/test_auth.py` covering register success, duplicate-email rejection, login success, and login failure with wrong password.

**Context & Why:** This is the first real automated test coverage for the backend, and the direct proof that Prompts 72–73's two most important routes behave exactly as specified — it also becomes the foundation Prompt 105's shared fixtures and Prompt 106's coverage report build on.

**Requirements:**
- Use FastAPI's `TestClient` (via `httpx`) against the app instance, pointed at a **test-specific database** (not the local dev database) — even before Prompt 105 formalizes shared fixtures, this test file should already isolate itself (e.g. via a temporary SQLite database or a dedicated test Postgres database/schema) so running tests never touches or pollutes real development data.
- Test `test_register_success`: POST valid signup data to `/auth/register`, assert `201`, assert response contains `access_token`, assert a corresponding row now exists in the `users` table.
- Test `test_register_duplicate_email_rejected`: register once successfully, attempt to register again with the same email (different other fields is fine), assert `409`, assert only one row exists for that email in the database.
- Test `test_login_success`: register a user, then log in with the same credentials, assert `200` and a valid `access_token`, assert `last_login_at` was updated in the database.
- Test `test_login_wrong_password_fails`: register a user, attempt login with an incorrect password, assert `401`.
- Include Prompt 75's route-allowlist test in this same file, or note explicitly if it's been placed elsewhere.

**Acceptance Criteria:**
- [ ] All four (or five, including the allowlist test) tests pass with `pytest backend/tests/test_auth.py`.
- [ ] Tests do not depend on execution order (each test independently sets up its own needed data — no test relies on a previous test having already created a specific user).
- [ ] Running the full file twice in a row (fresh test-database state each time, or self-cleaning) produces identical pass results both times.

**Must Not Break:** Tests must exercise the real `/auth/register` and `/auth/login` routes exactly as implemented in Prompts 72–73, not mocked-out versions.

---

#### Prompt 77 — Email Format and Password Strength Validation

**Do:** Add email-format and password-strength validation to the `UserCreate` schema.

**Context & Why:** Prompt 71 already added a basic `EmailStr` type and an 8-character minimum length — this prompt is about going further to actually enforce meaningful password strength, closing a gap a security-focused viva question (or Prompt 184's later audit) would otherwise flag.

**Requirements:**
- In `backend/app/schemas/auth.py`'s `UserCreate`, add a custom Pydantic validator (`@field_validator("password")`) enforcing, in addition to the existing minimum length of 8: at least one uppercase letter, at least one lowercase letter, at least one digit — raise a `ValueError` with a clear, specific message identifying exactly which requirement was missed (not just a generic "invalid password") so the frontend's error display (Prompt 123) can show something genuinely useful.
- Confirm `EmailStr` from Prompt 71 is already correctly rejecting malformed emails (e.g. `"not-an-email"`) — if it isn't already working correctly, fix the underlying `email-validator` dependency installation rather than writing a redundant custom regex validator.
- Do NOT implement any password strength rule that would be considered outdated/harmful best practice (e.g. do not require special characters as a hard rule if it meaningfully hurts usability without a corresponding security benefit — length and character-class diversity as specified above is a defensible, modern minimum; document this reasoning briefly in a code comment).

**Acceptance Criteria:**
- [ ] `UserCreate` rejects `"alllowercase1"` missing an uppercase letter, `"ALLUPPERCASE1"` missing a lowercase letter, and `"NoDigitsHere"` missing a digit, each with a specific, distinct error message.
- [ ] `UserCreate` accepts a genuinely strong password like `"Str0ngPass"`.
- [ ] Malformed emails are rejected by the existing `EmailStr` type (verify, don't assume).

**Must Not Break:** Must not change `UserCreate`'s field names or the `Token`/`UserLogin`/`UserOut` schemas from Prompt 71 — this is an additive validation-only change to one field.

---

#### Prompt 78 — Brute-Force Protection Stub on Login

**Do:** Add rate-limiting or basic brute-force protection notes/middleware stub on the `/auth/login` route.

**Context & Why:** A login endpoint with no rate limiting is a standing invitation for credential-stuffing/brute-force attacks — this prompt establishes at least a basic, documented mitigation now, with Prompt 187 explicitly planned to harden it further during the dedicated security pass in Phase 4.

**Requirements:**
- Implement a simple in-memory (or Redis-backed if the team already has Redis available — otherwise in-memory is acceptable for this stage, with a code comment noting it won't survive across multiple server instances/restarts and should be revisited for production in Prompt 187) rate limiter: track failed login attempts per email (or per IP) over a rolling time window (e.g. max 5 failed attempts per 15 minutes), and return `HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")` once the threshold is exceeded.
- Reset the failed-attempt counter for a given email/IP immediately on a successful login.
- Clearly document in a code comment (and in `backend/README.md`, referenced again in Prompt 108) that this is an intentionally basic, single-process implementation for now, with a named forward-reference to Prompt 187 for production hardening (e.g. a proper distributed rate-limiter, IP-based in addition to email-based tracking, etc.).

**Acceptance Criteria:**
- [ ] 5 consecutive failed login attempts for the same email within the time window trigger a `429` on the 6th attempt, even with the correct password on that 6th attempt.
- [ ] A successful login resets the counter, allowing subsequent failed attempts to again take up to 5 tries before triggering the limit.
- [ ] The limitation of this basic approach is explicitly documented, not silently presented as a complete solution.

**Must Not Break:** Must not alter the core success/failure logic of `/auth/login` from Prompt 73 — this wraps additional rate-limiting logic around the existing route, it doesn't change credential verification itself.

---
### 2.D User Profile Module

#### Prompt 79 — Profile Schemas

**Do:** Define Pydantic schemas `UserProfileOut` and `UserProfileUpdate` in `backend/app/schemas/user.py`.

**Context & Why:** These are separate from Prompt 71's `UserOut` because the profile page (Prompt 154) and its edit form (Prompt 155) have slightly different needs than the auth response — this separation also means changing what the profile page exposes/accepts later won't risk breaking the auth flow's response contract.

**Requirements:**
- `UserProfileOut(BaseModel)`: identical field set to `UserOut` (Prompt 71) — reuse `UserOut` directly via inheritance or aliasing (`UserProfileOut = UserOut`) rather than duplicating the field list verbatim, unless a genuine difference emerges later; document the choice either way in a code comment so it's clear this wasn't accidental duplication.
- `UserProfileUpdate(BaseModel)`: `name: Optional[str] = None`, `phone: Optional[str] = None`, `location: Optional[str] = None`, `preferred_crops: Optional[List[str]] = None` — **deliberately excludes `email` and `password`** (email changes and password changes are sensitive enough to warrant their own dedicated, more carefully-guarded endpoints if ever added later — out of scope for this 220-prompt build, but the exclusion here should be a deliberate, documented decision, not an oversight).
- All fields on `UserProfileUpdate` optional, since a `PUT` (Prompt 81) should support partial updates (only fields the user actually changed are sent).

**Acceptance Criteria:**
- [ ] `UserProfileOut` never includes `password_hash`.
- [ ] `UserProfileUpdate` has no `email` or `password` field, confirmed by inspecting the schema's fields programmatically in a quick test.
- [ ] A `UserProfileUpdate` instance with all fields omitted validates successfully (all-optional confirmed).

**Must Not Break:** Should reuse, not duplicate, `UserOut` from Prompt 71 where the field sets are genuinely identical.

---

#### Prompt 80 — `GET /users/me`

**Do:** Implement `GET /users/me` in `backend/app/routes/users.py` returning the current authenticated user's profile.

**Context & Why:** This is the first route to use `get_current_user` (Prompt 74) for something other than authorization gatekeeping — here the dependency's return value IS the actual response payload, which is exactly the pattern every later "my own data" route (stats, history) will follow.

**Requirements:**
- `@router.get("/users/me", response_model=UserProfileOut)` with `current_user: User = Depends(get_current_user)` as its only parameter (no `db` dependency needed separately, since `get_current_user` already did the database lookup).
- Simply return `current_user` — FastAPI's `response_model` will handle converting the ORM object to the `UserProfileOut` schema automatically (relying on that schema's `from_attributes=True` config inherited from `UserOut`, per Prompt 79).
- No request body, no query parameters.

**Acceptance Criteria:**
- [ ] Calling with a valid token returns 200 and the correct authenticated user's full profile.
- [ ] Calling with no/invalid token returns 401 (inherited automatically from `get_current_user`'s existing behavior, Prompt 74 — no route-specific 401 logic needed here).
- [ ] Two different users' tokens return two different, correct profiles (never leaks user A's data when user B's token is presented) — this is the first concrete test of the data-isolation principle formally verified later in Prompt 172.

**Must Not Break:** Depends on `get_current_user` (Prompt 74) and `UserProfileOut` (Prompt 79) exactly as defined.

---

#### Prompt 81 — `PUT /users/me`

**Do:** Implement `PUT /users/me` allowing the user to update name, phone, location, and preferred_crops.

**Context & Why:** This is the backend half of the frontend's Edit Profile form (Prompt 155) — it must support true partial updates so the frontend doesn't need to resend every field just to change one.

**Requirements:**
- `@router.put("/users/me", response_model=UserProfileOut)` accepting a `UserProfileUpdate` body (Prompt 79), `current_user: User = Depends(get_current_user)`, `db: Session = Depends(get_db)`.
- For each field present (not `None`) in the incoming `UserProfileUpdate`, set the corresponding attribute on `current_user` — use `payload.model_dump(exclude_unset=True)` (not `exclude_none=True` alone) so a field explicitly sent as an empty string still updates, but a field genuinely omitted from the request body is left untouched, correctly distinguishing "user wants to clear this field" from "user didn't touch this field."
- Commit and refresh, then return the updated `current_user`.
- Reject attempts to set fields not present on `UserProfileUpdate` (this is naturally enforced by Pydantic already rejecting unknown fields if the schema is configured with `extra="forbid"` — set this explicitly rather than relying on default lenient behavior, to make it impossible for a client to sneak an `email` or `password_hash` field into this request body).

**Acceptance Criteria:**
- [ ] Sending only `{"location": "Kolkata"}` updates just the location field, leaving name/phone/preferred_crops unchanged.
- [ ] Sending an unrecognized field (e.g. `{"email": "new@example.com"}`) is rejected with a 422 validation error, not silently ignored or silently applied.
- [ ] The updated profile is immediately reflected in a subsequent `GET /users/me` call.

**Must Not Break:** Must operate only on the currently authenticated user (`current_user` from the JWT) — never accept or honor any user-id field from the request body itself.

---

#### Prompt 82 — Profile Photo Upload

**Do:** Implement `POST /users/me/photo` accepting a profile-photo upload, storing it, and updating `profile_photo_url`.

**Context & Why:** This is the backend counterpart to the frontend's photo-upload control (Prompt 156) and feeds directly into the avatar shown in the navbar (Prompt 160) and dashboard header (Prompt 128).

**Requirements:**
- `@router.post("/users/me/photo", response_model=UserProfileOut)` accepting `file: UploadFile = File(...)`, `current_user`, `db`.
- Validate the uploaded file's content type is an accepted image format (`image/jpeg`, `image/png`, `image/webp`) — reject anything else with a `422`/`400` and a clear message.
- Enforce a maximum file size (reuse `get_settings().max_upload_size_mb` from Prompt 58, applied consistently here and later in Prompt 89's prediction upload) — reject oversized files before fully reading them into memory where practical.
- Store the file (for local/simple deployment, this can be a local `backend/uploads/profile_photos/` directory served via a static file mount added to `main.py`; note that Prompt 93 later introduces the option of proper object storage for prediction images, and this same approach could be adopted here too — pick local storage now, document the upgrade path in a comment) using a generated unique filename (e.g. `f"{current_user.id}_{uuid4().hex}.{ext}"`) to avoid collisions and to avoid using any user-supplied filename directly (a path-traversal risk relevant again in Prompt 188's security review).
- Update `current_user.profile_photo_url` to the resulting accessible URL/path and commit.

**Acceptance Criteria:**
- [ ] Uploading a valid JPEG/PNG updates `profile_photo_url` and the file is retrievable at that URL.
- [ ] Uploading a non-image file (e.g. a `.txt`) is rejected with a clear error.
- [ ] Uploading a file exceeding the configured max size is rejected before consuming excessive memory/disk.
- [ ] The generated filename never directly reuses the client-supplied original filename.

**Must Not Break:** Must not affect any other `UserProfileUpdate` fields (Prompt 81) — this route only touches `profile_photo_url`.

---

#### Prompt 83 — Initials-Based Default Avatar

**Do:** Add default-avatar generation logic (initials-based) for users without an uploaded photo.

**Context & Why:** Most new users won't upload a photo immediately after signing up, so the UI needs a sensible fallback rather than a broken image icon everywhere `profile_photo_url` would otherwise be `None` — this matches the frontend's `Avatar.tsx` component's stated initials-fallback design (Prompt 115).

**Requirements:**
- This is primarily a **frontend-side responsibility** (Prompt 115's `Avatar.tsx` component) — however, the backend's role here is to make this easy: ensure `UserProfileOut`/`UserOut`'s `profile_photo_url` is explicitly `null`/`None` (never an empty string or a broken placeholder URL) when no photo has been uploaded, so the frontend can reliably branch on `photo_url == null` to decide whether to render initials.
- Optionally, add a small pure helper function `get_initials(name: str) -> str` in `backend/app/core/security.py` or a new small `backend/app/core/utils.py` (e.g. returning the first letter of the first and last words of `name`, uppercased) that COULD be used if the team decides initials should ever be computed server-side (e.g. for server-rendered emails later) — but the primary, required implementation of the visible avatar fallback belongs in Prompt 115 on the frontend; this backend prompt's job is just to guarantee the clean `None`/`null` contract that makes that possible.

**Acceptance Criteria:**
- [ ] A newly registered user (no photo uploaded) has `profile_photo_url: null` in every API response that includes it, never an empty string.
- [ ] After a successful photo upload (Prompt 82), `profile_photo_url` becomes a real, non-null URL.

**Must Not Break:** Must not change `UserProfileOut`'s field types (Prompt 79) — `profile_photo_url` remains `Optional[str]`.

---

#### Prompt 84 — `GET /users/me/stats`

**Do:** Implement `GET /users/me/stats` returning total scans, diseases-detected count, and healthy-count for the dashboard cards.

**Context & Why:** This is the exact data source for Prompt 129's three dashboard `StatsCard` components — its numbers must be computed correctly and efficiently since this endpoint will be called every time a user visits their dashboard.

**Requirements:**
- `@router.get("/users/me/stats")` returning a small ad-hoc response model (define `UserStatsOut(BaseModel)` in `backend/app/schemas/user.py`, extending Prompt 79's file): `total_scans: int`, `diseases_detected: int`, `healthy_confirmed: int`.
- Compute via efficient database aggregation queries scoped to `current_user.id` — `total_scans` = `count(*)` of `predictions` where `user_id = current_user.id`; `diseases_detected` = count where `disease != 'Healthy'` (or wherever the healthy/disease distinction is encoded per the seeded `Disease` naming from Prompt 67 — use whatever exact string/convention was actually seeded, don't assume); `healthy_confirmed` = count where `disease == 'Healthy'`. Use SQL-side `COUNT`/`CASE WHEN` aggregation (e.g. via SQLAlchemy's `func.count`, `case()`) rather than loading every prediction row into Python and counting in application code, for efficiency as history grows.
- All three counts must be scoped strictly to `current_user` — reuse the same identity-from-JWT pattern as every other protected route.

**Acceptance Criteria:**
- [ ] A user with a mix of healthy and diseased predictions gets correct counts across all three fields, verified against a manually-inserted test dataset.
- [ ] A brand-new user with zero predictions gets `{"total_scans": 0, "diseases_detected": 0, "healthy_confirmed": 0}`, not an error.
- [ ] User A's stats are unaffected by user B's predictions (isolation check).

**Must Not Break:** Depends on the `Prediction` model's exact field names from Prompt 63 (`user_id`, `disease`) — must use the exact "Healthy" string convention that Prompt 67's seed data and Prompt 89's prediction-writing logic actually use (cross-check, don't assume).

---

#### Prompt 85 — Users Module Tests

**Do:** Write `backend/tests/test_users.py` covering profile fetch, profile update, and stats calculation.

**Context & Why:** Closes out sub-phase 2.D with automated proof that Prompts 80, 81, and 84 behave correctly, extending the testing pattern established in Prompt 76.

**Requirements:**
- Reuse the same test-database isolation approach as `test_auth.py` (Prompt 76) — do not introduce a second, inconsistent test-setup pattern; if `conftest.py` (Prompt 105) doesn't exist yet at the time this prompt is executed, replicate `test_auth.py`'s setup here and plan to consolidate once `conftest.py` lands.
- Test `test_get_profile`: register a user, call `GET /users/me` with their token, assert the returned profile matches what was registered.
- Test `test_update_profile_partial`: register a user, `PUT /users/me` with only `{"location": "..."}`, assert only that field changed and others remained as originally set.
- Test `test_update_profile_rejects_email_field`: attempt to `PUT /users/me` with an `email` field present, assert a 422.
- Test `test_stats_zero_for_new_user`: register a user, call `GET /users/me/stats`, assert all three counts are 0.
- Test `test_stats_with_predictions`: manually insert a few `Prediction` rows directly via the test database session for a given user (mixing healthy/diseased outcomes), call `GET /users/me/stats`, assert the counts exactly match the inserted data.

**Acceptance Criteria:**
- [ ] All five tests pass.
- [ ] Tests are independent and order-agnostic, matching the standard established in Prompt 76.

**Must Not Break:** Must test the real routes from Prompts 80, 81, 84 exactly as implemented, using the real `User`/`Prediction` models (Prompts 62–63).

---
### 2.E Prediction / Inference Module

#### Prompt 86 — Model Service (Singleton Load)

**Do:** Create `backend/app/services/model_service.py` that loads `crop_disease_model.keras` and `class_names.json` once at application startup (singleton pattern).

**Context & Why:** Loading a TensorFlow model from disk takes real time (potentially seconds) and real memory — doing this on every single `/predict` request would make the API unacceptably slow and would eventually be the exact bottleneck Prompt 182's load test is designed to surface; loading it exactly once at startup and reusing the same in-memory model object for every request is the standard, correct pattern.

**Requirements:**
- Define a `ModelService` class (or a simpler module-level singleton via a `@lru_cache`-wrapped getter function — pick one pattern and use it consistently) that, on first access, loads `tf.keras.models.load_model(get_settings().model_path)` (Prompt 58) and `json.load(open(get_settings().class_names_path))` (Prompt 58), storing both as instance/module attributes.
- Expose `def predict(self, preprocessed_image: np.ndarray) -> Tuple[int, float]:` returning `(predicted_class_index, confidence)`, where `confidence` is the max softmax probability, computed via `model.predict(np.expand_dims(preprocessed_image, axis=0))` (adding the batch dimension the model expects) followed by `np.argmax` and `np.max` on the resulting single-row output.
- Wire this service to be instantiated once at FastAPI startup via a `@app.on_event("startup")` handler in `main.py` (or the newer `lifespan` context manager pattern — either is acceptable, prefer `lifespan` if the team's FastAPI version supports it well, and document the choice), storing the loaded service on `app.state.model_service` so route handlers can access it via `request.app.state.model_service` or a dedicated FastAPI dependency wrapping that access.
- Log (via Python's standard `logging` module, not bare `print`) a clear message when the model finishes loading, including the model file path and how long loading took, so this is visible in server startup logs and easy to confirm in Prompt 197's deployment smoke test.
- Fail loudly and immediately at startup (crash the app, don't start accepting requests) if the model or class_names file fails to load — a backend that "starts successfully" but can't actually run predictions is worse than one that fails fast and obviously.

**Acceptance Criteria:**
- [ ] The model loads exactly once per application process lifetime (verify by adding a temporary log/counter during development and confirming it doesn't increment per-request).
- [ ] `predict()` on a known sample input returns a class index in `[0, 7]` and a confidence in `[0.0, 1.0]`.
- [ ] Deliberately pointing `MODEL_PATH` at a non-existent file causes the app to fail at startup with a clear error, not a lazy failure on the first prediction request.

**Must Not Break:** Must load the exact files frozen in Phase 1 (Prompts 42–43/55) via the paths configured in Prompt 58 — must not hardcode a different path or silently fall back to a different model file if the configured one is missing.

---

#### Prompt 87 — Preprocessing Service (Production Parity)

**Do:** Create `backend/app/services/preprocessing_service.py` replicating the exact resize/normalize logic used during training, applied to incoming uploaded images.

**Context & Why:** This is the single most important correctness-critical file in the entire backend — as flagged repeatedly since Prompt 16, any divergence here from the training-time preprocessing (`ml/preprocessing/loader.py`) silently degrades every production prediction without raising any visible error, since the model will still happily produce a (wrong) softmax output on mismatched input.

**Requirements:**
- Do not reimplement preprocessing logic independently — instead, either (a) import `ml/preprocessing/loader.py`'s `load_and_preprocess_image` function directly if the backend's Python environment/deployment can practically share code with the `ml/` folder (e.g. via a small shared local package, or by copying the file verbatim with a clear "keep in sync with ml/preprocessing/loader.py" comment at the top if a shared-package setup isn't practical for this project's structure), or (b) if truly reimplementing, copy the exact resize method (bilinear), exact target size (224×224), exact color conversion (RGB), and exact normalization range (`[0,1]`) with no deviation, and add an automated cross-check test (see Prompt 95) that runs both the `ml/` version and the `backend/` version on the same sample image and asserts numerically identical output.
- Accept the raw uploaded file's bytes (from FastAPI's `UploadFile.read()`) as input, since production input arrives as an in-memory upload, not a filesystem path — confirm Prompt 16's `load_and_preprocess_image` signature already supports a bytes input (it was specifically designed to in Prompt 16) and reuse that exact code path.
- Return the same `(224, 224, 3)` float32 `[0,1]`-range array shape that `model_service.predict()` (Prompt 86) expects as input.

**Acceptance Criteria:**
- [ ] Preprocessing a known sample image's bytes here produces a numerically identical array (via `np.allclose`) to running `ml/preprocessing/loader.py`'s function on the same image's file path.
- [ ] Passing corrupted/invalid image bytes raises the same `ImageLoadError` (or an equivalent, clearly-defined exception) as the `ml/` version, for consistent error handling upstream in Prompt 94.

**Must Not Break:** Must maintain output shape/range/dtype parity with Prompt 86's `model_service.predict()` input expectations, and logical parity with `ml/preprocessing/loader.py` (Prompt 16) and `ml/preprocessing/README.md`'s (Prompt 25) documented "Parity With Production" contract.

---

#### Prompt 88 — Prediction Response Schema

**Do:** Define Pydantic schema `PredictionOut` in `backend/app/schemas/prediction.py` matching the documented API response shape.

**Context & Why:** This schema is the exact contract the frontend's Result page (Prompt 143) is built against — every field the UI needs to render (image, crop, disease, confidence, symptoms/prevention/management, confidence flag) must be present here with names the frontend will actually consume without any renaming/mapping friction.

**Requirements:**
- `PredictionOut(BaseModel)`: `id: int`, `crop: str`, `disease: str`, `confidence: float` (as a `0.0–1.0` fraction, matching the storage convention from Prompt 63 — the frontend, per Prompt 143/144, is responsible for formatting this as a percentage for display, not the backend), `is_confident: bool`, `image_url: Optional[str]`, `created_at: datetime`, and a nested disease-info object: `disease_info: DiseaseInfoOut` containing `description: str`, `symptoms: str`, `prevention: str`, `management: str` (matching whatever text/JSON structure was decided in Prompt 64 for these fields).
- Add `model_config = ConfigDict(from_attributes=True)` for ORM compatibility.
- Define `DiseaseInfoOut` as its own reusable nested schema in the same file (also reused later by Prompts 96–97's `/diseases` endpoints, so define it once here rather than duplicating it in a separate schemas file).

**Acceptance Criteria:**
- [ ] Schema includes every field named above with correct types.
- [ ] `confidence` is documented (in a field description or docstring) as a `0.0–1.0` fraction, not a percentage, to prevent a unit-mismatch bug when the frontend consumes it.
- [ ] `DiseaseInfoOut` is defined once and importable/reusable, not duplicated.

**Must Not Break:** Field types must be consistent with `Prediction` (Prompt 63) and `Disease` (Prompt 64) models.

---

#### Prompt 89 — `POST /predict`

**Do:** Implement `POST /predict` in `backend/app/routes/predict.py`: accept multipart image upload, validate file type/size, run preprocessing + inference.

**Context & Why:** This is the single most important route in the entire application — the whole product's value proposition (upload a leaf photo, get a diagnosis) happens here, and it's the direct target of the frontend's scan flow (Prompt 138).

**Requirements:**
- `@router.post("/predict", response_model=PredictionOut)` accepting `file: UploadFile = File(...)`, `current_user: User = Depends(get_current_user)`, `db: Session = Depends(get_db)`.
- Validate content type (`image/jpeg`, `image/png`, `image/webp`) and size (against `get_settings().max_upload_size_mb`, reusing the same validation approach established in Prompt 82) BEFORE running any preprocessing/inference, to fail fast and cheaply on bad input.
- Call Prompt 87's preprocessing service on the uploaded bytes, then Prompt 86's model service's `predict()` on the result, obtaining `(predicted_class_index, confidence)`.
- Map `predicted_class_index` to a crop/disease name via the same `class_names.json` data already loaded inside `model_service` (Prompt 86) — do not re-load or re-parse this file separately here.
- This prompt covers validation + inference only — wiring the confidence threshold (Prompt 90), disease-info lookup (Prompt 91), and database persistence (Prompt 92) are each their own subsequent prompts; keep this prompt's scope to producing the raw `(crop, disease, confidence)` result correctly and return a provisional response (later prompts will complete the full response construction).

**Acceptance Criteria:**
- [ ] Uploading a valid image returns a successful prediction with a real crop/disease name and a confidence value in `[0.0, 1.0]`.
- [ ] Uploading a non-image file is rejected before any model inference is attempted.
- [ ] Uploading an oversized file is rejected before the full file is read into memory.
- [ ] The route requires authentication (401 without a valid token).

**Must Not Break:** Must use Prompt 86's model service and Prompt 87's preprocessing service exactly as built — must not reimplement either inline in this route.

---

#### Prompt 90 — Confidence Threshold Logic

**Do:** Add confidence-threshold logic to `/predict` that sets `is_confident: false` and an "uncertain result" message below the production threshold.

**Context & Why:** This is the direct backend implementation of the exact decision documented in `ml/evaluation/CONFIDENCE_THRESHOLD.md` (Prompt 48) — the threshold value must be read from that ML-phase decision (via `get_settings().confidence_threshold`, Prompt 58), never re-guessed independently in this route.

**Requirements:**
- Extend Prompt 89's `/predict` logic: after obtaining `confidence`, compute `is_confident = confidence >= get_settings().confidence_threshold`.
- When `is_confident` is `False`, the response should still include the raw predicted crop/disease/confidence (the frontend, per Prompt 146, will render a distinct "uncertain result" warning UI state around this same data, not receive a fundamentally different response shape) — do not omit or null-out the prediction fields just because confidence was low; only the `is_confident` flag changes.
- This threshold check must use the exact same `>=` comparison direction and the exact configured value — write a code comment citing `ml/evaluation/CONFIDENCE_THRESHOLD.md` as the source of truth for this number.

**Acceptance Criteria:**
- [ ] A prediction with confidence above the configured threshold returns `is_confident: true`.
- [ ] A prediction with confidence below the threshold returns `is_confident: false`, while still including the actual predicted crop/disease/confidence values (not nulled out).
- [ ] Changing `CONFIDENCE_THRESHOLD` in `.env` correctly changes this route's behavior on the next request (confirms it's read from config, not hardcoded).

**Must Not Break:** Must not change Prompt 89's validation/inference logic — this is additive logic layered on top of the already-obtained `confidence` value.

---

#### Prompt 91 — Wire Disease Information Lookup

**Do:** Wire `/predict` to look up the predicted disease's info from the `diseases` table and include it in the response.

**Context & Why:** This connects the model's raw numeric prediction to the actual human-readable guidance (symptoms/prevention/management) that gives the app real value beyond just naming a disease — this is the `disease_info` nested object in `PredictionOut` (Prompt 88) that the frontend's Result page (Prompt 145) directly renders.

**Requirements:**
- After determining the predicted `crop`/`disease` strings (Prompt 89), query `db.query(Disease).filter(Disease.crop == crop, Disease.disease_name == disease).first()`.
- If no matching row is found (which should be impossible if Prompt 67's seeding correctly covered all 8 classes from `class_names.json` — but defensively handle it anyway), raise a clear `500`-level internal error with a descriptive log message (this indicates a data-integrity bug between the model's classes and the seeded `diseases` table, not a normal user-facing error condition, and should be loud in logs for a developer to notice and fix, rather than silently returning an incomplete response).
- Populate the `disease_info` field of the response with the found row's `description`, `symptoms`, `prevention`, `management`.

**Acceptance Criteria:**
- [ ] Every one of the 8 possible predicted classes correctly resolves to its matching seeded `Disease` row and returns real, non-empty `disease_info`.
- [ ] The defensive "no matching disease found" code path is manually verified once (e.g. by temporarily testing against a database missing one seed row) to confirm it fails loudly rather than silently.

**Must Not Break:** Depends on Prompt 67's seed data actually covering the exact same crop/disease-name strings the model's `class_names.json` (Prompt 43) produces — cross-check string formatting consistency (e.g. exact capitalization/spacing) between the two.

---

#### Prompt 92 — Persist Predictions to the Database

**Do:** Wire `/predict` to save a new row to the `predictions` table with the correct `user_id` from the authenticated request.

**Context & Why:** Without this, every prediction would be ephemeral — no history (Prompt 98), no stats (Prompt 84), no dashboard recent-scans (Prompt 130). This is also the exact point where the critical security rule (`user_id` always from the JWT, never client-supplied) is enforced for prediction data specifically.

**Requirements:**
- After computing `crop`, `disease`, `confidence`, `is_confident` (Prompts 89–90), construct a new `Prediction` ORM instance with `user_id=current_user.id` (from the `get_current_user`-derived object, never from any request body/form field), plus the computed fields, and commit it.
- Include the newly-created row's real database `id` and `created_at` in the returned `PredictionOut` response (so the frontend's feedback control, Prompt 148, has a real `prediction_id` to reference).
- Ensure this database write happens within the same request as the inference call — if the database write fails (e.g. a transient connection issue), the response should reflect an error rather than returning a "successful" prediction that was never actually persisted (silently losing history data).

**Acceptance Criteria:**
- [ ] A successful `/predict` call creates exactly one new row in `predictions` with the correct `user_id`, `crop`, `disease`, `confidence`, `is_confident`.
- [ ] The returned response's `id`/`created_at` match the actual persisted row.
- [ ] Simulating a database failure during this step (e.g. in a test with a broken session) results in a clear error response, not a "successful" response with silently lost data.

**Must Not Break:** Must use `Prediction` (Prompt 63) and `get_db`/session patterns (Prompt 61) exactly as already defined; must not accept a `user_id` from anywhere other than `current_user`.

---

#### Prompt 93 — Optional Raw Image Persistence

**Do:** Add optional image persistence: upload the raw image to object storage and store its URL on the prediction row.

**Context & Why:** Storing the actual uploaded image (not just the prediction result) lets users review exactly what they photographed later (Prompt 152's history detail view shows the original image), but this is explicitly optional/best-effort so a storage hiccup never blocks the core prediction feature from working.

**Requirements:**
- Following the same local-storage-now, documented-upgrade-path-later pattern established in Prompt 82 (or, if the team has already set up real object storage like S3/Cloudinary/Supabase Storage by this point, use that instead — either is acceptable, but be consistent with whatever choice Prompt 82 made for profile photos), save the uploaded prediction image using a generated unique filename (never the client-supplied name, same path-traversal precaution as Prompt 82) and set `Prediction.image_url` to the resulting accessible URL.
- **Make this step fail-soft**: wrap the image-saving logic in a try/except that logs a warning and proceeds with `image_url = None` on failure, rather than letting an image-storage failure prevent the actual prediction (which is the feature's core value) from completing and being saved. Document this explicitly as an intentional design decision in a code comment.
- Reuse the max-file-size validation already enforced in Prompt 89 — do not re-read or re-validate the file a second time unnecessarily; store the already-validated, already-read bytes.

**Acceptance Criteria:**
- [ ] A successful `/predict` call results in `image_url` being populated and the image retrievable at that URL.
- [ ] Simulating an image-storage failure (e.g. a full/unwritable storage path in a test) still results in a successful prediction response with `image_url: null`, not a failed request.

**Must Not Break:** Must not change the core prediction/persistence logic from Prompts 89–92 — image storage is additive and must degrade gracefully, never block the primary flow.

---

#### Prompt 94 — Robust Error Handling for `/predict`

**Do:** Add robust error handling for invalid/corrupt image uploads and for model-inference failures.

**Context & Why:** This is a dedicated hardening pass over the whole `/predict` route built across Prompts 89–93, ensuring every realistic failure mode returns a clear, correctly-coded response instead of an unhandled 500 stack trace leaking internal details to the client.

**Requirements:**
- Catch `ImageLoadError` (or whatever exception Prompt 87's preprocessing service raises on corrupt/invalid images) and return a `422` with a clear, user-facing message like "The uploaded file could not be processed as a valid image."
- Catch any exception raised during `model_service.predict()` (Prompt 86) — while this should be rare given Prompts 86–87's careful design, a defensive catch here should return a `500` with a generic user-facing message (never leak the raw exception/stack trace to the client) while logging the full exception details server-side for debugging.
- Confirm the file-type/size validation from Prompt 89 already returns clear `4xx` errors (verify, don't just assume) rather than raising unhandled exceptions if, say, `UploadFile.content_type` is unexpectedly `None`.
- Ensure the response error shape stays consistent with the project's global error-shape convention (`{"detail": ..., "error_code": ...}`) across every one of these cases.

**Acceptance Criteria:**
- [ ] Uploading a deliberately corrupted image file (valid extension, invalid content) returns a clean `422`, not a `500` with a raw traceback.
- [ ] A simulated model-inference exception (e.g. via a test that monkey-patches `model_service.predict` to raise) returns a clean `500` with a generic message, and the real exception details appear in server logs, not in the response.
- [ ] No response body from this route, under any failure condition, ever includes a raw Python traceback or internal file path.

**Must Not Break:** Must wrap, not replace, the successful-path logic from Prompts 89–93.

---

#### Prompt 95 — Predict Module Tests

**Do:** Write `backend/tests/test_predict.py` covering a valid prediction, a low-confidence prediction, and an invalid file upload.

**Context & Why:** This is the automated proof that the single most important route in the app (Prompts 86–94) works correctly end-to-end, including its most important edge cases.

**Requirements:**
- Test `test_predict_valid_image`: authenticate a test user, upload a real, known sample image (a small fixture image committed to `backend/tests/fixtures/`, ideally one where the expected predicted class is roughly known/verifiable), assert `200`, assert the response includes a valid `crop`/`disease`/`confidence`/`disease_info`, and assert a new row was created in `predictions` for that user.
- Test `test_predict_low_confidence_flagged`: this is harder to trigger with a real model deterministically — achieve it either by temporarily monkey-patching/mocking `model_service.predict` to return a low, known confidence value for this specific test, or by using a genuinely ambiguous test image if one is known to reliably produce low confidence; assert `is_confident: false` in the response.
- Test `test_predict_invalid_file_rejected`: upload a non-image file (e.g. a `.txt`), assert a `4xx` response, assert NO new row was created in `predictions`.
- Test `test_predict_requires_auth`: call `/predict` with no `Authorization` header, assert `401`.
- Include (per Prompt 87's requirement) the cross-check test comparing `ml/preprocessing/loader.py`'s output to `backend/app/services/preprocessing_service.py`'s output on the same sample image, asserting numerical equality — this can live in this file or in a dedicated `test_preprocessing_parity.py`, but it must exist somewhere in the test suite.

**Acceptance Criteria:**
- [ ] All five described tests pass.
- [ ] The preprocessing-parity test specifically is confirmed to actually exercise both the `ml/` and `backend/` code paths, not accidentally test the same function against itself.
- [ ] Tests do not depend on a specific trained model producing exactly reproducible predictions beyond what's reasonable (e.g. don't hardcode an assertion on an exact confidence float from the real model unless using a mocked/monkey-patched value) — assert on response shape/type/range for the real-model test, and assert on exact values only for the mocked low-confidence test.

**Must Not Break:** Must test the real, fully-assembled `/predict` route from Prompts 89–94, not a simplified stand-in.

---
### 2.F Disease Information & History Module

#### Prompt 96 — `GET /diseases`

**Do:** Implement `GET /diseases` listing all disease records (crop, name, short description) for the About/Methodology page.

**Context & Why:** This is one of the few intentionally public (non-authenticated) routes in the app — it powers Prompt 161's About page, which should be viewable by anyone evaluating the project (including a viva examiner) without needing to create an account first.

**Requirements:**
- `@router.get("/diseases", response_model=List[DiseaseListItemOut])` — define a new lightweight `DiseaseListItemOut(BaseModel)` in `backend/app/schemas/prediction.py` (alongside `DiseaseInfoOut` from Prompt 88) or a new `backend/app/schemas/disease.py` if that's cleaner: `id: int`, `crop: str`, `disease_name: str`, `description: str` — deliberately a **shorter** response than the full `DiseaseInfoOut` used in prediction responses (omit `symptoms`/`prevention`/`management` here, matching the stated purpose "short description" for a list/browse view; full detail is reserved for Prompt 97's single-item endpoint).
- No authentication required — do not include `Depends(get_current_user)`.
- Return all 8 seeded rows (Prompt 67) ordered by `crop`, then `disease_name` alphabetically for a stable, predictable listing order.

**Acceptance Criteria:**
- [ ] Returns `200` with exactly 8 items, no authentication needed.
- [ ] Each item includes only the 4 specified fields, not the full symptoms/prevention/management text.
- [ ] Ordering is stable and alphabetical.

**Must Not Break:** Must be added to Prompt 75's public-route allowlist (the automated test there must be updated to include this new intentionally-public route, or it will incorrectly flag `/diseases` as missing required authentication).

---

#### Prompt 97 — `GET /diseases/{id}`

**Do:** Implement `GET /diseases/{id}` returning full detail for one disease.

**Context & Why:** This is the "click through for more detail" counterpart to Prompt 96's list view, and reuses the same full `DiseaseInfoOut` schema already defined for prediction responses (Prompt 88), keeping disease-detail representation consistent across the two different contexts it appears in.

**Requirements:**
- `@router.get("/diseases/{disease_id}", response_model=DiseaseInfoOut)` (reusing Prompt 88's schema, adding an `id: int` field to it if not already present, or wrapping it — confirm `DiseaseInfoOut` either already includes `id`/`crop`/`disease_name` or extend it to, since the nested use inside `PredictionOut` may not have needed those top-level identifying fields but this standalone endpoint does; resolve this by having `DiseaseInfoOut` always include `id`, `crop`, `disease_name` alongside `description`/`symptoms`/`prevention`/`management`, so both use sites get a consistent full shape).
- No authentication required (same public-route reasoning as Prompt 96).
- If `disease_id` doesn't correspond to any seeded row, return a proper `404` with a clear message, not a `500`.

**Acceptance Criteria:**
- [ ] A valid disease id returns `200` with full detail (all 7 fields).
- [ ] An invalid/non-existent id returns `404`.
- [ ] No authentication required.

**Must Not Break:** If `DiseaseInfoOut` is extended with new fields here, confirm this doesn't break its existing nested usage inside `PredictionOut` (Prompt 88) — extra fields being present shouldn't cause issues, but verify the `/predict` route's response still serializes correctly after this change.

---

#### Prompt 98 — `GET /predictions/history`

**Do:** Implement `GET /predictions/history` returning the authenticated user's own predictions, most recent first, with pagination support.

**Context & Why:** This is the direct backend for the frontend's History page (Prompt 149) and its pagination/filtering controls (Prompts 150–151) — getting pagination parameters and response shape right here avoids rework when the frontend is wired up in Prompt 170.

**Requirements:**
- `@router.get("/predictions/history", response_model=PaginatedPredictionsOut)` — define `PaginatedPredictionsOut(BaseModel)`: `items: List[PredictionOut]`, `total: int`, `page: int`, `page_size: int`, `total_pages: int`.
- Query params: `page: int = 1`, `page_size: int = 20` (with a sensible max, e.g. reject or cap at 100 to prevent abuse), and — anticipating Prompts 150–151's frontend filtering/sorting needs even though this prompt's primary scope is pagination — optional `crop: Optional[str] = None`, `disease: Optional[str] = None` query params for filtering, and `sort_by: str = "created_at"`, `sort_order: str = "desc"` for sorting (validate `sort_by` against an allowlist of actual column names to prevent any injection risk, and `sort_order` against `{"asc","desc"}`).
- Scope the base query strictly to `current_user.id` — this is the exact mechanism verified in Prompt 172's two-account isolation test.
- Compute `total` via a separate `COUNT` query (not by loading all matching rows into memory and counting in Python) before applying `LIMIT`/`OFFSET` for the actual page of results.

**Acceptance Criteria:**
- [ ] Returns correctly paginated, correctly-ordered (most recent first by default) results scoped to the authenticated user only.
- [ ] `crop`/`disease` filters correctly narrow results when provided.
- [ ] Requesting a `page` beyond the available data returns an empty `items` list with correct `total`/`total_pages`, not an error.
- [ ] A second user's predictions never appear in this user's results, regardless of filter/sort parameters used.

**Must Not Break:** Must reuse `PredictionOut` (Prompt 88) for each item in the list.

---

#### Prompt 99 — `POST /predictions/{id}/feedback`

**Do:** Implement `POST /predictions/{id}/feedback` letting a user confirm or correct a past prediction, writing to the `feedback` table.

**Context & Why:** This is the backend for the frontend Result page's "Was this correct?" control (Prompt 148) — it must enforce that users can only give feedback on their own past predictions, a specific ownership check distinct from (and in addition to) the general authentication check.

**Requirements:**
- `@router.post("/predictions/{prediction_id}/feedback", response_model=FeedbackOut, status_code=201)` — define `FeedbackCreate(BaseModel)`: `is_correct: bool`, `actual_disease: Optional[str] = None`, `comment: Optional[str] = None`; define `FeedbackOut(BaseModel)` mirroring the `Feedback` model's fields.
- First, look up the referenced `Prediction` by `prediction_id`; if not found, `404`. **Critically**, if found but `prediction.user_id != current_user.id`, also return `404` (not `403`) — returning `404` rather than `403` for another user's prediction avoids confirming to an attacker that a given prediction id exists at all, a standard defense against resource-enumeration.
- Create a new `Feedback` row with `prediction_id`, `user_id=current_user.id` (from the JWT, never trusted from the body), and the submitted fields.
- If `is_correct=True`, `actual_disease` should be ignored/nulled even if submitted (a "yes this was correct" feedback has no meaningful correction to record) — document this behavior clearly.

**Acceptance Criteria:**
- [ ] Submitting feedback on one's own prediction succeeds and creates a row with the correct `user_id`/`prediction_id`.
- [ ] Submitting feedback on another user's prediction id returns `404`, not `403` or `200`.
- [ ] Submitting feedback on a non-existent prediction id returns the same `404`.
- [ ] `is_correct=True` with an `actual_disease` value provided results in `actual_disease` being stored as `null`, not the submitted value.

**Must Not Break:** Must use `Feedback`/`Prediction` models (Prompts 65/63) and the standard `get_current_user` pattern exactly as already established.

---

#### Prompt 100 — History & Feedback Tests

**Do:** Write `backend/tests/test_history_feedback.py` covering history scoping (user A cannot see user B's predictions) and feedback submission.

**Context & Why:** This is the automated test that formally proves the per-user data isolation guarantee for history and feedback specifically — a close cousin of, but distinct from, Prompt 172's later full end-to-end frontend version of the same concept.

**Requirements:**
- Test `test_history_scoped_to_user`: create two users (A and B) with tokens; insert predictions for both; call `GET /predictions/history` as user A; assert only user A's predictions appear, never user B's, even though both exist in the database.
- Test `test_history_pagination`: insert more predictions than one page size for a single user; verify `page`/`page_size`/`total`/`total_pages` behave correctly across multiple page requests.
- Test `test_feedback_on_own_prediction_succeeds`: user A submits feedback on their own prediction, assert `201` and a correctly-linked `Feedback` row.
- Test `test_feedback_on_others_prediction_returns_404`: user A attempts to submit feedback on user B's prediction id, assert `404`.
- Test `test_feedback_correct_nulls_actual_disease`: submit `is_correct=true` with an `actual_disease` value anyway, assert the stored row has `actual_disease: null`.

**Acceptance Criteria:**
- [ ] All five tests pass.
- [ ] The cross-user isolation tests specifically use two genuinely distinct authenticated users/tokens, not the same user tested twice.

**Must Not Break:** Must test the real routes from Prompts 98–99 as implemented.

---
### 2.G Middleware, Error Handling, Testing & Docs

#### Prompt 101 — Global Exception Handlers

**Do:** Add global exception handlers in `backend/app/main.py` for validation errors and unhandled server errors, returning consistent JSON error shapes.

**Context & Why:** Individual routes (Prompt 94 for `/predict`, for example) handle their own specific expected error cases, but this prompt is the final safety net catching anything unexpected anywhere in the app, guaranteeing the client NEVER sees a raw, unstructured error response regardless of what went wrong or where.

**Requirements:**
- Add `@app.exception_handler(RequestValidationError)` (FastAPI/Pydantic's standard validation error) that reformats the default (fairly verbose, nested) error detail into the project's standard shape: `{"detail": "<human-readable summary>", "error_code": "VALIDATION_ERROR", "fields": [...]}` (where `fields` optionally lists which specific fields failed, for frontend form-error display, per Prompt 158's planned form-validation UI).
- Add `@app.exception_handler(Exception)` as a true catch-all for any unhandled exception, returning `500` with `{"detail": "An unexpected error occurred.", "error_code": "INTERNAL_SERVER_ERROR"}` — never include the raw exception message or traceback in this response — while logging the full exception (including traceback) server-side via Python's `logging` module at `ERROR` level.
- Confirm `HTTPException`s explicitly raised by route code (e.g. the various `401`/`404`/`409` responses from Prompts 72–99) still pass through with their intended status codes and messages, unaffected by this new catch-all (FastAPI's default `HTTPException` handling should already compose correctly with a new generic `Exception` handler, but verify this explicitly with a test).

**Acceptance Criteria:**
- [ ] A deliberately malformed request body to any route returns the standardized validation-error shape, not FastAPI's raw default format.
- [ ] A deliberately triggered unhandled exception (e.g. a temporary test route that raises `ValueError("boom")`) returns a clean `500` with the generic message, and the real `ValueError` and its traceback appear in server logs.
- [ ] Existing explicit `HTTPException` responses from earlier prompts (e.g. `401` from `get_current_user`, `409` from registration) are confirmed unchanged after adding these handlers.

**Must Not Break:** Must not alter the status codes or intended messages of any `HTTPException` already explicitly raised in Prompts 72–99.

---

#### Prompt 102 — Request Logging Middleware

**Do:** Add request-logging middleware to `backend/app/main.py` for debugging and audit purposes.

**Context & Why:** Without this, diagnosing a production issue (or even a local bug during development) means guessing which requests were made and when — basic structured request logging is cheap to add now and valuable for the rest of the project's life, including during Prompt 181's manual mobile QA and Prompt 182's load testing.

**Requirements:**
- Add a FastAPI `@app.middleware("http")` function that logs, for every request: HTTP method, path, response status code, and processing time in milliseconds — using Python's `logging` module (not `print`), at `INFO` level.
- **Explicitly never log request bodies or headers** (this would risk logging plaintext passwords from `/auth/login`/`/auth/register` payloads, or JWT tokens from `Authorization` headers) — log only the metadata listed above, and state this exclusion explicitly in a code comment given its security importance.
- Ensure the middleware correctly measures and logs timing even when a request results in an error (it should wrap/measure regardless of success/failure, using a `try/finally` around calling the next middleware/route handler).

**Acceptance Criteria:**
- [ ] Every request produces exactly one log line with method, path, status, and timing.
- [ ] No request/response body content or header values (especially `Authorization`) ever appear in logs — verified by making a login request with a known password and confirming it does not appear anywhere in the log output.
- [ ] Logging occurs correctly for both successful and error responses.

**Must Not Break:** Must not interfere with the exception handlers from Prompt 101 — logging middleware should wrap around, not replace or swallow, error handling.

---

#### Prompt 103 — Tighten CORS Configuration

**Do:** Configure CORS explicitly to allow only the deployed frontend origin(s).

**Context & Why:** Prompt 60 set up CORS reading from configuration rather than a wildcard, but at this stage of the project the actual deployed frontend origin doesn't exist yet — this prompt is the formal point to make sure that configuration is correctly populated and the wildcard temptation (common during easy local development) never leaks into a committed default.

**Requirements:**
- Confirm `get_settings().cors_allowed_origins` (Prompt 58) is read from an actual `.env` list (e.g. `CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000` parsed into a list) and that `backend/.env.example` (Prompt 59) documents this clearly with realistic local-dev example values.
- Explicitly confirm (via a code comment and/or a startup log line) that no `"*"` wildcard origin is ever used, even in local development — local dev origins should be explicitly listed (`http://localhost:5173` etc.), not wildcarded, so the team never develops a habit that would be dangerous if accidentally carried into production configuration.
- Leave a clear placeholder/TODO in `.env.example` for the production frontend URL, to be filled in during Prompt 196/204's deployment configuration.

**Acceptance Criteria:**
- [ ] CORS middleware configuration never includes `"*"` anywhere in the codebase.
- [ ] A request from a non-allowlisted origin is correctly blocked by CORS (verified via a test using an unexpected `Origin` header).
- [ ] A request from an allowlisted local-dev origin succeeds with correct CORS headers.

**Must Not Break:** Must not break the existing local frontend dev experience — the actual local dev origin(s) the frontend will use (Prompt 111's Vite default) must remain correctly allowlisted.

---

#### Prompt 104 — Upload Size Limits at the App Level

**Do:** Add input-size limits (max upload size) to the FastAPI app configuration.

**Context & Why:** Prompts 82 and 89 already validate file size inside their own route logic, but that check happens only after some amount of data has already been read — this prompt adds a defense-in-depth, server/framework-level limit that rejects oversized request bodies earlier, before they can consume excessive memory or bandwidth, directly relevant to the abuse-prevention goal Prompt 187 will expand on.

**Requirements:**
- Configure the ASGI server (uvicorn) and/or add explicit middleware that rejects request bodies exceeding a safe absolute ceiling (e.g. somewhat above `get_settings().max_upload_size_mb` to allow for multipart overhead, but still a hard ceiling — e.g. if the configured limit is 10MB, set the hard server-level ceiling at something like 12–15MB) before the request body is fully buffered into application code.
- Document clearly in a code comment the relationship between this hard server-level ceiling and the softer, more precisely-messaged application-level checks in Prompts 82/89 — both layers should exist, serving different purposes (defense-in-depth), not be seen as redundant/one replacing the other.
- Confirm the error returned when this server-level limit is hit is still reasonably clear (even if less polished than the application-level validation's custom message) and does not crash the server process.

**Acceptance Criteria:**
- [ ] A request body exceeding the hard server-level ceiling is rejected without crashing the server or consuming unbounded memory.
- [ ] Requests within the configured limit continue to work normally through Prompts 82/89's existing logic.

**Must Not Break:** Must not conflict with or duplicate-reject valid uploads already correctly handled by Prompts 82/89's own size checks — the server-level ceiling should sit comfortably above the application-level limit, not below or equal to it.

---

#### Prompt 105 — Shared Test Fixtures (`conftest.py`)

**Do:** Write `backend/tests/conftest.py` setting up a test database and a reusable authenticated test-client fixture.

**Context & Why:** By this point, `test_auth.py` (76), `test_users.py` (85), `test_predict.py` (95), and `test_history_feedback.py` (100) have each informally set up their own test database/client patterns — this prompt consolidates that into one shared, canonical fixture set, both as cleanup and as the foundation Prompt 106's coverage work builds on.

**Requirements:**
- Define a `db_session` pytest fixture that creates a fresh, isolated test database (e.g. a separate test Postgres database, or SQLite in-memory if the team's SQLAlchemy usage is portable enough — confirm compatibility given `JSON`/`ARRAY` column types used in Prompt 62, which may need adjustment for SQLite; if full Postgres-feature compatibility matters, prefer a real disposable test Postgres database/schema instead), runs migrations (or `Base.metadata.create_all`) fresh for each test function or test session (choose function-scoped for full isolation, documenting the trade-off versus session-scoped speed), and tears it down afterward.
- Define a `client` fixture providing a FastAPI `TestClient` wired to use the `db_session` fixture (overriding the `get_db` dependency via FastAPI's `app.dependency_overrides`) instead of the real configured database.
- Define an `authenticated_client` (or a `test_user` + helper function) fixture that registers a fresh test user via the real `/auth/register` route and returns a `client` pre-configured with that user's `Authorization: Bearer <token>` header attached to every request, so individual tests don't need to repeat this boilerplate.
- Refactor `test_auth.py`, `test_users.py`, `test_predict.py`, `test_history_feedback.py` (Prompts 76, 85, 95, 100) to use these new shared fixtures instead of each file's own ad-hoc setup, removing now-duplicated setup code.

**Acceptance Criteria:**
- [ ] All four existing test files pass unchanged in behavior after being refactored to use the shared fixtures.
- [ ] Running the full test suite twice in a row produces identical results both times (confirms proper isolation/teardown between runs).
- [ ] No test file outside `conftest.py` contains its own database-setup or manual-registration-and-login boilerplate anymore.

**Must Not Break:** Must not change the actual behavior/assertions of any existing test — this is a refactor of test infrastructure, not test logic.

---

#### Prompt 106 — Test Coverage Verification

**Do:** Achieve and verify test coverage across auth, users, predict, history, and feedback modules; document results in `backend/TESTING.md`.

**Context & Why:** This is the formal checkpoint confirming the whole backend's automated test suite (Prompts 76, 85, 95, 100, now unified via Prompt 105) is actually comprehensive, not just present — and it produces the written artifact referenced again in Prompt 183's broader Phase 4 testing report.

**Requirements:**
- Add `pytest-cov` to `backend/requirements.txt`, run `pytest --cov=app --cov-report=term-missing --cov-report=html backend/tests/`.
- Review the coverage report and identify any route or significant branch (e.g. an error-handling path) with no test coverage; add tests to close meaningful gaps (not necessarily chasing 100% — focus on every route and every documented edge case from Prompts 72–100's own Acceptance Criteria sections, which already enumerate the behaviors that matter most).
- Write `backend/TESTING.md` summarizing: overall coverage percentage, a per-module breakdown, any intentionally-uncovered code with a justification (e.g. a defensive `else` branch that's genuinely unreachable in normal operation), and instructions for running the suite and regenerating the coverage report.

**Acceptance Criteria:**
- [ ] `backend/TESTING.md` exists with real, current coverage numbers (not estimated/placeholder).
- [ ] Every route defined in Phase 2 has at least one passing test exercising it.
- [ ] Any gap in coverage is explicitly justified in the document, not silently left unmentioned.

**Must Not Break:** Must not reduce existing test coverage/pass rate while closing gaps — all previously-passing tests from Prompts 76, 85, 95, 100 must remain passing.

---

#### Prompt 107 — Annotate OpenAPI/Swagger Docs

**Do:** Review FastAPI's automatic OpenAPI/Swagger docs at `/docs`; annotate routes with clear summaries and example responses.

**Context & Why:** FastAPI generates `/docs` automatically from route signatures, but without explicit annotations it's often sparse/unclear — this prompt makes `/docs` genuinely usable as living API documentation for the frontend team building against it in Phase 3, and for Prompt 109's HTTP-request reference.

**Requirements:**
- For every route across `auth.py`, `users.py`, `predict.py`, `diseases.py` (as organized per the file structure), add a `summary` and `description` to each `@router.<method>(...)` decorator, and add `responses={...}` documenting at least the success status code and the most important error status codes (e.g. `401`, `404`, `409`, `422` as applicable per route) with example response bodies matching the project's standard error shape.
- Add `response_model_exclude_none=True` where appropriate so optional `null` fields don't clutter example responses unnecessarily (evaluate case by case — some `null`s, like `profile_photo_url`, are meaningful and worth showing).
- Group routes logically using FastAPI's `tags=[...]` parameter (e.g. `tags=["Auth"]`, `tags=["Users"]`, `tags=["Predictions"]`, `tags=["Diseases"]`) so `/docs` renders them in clearly organized sections.

**Acceptance Criteria:**
- [ ] `/docs` (Swagger UI) shows every route with a human-readable summary, grouped into logical tagged sections, with documented example error responses for each route's realistic failure modes.
- [ ] A new developer (or the frontend team) could reasonably integrate against the API using only `/docs`, without needing to read the backend's Python source code.

**Must Not Break:** Purely additive documentation/metadata — must not change any route's actual runtime behavior.

---

#### Prompt 108 — Backend README

**Do:** Write `backend/README.md` documenting setup, environment variables, running locally, running tests, and the full API reference.

**Context & Why:** This is the single document a new teammate (or the deployment process in Prompt 197) should be able to follow start-to-finish to get the backend running locally or in production, without needing to read through all 55 of this phase's individual prompts.

**Requirements:**
- "Setup" section: exact venv creation/activation/install commands (mirroring Prompt 56's requirements), `.env` setup instructions referencing `.env.example` (Prompt 59).
- "Database Setup" section: migration commands (`alembic upgrade head`, Prompt 66) and seeding (`python -m app.db.seed_diseases`, Prompt 67), plus the local reset script (Prompt 68).
- "Running Locally" section: exact `uvicorn app.main:app --reload` command and the resulting local URL/port, plus a pointer to `/docs` (Prompt 107) for interactive API exploration.
- "Running Tests" section: exact `pytest` command, how to generate coverage (Prompt 106), and a note that tests require their own isolated test database configuration (per `conftest.py`, Prompt 105).
- "API Reference" section: either a concise manually-written summary table of every route (method, path, auth required y/n, one-line purpose) linking to `/docs` for full detail, or an explicit note that full reference lives in `/docs` and in `docs/api-requests.http` (Prompt 109) — don't fully duplicate Swagger's detailed content here, keep this README as a high-level map.
- "Rate Limiting & Security Notes" section: briefly reference Prompt 78's login rate-limiting and note that further hardening happens in Phase 4 (Prompts 184–189).

**Acceptance Criteria:**
- [ ] Following this README exactly, from a clean checkout, a new developer can get the backend running locally and passing its test suite.
- [ ] Every environment variable referenced is consistent with `.env.example` (Prompt 59).
- [ ] The API reference section accurately lists every route that exists as of this point in the project.

**Must Not Break:** Must accurately describe the real current state of the backend — update this file again if later prompts (Phase 4 especially) change setup/deployment steps.

---

#### Prompt 109 — HTTP Request Reference File

**Do:** Write a curl/HTTP request reference covering every endpoint, saved to `backend/docs/api-requests.http`.

**Context & Why:** This `.http` file format (compatible with the REST Client extension in VS Code, IntelliJ's built-in HTTP client, and easily convertible to curl/Postman) gives the team copy-pasteable, runnable example requests for manual testing during development and debugging — distinct from, and more immediately actionable than, the descriptive Swagger docs from Prompt 107.

**Requirements:**
- One clearly-commented section per route, in logical order matching the route groups from Prompt 107 (Auth, Users, Predictions, Diseases): `POST /auth/register`, `POST /auth/login`, `GET /users/me`, `PUT /users/me`, `POST /users/me/photo`, `GET /users/me/stats`, `POST /predict`, `GET /predictions/history`, `POST /predictions/{id}/feedback`, `GET /diseases`, `GET /diseases/{id}`.
- Each entry includes realistic example request bodies/headers, and a `@variable`-style mechanism (supported by the `.http` format) for reusing a captured auth token across subsequent requests in the same file, e.g. capturing `{{authToken}}` from the login response and reusing it in the `Authorization` header of later requests.
- A top-of-file comment explaining how to use the file (which tool/extension, how the variable substitution works) and reminding the reader to update the `@baseUrl` variable between local (`http://localhost:8000`) and deployed (Prompt 200's production URL, once it exists) environments.

**Acceptance Criteria:**
- [ ] Every route from Prompt 108's API reference has a corresponding, runnable example request in this file.
- [ ] Manually running the requests in order (register → login, capturing the token → an authenticated request) against a running local backend succeeds.

**Must Not Break:** Must stay in sync with the real route signatures/schemas — update this file if any route's request/response shape changes in later prompts.

---

#### Prompt 110 — Final Backend Code Review Pass

**Do:** Do a final backend code-review pass: consistent naming, remove dead code, confirm every protected route uses `get_current_user`.

**Context & Why:** This is the formal close of Phase 2, mirroring Phase 1's Prompt 55 freeze — it is the last chance to catch naming drift, leftover debugging code, or a missed `get_current_user` dependency before the frontend team (Phase 3) starts building against this API as a stable contract.

**Requirements:**
- Re-run Prompt 75's automated route-allowlist test against the FULL, final route set (now including `predict.py`, `diseases.py` routes added since that test was first written) and confirm it still correctly distinguishes public vs. protected routes with no gaps.
- Grep the codebase for leftover `print()` statements (should all have been replaced by proper `logging` calls per Prompts 101–102's conventions), commented-out dead code blocks, and any TODO comments that were meant to be resolved within this phase (as opposed to ones deliberately deferred to Phase 4, which should be clearly labeled as such, e.g. referencing "Prompt 187" or "Phase 4" explicitly rather than being vague).
- Confirm consistent naming conventions across all files per the Global Conventions (snake_case files/functions, PascalCase classes, consistent `response_model` usage, consistent error shapes).
- Re-run the full test suite (`pytest backend/tests/`) one final time and confirm 100% pass, and re-check `backend/TESTING.md` (Prompt 106) is still accurate.
- Make a final Phase 2 commit, e.g. `"feat: complete backend API (Phase 2) — auth, users, predictions, diseases"`.

**Acceptance Criteria:**
- [ ] Zero stray `print()` debugging statements remain in `backend/app/`.
- [ ] Every route confirmed to have correct public/protected status via the updated allowlist test.
- [ ] Full test suite passes.
- [ ] `backend/README.md` (Prompt 108) and `backend/TESTING.md` (Prompt 106) are both confirmed accurate as of this final state.
- [ ] Phase 2 is formally declared complete — Phase 3 integration work and Phase 4's full-stack integration (Section 4.A) may now begin once Phase 3's own prompts are also complete.

**Must Not Break:** This is a review/cleanup pass — it must not change any route's documented behavior from Prompts 56–109; any "fix" discovered here that would change behavior should be treated as a deliberate, separately-justified change, not silently folded into this cleanup commit.

---
## 5. PHASE 3 — Frontend (React)

*Prompts 111–165*

This phase builds the multi-user interface: authentication screens, the personalized dashboard, the scan flow, and every screen that makes the app feel like each user's own. Section 3.A may be scaffolded in parallel with Phase 2 using mock data, but full data integration (anything calling the real backend) must wait until the relevant Phase 2 routes exist and pass their tests.

### 3.A Project Setup & Design System

#### Prompt 111 — Initialize the Vite + React + TypeScript Project

**Do:** Initialize `frontend/` as a React project (Vite) with TypeScript, and install Tailwind CSS, React Router, and Zustand.

**Context & Why:** Every later frontend prompt assumes this exact toolchain — Vite for fast dev/build, TypeScript strict mode for catching API-contract mismatches at compile time (directly reducing the kind of bugs Prompt 173 exists to fix), Tailwind for utility-first styling matching the design tokens configured next in Prompt 113, Zustand for lightweight global auth state (Prompt 119), React Router for the page structure (Prompt 117).

**Requirements:**
- `npm create vite@latest frontend -- --template react-ts` (or equivalent), then `cd frontend && npm install`.
- `npm install react-router-dom zustand`.
- `npm install -D tailwindcss postcss autoprefixer` and run `npx tailwindcss init -p` to generate `tailwind.config.js`/`postcss.config.js`.
- Enable TypeScript `strict: true` in `tsconfig.json` if not already the Vite template default — confirm explicitly.
- Add Tailwind's `@tailwind base; @tailwind components; @tailwind utilities;` directives to the main CSS entry file, and confirm a trivial Tailwind utility class (e.g. `text-red-500`) actually renders correctly in the default Vite starter page before proceeding further.

**Acceptance Criteria:**
- [ ] `npm run dev` starts a working Vite dev server.
- [ ] TypeScript strict mode is confirmed enabled (check `tsconfig.json`).
- [ ] A Tailwind utility class visibly applies styling in the browser.
- [ ] `react-router-dom` and `zustand` are listed in `package.json` dependencies.

**Must Not Break:** N/A — new subproject, must live inside `frontend/` per the root structure from Prompt 1.

---

#### Prompt 112 — Frontend Folder Structure

**Do:** Create the folder structure: `frontend/src/{components/, pages/, services/, store/, hooks/, assets/}`.

**Context & Why:** Mirrors the clear separation-of-concerns pattern already established for the backend in Prompt 57 — `components/` for reusable UI pieces, `pages/` for route-level screens, `services/` for API-calling logic, `store/` for Zustand global state, `hooks/` for custom React hooks, `assets/` for images/icons.

**Requirements:**
- Create every folder listed, each as an empty directory (no index files needed yet beyond what Vite's template already provides at `src/`).
- Within `components/`, anticipate the `ui/` subfolder needed starting Prompt 114 (can create it now or let Prompt 114 create it — either is fine, but don't create unrelated subfolders not called for by name in later prompts).
- Remove/clean up any unused Vite starter template boilerplate (the default counter example component, placeholder CSS, default logo assets) that won't be used in this project, to avoid confusing dead code accumulating from the start.

**Acceptance Criteria:**
- [ ] All six folders exist under `frontend/src/`.
- [ ] No leftover unused Vite starter template files remain (verify `src/` contains only intentionally-created project structure).

**Must Not Break:** Must sit inside `frontend/src/` from Prompt 111's scaffold.

---

#### Prompt 113 — Tailwind Design Tokens

**Do:** Configure Tailwind with the project's design tokens: primary green palette, neutral greys, spacing scale, and typography.

**Context & Why:** This is the single source of truth for the app's visual identity — matching the agriculture-appropriate green palette already established in the project's report/presentation materials — and every later UI component (Prompts 114–165) should pull colors/spacing from these named tokens rather than using arbitrary one-off Tailwind values, keeping the whole app visually consistent.

**Requirements:**
- In `tailwind.config.js`'s `theme.extend.colors`, define a `primary` color scale (e.g. `primary: { 50: '#...', ..., 900: '#...' }`) built around a forest/leaf green matching the tones already used in the project report document (e.g. the `#1B4332`/`#2D6A4F`/`#95D5B2` family already established there — reuse these exact hex values as anchor points in the scale for visual consistency across the whole project's deliverables, not just the app itself).
- Define a `neutral`/`grey` scale for text/background/border use, and confirm a comfortable contrast ratio between `primary` tones and white/light backgrounds for accessibility.
- Extend `theme.extend.fontFamily` with a clean, readable sans-serif stack (document the choice, e.g. Inter or the system font stack) and confirm it's actually loaded/applied (via a Google Fonts `<link>` in `index.html` if using a non-system font, or confirmed default otherwise).
- Document the full token palette (hex values and their semantic names) in a short `frontend/src/DESIGN_TOKENS.md` so every teammate uses the same names consistently rather than reinventing shades ad hoc in later components.

**Acceptance Criteria:**
- [ ] `bg-primary-600` (or equivalent token name) renders the correct intended green in the browser.
- [ ] `DESIGN_TOKENS.md` exists and lists every custom color/spacing/typography token with its purpose.
- [ ] Color choices are confirmed consistent with the hex values already used in the project's existing report document diagrams.

**Must Not Break:** Must extend, not replace, Tailwind's default scales where sensible (e.g. keep default spacing scale unless there's a specific reason to override it).

---

#### Prompt 114 — Base `Button` Component

**Do:** Build a base `frontend/src/components/ui/Button.tsx` component with primary/secondary/ghost variants.

**Context & Why:** Every clickable action across the whole app (login/signup submit, "+ New Scan", "Scan Another", feedback buttons, etc.) should render through this one component so visual consistency and future-wide style changes (e.g. adjusting hover states) only need to happen in one place.

**Requirements:**
- `interface ButtonProps { variant?: "primary" | "secondary" | "ghost"; size?: "sm" | "md" | "lg"; disabled?: boolean; loading?: boolean; onClick?: () => void; children: React.ReactNode; type?: "button" | "submit"; }` — a functional component using these props.
- `primary`: solid `primary` token background, white text, used for the single main call-to-action on any given screen.
- `secondary`: outlined or lighter-background variant, used for secondary actions.
- `ghost`: text-only, minimal styling, used for tertiary/low-emphasis actions (e.g. "Cancel").
- Support a `loading` state that shows Prompt 116's `Spinner` component inside the button and disables interaction while `loading` is `true`, without changing the button's size/layout (prevent layout shift).
- Ensure disabled state is visually distinct (reduced opacity, `cursor-not-allowed`) and actually prevents the `onClick` handler from firing.

**Acceptance Criteria:**
- [ ] All three variants render visually distinctly and consistently with the design tokens from Prompt 113.
- [ ] `loading` state shows a spinner and blocks further clicks without the button resizing.
- [ ] `disabled` state visually and functionally prevents interaction.

**Must Not Break:** Depends on the Tailwind tokens from Prompt 113 and (once it exists) the `Spinner` from Prompt 116 — if built before `Spinner` exists, use a simple inline loading indicator temporarily and swap it in once Prompt 116 lands, noting this explicitly in a comment/TODO.

---

#### Prompt 115 — `Card`, `Input`, `Avatar` Components

**Do:** Build base `Card.tsx`, `Input.tsx`, and `Avatar.tsx` (with initials-fallback) components in `frontend/src/components/ui/`.

**Context & Why:** `Card` is the container pattern used for the dashboard stats (Prompt 129), recent scans table wrapper (Prompt 130), and the Result page's content sections (Prompt 143) — `Input` standardizes every form field across Signup/Login/Profile — `Avatar` is the exact component implementing the initials-fallback behavior anticipated by the backend's `profile_photo_url: null` contract (Prompt 83).

**Requirements:**
- `Card.tsx`: a simple wrapper component (rounded corners, subtle shadow/border, consistent padding using the design tokens) accepting `children` and an optional `className` for extension.
- `Input.tsx`: `interface InputProps { label: string; type?: string; value: string; onChange: (value: string) => void; error?: string; placeholder?: string; required?: boolean; }` — renders a labeled input with consistent styling, and conditionally renders an error message below the field in a distinct (e.g. red) color when `error` is provided, directly supporting Prompt 122's validation display needs.
- `Avatar.tsx`: `interface AvatarProps { photoUrl?: string | null; name: string; size?: "sm" | "md" | "lg"; }` — if `photoUrl` is a non-null, non-empty string, render an `<img>`; otherwise, compute initials from `name` (e.g. first letter of first and last word, uppercased, matching the same logic conceptually described in Prompt 83's optional backend helper) and render them centered inside a colored circle (using a `primary` token background).
- All three components should be genuinely reusable with no page-specific logic baked in.

**Acceptance Criteria:**
- [ ] `Card` renders consistent styling wrapping arbitrary children.
- [ ] `Input` correctly displays and clears error messages as its `error` prop changes.
- [ ] `Avatar` correctly falls back to initials when `photoUrl` is `null`/`undefined`/empty, and correctly renders an image when a valid URL is provided.

**Must Not Break:** Must use Tailwind tokens from Prompt 113; `Avatar`'s initials logic must handle names with only one word gracefully (e.g. use just the first letter, don't crash on `name.split(" ")[1]` being undefined).

---

#### Prompt 116 — `Spinner` Loading Component

**Do:** Build a `Spinner.tsx` loading-state component for the "Analyzing..." screen.

**Context & Why:** Used both inside `Button`'s loading state (Prompt 114) and standalone on the full-page `Analyzing.tsx` screen (Prompt 139) during prediction requests — a single consistent spinner design reinforces that "the app is working on something" looks the same everywhere.

**Requirements:**
- `interface SpinnerProps { size?: "sm" | "md" | "lg"; className?: string; }` — a simple animated (CSS `animate-spin`, Tailwind's built-in utility) circular loading indicator, colored with the `primary` token.
- No external animation library needed — pure CSS/Tailwind is sufficient and keeps bundle size down (relevant to Prompt 192's later bundle-optimization pass).
- Ensure the spinner has an accessible label (e.g. `aria-label="Loading"` or visually-hidden text) for screen-reader users.

**Acceptance Criteria:**
- [ ] Spinner visibly animates/rotates continuously.
- [ ] Renders correctly at all three defined sizes.
- [ ] Has an accessible label.

**Must Not Break:** Must integrate cleanly as a drop-in replacement for Prompt 114's temporary inline loading indicator, if one was used as a placeholder.

---

#### Prompt 117 — React Router Setup

**Do:** Set up React Router in `frontend/src/App.tsx` with routes for `/login`, `/signup`, `/dashboard`, `/scan`, `/history`, `/profile`, `/about`.

**Context & Why:** This establishes the app's entire navigable structure up front — every page component built in later prompts (120+) plugs into one of these exact route paths, and Prompt 124's `ProtectedRoute` wrapper will apply to most of them.

**Requirements:**
- Use `createBrowserRouter`/`RouterProvider` (React Router v6+'s recommended data-router API) or `<BrowserRouter><Routes>...` (the simpler, equally valid classic API) — pick one approach and use it consistently throughout the project.
- Define routes: `/login` → `Login` (placeholder component for now if not yet built), `/signup` → `Signup`, `/dashboard` → `Dashboard`, `/scan` → `NewScan`, `/history` → `History`, `/profile` → `Profile`, `/about` → `About`, plus a root `/` route that redirects to `/dashboard` if authenticated or `/login` if not (this redirect logic can be stubbed now and properly wired once Prompt 119's auth store exists), and a catch-all `*` route rendering a simple "Page Not Found" message.
- Leave all page components as minimal placeholder stubs at this point if their full implementation prompt hasn't run yet (e.g. a page that just renders its own name) — this prompt's scope is routing structure only, not page content.

**Acceptance Criteria:**
- [ ] Navigating directly to each of the seven listed URLs renders the corresponding (possibly placeholder) page without a routing error.
- [ ] The catch-all route correctly handles an undefined path.
- [ ] The root `/` route redirects somewhere sensible.

**Must Not Break:** N/A — new routing setup, but must be structured so Prompt 124's `ProtectedRoute` can later wrap the appropriate subset of these routes without a significant restructure.

---

#### Prompt 118 — API Service Wrapper

**Do:** Create `frontend/src/services/api.ts` with a configured fetch wrapper that attaches the JWT Authorization header automatically.

**Context & Why:** This is the single chokepoint every API call in the entire frontend (auth, profile, predict, history, feedback, diseases) will go through — centralizing JWT attachment, base URL configuration, and error handling here prevents each individual page/component from re-implementing (and potentially inconsistently re-implementing) this logic.

**Requirements:**
- Read the backend base URL from an environment variable (`import.meta.env.VITE_API_BASE_URL`), with a sensible local-dev default (e.g. `http://localhost:8000`) — anticipating Prompt 175's environment-based configuration requirement, set this up correctly from the start rather than hardcoding the URL now and refactoring later.
- Export a generic `async function apiRequest<T>(path: string, options?: RequestInit): Promise<T>` that: reads the current JWT from the auth store (Prompt 119 — if that doesn't exist yet when this prompt runs, read directly from `localStorage` under a clearly-named key like `auth_token`, and update this function once Prompt 119's store exists to read from there consistently instead), attaches `Authorization: Bearer <token>` header automatically when a token is present (and omits it cleanly when not, for the two intentionally-public auth routes), sets `Content-Type: application/json` by default (letting multipart requests like photo/predict uploads override this appropriately — do not force JSON content-type on `FormData` bodies, which need their own browser-set multipart boundary header), parses the JSON response body, and throws a typed error (including the backend's `detail`/`error_code` fields from its standard error shape, per Phase 2's Global Conventions) on any non-2xx response, so calling code can catch and handle a single consistent error type everywhere.
- Export convenience wrappers if useful (e.g. `apiGet`, `apiPost`, `apiPostFormData`) built on top of the core `apiRequest` function, rather than duplicating fetch logic per call site.

**Acceptance Criteria:**
- [ ] A request made through this wrapper to a protected backend route automatically includes a valid `Authorization` header when a token is present in storage/state.
- [ ] A request to `/auth/login` (no token yet available) succeeds without an `Authorization` header causing an error.
- [ ] A non-2xx backend response is caught and surfaced as a typed error object with the backend's `detail` message accessible to calling code.
- [ ] `FormData` uploads (anticipating Prompts 138/156) are not forced into `Content-Type: application/json`.

**Must Not Break:** Must point at the real backend base URL/port the FastAPI app runs on (Prompt 60); must be updated to read from Prompt 119's auth store once that exists, rather than leaving a stale direct-`localStorage` implementation in place.

---
### 3.B Auth State & Pages

#### Prompt 119 — Zustand Auth Store

**Do:** Create `frontend/src/store/authStore.ts` (Zustand) holding the current user, JWT token, and login/logout actions, persisted to localStorage.

**Context & Why:** This is the single source of truth for "who is logged in" across the entire app — `ProtectedRoute` (Prompt 124), the navbar (Prompt 160), the dashboard greeting (Prompt 127), and `api.ts`'s token attachment (Prompt 118, to be updated to use this store) all read from this one store rather than each maintaining their own separate notion of auth state.

**Requirements:**
- Define the store shape: `{ user: UserProfile | null; token: string | null; isAuthenticated: boolean; login: (user: UserProfile, token: string) => void; logout: () => void; setUser: (user: UserProfile) => void; }` where `UserProfile` is a TypeScript interface matching the backend's `UserProfileOut` schema (Prompt 79) field-for-field — define this interface in a shared `frontend/src/types/` location (create this folder now if it doesn't exist) so it can be reused across pages/components without duplication.
- Use Zustand's `persist` middleware to automatically sync `user` and `token` to `localStorage` under a clearly-named key (e.g. `"crop-disease-auth"`), so a page refresh (Prompt 167's test target) retains the logged-in state.
- `login(user, token)` sets all three state fields (`user`, `token`, `isAuthenticated: true`) in one action, called by both Signup (Prompt 120) and Login (Prompt 121) on success.
- `logout()` clears all three fields back to their logged-out defaults (`null`, `null`, `false`) and should also clear the persisted `localStorage` entry (the `persist` middleware handles this automatically on state change, but verify explicitly).
- `setUser(user)` updates just the `user` object without touching the token — needed by Prompt 171 to reflect profile edits immediately in the navbar without a full re-login.

**Acceptance Criteria:**
- [ ] After calling `login()`, `isAuthenticated` is `true` and the data persists correctly across a simulated page reload (verified by re-reading `localStorage` directly or reloading the test page).
- [ ] After calling `logout()`, all auth state is cleared and `localStorage` no longer contains stale user/token data.
- [ ] `setUser()` updates only the `user` field, leaving `token`/`isAuthenticated` unchanged.

**Must Not Break:** `UserProfile` type must exactly match the backend's actual `UserProfileOut` schema (Prompt 79) — any backend field addition/rename must be mirrored here.

---

#### Prompt 120 — Signup Page

**Do:** Build `frontend/src/pages/Signup.tsx` with a form for name, email, password, optional phone/location, calling `POST /auth/register`.

**Context & Why:** This is the real implementation replacing Prompt 117's placeholder `/signup` route, and the first page in the app that actually talks to the backend.

**Requirements:**
- Controlled form fields using `useState` (or `react-hook-form` if the team prefers introducing it — either is acceptable, but be consistent across Signup/Login/Profile forms, not a mix) for `name`, `email`, `password`, `phone` (optional), `location` (optional), each rendered via Prompt 115's `Input` component.
- On submit, call the API service (Prompt 118) with a `POST` to `/auth/register` matching the backend's `UserCreate` schema (Prompt 71) field-for-field exactly (correct field names: `name`, `email`, `password`, `phone`, `location`).
- This prompt covers the form and the API call itself — full validation display (Prompt 122), error display (Prompt 123), and the post-success redirect (Prompt 125) are separate subsequent prompts; at minimum, this prompt should result in a successful signup actually creating a user in the backend when tested manually.
- Include a link to `/login` for existing users ("Already have an account? Log in").

**Acceptance Criteria:**
- [ ] Submitting the form with valid data results in a real new user being created in the backend database (verified by checking the database or via a subsequent successful login with the same credentials).
- [ ] Form field names/types sent to the backend exactly match `UserCreate`'s schema (Prompt 71).

**Must Not Break:** Must call the real `POST /auth/register` route (Prompt 72) via `api.ts` (Prompt 118), not a mocked response, once Phase 2 is complete (if built in parallel before Phase 2 finishes, per the library's stated parallel-work option, use a clearly-marked temporary mock and replace it once the real backend is ready).

---

#### Prompt 121 — Login Page

**Do:** Build `frontend/src/pages/Login.tsx` with a form for email/password, calling `POST /auth/login`.

**Context & Why:** The returning-user counterpart to Prompt 120, replacing the `/login` placeholder route.

**Requirements:**
- Controlled form fields for `email`, `password` using Prompt 115's `Input` component, following the same state-management pattern chosen in Prompt 120 for consistency.
- On submit, call `POST /auth/login` via `api.ts` matching the backend's `UserLogin` schema (Prompt 71) exactly.
- Include a link to `/signup` for new users ("Don't have an account? Sign up").

**Acceptance Criteria:**
- [ ] Submitting valid credentials for an existing user succeeds against the real backend.
- [ ] Field names sent match `UserLogin`'s schema exactly.

**Must Not Break:** Must call the real `POST /auth/login` route (Prompt 73) via `api.ts`.

---

#### Prompt 122 — Client-Side Form Validation

**Do:** Add client-side form validation (required fields, email format, password length) to both auth forms.

**Context & Why:** Catching obviously-invalid input before it even reaches the backend gives users immediate feedback and reduces unnecessary round-trips — this should mirror, not replace, the backend's own validation (Prompts 71/77), since the backend remains the authoritative source of truth and must never be bypassed by trusting client-side validation alone.

**Requirements:**
- On both `Signup.tsx` and `Login.tsx`, add validation logic (either manual per-field checks on submit, or via a lightweight schema library like `zod` if the team wants to introduce one — if introduced, use it consistently for all forms going forward, including Profile's edit form in Prompt 158) checking: required fields are non-empty, email fields match a reasonable email-format pattern, password fields meet the same minimum-length (and ideally the same character-class rules established in Prompt 77) requirements as the backend.
- Prevent form submission (don't call the API at all) if client-side validation fails, and surface the specific validation error(s) via Prompt 115's `Input` component's `error` prop, matching each error to its specific field (not a single generic banner for the whole form) wherever that level of fidelity is reasonable.
- Mirror the backend's password rules from Prompt 77 as closely as practical in the client-side check, but always treat the backend's response (Prompt 123) as authoritative if a mismatch ever occurs — document this explicitly in a comment so a future maintainer doesn't assume client-side validation alone is sufficient.

**Acceptance Criteria:**
- [ ] Submitting either form with an empty required field, a malformed email, or a too-short password shows a clear, field-specific error and does NOT trigger an API call.
- [ ] Valid input passes client-side validation and proceeds to the API call.

**Must Not Break:** Must not prevent legitimately valid input from being submitted — test with several realistic valid examples to confirm no over-aggressive validation rule accidentally blocks good input.

---

#### Prompt 123 — Server Error Display

**Do:** Add error-message display for failed login/signup attempts (wrong password, duplicate email).

**Context & Why:** Client-side validation (Prompt 122) can't catch everything — a duplicate email or wrong password is only knowable by asking the backend — this prompt ensures those real, server-returned errors reach the user clearly, using the exact messages the backend already provides (Prompts 72–73).

**Requirements:**
- Catch the typed error thrown by `api.ts` (Prompt 118) around the `POST /auth/register`/`POST /auth/login` calls, and display its `detail` message in a clearly-visible, appropriately-styled (e.g. red-bordered banner or inline text near the submit button) error area on the respective form.
- Distinguish, where the backend's `error_code` allows it, between different error types if useful for UX (e.g. a 409 `EMAIL_ALREADY_EXISTS` on signup could additionally suggest "Already have an account? Log in" with a direct link) — but never invent a more specific message than the backend actually provided; if `error_code` doesn't map to a specifically-handled case, fall back to simply displaying the backend's raw `detail` string.
- Clear any previously-shown error message when the user starts editing the form again (don't leave a stale error visible after they've already changed the offending field).

**Acceptance Criteria:**
- [ ] Attempting to sign up with an already-registered email shows the backend's actual error message, not a generic "something went wrong."
- [ ] Attempting to log in with a wrong password shows the backend's actual generic message (per Prompt 73's deliberate email/password ambiguity — the frontend must not add extra text that re-introduces the account-enumeration leak the backend deliberately avoided).
- [ ] The error message clears when the user edits the form again.

**Must Not Break:** Must not contradict or weaken the backend's deliberate security choice (Prompt 73) to give an identical message for "wrong password" and "email not found" — the frontend must not add any hint distinguishing the two.

---

#### Prompt 124 — `ProtectedRoute` Wrapper

**Do:** Create a `ProtectedRoute.tsx` wrapper component that redirects unauthenticated users to `/login`.

**Context & Why:** This is the frontend's enforcement layer ensuring `/dashboard`, `/scan`, `/history`, `/profile` are never rendered for an unauthenticated visitor — the direct frontend counterpart to the backend's `get_current_user` dependency (Prompt 74), and the exact component Prompt 178's end-to-end test targets.

**Requirements:**
- `ProtectedRoute.tsx`: a component (or a React Router "layout route" pattern) that reads `isAuthenticated` from the auth store (Prompt 119) and either renders its `children`/`<Outlet />` if `true`, or `<Navigate to="/login" replace />` if `false`.
- Update `App.tsx`'s route definitions (Prompt 117) to wrap `/dashboard`, `/scan`, `/history`, `/profile` (and any other routes that should require login — `/about` likely remains public, matching the backend's public `/diseases` routes) with this `ProtectedRoute`.
- Consider (and document the decision either way) whether to preserve the originally-requested URL so the user lands back on it after logging in, rather than always dropping them at a fixed default page post-login — a reasonable, if optional, UX enhancement.

**Acceptance Criteria:**
- [ ] Navigating directly to `/dashboard` (or any other protected route) while logged out redirects to `/login`.
- [ ] Navigating to the same routes while logged in renders the actual page content.
- [ ] `/about` (and `/login`/`/signup` themselves) remain accessible without authentication.

**Must Not Break:** Depends on `authStore` (Prompt 119)'s `isAuthenticated` field and must correctly wrap the route structure from Prompt 117 without breaking any currently-public route's accessibility.

---

#### Prompt 125 — Wire Successful Auth to Redirect

**Do:** Wire successful login/signup to store the JWT and redirect to `/dashboard`.

**Context & Why:** Completes the Signup (120) and Login (121) flows by connecting a successful API response to both the auth store (119) and navigation — without this, a successful signup/login would leave the user sitting on the same form with no visible indication anything happened.

**Requirements:**
- On a successful `POST /auth/register` or `POST /auth/login` response (which returns a `Token`, per Prompt 71's schema — note it does NOT include the full user profile object, only `access_token`/`token_type`), immediately make a follow-up `GET /users/me` call (Prompt 80) using the newly-received token to fetch the full user profile, then call `authStore.login(user, token)` (Prompt 119) with both pieces of data together.
- After the store update completes, use React Router's `useNavigate()` to programmatically redirect to `/dashboard`.
- Handle the edge case where the follow-up `GET /users/me` call itself fails (rare, but possible e.g. on a flaky network) — in that case, do not leave the user in a broken partially-authenticated state; either retry once or surface a clear error and avoid calling `login()` with incomplete data.

**Acceptance Criteria:**
- [ ] A successful signup or login results in the browser URL changing to `/dashboard` and the dashboard rendering with the correct real user's data (confirms both the store update and the navigation worked correctly together).
- [ ] The auth store, inspected after this flow, contains both a valid token and a fully-populated user profile object, not just the token alone.

**Must Not Break:** Must use `authStore.login()` (Prompt 119) exactly as defined; must correctly sequence the token-then-profile-fetch, not attempt to populate `user` before the token is available to authorize that follow-up request.

---

#### Prompt 126 — Logout Functionality

**Do:** Implement logout functionality (clear token, redirect to `/login`) accessible from the navbar dropdown.

**Context & Why:** The mirror-image of Prompt 125 — this is the clean exit path, and it's referenced again by Prompt 160's navbar build (which this prompt's logic will be wired into once that navbar exists).

**Requirements:**
- A `handleLogout` function (can live as a small exported hook or plain function, called from wherever the navbar's logout control ends up, per Prompt 160) that calls `authStore.logout()` (Prompt 119) and then navigates to `/login` via `useNavigate()`.
- If the navbar (Prompt 160) doesn't exist yet when this prompt is executed, implement this logic now as a reusable function/hook and add a simple temporary logout button somewhere reachable (e.g. on the Dashboard page) so the functionality can be tested immediately — then wire it into the real navbar control once Prompt 160 builds it, removing the temporary button at that point.
- Ensure logging out correctly prevents any further authenticated API calls from appearing to work with stale cached data — confirm the auth store's `token`/`user` are genuinely cleared, not just the UI's navigation changing while stale state lingers in memory.

**Acceptance Criteria:**
- [ ] Triggering logout clears all auth state (verified via the store and `localStorage`) and redirects to `/login`.
- [ ] After logout, attempting to navigate directly to `/dashboard` correctly redirects back to `/login` (confirms `ProtectedRoute`, Prompt 124, correctly reflects the cleared state).

**Must Not Break:** Must use `authStore.logout()` (Prompt 119) exactly as defined.

---
### 3.C Personalized Dashboard

#### Prompt 127 — Dashboard Greeting Header

**Do:** Build `frontend/src/pages/Dashboard.tsx` with a greeting header ("Welcome back, {user.name}!") using the authenticated user's data.

**Context & Why:** This replaces Prompt 117's placeholder `/dashboard` route with the app's real post-login landing page, and is the first visible proof that per-user personalization (the whole point of the "Personalized Dashboard" phase name) is actually working.

**Requirements:**
- Read the current user from `authStore` (Prompt 119) — do not re-fetch `/users/me` again here if the store already holds a fresh profile from Prompt 125's login flow (avoid redundant API calls); only re-fetch if the store's data could plausibly be stale (e.g. consider a `useEffect` that refetches on mount only if explicitly needed for freshness — document the decision).
- Render `Welcome back, {user.name}!` as a prominent heading.
- Render Prompt 115's `Avatar` component alongside the greeting (full implementation of the avatar's photo-vs-initials logic is covered by Prompt 128, but this prompt should at minimum place the component in the header with the correct props wired).
- This prompt's scope is the header only — stats cards (129), recent scans (130), and the "+ New Scan" button (131) are separate subsequent prompts building out the rest of this same page.

**Acceptance Criteria:**
- [ ] The dashboard header displays the actual logged-in user's real name, not a placeholder.
- [ ] Logging in as two different test users and viewing the dashboard shows two different, correct greetings (an early, simple confirmation of the personalization/isolation principle verified more thoroughly in Prompt 172).

**Must Not Break:** Depends on `authStore` (Prompt 119) correctly holding a populated `user` object by the time this page renders (guaranteed by Prompt 125's flow, and by `ProtectedRoute`, Prompt 124, ensuring only authenticated users reach this page at all).

---

#### Prompt 128 — Dashboard Avatar with Fallback

**Do:** Fetch and display the user's avatar/photo in the dashboard header, falling back to initials if no photo is set.

**Context & Why:** Completes the avatar piece of Prompt 127's header, exercising the full `Avatar` component (Prompt 115) behavior against real backend data for the first time.

**Requirements:**
- Pass `user.profile_photo_url` and `user.name` from the auth store directly into the `Avatar` component's props (Prompt 115) — no additional logic needed here beyond correct prop-wiring, since `Avatar` itself already encapsulates the fallback behavior.
- Confirm this correctly handles the real backend contract from Prompt 83 (`profile_photo_url` is `null`, never an empty string, when no photo exists) — if the real backend ever returns an empty string instead of `null` for any reason, treat that as a backend bug to flag/fix (per Prompt 83's explicit contract) rather than silently patching around it with extra frontend logic.

**Acceptance Criteria:**
- [ ] A user with no uploaded photo shows correctly-computed initials in the dashboard header.
- [ ] A user who has uploaded a photo (once Prompt 156's upload flow exists and has been used) shows their actual photo instead.

**Must Not Break:** Must use the `Avatar` component (Prompt 115) as-is, not a dashboard-specific reimplementation of avatar logic.

---

#### Prompt 129 — Stats Cards

**Do:** Build `frontend/src/components/StatsCard.tsx` and wire three cards (Total Scans, Diseases Detected, Healthy Confirmed) to `GET /users/me/stats`.

**Context & Why:** This is the direct frontend consumer of the backend's `GET /users/me/stats` route (Prompt 84) — three at-a-glance numbers giving the user an immediate sense of their usage history every time they land on the dashboard.

**Requirements:**
- `StatsCard.tsx`: `interface StatsCardProps { label: string; value: number; icon?: React.ReactNode; }` built on top of Prompt 115's `Card` component, displaying a large prominent number and a smaller label beneath/above it.
- In `Dashboard.tsx`, on mount, call `GET /users/me/stats` via `api.ts` (Prompt 118), and render three `StatsCard` instances for `total_scans`, `diseases_detected`, `healthy_confirmed` once the data loads.
- Handle the loading state while the stats request is in flight (a simple placeholder/skeleton is acceptable here; Prompt 132 formalizes loading/empty states more thoroughly across the whole dashboard).

**Acceptance Criteria:**
- [ ] The three stats cards display real numbers matching the authenticated user's actual prediction history in the backend database.
- [ ] A brand-new user (zero predictions) correctly shows all three cards at `0`, not an error or blank state.

**Must Not Break:** Must call the real `GET /users/me/stats` route (Prompt 84) with field names matching its response schema exactly (`total_scans`, `diseases_detected`, `healthy_confirmed`).

---

#### Prompt 130 — Recent Scans Table

**Do:** Build `frontend/src/components/RecentScansTable.tsx` showing the 5 most recent predictions, fetched from `GET /predictions/history`.

**Context & Why:** Gives users immediate visibility into their most recent activity without navigating to the full History page (Prompt 149) — this is a deliberately small, dashboard-scoped slice of the same underlying data `History.tsx` will later show in full with pagination/filtering.

**Requirements:**
- Call `GET /predictions/history?page=1&page_size=5&sort_by=created_at&sort_order=desc` (matching Prompt 98's exact query parameter contract) on dashboard mount.
- Render as a table (or a card-based list on narrower viewports, per Prompt 134's responsive requirement) with columns/fields: thumbnail (if `image_url` is present), crop, disease, confidence (formatted as a percentage — recall Prompt 88's note that the backend sends a `0.0–1.0` fraction, so the frontend is responsible for the `× 100` conversion and `%` formatting here), and date (formatted human-readably, e.g. "2 hours ago" or a localized date string — pick one approach and use it consistently wherever dates are shown elsewhere in the app, like Prompt 149's full history).
- Visually distinguish low-confidence (`is_confident: false`) rows with a subtle warning indicator (a small badge/icon), consistent with how Prompt 146 will more fully treat uncertain results on the Result page itself.

**Acceptance Criteria:**
- [ ] Table correctly displays up to 5 most recent real predictions for the authenticated user, correctly sorted newest-first.
- [ ] Confidence values are correctly converted from the backend's `0.0–1.0` fraction to a human-readable percentage.
- [ ] Rows with `is_confident: false` are visually distinguishable from confident ones.

**Must Not Break:** Must use the exact query parameters and response shape from Prompt 98's `GET /predictions/history`.

---

#### Prompt 131 — "+ New Scan" Call-to-Action

**Do:** Add a prominent "+ New Scan" call-to-action button linking to `/scan`.

**Context & Why:** This is the single most important action on the entire dashboard — the app's core value (diagnose a crop) starts here, so it should be visually unmissable, not buried among secondary navigation.

**Requirements:**
- Use Prompt 114's `Button` component with `variant="primary"`, prominently placed near the top of the dashboard (e.g. directly beside or below the greeting header from Prompt 127), using React Router's `Link`/`useNavigate` to route to `/scan` on click.
- Ensure it remains visible/accessible without excessive scrolling on both desktop and the mobile breakpoint anticipated in Prompt 134.

**Acceptance Criteria:**
- [ ] Clicking the button navigates to `/scan`.
- [ ] The button is visually the most prominent single element on the dashboard, consistent with its role as the primary call-to-action.

**Must Not Break:** Must use `Button` (Prompt 114) and route to the real `/scan` path already defined in Prompt 117.

---

#### Prompt 132 — Loading and Empty States

**Do:** Add loading and empty states to the dashboard (e.g. "No scans yet — start your first scan").

**Context & Why:** Prompts 129–130 already fetch real data on mount, but without explicit handling, a slow network or a genuinely empty history (a brand-new user) would show a blank or broken-looking page — this prompt makes both situations feel intentional and polished rather than like a bug.

**Requirements:**
- While `GET /users/me/stats` and `GET /predictions/history` requests are in flight, show a loading skeleton or spinner (Prompt 116's `Spinner`) in place of the stats cards and recent-scans table respectively, rather than an empty/blank area.
- If the recent-scans table's response has zero items (`items.length === 0`), replace the table with a friendly empty-state message ("No scans yet — start your first scan") that itself includes or sits near a call-to-action pointing at `/scan` (reusing or complementing Prompt 131's button).
- Handle the stats cards' own zero-state gracefully too (already covered functionally by Prompt 129's requirement that zero values render correctly, not as an error — this prompt's job is to make sure the *loading* transition into that zero-state is also smooth, not jarring).

**Acceptance Criteria:**
- [ ] A deliberately slow/throttled network connection shows a clear loading indicator for both the stats and recent-scans sections, not a blank page.
- [ ] A brand-new test user with zero predictions sees the friendly empty-state message instead of an empty table.

**Must Not Break:** Must not interfere with the correct rendering of real data once it loads (Prompts 129–130) — loading/empty states must cleanly transition away once data arrives.

---

#### Prompt 133 — Click-Through From Recent Scan to Detail

**Do:** Add click-through from a recent-scan row to a detailed result view.

**Context & Why:** Lets a user revisit a past diagnosis directly from the dashboard without navigating through the full History page first — a small but meaningful convenience, and the first place the app needs a route/pattern for viewing one specific past prediction's full detail (a need Prompt 152 addresses more fully from the History page's side).

**Requirements:**
- Make each row in `RecentScansTable` (Prompt 130) clickable, navigating to a detail view for that specific prediction — decide now (and apply consistently again in Prompt 152) whether this is a dedicated route (e.g. `/history/:id`) or a modal overlay; a dedicated route is generally simpler to reason about and share-link, so prefer that unless there's a strong reason for a modal — document the choice.
- The detail view itself can reuse much of the Result page's (Prompt 143) rendering logic/components, since both show "one prediction's full detail" — consider extracting a shared `PredictionDetail` component used by both the fresh post-scan Result page and this past-prediction detail view, rather than duplicating the rendering logic.

**Acceptance Criteria:**
- [ ] Clicking a recent-scan row navigates to a working detail view showing that exact prediction's full information (crop, disease, confidence, symptoms/prevention/management).
- [ ] The same detail-view pattern/route is reused (not duplicated) when Prompt 152 adds the equivalent click-through from the full History page.

**Must Not Break:** Must correctly pass the specific clicked prediction's real `id` through routing/state so the detail view fetches/displays the correct record, never a mismatched or most-recent-by-default one.

---

#### Prompt 134 — Responsive Dashboard Layout

**Do:** Make the dashboard layout responsive for mobile screens (stacked cards, scrollable table).

**Context & Why:** A meaningful share of real users (farmers checking a scan result in the field) will likely use the app on a phone — this is the dashboard's dedicated responsive pass, ahead of the full-app responsive pass in Prompt 163.

**Requirements:**
- At narrow viewport widths (Tailwind's `sm`/below breakpoints), stack the three `StatsCard` components vertically (or in a 2+1 or horizontally-scrollable row) instead of a fixed 3-column grid that would otherwise overflow/compress awkwardly.
- Make `RecentScansTable` horizontally scrollable within its container on narrow screens (`overflow-x-auto` on a wrapping div) rather than letting it break the page's overall layout, or alternatively switch to a stacked card-per-row layout on mobile — pick one approach and apply the same pattern consistently wherever tables appear elsewhere in the app (History's table, Prompt 149).
- Verify the "+ New Scan" button (Prompt 131) remains prominently placed and easily tappable (adequate touch-target size) on mobile.

**Acceptance Criteria:**
- [ ] The dashboard renders cleanly with no horizontal page overflow or obviously broken layout at common mobile viewport widths (e.g. 375px, 414px).
- [ ] All interactive elements remain easily tappable at mobile sizes.

**Must Not Break:** Must not degrade the existing desktop layout while adding responsive behavior — verify both breakpoints after this change.

---
### 3.D Scan / Upload Flow

#### Prompt 135 — Image Picker UI

**Do:** Build `frontend/src/pages/NewScan.tsx` with a drag-and-drop / click-to-upload image picker.

**Context & Why:** This replaces Prompt 117's placeholder `/scan` route with the real entry point into the app's core feature — the picker's UX quality directly affects how usable the whole product feels, since this is the very first interaction in every single scan.

**Requirements:**
- A large, clearly-labeled drop zone (e.g. "Drag and drop a leaf photo here, or click to browse") implemented with native HTML5 drag-and-drop events (`onDragOver`, `onDrop`) plus a hidden `<input type="file" accept="image/*">` triggered by clicking the zone, for devices/users without drag-and-drop support.
- Store the selected `File` object in component state (`useState<File | null>`) — this prompt's scope is selection only; preview (136), validation (137), and the actual upload (138) are separate subsequent prompts.
- Visually indicate an active drag-over state (e.g. a border/background color change) while a file is being dragged over the zone, for clear affordance.

**Acceptance Criteria:**
- [ ] Both dragging-and-dropping a file and clicking-to-browse successfully select a file into component state.
- [ ] The drop zone visually responds to an active drag-over state.

**Must Not Break:** N/A — new page, replaces Prompt 117's placeholder.

---

#### Prompt 136 — Image Preview

**Do:** Add a client-side image preview before submission.

**Context & Why:** Users should be able to confirm they selected the right photo before committing to an upload (and before it counts as an API call/history entry) — a basic but important trust-building UX step.

**Requirements:**
- Once a file is selected (Prompt 135), generate a preview using `URL.createObjectURL(file)` and render it as an `<img>` within the page, replacing or sitting alongside the drop-zone UI.
- Provide a clear way to clear/change the selection (e.g. an "×" or "Choose a different photo" control) that resets state back to the empty drop-zone view.
- Properly revoke the object URL (`URL.revokeObjectURL`) when the component unmounts or when a new file replaces the previous preview, to avoid memory leaks from accumulated unreleased object URLs.

**Acceptance Criteria:**
- [ ] Selecting a file immediately shows a correct visual preview of that exact image.
- [ ] Clearing the selection returns to the empty drop-zone state cleanly.
- [ ] No memory-leak warnings from un-revoked object URLs across repeated selections (verify by selecting/clearing several files in a row during manual testing).

**Must Not Break:** Must build on Prompt 135's file-selection state without altering its drag-and-drop/click-to-browse behavior.

---

#### Prompt 137 — Client-Side File Validation

**Do:** Add client-side file-type and file-size validation before upload.

**Context & Why:** Mirrors the backend's own validation (Prompt 89) on the client side for immediate feedback, exactly as Prompt 122 did for the auth forms — catching an obviously-wrong file (a PDF, a 50MB image) before spending time on an upload that the backend would reject anyway.

**Requirements:**
- Validate the selected file's MIME type against the same accepted set the backend enforces (`image/jpeg`, `image/png`, `image/webp`, per Prompt 89) and its size against the same configured maximum (expose `VITE_MAX_UPLOAD_SIZE_MB` as a frontend environment variable mirroring the backend's `MAX_UPLOAD_SIZE_MB` setting from Prompt 58, so the two stay easy to keep in sync, rather than hardcoding a possibly-different number here).
- Show a clear, specific error message (e.g. "Please upload a JPEG, PNG, or WEBP image" / "File is too large — please upload an image under 10MB") directly in the `NewScan` page if validation fails, and prevent the preview (Prompt 136) and any subsequent upload attempt (Prompt 138) from proceeding with an invalid file.
- As with Prompt 122's auth validation, explicitly document that this is a UX convenience, not a security boundary — the backend's own validation (Prompt 89) remains authoritative and must never be assumed redundant/skippable because of this client-side check.

**Acceptance Criteria:**
- [ ] Selecting a non-image file shows a clear error and does not proceed to preview/upload.
- [ ] Selecting an oversized image shows a clear error and does not proceed.
- [ ] Selecting a valid image proceeds normally to the preview state from Prompt 136.

**Must Not Break:** Must not block legitimately valid images — verify with several real sample images of varying (valid) sizes and formats.

---

#### Prompt 138 — Wire Upload to `POST /predict`

**Do:** Wire the upload form to `POST /predict` with multipart/form-data and the JWT header.

**Context & Why:** This is the actual connection to the backend's core feature route (Prompt 89) — everything built in Prompts 135–137 has been leading to this single API call.

**Requirements:**
- On a "Scan" / "Analyze" submit action (a button, using Prompt 114's `Button` component), construct a `FormData` object with the selected file appended under the exact field name the backend expects (`file`, per Prompt 89's `file: UploadFile = File(...)` parameter name), and call the API service's `apiPostFormData`-style helper (Prompt 118) against `/predict`.
- Confirm (per Prompt 118's explicit requirement) that this request does NOT have `Content-Type: application/json` forced onto it, letting the browser set the correct `multipart/form-data` boundary header automatically.
- Do not yet handle the loading-state UI (Prompt 139) or error handling (Prompt 140) in detail in this prompt — focus on confirming the raw upload mechanically reaches the backend and a real prediction comes back successfully when tested manually end-to-end.

**Acceptance Criteria:**
- [ ] Submitting a valid image results in a real `POST /predict` request reaching the backend and a real prediction response being received by the frontend (verified via browser dev tools network tab and/or a temporary console log of the response).
- [ ] The request correctly includes the JWT Authorization header (via `api.ts`, Prompt 118) and the file under the correct `file` field name.

**Must Not Break:** Must call the real `POST /predict` route (Prompts 89–94) with the exact field name and auth header it expects.

---

#### Prompt 139 — "Analyzing..." Loading Screen

**Do:** Build an `Analyzing.tsx` loading state shown while the request is in flight.

**Context & Why:** A model-inference request (Prompt 86) isn't instant — showing a dedicated, reassuring full-screen loading state (rather than a generic small spinner on an otherwise-static form) manages user expectations during this wait, especially relevant given Prompt 190's later performance-latency work implies this wait could be non-trivial.

**Requirements:**
- `Analyzing.tsx`: a full-page (or full-content-area) state featuring Prompt 116's `Spinner` component at a large size, a reassuring message (e.g. "Analyzing your photo..." with perhaps a rotating sub-message like "Checking for common diseases..." for a touch of polish, optional), and critically, no interactive elements that could let the user navigate away mid-request in a way that orphans the pending API call awkwardly (though the request itself, once fired, will complete regardless of navigation — document this behavior).
- Wire this into `NewScan.tsx`'s submit flow from Prompt 138: show this state (either by swapping rendered content within the same page/component, or navigating to a distinct `/scan/analyzing`-style sub-state — a simple in-page conditional render based on a `isAnalyzing` boolean state is likely simplest and avoids extra routing complexity) for the duration of the `POST /predict` request.

**Acceptance Criteria:**
- [ ] Submitting a scan shows this dedicated analyzing state immediately, replacing the upload form, for the duration of the real API request.
- [ ] The analyzing state disappears and is replaced by the next appropriate state (success → Result page, per Prompt 142; failure → error display, per Prompt 140) exactly when the request resolves.

**Must Not Break:** Must correctly wrap the exact `POST /predict` call from Prompt 138 — timing must reflect the real request's actual in-flight duration, not a fixed/fake delay.

---

#### Prompt 140 — Network/Server Error Handling

**Do:** Handle and display network/server errors gracefully on the scan page.

**Context & Why:** Prompt 94 already made the backend return clean, informative error responses for `/predict`'s various failure modes — this prompt ensures those errors actually reach and are clearly shown to the user, rather than leaving them stuck on the `Analyzing` screen (Prompt 139) indefinitely or facing a silent failure.

**Requirements:**
- Catch errors from the `POST /predict` call (Prompt 138) the same way Prompt 123 did for auth errors — using the typed error from `api.ts` (Prompt 118) and displaying its `detail` message clearly on the `NewScan` page once the request fails, transitioning out of the `Analyzing` state (Prompt 139) back to a state where the user can see the error and try again.
- Separately handle true network failures (e.g. the backend is unreachable entirely — a `fetch` network error rather than a non-2xx HTTP response) with a distinct, clear message ("Unable to reach the server. Please check your connection and try again.") since this case won't have a backend-provided `detail` message to display.
- Provide a clear way to retry (re-attempt the same already-selected image) or start over (clear the selection and return to the picker, Prompt 135) after an error.

**Acceptance Criteria:**
- [ ] A deliberately-triggered backend error (e.g. temporarily stopping the backend server during a test, or uploading a file that triggers Prompt 94's `422`/`500` paths) shows a clear, appropriate error message and exits the `Analyzing` state.
- [ ] The user can retry or start over after an error without needing to reload the whole page.

**Must Not Break:** Must not interfere with the successful-path flow (Prompts 138–139, 142) — error handling is an additional branch, not a replacement for existing success logic.

---

#### Prompt 141 — "Open Camera" Placeholder

**Do:** Add a placeholder "Open Camera" button (disabled/v2) with a tooltip noting camera capture is a planned enhancement.

**Context & Why:** Direct camera capture (rather than only picking an existing photo) is a natural, expected feature for this kind of app, but is explicitly out of scope for the current 220-prompt build — this placeholder sets correct user expectations now rather than the feature simply appearing to be missing/forgotten, and gives the team a clearly-marked, deliberate spot to implement it later if desired.

**Requirements:**
- Add a visibly disabled secondary button/control near the main upload picker (Prompt 135) labeled "Open Camera" (or similar), styled using Prompt 114's `Button` component with `disabled={true}`.
- Add a tooltip (a simple CSS-only tooltip on hover, or a small always-visible caption beneath the button, whichever is simpler to implement well) stating "Camera capture coming soon" or similar, so its disabled state reads as "not yet available" rather than "broken."

**Acceptance Criteria:**
- [ ] The "Open Camera" control is visibly present but clearly disabled/non-interactive.
- [ ] Hovering (or otherwise inspecting) it reveals a clear explanatory tooltip/caption.

**Must Not Break:** Must not interfere with the real, functional upload picker (Prompt 135) — this is a purely additive, non-functional UI element.

---

#### Prompt 142 — Redirect to Result on Success

**Do:** Redirect to the Result page automatically on a successful prediction response.

**Context & Why:** Completes the scan flow's happy path, connecting `NewScan.tsx`'s successful `POST /predict` response (Prompt 138) to the Result page (built next, in Prompt 143) — without this, a successful scan would have nowhere to go.

**Requirements:**
- On a successful (non-error) response from Prompt 138's `POST /predict` call, transition out of the `Analyzing` state (Prompt 139) and navigate to a result view — decide now (consistent with the pattern established in Prompt 133) whether this uses a dedicated route (e.g. `/scan/result/:id`, using the newly-created prediction's real `id` from the response) or passes the response data directly via React Router's navigation `state` — a dedicated route using the real `id` is preferable since it makes the result shareable/bookmarkable/refreshable (refreshing would then re-fetch by id rather than losing the data), and is consistent with Prompt 133's detail-view approach.
- Ensure the full prediction response data (or at minimum its `id`, with the Result page then fetching full detail if needed) correctly reaches the Result page so Prompt 143 has what it needs to render immediately without an extra unnecessary round-trip if the data is already in hand from the `/predict` response itself.

**Acceptance Criteria:**
- [ ] A successful scan automatically navigates to a working Result page displaying that exact prediction's data (crop, disease, confidence), with no manual action needed from the user beyond having submitted the scan.
- [ ] Refreshing the browser on the resulting Result page URL still correctly shows the same prediction's data (confirms the routing approach correctly supports direct/refreshed access, not only in-app navigation with transient state).

**Must Not Break:** Must correctly use the real response data from Prompt 138's `POST /predict` call, including its real database `id` (per Prompt 92's backend requirement that the response include the persisted row's `id`).

---
### 3.E Result Display

#### Prompt 143 — Core Result Page

**Do:** Build `frontend/src/pages/Result.tsx` showing the uploaded image thumbnail, predicted crop, disease name, and confidence percentage.

**Context & Why:** This is the payoff screen of the entire app — the single page that delivers the actual value proposition ("here's what's wrong with your plant") — and the direct target of Prompt 142's post-scan redirect, Prompt 133's recent-scan click-through, and Prompt 152's history detail click-through.

**Requirements:**
- Accept a prediction `id` via the route (per the routing decision made in Prompt 142), and fetch its full detail if not already available from navigation state — consider extracting a shared data-fetching hook (e.g. `usePrediction(id)`) reusable across this page and any other detail-view context (Prompts 133/152), avoiding duplicated fetch logic.
- Render: the uploaded image (via `image_url`, handling the case where it's `null` per Prompt 93's fail-soft image-persistence behavior — show a sensible placeholder/fallback graphic in that case, not a broken image icon), the predicted crop name, the disease name, and the confidence value formatted as a percentage (same `× 100` conversion convention established in Prompt 130).
- This prompt's scope is these core fields only — the confidence visual indicator (144), symptoms/prevention/management sections (145), the uncertain-result state (146), "Scan Another" (147), and feedback control (148) are each separate subsequent prompts building out the rest of this page.

**Acceptance Criteria:**
- [ ] Navigating to a valid prediction's Result page correctly displays its real crop, disease, and confidence percentage.
- [ ] A prediction with `image_url: null` shows a sensible fallback rather than a broken image.

**Must Not Break:** Must correctly consume the real `PredictionOut` response shape (Prompt 88) from the backend.

---

#### Prompt 144 — Confidence Visual Indicator

**Do:** Build a confidence-bar or badge component that visually reflects the confidence score.

**Context & Why:** A bare percentage number is less immediately scannable than a visual indicator — this small, focused component makes "how sure is the app" instantly legible at a glance, complementing the text percentage already shown per Prompt 143.

**Requirements:**
- Build as a small reusable component (e.g. `frontend/src/components/ConfidenceBar.tsx`) accepting `confidence: number` (the `0.0–1.0` fraction) and rendering either a horizontal progress-bar-style fill (width proportional to confidence, using the `primary` token for high confidence) or a colored badge/pill with the percentage text inside it.
- Use color to reinforce meaning: consider a gradient or threshold-based color shift (e.g. green for high confidence, amber/yellow approaching the threshold, consistent with — but visually distinct from — the dedicated warning treatment Prompt 146 adds specifically for results below the actual production threshold) — document the exact color-threshold logic chosen in a code comment so it's clearly intentional, not arbitrary.
- Reuse this same component later wherever a confidence value is shown elsewhere in the app (e.g. consider using it in Prompt 130's recent-scans table and Prompt 149's history table too, for visual consistency, rather than inventing a separate ad hoc indicator in each location).

**Acceptance Criteria:**
- [ ] The component correctly renders a visually proportional/accurate representation of a given confidence value.
- [ ] Color changes meaningfully and consistently across a range of test confidence values (e.g. 0.95 vs. 0.60 vs. 0.40 look visibly, meaningfully different).

**Must Not Break:** Must accept the same `0.0–1.0` fraction convention as the rest of the app (Prompt 88) — do not silently expect a pre-converted percentage.

---

#### Prompt 145 — Symptoms / Prevention / Management Sections

**Do:** Build collapsible/sectioned display for Symptoms, Prevention, and Management content returned by the API.

**Context & Why:** This is the actual actionable guidance the app promises beyond just naming a disease — the `disease_info` object from `PredictionOut` (Prompt 88) is rendered here, giving the result genuine practical value to a farmer, not just a diagnosis label.

**Requirements:**
- Render three clearly-labeled sections — "Symptoms", "Prevention", "Management" — each displaying its corresponding text/content from `prediction.disease_info` (handling whichever text/JSON-array structure was decided back in Prompt 64 for these fields — render as a paragraph if plain text, or a bulleted list if structured as an array).
- Use a simple accordion/collapsible pattern (each section expandable/collapsible independently, perhaps with "Symptoms" expanded by default since it's often the most immediately relevant) to keep the page scannable rather than presenting three large blocks of text all at once — a lightweight custom implementation (a `useState` boolean per section) is sufficient; no heavy UI library needed for this.
- Also render the disease's general `description` field prominently near the top of this section group, before the three collapsible sub-sections, since it provides useful context before diving into specifics.

**Acceptance Criteria:**
- [ ] All four fields (`description`, `symptoms`, `prevention`, `management`) from the real backend response are correctly displayed with accurate content for the actual predicted disease.
- [ ] Collapsible sections correctly expand/collapse independently of each other.

**Must Not Break:** Must correctly consume `prediction.disease_info`'s real field names/structure from Prompt 88's schema.

---

#### Prompt 146 — Uncertain Result UI State

**Do:** Add a distinct "uncertain result" UI state (warning styling + message) for predictions below the confidence threshold.

**Context & Why:** This is the frontend's direct, essential response to the backend's `is_confident` flag (Prompt 90) — showing a confident-looking result for a prediction the model itself flagged as unreliable would be actively misleading to a farmer potentially making real treatment decisions, so this distinction must be impossible to miss.

**Requirements:**
- When `prediction.is_confident === false`, render a prominent warning banner near the top of the Result page (distinct amber/yellow styling, clearly different from the normal confident-result presentation) with a message along the lines of: "This result has lower confidence than usual. Consider retaking the photo in better lighting, from a closer angle, or consulting an agricultural expert for confirmation." — the message should be genuinely actionable (suggesting concrete next steps), not just a bare warning label.
- The rest of the page (crop/disease/confidence/symptoms, per Prompts 143–145) should still render normally beneath this banner (per Prompt 90's backend behavior — the data is still present and potentially useful even if uncertain), not be hidden or replaced entirely.
- Ensure this state is visually impossible to miss (placement, color, perhaps an icon) — this is a user-safety-relevant UI element, not a minor cosmetic detail.

**Acceptance Criteria:**
- [ ] A prediction with `is_confident: false` (achievable via Prompt 95's testing approach, or a genuinely ambiguous real test image) shows the warning banner prominently, with the rest of the result still visible beneath it.
- [ ] A prediction with `is_confident: true` never shows this banner.

**Must Not Break:** Must correctly key off the real `is_confident` boolean field from the backend (Prompt 90) — must not attempt to independently recompute a confidence threshold on the frontend using a possibly-different/stale value.

---

#### Prompt 147 — "Scan Another" Button

**Do:** Add a "Scan Another" button returning to `/scan`.

**Context & Why:** Closes the loop back to the start of the scan flow, supporting the realistic use case of a user wanting to check multiple leaves/plants in one sitting without extra navigation friction.

**Requirements:**
- Place a clearly-visible `Button` (Prompt 114, likely `variant="secondary"` since the primary action on this page has already been completed — viewing the result — making this a secondary next-step rather than the page's main focus) near the bottom of the Result page, navigating to `/scan` on click.
- Ensure navigating to `/scan` from here correctly resets `NewScan.tsx`'s internal state (Prompt 135's file-selection state) back to empty, not leftover from the previous scan — verify this explicitly, since component state could otherwise persist unexpectedly depending on how routing/unmounting is handled.

**Acceptance Criteria:**
- [ ] Clicking "Scan Another" navigates to `/scan` with a fully-reset, empty upload picker ready for a new image.

**Must Not Break:** Must route to the real `/scan` path (Prompt 117) and must not leave stale state from the previous scan session.

---

#### Prompt 148 — "Was This Correct?" Feedback Control

**Do:** Add an optional "Was this correct?" feedback control that calls `POST /predictions/{id}/feedback`.

**Context & Why:** This is the frontend trigger for the backend's feedback endpoint (Prompt 99) — closing the loop on the project's stated future-scope ambition of eventually using this data to improve the model, even though that retraining loop itself is out of scope for this build.

**Requirements:**
- Render a simple "Was this correct?" prompt with "Yes" / "No" controls. On "Yes," immediately call `POST /predictions/{id}/feedback` with `{"is_correct": true}` (matching the backend's `FeedbackCreate` schema, Prompt 99) and show a brief confirmation ("Thanks for the feedback!").
- On "No," reveal an additional small form allowing the user to optionally specify what the actual disease was (a text input or ideally a dropdown populated from `GET /diseases`, Prompt 96, for consistency with the app's known disease vocabulary) and an optional free-text comment, then submit `{"is_correct": false, "actual_disease": "...", "comment": "..."}`.
- After successful submission (either path), disable/hide the control for that prediction (prevent duplicate feedback submissions in the same session) and show a clear confirmation state.
- Handle submission errors gracefully (reusing the same error-display pattern as Prompts 123/140) — a failed feedback submission should not disrupt the rest of the Result page's display.

**Acceptance Criteria:**
- [ ] Submitting "Yes" feedback results in a real `Feedback` row created in the backend with `is_correct: true`.
- [ ] Submitting "No" feedback with a selected actual disease and comment results in a real row with those exact values.
- [ ] The control correctly prevents/discourages duplicate submissions for the same prediction within the same page session.

**Must Not Break:** Must call the real `POST /predictions/{id}/feedback` route (Prompt 99) with the correct `prediction_id` path parameter and request body shape.

---
### 3.F History Page

#### Prompt 149 — Paginated History Table

**Do:** Build `frontend/src/pages/History.tsx` listing all of the current user's past predictions in a paginated table.

**Context & Why:** This replaces Prompt 117's placeholder `/history` route with the full, unabridged counterpart to the dashboard's 5-row preview (Prompt 130) — exercising the complete pagination contract of `GET /predictions/history` (Prompt 98) that the dashboard's simpler call only partially used.

**Requirements:**
- Maintain `page` state (starting at 1) and call `GET /predictions/history?page={page}&page_size=20` (or another reasonable default page size) via `api.ts`, rendering the response's `items` in a table with the same column set established in Prompt 130 (thumbnail, crop, disease, confidence — via Prompt 144's shared `ConfidenceBar` component for consistency — and date), plus pagination controls (Previous/Next buttons, and/or numbered page links) driven by the response's `total_pages`.
- Disable/hide the "Previous" control on page 1 and the "Next" control on the last page, based on the real `total_pages` value from the backend, not a guessed/local calculation.
- This prompt's scope is the base paginated table — filtering (150), sorting (151), detail modal (152), and loading/empty states (153) are separate subsequent prompts.

**Acceptance Criteria:**
- [ ] Table correctly displays a full page of the authenticated user's real prediction history, with working Previous/Next pagination reflecting the backend's real `total`/`total_pages`.
- [ ] A user with fewer predictions than one page size sees all of them on page 1 with pagination controls appropriately disabled/hidden.

**Must Not Break:** Must use the real `GET /predictions/history` contract from Prompt 98, including its exact query parameter names.

---

#### Prompt 150 — Filtering by Crop and Disease

**Do:** Add filtering by crop and by disease to the history table.

**Context & Why:** As a user's history grows, finding a specific past scan (e.g. "show me all my Tomato scans") becomes valuable — this directly exercises the `crop`/`disease` query parameters Prompt 98 already built into the backend route specifically to support this.

**Requirements:**
- Add two dropdown filters (populated from `GET /diseases`, Prompt 96, to ensure the exact crop/disease name strings used match what the backend's `predictions` table actually stores — rather than a free-text input that could mismatch backend naming/casing) for "Crop" and "Disease," each including an "All" option to clear that specific filter.
- Changing either filter triggers a new `GET /predictions/history` call including the corresponding `crop`/`disease` query parameter, and resets `page` back to 1 (since the previously-current page number may no longer be valid/meaningful under a new filter).
- Both filters should be combinable (selecting both a crop and a disease narrows to predictions matching both simultaneously, matching the backend's AND-combined filter behavior from Prompt 98).

**Acceptance Criteria:**
- [ ] Selecting a specific crop correctly narrows the table to only that crop's predictions, verified against the real backend data.
- [ ] Combining a crop filter and a disease filter correctly narrows to the intersection of both.
- [ ] Clearing a filter (selecting "All") correctly returns to the unfiltered (or remaining-filter-only) result set.

**Must Not Break:** Must send exactly the crop/disease name strings the backend expects (sourced from `GET /diseases`, Prompt 96, not independently typed/guessed), and must not break the base pagination behavior from Prompt 149.

---

#### Prompt 151 — Sorting by Date and Confidence

**Do:** Add sorting by date and by confidence.

**Context & Why:** Completes the exercise of Prompt 98's full query-parameter contract (`sort_by`/`sort_order`), giving users control over how their history is ordered beyond the default most-recent-first.

**Requirements:**
- Add sortable column headers (or a simple dropdown control) for "Date" and "Confidence," each toggling between ascending/descending on repeated clicks, sending the corresponding `sort_by`/`sort_order` query parameters to `GET /predictions/history` (reusing the exact allowlisted values the backend validates against, per Prompt 98 — confirm `created_at` and `confidence` are both in that backend allowlist; if `confidence` isn't yet allowlisted there, that's a backend gap to flag and fix rather than silently working around on the frontend).
- Visually indicate the currently-active sort column and direction (e.g. an arrow icon next to the active column header).
- Changing sort should reset `page` back to 1, same reasoning as Prompt 150's filter-change behavior.

**Acceptance Criteria:**
- [ ] Clicking "Date" toggles between newest-first and oldest-first, correctly reflected in the displayed order.
- [ ] Clicking "Confidence" toggles between highest-first and lowest-first.
- [ ] The active sort state is visually indicated and persists correctly across pagination (e.g. moving to page 2 while sorted by confidence keeps that same sort order).

**Must Not Break:** Must use the real backend-supported `sort_by`/`sort_order` values from Prompt 98 — do not invent frontend-only sort options the backend can't actually fulfill.

---

#### Prompt 152 — Prediction Detail Modal/Page

**Do:** Add a detail modal/page for viewing a single past prediction's full result again.

**Context & Why:** This is the History page's version of Prompt 133's dashboard click-through — reusing the same shared detail-view pattern/component decided there (likely the dedicated route approach, e.g. `/history/:id` or reusing `Result.tsx`'s route pattern directly) rather than building a second, divergent implementation.

**Requirements:**
- Make each row in the `History` table clickable, navigating to the same shared prediction-detail view established in Prompt 133/Result.tsx — confirm this reuses the actual `Result.tsx` page (or its extracted shared rendering component) rather than creating a near-duplicate "history detail" page with its own separate implementation of symptoms/prevention/confidence rendering.
- Ensure navigating back from this detail view (a "Back to History" link/browser back button) returns the user to the History page with their previous filters/sort/page state ideally preserved (a nice-to-have; at minimum, returning to an unfiltered first page of History is acceptable if preserving exact prior state proves complex, but document which behavior was actually implemented).

**Acceptance Criteria:**
- [ ] Clicking any history row navigates to a working detail view showing that exact prediction's full data, using the same component/page as the fresh post-scan Result page (Prompt 143), confirmed by code reuse, not duplication.
- [ ] Navigating back returns to the History page in a reasonable, working state.

**Must Not Break:** Must reuse, not duplicate, the Result page/detail-view logic established in Prompts 133/142/143.

---

#### Prompt 153 — History Empty and Loading States

**Do:** Add an empty-state and a loading-skeleton state to the history page.

**Context & Why:** Mirrors Prompt 132's dashboard treatment, applied to the full History page — particularly important here since filtering (150) can legitimately produce a correct, valid empty result set (e.g. "no Tomato scans yet") distinct from the "no predictions at all" case the dashboard's empty state handles.

**Requirements:**
- Show a loading skeleton/spinner (Prompt 116) while any `GET /predictions/history` request (initial load, or triggered by a page/filter/sort change) is in flight.
- Distinguish two different empty-state messages: (a) the user has zero predictions at all (reuse/mirror Prompt 132's dashboard empty-state message and call-to-action), versus (b) the user has predictions, but the current filter combination matches none of them (a different message, e.g. "No scans match your current filters" with a clear way to reset filters, rather than incorrectly suggesting the user has never scanned anything).
- Ensure transitioning between loading/empty/populated states as filters/pagination change is smooth and doesn't flash incorrect intermediate states (e.g. briefly showing a stale "empty" message while new filtered data is still loading).

**Acceptance Criteria:**
- [ ] A brand-new user sees the correct "no scans yet" empty state with a call-to-action.
- [ ] A user with history, but an overly-narrow filter combination, sees the distinct "no scans match your filters" message with an easy way to reset filters.
- [ ] Loading states correctly appear during every data-changing interaction (initial load, pagination, filter change, sort change), not only the very first page load.

**Must Not Break:** Must correctly distinguish the two empty-state cases based on real data (total history count vs. filtered result count), not guess based on UI state alone.

---
### 3.G Profile / Settings Page

#### Prompt 154 — Profile Display

**Do:** Build `frontend/src/pages/Profile.tsx` displaying the user's name, email, photo, phone, location, and preferred crops.

**Context & Why:** Replaces Prompt 117's placeholder `/profile` route — this is the read view of the user's own account data, sourced from `authStore` (Prompt 119), that Prompts 155–159 will progressively add editing capability to.

**Requirements:**
- Read the current user from `authStore` directly (no need for a fresh `GET /users/me` call on mount if the store is already populated and kept in sync — per Prompt 119's `setUser` action, the store should already reflect the latest known profile).
- Display each field clearly labeled: name, email (note: email is read-only everywhere in this app, per Prompt 79's deliberate exclusion from the update schema — visually indicate this, e.g. no edit affordance on this specific field even once the edit form (155) is added), photo (via `Avatar`, Prompt 115), phone, location, preferred crops (as a list/set of tags/chips).
- Handle fields that are `null`/empty gracefully (e.g. "Not set" placeholder text for an unset phone/location, rather than a blank space that looks broken).

**Acceptance Criteria:**
- [ ] All six listed pieces of information display correctly for the real authenticated user.
- [ ] Unset optional fields show a clear "not set" indication rather than appearing broken/blank.

**Must Not Break:** Must read from `authStore` (Prompt 119) using its real `UserProfile` field names.

---

#### Prompt 155 — Edit Profile Form

**Do:** Add an "Edit Profile" form wired to `PUT /users/me`.

**Context & Why:** This is the real editing capability for everything Prompt 154 displays (except email, deliberately) — the frontend counterpart to the backend's partial-update route (Prompt 81).

**Requirements:**
- Toggle between a read-only display mode (Prompt 154) and an editable form mode (an "Edit Profile" button switches into edit mode; "Save"/"Cancel" buttons in edit mode), using Prompt 115's `Input` component for `name`, `phone`, `location` fields (preferred crops handled separately in Prompt 159).
- On "Save," construct a `PUT /users/me` request body containing only the fields the user actually has the ability to change on this form (matching the backend's `UserProfileUpdate` schema from Prompt 79 — `name`, `phone`, `location`, `preferred_crops`), and on success, update `authStore` via `setUser()` (Prompt 119) with the response's updated profile, then return to read-only display mode.
- On "Cancel," discard any in-progress unsaved edits and return to read-only mode showing the original (unchanged) data.

**Acceptance Criteria:**
- [ ] Editing and saving the name/phone/location fields correctly persists the change to the backend and is immediately reflected both in this page's display and (per Prompt 171) in the navbar.
- [ ] "Cancel" correctly discards unsaved changes without calling the API.
- [ ] The email field has no edit affordance anywhere in this form.

**Must Not Break:** Must call the real `PUT /users/me` route (Prompt 81) with field names matching `UserProfileUpdate` (Prompt 79) exactly, and must update `authStore` via `setUser()` (Prompt 119), not `login()`, since no new token is issued by this action.

---

#### Prompt 156 — Profile Photo Upload Control

**Do:** Add a profile-photo upload control wired to `POST /users/me/photo`.

**Context & Why:** The frontend counterpart to the backend's photo-upload route (Prompt 82), completing the avatar-personalization loop started by Prompt 83's `null`-vs-URL contract.

**Requirements:**
- Add a clickable control over/near the `Avatar` component on the Profile page (e.g. a small camera-icon overlay, or a distinct "Change Photo" button) that opens a native file picker (`<input type="file" accept="image/*">`), reusing the same client-side validation pattern established in Prompt 137 (correct MIME types, size limit) before attempting upload.
- On file selection, immediately call `POST /users/me/photo` via `api.ts`'s multipart-upload helper (Prompt 118), show a brief loading indicator during the upload, and on success update `authStore` via `setUser()` with the response's updated `profile_photo_url`.
- Handle upload errors (reusing the established error-display pattern from Prompts 123/140) without leaving the page in a broken/stuck loading state.

**Acceptance Criteria:**
- [ ] Selecting a valid photo successfully uploads it, and the new photo immediately appears in the `Avatar` on this page and (per Prompt 171) in the navbar.
- [ ] Invalid file type/size selections are caught client-side before attempting upload, consistent with Prompt 137's validation approach.

**Must Not Break:** Must call the real `POST /users/me/photo` route (Prompt 82) and correctly update `authStore` (Prompt 119) afterward.

---

#### Prompt 157 — Read-Only Account Metadata

**Do:** Display account metadata (member since, last login) read-only on the profile page.

**Context & Why:** Small but meaningful transparency/trust-building details, sourced directly from the `User` model's `created_at`/`last_login_at` fields (Prompt 62) that have existed since Phase 2 but haven't yet been surfaced anywhere in the UI.

**Requirements:**
- Display "Member since {formatted created_at date}" and "Last login: {formatted last_login_at date, or 'This is your first login' / similar if null}" in a clearly read-only section of the Profile page (visually distinct from the editable fields above it — e.g. smaller, muted text, with no edit affordance of any kind).
- Use the same date-formatting convention established elsewhere in the app (Prompt 130) for consistency.

**Acceptance Criteria:**
- [ ] Both dates display correctly, sourced from the real authenticated user's actual account data.
- [ ] A user on their very first session (where `last_login_at` might still reflect this exact login, or be freshly set, depending on Prompt 73's exact timing) shows a sensible value, not `null`/`undefined` rendered as literal text.

**Must Not Break:** Must read the real `created_at`/`last_login_at` fields from `authStore`'s `UserProfile` (Prompt 119), which must already include them per Prompt 79's `UserProfileOut` schema.

---

#### Prompt 158 — Form Validation and Toasts

**Do:** Add form validation and success/error toasts for profile updates.

**Context & Why:** Brings the Profile edit form (Prompt 155) up to the same UX standard already established for the auth forms (Prompts 122–123) — clear validation feedback and clear confirmation that an action actually succeeded, rather than a silent, ambiguous save.

**Requirements:**
- Add the same client-side validation approach used elsewhere (Prompt 122) to the editable Profile fields where meaningful (e.g. `name` required/non-empty; `phone`/`location` can remain genuinely optional with no required-format validation unless the team wants to add phone-format validation specifically — document the decision).
- Introduce a lightweight toast/notification pattern (a simple custom implementation — a small `useState`-driven dismissible banner, or a minimal library if the team prefers — is sufficient; no need for a heavy toast library for this scope) showing a brief "Profile updated successfully" confirmation after a successful `PUT /users/me` (Prompt 155) or `POST /users/me/photo` (Prompt 156), and a clear error toast/message on failure of either.
- Reuse this same toast pattern for the feedback-submission confirmation already described in Prompt 148, if that hasn't already been implemented with its own separate confirmation UI — consolidate to one consistent pattern across the app rather than inventing a second one here.

**Acceptance Criteria:**
- [ ] A successful profile update or photo upload shows a clear, brief success confirmation.
- [ ] A failed update/upload shows a clear error message, distinct from the success state.
- [ ] Submitting the edit form with an empty required field (e.g. blank name) is caught client-side before attempting the API call.

**Must Not Break:** Must not change the actual save/upload logic from Prompts 155–156 — this prompt adds validation and feedback UI around that existing logic.

---

#### Prompt 159 — Preferred Crops Multi-Select

**Do:** Add a "Preferred Crops" multi-select/tag input for the user to customize.

**Context & Why:** Completes the `preferred_crops` field's editing capability (already supported by the backend's `UserProfileUpdate` schema since Prompt 79, and partially displayed read-only since Prompt 154) — letting users personalize which crops they're most interested in, potentially useful for future features (e.g. filtering/prioritizing relevant content) even though this build doesn't yet use the field for anything beyond storage/display.

**Requirements:**
- Build (or adopt a simple existing pattern/library if the team prefers, documenting the choice) a tag-style multi-select input populated with the known crop names (sourced from `GET /diseases`, Prompt 96, deduplicated to unique `crop` values — the same small set of crops the model actually recognizes, per `ml/models/class_names.json`'s crops, rather than an arbitrary/unbounded free-text list that could include crops the app has no data for) that the user can add/remove from within the Edit Profile form (Prompt 155).
- Include this field's current/updated value in the same `PUT /users/me` request body already being constructed by Prompt 155's save logic — this is additive to that existing form, not a separate save action.
- On the read-only Profile display (Prompt 154), render the selected crops as a clean row of tags/chips rather than a plain comma-separated string.

**Acceptance Criteria:**
- [ ] The multi-select is populated with the real, correct set of crop names the app actually supports.
- [ ] Adding/removing crops and saving correctly persists the updated list to the backend and displays correctly afterward in both edit and read-only views.

**Must Not Break:** Must integrate into Prompt 155's existing save flow (single `PUT /users/me` call including this field), not introduce a separate, redundant save action.

---
### 3.H Navigation, Layout & About Page

#### Prompt 160 — Persistent Top Navigation Bar

**Do:** Build a persistent top navigation bar with logo, nav links, and a user-avatar dropdown (Profile / Logout) shown on every authenticated page.

**Context & Why:** This is the connective tissue making the app feel like one cohesive product rather than a set of disconnected pages — it's also where Prompt 126's logout logic and Prompt 115's `Avatar` component get their first real, permanent home in the UI (replacing any temporary logout button used for earlier testing).

**Requirements:**
- Build `frontend/src/components/Navbar.tsx` (or similar) containing: an app logo/name on the left, primary nav links (Dashboard, Scan, History, Profile, About) in the center/left-of-center, and on the right, the user's `Avatar` (Prompt 115) which, on click, opens a small dropdown with "Profile" (linking to `/profile`) and "Logout" (triggering Prompt 126's `handleLogout` logic) options.
- Visually highlight the currently-active nav link (using React Router's `NavLink` component, which provides active-state styling hooks out of the box) so users always know which page they're on.
- This navbar renders only for authenticated users/pages — on `/login`/`/signup`, either omit it entirely or render a simplified public-only version (just the logo, no authenticated nav links/avatar) — decide and document which approach is used.

**Acceptance Criteria:**
- [ ] The navbar appears consistently across Dashboard, Scan, History, Profile pages, with correct active-link highlighting.
- [ ] The avatar dropdown correctly navigates to Profile and correctly logs out via the real logic from Prompt 126.
- [ ] The navbar does not render its full authenticated form on the public Login/Signup pages.

**Must Not Break:** Must use `Avatar` (Prompt 115), `authStore` (Prompt 119), and the logout logic (Prompt 126) exactly as already built — must remove/replace any temporary ad hoc logout button used earlier for testing before Prompt 160 existed.

---

#### Prompt 161 — About Page

**Do:** Build `frontend/src/pages/About.tsx` describing the dataset, model, scope, and limitations for transparency.

**Context & Why:** This is the user-facing (and viva-examiner-facing) transparency page — it should accurately summarize real content already produced across Phase 1 (dataset, model choice, limitations) rather than restating the marketing-style framing from the original project report alone, giving visitors genuine insight into how the system actually works and where it falls short.

**Requirements:**
- Pull real content (paraphrased for a general audience, not copy-pasted raw technical documentation) from: `ml/dataset/README.md` (Prompt 15, for dataset description/source/license), `ml/evaluation/MODEL_SELECTION.md` (Prompt 41, for which model and why), `ml/evaluation/SUMMARY.md` (Prompt 50, for real achieved accuracy), and `ml/evaluation/REAL_WORLD_FINDINGS.md` (Prompt 54, for honest limitations) — this page should be the plain-language, public-facing distillation of those more technical internal documents.
- Render via `GET /diseases` (Prompt 96, the one genuinely public, no-auth-required backend data source already available) to also list the 8 supported crop/disease classes directly on this page, since that's directly relevant "scope" information for a visitor wondering "will this work for my crop?"
- Structure with clear headings: "About This Project," "The Dataset," "The Model," "Supported Crops & Diseases," "Known Limitations."

**Acceptance Criteria:**
- [ ] Every factual claim on this page (accuracy numbers, dataset name, model architecture, limitations) is accurate and traceable to a real Phase 1 document, not invented or left as placeholder/illustrative content.
- [ ] The supported crops/diseases list is fetched live from `GET /diseases`, not hardcoded (so it stays correct if the backend's seeded data ever changes).
- [ ] This page is accessible without authentication.

**Must Not Break:** Must be added to the backend's public-route allowlist awareness if relevant (though `About.tsx` itself is a frontend-only route, its one data dependency — `GET /diseases` — is already correctly public per Prompt 96).

---

#### Prompt 162 — Shared Layout Wrapper

**Do:** Build a shared `Layout.tsx` wrapper combining the navbar and page content consistently across all authenticated routes.

**Context & Why:** Rather than every page component individually importing and rendering `Navbar` (Prompt 160), this wrapper centralizes that composition — a cleaner pattern that also gives one single place to add any future app-wide chrome (e.g. a footer, a global error boundary per Prompt 174) without touching every individual page file again.

**Requirements:**
- `Layout.tsx`: renders `Navbar` (Prompt 160) plus a content area (`<Outlet />` if using React Router's nested-route layout pattern, or a `children` prop otherwise) with consistent page padding/max-width/background styling using the design tokens (Prompt 113).
- Update `App.tsx`'s route configuration (Prompt 117, already modified once by `ProtectedRoute` in Prompt 124) to wrap the authenticated route group in this `Layout` — the nested-route pattern (a parent route rendering `Layout`, with `Dashboard`/`NewScan`/`History`/`Profile` as its children rendering into `<Outlet />`) combines cleanly with `ProtectedRoute` from Prompt 124 (one can wrap the other, or both conditions can be checked in the same parent route element — pick a clean composition and document it).
- Decide and document whether `/about` also uses this `Layout` (showing the navbar even though the page itself doesn't require auth) or renders standalone — likely cleaner UX to include the navbar here too for logged-in users browsing to About, while still allowing fully logged-out visitors to view it via a simpler fallback if `Layout` assumes an authenticated user context for the navbar's avatar — resolve this cleanly rather than leaving it ambiguous.

**Acceptance Criteria:**
- [ ] Every authenticated page renders with a consistent navbar/content composition via this single shared wrapper, with no page individually re-implementing that composition.
- [ ] The About page's accessibility (logged-in and logged-out) is explicitly resolved and works correctly in both cases.

**Must Not Break:** Must correctly compose with `ProtectedRoute` (Prompt 124) and `Navbar` (Prompt 160) without creating duplicate navbars or broken nested-routing.

---

### 3.I Responsive & Visual Polish

#### Prompt 163 — Full Responsive Pass

**Do:** Do a full responsive-design pass across all pages at mobile, tablet, and desktop breakpoints.

**Context & Why:** Prompt 134 already handled the Dashboard specifically — this prompt extends that same rigor to every remaining page (Login, Signup, NewScan, Result, History, Profile, About), since a real farmer using this app in the field is likely on a phone, making mobile usability a functional requirement, not a cosmetic nice-to-have.

**Requirements:**
- Systematically review every page built in this phase at three representative widths (e.g. ~375px mobile, ~768px tablet, ~1280px+ desktop), fixing: text that overflows or wraps awkwardly, touch targets that are too small/close together on mobile (buttons, nav links, the avatar dropdown trigger), forms that don't comfortably fit/scroll on small screens, and the `NewScan` drag-and-drop zone's behavior on touch devices (drag-and-drop isn't really a mobile interaction pattern — confirm the click-to-browse fallback from Prompt 135 is the primary, well-presented interaction on mobile, not a visually secondary afterthought).
- Pay particular attention to the `History` table (Prompt 149) and any other tabular content — apply the same horizontal-scroll-or-card-layout decision made in Prompt 134 consistently here too.
- Document any page-specific responsive decisions worth noting in a brief `frontend/RESPONSIVE_NOTES.md` (optional, but useful if any non-obvious trade-offs were made).

**Acceptance Criteria:**
- [ ] Every page renders without horizontal overflow, broken layout, or illegibly small text/touch-targets at all three tested breakpoints.
- [ ] The `NewScan` page's mobile experience is confirmed good specifically as a click-to-browse-first experience, not solely relying on desktop drag-and-drop affordances.

**Must Not Break:** Must not alter existing page functionality/data-fetching logic — this is a styling/layout-only pass.

---

#### Prompt 164 — Consistent Empty/Loading/Error States Everywhere

**Do:** Add consistent empty/loading/error states across every data-driven page.

**Context & Why:** Prompts 132 (Dashboard) and 153 (History) already built dedicated loading/empty states for their specific pages — this prompt is the sweep confirming every OTHER data-fetching surface in the app (Profile's initial load if it ever fetches fresh data beyond the store, the Result page's fetch-by-id path, the About page's `GET /diseases` call) also has equivalent, visually-consistent treatment, rather than some pages feeling polished and others feeling unfinished.

**Requirements:**
- Audit every component/page that makes an API call (`Dashboard`, `NewScan`/`Analyzing`, `Result`, `History`, `Profile`, `About`) and confirm each has: a loading state (Prompt 116's `Spinner`, used consistently rather than each page inventing its own loading visual), a clear error state (reusing the established error-display pattern from Prompts 123/140/158) for failed requests, and — where applicable — a meaningful empty state (e.g. `About` if `GET /diseases` somehow returned zero items, which shouldn't normally happen given Prompt 67's seeding, but should still be handled gracefully rather than rendering a broken-looking blank section).
- Specifically confirm the `Result` page (Prompt 143) correctly handles the case where fetching a specific prediction `id` fails (e.g. the id doesn't exist, or belongs to another user and the backend correctly returns an error) — this page hasn't had explicit error-state treatment specified yet in Prompts 143–148, so ensure it's added now as part of this consistency sweep.

**Acceptance Criteria:**
- [ ] Every data-fetching page/component in the app has a visually consistent loading indicator, error message, and (where relevant) empty-state treatment, using the same shared components/patterns throughout.
- [ ] The `Result` page specifically now correctly handles a failed/invalid prediction-id fetch with a clear error rather than a blank or broken page.

**Must Not Break:** Must not alter the successful-path rendering of any page — this is additive coverage of previously-unhandled edge states.

---

#### Prompt 165 — Final Visual QA Pass

**Do:** Do a final visual QA pass against the design system (spacing, colors, typography) and fix inconsistencies.

**Context & Why:** This is the formal close of Phase 3, mirroring Phase 1's Prompt 55 and Phase 2's Prompt 110 — the last chance to catch visual drift (a button that forgot to use the `Button` component, a color that doesn't match the tokens from Prompt 113, inconsistent spacing between sections across different pages) before Phase 4's integration work treats the frontend as feature-complete.

**Requirements:**
- Systematically review every page against `frontend/src/DESIGN_TOKENS.md` (Prompt 113): confirm every color used traces back to a defined token (no stray arbitrary hex values introduced ad hoc in later prompts), confirm spacing between major page sections is consistent (e.g. the same vertical rhythm/padding scale used across Dashboard, History, Profile, etc.), confirm every button on every page actually uses the shared `Button` component (Prompt 114) rather than a raw unstyled `<button>` that may have crept in during rapid page-building.
- Confirm every loading/error/empty state (per Prompt 164's sweep) is not just functionally present but visually consistent in styling (same spinner, same error-banner look-and-feel) across every page.
- Fix any discovered inconsistencies directly; where a fix would be a larger undertaking than this pass's scope reasonably allows, document it as a known, explicitly-named issue (not silently left unaddressed) for a future pass.
- Make a final Phase 3 commit, e.g. `"feat: complete frontend (Phase 3) — auth, dashboard, scan flow, history, profile"`.

**Acceptance Criteria:**
- [ ] A full click-through of every page in the app shows visually consistent colors, spacing, typography, and shared-component usage, with no glaring one-off deviations.
- [ ] Any remaining known visual issue is explicitly documented, not silently present and unmentioned.
- [ ] Phase 3 is formally declared complete — Phase 4's full integration work (Section 4.A onward) may now begin, assuming Phase 2 is also complete.

**Must Not Break:** This is a polish/consistency pass — it must not alter any page's actual data-fetching logic or functional behavior established in Prompts 111–164; any functional bug discovered here should be fixed, but as a clearly-noted fix, not silently bundled into an ostensibly cosmetic-only commit.

---
## 6. PHASE 4 — Integration, Testing, Deployment & Docs

*Prompts 166–220*

This phase connects the three finished pieces into one live product, proves it works, hardens it, ships it, and prepares the written and spoken deliverables. Do not begin Section 4.A until both Phase 2 (Prompt 110) and Phase 3 (Prompt 165) are formally complete.

### 4.A Frontend-Backend Integration

#### Prompt 166 — End-to-End Signup Verification

**Do:** Wire the Signup page end-to-end against the live backend and verify a new user lands on a working dashboard.

**Context & Why:** Although Prompt 120 already implemented Signup against the real backend route during Phase 3, this prompt is the first prompt in the project where BOTH sides are guaranteed fully complete and frozen (per Prompts 110 and 165) — this is a deliberate, formal re-verification pass, not a redundant re-implementation, treating integration as its own distinct milestone worth explicitly testing rather than assuming it "already worked" from earlier incremental checks.

**Requirements:**
- Run both the backend (`uvicorn app.main:app`) and frontend (`npm run dev`) locally, pointed at each other via correct `.env`/`VITE_API_BASE_URL` configuration.
- Manually walk through: open the Signup page, fill in realistic test data, submit, confirm the browser navigates to `/dashboard`, confirm the dashboard shows the correct new user's name/greeting (Prompt 127) and correctly-empty stats/history (Prompts 129–130, 132).
- Open backend logs (per Prompt 102's request-logging middleware) during this walkthrough and confirm the expected sequence of requests appears (`POST /auth/register`, `GET /users/me`, `GET /users/me/stats`, `GET /predictions/history`), with no unexpected errors.
- Fix anything discovered broken during this manual walkthrough immediately — this is a verification prompt, but its job includes closing any gap it finds, not just reporting it.

**Acceptance Criteria:**
- [ ] A fresh, never-before-used email/signup completes the full flow described above with no errors, ending on a correctly-personalized, correctly-empty dashboard.
- [ ] Backend request logs confirm the expected real request sequence occurred.

**Must Not Break:** Must use the real, final Phase 2 and Phase 3 code — no mocks remaining from any earlier parallel-development shortcuts (per the library's stated parallel-work option) should still be in place by this point; remove any that are found.

---

#### Prompt 167 — End-to-End Login and JWT Persistence

**Do:** Wire the Login page end-to-end and verify JWT persistence across a page refresh.

**Context & Why:** This specifically tests Prompt 119's `persist` middleware behavior under real conditions — a correctly-implemented auth store should survive a full page reload without forcing the user to log in again, a basic but easy-to-get-wrong expectation for any authenticated web app.

**Requirements:**
- Log in as an existing test user (e.g. the one created in Prompt 166), confirm successful navigation to `/dashboard`.
- Perform a full hard browser refresh (not just an in-app navigation) on the dashboard, and confirm the user remains logged in (dashboard still renders correctly with the same user's data, not a redirect to `/login`).
- Confirm this also works correctly after closing and reopening the browser tab/window (testing `localStorage` persistence specifically, beyond just in-memory React state surviving a soft navigation).
- Confirm an expired token (can be tested by temporarily setting a very short `JWT_EXPIRY_MINUTES` in the backend's `.env` for this specific manual test) correctly results in subsequent API calls failing with 401 and the frontend correctly handling this by redirecting to `/login` (this reveals whether a global 401-handling interceptor is needed in `api.ts`, Prompt 118 — if not already present, add one now: any API response with a 401 status should trigger `authStore.logout()` and a redirect to `/login` automatically, rather than each individual page needing to handle this case separately).

**Acceptance Criteria:**
- [ ] Login persists correctly across a hard page refresh and across closing/reopening the browser.
- [ ] An expired token correctly results in automatic logout and redirect to `/login`, confirmed via the short-expiry manual test.

**Must Not Break:** Must use the real `authStore` (Prompt 119) and `api.ts` (Prompt 118) — if a global 401-handling addition is needed, add it to `api.ts` directly so it benefits every API call, not just a few specific ones patched individually.

---

#### Prompt 168 — End-to-End Scan Flow

**Do:** Wire the full scan flow end-to-end: upload → analyzing → result → saved to history.

**Context & Why:** This is the single most important integration test in the whole project — it exercises nearly every piece of the backend (Prompts 86–95) and frontend (Prompts 135–148) built across both phases, together, for the first time under fully real, fully-frozen conditions.

**Requirements:**
- Using a logged-in test user, walk through: select/upload a real sample leaf image on `/scan`, confirm the `Analyzing` state (Prompt 139) appears and correctly disappears once the real backend responds, confirm correct navigation to the Result page (Prompt 142) showing accurate crop/disease/confidence/symptoms data matching what the backend actually computed (cross-check against a direct `curl`/`.http`-file (Prompt 109) call to `/predict` with the same image, to confirm the frontend isn't somehow displaying stale/incorrect/mismatched data).
- Immediately after, navigate to `/history` and confirm the just-completed scan appears correctly at the top of the list (most recent first), and navigate to `/dashboard` and confirm its stats/recent-scans correctly reflect this new scan too.
- Test with at least one image per represented crop category (not just one single test image) to build broader confidence the whole pipeline works across the model's actual class range, not just one lucky case.

**Acceptance Criteria:**
- [ ] The full upload → analyzing → result → history → dashboard-reflects-it chain works correctly and consistently across multiple different real test images.
- [ ] Data shown on the Result page is confirmed accurate against a direct backend API call for the same image, not just "looks plausible."

**Must Not Break:** This is the integration test of record for the entire core feature — any bug found here takes priority to fix before proceeding further in Phase 4.

---

#### Prompt 169 — Verify Immediate Dashboard Updates

**Do:** Verify the dashboard stats and recent-scans update immediately after a new scan.

**Context & Why:** A subtle but important UX correctness check building on Prompt 168 — confirms there's no stale-cache problem where the dashboard shows outdated numbers until a manual refresh, which would undermine user trust in the app's accuracy.

**Requirements:**
- Specifically test the navigation path: complete a scan (per Prompt 168), then click through to `/dashboard` via normal in-app navigation (not a hard browser refresh) — confirm the stats cards (Prompt 129) and recent-scans table (Prompt 130) reflect the just-completed scan immediately, without requiring a manual page reload.
- If this reveals a stale-data bug (e.g. the dashboard's data was fetched once on an earlier mount and never refetched), fix it — likely by ensuring the relevant `useEffect`/data-fetching logic correctly re-runs on every mount of the Dashboard component (which should already happen naturally with standard React Router navigation unmounting/remounting the page component, unless some overly-aggressive memoization was introduced somewhere) rather than only once per full app session.

**Acceptance Criteria:**
- [ ] Navigating to the dashboard via in-app navigation immediately after a scan shows fully up-to-date stats and recent-scans data, with no manual refresh needed.

**Must Not Break:** Must not introduce excessive/wasteful re-fetching either (e.g. don't fetch on every single render) — the fix should be "correctly fetch fresh data on each genuine navigation to this page," not "fetch constantly."

---

#### Prompt 170 — Verify History Pagination/Filtering Against Real Data

**Do:** Verify the History page correctly paginates and filters against real backend data.

**Context & Why:** Prompts 149–151 were built and unit-level-manually-tested during Phase 3, but this prompt specifically re-verifies them against a realistically-sized, real dataset (more than one page's worth of real predictions) — something easy to under-test during initial feature development when only a handful of test predictions typically exist.

**Requirements:**
- Generate enough real test prediction history for one test user (e.g. by scripting multiple `/predict` calls via the `.http` file from Prompt 109, or by manually performing enough scans through the UI) to exceed one page size (per Prompt 149's chosen `page_size`), covering a mix of different crops/diseases/confidence levels.
- Verify pagination controls correctly move between pages with accurate data on each page and correct `total`/`total_pages` reflected in the UI.
- Verify each filter (crop, disease, Prompt 150) and each sort option (date, confidence, Prompt 151) produces results that are independently verifiable as correct against the real underlying data (e.g. manually count how many of this user's real predictions are "Tomato" and confirm the filtered view shows exactly that many).

**Acceptance Criteria:**
- [ ] Pagination, filtering, and sorting all independently and correctly reflect a realistically-sized real dataset, each verified against a manual ground-truth count/check.

**Must Not Break:** Must not require any change to the already-built History page logic unless a genuine bug is discovered during this more thorough testing — if no bug is found, this prompt's output is simply confirmed verification.

---

#### Prompt 171 — Verify Profile Edit Propagates to Navbar

**Do:** Verify the Profile edit flow persists changes and reflects them immediately in the navbar avatar/name.

**Context & Why:** Specifically tests that `authStore`'s `setUser()` action (Prompt 119), used by both the Profile edit form (Prompt 155) and photo upload (Prompt 156), correctly propagates to every other component reading from the same store — in this case, the `Navbar`'s avatar (Prompt 160), which should update in real time without requiring a page refresh or re-login.

**Requirements:**
- Edit the profile name and/or upload a new photo, save, and without refreshing the page, confirm the navbar's avatar/display immediately reflects the change (relying on Zustand's reactive subscription model working correctly, since both the Profile page and Navbar read from the same shared store).
- If this reveals a propagation bug (e.g. the navbar reads from a stale local copy rather than subscribing live to the store), fix it directly in the `Navbar` component to correctly subscribe to live `authStore` state.

**Acceptance Criteria:**
- [ ] A name change and/or photo upload on the Profile page is immediately visible in the navbar with no refresh required.

**Must Not Break:** Must not require a backend change — this is purely a frontend state-propagation verification/fix.

---

#### Prompt 172 — Verify Cross-User Data Isolation (Frontend)

**Do:** Verify that logging in as a second test user shows a completely separate dashboard/history (no data leakage between accounts).

**Context & Why:** This is the frontend/full-stack, manually-verified counterpart to the backend-only automated tests already covering this exact concern (Prompt 80's isolation check, Prompt 98's history-scoping, Prompt 172 being explicitly named in Prompts 63/80/84/98's own "Context & Why" sections as the eventual real-world confirmation of that design principle) — critical enough to deserve this dedicated, explicit, full end-to-end manual (or scripted) re-verification.

**Requirements:**
- Create a second, genuinely distinct test user (different email) via Signup, perform a few scans as this user, then log out and log back in as the original test user from Prompts 166–170.
- Confirm the original user's dashboard, stats, and history show ONLY their own data — zero visibility into the second user's scans, name, email, photo, or any other data, under any page or feature in the app.
- Repeat the check in the other direction (log in as the second user, confirm no visibility into the first user's data).
- This check should cover every page built in Phase 3, not just Dashboard/History — confirm Profile correctly shows only the currently-logged-in user's own profile data as well.

**Acceptance Criteria:**
- [ ] Exhaustive manual (or scripted) cross-checking confirms zero data leakage between the two distinct test accounts across every page of the app.

**Must Not Break:** If any leakage is found, this is a critical, high-priority bug — fix immediately before proceeding further in Phase 4, regardless of what other prompts might otherwise come next in sequence.

---

#### Prompt 173 — Fix API-Contract Mismatches

**Do:** Fix any API-contract mismatches discovered during integration (field naming, date formats, error shapes).

**Context & Why:** This prompt exists to formally close out any small discrepancies accumulated across Prompts 166–172's integration testing — a deliberate cleanup checkpoint rather than letting such fixes scatter ad hoc across other prompts' scopes.

**Requirements:**
- Review every discrepancy noted (even informally) during Prompts 166–172's testing — field name mismatches between what the backend sends and what the frontend expects, date format inconsistencies (confirm the backend consistently sends ISO-8601 timestamps per the Global Conventions, and the frontend consistently parses/formats them the same way everywhere per the convention established in Prompt 130), and error response shape mismatches (confirm the frontend's error-handling code, per Prompt 118, correctly expects the real `{"detail": ..., "error_code": ...}` shape from Prompt 101's global exception handlers in every case, not just the specific error shapes individually tested in earlier prompts).
- Fix each discovered mismatch at its root (correct the backend schema, or correct the frontend's consumption of it — whichever is the more correct/consistent fix given the project's established conventions) rather than patching around it with ad hoc frontend-side data transformation that masks an underlying inconsistency.
- Document every fix made in a short integration-notes section (can live in `docs/ARCHITECTURE.md`, to be properly written in Prompt 208, or as a temporary `docs/INTEGRATION_FIXES.md` note for now) so the final documentation accurately reflects the as-built, truly-integrated system rather than its earlier, now-corrected design.

**Acceptance Criteria:**
- [ ] Every mismatch identified during Prompts 166–172 is resolved, with the fix applied at the correct (root-cause) layer.
- [ ] Re-running the relevant Prompt 166–172 verification steps confirms the fix actually resolved the issue without introducing a new one.

**Must Not Break:** Must re-verify (not just assume) that fixing one mismatch doesn't break a previously-passing backend test (Prompts 76/85/95/100) or frontend behavior — re-run the backend test suite after any backend-side schema change made here.

---

#### Prompt 174 — Global Frontend Error Boundaries

**Do:** Add global frontend error boundaries and a friendly fallback UI for unexpected failures.

**Context & Why:** Everything built so far handles *expected* error cases (failed API calls, validation errors) gracefully — but a genuinely unexpected JavaScript runtime error (a bug) in any component would otherwise crash the entire React app to a blank white screen; a top-level error boundary prevents that worst-case experience.

**Requirements:**
- Implement a React class-based `ErrorBoundary` component (error boundaries currently require the class component lifecycle methods `componentDidCatch`/`getDerivedStateFromError` — functional-component error boundaries aren't yet a standard React pattern, so this is a deliberate, documented exception to the project's otherwise functional-components-only convention from the Global Conventions) wrapping the entire app (around the router, in `App.tsx` or `main.tsx`).
- On catching an error, render a friendly fallback UI ("Something went wrong. Please refresh the page or try again later.") with a button to reload the app, rather than a blank screen — and log the caught error (e.g. to the browser console at minimum; consider whether a more robust error-reporting service is in scope — likely not for this build, but note it as a future consideration) for debugging purposes.
- Confirm this boundary does NOT swallow/hide the specific, already-well-handled error states built in earlier prompts (failed API calls, validation errors) — it should only catch genuinely unexpected rendering/runtime errors that would otherwise crash the whole app, not replace the existing, more specific and more helpful per-page error handling.

**Acceptance Criteria:**
- [ ] A deliberately-introduced test bug (e.g. a temporary `throw new Error("test")` inside some component) is caught by the boundary and shows the friendly fallback UI instead of a blank crashed page.
- [ ] Normal, already-handled error states (failed login, failed prediction) continue to work exactly as before, unaffected by this new top-level boundary.

**Must Not Break:** Must not interfere with any existing error-handling logic from Prompts 123/140/158/164 — this is an additional, outermost safety net, not a replacement for those more specific, more helpful error states.

---

#### Prompt 175 — Environment-Based API Base URL Configuration

**Do:** Add environment-based API base URL configuration (`.env` for local vs. production).

**Context & Why:** Prompt 118 already read the API base URL from an environment variable from the start, anticipating this exact need — this prompt is the formal confirmation/completion of that setup specifically for the local-vs-production split, ahead of Prompt 201's production deployment configuration.

**Requirements:**
- Confirm `frontend/.env` (local development) sets `VITE_API_BASE_URL=http://localhost:8000` and create a `frontend/.env.example` (mirroring the backend's pattern from Prompt 59) documenting this and any other frontend environment variables introduced along the way (e.g. `VITE_MAX_UPLOAD_SIZE_MB` from Prompt 137).
- Confirm Vite's built-in environment-mode support (`.env.development`, `.env.production`) is understood and will be used correctly in Prompt 201 — this prompt doesn't yet need the real production URL (which doesn't exist until Prompt 197), but should ensure the mechanism is fully ready and correctly structured to receive it.
- Add `frontend/.env` (the real, local one, as opposed to `.env.example`) to the root `.gitignore` if not already covered by Prompt 5's wildcard rules — confirm explicitly.

**Acceptance Criteria:**
- [ ] The frontend correctly reads its API base URL from environment configuration, confirmed by temporarily changing the value and observing requests go to the new address.
- [ ] `frontend/.env.example` exists, documenting every frontend environment variable in use as of this point in the project.

**Must Not Break:** Must not hardcode the API base URL anywhere in the frontend codebase outside of this environment-variable mechanism — grep the codebase to confirm no stray hardcoded `localhost:8000` references exist elsewhere.

---
### 4.B End-to-End Testing

#### Prompt 176 — Core E2E Test: Signup → Login → Scan → Result → Logout

**Do:** Write an end-to-end test script (Playwright or Cypress) covering: signup → login → scan → view result → logout.

**Context & Why:** Everything in Section 4.A was manually verified — this prompt converts the single most important of those manual walkthroughs (essentially Prompts 166+168+126 combined) into a permanent, automated, repeatable test that can be re-run after any future change to catch regressions, rather than relying on manual re-testing forever.

**Requirements:**
- Choose one framework (Playwright is generally recommended for modern projects — faster, better debugging tools, built-in test runner — but Cypress is equally acceptable; pick one and use it consistently for all of Prompts 176–179) and set it up in a new `frontend/e2e/` folder (or `frontend/tests/e2e/`, documented clearly) with its own `package.json` dependency and config.
- Write a test that, against a running local instance of both backend and frontend (document how to start both before running e2e tests, likely in a new `frontend/e2e/README.md` or added to the main `docs/TESTING_REPORT.md`, Prompt 183): registers a brand-new, uniquely-generated test user (e.g. using a timestamp or random string in the email to avoid collision with prior test runs), logs in (or confirms already-logged-in from registration, per Prompt 125's auto-login behavior — adjust the test accordingly), uploads a real sample test image on `/scan`, waits for and confirms the Result page renders with real prediction data, then logs out and confirms redirect to `/login`.
- Use the testing framework's real browser automation (not mocked network requests) so this genuinely exercises the full, real stack end-to-end, including actual model inference.

**Acceptance Criteria:**
- [ ] The test passes reliably (not flaky) when run against a correctly-running local backend+frontend.
- [ ] The test uses a genuinely unique test user each run (no collision with previous runs' leftover data).
- [ ] Instructions for running this test exist and are accurate.

**Must Not Break:** Must test the real, running application — not a simplified/mocked stand-in.

---

#### Prompt 177 — E2E Test: Uncertain Result Path

**Do:** Write an end-to-end test covering the "uncertain result" path using a deliberately ambiguous test image.

**Context & Why:** This specifically exercises the safety-relevant UI behavior from Prompt 146 under genuine end-to-end conditions — confirming the warning banner actually appears correctly when the real backend genuinely returns `is_confident: false`, not just in the isolated unit-level testing already done in Prompt 95.

**Requirements:**
- Identify or construct a genuinely ambiguous test image reliably triggering a low-confidence prediction from the real model (this may require some experimentation — e.g. a heavily cropped/blurred/oddly-lit sample image, or one from an edge case discovered during Prompt 49's error analysis) — if no naturally-occurring image reliably triggers this, as a documented fallback, the test may temporarily lower `CONFIDENCE_THRESHOLD` via test-specific backend configuration to make a normally-confident image register as "uncertain" for testing purposes, clearly noting this is a test-environment-only configuration adjustment.
- Run the same upload → result flow as Prompt 176, but specifically assert that the uncertain-result warning banner (Prompt 146) is visible on the Result page for this test case.

**Acceptance Criteria:**
- [ ] The test reliably and reproducibly triggers and verifies the uncertain-result UI state.
- [ ] The method used to achieve a reliably-low-confidence test case is clearly documented in the test file's comments.

**Must Not Break:** Must not require a permanent change to the real production `CONFIDENCE_THRESHOLD` configuration — any threshold adjustment used to make this test reliable must be scoped specifically to the test environment/run, never affecting real production behavior.

---

#### Prompt 178 — E2E Test: Protected Route Redirects

**Do:** Write an end-to-end test verifying protected routes redirect unauthenticated users to `/login`.

**Context & Why:** The direct automated proof of Prompt 124's `ProtectedRoute` behavior under real browser conditions.

**Requirements:**
- Starting from a genuinely logged-out browser state (no stored token — e.g. clear cookies/localStorage at the start of the test, or use the testing framework's isolated-context feature), attempt to navigate directly to each protected route (`/dashboard`, `/scan`, `/history`, `/profile`) one at a time, and assert the browser ends up redirected to `/login` in every case.
- Also test the inverse: while genuinely logged in, confirm these same routes render their real content rather than redirecting.

**Acceptance Criteria:**
- [ ] All four protected routes correctly redirect when accessed while logged out.
- [ ] All four correctly render their real content when accessed while logged in.

**Must Not Break:** Must test the real `ProtectedRoute` component (Prompt 124) under genuine browser navigation, not a simulated/mocked routing check.

---

#### Prompt 179 — E2E Test: Cross-Account Data Isolation

**Do:** Write an end-to-end test verifying user data isolation between two different accounts.

**Context & Why:** Converts Prompt 172's manual verification into a permanent automated regression test — given how critical this property is, it deserves a lasting automated guard, not just a one-time manual check that could silently regress later without anyone noticing.

**Requirements:**
- Register two distinct, uniquely-generated test users within the test; as User A, perform a scan; as User B (after logging out of A and logging into B, or using two separate isolated browser contexts if the testing framework supports running them concurrently — Playwright's multiple-browser-context feature is well suited to this), confirm User B's dashboard/history show zero trace of User A's scan, and vice versa after a symmetric check.

**Acceptance Criteria:**
- [ ] The test reliably and repeatedly confirms zero cross-account data leakage, using genuinely distinct, dynamically-created test accounts each run.

**Must Not Break:** Must exercise the real, running application exactly as Prompt 172's manual check did, just now automated and permanent.

---

#### Prompt 180 — Run and Fix the Full Backend Test Suite

**Do:** Run the full backend test suite (`pytest`) and fix any failing tests.

**Context & Why:** Given how much backend-adjacent context has changed since Prompt 110's original "all tests pass" checkpoint (Prompt 173's contract-mismatch fixes especially), this is a deliberate re-verification that the entire Phase 2 test suite (Prompts 76, 85, 95, 100, consolidated via 105, measured via 106) still fully passes after all of Phase 4's integration work so far.

**Requirements:**
- Run `pytest backend/tests/ --cov=app` and review both the pass/fail results and the coverage report (Prompt 106).
- Investigate and fix any failure found — given the project's maturity at this point, a failure here likely indicates either a genuine regression introduced during Prompt 173's fixes, or a test that was already subtly wrong and is only now being caught; determine which for each failure and fix at the correct root cause (fix the code if the test was correctly catching a real regression, or fix the test if it was testing outdated/incorrect expected behavior — document which was which).

**Acceptance Criteria:**
- [ ] `pytest backend/tests/` reports 100% pass with no failures or errors.
- [ ] Any fix made is clearly understood and documented as either "fixed a regression" or "corrected an outdated test," not left ambiguous.

**Must Not Break:** Must not "fix" a failing test by weakening its assertion to match incorrect behavior — a failing test should only be changed if its original expectation was genuinely wrong, never to paper over a real bug.

---

#### Prompt 181 — Manual Mobile Device QA

**Do:** Perform manual QA on real mobile devices (Android and iOS browsers) for the upload flow.

**Context & Why:** Prompt 163's responsive pass was done via browser dev-tools device emulation — real devices can reveal issues emulation misses entirely (actual camera-roll/file-picker UI differences, actual touch behavior, real mobile network conditions, real viewport quirks across different OS browser engines).

**Requirements:**
- Test the core scan flow (upload picker, image selection from an actual phone's photo library, submission, result viewing) on at least one real Android device (Chrome) and one real iOS device (Safari) — if genuinely unavailable, browser-based device-specific testing tools (e.g. BrowserStack or similar) are an acceptable documented substitute, but note this limitation explicitly if used.
- Specifically verify: the native file-picker/camera-roll integration behaves sensibly on both platforms, touch targets are comfortably tappable, the page doesn't suffer from unexpected zoom/scroll behavior, and performance (feel of responsiveness, not just raw load time) is acceptable on a real mobile data connection, not just a fast office/home WiFi connection.
- Document findings (what was tested, on which real devices/OS versions, and any issues found and fixed) in `docs/TESTING_REPORT.md` (Prompt 183).

**Acceptance Criteria:**
- [ ] The core scan flow is confirmed to work acceptably on at least one real Android and one real iOS device (or documented equivalent).
- [ ] Any device-specific issue found is fixed or explicitly documented as a known limitation.

**Must Not Break:** Any fix made for mobile-specific behavior must be re-verified not to break the already-tested desktop experience (Prompt 165).

---

#### Prompt 182 — Load Test `/predict`

**Do:** Load-test the `/predict` endpoint with concurrent requests to confirm the model-loading singleton performs acceptably.

**Context & Why:** This is the direct, practical test of whether Prompt 86's singleton model-loading pattern actually delivers the performance benefit it was designed for under realistic concurrent load, rather than remaining a theoretical assumption.

**Requirements:**
- Use a load-testing tool (e.g. `locust`, `k6`, or even a simple custom Python `asyncio`/`concurrent.futures` script making many concurrent requests — pick whichever the team is comfortable setting up quickly) to send a realistic number of concurrent `/predict` requests (e.g. 10, 25, 50 concurrent users, each submitting a real test image) against a locally-running backend instance.
- Measure and record: average/median/p95 response time per request, error rate (if any requests fail/time out under load), and whether memory usage grows unboundedly across the test (which would suggest a resource leak somewhere in the inference path, worth investigating further if observed).
- Confirm the TensorFlow model itself handles concurrent `predict()` calls safely (TensorFlow/Keras models are generally safe for concurrent inference calls from multiple threads/async contexts within one process, but verify this holds true in practice for this specific setup rather than assuming it).

**Acceptance Criteria:**
- [ ] Load test results (response times, error rate) are recorded and show acceptable behavior under the tested concurrency levels (no crashes, no unbounded memory growth, response times remaining within a reasonable range — define "reasonable" relative to the single-request baseline established informally in Prompt 190's upcoming profiling work, or set a simple target now, e.g. "p95 under 3 seconds at 25 concurrent users," adjusted based on real observed single-request latency).
- [ ] Findings are documented in `docs/TESTING_REPORT.md` (Prompt 183) and feed into Prompt 190's performance-optimization decisions if any bottleneck is identified here.

**Must Not Break:** This is a read-only testing activity against the existing implementation — if a genuine bottleneck/bug is found, flag it for Prompt 190/191's performance-pass scope rather than attempting an uncoordinated fix here.

---

#### Prompt 183 — Document All Test Results

**Do:** Document all test results and known issues in `docs/TESTING_REPORT.md`.

**Context & Why:** Consolidates everything tested across Prompts 166–182 (backend unit/integration tests, e2e tests, manual mobile QA, load testing) into one comprehensive, submittable testing report — directly useful for the final project report and for anyone (including a viva examiner) wanting to understand how thoroughly the system was actually verified.

**Requirements:**
- Sections: "Backend Test Suite" (link/summarize `backend/TESTING.md` from Prompt 106, restate final pass rate/coverage), "End-to-End Tests" (list each e2e test from Prompts 176–179, what it covers, confirm all passing), "Manual Mobile QA" (Prompt 181's findings), "Load Testing" (Prompt 182's results), "Known Issues" (an honest, explicit list of anything discovered during Phase 4 testing that was NOT fully resolved, with a brief note on severity/planned handling — this section's honesty is more valuable to the project's credibility than pretending everything is perfect).
- Include exact commands for re-running every category of test described, so this document doubles as a practical "how to verify this project still works" reference for anyone picking it up later.

**Acceptance Criteria:**
- [ ] Every test category from Prompts 166–182 is accurately represented with real results, not placeholder/aspirational claims.
- [ ] The "Known Issues" section is honest and complete, not empty by default assumption.

**Must Not Break:** Must accurately reflect the real, current state of testing as of this point — update it again later if Phase 4's remaining prompts (security/performance/deployment) surface anything new worth recording here.

---
### 4.C Security Hardening

#### Prompt 184 — Audit for Client-Supplied Identity

**Do:** Audit all protected routes to confirm none rely on client-supplied user IDs instead of the JWT-derived identity.

**Context & Why:** This is the formal, explicit verification of the single most important security rule stated in this entire library's Global Conventions — stated as a design intention since Prompt 60/74, this prompt is where the team actually proves it was followed everywhere, not just where it was consciously top-of-mind while writing each individual route.

**Requirements:**
- Grep the entire `backend/app/routes/` directory for every occurrence of `user_id` to confirm it is NEVER read from a request body field, query parameter, or path parameter in any route handler — every single usage should trace back to `current_user.id` (from `get_current_user`, Prompt 74).
- Specifically re-verify: `POST /predict` (Prompt 92, writes `user_id`), `GET /predictions/history` (Prompt 98, filters by `user_id`), `POST /predictions/{id}/feedback` (Prompt 99, writes `user_id` AND checks prediction ownership), `GET/PUT /users/me` and `/users/me/stats` (Prompts 80/81/84, all implicitly scoped via `current_user`).
- If any violation is found (a route accepting a client-supplied `user_id` anywhere), this is a critical severity fix — correct it immediately to derive identity only from `current_user`.

**Acceptance Criteria:**
- [ ] A full grep/code-review audit confirms zero instances of `user_id` sourced from anywhere other than `current_user.id` across the entire route layer.
- [ ] Any violation found is fixed and re-verified via the relevant existing test (Prompts 76/85/95/100) or a new test added specifically to catch this category of bug going forward.

**Must Not Break:** Must not change any already-correct route's behavior — this audit should find zero issues if Prompts 72–99 were implemented exactly as specified; treat any finding as a genuine regression to fix, not an expected outcome.

---

#### Prompt 185 — Confirm Password Hashes Never Leak

**Do:** Confirm password hashes are never included in any API response, log line, or error message.

**Context & Why:** A second explicit, formal audit of another critical security property stated since Prompt 71 — `UserOut`/`UserProfileOut` were designed from the start to exclude `password_hash`, but this prompt verifies that design intention held true across every response path, including error cases that might bypass the normal schema-based serialization.

**Requirements:**
- Review every response model (`UserOut`, `UserProfileOut`, and any other schema that serializes from a `User` ORM object) to confirm `password_hash` is never a field on any of them (already true per Prompts 71/79's design, but re-verify explicitly rather than assuming).
- Review Prompt 102's request-logging middleware and Prompt 101's exception handlers to confirm neither ever logs a full request body (which could contain a plaintext password from `/auth/register`/`/auth/login`) or a full `User` object (which could expose `password_hash` if naively `str()`-ed or logged directly) — confirm logging is limited strictly to the metadata already specified (method, path, status, timing) with no broader object dumping anywhere.
- Write a small, permanent automated test confirming a raw `/auth/register` or `/users/me` response, inspected as raw JSON, never contains the string `"password_hash"` or anything resembling a bcrypt hash pattern (`$2b$...`) as a defense-in-depth automated check, not just a one-time manual review.

**Acceptance Criteria:**
- [ ] Manual review confirms no response schema or log statement anywhere in the codebase could expose `password_hash` or a raw plaintext password.
- [ ] The new automated test passes and would catch a future regression if someone accidentally added `password_hash` to a response schema later.

**Must Not Break:** Must not change any legitimate response field — only remove/prevent genuine password-hash exposure if found (which, per Prompts 71/79's careful original design, should ideally be none).

---

#### Prompt 186 — Secure Token Storage Configuration

**Do:** Add HTTPS-only cookie flags / secure token storage configuration for production.

**Context & Why:** The current implementation (per Prompt 119) stores the JWT in `localStorage`, which is simple and already works correctly for the app's needs but carries a well-known XSS-related risk profile (a successful XSS attack could read `localStorage` directly) — this prompt is where the team makes a deliberate, documented decision about whether to accept this risk as-is for the project's scope, or harden it further for production.

**Requirements:**
- Document the trade-off explicitly: `localStorage` (current approach) is simple but vulnerable to XSS-based token theft; an `httpOnly` secure cookie (requiring backend changes to set/read the cookie rather than the frontend managing a bearer token directly, and corresponding CSRF-protection considerations since cookies are automatically sent by the browser) is more secure against XSS but adds meaningful complexity.
- Given this is a student/academic project with a defined scope, a reasonable, defensible decision is to: **keep `localStorage` for this build**, but explicitly ensure production deployment serves the app exclusively over HTTPS (relevant again in Prompt 203) so at minimum the token is never transmitted in plaintext over the network, and document this as a known, deliberate, explained trade-off in `docs/SECURITY.md` (Prompt 189) rather than silently leaving it unaddressed — this honest trade-off documentation is itself a legitimate, defensible security-engineering decision, and a good answer if raised in the viva (Prompt 217).
- If the team has time/interest in implementing the more secure `httpOnly` cookie approach instead, that is also acceptable — but it is a larger, more invasive change (affecting `create_access_token`/route cookie-setting on the backend, Prompt 118's token-attachment logic on the frontend, and CORS/CSRF configuration) and should only be undertaken as a deliberate, fully-reasoned-through decision, not a rushed partial implementation.

**Acceptance Criteria:**
- [ ] A clear, explicit decision is made and documented (continue with `localStorage` + HTTPS-only deployment, or migrate to `httpOnly` cookies) — "we didn't think about it" is not an acceptable outcome of this prompt; an explicit, reasoned decision is required either way.
- [ ] Whichever approach is chosen is confirmed actually correctly implemented end-to-end (if migrating to cookies, confirm the full flow genuinely still works after the change, re-running Prompts 166–172's integration checks).

**Must Not Break:** If the `localStorage` approach is kept (the simpler, likely choice given project scope), nothing changes functionally — this prompt's main deliverable is the documented decision itself. If migrating to cookies, must not break any already-passing auth flow — re-verify thoroughly.

---

#### Prompt 187 — Production-Grade Rate Limiting

**Do:** Add basic rate-limiting to `/auth/login` and `/predict` to reduce abuse risk.

**Context & Why:** This is the explicit, planned follow-up to Prompt 78's intentionally-basic, single-process, in-memory rate limiter — this prompt either hardens that same mechanism for `/auth/login` with awareness of its documented limitations, and extends equivalent protection to `/predict` (which, being a compute-expensive ML-inference endpoint, is an even more attractive target for abuse/cost-exhaustion attacks than login itself).

**Requirements:**
- For `/auth/login`: if the project's deployment remains single-process (a reasonable assumption for this project's scope, confirmed by checking Prompt 197's actual deployment plan), the existing Prompt 78 in-memory approach may be retained as-is, with its known limitation re-confirmed and explicitly accepted/documented (rather than necessarily requiring a full Redis-backed distributed rate limiter, which may be disproportionate engineering effort for this project's actual deployment scale) — or implement the more robust version if time/interest allows; document whichever decision is made.
- For `/predict`: add a separate rate limit (e.g. max N predictions per user per minute/hour, using the same mechanism/pattern as Prompt 78) to prevent a single compromised or malicious account from exhausting server compute resources via rapid repeated inference requests — this limit should be generous enough not to interfere with genuine normal use (a real user scanning several plants in one sitting) while still meaningfully capping abuse.
- Both limits should return a clear `429 Too Many Requests` response with a `Retry-After`-style hint if practical.

**Acceptance Criteria:**
- [ ] `/predict` has a working rate limit that blocks rapid-fire abuse while allowing a reasonable number of genuine sequential real-world scans without friction.
- [ ] The `/auth/login` rate limiter from Prompt 78 is re-confirmed working and its known limitations (if retained as-is) are explicitly documented, not silently assumed sufficient without comment.

**Must Not Break:** Must not block legitimate normal usage patterns — test with a realistic sequence of genuine scans to confirm the `/predict` limit's threshold is sensibly calibrated, not overly aggressive.

---

#### Prompt 188 — File-Upload Security Review

**Do:** Review file-upload handling for path-traversal and malicious-file risks.

**Context & Why:** Both profile-photo upload (Prompt 82) and prediction-image upload (Prompt 93) already followed the "never use the client-supplied filename, always generate one" precaution from the start — this prompt is the formal, explicit security review confirming that precaution (and others) actually holds everywhere file uploads occur in the codebase.

**Requirements:**
- Re-verify both upload paths (Prompts 82, 93) never use any part of the client-supplied original filename in constructing the stored file's path — confirm the generated-UUID-based naming pattern is genuinely used in both places, not just one.
- Confirm uploaded file content type is validated based on actual inspection where practical (e.g. using a library like `python-magic` to sniff real file content/magic-bytes, rather than trusting only the client-supplied `Content-Type` header or file extension, both of which can be trivially spoofed by a malicious client) — if this deeper content-sniffing wasn't already implemented in Prompts 82/89, add it now as a hardening improvement, since trusting only the client-asserted content type is a known, real vulnerability class (e.g. a malicious executable renamed with a `.jpg` extension and a spoofed content-type header).
- Confirm the storage directory for uploads (`backend/uploads/...`, per the local-storage pattern chosen in Prompt 82) is not directly web-servable in a way that could execute uploaded content (e.g. confirm it's served purely as static file content, never passed through any code-execution path, and ideally sits outside any directory that could be misconfigured to execute scripts).

**Acceptance Criteria:**
- [ ] Both upload paths are re-confirmed to never use client-supplied filenames.
- [ ] Content-type validation is confirmed to inspect actual file content/magic-bytes, not solely the client-asserted header/extension (added now if this gap is found).
- [ ] The upload storage location is confirmed safe from any code-execution risk.

**Must Not Break:** Must not break legitimate valid image uploads while adding stricter content validation — test with a range of genuinely valid JPEG/PNG/WEBP files to confirm the stricter check still accepts them correctly.

---

#### Prompt 189 — Security Documentation

**Do:** Document the security measures taken in `docs/SECURITY.md`.

**Context & Why:** Consolidates every security-relevant decision and safeguard built across the entire project (Prompts 69–78, 184–188, and relevant earlier design decisions like Prompt 73's email-enumeration prevention) into one authoritative document — directly useful for the final project report's methodology/implementation section and for confidently answering security-related viva questions (Prompt 217).

**Requirements:**
- Sections covering, at minimum: password handling (bcrypt hashing, never storing/logging plaintext, Prompts 69/185), authentication (JWT design, expiry, the deliberate login-error-message ambiguity from Prompt 73), authorization (the JWT-derived-identity-only principle re-verified in Prompt 184), rate limiting (Prompts 78/187, including honest discussion of the in-memory approach's known limitations), file-upload safety (Prompt 188's path-traversal and content-sniffing protections), token storage trade-offs (Prompt 186's documented decision), and CORS configuration (Prompt 103).
- Write this document to genuinely stand up to scrutiny — an honest, specific account of what was done and why, including known limitations and their justifications (e.g. "we accepted X limitation given Y scope/constraint, and would address it via Z in a production deployment beyond this project's scope"), rather than a vague, unconvincing claim of "the app is secure."

**Acceptance Criteria:**
- [ ] Every security measure actually implemented across Prompts 69–78 and 184–188 is accurately documented with specific, correct technical detail (not generic security-checklist boilerplate).
- [ ] Known limitations/trade-offs are honestly stated, with reasoning, not hidden.

**Must Not Break:** Must accurately reflect the real, final state of the security-relevant code — do not describe an aspirational security posture the actual implementation doesn't match.

---
### 4.D Performance Pass

#### Prompt 190 — Profile and Optimize `/predict` Latency

**Do:** Profile the `/predict` endpoint latency and optimize preprocessing/inference if it exceeds an acceptable response-time budget.

**Context & Why:** Builds directly on Prompt 182's load-test findings and Prompt 40's already-measured per-model inference time — this prompt establishes whether real single-request latency (not just under concurrent load) is acceptable for a responsive user experience, and investigates/fixes the bottleneck if not.

**Requirements:**
- Instrument `/predict` with precise timing breakdown (e.g. using Python's `time.perf_counter()` around each major step: file read, preprocessing, model inference, database write) logged at `DEBUG` level (distinct from Prompt 102's standard `INFO`-level request logging, so this detailed breakdown doesn't clutter normal logs) — run several real requests and record where time is actually spent.
- Define an acceptable response-time budget (e.g. "under 2 seconds end-to-end for a single request on the target deployment hardware" — set a concrete number, informed by Prompt 40's known model inference time plus reasonable overhead) and compare real measurements against it.
- If a bottleneck is found: common culprits and fixes include image preprocessing being unnecessarily slow (e.g. an inefficient resize method — unlikely given Prompt 16's already-reasonable PIL-based approach, but verify), the model itself being slower than expected on the actual deployment hardware (in which case revisit whether MobileNetV2 remains the right choice given Prompt 41's original trade-off analysis, or whether model quantization/optimization — e.g. TensorFlow Lite conversion — is worth considering, noting this would be a significant additional scope item, likely only pursued if genuinely necessary), or unnecessary synchronous blocking elsewhere in the request path.
- Document findings and any optimization made in `docs/PERFORMANCE.md` (Prompt 194).

**Acceptance Criteria:**
- [ ] Real, measured per-step latency breakdown is recorded for `/predict`.
- [ ] If the defined budget was exceeded, a concrete optimization was investigated and either successfully applied (with before/after numbers) or explicitly documented as accepted/out-of-scope with reasoning.

**Must Not Break:** Any optimization applied must be re-verified against the existing test suite (Prompt 95) and integration tests (Prompt 168) to confirm correctness wasn't sacrificed for speed (e.g. confirm predictions remain numerically consistent before/after any preprocessing optimization).

---

#### Prompt 191 — Response Caching for Reference Data

**Do:** Add response caching where appropriate (e.g. `/diseases` reference data).

**Context & Why:** `GET /diseases` (Prompt 96) returns genuinely static reference data (the 8 seeded disease records rarely if ever change after Prompt 67's initial seeding) — repeatedly querying the database for identical, unchanging data on every single request is unnecessary overhead easily eliminated with simple caching.

**Requirements:**
- Add a simple in-memory cache (e.g. `functools.lru_cache` on a wrapper function, or a simple module-level variable populated on first request and reused thereafter, with a documented cache-invalidation story — e.g. "cache is cleared/refreshed only on app restart, which is acceptable since disease data is only ever changed via the seed script, which itself only runs during deployment/maintenance, not during normal operation") for `GET /diseases` and `GET /diseases/{id}` specifically.
- Confirm this caching does NOT get applied to any genuinely dynamic, per-user data (predictions, user profiles, stats) — this optimization is deliberately scoped only to the truly static reference data, and applying it more broadly would risk serving stale per-user data, a serious correctness bug.
- Measure and document the before/after response time improvement for these specific routes.

**Acceptance Criteria:**
- [ ] `GET /diseases`/`GET /diseases/{id}` show measurably reduced database load/response time after caching, while still returning correct, accurate data.
- [ ] No other route's data freshness is affected by this change.

**Must Not Break:** Must not cause `/diseases` to ever serve stale data if the underlying seed data is intentionally updated/re-seeded during active development — document the cache-invalidation trade-off clearly so this isn't a confusing surprise later.

---

#### Prompt 192 — Frontend Bundle Size Optimization

**Do:** Optimize frontend bundle size (code-splitting routes, lazy-loading the Result/History pages).

**Context & Why:** A smaller initial JavaScript bundle means faster first-load times, especially relevant for the real-world mobile/field-use context this app targets, where network conditions may be poor (directly connecting back to Prompt 181's mobile QA concerns).

**Requirements:**
- Use React's `lazy()` and `Suspense` to code-split route-level components (`Dashboard`, `NewScan`, `Result`, `History`, `Profile`, `About`) so each page's code is only downloaded when the user actually navigates to it, rather than all being bundled into one large initial JavaScript payload.
- Add a sensible `Suspense` fallback (reusing Prompt 116's `Spinner`) shown briefly while a lazily-loaded route's code downloads.
- Run `npm run build` and inspect the resulting bundle breakdown (Vite's build output, or a bundle-analyzer plugin if more detail is wanted) to confirm the code-splitting actually produced multiple smaller chunks rather than one single unchanged bundle, and record the before/after total initial-load JavaScript size.

**Acceptance Criteria:**
- [ ] The production build produces separate JavaScript chunks per lazily-loaded route, confirmed via build output inspection.
- [ ] Initial page-load JavaScript size is measurably reduced compared to the pre-optimization baseline.
- [ ] Navigating between routes still works correctly and smoothly, with the brief loading fallback appearing appropriately during chunk downloads, without introducing any new broken navigation behavior.

**Must Not Break:** Must re-verify (via a quick manual click-through, or re-running the e2e tests from Prompts 176–179) that all routing/navigation still works correctly after introducing lazy-loading — a common mistake is a `Suspense` boundary placed incorrectly, breaking nested routing.

---

#### Prompt 193 — Client-Side Image Compression Before Upload

**Do:** Add image compression/resizing on the client before upload to reduce payload size.

**Context & Why:** A real phone photo can easily be several megabytes — resizing/compressing it in the browser before upload (down to roughly what the model actually needs, since it will be resized to 224×224 anyway, per Prompt 16) meaningfully reduces upload time on poor mobile connections and reduces server-side bandwidth/storage costs, without any loss in prediction quality (since the model's effective input resolution is far lower than a typical phone photo's native resolution anyway).

**Requirements:**
- In `NewScan.tsx` (Prompt 135), after a file is selected but before upload (Prompt 138), use the browser's `Canvas` API (drawing the image onto an off-screen canvas at a reduced resolution — e.g. resize so the longest edge is no more than ~800–1000px, comfortably larger than the model's 224×224 input to preserve reasonable preview/stored-image quality while still meaningfully smaller than a typical multi-megapixel phone photo) and `canvas.toBlob()` with a reasonable JPEG quality setting (e.g. 0.8) to produce a compressed version of the image, which is then what actually gets uploaded (and used for the preview in Prompt 136, for consistency between what's previewed and what's sent).
- Measure and document the typical before/after file size reduction using a few representative real test photos.
- Ensure this compression step doesn't introduce a noticeable delay/freeze in the UI for a reasonably-sized source image (if it does, perform the compression asynchronously/off the main thread where practical, or at minimum show a brief processing indicator).

**Acceptance Criteria:**
- [ ] A large real test photo (several MB) is confirmed to be meaningfully smaller after this client-side compression step, with the compressed version being what's actually sent in the `/predict` request.
- [ ] Prediction accuracy/quality is confirmed unaffected by this compression (a quick comparison: predict on the same source image with and without this compression step, confirming the model's resize-to-224×224 step already dominates any quality loss, making the extra client-side compression's impact on final prediction negligible).

**Must Not Break:** Must not degrade prediction quality in any meaningfully observable way — verify with a direct before/after comparison on at least a few test images; must also not break the preview functionality from Prompt 136, which should now show the compressed version being actually uploaded.

---

#### Prompt 194 — Document Performance Results

**Do:** Re-run and document before/after performance numbers in `docs/PERFORMANCE.md`.

**Context & Why:** Consolidates every performance measurement and optimization made across Prompts 182, 190–193 into one reference document — both for the final project report and as a baseline future performance work could compare against.

**Requirements:**
- Sections: "Backend Latency" (Prompt 190's per-step breakdown, before/after any optimization applied), "Load Test Results" (Prompt 182's findings), "Caching Impact" (Prompt 191's before/after numbers), "Frontend Bundle Size" (Prompt 192's before/after), "Upload Payload Size" (Prompt 193's before/after).
- Present numbers clearly (tables/simple charts where helpful — reusable chart-generation approach similar to the matplotlib-based figures already used in the project's ML evaluation work, Prompt 45, could be adapted here if visual charts are desired for this document too) with enough specificity (exact numbers, exact test conditions) that the claims are genuinely verifiable, not vague ("it's faster now").

**Acceptance Criteria:**
- [ ] Every optimization from Prompts 190–193 has a clearly documented, specific before/after comparison.
- [ ] The document would allow someone to understand exactly what performance work was done and its measured impact, without needing to re-read every individual prompt's implementation.

**Must Not Break:** Must accurately reflect real, measured numbers from the actual optimizations applied — never present estimated/assumed figures as if they were measured.

---
### 4.E Backend Deployment

#### Prompt 195 — Provision Managed PostgreSQL

**Do:** Provision a managed PostgreSQL instance (e.g. Render/Railway/Supabase) for production.

**Context & Why:** All development so far has used a local Postgres instance — this is the first genuinely production-facing infrastructure step, creating the real database the deployed backend (Prompt 197) will connect to.

**Requirements:**
- Choose one managed provider (Render, Railway, and Supabase are all reasonable, commonly-free-tier-available choices for a student project; pick one and document the choice and reasoning briefly, e.g. "Render chosen for its straightforward free-tier Postgres offering and because the backend will also be hosted there, simplifying network configuration").
- Create the production database instance, and securely record its connection string (never commit this to Git — it belongs only in the deployment platform's environment-variable configuration, per Prompt 196).
- Confirm the production database is reachable (e.g. via `psql` or a quick test connection script) before proceeding to configure the backend against it.

**Acceptance Criteria:**
- [ ] A real, running managed Postgres instance exists and is confirmed reachable.
- [ ] Its connection string is recorded securely (e.g. in the team's password manager or the hosting platform's own secrets UI) and is NOT present anywhere in the Git repository.

**Must Not Break:** N/A — new infrastructure, doesn't touch existing local development setup.

---

#### Prompt 196 — Configure Production Environment Variables

**Do:** Configure production environment variables (DATABASE_URL, JWT_SECRET, MODEL_PATH) on the hosting platform.

**Context & Why:** Mirrors `backend/.env.example`'s documented variable list (Prompt 59) but with real production values, set directly in the hosting platform's environment-configuration UI/mechanism rather than a committed file.

**Requirements:**
- Set every variable from `backend/.env.example` (Prompt 59) in the chosen hosting platform's environment-variable settings, using Prompt 195's real production `DATABASE_URL`, a freshly-generated strong `JWT_SECRET` (never reused from local development — generate a new one specifically for production, per Prompt 59's documented generation method), the correct production `MODEL_PATH`/`CLASS_NAMES_PATH` (confirming these paths will be valid once Prompt 199 ensures the model files are actually present on the production deployment), and the correct `CORS_ALLOWED_ORIGINS` (a placeholder/TODO here until Prompt 202 establishes the real deployed frontend URL, to be updated once that exists per Prompt 204).
- Double-check every variable name matches exactly what `backend/app/core/config.py`'s `Settings` class (Prompt 58) expects — a typo'd environment variable name is a common, easy-to-miss deployment failure mode.

**Acceptance Criteria:**
- [ ] Every required environment variable is set correctly in the production hosting platform's configuration.
- [ ] `JWT_SECRET` used in production is confirmed different from the one used in local development.
- [ ] No production secret is present anywhere in the Git repository.

**Must Not Break:** Must exactly match the variable names/types expected by Prompt 58's `Settings` class.

---

#### Prompt 197 — Deploy the FastAPI Backend

**Do:** Deploy the FastAPI backend (Docker or platform-native build) and confirm `GET /health` responds correctly.

**Context & Why:** This is the first time the backend runs anywhere other than a developer's local machine — `GET /health` (Prompt 60) was specifically built as a dependency-free liveness check exactly for this moment.

**Requirements:**
- Choose a deployment method consistent with the chosen hosting platform (Prompt 195) — a `Dockerfile` (building the `backend/` app with its `requirements.txt`, Prompt 56) is a portable, broadly-compatible choice if the platform supports it, or a platform-native Python buildpack if simpler for the chosen provider; document the choice.
- If using Docker, write a `backend/Dockerfile` that correctly installs dependencies, copies the application code, and correctly handles the model file's presence (Prompt 199 addresses this in more detail — at minimum, confirm the Dockerfile doesn't need to bundle the large model file into the image itself if a separate strategy, like mounting/downloading it, is preferred, though bundling it directly is also an acceptable, simpler choice for this project's scope — document whichever is chosen).
- Deploy, and once live, call `GET /health` against the real production URL and confirm a `200 {"status": "ok"}` response.

**Acceptance Criteria:**
- [ ] The backend is successfully deployed and reachable at a real public URL.
- [ ] `GET /health` against that URL returns the expected response.

**Must Not Break:** Must use the real application code and configuration from all of Phase 2 and Phase 4's backend-side work so far — no simplified/stripped-down deployment-only version of the app.

---

#### Prompt 198 — Run Production Migrations and Seed Data

**Do:** Run production database migrations and seed the `diseases` table in the production database.

**Context & Why:** Prompt 197's deployed backend process exists now, but its database (Prompt 195) is still empty — this prompt brings the production schema and reference data up to the same state local development has had since Prompts 66–67.

**Requirements:**
- Run `alembic upgrade head` (Prompt 66) against the production `DATABASE_URL` (either by running this command from a local machine configured to point at the production database temporarily, or via the hosting platform's provided mechanism for running one-off commands against the deployed app — whichever is safer/more appropriate for the chosen platform).
- Run `seed_diseases.py` (Prompt 67) against production the same way, confirming its idempotent upsert behavior (already a Prompt 67 requirement) makes this safe to run even if accidentally run more than once.
- Verify, via a direct database inspection (`psql` against the production connection string, or the hosting platform's database browser UI if available) that all four tables exist with the correct schema and the `diseases` table contains exactly 8 correctly-seeded rows.

**Acceptance Criteria:**
- [ ] Production database schema matches the final local development schema exactly (all four tables, all constraints).
- [ ] `diseases` table in production contains the correct 8 seeded rows.

**Must Not Break:** Must use the exact same migration/seed scripts already verified correct in local development (Prompts 66–67) — do not hand-write a separate, divergent production setup process.

---

#### Prompt 199 — Ensure Model File Accessibility in Production

**Do:** Upload/verify the trained model file is accessible to the deployed backend instance.

**Context & Why:** `ml/models/crop_disease_model.keras` and `class_names.json` were frozen locally (Prompt 55) but need to actually exist at the configured `MODEL_PATH`/`CLASS_NAMES_PATH` (Prompt 58/196) on the production deployment for `model_service.py` (Prompt 86) to load them successfully at startup.

**Requirements:**
- Confirm the chosen deployment approach (Prompt 197) correctly includes these two files — if using a Docker image, confirm the `Dockerfile`'s build context includes `ml/models/crop_disease_model.keras` and `ml/models/class_names.json` and copies them to the expected production path inside the container (noting the model file's size — likely tens of megabytes for MobileNetV2 — is included in the image size, which is an acceptable, simple approach for this project's scope); if the platform has a size constraint making this impractical, an alternative is uploading the model file to object storage and having the application download it once at startup/build time — document whichever approach was actually used.
- After deployment, confirm via Prompt 197's already-working `GET /health` that the app started successfully at all (recall Prompt 86's requirement that the app fails loudly at startup if the model can't load — so a successful `/health` response is itself indirect confirmation the model loaded correctly, assuming `/health` doesn't touch the model directly per its original design; for a more direct confirmation, perform a real test `POST /predict` call against the production URL, per Prompt 200's smoke test).

**Acceptance Criteria:**
- [ ] The deployed backend's startup logs (per Prompt 86's logging requirement) confirm successful model loading in the production environment.
- [ ] A real test prediction against the production URL succeeds (cross-verified fully in Prompt 200).

**Must Not Break:** Must deploy the exact, frozen production model files from Prompt 55 — never a different/retrained model file than the one whose accuracy/evaluation numbers are documented throughout `ml/evaluation/`.

---

#### Prompt 200 — Smoke-Test All Production Endpoints

**Do:** Smoke-test all API endpoints against the live production URL.

**Context & Why:** This is the formal, comprehensive confirmation that the entire backend — not just `/health` and one test prediction — genuinely works correctly in its real production environment, closing out Section 4.E.

**Requirements:**
- Using the `.http` file reference (Prompt 109) or an equivalent script, manually or semi-automatically exercise every single backend route against the real production URL: register a real (clearly-labeled test) production user, log in, fetch/update profile, upload a photo, submit a real prediction, fetch history, submit feedback, fetch diseases list/detail.
- Confirm every response matches expected shape/behavior exactly as already verified locally throughout Phase 2 and Phase 4 — this is specifically about confirming the production environment introduces no new discrepancies (different Python/library versions, different filesystem permissions, different network configuration) compared to local development.
- Clean up/remove the test data created during this smoke test afterward if the production database should start genuinely clean for real users (or clearly label it as test data if cleanup isn't practical/necessary at this stage).

**Acceptance Criteria:**
- [ ] Every backend route is confirmed working correctly against the real production deployment.
- [ ] Any production-specific discrepancy discovered (compared to local-dev behavior) is identified and fixed before proceeding to frontend deployment (Section 4.F).

**Must Not Break:** This is a comprehensive production verification — any failure found here is high priority to fix before considering the backend genuinely deployment-complete.

---
### 4.F Frontend Deployment

#### Prompt 201 — Configure Production Frontend Environment

**Do:** Configure the frontend's production `.env` with the live backend API URL.

**Context & Why:** The exact moment Prompt 175's environment-based configuration mechanism was built for — the real production backend URL now exists (per Section 4.E) and needs to be wired into the frontend's production build configuration.

**Requirements:**
- Set `VITE_API_BASE_URL` (and any other frontend environment variables from Prompt 175's `.env.example`, e.g. `VITE_MAX_UPLOAD_SIZE_MB`) to the real production backend URL (from Prompt 197) in whichever mechanism the chosen frontend hosting platform (Prompt 202) uses for build-time environment variables (most platforms, including Vercel, provide a dashboard UI for this, consistent with how backend environment variables were set in Prompt 196).
- Confirm this production value is correctly distinct from the local-development `.env` value, and that both are correctly git-ignored/never committed (per Prompt 175).

**Acceptance Criteria:**
- [ ] A production build of the frontend (`npm run build`), inspected, correctly embeds the real production backend URL rather than the local-development one.

**Must Not Break:** Must not affect local development's existing `.env` configuration from Prompt 175.

---

#### Prompt 202 — Deploy the Frontend

**Do:** Deploy the React frontend to Vercel (or equivalent) and verify the build succeeds.

**Context & Why:** Gets the actual user-facing application live and publicly reachable for the first time.

**Requirements:**
- Connect the project's Git repository to Vercel (or an equivalent static-hosting platform like Netlify — pick one, Vercel is a natural fit for a Vite/React project and is explicitly already named in the original prompt library's framing), configure the build command (`npm run build`) and output directory (`dist/`, Vite's default) correctly, and set the production environment variables from Prompt 201 in the platform's configuration.
- Trigger a deployment and confirm the build completes successfully with no errors, and that the resulting deployed site loads correctly in a browser.

**Acceptance Criteria:**
- [ ] The frontend is successfully deployed and publicly reachable at a real URL.
- [ ] The deployed site's build log shows no errors/warnings that would indicate a broken or incomplete build.

**Must Not Break:** Must deploy the real, final frontend codebase from all of Phase 3 and Phase 4's frontend-side work — not a partial/outdated branch.

---

#### Prompt 203 — Custom Domain and HTTPS

**Do:** Configure a custom domain (or confirm the platform-provided URL) and HTTPS.

**Context & Why:** Directly closes the loop on Prompt 186's documented security decision — the app's production deployment must genuinely be served over HTTPS for that decision's reasoning (tokens never transmitted in plaintext) to actually hold true in practice, not just in theory.

**Requirements:**
- If the team has access to a custom domain, configure it through the hosting platform (Prompt 202); otherwise, the platform-provided default URL (e.g. `*.vercel.app`) is an entirely acceptable choice for this project's scope — document whichever was chosen.
- Confirm HTTPS is active (most modern static-hosting platforms, including Vercel, provision this automatically via Let's Encrypt or equivalent for both custom and platform-provided domains — verify this is genuinely active, not assumed) by checking the browser's address bar/certificate details on the live deployed site.
- Confirm the backend (Prompt 197) is also genuinely served over HTTPS (most managed hosting platforms, per Prompt 195, provide this automatically as well) — both halves of the stack must be HTTPS for the end-to-end security property to actually hold.

**Acceptance Criteria:**
- [ ] The live, deployed frontend is confirmed reachable only over HTTPS (not plain HTTP), with a valid certificate.
- [ ] The backend is confirmed to also be served over HTTPS.

**Must Not Break:** N/A — this is additive infrastructure configuration.

---

#### Prompt 204 — Verify Production CORS Configuration

**Do:** Verify CORS is correctly configured between the deployed frontend and backend origins.

**Context & Why:** Prompt 196 left `CORS_ALLOWED_ORIGINS` as a placeholder pending the real deployed frontend URL — that URL now exists (Prompt 202/203), so this is the moment to close that loop and confirm the two deployed services can actually talk to each other in production.

**Requirements:**
- Update the backend's production `CORS_ALLOWED_ORIGINS` environment variable (Prompt 196) to include the real, final deployed frontend URL/domain (from Prompt 202/203) — redeploy/restart the backend if the platform requires that for environment variable changes to take effect.
- From the live deployed frontend, perform a real action requiring an API call (e.g. attempt to load the About page's `GET /diseases` call, or attempt a login) and confirm it succeeds without a browser CORS error in the developer console.
- Confirm the backend still correctly rejects requests from arbitrary other origins (re-verify Prompt 103's CORS test still holds true against the production configuration, not just local development).

**Acceptance Criteria:**
- [ ] The live deployed frontend can successfully make API calls to the live deployed backend with no CORS errors.
- [ ] A request from an arbitrary non-allowlisted origin against the production backend is still correctly rejected by CORS.

**Must Not Break:** Must not accidentally widen production CORS to `"*"` or to an overly broad set of origins while fixing this — only the specific, real deployed frontend origin(s) should be allowlisted.

---

#### Prompt 205 — Full Live Smoke Test

**Do:** Run a full smoke test of the live deployed app: signup, login, scan, dashboard, history, profile.

**Context & Why:** The final, comprehensive confirmation that the ENTIRE deployed product — both frontend and backend, genuinely talking to each other in production — works correctly end-to-end, exactly as the local integration testing (Section 4.A) and e2e tests (Section 4.B) already proved for the local environment.

**Requirements:**
- Using a fresh browser session (no leftover local-dev session state) against the real, live, deployed frontend URL, walk through the complete core journey: sign up as a genuinely new test user, confirm landing on a correctly-personalized empty dashboard, perform a real scan with a real test image, confirm the Result page shows accurate data, confirm the History page shows the scan, confirm the Profile page shows and allows editing the correct user's data, and confirm logout/login works correctly.
- This walkthrough should mirror Prompt 168's local integration test exactly, just now performed against the real, live, publicly-deployed system rather than local development servers.
- Fix immediately any discrepancy found between local and production behavior.

**Acceptance Criteria:**
- [ ] The complete core user journey works correctly, end-to-end, against the real live deployed application.
- [ ] Any production-specific issue discovered is fixed and re-verified before considering deployment complete.

**Must Not Break:** This is the final deployment-completeness gate — any failure here means deployment is not yet genuinely done, regardless of what earlier individual deployment prompts (195–204) each individually confirmed.

---
### 4.G Documentation

#### Prompt 206 — Root README

**Do:** Write the root `README.md` with project overview, architecture diagram, and links to backend/frontend/ml docs.

**Context & Why:** This replaces/expands Prompt 1's original minimal placeholder README with the final, complete entry point into the entire project — the first thing anyone (a teammate, an evaluator, a future contributor) reads.

**Requirements:**
- Expand Prompt 1's original sections (project description, subfolder purposes, tech stack, team) with: a high-level architecture diagram (can reuse/adapt the system architecture diagram already created for the project report, or a simplified version of it, showing React frontend → FastAPI backend → PostgreSQL + TensorFlow model), a "Live Demo" section linking to the real deployed frontend URL (Prompt 203) once it exists, a "Documentation" section linking out to every other doc in `docs/` and each subfolder's own README (`ml/README.md`, `backend/README.md`), and a "Quick Start" section pointing to `docs/SETUP.md` (Prompt 207) for full local setup instructions.
- Include real, current project status (e.g. final measured model accuracy from `ml/evaluation/SUMMARY.md`, Prompt 50) prominently, since this is likely the first concrete fact a reader wants to know about a crop-disease-detection project.

**Acceptance Criteria:**
- [ ] The root README gives a genuinely useful, accurate, complete overview and correctly links to every other major documentation artifact produced across all four phases.
- [ ] The live demo link (once available) works correctly.

**Must Not Break:** Must accurately reflect the real, final state of the project, not its originally-planned state — e.g. if the final chosen model differs from early assumptions, this document must reflect the real, final choice (per Prompt 41).

---

#### Prompt 207 — Full Local Setup Guide

**Do:** Write `docs/SETUP.md` with full local-development setup instructions for all three subprojects.

**Context & Why:** Consolidates `ml/README.md` (Prompt 3), `backend/README.md` (Prompt 108), and the frontend's equivalent setup knowledge (scattered across Prompts 111/175/201) into one single, complete, ordered guide for someone setting up the ENTIRE project from a clean checkout — not just one subproject in isolation.

**Requirements:**
- Present as one ordered sequence: prerequisites (Python version, Node version, Postgres, Kaggle API access if they want to reproduce the ML training from scratch — though for most setup purposes, simply using the already-frozen `ml/models/` artifacts without re-running training is the realistic default path, and the guide should make this distinction clear: "Option A: use the pre-trained model (recommended for most setup) / Option B: reproduce training from scratch"), then clone/install steps for each of `ml/`, `backend/`, `frontend/` in the correct dependency order (backend needs the ML model artifacts to exist; frontend needs the backend running to be useful), then how to run all three together for local development, then how to run the test suites.
- Cross-link to each subproject's own more detailed README rather than fully duplicating their content here — this document's job is the high-level, correctly-ordered map; the subproject READMEs remain the detailed reference for their own scope.

**Acceptance Criteria:**
- [ ] Following this guide exactly, from a completely clean checkout, a new developer can get the full stack (ML artifacts present, backend running, frontend running, both talking to each other) working locally.
- [ ] The "use pre-trained model vs. reproduce training" distinction is clearly explained so a reader doesn't assume they must re-run the entire multi-hour Phase 1 training pipeline just to run the app locally.

**Must Not Break:** Must accurately reflect the real, final setup steps for each subproject as of this point in the project — re-verify against the actual current `ml/README.md`/`backend/README.md`/frontend setup rather than from memory of how early prompts originally described it.

---

#### Prompt 208 — Architecture Documentation

**Do:** Write `docs/ARCHITECTURE.md` documenting the full system architecture, matching the diagrams in the project report.

**Context & Why:** A deeper, more technical companion to the root README's high-level architecture summary — this is the document that explains not just *what* the components are but *how* they interact and *why* they're structured this way, directly useful for viva questions about architectural decisions (Prompt 217).

**Requirements:**
- Describe the full request lifecycle for the core scan feature end-to-end: browser → React frontend (`NewScan.tsx`) → `POST /predict` → FastAPI route → preprocessing service → model service (singleton-loaded TensorFlow model) → database write → response → React Result page rendering — this should read as a genuine technical walkthrough, not just a restatement of the file structure.
- Document the authentication architecture specifically (JWT issuance, verification, the `get_current_user` dependency pattern) since this is explicitly named as a topic Prompt 217 anticipates being asked about in the viva.
- Incorporate/reference Prompt 173's integration-fixes notes (if a separate temporary file was used for those) so this final architecture document reflects the real, as-built, fully-integrated system rather than its original per-phase design intentions alone.
- Include (or reference) the same kind of clean architecture/workflow diagrams already produced for the existing project report document, updated if anything about the actual implementation diverged from those original diagrams.

**Acceptance Criteria:**
- [ ] A reader unfamiliar with the codebase could understand the full system's structure and the core request flow after reading this document, without needing to read the source code directly.
- [ ] Diagrams/descriptions accurately reflect the final, real implementation, not the original early-phase plan where the two diverged.

**Must Not Break:** Must be consistent with the real, final codebase — this is a description of what was actually built, not an aspirational design document.

---

#### Prompt 209 — API Reference Documentation

**Do:** Write `docs/API_REFERENCE.md` documenting every backend endpoint with request/response examples.

**Context & Why:** A more complete, narrative companion to the auto-generated Swagger docs (Prompt 107) and the raw `.http` examples (Prompt 109) — useful as a readable, linear reference document (e.g. to include as an appendix in the final project report) rather than only an interactive tool.

**Requirements:**
- One section per route, each with: HTTP method + path, authentication requirement (yes/no), a brief description, example request (including headers/body where relevant), example success response, and example error response(s) for the most relevant failure cases — this content should be derivable directly from Prompt 107's Swagger annotations and Prompt 109's `.http` examples, consolidated into prose/Markdown form here rather than independently re-derived.
- Organize using the same logical grouping as Prompt 107's tags (Auth, Users, Predictions, Diseases).

**Acceptance Criteria:**
- [ ] Every route in the final backend is documented here with accurate, real (not fabricated/placeholder) example requests/responses.
- [ ] Content is consistent with `/docs` (Prompt 107) and `backend/docs/api-requests.http` (Prompt 109) — no contradictions between the three references.

**Must Not Break:** Must accurately reflect the final, real route set and schemas as of this point in Phase 4 (post Prompt 173's any contract fixes).

---

#### Prompt 210 — Database Schema Documentation

**Do:** Write `docs/DATABASE_SCHEMA.md` documenting all four tables and their relationships.

**Context & Why:** A focused, standalone reference for the data model specifically — useful both for onboarding and as a natural artifact to include in the final project report's "System Architecture & Database" section (directly extending the content already partially present in the existing project report document).

**Requirements:**
- For each of the four tables (`users`, `predictions`, `diseases`, `feedback`, per Prompts 62–65): list every column with its type and constraints, and describe its purpose in one sentence.
- Document the relationships explicitly: `predictions.user_id → users.id`, `feedback.prediction_id → predictions.id`, `feedback.user_id → users.id` — and note the deliberate design choice (from Prompt 63) that `predictions.disease` denormalizes the disease name directly rather than only foreign-keying to `diseases`, explaining why (historical record stability even if reference data changes).
- Include a simple entity-relationship diagram (can be a basic box-and-arrow diagram, consistent in style with the diagrams already produced for the project report).

**Acceptance Criteria:**
- [ ] Every column of every table is accurately documented, matching the real, final migration-applied schema (Prompt 66) exactly.
- [ ] Relationships and the deliberate denormalization decision are clearly explained with reasoning, not just stated as fact.

**Must Not Break:** Must match the real, final database schema exactly — cross-check against the actual Alembic migration files, not just the original model-definition prompts' descriptions, in case any field was adjusted along the way.

---

#### Prompt 211 — Compile Final Report Chapters with Real Numbers

**Do:** Compile the final project report chapters with final, measured accuracy/evaluation numbers filled in.

**Context & Why:** This is the direct, explicit task of updating the project's existing report document (the one already produced, which currently uses illustrative/placeholder evaluation figures and diagrams) with the genuine, final numbers and findings produced throughout this entire 220-prompt build — closing the loop between the originally-illustrative report and the actually-completed project.

**Requirements:**
- Replace the report's illustrative confusion matrix and evaluation-metrics chart (originally generated as clearly-labeled placeholders) with the real, final versions from `ml/evaluation/confusion_matrix.png` (Prompt 45) and real accuracy/precision/recall/F1 figures from `ml/evaluation/final_model_metrics.json` (Prompt 46).
- Update the report's "Model Evaluation & Expected Output" section with the real achieved accuracy (replacing the original illustrative "94%" example and illustrative metric percentages) and real example output from an actual test prediction.
- Incorporate the real-world testing findings (Prompts 51–54) as a new or expanded section, since the original report's limitations section only hypothesized this gap rather than having measured it.
- Update the "Technology Stack" and "System Architecture" sections if anything about the final, real implementation diverged from the original report's descriptions (e.g. if a different final model was chosen than originally assumed, per Prompt 41's real decision process).
- Reference `docs/ARCHITECTURE.md` (208), `docs/DATABASE_SCHEMA.md` (210), and `ml/evaluation/SUMMARY.md` (50) as the authoritative sources for this update, rather than re-deriving numbers independently.

**Acceptance Criteria:**
- [ ] The final report document contains zero remaining illustrative/placeholder figures or numbers — every claim is backed by a real artifact produced during the actual build.
- [ ] The report accurately reflects the real, final architecture and model choice, correcting any divergence from its original early-draft assumptions.

**Must Not Break:** Must not alter the report's core structure/narrative more than necessary — this is an update-with-real-data task, not a full rewrite, unless a genuine divergence (e.g. a different final model) requires more substantial narrative correction.

---

#### Prompt 212 — Prepare Clean Presentation-Ready Diagrams

**Do:** Prepare architecture and flow diagrams as clean, slide-ready images for the presentation.

**Context & Why:** Feeds directly into Prompt 214's slide deck build — ensures the visual assets used in the live presentation are polished, consistent, and based on the real final system (per Prompt 208/211), not reused unchanged from an early draft.

**Requirements:**
- Review every diagram already produced (the project report's existing workflow/CNN-architecture/system-architecture diagrams, plus any new ones from `docs/ARCHITECTURE.md`, Prompt 208, and `docs/DATABASE_SCHEMA.md`, Prompt 210) and confirm each is: accurate to the final real system, legible at presentation scale/projector resolution (not just document-page scale), and visually consistent with each other (same color palette/style, per the design tokens already established across both the report document and the frontend's Tailwind config, Prompt 113).
- Export final versions at high resolution suitable for direct embedding into presentation slides (Prompt 214), named clearly and organized in a dedicated location (e.g. `docs/presentation-assets/`).

**Acceptance Criteria:**
- [ ] A complete, accurate, visually-consistent set of diagrams exists, verified legible at presentation scale, ready for direct use in Prompt 214's slide deck.

**Must Not Break:** Must accurately reflect the real, final system — do not present an outdated diagram if the actual implementation diverged from an earlier draft.

---

#### Prompt 213 — Write the Demo Script

**Do:** Write `docs/DEMO_SCRIPT.md` — a step-by-step script for the live demonstration during evaluation.

**Context & Why:** Directly sets up Prompt 215's rehearsed live-demo walkthrough — having this written down in advance ensures the demo covers the right things in the right order and doesn't rely purely on improvisation during a high-stakes evaluation.

**Requirements:**
- A precise, step-by-step sequence: which URL to open, which test account to log in with (or to demonstrate signup live), exactly which test image(s) to use for the scan demonstration (chosen deliberately — e.g. one clearly-confident correct prediction, and optionally one lower-confidence example to demonstrate the uncertain-result handling from Prompt 146, showing off that specific thoughtful feature), what to point out on the Result page (confidence indicator, symptoms/prevention/management), a quick pass through History and Profile, and a closing summary statement.
- Include timing estimates per step, totaling to match Prompt 215's target demo length (2–3 minutes), and a clearly-marked "if something goes wrong" contingency note pointing to Prompt 218's fallback plan.

**Acceptance Criteria:**
- [ ] The script is specific and complete enough that any team member could execute the demo from this document alone, without needing to improvise what to click or say next.
- [ ] The chosen test images/accounts are confirmed to actually produce the intended demonstration results (e.g. the "uncertain result" example image is confirmed to actually trigger that state against the real deployed model) before finalizing the script.

**Must Not Break:** Must reference the real, live deployed application (Prompt 205) and real, working test data/accounts.

---
### 4.H Presentation & Viva Preparation

#### Prompt 214 — Build the Presentation Slide Deck

**Do:** Build the presentation slide deck (title, problem, methodology, architecture, results, demo, limitations, future scope).

**Context & Why:** This is the final, polished evolution of the project's already-existing 12-slide presentation — now updated throughout with the real diagrams (Prompt 212), real evaluation numbers (Prompt 211), and a structure that explicitly makes room for the live demo (Prompt 215) rather than only static content.

**Requirements:**
- Follow the same overall structure already established and refined in the existing presentation (Title → Introduction → Problem Statement → Objectives → Proposed System & Workflow → Dataset & Image Processing → Machine Learning Model → Technology Stack → System Architecture & Database → Model Evaluation & Expected Output → Advantages/Limitations/Future Scope → Conclusion), updating every slide that previously contained illustrative/placeholder content with the real, final figures and diagrams from Prompts 211–212.
- Add an explicit "Live Demo" slide/marker at the appropriate point in the sequence (logically after System Architecture, before or alongside Model Evaluation) indicating exactly when the presenter should pause the slides and switch to the live application, per the demo script (Prompt 213).
- Keep slide text itself reasonably concise (per the existing presentation's already-good balanced structure of 4–6 points per slide) — the deck supports the spoken presentation, it doesn't replace it.

**Acceptance Criteria:**
- [ ] The final deck contains zero illustrative/placeholder figures — everything is the real, final data and diagrams.
- [ ] A clear, explicit point in the deck marks the transition to the live demo.

**Must Not Break:** Should build on and refine the existing presentation's already-established structure, not discard it and start over unnecessarily.

---

#### Prompt 215 — Rehearse the Scripted Live Demo

**Do:** Prepare a 2–3 minute scripted live-demo walkthrough covering signup through result display.

**Context & Why:** Converts Prompt 213's written script into an actually-rehearsed, time-boxed spoken-and-clicked performance — the gap between "a script exists" and "the team can reliably execute it live under time pressure" is exactly what rehearsal closes.

**Requirements:**
- Have the designated presenter(s) walk through `docs/DEMO_SCRIPT.md` (Prompt 213) against the real live deployed application (Prompt 205) at least once, timing the full walkthrough and adjusting the script/pacing if it runs significantly over or under the 2–3 minute target.
- Confirm every step in the script still works exactly as written against the current live deployment (deployments/data can drift — re-verify rather than assuming the script, once written, stays perpetually accurate).

**Acceptance Criteria:**
- [ ] The demo, performed live against the real deployed app, reliably completes within the 2–3 minute target window.
- [ ] Every step confirmed working exactly as scripted at time of this rehearsal.

**Must Not Break:** If rehearsal reveals the script no longer matches the live app's actual behavior (e.g. due to later data/deployment changes), update `docs/DEMO_SCRIPT.md` (Prompt 213) to match reality rather than forcing the live demo to match an outdated script.

---

#### Prompt 216 — Prepare Core Technical Viva Answers

**Do:** Prepare answers to likely viva questions: why CNN, why transfer learning, why FastAPI, why PostgreSQL, what is overfitting, what is precision/recall/F1.

**Context & Why:** Converts the reasoning already developed and documented throughout the project (Prompt 41's model-selection trade-off analysis, Prompt 32's real overfitting diagnosis, Prompt 44's real precision/recall/F1 results) into concise, confident, interview-ready spoken answers — the goal is that every answer traces back to something genuinely built and measured in this project, not a generic textbook recitation.

**Requirements:**
- For each named question, write a concise (aim for roughly 30–60 seconds spoken) answer grounded in this project's real specifics: "why CNN" should reference the nature of image classification and cite this project's own baseline-vs-transfer-learning comparison (Prompt 40); "why transfer learning" should cite the real accuracy/efficiency trade-off numbers from `MODEL_SELECTION.md` (Prompt 41); "why FastAPI" should mention its async support, automatic OpenAPI docs (directly demonstrable via `/docs`, Prompt 107), and type-safety via Pydantic; "why PostgreSQL" should mention relational integrity for the user/prediction/feedback relationships (Prompt 63's foreign keys) and its maturity/reliability for a structured schema like this one; "what is overfitting" should be explained using this project's own real baseline training curves (Prompt 32) as a concrete illustrative example rather than only an abstract definition; "precision/recall/F1" should be explained using this project's own real per-class numbers (Prompt 44) as the concrete example.
- Have every team member (not just whoever happens to answer in the moment) genuinely understand and be able to deliver each of these answers, not just one designated "technical" team member — directly feeding into Prompt 220's final team-wide readiness check.

**Acceptance Criteria:**
- [ ] A written answer exists for every listed question, each one grounded in this project's real, specific artifacts/numbers rather than generic, project-agnostic explanations.
- [ ] Every team member has reviewed and can deliver each answer in their own words, not just read a memorized script.

**Must Not Break:** N/A — this is a preparation/documentation task, not a code change.

---

#### Prompt 217 — Prepare Architecture/Security Viva Answers

**Do:** Prepare answers explaining the authentication and personalization architecture (JWT, per-user data scoping).

**Context & Why:** A second, focused viva-prep prompt specifically for the architectural/security questions a more systems-and-security-minded evaluator might ask — directly drawing on `docs/ARCHITECTURE.md` (Prompt 208) and `docs/SECURITY.md` (Prompt 189).

**Requirements:**
- Prepare a clear, concise explanation of: what a JWT is and why it was chosen over session-based auth for this stateless API design, how `get_current_user` (Prompt 74) enforces that every piece of user-specific data is correctly scoped (concretely citing the `predictions.user_id` foreign key and the backend's deliberate rule of never trusting a client-supplied user id, per Prompt 184's audit), and the honest trade-off reasoning behind the `localStorage`-vs-`httpOnly`-cookie token-storage decision (Prompt 186) — being ready to discuss this specific trade-off is itself a sign of mature security thinking, more valuable in a viva than simply claiming "it's secure" without nuance.
- Be ready to directly reference/show the real, passing automated tests that prove data isolation (Prompt 172/179) if asked "how do you know this actually works," rather than only asserting it verbally.

**Acceptance Criteria:**
- [ ] A clear, confident, technically-accurate explanation exists and is understood by the team for each of these architecture/security topics.
- [ ] The team can, if asked, point directly to specific real tests/code (not just describe it abstractly) proving the data-isolation claim.

**Must Not Break:** N/A — preparation/documentation task.

---

#### Prompt 218 — Rehearse With a Fallback Plan

**Do:** Rehearse the demo end-to-end at least twice, including a fallback plan (e.g. screen recording) in case of live network issues.

**Context & Why:** Live demos against a real deployed network service are inherently vulnerable to venue WiFi problems, unexpected deployment downtime, or other factors entirely outside the team's control during the actual evaluation — having a tested fallback ready is professional risk management, not a lack of confidence in the real system.

**Requirements:**
- Rehearse Prompt 215's live demo a second time (and more, if useful), ideally including at least one rehearsal under conditions simulating potential real presentation constraints (e.g. a venue's possibly-slower WiFi, or presenting from a different laptop/browser than used for development).
- Record a clean screen-recording of a full, successful demo walkthrough (matching the real script, Prompt 213) as the explicit fallback artifact, to be played instead of attempting a live demo if a genuine technical failure occurs during the actual evaluation — store this recording somewhere immediately accessible on presentation day (not solely relying on a network connection to retrieve it, given the fallback's whole purpose is to handle network failure).
- Brief the team explicitly on when/how to invoke the fallback (e.g. "if the live demo hasn't loaded within 15 seconds, switch immediately to the recording rather than continuing to troubleshoot live in front of evaluators").

**Acceptance Criteria:**
- [ ] The live demo has been successfully rehearsed at least twice.
- [ ] A complete, successful fallback screen-recording exists and is stored for reliable offline access on presentation day.
- [ ] The team has an explicit, agreed-upon trigger condition for switching to the fallback.

**Must Not Break:** N/A — preparation task; the fallback recording should reflect the real, final application exactly as it will be demonstrated live.

---

#### Prompt 219 — Final Consistency Walkthrough

**Do:** Do a final walkthrough of the entire report for consistency between the written claims and the actual measured results.

**Context & Why:** A last, dedicated integrity check across the entire project's written documentation — specifically hunting for any remaining inconsistency between what's claimed in writing (the report, Prompt 211; the README, Prompt 206; the architecture docs, Prompt 208) and what the actual, real, deployed system does.

**Requirements:**
- Read through the final project report (Prompt 211), root README (Prompt 206), `docs/ARCHITECTURE.md` (208), `docs/SECURITY.md` (189), and `docs/PERFORMANCE.md` (194) end-to-end, cross-checking every specific factual claim (an accuracy number, an architectural description, a security measure, a performance figure) against the actual corresponding real artifact/code/test result it should trace back to.
- Correct any discovered discrepancy immediately — a mismatch here, caught by an evaluator during review or viva, would seriously undermine the project's credibility, so this check deserves genuine care rather than a cursory skim.

**Acceptance Criteria:**
- [ ] Every specific factual claim across all reviewed documents is confirmed to accurately match the real, final implementation — zero discovered discrepancies remain uncorrected.

**Must Not Break:** This is a verification/correction pass — any fix made should correct a document to match reality, never the reverse (never adjust the real system's behavior just to match a convenient but inaccurate written claim).

---

#### Prompt 220 — Final Team Readiness Review

**Do:** Final team review: confirm every member can explain every phase of the pipeline, not just their own module.

**Context & Why:** The final prompt in the entire 220-prompt library — a deliberate, explicit check that the project's completion is a genuinely shared team accomplishment and understanding, not a set of four disconnected individual contributions that only their original author can explain.

**Requirements:**
- Hold a team session where each member, in turn, explains a phase of the project they did NOT primarily work on (e.g. a frontend-focused member explains the ML pipeline's transfer-learning approach at a reasonable level of detail; an ML-focused member explains the JWT authentication flow) — the goal is genuine cross-team understanding sufficient to confidently handle an unpredictable viva question directed at any team member about any part of the system, not rehearsed memorization of someone else's talking points.
- Identify any team member who struggles to explain a given phase, and spend focused time closing that specific gap (reviewing the relevant `README`/`SUMMARY`/`ARCHITECTURE` documentation together, per Prompts 25/50/108/208) before the actual evaluation.
- Treat this as the formal, final closing checkpoint of the entire 220-prompt build — once every team member can confidently discuss every phase, the project is genuinely complete and the team is genuinely ready.

**Acceptance Criteria:**
- [ ] Every team member has successfully explained, in their own words, at least the core concepts of every one of the four phases (ML, Backend, Frontend, Integration/Deployment), confirmed by the rest of the team listening and providing feedback.
- [ ] Any identified understanding gap has been actively addressed before this final prompt is considered complete.

**Must Not Break:** N/A — this is the final human/team-readiness checkpoint, not a code or documentation change; it closes the entire 220-prompt library.

---
## Progress Tracker

| Phase | Range | Prompts | Gate to Pass Before Next Phase |
|---|---|---|---|
| PHASE 1 — Machine Learning & Data Pipeline | Prompts 1–55 | 55 | Prompt 55: `crop_disease_model.keras` + `class_names.json` frozen, hashed, committed |
| PHASE 2 — Backend & Database (FastAPI) | Prompts 56–110 | 55 | Prompt 110: full test suite passing, every route audited for `get_current_user` |
| PHASE 3 — Frontend (React) | Prompts 111–165 | 55 | Prompt 165: full visual QA pass complete, no placeholder/mock data remaining |
| PHASE 4 — Integration, Testing, Deployment & Docs | Prompts 166–220 | 55 | Prompt 220: every team member can explain every phase |
| **Total** | | **220** | |

Track completion by checking off each prompt's **Acceptance Criteria** checklist as it's finished — a prompt isn't "done" until every box in its own checklist is checked, not merely until Claude Code stops producing new output for it.
