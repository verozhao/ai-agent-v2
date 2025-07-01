# AI Agent Feedback Loop for Financial Document Correction

This repository contains an advanced AI agent for extracting and correcting structured data from financial documents. The system is designed to not only detect and fix common and complex extraction errors, but also to learn and adapt over time using reinforcement learning and active learning techniques.

## How It Works

When a document is processed, the agent analyzes the extracted data, detects anomalies, and attempts to auto-correct errors. It uses a combination of semantic understanding, pattern recognition, and statistical validation. The agent is capable of handling:
- Swapped fields and type errors
- Cumulative fields (e.g., q4 should be the sum of q1, q2, q3)
- Pattern consistency (e.g., date sequences, value trends)
- Nested and out-of-order structures
- Subtle and realistic anomalies

The agent employs reinforcement learning strategies: it explores new correction strategies when uncertain, exploits known successful patterns when confident, and adapts its behavior based on feedback. Pattern weights and an exploration rate (epsilon) are updated after every feedback, so the agent gets better with experience.

## Learning and Feedback Loop

After each correction, the agent receives feedback (simulated as ground truth in the test set). If its correction is accepted, it reinforces that pattern; if not, it penalizes it and explores alternatives. The agent tracks its learning curve, including pattern weights, rewards, and exploration rate, and can visualize its progress over time.

## Running the System

To run the feedback loop and see the agent in action:

```
python main.py
```

The script will process all test cases, print out the agent's corrections, show when exploration, exploitation, or uncertainty is triggered, and display feedback loop metrics. At the end, if you have `matplotlib` installed, you'll see a plot of the agent's learning curve.

## Customizing Test Cases

Test cases are defined in `scripts/generate_test_data.py` as a list of dictionaries, each with an `extracted` (raw) and `audited` (ground truth) version, and a `pattern_type` label. You can edit this file to add new scenarios, cover more edge cases, or remove tests you no longer need. The agent is designed to handle realistic, complex document patterns.

## Start

```bash
git clone https://github.com/verozhao/ai-agent-v2
cd agents/anomaly_correction_agent

pip install -r requirements.txt
python main.py
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Document Input  │────▶│ Anomaly Detector │────▶│ Auto-Correction │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │
                        ┌──────────────────┐               │
                        │  DataOps Review  │◀──────────────┘
                        └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │  Feedback Loop   │
                        │  (Learning)      │
                        └──────────────────┘
```

## Repository Structure

```
anomaly-correction-agent/
├── agents/
│   ├── __init__.py
│   ├── anomaly_correction_agent.py    # Core agent implementation
│   └── feedback_loop.py               # Feedback loop manager
├── models/
│   └── field_patterns.json            # Field pattern definitions
├── tests/
│   ├── __init__.py
│   ├── test_agent.py                  # Agent unit tests
│   └── test_feedback_loop.py          # Integration tests
├── scripts/
│   └── generate_test_data.py          # Test data generator
├── docker/
│   ├── Dockerfile                     # Production Docker image
│   └── docker-compose.yml             # Local development setup
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package setup
├── main.py                           # Main execution
└── README.md                         # This file
```

## Key Features

### 1. Intelligent Field Classification
- Semantic embedding-based field type detection
- Pattern recognition for common field types (dates, fund names, amounts, percentages)
- Context-aware classification using transformer models

### 2. Multi-Strategy Auto-Correction
- Pattern-based: Rule-based corrections for common swap patterns
- ML-based: Learning from historical corrections
- Cross-field validation: Ensuring data consistency across fields

### 3. Continuous Learning
- Reinforcement of successful patterns
- Learning from DataOps team validations
- Adaptive confidence thresholds