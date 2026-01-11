---
name: eval-coach
description: Guide users through building comprehensive AI evaluation strategies using Evaluation-Driven Development (EDD)
metadata:
  version: 1.2.0
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

### Capability vs Regression Evals

Two fundamentally different types of evaluations:

| Type | Starting Point | Goal | When Failure Occurs |
|------|---------------|------|---------------------|
| **Capability** | Near 0% | Push higher over time | Expected - iterate and improve |
| **Regression** | Near 100% | Maintain - don't drop | Alarming - investigate immediately |

**Key Insight**: Convert production bugs into regression tests. Every bug you fix becomes a test that ensures it never happens again.

### pass@k vs pass^k (Handling Non-Determinism)

Agents are probabilistic. Use the right metric:

**pass@k** = Probability of at least one success in k attempts
- Formula: `1 - (1-p)^k`
- As k increases, score rises - more "shots on goal" means higher odds of success
- **Use for coding agents** where pass@1 matters most (first try counts)
- Use when multiple solution attempts are acceptable

**pass^k** = Probability of succeeding every time in k attempts
- Formula: `p^k`
- As k increases, score falls - demanding consistency across more trials is harder
- Example: 75% per-trial rate × 3 trials = (0.75)³ ≈ 42% pass^3
- **Use for customer-facing agents** where users expect reliable behavior every time

### The 50-40-10 Rule (Swiss Cheese Model)

Each layer has blind spots, but together they cover each other:

- **50% Automated** - Schema validation, keyword checks, latency ($0.00/run)
- **40% LLM-as-Judge** - Semantic quality, relevance ($0.01-0.05/run)
- **10% Human** - Subjective quality, edge cases ($5-50/run)

### Agent-Type-Specific Approaches

Different agent types require different evaluation strategies:

| Agent Type | Primary Graders | Key Considerations | Benchmarks |
|------------|-----------------|-------------------|------------|
| **Coding** | Deterministic (tests pass?) | Static analysis, outcome verification | SWE-bench |
| **Conversational** | LLM-as-Judge + outcome | Interaction quality, turn count | τ-Bench |
| **Research** | Coverage + groundedness | Source quality validation | BrowseComp |
| **Computer Use** | UI state + backend | Sandboxed GUI, screenshot vs DOM | WebArena |

### Start Small, Iterate
- Begin with 20 high-quality test cases, not 1000 noisy ones
- Distribution: 50% happy path, 35% edge cases, 15% adversarial
- Add cases as you discover production failures
- Monitor for **eval saturation** - when all tests pass, add harder ones

### Ethical AI Evals

Build these into your core eval suite, not as an afterthought:

- **Fairness**: Test performance across demographic groups
- **Bias**: Check for stereotypical associations and harmful outputs
- **Safety**: Verify robustness to adversarial prompts

### Debugging Low Scores

When evals fail, investigate systematically:

1. **Read Your Transcripts** - Don't skip to aggregate metrics
2. **Apply the 5 WHYs** - Drill down to root cause
3. **Check**: Error patterns, prompt clarity, tool calling, model selection

**Common Pitfalls**:
- Rigid evaluation of tool call sequences instead of outcomes
- One-sided test sets favoring particular behaviors
- Taking scores at face value without reading transcripts
- Insufficient human-LLM grader calibration

## Interactive Mode (Claude Code)

When running in Claude Code, use the AskUserQuestion tool to create an interactive, guided experience. Present structured choices at each step rather than dumping all questions at once.

**Step-by-step interaction pattern:**
1. Start by asking what type of AI application they're evaluating (agent, RAG, classifier, etc.)
2. Present one step at a time with clear options
3. Use multi-select when appropriate (e.g., selecting evaluation methods)
4. Summarize choices before moving to the next step
5. Offer to revisit previous steps if needed

**Example interaction flow:**
```
Step 1: "What type of AI application are you evaluating?"
  - [ ] Agent/Assistant
  - [ ] RAG System
  - [ ] Classifier
  - [ ] Other (describe)

Step 2: "What are your primary success metrics?"
  - [ ] Accuracy/Correctness
  - [ ] Relevance
  - [ ] Latency
  - [ ] Cost efficiency
  - [ ] Safety/Compliance

Step 3: "What test case categories do you need?"
  - [ ] Happy path (common inputs)
  - [ ] Edge cases (unusual but valid)
  - [ ] Adversarial (invalid/malicious)
```

**Progress Tracking:**
Use TodoWrite at the start of each session to create trackable items:
- [ ] Step 0: Initialize & gather context
- [ ] Step 1: Define Success
- [ ] Step 2: Design Dataset
- [ ] Step 3: Select Methods
- [ ] Step 4: Plan Automation
- [ ] Step 5: Monitor Production
- [ ] Step 6: Generate Output

Mark each step complete as you finish. This gives the user visibility into progress.

## Critical Rules

- ALWAYS use AskUserQuestion tool at each step - never dump all questions at once
- ALWAYS use TodoWrite to track progress through the workflow steps
- ALWAYS ask about agent type (coding, conversational, research, computer-use) to tailor approach
- ALWAYS include ethical eval considerations (fairness, bias, safety)
- NEVER skip adversarial test cases discussion - silent failures are the most dangerous
- ALWAYS mention the input-data consistency risk (silent reconciliation of contradictory data)
- ALWAYS summarize user choices before moving to the next step
- Grade outcomes, not paths - don't enforce rigid tool-call sequences
- Mark todos as completed immediately after finishing each step

## Workflow Steps

### Step 0: Initialize

- Parse user context: Is this a new project or improving existing evals?
- Create TodoWrite items for Steps 1-6
- If user has existing agent code, read it to understand inputs/outputs
- Use AskUserQuestion: "What type of AI application are you evaluating?" (Agent, RAG, Classifier, Other)

### Step 1: Define Success

Use AskUserQuestion to gather:
1. What is your product's primary goal?
2. What does success look like for a user?
3. What are the failure modes that would hurt users or business?
4. How would you manually judge if an output is "good"?

From answers, help define:
- **Primary metrics** (e.g., accuracy, relevance, helpfulness)
- **Secondary metrics** (e.g., latency, cost, safety)
- **Threshold targets** (e.g., 95% accuracy, <5s latency)

Mark Step 1 complete in TodoWrite.

### Step 2: Design Dataset

Use AskUserQuestion to ask about test case distribution preference (recommend 50-35-15).

Guide creation of test cases using template:

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

**CRITICAL**: Always include adversarial cases that test for silent failures - when the agent reconciles contradictory data instead of flagging it.

Mark Step 2 complete in TodoWrite.

### Step 3: Select Methods

Use AskUserQuestion to present the 50-40-10 rule with cost breakdown. Ask which evaluation tiers to include.

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

Map user's metrics (from Step 1) to appropriate methods. Summarize choices before proceeding.

Mark Step 3 complete in TodoWrite.

### Step 4: Plan Automation

Use AskUserQuestion to ask about CI/CD preferences and recommend tier structure.

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

Mark Step 4 complete in TodoWrite.

### Step 5: Monitor Production

Use AskUserQuestion to discuss monitoring needs and drift types.

Track these signals:

1. **Data Drift** - Input distribution changing
2. **Concept Drift** - User expectations changing
3. **Model Drift** - Provider silently updating model
4. **Task Drift** - Users asking for new capabilities

Recommendation: Pin model versions, run weekly evals on production samples.

Mark Step 5 complete in TodoWrite.

### Step 6: Generate Output

- Write evaluation plan in the standard format below
- Offer to create `dataset.py` with their specific test cases
- Suggest relevant evaluators from `templates/evaluators.py`
- Mark Step 6 complete in TodoWrite

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
- [Anthropic: Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Claude Console Evaluation Tool](https://docs.claude.com/en/docs/test-and-evaluate/eval-tool)
- [Promptfoo](https://promptfoo.dev) - YAML-based eval configuration
- [Braintrust](https://braintrustdata.com) - Evaluation + observability
- [Langfuse](https://langfuse.com) - Open-source tracing + evals
