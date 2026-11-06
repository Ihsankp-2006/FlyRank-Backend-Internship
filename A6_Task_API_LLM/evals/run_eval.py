import json
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES_FILE = ROOT / "evals" / "cases.json"
API_URL = "http://127.0.0.1:8000/classify"

cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))

correct = 0
results = []

print("\nA6 SUPPORT TICKET CLASSIFIER EVALUATION")
print("=" * 55)

for index, case in enumerate(cases, start=1):
    payload = json.dumps({"message": case["message"]}).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=65) as response:
            output = json.loads(response.read().decode("utf-8"))

        predicted = output["category"]
        expected = case["expected_category"]
        passed = predicted == expected

        if passed:
            correct += 1

        results.append({
            "case": index,
            "expected": expected,
            "predicted": predicted,
            "passed": passed,
        })

        print(f"\nCase {index}: {'PASS' if passed else 'FAIL'}")
        print(f"Expected: {expected}")
        print(f"Predicted: {predicted}")

    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        print(f"\nCase {index}: ERROR - {exc}")

total = len(cases)
accuracy = (correct / total) * 100 if total else 0

print("\n" + "=" * 55)
print(f"Correct: {correct}/{total}")
print(f"Category accuracy: {accuracy:.2f}%")
print("Prompt version: support_ticket_v1")

report = {
    "prompt_version": "support_ticket_v1",
    "total_cases": total,
    "correct": correct,
    "accuracy_percent": accuracy,
    "results": results,
}

report_path = ROOT / "evals" / "results.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print(f"Evaluation report saved to: {report_path}")
