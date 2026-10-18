import pandas as pd
import argparse
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from engines.intent_engine import IntentEngine

# Default evaluation set, stored next to this script
DEFAULT_TEST_PATH = Path(__file__).resolve().parent / "intent_test.csv"

def main(path: Path):
    df = pd.read_csv(path)

    # Make sure the column exists
    if "true_intent" not in df.columns:
        raise ValueError(
            f"CSV must contain a 'true_intent' column. Found: {list(df.columns)}"
        )

    # Force clean string labels
    y_true = df["true_intent"].fillna("unknown").astype(str).tolist()
    texts = df["text"].fillna("").astype(str).tolist()

    engine = IntentEngine()

    y_pred = []

    for t in texts:
        label, score, _ = engine.match(t)

        # Convert None to a string label for metrics
        label = label if label is not None else "unknown"

        y_pred.append(str(label))

    # Now metrics won't explode
    acc = accuracy_score(y_true, y_pred)
    print(f"\nAccuracy: {acc:.3f}\n")

    print("Classification report:")
    print(classification_report(y_true, y_pred, digits=3, zero_division=0))

    labels = sorted(set(y_true) | set(y_pred))
    print("\nLabels order:")
    print(labels)

    print("\nConfusion matrix:")
    print(confusion_matrix(y_true, y_pred, labels=labels))

    df_out = df.copy()
    df_out["pred_intent"] = y_pred

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=DEFAULT_TEST_PATH)
    args = parser.parse_args()
    main(args.path)