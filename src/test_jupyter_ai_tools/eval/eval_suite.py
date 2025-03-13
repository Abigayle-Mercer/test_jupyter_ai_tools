import json
import shutil
from collections import defaultdict
from pathlib import Path
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import os

BASE_NOTEBOOK = "tests/test_notebook.ipynb"
WORKING_NOTEBOOK = "tests/test_notebook_temp.ipynb"
TEST_CASES_PATH = "tests/tests.json"

console = Console()

def print_rich_test_result(command, expected_tools, actual_tools, TP, FP, FN, precision, recall):
    console.rule(f"[bold yellow]📝 Prompt: {command}", style="bright_yellow")

    table = Table(title="🔍 Tool Evaluation", box=box.ROUNDED, show_lines=True)
    table.add_column("Tool", style="cyan", justify="left")
    table.add_column("Expected", style="green", justify="center")
    table.add_column("Used", style="magenta", justify="center")

    all_tools = sorted(expected_tools | actual_tools)
    for tool in all_tools:
        exp = "✅" if tool in expected_tools else ""
        act = "✅" if tool in actual_tools else ""
        table.add_row(tool, exp, act)

    console.print(table)

    metrics_panel = Panel.fit(
        f"[bold green]✅ TP:[/] {TP}    [bold red]❌ FP:[/] {FP}    [bold yellow]🔍 FN:[/] {FN}\n"
        f"[bold blue]🎯 Precision:[/] {precision:.2f}    [bold purple]📈 Recall:[/] {recall:.2f}",
        title="📊 Metrics", border_style="bold white"
    )
    console.print(metrics_panel)



class ToolTrackingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.tools_used = []

    def on_tool_start(self, tool, input_str, **kwargs):
        if isinstance(tool, dict) and "name" in tool:
            self.tools_used.append(tool["name"])
        else:
            self.tools_used.append(str(tool))


def run_eval_suite(agent, test_cases_path: str = TEST_CASES_PATH):
    # Load test cases from JSON file
    with open(test_cases_path, "r") as f:
        test_cases = json.load(f)

    category_metrics = defaultdict(lambda: {"TP": 0, "FP": 0, "FN": 0})
    system_metrics = {"TP": 0, "FP": 0, "FN": 0}

    for category, prompts in test_cases.items():
        for test_case in prompts:
            shutil.copy(BASE_NOTEBOOK, WORKING_NOTEBOOK)
            command = test_case["command"]
            expected_tools = set(test_case["expected_tools"])

            # ✅ Track tools via callback
            full_prompt = f"{command} 📁 You are editing notebook `{WORKING_NOTEBOOK}`."


            # ✅ Track tools via callback
            tracker = ToolTrackingCallbackHandler()

            state = {"messages":  [{"role": "user", "content": full_prompt}], "file_path": WORKING_NOTEBOOK}


            config = {"configurable": {"thread_id": "thread-1"}, "callbacks": [tracker]}
            agent.invoke(state, config=config)

            actual_tools = set(tracker.tools_used)


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

            print_rich_test_result(command, expected_tools, actual_tools, TP, FP, FN, precision, recall)

    if os.path.exists(WORKING_NOTEBOOK):
        os.remove(WORKING_NOTEBOOK)
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
