"""Experiment comparison utilities for LangSmith.

This template provides starter code for comparing different implementations.

Usage:
    1. Run evaluations on different implementations
    2. Use compare_experiments() to see results
    3. Analyze differences to make data-driven decisions
"""

from langsmith import Client
from langsmith.evaluation import evaluate
import json

client = Client()


def run_evaluation(
    agent_fn,
    dataset_name: str,
    evaluators: list,
    experiment_prefix: str,
    metadata: dict = None,
):
    """Run evaluation and return results.

    Args:
        agent_fn: Function to evaluate (takes inputs dict, returns outputs dict)
        dataset_name: Name of LangSmith dataset to use
        evaluators: List of evaluator functions
        experiment_prefix: Prefix for experiment name (e.g., "langgraph_v1")
        metadata: Optional metadata to attach to experiment

    Returns:
        Evaluation results object
    """
    results = evaluate(
        agent_fn,
        data=dataset_name,
        evaluators=evaluators,
        experiment_prefix=experiment_prefix,
        metadata=metadata or {},
    )

    return results


def compare_experiments(
    experiment_names: list[str],
    metrics: list[str] = None,
) -> dict:
    """Compare multiple experiments side-by-side.

    Args:
        experiment_names: List of experiment names/prefixes to compare
        metrics: List of metric keys to compare (defaults to all)

    Returns:
        Comparison dict with metrics for each experiment
    """
    comparison = {}

    for exp_name in experiment_names:
        # Get experiment results
        experiments = list(client.list_runs(
            project_name=exp_name,
            is_root=True,
        ))

        if not experiments:
            print(f"Warning: No runs found for {exp_name}")
            continue

        # Aggregate metrics
        exp_metrics = {}
        for run in experiments:
            if run.feedback_stats:
                for key, stats in run.feedback_stats.items():
                    if metrics and key not in metrics:
                        continue
                    if key not in exp_metrics:
                        exp_metrics[key] = []
                    exp_metrics[key].append(stats.get("avg", 0))

        # Calculate averages
        comparison[exp_name] = {
            key: sum(vals) / len(vals) if vals else 0
            for key, vals in exp_metrics.items()
        }

    return comparison


def print_comparison(comparison: dict):
    """Print comparison results in a readable format."""
    if not comparison:
        print("No comparison data available")
        return

    # Get all metric keys
    all_metrics = set()
    for exp_metrics in comparison.values():
        all_metrics.update(exp_metrics.keys())

    # Print header
    exp_names = list(comparison.keys())
    header = f"{'Metric':<25} | " + " | ".join(f"{name:<15}" for name in exp_names)
    print(header)
    print("-" * len(header))

    # Print each metric
    for metric in sorted(all_metrics):
        row = f"{metric:<25} | "
        values = []
        for exp_name in exp_names:
            val = comparison[exp_name].get(metric, 0)
            values.append(val)
            row += f"{val:>15.3f} | "
        print(row)

        # Highlight winner
        if values and max(values) != min(values):
            winner_idx = values.index(max(values))
            print(f"  -> Best: {exp_names[winner_idx]}")


def generate_report(comparison: dict, output_file: str = None) -> str:
    """Generate a markdown comparison report.

    Args:
        comparison: Comparison dict from compare_experiments()
        output_file: Optional file path to save report

    Returns:
        Markdown report string
    """
    report = ["# Experiment Comparison Report\n"]

    if not comparison:
        report.append("No comparison data available.\n")
        return "\n".join(report)

    # Summary table
    report.append("## Summary\n")
    report.append("| Metric | " + " | ".join(comparison.keys()) + " |")
    report.append("|" + "---|" * (len(comparison) + 1))

    all_metrics = set()
    for exp_metrics in comparison.values():
        all_metrics.update(exp_metrics.keys())

    for metric in sorted(all_metrics):
        row = f"| {metric} |"
        values = []
        for exp_name in comparison:
            val = comparison[exp_name].get(metric, 0)
            values.append(val)
            # Bold the best value
            if values and val == max(values):
                row += f" **{val:.3f}** |"
            else:
                row += f" {val:.3f} |"
        report.append(row)

    # Recommendations
    report.append("\n## Recommendations\n")

    # Find overall winner
    totals = {exp: sum(metrics.values()) for exp, metrics in comparison.items()}
    winner = max(totals, key=totals.get)
    report.append(f"- **Overall Best**: {winner} (highest total score)")

    if output_file:
        with open(output_file, "w") as f:
            f.write("\n".join(report))
        print(f"Report saved to: {output_file}")

    return "\n".join(report)


# === EXAMPLE USAGE ===

if __name__ == "__main__":
    # Example: Compare two implementations
    from templates.evaluators import ALL_EVALUATORS

    # Uncomment and customize for your use case:
    #
    # # Run evaluation on implementation A
    # results_a = run_evaluation(
    #     agent_fn=implementation_a.invoke,
    #     dataset_name="my_eval_dataset",
    #     evaluators=ALL_EVALUATORS,
    #     experiment_prefix="impl_a_v1",
    # )
    #
    # # Run evaluation on implementation B
    # results_b = run_evaluation(
    #     agent_fn=implementation_b.invoke,
    #     dataset_name="my_eval_dataset",
    #     evaluators=ALL_EVALUATORS,
    #     experiment_prefix="impl_b_v1",
    # )
    #
    # # Compare results
    # comparison = compare_experiments(["impl_a_v1", "impl_b_v1"])
    # print_comparison(comparison)
    # generate_report(comparison, "comparison_report.md")

    print("Compare template loaded. See example usage in __main__ block.")
