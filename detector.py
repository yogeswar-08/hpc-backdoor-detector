#!/usr/bin/env python3
"""Train a clean HPC baseline and flag unusually distant rows."""

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any


def read_csv(path: str, wanted_columns: list[str] | None = None) -> tuple[list[str], list[list[float]]]:
    """Read the requested numeric columns from a CSV file."""
    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError(f"{path} does not contain a header row.")

        available = [name.strip() for name in reader.fieldnames]
        columns = wanted_columns or available
        missing = [name for name in columns if name not in available]
        if missing:
            raise ValueError(
                f"{path} is missing these columns: {', '.join(missing)}"
            )

        values: list[list[float]] = []
        for row_number, row in enumerate(reader, start=2):
            current: list[float] = []
            for column in columns:
                raw = (row.get(column) or "").strip()
                if not raw:
                    raise ValueError(
                        f"{path}, row {row_number}: empty value in {column!r}."
                    )
                try:
                    current.append(float(raw))
                except ValueError as error:
                    raise ValueError(
                        f"{path}, row {row_number}: {raw!r} is not a number."
                    ) from error
            values.append(current)

    if not values:
        raise ValueError(f"{path} does not contain any data rows.")
    return columns, values


def percentile(values: list[float], fraction: float) -> float:
    """Calculate a percentile using linear interpolation."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def fit_model(
    columns: list[str],
    values: list[list[float]],
    threshold_percentile: float,
) -> dict[str, Any]:
    """Build a median/MAD profile from clean rows."""
    centres = [statistics.median(column) for column in zip(*values)]
    scales: list[float] = []

    for column_index, centre in enumerate(centres):
        deviations = [
            abs(row[column_index] - centre)
            for row in values
        ]
        mad = statistics.median(deviations)
        scale = 1.4826 * mad

        # A constant counter has no MAD, so use a small fallback scale.
        if scale <= 1e-12:
            column_values = [row[column_index] for row in values]
            scale = statistics.pstdev(column_values) or 1.0
        scales.append(scale)

    training_scores = [
        anomaly_score(row, centres, scales)
        for row in values
    ]
    threshold = percentile(training_scores, threshold_percentile)

    return {
        "method": "robust_squared_z_distance",
        "columns": columns,
        "centres": centres,
        "scales": scales,
        "threshold_percentile": threshold_percentile,
        "threshold": threshold,
        "training_rows": len(values),
    }


def anomaly_score(
    row: list[float],
    centres: list[float],
    scales: list[float],
) -> float:
    """Return the squared standardized distance from the baseline."""
    return sum(
        ((value - centre) / scale) ** 2
        for value, centre, scale in zip(row, centres, scales)
    )


def train(args: argparse.Namespace) -> None:
    columns, values = read_csv(args.input)
    model = fit_model(columns, values, args.threshold_percentile)

    with open(args.model, "w", encoding="utf-8") as file:
        json.dump(model, file, indent=2)

    print(f"Training rows: {len(values)}")
    print(f"HPC columns: {', '.join(columns)}")
    print(f"Anomaly threshold: {model['threshold']:.6f}")
    print(f"Saved model: {args.model}")


def predict(args: argparse.Namespace) -> None:
    with open(args.model, "r", encoding="utf-8") as file:
        model = json.load(file)

    columns, values = read_csv(args.input, model["columns"])
    threshold = float(model["threshold"])
    rows: list[dict[str, Any]] = []

    for row_number, row in enumerate(values, start=2):
        score = anomaly_score(row, model["centres"], model["scales"])
        rows.append(
            {
                "row_number": row_number,
                "anomaly_score": round(score, 6),
                "prediction": "backdoor" if score > threshold else "clean",
            }
        )

    with open(args.output, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["row_number", "anomaly_score", "prediction"],
        )
        writer.writeheader()
        writer.writerows(rows)

    suspicious = sum(row["prediction"] == "backdoor" for row in rows)
    print(f"Input rows: {len(rows)}")
    print(f"Rows flagged as possible backdoors: {suspicious}")
    print(f"Saved predictions: {args.output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HPC anomaly detector")
    commands = parser.add_subparsers(dest="command", required=True)

    train_parser = commands.add_parser(
        "train",
        help="learn a baseline from a clean CSV",
    )
    train_parser.add_argument("--input", required=True, help="clean training CSV")
    train_parser.add_argument(
        "--model",
        default="suraksha_model.json",
        help="where to save the learned model",
    )
    train_parser.add_argument(
        "--threshold-percentile",
        type=float,
        default=0.995,
        help="clean-data percentile used as the alert threshold",
    )
    train_parser.set_defaults(function=train)

    predict_parser = commands.add_parser(
        "predict",
        help="score a CSV with a saved model",
    )
    predict_parser.add_argument("--input", required=True, help="CSV to score")
    predict_parser.add_argument(
        "--model",
        default="suraksha_model.json",
        help="saved model file",
    )
    predict_parser.add_argument(
        "--output",
        default="predictions.csv",
        help="where to save predictions",
    )
    predict_parser.set_defaults(function=predict)
    return parser


if __name__ == "__main__":
    arguments = build_parser().parse_args()
    arguments.function(arguments)
