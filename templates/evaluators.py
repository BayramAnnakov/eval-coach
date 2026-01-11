"""Evaluator templates for LangSmith.

This template provides common evaluator patterns you can customize.

Evaluator Types:
- Automated (Tier 1): Free, fast, deterministic
- LLM-as-Judge (Tier 2): Semantic understanding, ~$0.01-0.05/run
- Human-in-Loop (Tier 3): Flag for review, $5-50/run

Configuration:
- Set JUDGE_MODEL env var to customize LLM judge (default: gemini-3-flash-preview)
"""

import json
import os
from langsmith.schemas import Run, Example
from langchain_google_genai import ChatGoogleGenerativeAI

# Configurable judge model - set JUDGE_MODEL env var to override
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gemini-3-flash-preview")


# === TIER 1: AUTOMATED EVALUATORS ===

def schema_evaluator(run: Run, example: Example) -> dict:
    """Check if output contains expected fields.

    Customize: Update expected_fields in your test cases.
    """
    output = run.outputs or {}
    expected = example.outputs.get("expected_fields", [])

    if not expected:
        return {"key": "schema_valid", "score": 1.0, "comment": "No expected fields defined"}

    present = [f for f in expected if output.get(f) is not None]
    missing = [f for f in expected if f not in present]
    score = len(present) / len(expected)

    comment = f"All fields present ({len(present)}/{len(expected)})" if score == 1.0 else f"Missing: {missing}"
    return {"key": "schema_valid", "score": score, "comment": comment}


def keyword_coverage_evaluator(run: Run, example: Example) -> dict:
    """Check if output contains expected keywords.

    Customize: Update should_mention in your test cases.
    """
    output = run.outputs or {}
    should_mention = example.outputs.get("should_mention", [])

    if not should_mention:
        return {"key": "keyword_coverage", "score": 1.0, "comment": "No keywords to check"}

    # Check all output fields for keywords
    output_text = json.dumps(output).lower()
    found = [kw for kw in should_mention if kw.lower() in output_text]
    missing = [kw for kw in should_mention if kw.lower() not in output_text]
    score = len(found) / len(should_mention)

    comment = f"All keywords found ({len(found)}/{len(should_mention)})" if score == 1.0 else f"Missing: {missing}"
    return {"key": "keyword_coverage", "score": score, "comment": comment}


def report_length_evaluator(run: Run, example: Example) -> dict:
    """Check if output meets length requirements.

    Customize: Update min_report_length in your test cases.
    """
    output = run.outputs or {}
    # Try common output field names
    response = output.get("final_report", "") or output.get("output", "") or output.get("response", "")

    min_len = example.outputs.get("min_report_length", 0)
    if not min_len:
        return {"key": "report_length", "score": 1.0, "comment": "No minimum length defined"}

    actual = len(response)
    score = min(1.0, actual / min_len)

    if score < 1.0:
        comment = f"Too short: {actual} chars < {min_len} minimum"
    else:
        comment = f"Length OK: {actual} chars"

    return {"key": "report_length", "score": score, "comment": comment}


def graceful_error_evaluator(run: Run, example: Example) -> dict:
    """Check if agent handles error cases gracefully.

    Customize: Set should_handle_gracefully: true in adversarial test cases.
    """
    should_handle = example.outputs.get("should_handle_gracefully", False)

    if not should_handle:
        return {"key": "graceful_error", "score": 1.0, "comment": "Not an error case"}

    # Check if agent crashed
    if run.error:
        return {"key": "graceful_error", "score": 0.0, "comment": f"Agent crashed: {run.error}"}

    # Check if there's still output
    output = run.outputs or {}
    has_output = bool(output.get("final_report") or output.get("output") or output.get("response"))

    if has_output:
        return {"key": "graceful_error", "score": 1.0, "comment": "Handled gracefully with output"}
    else:
        return {"key": "graceful_error", "score": 0.5, "comment": "No crash but no output either"}


# === TIER 1: PERFORMANCE EVALUATORS ===

def latency_evaluator(run: Run, example: Example) -> dict:
    """Check if agent completes within acceptable time.

    Default threshold: 30 seconds. Override with max_latency_seconds in test case.
    """
    max_latency = example.outputs.get("max_latency_seconds", 30)

    if not run.start_time or not run.end_time:
        return {"key": "latency_seconds", "score": 0.5, "comment": "No timing data available"}

    latency = (run.end_time - run.start_time).total_seconds()
    score = max(0.0, 1.0 - (latency / max_latency))

    return {
        "key": "latency_seconds",
        "score": score,
        "comment": f"{latency:.2f}s (threshold: {max_latency}s)",
    }


def token_efficiency_evaluator(run: Run, example: Example) -> dict:
    """Check if agent uses tokens efficiently.

    Default threshold: 10,000 tokens. Override with max_tokens in test case.
    """
    max_tokens = example.outputs.get("max_tokens", 10000)

    # Try to get token usage from run metadata
    extra = run.extra or {}
    token_usage = extra.get("token_usage", {})
    total_tokens = token_usage.get("total_tokens", 0)

    if not total_tokens:
        return {"key": "token_efficiency", "score": 0.5, "comment": "No token data available"}

    score = max(0.0, 1.0 - (total_tokens / max_tokens))

    return {
        "key": "token_efficiency",
        "score": score,
        "comment": f"{total_tokens} tokens (threshold: {max_tokens})",
    }


# === TIER 2: LLM-AS-JUDGE EVALUATORS ===

def quality_evaluator(run: Run, example: Example) -> dict:
    """Evaluate output quality using LLM-as-Judge.

    Customize: Update the rubric in the prompt below.
    """
    output = run.outputs or {}
    response = output.get("final_report", "") or output.get("output", "") or output.get("response", "")

    if not response:
        return {"key": "quality", "score": 0.0, "comment": "No output to evaluate"}

    judge_prompt = f"""Evaluate this output on a scale of 1-5.

Output to evaluate:
{response[:3000]}

Rubric:
- 5: Excellent - comprehensive, accurate, well-structured
- 4: Good - mostly complete, minor issues
- 3: Adequate - basic but acceptable
- 2: Poor - significant issues
- 1: Failing - incorrect or unusable

Return JSON: {{"score": 1-5, "reasoning": "brief explanation"}}
"""

    try:
        llm = ChatGoogleGenerativeAI(model=JUDGE_MODEL, temperature=0)
        result = llm.invoke(judge_prompt)
        parsed = json.loads(result.content)

        return {
            "key": "quality",
            "score": parsed["score"] / 5.0,
            "comment": parsed.get("reasoning", ""),
        }
    except Exception as e:
        return {"key": "quality", "score": 0.5, "comment": f"Judge error: {e}"}


def relevance_evaluator(run: Run, example: Example) -> dict:
    """Check if output is relevant to input.

    Customize: Update relevance criteria in the prompt.
    """
    inputs = run.inputs or {}
    output = run.outputs or {}

    query = inputs.get("query", "") or inputs.get("target", "") or str(inputs)[:500]
    response = output.get("final_report", "") or output.get("output", "") or output.get("response", "")

    if not response:
        return {"key": "relevance", "score": 0.0, "comment": "No output to evaluate"}

    judge_prompt = f"""Is this response relevant to the query?

Query: {query}
Response: {response[:2000]}

Score 1-5:
- 5: Directly addresses the query
- 3: Partially relevant
- 1: Off-topic or irrelevant

Return JSON: {{"score": 1-5, "reasoning": "brief explanation"}}
"""

    try:
        llm = ChatGoogleGenerativeAI(model=JUDGE_MODEL, temperature=0)
        result = llm.invoke(judge_prompt)
        parsed = json.loads(result.content)

        return {
            "key": "relevance",
            "score": parsed["score"] / 5.0,
            "comment": parsed.get("reasoning", ""),
        }
    except Exception as e:
        return {"key": "relevance", "score": 0.5, "comment": f"Judge error: {e}"}


def input_data_consistency_evaluator(run: Run, example: Example) -> dict:
    """Check if report conclusions match the gathered source data.

    CRITICAL: This evaluator catches when an agent silently reconciles
    contradictory information instead of flagging it or asking for clarification.

    Example: User provides company="Anthropic" but LinkedIn shows company="onsa.ai"
    - BAD: Agent writes "engaged with Anthropic via community work" (silent reconciliation)
    - GOOD: Agent flags the mismatch explicitly
    """
    inputs = run.inputs or {}
    output = run.outputs or {}

    # Get relevant fields - adjust these to match your agent's input/output structure
    target = inputs.get("linkedin_url", "") or inputs.get("target", "")
    company = inputs.get("company_name", "") or inputs.get("company", "")
    report = output.get("final_report", "") or output.get("output", "") or output.get("response", "")

    if not report or not company:
        return {"key": "input_data_consistency", "score": 1.0, "comment": "No company/report to verify"}

    judge_prompt = f"""Analyze this research report for input-data consistency.

USER INPUT:
- Target: {target}
- Company claimed: {company}

REPORT:
{report[:3000]}

QUESTIONS:
1. Does the report confirm the person actually works at "{company}"?
2. If the source data shows a DIFFERENT company, did the agent:
   a) Explicitly flag the mismatch? (GOOD)
   b) Silently reconcile by finding tangential connections? (BAD)
   c) Ignore the mismatch entirely? (BAD)

SCORING:
- 1.0: Data matches OR agent explicitly flagged mismatch
- 0.5: Minor discrepancy, agent partially addressed
- 0.0: Major mismatch silently reconciled (hallucination risk)

Return JSON: {{"score": 0.0-1.0, "mismatch_found": true/false, "reasoning": "explanation"}}
"""

    try:
        llm = ChatGoogleGenerativeAI(model=JUDGE_MODEL, temperature=0)
        response = llm.invoke(judge_prompt)
        result = json.loads(response.content)
        return {
            "key": "input_data_consistency",
            "score": result.get("score", 0.5),
            "comment": f"Mismatch: {result.get('mismatch_found', 'unknown')} - {result.get('reasoning', '')}",
        }
    except Exception as e:
        return {"key": "input_data_consistency", "score": 0.5, "comment": f"Judge error: {e}"}


# === TIER 3: HUMAN-IN-THE-LOOP ===

def needs_human_review(run: Run, example: Example) -> dict:
    """Flag cases that need human review.

    Customize: Update the flagging heuristics below.
    """
    output = run.outputs or {}
    response = output.get("final_report", "") or output.get("output", "") or output.get("response", "")

    # Customize these heuristics
    needs_review = (
        len(response) < 200 or              # Too short
        "error" in response.lower() or      # Contains error
        "sorry" in response.lower() or      # Apology (often indicates failure)
        "unable to" in response.lower() or  # Inability
        run.error is not None               # Agent crashed
    )

    return {
        "key": "needs_human_review",
        "score": 0.0 if needs_review else 1.0,
        "comment": "Flagged for human review" if needs_review else "Auto-approved",
    }


# === EVALUATOR COLLECTIONS ===

AUTOMATED_EVALUATORS = [
    schema_evaluator,
    keyword_coverage_evaluator,
    report_length_evaluator,
    graceful_error_evaluator,
]

PERFORMANCE_EVALUATORS = [
    latency_evaluator,
    token_efficiency_evaluator,
]

LLM_JUDGE_EVALUATORS = [
    quality_evaluator,
    relevance_evaluator,
    input_data_consistency_evaluator,
]

ALL_EVALUATORS = AUTOMATED_EVALUATORS + PERFORMANCE_EVALUATORS + LLM_JUDGE_EVALUATORS + [needs_human_review]
