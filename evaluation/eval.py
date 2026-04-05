import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import TEST_FILE, EVAL_RESULTS_FILE
from src.guardrails import ErrorType


def load_test_data(path=None):
    with open(path or TEST_FILE) as f:
        return json.load(f)


def compute_metrics(predictions, ground_truths, categories):
    n = len(predictions)
    if n == 0:
        return {}

    json_valid = 0
    exact_match = 0
    field_precision_sum = 0
    field_recall_sum = 0
    field_f1_sum = 0
    retry_total = 0
    retry_count = 0
    success_after_retry = 0
    total_errors = {et.value: 0 for et in ErrorType}
    failure_count = 0
    successful_count = 0

    for i, pred in enumerate(predictions):
        raw_output = pred.get("raw_output", "")
        retries = pred.get("retries", 0)
        success = pred.get("success", False)
        pred_output = pred.get("final_output")

        # JSON validity of raw output
        try:
            json.loads(raw_output)
            json_valid += 1
        except (json.JSONDecodeError, TypeError):
            pass

        # retry stats
        if retries > 0:
            retry_count += 1
            retry_total += retries
            if success:
                success_after_retry += 1

        if not success:
            failure_count += 1
            for e in pred.get("errors", []):
                etype = e.get("type", "")
                if etype in total_errors:
                    total_errors[etype] += 1
            continue

        if not isinstance(pred_output, dict):
            failure_count += 1
            continue

        successful_count += 1

        # parse ground truth
        try:
            gt = json.loads(ground_truths[i])
        except (json.JSONDecodeError, TypeError):
            gt = {}

        # exact match
        if json.dumps(pred_output, sort_keys=True) == json.dumps(gt, sort_keys=True):
            exact_match += 1

        # field-level precision/recall
        gt_fields = set(gt.keys())
        pred_fields = set(pred_output.keys())

        if pred_fields:
            correct = sum(1 for f in pred_fields & gt_fields if pred_output[f] == gt[f])
            precision = correct / len(pred_fields)
            recall = correct / len(gt_fields) if gt_fields else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            field_precision_sum += precision
            field_recall_sum += recall
            field_f1_sum += f1

    # average field metrics over successful samples only (not total)
    denom = successful_count if successful_count > 0 else 1

    return {
        "total_samples": n,
        "json_validity_rate": round(json_valid / n, 4),
        "exact_match_accuracy": round(exact_match / n, 4),
        "field_precision": round(field_precision_sum / denom, 4),
        "field_recall": round(field_recall_sum / denom, 4),
        "field_f1": round(field_f1_sum / denom, 4),
        "failure_rate": round(failure_count / n, 4),
        "retry_rate": round(retry_count / n, 4),
        "avg_retries_per_sample": round(retry_total / n, 4),
        "retry_success_rate": round(success_after_retry / retry_count, 4) if retry_count > 0 else 0,
        "error_taxonomy": total_errors,
    }


def run_evaluation(inference_logs_path, label, test_data):
    with open(inference_logs_path) as f:
        logs = json.load(f)

    ground_truths = [s["output"] for s in test_data[:len(logs)]]
    categories = [s["category"] for s in test_data[:len(logs)]]

    metrics = compute_metrics(logs, ground_truths, categories)
    metrics["label"] = label
    return metrics


def print_comparison_table(results):
    print("\n" + "=" * 80)
    print("EVALUATION RESULTS: 3-Way Comparison")
    print("=" * 80)

    metric_keys = [
        ("JSON Validity Rate", "json_validity_rate"),
        ("Exact Match Accuracy", "exact_match_accuracy"),
        ("Field Precision", "field_precision"),
        ("Field Recall", "field_recall"),
        ("Field F1", "field_f1"),
        ("Failure Rate", "failure_rate"),
        ("Retry Rate", "retry_rate"),
        ("Avg Retries/Sample", "avg_retries_per_sample"),
        ("Retry Success Rate", "retry_success_rate"),
    ]

    header = f"{'Metric':<25}" + "".join(f"{r['label']:<20}" for r in results)
    print(header)
    print("-" * 80)

    for display_name, key in metric_keys:
        row = f"{display_name:<25}"
        for r in results:
            val = r.get(key, "N/A")
            row += f"{val:<20.4f}" if isinstance(val, float) else f"{str(val):<20}"
        print(row)

    print("\nError Taxonomy:")
    print("-" * 80)
    for etype in ErrorType:
        row = f"  {etype.value:<23}"
        for r in results:
            row += f"{r.get('error_taxonomy', {}).get(etype.value, 0):<20}"
        print(row)


def save_results(results, qualitative_examples=None):
    output = {"comparison": results, "qualitative_examples": qualitative_examples or []}
    os.makedirs(os.path.dirname(EVAL_RESULTS_FILE), exist_ok=True)
    with open(EVAL_RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {EVAL_RESULTS_FILE}")


def main():
    test_data = load_test_data()
    print(f"Loaded {len(test_data)} test samples")

    results = []
    log_files = [
        ("evaluation/logs_base.json", "Base Model"),
        ("evaluation/logs_finetuned.json", "Fine-tuned"),
        ("evaluation/logs_finetuned_guardrails.json", "Fine-tuned + Guardrails"),
    ]

    for log_path, label in log_files:
        if os.path.exists(log_path):
            metrics = run_evaluation(log_path, label, test_data)
            results.append(metrics)
            print(f"Evaluated: {label}")
        else:
            print(f"Skipping {label}: {log_path} not found")

    if results:
        print_comparison_table(results)
        save_results(results)
    else:
        print("No inference logs found. Run inference first.")


if __name__ == "__main__":
    main()
