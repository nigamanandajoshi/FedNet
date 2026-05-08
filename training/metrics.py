"""Metrics calculation for model evaluation."""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from typing import Dict, List


def calculate_metrics(y_true: List, y_pred: List) -> Dict[str, float]:
    """
    Calculate classification metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        
    Returns:
        Dictionary of metrics
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
    }
    
    return metrics


def calculate_confusion_matrix(y_true: List, y_pred: List) -> np.ndarray:
    """Calculate confusion matrix."""
    return confusion_matrix(y_true, y_pred)


def get_classification_report(
    y_true: List,
    y_pred: List,
    target_names: List[str] = None
) -> str:
    """
    Get detailed classification report.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        target_names: Names of classes
        
    Returns:
        Classification report string
    """
    if target_names is None:
        target_names = ["Normal", "Thalassemia Minor", "Thalassemia Major"]
    
    return classification_report(y_true, y_pred, target_names=target_names)


def calculate_per_class_metrics(y_true: List, y_pred: List) -> Dict[str, Dict]:
    """Calculate metrics for each class."""
    classes = sorted(set(y_true))
    per_class = {}
    
    for cls in classes:
        y_true_binary = [1 if y == cls else 0 for y in y_true]
        y_pred_binary = [1 if y == cls else 0 for y in y_pred]
        
        per_class[f"class_{cls}"] = {
            "precision": precision_score(y_true_binary, y_pred_binary, zero_division=0),
            "recall": recall_score(y_true_binary, y_pred_binary, zero_division=0),
            "f1": f1_score(y_true_binary, y_pred_binary, zero_division=0),
        }
    
    return per_class
