import json
import shutil
from collections import defaultdict
from pathlib import Path

ORIGINAL_NOTEBOOK = "test_notebook.ipynb"
BACKUP_NOTEBOOK = "test_notebook_backup.ipynb"
TEST_CASES_PATH = "tests.json"


def run_eval_suite(agent, test_cases_path: str = TEST_CASES_PATH):
    # Backup notebook before tests
    shutil.copy(ORIGINAL_NOTEBOOK, BACKUP_NOTEBOOK)

    # Load test cases from JSON file
    with open(test_cases_path, "r") as f:
        test_cases = json.load(f)

    category_metrics = defaultdict(lambda: {"TP": 0, "FP": 0, "FN": 0})
    system_metrics = {"TP": 0, "FP": 0, "FN": 0}

    for category, prompts in test_cases.items():
        for test_case in prompts:
            command = test_case["command"]
            expected_tools = set(test_case["expected_tools"])

            print("\n============================")
            print(f"🔍 Prompt: {command}")
            print(f"📌 Expected tools: {expected_tools}")

            # Run agent
            config = {"configurable": {"thread_id": "thread-1"}}
            state = {"messages": [{"role": "user", "content": command}], "file_path": ORIGINAL_NOTEBOOK}
            output_state = agent.invoke(state, config)

            actual_tools = set()
            for msg in output_state["messages"]:
                additional = getattr(msg, "additional_kwargs", {})
                if "tool_calls" in additional:
                    for call in additional["tool_calls"]:
                        actual_tools.add(call["function"]["name"])

            # Calculate scores
            TP = len(expected_tools & actual_tools)
            FP = len(actual_tools - expected_tools)
            FN = len(expected_tools - actual_tools)

            category_metrics[category]["TP"] += TP
            category_metrics[category]["FP"] += FP
            category_metrics[category]["FN"] += FN

            system_metrics["TP"] += TP
            system_metrics["FP"] += FP
            system_metrics["FN"] += FN

            precision = TP / (TP + FP) if (TP + FP) > 0 else 0
            recall = TP / (TP + FN) if (TP + FN) > 0 else 0

            print(f"✅ Actual tools: {actual_tools}")
            print(f"🎯 TP={TP}, FP={FP}, FN={FN}")
            print(f"📈 Precision: {precision:.2f}, Recall: {recall:.2f}")

            # Restore notebook to original state after each test
            shutil.copy(BACKUP_NOTEBOOK, ORIGINAL_NOTEBOOK)

    # Final metrics summary
    print("\n============================")
    print("🔷 CATEGORY-WISE METRICS 🔷")
    for category, metrics in category_metrics.items():
        TP, FP, FN = metrics["TP"], metrics["FP"], metrics["FN"]
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        print(f"\n📂 {category.upper()}")
        print(f"Precision: {precision:.2f}, Recall: {recall:.2f}")

    TP, FP, FN = system_metrics["TP"], system_metrics["FP"], system_metrics["FN"]
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0

    print("\n============================")
    print("🔷 OVERALL SYSTEM METRICS 🔷")
    print(f"Precision: {precision:.2f}, Recall: {recall:.2f}")
