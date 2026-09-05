# Suraksha

Suraksha looks for unusual hardware-performance-counter (HPC) measurements in model inference runs. The available training data contains clean runs only, so the detector learns a clean baseline and flags rows that sit unusually far from it.

## Files

- `detector.py` — command-line training and prediction tool
- `clean_training.csv` — clean reference data supplied for training
- `suraksha_model.json` — model generated from that data
- `report.md` / `report.pdf` — method and limitations
- `make_report_pdf.py` — small helper for rebuilding the PDF

## Requirements

- Python 3.10 or newer
- No third-party packages

## Usage

Train a model from the clean reference file:

```bash
python3 detector.py train \
  --input clean_training.csv \
  --model suraksha_model.json
```

The checked-in model was trained on 800 rows. Its alert threshold is `19.742107`, which is the 99.5th percentile of the training scores. Training again from the same CSV produces the same model.

Score another CSV:

```bash
python3 detector.py predict \
  --input validation.csv \
  --model suraksha_model.json \
  --output predictions.csv
```

The input must include these columns:

- `cache-references`
- `cycles`
- `LLC-loads`

The output contains the source row number, an anomaly score, and either `clean` or `backdoor`. A larger score means the measurements are farther from the clean baseline. Rows are flagged only when the score is strictly greater than the threshold.

## Detection method

For each counter, the detector stores the median of the clean values and a robust spread based on the median absolute deviation (MAD). It then adds the squared standardized distance across the three counters:

`sum(((value - median) / scale) ** 2)`

The MAD-based scale is less sensitive to a few unusual clean measurements than a mean and standard deviation. If a counter is flat, the code falls back to its population standard deviation and then to `1.0` if necessary.

## Limitations

This repository does not contain labelled backdoor examples, so it cannot provide accuracy, recall, F1, or AUROC. The method also evaluates each row on its own, without modelling relationships between counters or changes over time. Results can change if the hardware, operating system, workload, or clean-data distribution changes. A labelled validation set should be used to recalibrate the threshold before reporting performance.
