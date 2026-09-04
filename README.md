# Detection of Backdoor Attacks Using HPCs

This folder is a self-contained, dependency-free submission for Problem 1 of
the hackathon. It learns the normal hardware-performance-counter (HPC) profile
from clean inferences, then flags unusually distant rows as possible
`backdoor` examples.

## Files

- `detector.py` — training and prediction command-line program
- `clean_training.csv` — supplied clean training examples
- `model.json` — final model trained on the supplied clean CSV
- `report.pdf` — short technical report
- `report.md` — editable source for the report
- `make_report_pdf.py` — dependency-free helper to regenerate the PDF
- `SUBMISSION_CHECKLIST.md` — beginner-friendly GitHub upload instructions

## What the program does

The supplied training file contains only clean model inferences. Each row is
one example and each column is a Hardware Performance Counter (HPC):

- `cache-references`
- `cycles`
- `LLC-loads`

The program learns the normal centre and spread of those counters. A new row
that is far away from the normal profile receives a high anomaly score and is
flagged as a possible `backdoor`. Larger scores indicate more unusual
measurements.

This is intentionally an **anomaly detector**, not a normal supervised
classifier, because the organizers do not provide backdoor examples for
training.

## Requirements

- Python 3.10 or newer
- No third-party Python packages

## Run it from the repository root

Train the included final model from the supplied clean data:

```bash
python3 detector.py train \
  --input clean_training.csv \
  --model model.json
```

The final checked-in model was trained on 800 rows and uses a threshold of
`19.742107` (the 99.5th percentile of the clean training scores). Re-running
the command recreates the model deterministically from the same CSV.

To score another CSV:

```bash
python3 detector.py predict \
  --input validation.csv \
  --model model.json \
  --output predictions.csv
```

The input CSV must contain the three HPC columns with the same names and
numeric values.

The prediction output contains:

- `row_number`: the original row number in the input CSV
- `anomaly_score`: larger means more unusual
- `prediction`: either `clean` or `backdoor`

The detector uses a strict `score > threshold` comparison. A score exactly
equal to the threshold is therefore labeled `clean`.

## Final method and parameters

The submitted method is `robust_squared_z_distance`:

1. For each counter, calculate the median of the clean training values.
2. Calculate the median absolute deviation (MAD), converted to a
   standard-deviation-like scale with `1.4826 * MAD`.
3. For each row, calculate the sum of squared standardized distances:
   `sum(((value - median) / scale) ** 2)`.
4. Flag a row when its score is above the `0.995` clean-training percentile.

The MAD approach is less affected by a small number of unusual measurements
than a mean-and-standard-deviation profile. If a counter is flat, the program
uses its population standard deviation, or `1.0` when that is also zero.

## Limitations

The uploaded file is clean-only, so it cannot prove how well the detector
catches backdoors. The private evaluation set supplied by the organizers is
needed for accuracy, TPR, FPR, F1, and AUROC measurements. The method also
scores each row independently, does not model correlations between counters or
temporal patterns, and assumes future clean data resembles the training
distribution. The threshold should be recalibrated if the organizers provide
labeled validation data or a required submission format.

See `report.pdf` for the concise technical explanation of HPCs, anomaly
detection, this method, and its limitations.

For a step-by-step GitHub upload guide, see `SUBMISSION_CHECKLIST.md`.