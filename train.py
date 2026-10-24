"""
Training and Evaluation Pipeline for DeadlockGuard.
Trains an explainable Decision Tree Classifier (and Logistic Regression baseline)
on 4,800 samples and evaluates on 1,200 hidden test cases.
Saves model.joblib for instant loading in the web app.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from dataset import generate_dataset, DEFAULT_CONFIG


FEATURE_COLS = [
    "cycle_length",
    "min_priority",
    "max_priority",
    "avg_priority",
    "min_progress",
    "max_progress",
    "avg_progress",
    "min_checkpoint_distance",
    "avg_checkpoint_distance",
    "max_preempt_count",
    "avg_preempt_count",
    "heuristic_term_proxy",
    "heuristic_roll_proxy",
    "heuristic_prmp_proxy",
]


def train_models(dataset_path: str = "dataset.csv", force_regenerate: bool = False):
    if not os.path.exists(dataset_path) or force_regenerate:
        print("Generating fresh dataset (6,000 scenarios)...")
        df = generate_dataset(num_samples=6000, seed=42)
        df.to_csv(dataset_path, index=False)
    else:
        print(f"Loading existing dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)

    X = df[FEATURE_COLS]
    y = df["best_fix"]

    # 4,800 train (80%) and 1,200 hidden test cases (20%)
    X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(
        X, y, df.index, test_size=1200, random_state=42, stratify=y
    )

    test_df = df.loc[indices_test].copy()

    # 1. Explainable Decision Tree
    tree_clf = DecisionTreeClassifier(
        max_depth=6,
        min_samples_leaf=15,
        random_state=42,
    )
    tree_clf.fit(X_train, y_train)
    tree_pred = tree_clf.predict(X_test)
    tree_acc = accuracy_score(y_test, tree_pred)

    # 2. Logistic Regression (Baseline for comparison)
    lr_clf = LogisticRegression(max_iter=1000, random_state=42)
    lr_clf.fit(X_train, y_train)
    lr_pred = lr_clf.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_pred)

    print(f"Decision Tree Accuracy on 1,200 hidden test cases: {tree_acc * 100:.2f}%")
    print(f"Logistic Regression Accuracy on hidden test cases: {lr_acc * 100:.2f}%")
    print("\nDecision Tree Classification Report:")
    print(classification_report(y_test, tree_pred))

    # Save artifact bundle
    model_payload = {
        "model": tree_clf,
        "lr_model": lr_clf,
        "feature_cols": FEATURE_COLS,
        "classes": list(tree_clf.classes_),
        "tree_accuracy": round(tree_acc, 4),
        "lr_accuracy": round(lr_acc, 4),
        "test_df": test_df,
    }

    joblib.dump(model_payload, "model.joblib")
    print("Model payload saved to model.joblib successfully.")
    return model_payload


def extract_features_from_state(deadlock_info: dict, processes: dict) -> dict:
    """Extract model feature dictionary from current live simulation state."""
    cycle_processes = deadlock_info.get("cycle_processes", [])
    cycle_procs = [processes[p] for p in cycle_processes if p in processes]

    if not cycle_procs:
        return {}

    priorities = [p.get("priority", 1) for p in cycle_procs]
    progresses = [p.get("progress", 0.5) for p in cycle_procs]
    ckpt_dists = [max(1, p.get("step", 5) - p.get("checkpoint_step", 1)) for p in cycle_procs]
    preempt_counts = [p.get("preempt_count", 0) for p in cycle_procs]

    features = {
        "cycle_length": len(cycle_processes),
        "min_priority": min(priorities),
        "max_priority": max(priorities),
        "avg_priority": round(float(np.mean(priorities)), 2),
        "min_progress": min(progresses),
        "max_progress": max(progresses),
        "avg_progress": round(float(np.mean(progresses)), 2),
        "min_checkpoint_distance": min(ckpt_dists),
        "avg_checkpoint_distance": round(float(np.mean(ckpt_dists)), 2),
        "max_preempt_count": max(preempt_counts),
        "avg_preempt_count": round(float(np.mean(preempt_counts)), 2),
        "heuristic_term_proxy": round(min(priorities) * 2.2 + min(progresses) * 7.0, 2),
        "heuristic_roll_proxy": round(min(ckpt_dists) * 1.5, 2),
        "heuristic_prmp_proxy": round(max(preempt_counts) * 2.8, 2),
    }
    return features


def explain_prediction(model_payload: dict, sample_features: dict) -> dict:
    """
    Explain a prediction from the Decision Tree in human terms (Innovation A).
    """
    tree: DecisionTreeClassifier = model_payload["model"]
    classes = model_payload["classes"]

    row = [[sample_features.get(col, 0.0) for col in FEATURE_COLS]]
    probs = tree.predict_proba(row)[0]
    pred_idx = np.argmax(probs)
    pred_class = classes[pred_idx]
    confidence = float(probs[pred_idx])

    prob_dict = {classes[i]: round(float(probs[i]), 3) for i in range(len(classes))}

    signals = []
    if sample_features.get("min_progress", 1.0) <= 0.15 and sample_features.get("min_priority", 3) <= 2:
        signals.append("Low priority candidate with minimal completed work detected (< 15% progress) — termination is extremely inexpensive.")
    if sample_features.get("min_checkpoint_distance", 10) <= 2:
        signals.append("Recent checkpoint exists (<= 2 steps of work to undo) — rollback offers rapid cycle resolution with minimal rework.")
    if sample_features.get("max_preempt_count", 0) == 0:
        signals.append("Zero prior preemption history — preemption carries no starvation penalty.")
    elif sample_features.get("max_preempt_count", 0) >= 2:
        signals.append("Repeated prior preemption on cycle processes — starvation protection actively discourages further preemption.")

    if not signals:
        signals.append(f"Optimal balance identified for cycle of size {sample_features.get('cycle_length', 2)} across contention metrics.")

    return {
        "recommended_fix": pred_class,
        "confidence": confidence,
        "confidence_pct": round(confidence * 100, 1),
        "probabilities": prob_dict,
        "key_signals": signals,
    }


if __name__ == "__main__":
    train_models(force_regenerate=True)
