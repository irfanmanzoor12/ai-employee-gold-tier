# Reasoning Loop Setup - Silver Tier

## Overview

The Reasoning Loop monitors `Needs_Action/` folder, analyzes tasks with Claude, and generates `Plan.md` files in the `Plans/` folder.

---

## Prerequisites

### 1. Anthropic API Key

Get your API key from: https://console.anthropic.com/

```bash
export ANTHROPIC_API_KEY='sk-ant-api03-...'
```

To make it permanent, add to `~/.bashrc`:
```bash
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Install Dependencies

```bash
cd /mnt/d/Irfan/FTE-H/watchers
python3 -m pip install anthropic
```

---

## How It Works

```
1. Watcher creates task → Needs_Action/TASK_123.md
2. Reasoning Loop detects task
3. Sends task to Claude API
4. Claude analyzes and creates plan
5. Saves as Plans/PLAN_TASK_123.md
6. Links plan back to original task
7. Human reviews plan → Approve/Reject
```

---

## Running the Reasoning Loop

### Option 1: Continuous Mode (Recommended)

```bash
cd /mnt/d/Irfan/FTE-H/watchers
python3 reasoning_loop.py
```

Runs every 5 minutes, checking for new tasks.

### Option 2: One-Time Processing

```bash
python3 -c "
from reasoning_loop import ReasoningLoop
loop = ReasoningLoop('../AI_Employee_Vault', check_interval=0)
loop.process_tasks()
print('Done!')
"
```

Processes all unplanned tasks once, then exits.

---

## Testing

### 1. Check Test Task Exists

```bash
ls ../AI_Employee_Vault/Needs_Action/TEST_TASK_*.md
```

### 2. Run One-Time Processing

```bash
python3 -c "
from reasoning_loop import ReasoningLoop
loop = ReasoningLoop('../AI_Employee_Vault')
loop.process_tasks()
"
```

### 3. Verify Plan Created

```bash
ls ../AI_Employee_Vault/Plans/PLAN_TEST_TASK_*.md
cat ../AI_Employee_Vault/Plans/PLAN_TEST_TASK_*.md
```

### 4. Check Original Task Updated

```bash
cat ../AI_Employee_Vault/Needs_Action/TEST_TASK_*.md | grep "Plan"
```

Should show a link to the generated plan.

---

## Plan.md Structure

Generated plans include:

```markdown
---
type: plan
task_file: TASK_123.md
created: 2026-01-13T17:35:00
status: pending_review
---

# Plan: Task Name

**Created:** 2026-01-13 17:35:00
**Original Task:** [[TASK_123]]
**Status:** 🟡 Pending Review

---

1. **Objective**: Clear goal
2. **Analysis**: What needs to be done
3. **Approach**: Step-by-step plan
4. **Required Resources**: Files, APIs, credentials
5. **Risks & Considerations**: Potential issues
6. **Success Criteria**: Completion indicators

---

## Next Steps

- [ ] Human Review Required
- [ ] Approve → Move to Approved/
- [ ] Reject → Refine approach
```

---

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

```bash
# Check if set
echo $ANTHROPIC_API_KEY

# Set temporarily
export ANTHROPIC_API_KEY='your-key-here'

# Set permanently
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### "No module named 'anthropic'"

```bash
python3 -m pip install anthropic
# or
pip install anthropic
```

### Plans Not Being Created

1. Check task exists in Needs_Action/
2. Check API key is valid
3. Check internet connection
4. Run with verbose logging:

```bash
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from reasoning_loop import ReasoningLoop
loop = ReasoningLoop('../AI_Employee_Vault')
loop.process_tasks()
"
```

---

## Integration with Watchers

Watchers automatically create tasks:
- **Gmail Watcher** → Email tasks
- **File Watcher** → File change tasks
- **LinkedIn Watcher** → Social tasks

The Reasoning Loop picks these up automatically.

---

## Next: Human-in-the-Loop Approval

After plans are created, implement approval workflow:
1. Review plan in Plans/ folder
2. Approve → Move task to Approved/
3. Reject → Add feedback, regenerate plan
4. Execute → Follow plan steps

---

*Silver Tier - Personal AI Employee Hackathon 0*
*Reasoning Loop Documentation*
