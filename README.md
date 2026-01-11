# Eval Coach

An Agent Skill for designing comprehensive AI evaluation strategies using Evaluation-Driven Development (EDD).

## About

Created by [Bayram Annakov](https://linkedin.com/in/bayramannakov) while building [Onsa.ai](https://onsa.ai) - AI agents for B2B sales prospecting.

If you find this useful, say hi on LinkedIn!

## What is Eval Coach?

Eval Coach guides you through a structured 5-step framework for evaluating LLM applications:

1. **Define Success** - Map business goals to measurable metrics
2. **Design Dataset** - Create diverse test cases (happy path, edge cases, adversarial)
3. **Select Methods** - Choose Automated, LLM-as-Judge, or Human evaluation
4. **Plan Automation** - Integrate evals into CI/CD
5. **Monitor Production** - Track drift and collect feedback

## Installation

### Claude Code / Cursor / VS Code

Copy this skill to your project's skills directory:

```bash
git clone https://github.com/bayramannakov/eval-coach-skill.git ~/.claude/skills/eval-coach
```

Or add to your project:

```bash
mkdir -p skills
git clone https://github.com/bayramannakov/eval-coach-skill.git skills/eval-coach
```

### Usage

Invoke the skill by name or with trigger keywords:

```
/eval-coach
```

Or just mention evaluation-related topics:
- "help me create an evaluation strategy"
- "design test cases for my agent"
- "set up LLM testing"

## The 50-40-10 Rule

A practical distribution for evaluation methods:

| Tier | Method | Cost | Percentage |
|------|--------|------|------------|
| 1 | Automated (schema, keywords, latency) | $0.00/run | 50% |
| 2 | LLM-as-Judge (quality, relevance) | $0.01-0.05/run | 40% |
| 3 | Human Review | $5-50/run | 10% |

## Templates Included

- **`templates/dataset.py`** - LangSmith dataset creation with example test cases
- **`templates/evaluators.py`** - 10 ready-to-use evaluators (automated, LLM-as-Judge, performance)
- **`templates/compare.py`** - Experiment comparison utilities

## Key Insight: Silent Failures

The most dangerous failures are the ones your tests don't catch. The `input_data_consistency_evaluator` was born from a real production issue:

> We ran an agent with `--target john_smith --company CompanyA`, but John actually works at CompanyB. The agent **silently reconciled** the contradiction by writing "engaged with CompanyA via partnerships" instead of flagging the mismatch. All 9 evaluators passed, but the output was misleading.

Always include adversarial test cases that probe for silent failures.

## Agent Skill Standard

This skill follows the [Agent Skills](https://agentskills.io) open standard (SKILL.md format), supported by:
- Claude Code
- Cursor
- VS Code with AI extensions
- Gemini CLI
- OpenAI Codex

## Requirements

For the templates:
- Python 3.9+
- LangSmith account (for dataset management)
- OpenAI API key (for LLM-as-Judge evaluators)

```bash
pip install langsmith langchain-openai
```

## Configuration

Set the judge model via environment variable:

```bash
export JUDGE_MODEL="gpt-4o-mini"  # Default
export JUDGE_MODEL="gpt-4o"      # For higher quality judging
```

## License

MIT License - see [LICENSE](LICENSE)

## Related Resources

- [LangSmith Evaluation Guide](https://docs.smith.langchain.com/evaluation)
- [Anthropic Evaluation Best Practices](https://docs.anthropic.com/claude/docs/testing-and-evaluation)
- [Agent Skills Specification](https://agentskills.io/specification)
