# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Eval Coach is an Agent Skill that guides users through building AI evaluation strategies using Evaluation-Driven Development (EDD). It follows the [Agent Skills](https://agentskills.io) open standard (SKILL.md format).

This is primarily a **documentation and template repository** - it provides guidance, templates, and examples rather than a runnable application.

## Key Concepts

### 5-Step Framework
1. Define Success - Map business goals to measurable metrics
2. Design Dataset - Create test cases (50% happy path, 35% edge cases, 15% adversarial)
3. Select Methods - Choose Automated, LLM-as-Judge, or Human evaluation
4. Plan Automation - Integrate evals into CI/CD
5. Monitor Production - Track drift and collect feedback

### 50-40-10 Rule (Swiss Cheese Model)
- **50% Automated** - Schema validation, keyword checks, latency ($0.00/run)
- **40% LLM-as-Judge** - Semantic quality, relevance ($0.01-0.05/run)
- **10% Human** - Subjective quality, edge cases ($5-50/run)

### Silent Failures
The most critical insight: agents can silently reconcile contradictory data instead of flagging mismatches. The `input_data_consistency_evaluator` was created specifically to catch this.

## Repository Structure

```
.claude-plugin/
  plugin.json     # Plugin manifest for marketplace compatibility
templates/
  dataset.py      # LangSmith dataset creation with test case examples
  evaluators.py   # 10 evaluators: automated, LLM-as-Judge, performance
  compare.py      # Experiment comparison utilities
examples/
  research_agent_eval.md  # Complete evaluation plan example
SKILL.md          # Agent skill definition (triggers, workflow steps)
```

## Template Dependencies

```bash
pip install langsmith langchain-google-genai
```

## Configuration

```bash
export GOOGLE_API_KEY="your-api-key"
export JUDGE_MODEL="gemini-3-flash-preview"  # Default
export JUDGE_MODEL="gemini-3-pro-preview"    # For higher quality
```

## Evaluator Types in templates/evaluators.py

| Evaluator | Type | Purpose |
|-----------|------|---------|
| `schema_evaluator` | Automated | Check expected fields present |
| `keyword_coverage_evaluator` | Automated | Check keywords mentioned |
| `report_length_evaluator` | Automated | Validate response length |
| `graceful_error_evaluator` | Automated | Verify error handling |
| `latency_evaluator` | Performance | Check completion time |
| `token_efficiency_evaluator` | Performance | Monitor token usage |
| `quality_evaluator` | LLM-as-Judge | Assess output quality (5-point rubric) |
| `relevance_evaluator` | LLM-as-Judge | Check relevance to input |
| `input_data_consistency_evaluator` | LLM-as-Judge | Detect silent data reconciliation |
| `needs_human_review` | Flagging | Flag cases needing human review |

## Running Templates

```bash
# Create dataset in LangSmith
python templates/dataset.py

# Use evaluators in your project
from templates.evaluators import ALL_EVALUATORS, AUTOMATED_EVALUATORS, LLM_JUDGE_EVALUATORS
```

## Skill Invocation

The skill is triggered by `/eval-coach` or keywords: "eval", "evaluation", "testing strategy", "test cases", "LLM testing".

## Skill Workflow (v1.1.0)

When running `/eval-coach`, the skill follows a structured 7-step workflow:

| Step | Action | Tools Used |
|------|--------|------------|
| 0 | Initialize & gather context | TodoWrite |
| 1 | Define Success | AskUserQuestion |
| 2 | Design Dataset | AskUserQuestion |
| 3 | Select Methods | AskUserQuestion |
| 4 | Plan Automation | AskUserQuestion |
| 5 | Monitor Production | AskUserQuestion |
| 6 | Generate Output | Write |

Each step updates TodoWrite for progress visibility.
