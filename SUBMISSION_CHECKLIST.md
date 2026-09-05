# Submission checklist

## Files

The repository should contain:

- `detector.py`
- `clean_training.csv`
- `suraksha_model.json`
- `README.md`
- `report.md`
- `report.pdf`
- `.gitignore`

Do not commit `__pycache__` or generated prediction files unless the submission rules ask for them.

## Before submitting

1. From the repository root, rebuild the model:

   ```bash
   python3 detector.py train --input clean_training.csv --model suraksha_model.json
   ```

2. Check that the model file contains the expected columns, training row count, and threshold.
3. Run a prediction on the organiser's validation file when it is available.
4. Check the required prediction-column names against the submission instructions.

## GitHub

Create the repository, upload the files above, and use a commit message that describes the change. Keep the repository visibility and final prediction format aligned with the hackathon rules.

The clean training file by itself is not enough to claim a detection accuracy. That requires labelled evaluation data from the organisers.
