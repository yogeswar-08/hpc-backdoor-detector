# Beginner Submission Checklist

## Files to upload to GitHub

Upload these files from the `hackathon_solution` folder:

- `detector.py`
- `clean_training.csv`
- `model.json`
- `README.md`
- `report.md`
- `report.pdf`
- `.gitignore`

Do not upload `__pycache__` or temporary prediction files.

## Create the GitHub repository

1. Open `https://github.com`.
2. Sign in or create a GitHub account.
3. Tap the **+** button in the top-right corner.
4. Choose **New repository**.
5. Use a name such as `hpc-backdoor-detector`.
6. Choose **Public**, unless the hackathon instructions specifically require
   Private.
7. Tick **Add a README file**.
8. Tap **Create repository**.

## Upload the project

1. Open the new repository.
2. Choose **Add file**.
3. Choose **Upload files**.
4. Select the six files listed above.
5. Scroll down to the commit box.
6. Type: `Add HPC backdoor detector`
7. Tap **Commit changes**.

If GitHub does not show hidden files such as `.gitignore`, upload the other
files first and add `.gitignore` separately.

## What to say during the presentation

> We used clean-only anomaly detection because the training data contains no
> backdoor examples. The system learns the normal median and variation of
> hardware performance counters. For each new inference, it calculates a
> distance from that normal profile. A high distance is reported as a possible
> backdoor inference.

## Important honesty point

Do not claim a final accuracy score until the organizers provide labelled
validation data or the official evaluation result. The uploaded CSV contains
clean training examples only.