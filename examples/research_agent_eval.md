# Evaluation Plan: Research Agent

Example evaluation plan for a research agent that gathers information about people and companies.

## Business Objectives

**Primary Goal**: Provide actionable intelligence for outreach and research

**Success Criteria**:
- Reports contain specific, verifiable information
- Data is accurate and matches source materials
- Latency under 30 seconds for standard requests

**Failure Modes**:
- Generic, non-specific information
- Incorrect or outdated data
- **Silent reconciliation of contradictory data** (see AD-1 below)
- Missing key information
- Reports that are too long or too short

## Dataset Strategy

**Total Test Cases**: 21

### Happy Path (10 cases - 48%)
| ID | Description | Key Validation |
|----|-------------|----------------|
| HP-1 | Tech executive (large company) | Should mention company focus areas |
| HP-2 | Tech executive (AI company) | Should mention AI, technology stack |
| HP-3 | Startup founder | Should identify startup stage |
| HP-4 | Sales executive | Should identify sales focus |
| HP-5 | Engineering leader | Should identify technical focus |
| HP-6 | Healthcare executive | Should identify industry context |
| HP-7 | Finance director | Should identify finance focus |
| HP-8 | Marketing leader | Should identify marketing focus |
| HP-9 | Product manager | Should identify product focus |
| HP-10 | International executive | Should handle non-US context |

### Edge Cases (7 cases - 35%)
| ID | Description | Key Validation |
|----|-------------|----------------|
| EC-1 | No company provided | Should infer from profile |
| EC-2 | Very long profile URL | Should handle gracefully |
| EC-3 | Non-English name | Should handle Unicode |
| EC-4 | Acquired company | Should note acquisition |
| EC-5 | Person with multiple roles | Should identify current role |
| EC-6 | Minimal profile | Should handle limited data |
| EC-7 | Private/stealth company | Should handle missing data |

### Adversarial Cases (4 cases - 20%)
| ID | Description | Key Validation |
|----|-------------|----------------|
| AD-1 | **Data Mismatch** - User provides wrong company | Should FLAG mismatch, not silently reconcile |
| AD-2 | Invalid URL | Should return error gracefully |
| AD-3 | Non-existent profile | Should indicate not found |
| AD-4 | Malformed input | Should handle gracefully |

> **Real-World Example (AD-1)**: We ran an agent with `--target john_smith --company CompanyA`, but John actually works at CompanyB. The agent gathered accurate source data but **silently reconciled** the contradiction by writing "engaged with CompanyA via partnerships" instead of flagging the mismatch. All automated evaluators passed, but the output was misleading. This case caught our blind spot.

## Evaluation Methods

| Metric | Type | Method | Threshold |
|--------|------|--------|-----------|
| Schema Valid | Automated | Check fields present | 100% |
| Keywords Present | Automated | Check for expected terms | 80% |
| Report Length | Automated | 200-2000 chars | 100% |
| Graceful Errors | Automated | No crashes on edge cases | 100% |
| Research Quality | LLM-as-Judge | 5-point rubric | 4.0/5.0 |
| Relevance | LLM-as-Judge | Matches target person | 4.0/5.0 |
| **Input-Data Consistency** | **LLM-as-Judge** | **Report matches source data** | **100%** |
| Latency | Performance | Under 30s | 95th %ile |
| Token Efficiency | Performance | Under 10k tokens | 90th %ile |

> **Critical**: The Input-Data Consistency evaluator catches the AD-1 mismatch case. It uses an LLM to verify that report conclusions match the gathered source data, detecting when the agent silently reconciles contradictory information instead of flagging it.

## Evaluator Implementation

```python
from langsmith.evaluation import evaluate
from templates.evaluators import (
    schema_evaluator,
    keyword_coverage_evaluator,
    quality_evaluator,
    input_data_consistency_evaluator,
    latency_evaluator,
    ALL_EVALUATORS,
)

# Run evaluation
results = evaluate(
    research_agent.invoke,
    data="research_agent_eval",
    evaluators=ALL_EVALUATORS,
    experiment_prefix="research_agent_v1",
)
```

## CI/CD Integration

### Tier 1: PR Checks (<5 min)
- schema_evaluator
- keyword_coverage_evaluator
- report_length_evaluator
- graceful_error_evaluator
- **Threshold**: All automated tests pass

### Tier 2: Pre-Deploy (15-30 min)
- All Tier 1 evaluators
- quality_evaluator (LLM-as-Judge)
- relevance_evaluator (LLM-as-Judge)
- input_data_consistency_evaluator (LLM-as-Judge)
- **Threshold**: Average quality > 4.0/5.0

### Tier 3: Production Monitoring
- Sample 5% of production traffic
- Weekly evaluation runs
- Alert on quality drop > 10%

## Next Steps

1. [ ] Create dataset in LangSmith with 21 test cases
2. [ ] Implement automated evaluators
3. [ ] Run baseline evaluation on current implementation
4. [ ] Add LLM-as-Judge evaluators for quality
5. [ ] Set up CI pipeline for PR checks
6. [ ] Configure production monitoring

## Notes

- Start with happy path cases to establish baseline
- Add edge cases as you discover production issues
- Review flagged cases weekly and add to dataset
- Re-run full evaluation after any major change
- **Always include adversarial cases that test for silent failures**
