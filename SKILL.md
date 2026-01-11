---
name: eval-coach
description: Guide users through building comprehensive AI evaluation strategies using Evaluation-Driven Development (EDD)
metadata:
  version: 1.0.0
  author: Bayram Annakov
  triggers:
    - eval
    - evaluation
    - testing strategy
    - test cases
    - LLM testing
---

# Eval Coach

An Agent Skill for designing comprehensive AI evaluation strategies using Evaluation-Driven Development (EDD).

## Overview

Eval Coach guides you through a structured 5-step framework for evaluating LLM applications:

1. **Define Success** - Map business goals to measurable metrics
2. **Design Dataset** - Create diverse test cases (happy path, edge cases, adversarial)
3. **Select Methods** - Choose Automated, LLM-as-Judge, or Human evaluation
4. **Plan Automation** - Integrate evals into CI/CD
5. **Monitor Production** - Track drift and collect feedback

## When to Use This Skill

Invoke this skill when:
- Starting a new AI project and need an evaluation strategy
- Improving an existing agent's reliability
- Comparing different implementation approaches
- Setting up CI/CD for AI products
- Debugging production quality issues

## Evaluation Philosophy

### The 50-40-10 Rule
- **50% Automated** - Schema validation, keyword checks, latency ($0.00/run)
- **40% LLM-as-Judge** - Semantic quality, relevance ($0.01-0.05/run)
- **10% Human** - Subjective quality, edge cases ($5-50/run)

### Start Small, Iterate
- Begin with 20 high-quality test cases, not 1000 noisy ones
- Distribution: 50% happy path, 35% edge cases, 15% adversarial
- Add cases as you discover production failures

## Guidance Framework

### Step 1: Define Success

Ask the user:
1. What is your product's primary goal?
2. What does success look like for a user?
3. What are the failure modes that would hurt users or business?
4. How would you manually judge if an output is "good"?

From answers, help define:
- **Primary metrics** (e.g., accuracy, relevance, helpfulness)
- **Secondary metrics** (e.g., latency, cost, safety)
- **Threshold targets** (e.g., 95% accuracy, <5s latency)

### Step 2: Design Dataset

Guide creation of test cases:

```yaml
# Test Case Template
name: descriptive_name
category: happy_path | edge_case | adversarial
inputs:
  # The inputs your agent receives
  query: "user query here"
  context: "any context"
outputs:
  # What to validate
  expected_fields: [field1, field2]
  should_mention: [keyword1, keyword2]
  should_not_contain: [forbidden_term]
  min_length: 100
  max_length: 5000
```

Categories:
- **Happy Path (50%)**: Common, expected inputs
- **Edge Cases (35%)**: Unusual but valid inputs, boundary conditions
- **Adversarial (15%)**: Invalid inputs, prompt injection, error conditions

### Step 3: Select Methods

Match methods to evaluation needs:

| What to Measure | Method | Cost | When |
|----------------|--------|------|------|
| Schema/format | Automated | Free | Always (CI) |
| Keywords present | Automated | Free | Always (CI) |
| Semantic quality | LLM-as-Judge | $0.01-0.05 | Pre-deploy |
| Relevance to input | LLM-as-Judge | $0.01-0.05 | Pre-deploy |
| Input-Data Consistency | LLM-as-Judge | $0.01-0.05 | Pre-deploy |
| Subjective quality | Human | $5-50 | Edge cases |
| Safety/compliance | Human + Automated | Varies | Always |

### Step 4: Plan Automation

Integration tiers:

**Tier 1: PR-Level (<5 min)**
- Automated tests only
- Run on every PR
- Block merge on failure

**Tier 2: Pre-Deploy (15-30 min)**
- Full test suite including LLM-as-Judge
- Run before production deployment
- Compare to baseline metrics

**Tier 3: Production Monitoring (Continuous)**
- Sample real traffic for evaluation
- Track drift over time
- Alert on metric degradation

### Step 5: Monitor Production

Track these signals:

1. **Data Drift** - Input distribution changing
2. **Concept Drift** - User expectations changing
3. **Model Drift** - Provider silently updating model
4. **Task Drift** - Users asking for new capabilities

Recommendation: Pin model versions, run weekly evals on production samples.

## Output Format

After completing the framework, provide:

```markdown
## Evaluation Plan for [Product Name]

### Business Objectives
- Primary goal: [goal]
- Success criteria: [criteria]

### Dataset Strategy
- Total test cases: [N]
- Happy path: [N1] cases
- Edge cases: [N2] cases
- Adversarial: [N3] cases

### Evaluation Methods
| Metric | Type | Method | Threshold |
|--------|------|--------|-----------|
| ... | ... | ... | ... |

### CI/CD Integration
- PR checks: [list]
- Pre-deploy: [list]
- Monitoring: [list]

### Next Steps
1. [First action]
2. [Second action]
3. [Third action]
```

## Templates

This skill includes starter templates in the `templates/` directory:
- `dataset.py` - LangSmith dataset creation
- `evaluators.py` - Common evaluator implementations
- `compare.py` - Experiment comparison utilities

## Examples

See `examples/` for complete evaluation plans:
- `research_agent_eval.md` - Multi-agent research system evaluation

## Related Resources

- [LangSmith Evaluation Guide](https://docs.smith.langchain.com/evaluation)
- [Anthropic Evaluation Best Practices](https://docs.anthropic.com/claude/docs/testing-and-evaluation)
- [OpenAI Evaluation Cookbook](https://cookbook.openai.com/examples/evaluation)
